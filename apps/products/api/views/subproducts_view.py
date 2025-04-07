from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import InvalidOperation

# --- ORM, Modelos Stock, etc. ---
from django.db.models import OuterRef, Subquery, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal
from apps.stocks.models import SubproductStock 

# --- Otros Imports ---
# Ajusta rutas según tu estructura
from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.api.repositories.subproduct_repository import SubproductRepository
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.products.docs.subproduct_doc import (
    list_subproducts_doc, create_subproduct_doc, get_subproduct_by_id_doc,
    update_subproduct_by_id_doc, delete_subproduct_by_id_doc
)
# --- Importa los SERVICIOS de stock ---
from apps.stocks.services import initialize_subproduct_stock, adjust_subproduct_stock


@extend_schema(**list_subproducts_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def subproduct_list(request, prod_pk):
    """
    Lista subproductos activos de un producto padre, con paginación,
    e incluyendo el stock actual calculado.
    """
    parent_product = get_object_or_404(Product, pk=prod_pk, status=True)

    # Subquery para stock
    subproduct_stock_sq = SubproductStock.objects.filter(
        subproduct=OuterRef('pk'), status=True
    ).values('quantity')[:1]

    # Queryset anotado
    subproducts_qs = SubproductRepository.get_all_active(
        parent_product_id=parent_product.pk
    ).annotate(
        current_stock_val=Subquery(subproduct_stock_sq, output_field=DecimalField(max_digits=15, decimal_places=2))
    ).annotate(
        current_stock=Coalesce(
            'current_stock_val', Decimal('0.00'), output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    )
    # Orden por defecto (-created_at) viene de BaseModel.Meta

    paginator = Pagination()
    paginated_subproducts = paginator.paginate_queryset(subproducts_qs, request)
    serializer = SubProductSerializer(paginated_subproducts, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_subproduct_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_subproduct(request, prod_pk):
    """
    Crea un nuevo subproducto, inicializa su stock,
    y actualiza el flag del producto padre si es necesario.
    """
    parent_product = get_object_or_404(Product, pk=prod_pk, status=True)
    serializer_context = {'request': request, 'parent_product': parent_product}
    # Extraer datos de stock ANTES de pasarlos al serializer de Subproducto
    request_data = request.data.copy()
    initial_qty_str = request_data.pop('initial_stock_quantity', '0')
    initial_loc = request_data.pop('initial_stock_location', None)
    initial_reason = f"Stock Inicial por Creación Subproducto"  # Razón base

    # Validar cantidad inicial
    try:
        initial_qty = Decimal(initial_qty_str)
        if initial_qty < 0:
            raise ValueError("Cantidad negativa")
    except (InvalidOperation, ValueError):
        raise serializers.ValidationError({"initial_stock_quantity": f"Valor inválido ('{initial_qty_str}')"})

    # Validar datos del subproducto
    serializer = SubProductSerializer(data=request_data, context=serializer_context)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                # 1. Guardar Subproducto (llama a SubProductSerializer.create -> BaseSerializer.create -> instance.save)
                subproduct_instance = serializer.save(user=request.user)

                # Actualizar razón con ID ahora que existe
                initial_reason = f"Stock Inicial por Creación Subproducto #{subproduct_instance.pk}"

                # 2. Inicializar Stock del Subproducto via Servicio
                # (Esta función usa transaction.atomic internamente también, pero anidarlo está bien)
                initialize_subproduct_stock(
                    subproduct=subproduct_instance,
                    user=request.user,
                    initial_quantity=initial_qty,
                    location=initial_loc,
                    reason=initial_reason
                )

                # 3. Actualizar Flag del Producto Padre si es necesario
                if parent_product.has_individual_stock:
                    print(f"--- INFO: Actualizando has_individual_stock=False para Producto {parent_product.pk} ---")
                    parent_product.has_individual_stock = False
                    parent_product.save(user=request.user,
                                        update_fields=['has_individual_stock', 'modified_at', 'modified_by'])

            # 4. Serializar respuesta OK (con stock anotado)
            subproduct_annotated = Subproduct.objects.annotate(
                current_stock_val=Subquery(
                    SubproductStock.objects.filter(subproduct=subproduct_instance, status=True).values('quantity')[:1],
                    output_field=DecimalField(decimal_places=2))
            ).annotate(
                current_stock=Coalesce('current_stock_val', Decimal('0.00'), output_field=DecimalField(decimal_places=2))
            ).get(pk=subproduct_instance.pk)
            response_serializer = SubProductSerializer(subproduct_annotated, context=serializer_context)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except (ValidationError, serializers.ValidationError, ValueError, Exception) as e:
            print(f"Error en transacción al crear subproducto o inicializar stock: {e}")
            error_detail = getattr(e, 'detail', str(e)) if isinstance(
                e, (serializers.ValidationError, ValidationError)) else "Error interno al procesar la solicitud."
            status_code = status.HTTP_400_BAD_REQUEST if isinstance(
                e, (serializers.ValidationError, ValidationError, ValueError)) else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response({"detail": error_detail}, status_code)
    else:
        # Errores de validación del SubProductSerializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_subproduct_by_id_doc)
@extend_schema(**update_subproduct_by_id_doc)
@extend_schema(**delete_subproduct_by_id_doc) 
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def subproduct_detail(request, prod_pk, subp_pk):
    """
    Obtiene (con stock), actualiza datos del subproducto y/o ajusta stock,
    o realiza un soft delete.
    """
    parent_product = get_object_or_404(Product, pk=prod_pk, status=True)

    # --- GET ---
    if request.method == 'GET':
        # Lógica GET con anotación de stock (como antes)
        subproduct_stock_sq = SubproductStock.objects.filter(subproduct=OuterRef('pk'), status=True).values('quantity')[:1]
        queryset = Subproduct.objects.annotate(
            current_stock_val=Subquery(
                subproduct_stock_sq, output_field=DecimalField(max_digits=15, decimal_places=2))
        ).annotate(
            current_stock=Coalesce('current_stock_val', Decimal('0.00'),
                                  output_field=DecimalField(max_digits=15, decimal_places=2))
        )
        subproduct = get_object_or_404(queryset, pk=subp_pk, parent=parent_product, status=True)
        serializer = SubProductSerializer(subproduct, context={'request': request})
        return Response(serializer.data)

    else:  # Lógica común para PUT y DELETE
        subproduct_instance = get_object_or_404(Subproduct, pk=subp_pk, parent=parent_product, status=True)

        if request.method == 'PUT':
            # Usa serializer para validar datos del subproducto Y datos de ajuste de stock
            serializer = SubProductSerializer(subproduct_instance, data=request.data, context={'request': request},
                                         partial=True)
            if serializer.is_valid():
                # Extraer datos de ajuste de stock (write_only)
                validated_data = serializer.validated_data
                quantity_change = validated_data.get('quantity_change')
                reason = validated_data.get('reason')

                try:
                    # Usar transacción atómica
                    with transaction.atomic():
                        # 1. Guardar cambios del Subproducto (usando datos validados restantes)
                        #    Llama a BaseSerializer.update -> instance.save(user=...)
                        updated_subproduct = serializer.save(user=request.user)

                        # 2. Si se envió un ajuste de stock, llamar al servicio de stock
                        if quantity_change is not None:
                            try:
                                # Obtener el registro SubproductStock asociado
                                # Ajusta si manejas ubicaciones, aquí asume una o ninguna (None)
                                stock_record = SubproductStock.objects.select_for_update().get(
                                    subproduct=updated_subproduct,
                                    location=None,  # O location=request.data.get('location') si aplica
                                    status=True
                                )
                                # Llama al servicio de ajuste de subproducto
                                adjust_subproduct_stock(
                                    subproduct_stock=stock_record,
                                    quantity_change=quantity_change,
                                    reason=reason,  # Validado por serializer que no sea nulo si hay quantity_change
                                    user=request.user
                                )
                            except SubproductStock.DoesNotExist:
                                raise ValidationError(
                                    "No se encontró registro de stock para este subproducto. No se pudo aplicar el ajuste.")
                            except SubproductStock.MultipleObjectsReturned:
                                raise ValidationError(
                                    "Se encontraron múltiples registros de stock. Se requiere lógica adicional (ej. especificar ubicación).")

                    # 3. Serializar respuesta (sin stock recalculado aquí)
                    response_serializer = SubProductSerializer(updated_subproduct, context={'request': request})
                    return Response(response_serializer.data)

                except (ValidationError, ValueError, Exception) as e:
                    print(f"Error durante PUT de subproducto {subp_pk} con ajuste de stock: {e}")
                    error_detail = getattr(e, 'detail', str(e)) if isinstance(
                        e, (serializers.ValidationError, ValidationError)) else str(e)
                    status_code = status.HTTP_400_BAD_REQUEST if isinstance(
                        e, (ValidationError, serializers.ValidationError, ValueError)) else status.HTTP_500_INTERNAL_SERVER_ERROR
                    return Response({"detail": error_detail}, status_code)

            # Errores de validación del SubProductSerializer
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            try:
                # Llama al método delete de BaseModel
                subproduct_instance.delete(user=request.user)
                # Considera lógica adicional aquí o en signals/services si borrar
                # el último subproducto debe cambiar parent.has_individual_stock a True
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                print(f"Error al hacer soft delete de subproducto {subp_pk}: {e}")
                return Response({"detail": "Error interno al eliminar el subproducto."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)