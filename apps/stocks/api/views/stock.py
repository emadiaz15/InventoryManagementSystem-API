from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema

from apps.stocks.models import Stock
from apps.stocks.api.serializers import StockSerializer
from apps.users.permissions import IsStaffOrReadAndUpdateOnly


@extend_schema(
    methods=['GET'],
    operation_id="list_stocks",
    description="Recupera una lista de todos los registros de stock activos",
    responses={200: StockSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsStaffOrReadAndUpdateOnly])
def list_stocks_view(request):
    """
    Endpoint para listar todos los registros de stock activos.
    
    - Usuarios no staff: solo lectura (GET).
    - Usuarios staff: podrían crear/editar stock (pero no en este endpoint).
    """
    product_id = request.query_params.get('product')

    stocks = Stock.objects.filter(is_active=True)
    if product_id:
        stocks = stocks.filter(product_id=product_id)

    serializer = StockSerializer(stocks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    methods=['POST'],
    operation_id="create_stock",
    description="Crea un nuevo registro de stock",
    request=StockSerializer,
    responses={
        201: StockSerializer,
        400: "Solicitud incorrecta - Datos inválidos",
    },
)
@api_view(['POST'])
@permission_classes([IsStaffOrReadAndUpdateOnly])  # Solo staff puede crear
def create_stock_view(request):
    """
    Endpoint para crear un nuevo registro de stock (inicial).
    - Solo staff puede crear (POST).
    """
    serializer = StockSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        # Asigna el usuario actual al crear el registro de stock
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['GET'],
    operation_id="retrieve_stock",
    description="Recupera los detalles de un registro de stock específico",
    responses={200: StockSerializer, 404: "Stock not found"},
)
@extend_schema(
    methods=['PUT'],
    operation_id="update_stock",
    description="Actualiza los detalles de un registro de stock (puede cambiar la cantidad, ubicación, etc.)",
    request=StockSerializer,
    responses={
        200: StockSerializer,
        400: "Solicitud incorrecta - Datos inválidos",
    },
)
@extend_schema(
    methods=['DELETE'],
    operation_id="soft_delete_stock",
    description="Elimina de manera suave un registro de stock, marcándolo como inactivo",
    responses={204: "Stock set to inactive successfully.", 404: "Stock not found"},
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadAndUpdateOnly])  # GET y PUT para todos, DELETE solo staff
def stock_detail_view(request, pk=None):
    """
    Endpoint para obtener, actualizar o eliminar (soft) un registro de stock específico.
    
    - GET: Lectura para todos los autenticados.
    - PUT: Modificación para todos los autenticados (p.ej., cambiar cantidad o location).
    - DELETE: Solo staff (soft-delete que pone is_active=False).
    """
    try:
        stock = Stock.objects.get(pk=pk, is_active=True)
    except Stock.DoesNotExist:
        return Response({'detail': 'Stock not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StockSerializer(stock)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Permite actualización parcial (partial=True)
        serializer = StockSerializer(stock, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            # El método update del serializer se encargará de llamar a stock.apply_change
            # si la quantity cambió, registrando la operación en StockHistory.
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Solo staff puede eliminar (soft delete)
        # Llamamos a stock.soft_delete(...) en lugar de hacerlo manualmente.
        stock.soft_delete(reason="Soft deletion of stock", user=request.user)
        return Response({'detail': 'Stock set to inactive successfully.'}, status=status.HTTP_204_NO_CONTENT)
