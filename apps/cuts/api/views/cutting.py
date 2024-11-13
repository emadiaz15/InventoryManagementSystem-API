from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.cuts.models import CuttingOrder
from apps.cuts.api.serializers import CuttingOrderSerializer
from apps.stocks.models import Stock  # Importamos el modelo de Stock
from django.utils import timezone
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

# View para listar y crear órdenes de corte
@extend_schema(
    methods=['GET'],
    operation_id="list_cutting_orders",
    description="Retrieve a list of all cutting orders",
    responses={200: CuttingOrderSerializer(many=True)},
)
@extend_schema(
    methods=['POST'],
    operation_id="create_cutting_order",
    description="Create a new cutting order",
    request=CuttingOrderSerializer,
    responses={201: CuttingOrderSerializer, 400: "Bad Request - Invalid data", 409: "Stock not sufficient"},
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cutting_orders_view(request):
    """
    Endpoint para listar todas las órdenes de corte o crear una nueva.
    """
    if request.method == 'GET':
        return list_cutting_orders()

    elif request.method == 'POST':
        return create_cutting_order(request)


def list_cutting_orders():
    """Listar todas las órdenes de corte activas."""
    orders = CuttingOrder.objects.all()
    serializer = CuttingOrderSerializer(orders, many=True)
    return Response(serializer.data)


def create_cutting_order(request):
    """
    Crear una nueva orden de corte. Verifica si hay suficiente stock antes de crear la orden.
    """
    serializer = CuttingOrderSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.validated_data['product']
        cutting_quantity = serializer.validated_data['cutting_quantity']

        # Verificar el stock más reciente del producto
        latest_stock = Stock.objects.filter(product=product).order_by('-date').first()

        if latest_stock is None or latest_stock.quantity < cutting_quantity:
            # Responder con error si no hay suficiente stock
            return Response(
                {'detail': f'Not enough stock for this product. Available: {latest_stock.quantity if latest_stock else 0}, Requested: {cutting_quantity}'},
                status=status.HTTP_409_CONFLICT
            )

        # Si hay suficiente stock, crea la orden
        try:
            order = serializer.save(assigned_by=request.user)
            return Response(CuttingOrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View para detalle, actualización y eliminación de órdenes de corte
@extend_schema(
    methods=['GET'],
    operation_id="retrieve_cutting_order",
    description="Retrieve details of a specific cutting order",
    responses={200: CuttingOrderSerializer, 404: "Cutting order not found"},
)
@extend_schema(
    methods=['PUT', 'PATCH'],
    operation_id="update_cutting_order",
    description="Update details of a specific cutting order",
    request=CuttingOrderSerializer,
    responses={200: CuttingOrderSerializer, 400: "Bad Request - Invalid data"},
)
@extend_schema(
    methods=['DELETE'],
    operation_id="delete_cutting_order",
    description="Delete a specific cutting order",
    responses={204: "Cutting order deleted", 404: "Cutting order not found"},
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def cutting_order_detail_view(request, pk):
    """
    Endpoint para obtener, actualizar o eliminar una orden de corte específica.
    """
    try:
        order = CuttingOrder.objects.get(pk=pk)
    except CuttingOrder.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return get_cutting_order(order)

    elif request.method in ['PUT', 'PATCH']:
        return update_cutting_order(request, order)

    elif request.method == 'DELETE':
        return delete_cutting_order(order)


def get_cutting_order(order):
    """Obtener los detalles de una orden de corte."""
    serializer = CuttingOrderSerializer(order)
    return Response(serializer.data)


def update_cutting_order(request, order):
    """Actualizar una orden de corte, incluidas actualizaciones parciales."""
    serializer = CuttingOrderSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        try:
            updated_order = serializer.save()

            # Si la orden se completa, ejecutar lógica de corte
            if updated_order.status == 'completed':
                complete_cutting(updated_order)

            return Response(CuttingOrderSerializer(updated_order).data)

        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def delete_cutting_order(order):
    """Eliminar una orden de corte."""
    order.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# Lógica de finalización de una orden de corte
def complete_cutting(order):
    """
    Completa una orden de corte, actualiza el stock y marca la orden como 'completed'.
    """
    if order.status != 'in_process':
        raise ValueError("The operation must be in 'in_process' status to be completed.")

    latest_stock = order.product.latest_stock  # Obtener el último stock disponible

    # Verificar si hay suficiente stock para completar la operación
    if latest_stock.quantity < order.cutting_quantity:
        raise ValidationError(f"The cutting quantity ({order.cutting_quantity}) cannot exceed the available stock ({latest_stock.quantity}).")

    # Actualizar el stock del producto
    latest_stock.quantity -= order.cutting_quantity
    latest_stock.save()

    # Marcar la orden como completada
    order.status = 'completed'
    order.completed_at = timezone.now()
    order.save()
