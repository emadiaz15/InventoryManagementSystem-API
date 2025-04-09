from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404 

from apps.users.permissions import IsStaffOrReadOnly
from apps.stocks.api.serializers.stock_event_serializer import StockEventSerializer

from apps.stocks.api.repositories.stock_product_repository import StockProductRepository

from apps.products.models.product_model import Product

from apps.stocks.models.stock_event_model import StockEvent

from apps.stocks.docs.stock_event_doc import stock_event_history_doc

@extend_schema(**stock_event_history_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def product_stock_event_history(request, pk):
    """
    Obtiene el historial de eventos de stock para un producto específico
    (asumiendo que este producto NO tiene subproductos y usa ProductStock).
    """
    # 1. Obtener la instancia del Producto
    product = get_object_or_404(Product, pk=pk, status=True)

    # 2. Obtener el registro de ProductStock asociado a este producto
    #    Usamos el método refactorizado del repositorio
    stock_record = StockProductRepository.get_stock_for_product(product)

    # 3. Validar si existe el registro de stock
    if not stock_record:
        # Si no hay ProductStock, no puede haber eventos asociados a él.
        return Response({"detail": "No se encontró un registro de stock directo para este producto."}, status=status.HTTP_404_NOT_FOUND)

    # 4. Obtener eventos de stock asociados a ESE registro de stock específico
    #    Usamos el related_name 'events' definido en StockEvent.product_stock
    #    Optimizamos incluyendo el usuario que creó el evento (heredado de BaseModel)
    stock_events = StockEvent.objects.filter(product_stock=stock_record).select_related('created_by').order_by('-created_at')
    # Alternativa usando related_name:
    # stock_events = stock_record.events.select_related('created_by').order_by('-created_at')

    # 5. Si no hay eventos, devolver OK con mensaje (no es un error 404)
    if not stock_events.exists():
        # Puedes devolver una lista vacía o un mensaje, una lista vacía es más estándar para API
        # return Response({"detail": "No hay eventos registrados para este stock."}, status=status.HTTP_200_OK)
        return Response([], status=status.HTTP_200_OK)

    # 6. Serializar los eventos (¡Añadir contexto!)
    serializer = StockEventSerializer(stock_events, many=True, context={'request': request})

    return Response(serializer.data, status=status.HTTP_200_OK)

    # El try/except genérico se elimina, get_object_or_404 maneja DoesNotExist
