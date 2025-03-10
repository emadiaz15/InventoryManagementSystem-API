# apps/stocks/api/views/product_stock_event_history.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema

from apps.users.permissions import IsStaffOrReadOnly
from apps.stocks.api.serializers.stock_event_serializer import StockEventSerializer
from apps.stocks.api.repositories import ProductRepository
from apps.stocks.docs.stock_event_doc import stock_event_history_doc
from apps.products.models.product_model import Product

@extend_schema(**stock_event_history_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def product_stock_event_history(request, pk):
    """
    Obtiene el historial de eventos de stock para un producto.
    Los eventos incluyen entradas, salidas y ajustes.
    """
    try:
        # Obtener el stock asociado al producto
        stock = ProductRepository.get_product_stock(pk)

        # Validar si existe el stock
        if not stock:
            return Response({"detail": "No se encontró stock para el producto."}, status=status.HTTP_404_NOT_FOUND)

        # Obtener eventos de stock optimizados
        stock_events = stock.events.select_related("user").order_by('-created_at')

        # Si no hay eventos registrados, responder con un mensaje claro
        if not stock_events.exists():
            return Response({"detail": "No hay eventos registrados para este stock."}, status=status.HTTP_200_OK)

        # Serializar los eventos de stock
        serializer = StockEventSerializer(stock_events, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Product.DoesNotExist:
        return Response({"detail": "El producto no existe."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
