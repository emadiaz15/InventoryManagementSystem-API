from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.stocks.models import Stock
from apps.stocks.api.serializers import StockSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(
    methods=['GET'],
    operation_id="list_stocks",
    description="Retrieve a list of all available stocks",
    responses={200: StockSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_stocks_view(request):
    """
    Endpoint para listar todos los registros de stock.
    """
    stocks = Stock.objects.all()
    serializer = StockSerializer(stocks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    methods=['POST'],
    operation_id="create_stock",
    description="Create a new stock entry",
    request=StockSerializer,
    responses={
        201: StockSerializer,
        400: "Bad Request - Invalid data",
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_stock_view(request):
    """
    Endpoint para crear un nuevo registro de stock.
    """
    serializer = StockSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)  # Asigna el usuario que realiza la creación
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['GET'],
    operation_id="retrieve_stock",
    description="Retrieve details of a specific stock",
    responses={200: StockSerializer, 404: "Stock not found"},
)
@extend_schema(
    methods=['PUT'],
    operation_id="update_stock",
    description="Update details of a specific stock. This also records the update in stock history.",
    request=StockSerializer,
    responses={
        200: StockSerializer,
        400: "Bad Request - Invalid data",
    },
)
@extend_schema(
    methods=['DELETE'],
    operation_id="delete_stock",
    description="Delete a specific stock",
    responses={204: "Stock deleted successfully", 404: "Stock not found"},
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def stock_detail_view(request, pk=None):
    """
    Endpoint para obtener, actualizar o eliminar un registro de stock específico.
    """
    try:
        stock = Stock.objects.get(pk=pk)
    except Stock.DoesNotExist:
        return Response({'detail': 'Stock not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StockSerializer(stock)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        new_quantity = request.data.get('quantity')
        change_reason = request.data.get('change_reason', 'Update stock')
        
        if new_quantity is None:
            return Response({'detail': 'Quantity field is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Usa el método `update_stock` del modelo Stock para manejar el cambio
            stock.update_stock(new_quantity=new_quantity, reason=change_reason, user=request.user)
            serializer = StockSerializer(stock)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        stock.delete()
        return Response({'message': 'Stock deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
