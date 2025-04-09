from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.db import transaction

# --- ORM y Modelos de Stock ---
from django.db.models import Sum, F, Q, Case, When, DecimalField, OuterRef, Subquery
from apps.stocks.models import ProductStock, SubproductStock
from apps.products.models import Product

# Ajusta rutas
from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination
from apps.products.api.serializers.product_serializer import ProductSerializer
from apps.products.api.repositories.product_repository import ProductRepository
from apps.products.docs.product_doc import (
    list_product_doc, create_product_doc, get_product_by_id_doc,
    update_product_by_id_doc, delete_product_by_id_doc
)

# --- Importa los SERVICIOS de stock ---
from apps.stocks.services import initialize_product_stock, adjust_product_stock


@extend_schema(**list_product_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def product_list(request):
    """
    Lista productos activos con paginación, incluyendo el stock actual calculado.
    """
    # Subqueries para calcular stock
    product_stock_sq = ProductStock.objects.filter(product=OuterRef('pk'), status=True).values('quantity')[:1]
    subproduct_stock_sum_sq = SubproductStock.objects.filter(
        subproduct__parent_id=OuterRef('pk'), status=True, subproduct__status=True
    ).values('subproduct__parent').annotate(total=Sum('quantity')).values('total')

    # Anotar queryset
    products_qs = ProductRepository.get_all_active_products().annotate(
        individual_stock_qty=Subquery(product_stock_sq, output_field=DecimalField(max_digits=15, decimal_places=2)),
        subproduct_stock_total=Subquery(subproduct_stock_sum_sq, output_field=DecimalField(max_digits=15, decimal_places=2))
    ).annotate(
        current_stock=Case(
            When(has_individual_stock=True, individual_stock_qty__isnull=False, then=F('individual_stock_qty')),
            When(has_individual_stock=False, subproduct_stock_total__isnull=False, then=F('subproduct_stock_total')),
            default=Decimal('0.00'),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    )

    paginator = Pagination()
    paginated_products = paginator.paginate_queryset(products_qs, request)
    serializer = ProductSerializer(paginated_products, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_product_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_product(request):
    """
    Crea un nuevo producto y también inicializa su registro de stock
    con la cantidad proporcionada opcionalmente en el request.
    """
    request_data = request.data.copy()
    initial_quantity_str = request_data.pop('initial_stock_quantity', '0')
    initial_location = request_data.pop('initial_stock_location', None)
    initial_reason = request_data.pop('initial_stock_reason', 'Stock Inicial por Creación')

    try:
        initial_quantity = Decimal(initial_quantity_str)
        if initial_quantity < 0:
            raise serializers.ValidationError({"initial_stock_quantity": "La cantidad inicial no puede ser negativa."})
    except (InvalidOperation, ValueError):
        raise serializers.ValidationError(
            {"initial_stock_quantity": f"Valor inválido ('{initial_quantity_str}') para cantidad inicial."})

    serializer = ProductSerializer(data=request_data, context={'request': request})
    if serializer.is_valid():
        try:
            with transaction.atomic():
                # 1. Guardar Producto
                product_instance = serializer.save(user=request.user)

                # 2. Inicializar Stock si corresponde
                if product_instance.has_individual_stock:
                    initialize_product_stock(
                        product=product_instance,
                        user=request.user,
                        initial_quantity=initial_quantity,
                        location=initial_location,
                        reason=initial_reason
                    )

            # 3. Devolver respuesta del Producto creado
            response_serializer = ProductSerializer(product_instance, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except (ValidationError, ValueError, Exception) as e:
            print(f"ERROR Crítico al crear producto o inicializar stock: {e}")
            error_detail = getattr(e, 'detail', str(e)) if isinstance(
                e, (serializers.ValidationError, ValidationError)) else "Error interno al procesar la solicitud."
            status_code = status.HTTP_400_BAD_REQUEST if isinstance(
                e, (ValidationError, serializers.ValidationError, ValueError)) else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response({"detail": error_detail}, status_code)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_product_by_id_doc)
@extend_schema(**update_product_by_id_doc)
@extend_schema(**delete_product_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def product_detail(request, prod_pk):
    """
    Obtiene (con stock), actualiza datos del producto y/o ajusta stock,
    o realiza un soft delete.
    """

    # --- GET ---
    if request.method == 'GET':
        # Lógica para buscar y anotar para GET
        product_stock_sq = ProductStock.objects.filter(product=OuterRef('pk'), status=True).values('quantity')[:1]
        subproduct_stock_sum_sq = SubproductStock.objects.filter(
            subproduct__parent_id=OuterRef('pk'), status=True, subproduct__status=True
        ).values('subproduct__parent').annotate(total=Sum('quantity')).values('total')

        queryset = Product.objects.annotate(
            individual_stock_qty=Subquery(product_stock_sq, output_field=DecimalField(max_digits=15, decimal_places=2)),
            subproduct_stock_total=Subquery(subproduct_stock_sum_sq, output_field=DecimalField(max_digits=15, decimal_places=2))
        ).annotate(
            current_stock=Case(
                When(has_individual_stock=True, individual_stock_qty__isnull=False, then=F('individual_stock_qty')),
                When(has_individual_stock=False, subproduct_stock_total__isnull=False, then=F('subproduct_stock_total')),
                default=Decimal('0.00'),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        )
        product_annotated = get_object_or_404(queryset, pk=prod_pk, status=True)
        serializer = ProductSerializer(product_annotated, context={'request': request})
        return Response(serializer.data)

    else:  # Este 'else' cubre PUT y DELETE
        # --- Lógica común para PUT y DELETE: Obtener instancia base ---
        # Obtenemos sin anotar, ya que PUT/DELETE no necesitan el stock calculado
        product_instance = get_object_or_404(Product, pk=prod_pk, status=True)

        if request.method == 'PUT':
            serializer = ProductSerializer(product_instance, data=request.data, context={'request': request},
                                         partial=True)
            if serializer.is_valid():
                validated_data = serializer.validated_data.copy()
                quantity_change = validated_data.get('quantity_change')
                reason = validated_data.get('reason')

                try:
                    with transaction.atomic():
                        # 1. Guardar cambios del Producto
                        updated_product = serializer.save(user=request.user)

                        # 2. Si se envió un ajuste de stock, llamar al servicio
                        if quantity_change is not None:
                            if updated_product.has_individual_stock:
                                try:
                                    # Obtener stock record (ajusta lógica de ubicación si es necesario)
                                    stock_record = ProductStock.objects.select_for_update().get(
                                        product=updated_product, location=None)  # Asume ubicación única o None
                                    adjust_product_stock(
                                        product_stock=stock_record,
                                        quantity_change=quantity_change,
                                        reason=reason,
                                        user=request.user
                                    )
                                except ProductStock.DoesNotExist:
                                    raise ValidationError(
                                        "No se encontró registro de stock individual para este producto. No se pudo aplicar el ajuste.")
                            else:
                                raise ValidationError(
                                    "No se puede ajustar el stock directamente en un producto cuyo stock deriva de subproductos.")

                        # 3. Serializar respuesta (sin stock recalculado aquí)
                        response_serializer = ProductSerializer(updated_product, context={'request': request})
                        return Response(response_serializer.data)

                except (ValidationError, ValueError, Exception) as e:
                    print(f"Error durante PUT de producto {prod_pk} con ajuste de stock: {e}")
                    error_detail = getattr(e, 'detail', str(e)) if isinstance(
                        e, (serializers.ValidationError, ValidationError)) else str(e)
                    status_code = status.HTTP_400_BAD_REQUEST if isinstance(
                        e, (ValidationError, serializers.ValidationError, ValueError)) else status.HTTP_500_INTERNAL_SERVER_ERROR
                    return Response({"detail": error_detail}, status_code)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            try:
                # Llama al método delete de BaseModel
                product_instance.delete(user=request.user)
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                print(f"Error al hacer soft delete de producto {prod_pk}: {e}")
                return Response({"detail": "Error interno al eliminar el producto."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
