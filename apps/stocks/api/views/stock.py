from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema

from apps.stocks.models import Stock, StockHistory
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
    
    - Usuarios no staff: pueden leer.
    - Usuarios staff: pueden también crear, eliminar, etc. (pero este endpoint solo es GET).
    """
    # Filtro opcional por producto
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
    Endpoint para crear un nuevo registro de stock.
    - Solo staff puede crear (POST).
    """
    serializer = StockSerializer(data=request.data)
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
    description="Actualiza los detalles de un registro de stock y registra el cambio en el historial",
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
    - PUT: Modificación para todos los autenticados.
    - DELETE: Solo staff.
    """
    try:
        stock = Stock.objects.get(pk=pk, is_active=True)
    except Stock.DoesNotExist:
        return Response({'detail': 'Stock not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Solo lectura
        serializer = StockSerializer(stock)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Usuarios no staff pueden modificar también
        serializer = StockSerializer(stock, data=request.data, partial=True)
        if serializer.is_valid():
            stock_before = stock.quantity
            new_quantity = serializer.validated_data.get('quantity', stock_before)

            # Registrar el cambio en el historial
            StockHistory.objects.create(
                product=stock.product,
                stock_before=stock_before,
                stock_after=new_quantity,
                change_reason=serializer.validated_data.get('change_reason', 'Stock update'),
                user=request.user
            )

            # Actualizar el stock
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Solo staff puede eliminar (soft delete)
        if not stock.is_active:
            return Response({'detail': 'Stock already inactive'}, status=status.HTTP_400_BAD_REQUEST)

        StockHistory.objects.create(
            product=stock.product,
            stock_before=stock.quantity,
            stock_after=0,
            change_reason="Soft deletion of stock",
            user=request.user
        )

        stock.is_active = False
        stock.quantity = 0
        stock.save()
        return Response({'detail': 'Stock set to inactive successfully.'}, status=status.HTTP_204_NO_CONTENT)
