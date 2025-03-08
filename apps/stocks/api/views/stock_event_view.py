from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema

from apps.users.permissions import IsStaffOrReadOnly

from apps.stocks.models.stock_event_model import StockEvent
from apps.stocks.models.stock_model import Stock

from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct


from apps.stocks.api.serializers.stock_event_serializer import StockEventSerializer

from apps.stocks.docs.stock_event_doc import (stock_event_history_doc)

@extend_schema(**stock_event_history_doc)

@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def stock_event_history(request, pk, entity_type):
    """
    Obtiene el historial de eventos de stock para un producto o subproducto.
    Los eventos incluyen entradas, salidas y ajustes.
    """
    try:
        # Determinar si el `pk` corresponde a un producto o subproducto
        if entity_type == 'product':
            product = Product.objects.get(pk=pk)
            stock = Stock.objects.get(product=product)
        elif entity_type == 'subproduct':
            subproduct = Subproduct.objects.get(pk=pk)
            stock = Stock.objects.get(subproduct=subproduct)
        else:
            return Response({"detail": "Tipo de entidad no válido."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener los eventos de stock relacionados
        stock_events = StockEvent.objects.filter(stock=stock).order_by('-created_at')

        # Serializar los eventos de stock
        serializer = StockEventSerializer(stock_events, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except (Product.DoesNotExist, Subproduct.DoesNotExist, Stock.DoesNotExist):
        return Response({"detail": "Producto o subproducto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
