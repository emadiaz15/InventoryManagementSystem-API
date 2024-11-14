# Este archivo define las vistas para manejar las órdenes de corte, incluyendo listar, crear, obtener, actualizar y eliminar de manera suave.
# También se verifica el stock antes de crear o completar una orden y se envían notificaciones por correo electrónico.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.cuts.models import CuttingOrder
from apps.cuts.api.serializers import CuttingOrderSerializer
from apps.stocks.models import Stock
from django.utils import timezone
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from apps.core.utils import send_assignment_notification  # Importa la función de notificación

# Vista para listar órdenes de corte
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
    # Recupera solo las órdenes de corte activas (no eliminadas)
    orders = CuttingOrder.objects.filter(deleted_at__isnull=True)
    serializer = CuttingOrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Vista para crear una nueva orden de corte
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
    serializer = CuttingOrderSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.validated_data['product']
        cutting_quantity = serializer.validated_data['cutting_quantity']

        # Verificar el stock más reciente del producto
        latest_stock = Stock.objects.filter(product=product).order_by('-date').first()

        # Verifica si hay stock suficiente
        if latest_stock is None or latest_stock.quantity < cutting_quantity:
            return Response(
                {'detail': f'Stock insuficiente. Disponible: {latest_stock.quantity if latest_stock else 0}, Requerido: {cutting_quantity}'},
                status=status.HTTP_409_CONFLICT
            )

        try:
            # Guarda la orden y asigna el usuario que la crea
            order = serializer.save(assigned_by=request.user)
            
            # Enviar notificación de asignación de la orden
            send_assignment_notification(order)
            
            return Response(CuttingOrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Devuelve errores de validación
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Vista para obtener, actualizar o eliminar suavemente una orden de corte específica
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
    responses={204: "Orden de corte eliminada correctamente", 404: "Orden de corte no encontrada"},
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
        return Response({'detail': 'Orden de corte no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return get_cutting_order(order)

    elif request.method in ['PUT', 'PATCH']:
        return update_cutting_order(request, order)

    elif request.method == 'DELETE':
        return soft_delete_cutting_order(order)


def get_cutting_order(order):
    """Obtener detalles de una orden de corte específica."""
    serializer = CuttingOrderSerializer(order)
    return Response(serializer.data)


def update_cutting_order(request, order):
    """Actualizar una orden de corte, permitiendo actualizaciones parciales."""
    serializer = CuttingOrderSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        try:
            updated_order = serializer.save()

            # Si se completa la orden, ejecuta la lógica de corte
            if updated_order.status == 'completed':
                complete_cutting(updated_order)
            
            # Enviar notificación de asignación de la orden actualizada
            send_assignment_notification(updated_order)

            return Response(CuttingOrderSerializer(updated_order).data)

        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def soft_delete_cutting_order(order):
    """Elimina suavemente una orden de corte, estableciendo deleted_at con la fecha actual."""
    order.deleted_at = timezone.now()
    order.save(update_fields=['deleted_at'])
    return Response({'message': 'Orden de corte eliminada correctamente (soft delete)'}, status=status.HTTP_204_NO_CONTENT)


# Lógica para completar una orden de corte
def complete_cutting(order):
    """
    Completa una orden de corte, actualizando el stock y marcando la orden como 'completed'.
    """
    if order.status != 'in_process':
        raise ValueError("La operación debe estar en estado 'in_process' para completarse.")

    # Obtener el último stock disponible
    latest_stock = order.product.stocks.latest('date')

    # Verificar si hay suficiente stock para completar el corte
    if latest_stock.quantity < order.cutting_quantity:
        raise ValidationError(f"La cantidad de corte ({order.cutting_quantity}) no puede exceder el stock disponible ({latest_stock.quantity}).")

    # Actualizar el stock
    latest_stock.quantity -= order.cutting_quantity
    latest_stock.save()

    # Marcar la orden como completada
    order.status = 'completed'
    order.completed_at = timezone.now()
    order.save()
