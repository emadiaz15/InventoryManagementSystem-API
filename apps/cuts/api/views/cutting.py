from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from apps.cuts.models import CuttingOrder
from apps.cuts.api.serializers import CuttingOrderSerializer
from apps.stocks.models import Stock
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.core.utils import send_assignment_notification


@extend_schema(
    methods=['GET'],
    operation_id="list_cutting_orders",
    description="Recupera una lista de todas las órdenes de corte activas",
    responses={200: CuttingOrderSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def cutting_order_create_view(request):
    """
    Endpoint para crear una nueva orden de corte. Verifica el stock antes de crear la orden.
    """
    serializer = CuttingOrderSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        order = serializer.save(assigned_by=request.user)
        try:
            check_stock(order)  # Verificación de stock antes de guardar la orden
            send_assignment_notification(order)  # Enviar notificación
            return Response(CuttingOrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
@permission_classes([IsAuthenticated])
def cutting_order_detail_view(request, pk):
    """
    Endpoint para obtener, actualizar o eliminar suavemente una orden de corte específica.
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
        order = serializer.save()
        return Response(CuttingOrderSerializer(order).data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def soft_delete_cutting_order(order):
    """Realiza un soft delete de la orden de corte."""
    order.deleted_at = timezone.now()
    order.save()
    return Response({"detail": "Orden de corte eliminada (soft) correctamente."}, status=status.HTTP_204_NO_CONTENT)

def check_stock(order):
    """
    Método para verificar si hay suficiente stock para la orden de corte.
    Verifica cada item en la orden para asegurar que haya suficiente stock.
    """
    for item in order.items.all():
        # Intenta obtener el stock del producto
        stock = Stock.objects.filter(product=item.product).first()
        
        if not stock:
            raise ValidationError(f"No se encontró stock para el producto {item.product.name}.")
        
        if stock.quantity < item.quantity:
            raise ValidationError(f"No hay suficiente stock para el producto {item.product.name}. Solo hay {stock.quantity} unidades disponibles.")
    
    return True


def send_assignment_notification(order):
    """
    Envia una notificación cuando una orden de corte es asignada.
    """
    # Asumimos que `send_notification` es un método que envía un correo o notificación
    # Puedes adaptarlo a tu propio sistema de notificaciones.
    message = f"Una nueva orden de corte con ID {order.id} ha sido asignada."
    # Se envía la notificación al usuario asignado (supuesto que 'assigned_to' es un campo en el modelo)
    if order.assigned_to:
        order.assigned_to.send_notification(message)
