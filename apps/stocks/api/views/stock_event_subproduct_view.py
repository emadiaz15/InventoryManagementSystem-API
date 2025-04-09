from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

from apps.users.permissions import IsStaffOrReadOnly
from apps.stocks.api.serializers.stock_event_serializer import StockEventSerializer

from apps.stocks.api.repositories.stock_subproduct_repository import StockSubproductRepository

from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.models.stock_event_model import StockEvent


from apps.stocks.docs.stock_event_doc import stock_event_history_doc 

@extend_schema(**stock_event_history_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def subproduct_stock_event_history(request, product_pk, subproduct_pk): # Renombrado parámetro
    """
    Obtiene el historial de eventos de stock para un subproducto específico.
    """
    # 1. Validar que el subproducto existe y pertenece al producto padre
    subproduct = get_object_or_404(Subproduct, pk=subproduct_pk, parent_id=product_pk, status=True)
    # Si no existe o no pertenece al padre, get_object_or_404 dará 404

    # 2. Obtener TODOS los eventos asociados a CUALQUIER registro de stock
    #    de este subproducto específico.
    #    Filtramos StockEvent directamente.
    stock_events = StockEvent.objects.filter(
        subproduct_stock__subproduct=subproduct # Filtra por el subproducto a través del FK en StockEvent
        # Opcional: podrías querer filtrar solo por registros de stock activos:
        # subproduct_stock__status=True
    ).select_related('created_by', 'subproduct_stock').order_by('-created_at') # Optimizamos y ordenamos

    # 3. Si no hay eventos, devolver lista vacía
    if not stock_events.exists():
        return Response([], status=status.HTTP_200_OK)

    # 4. Serializar los eventos (¡Añadir contexto!)
    serializer = StockEventSerializer(stock_events, many=True, context={'request': request})

    return Response(serializer.data, status=status.HTTP_200_OK)

    # El try/except genérico se elimina, get_object_or_404 maneja DoesNotExist
