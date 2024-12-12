from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from apps.cuts.models import CuttingOrder
from apps.cuts.api.serializers import CuttingOrderSerializer
from apps.stocks.models import Stock
from django.utils.timezone import now
from django.core.exceptions import ValidationError


@extend_schema(
    methods=['GET'],
    operation_id="list_cutting_orders",
    description="Recupera una lista de todas las órdenes de corte activas",
    responses={200: CuttingOrderSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([AllowAny])  # Todos los usuarios tienen permiso CRUD, por lo tanto AllowAny
def cutting_orders_list_view(request):
    """
    Endpoint para listar todas las órdenes de corte activas.
    """
    orders = CuttingOrder.objects.filter(deleted_at__isnull=True)
    serializer = CuttingOrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    methods=['POST'],
    operation_id="create_cutting_order",
    description="Crea una nueva orden de corte, verificando si hay suficiente stock",
    request=CuttingOrderSerializer,
    responses={201: CuttingOrderSerializer, 400: "Datos inválidos", 409: "Stock insuficiente"},
)
@api_view(['POST'])
@permission_classes([AllowAny])
def cutting_order_create_view(request):
    """
    Endpoint para crear una nueva orden de corte. Verifica el stock antes de crear la orden.
    """
    serializer = CuttingOrderSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        order = serializer.save(assigned_by=request.user if request.user.is_authenticated else None)
        try:
            check_stock(order)  # Verificación de stock antes de devolver la respuesta
            return Response(CuttingOrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_409_CONFLICT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['GET'],
    operation_id="retrieve_cutting_order",
    description="Recupera los detalles de una orden de corte específica",
    responses={200: CuttingOrderSerializer, 404: "Orden de corte no encontrada"},
)
@extend_schema(
    methods=['PUT', 'PATCH'],
    operation_id="update_cutting_order",
    description="Actualiza una orden de corte específica",
    request=CuttingOrderSerializer,
    responses={200: CuttingOrderSerializer, 400: "Datos inválidos"},
)
@extend_schema(
    methods=['DELETE'],
    operation_id="delete_cutting_order",
    description="Elimina suavemente una orden de corte específica",
    responses={204: "Orden de corte eliminada (soft)", 404: "Orden de corte no encontrada"},
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def cutting_order_detail_view(request, pk):
    """
    Endpoint para obtener, actualizar o eliminar suavemente una orden de corte específica.
    Todos los usuarios tienen CRUD (crear, leer, actualizar, eliminar suave).
    """
    try:
        order = CuttingOrder.objects.get(pk=pk, deleted_at__isnull=True)
    except CuttingOrder.DoesNotExist:
        return Response({"detail": "Orden de corte no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return retrieve_cutting_order(order)
    elif request.method in ['PUT', 'PATCH']:
        return update_cutting_order(request, order)
    elif request.method == 'DELETE':
        return soft_delete_cutting_order(order)


def retrieve_cutting_order(order):
    """Obtiene los detalles de la orden de corte."""
    serializer = CuttingOrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)


def update_cutting_order(request, order):
    """Actualiza una orden de corte existente."""
    serializer = CuttingOrderSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        if 'status' in serializer.validated_data and serializer.validated_data['status'] == 'completed':
            # Completar la orden de corte verificando la lógica definida en el modelo
            try:
                order.complete_cutting()
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(CuttingOrderSerializer(order).data, status=status.HTTP_200_OK)
        else:
            order = serializer.save()
            return Response(CuttingOrderSerializer(order).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def soft_delete_cutting_order(order):
    """Realiza un soft delete de la orden de corte."""
    order.deleted_at = now()
    order.save()
    return Response({"detail": "Orden de corte eliminada (soft) correctamente."}, status=status.HTTP_204_NO_CONTENT)


def check_stock(order):
    """
    Verifica si hay suficiente stock para la orden de corte.
    """
    # Dado que ahora usamos product en lugar de subproduct
    # Ajustamos la lógica para filtrar el stock por product
    stock = Stock.objects.filter(product=order.product).first()
    if not stock:
        raise ValidationError(f"No stock found for product {order.product.name}.")

    if stock.quantity < order.cutting_quantity:
        raise ValidationError(f"Insufficient stock for {order.product.name}. Available: {stock.quantity}")
    return True
