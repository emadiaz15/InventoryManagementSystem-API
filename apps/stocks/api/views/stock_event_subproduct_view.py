from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

from apps.stocks.api.serializers.stock_event_serializer import StockEventSerializer
from apps.stocks.models.stock_event_model import StockEvent
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.docs.stock_event_doc import stock_event_history_doc

@extend_schema(
    summary=stock_event_history_doc["summary"],
    description=stock_event_history_doc["description"],
    tags=stock_event_history_doc["tags"],
    operation_id=stock_event_history_doc["operation_id"],
    parameters=stock_event_history_doc["parameters"],
    responses=stock_event_history_doc["responses"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subproduct_stock_event_history(request, product_pk, subproduct_pk):
    """
    Obtiene el historial de eventos de stock para un subproducto específico.
    Requiere que el usuario esté autenticado.
    """
    # 1. Validar existencia y pertenencia al producto padre
    subproduct = get_object_or_404(
        Subproduct,
        pk=subproduct_pk,
        parent_id=product_pk,
        status=True
    )

    # 2. Recuperar todos los eventos de stock para ese subproducto
    stock_events = StockEvent.objects.filter(
        subproduct_stock__subproduct=subproduct
    ).select_related('created_by', 'subproduct_stock').order_by('-created_at')

    # 3. Si no hay eventos, devolvemos una lista vacía
    if not stock_events.exists():
        return Response([], status=status.HTTP_200_OK)

    # 4. Serializar y devolver
    serializer = StockEventSerializer(stock_events, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
