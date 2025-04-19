from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404 

from apps.stocks.api.serializers.stock_event_serializer import StockEventSerializer
from apps.stocks.api.repositories.stock_product_repository import StockProductRepository
from apps.products.models.product_model import Product
from apps.stocks.models.stock_event_model import StockEvent
from apps.stocks.docs.stock_event_doc import stock_event_history_doc

@extend_schema(**stock_event_history_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_stock_event_history(request, pk):
    """
    Obtiene el historial de eventos de stock para un producto específico
    (cuando el producto NO tiene subproductos y usa ProductStock).
    Requiere que el usuario esté autenticado.
    """
    # 1. Verificar que el producto existe y está activo
    product = get_object_or_404(Product, pk=pk, status=True)

    # 2. Obtener el registro de ProductStock asociado
    stock_record = StockProductRepository.get_stock_for_product(product)
    if not stock_record:
        return Response(
            {"detail": "No se encontró un registro de stock directo para este producto."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 3. Recuperar eventos de stock, más recientes primero
    events = StockEvent.objects.filter(
        product_stock=stock_record
    ).select_related('created_by').order_by('-created_at')

    # 4. Devolver lista vacía si no hay eventos
    if not events.exists():
        return Response([], status=status.HTTP_200_OK)

    # 5. Serializar y devolver
    serializer = StockEventSerializer(events, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
