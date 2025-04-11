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

from django_filters.rest_framework import DjangoFilterBackend
from apps.products.filters.product_filter import ProductFilter

@extend_schema(**list_product_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def product_list(request):
    """
    Lista productos activos con paginación, incluyendo el stock actual calculado.
    Permite filtrar por código (exacto).
    """
    print("Iniciando product_list")
    product_stock_sq = ProductStock.objects.filter(product=OuterRef('pk'), status=True).values('quantity')[:1]
    subproduct_stock_sum_sq = SubproductStock.objects.filter(
        subproduct__parent_id=OuterRef('pk'), status=True, subproduct__status=True
    ).values('subproduct__parent').annotate(total=Sum('quantity')).values('total')

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

    # 🆕 Aplicar filtro por código
    filterset = ProductFilter(request.GET, queryset=products_qs)
    if not filterset.is_valid():
        return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
    filtered_qs = filterset.qs

    paginator = Pagination()
    paginated_products = paginator.paginate_queryset(filtered_qs, request)
    serializer = ProductSerializer(paginated_products, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_product_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_product(request):
    """
    Crea un nuevo producto y, opcionalmente, inicializa su registro de stock
    con 'initial_stock_quantity', 'initial_stock_location' y 'initial_stock_reason'.

    Se fuerza has_individual_stock=True al crear.
    """
    print("Iniciando create_product")
    request_data = request.data.copy()
    print("Datos recibidos:", request_data)
    
    # Forzar has_individual_stock=True
    request_data['has_individual_stock'] = True

    # Extraer y corregir el valor de initial_stock_quantity:
    initial_quantity_str = request_data.pop('initial_stock_quantity', '0')
    # Si viene como lista, tomamos el primer elemento.
    if isinstance(initial_quantity_str, list):
        initial_quantity_str = initial_quantity_str[0]
    
    initial_location = request_data.pop('initial_stock_location', None)
    initial_reason = request_data.pop('initial_stock_reason', 'Stock Inicial por Creación')
    print("Valor recibido para stock inicial:", initial_quantity_str)
    print("Ubicación de stock:", initial_location)
    print("Razón de stock inicial:", initial_reason)

    try:
        initial_quantity = Decimal(initial_quantity_str)
        if initial_quantity < 0:
            raise serializers.ValidationError({"initial_stock_quantity": "La cantidad inicial no puede ser negativa."})
    except (InvalidOperation, ValueError):
        raise serializers.ValidationError({
            "initial_stock_quantity": f"Valor inválido ('{initial_quantity_str}') para cantidad inicial."
        })

    serializer = ProductSerializer(data=request_data, context={'request': request})
    if serializer.is_valid():
        print("Serializer válido. Creando producto.")
        try:
            with transaction.atomic():
                product_instance = serializer.save(user=request.user)
                print(f"Producto creado exitosamente con ID: {product_instance.pk}")
                if product_instance.has_individual_stock:
                    print("Producto tiene stock individual. Inicializando stock...")
                    initialize_product_stock(
                        product=product_instance,
                        user=request.user,
                        initial_quantity=initial_quantity,
                        location=initial_location,
                        reason=initial_reason
                    )
                    print("Stock inicial creado.")
            response_serializer = ProductSerializer(product_instance, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except (ValidationError, ValueError, Exception) as e:
            print(f"ERROR al crear producto o inicializar stock: {e}")
            error_detail = getattr(e, 'detail', str(e)) if isinstance(
                e, (serializers.ValidationError, ValidationError)
            ) else "Error interno al procesar la solicitud."
            status_code = (
                status.HTTP_400_BAD_REQUEST
                if isinstance(e, (ValidationError, serializers.ValidationError, ValueError))
                else status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            return Response({"detail": error_detail}, status=status_code)
    else:
        print("Error de validación en el serializer:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(**get_product_by_id_doc)
@extend_schema(**update_product_by_id_doc)
@extend_schema(**delete_product_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def product_detail(request, prod_pk):
    """
    Obtiene/actualiza/elimina (soft delete) un producto específico.
    - GET: retorna el producto con stock anotado.
    - PUT: actualiza datos y, opcionalmente, ajusta stock.
    - DELETE: soft delete.
    """
    if request.method == 'GET':
        print(f"Product detail GET para producto ID: {prod_pk}")
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
        print("Producto obtenido y serializado para GET.")
        return Response(serializer.data)

    # Para PUT/DELETE
    product_instance = get_object_or_404(Product, pk=prod_pk, status=True)
    print(f"Iniciando actualización o eliminación para producto ID: {prod_pk}")

    if request.method == 'PUT':
        serializer = ProductSerializer(product_instance, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            print("Serializer válido para PUT.")
            validated_data = serializer.validated_data.copy()
            quantity_change = validated_data.get('quantity_change')
            reason = validated_data.get('reason')
            print("Ajuste de stock recibido en PUT:", quantity_change, reason)
            try:
                with transaction.atomic():
                    updated_product = serializer.save(user=request.user)
                    print(f"Producto actualizado. Nuevo estado del producto ID: {updated_product.pk}")
                    if quantity_change is not None:
                        if updated_product.has_individual_stock:
                            try:
                                stock_record = ProductStock.objects.select_for_update().get(
                                    product=updated_product, location=None
                                )
                                print("Registro de stock encontrado para ajuste:", stock_record.pk)
                                adjust_product_stock(
                                    product_stock=stock_record,
                                    quantity_change=quantity_change,
                                    reason=reason,
                                    user=request.user
                                )
                                print("Ajuste de stock realizado.")
                            except ProductStock.DoesNotExist:
                                raise ValidationError(
                                    "No se encontró registro de stock individual para este producto. "
                                    "No se pudo aplicar el ajuste."
                                )
                        else:
                            raise ValidationError(
                                "No se puede ajustar stock en un producto con subproductos (has_individual_stock=False)."
                            )
                response_serializer = ProductSerializer(updated_product, context={'request': request})
                return Response(response_serializer.data)
            except (ValidationError, ValueError, Exception) as e:
                print(f"Error durante PUT de producto {prod_pk}: {e}")
                error_detail = getattr(e, 'detail', str(e)) if isinstance(
                    e, (serializers.ValidationError, ValidationError)
                ) else str(e)
                status_code = (
                    status.HTTP_400_BAD_REQUEST
                    if isinstance(e, (ValidationError, serializers.ValidationError, ValueError))
                    else status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                return Response({"detail": error_detail}, status_code)
        print("Errores de validación en PUT:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            product_instance.delete(user=request.user)
            print(f"Producto ID {prod_pk} eliminado (soft delete).")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"Error al hacer soft delete de producto {prod_pk}: {e}")
            return Response(
                {"detail": "Error interno al eliminar el producto."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
