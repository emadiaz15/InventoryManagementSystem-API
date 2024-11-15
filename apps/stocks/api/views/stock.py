from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.stocks.models import Stock, StockHistory
from apps.stocks.api.serializers import StockSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(
    methods=['GET'],
    operation_id="list_stocks",
    description="Recupera una lista de todos los registros de stock activos",
    responses={200: StockSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_stocks_view(request):
    """
    Endpoint para listar todos los registros de stock activos.
    """
    # Recupera todos los registros de stock activos
    stocks = Stock.objects.filter(is_active=True)
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
@permission_classes([IsAuthenticated])
def create_stock_view(request):
    """
    Endpoint para crear un nuevo registro de stock.
    """
    # Serializa y valida los datos de entrada
    serializer = StockSerializer(data=request.data)
    if serializer.is_valid():
        # Guarda el nuevo registro de stock y asigna el usuario que realiza la creación
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # Devuelve errores de validación
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['GET'],
    operation_id="retrieve_stock",
    description="Recupera los detalles de un registro de stock específico",
    responses={200: StockSerializer, 404: "Stock no encontrado"},
)
@extend_schema(
    methods=['PUT'],
    operation_id="update_stock",
    description="Actualiza los detalles de un registro de stock y registra el cambio en el historial de stock",
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
    responses={204: "Stock eliminado correctamente (soft delete)", 404: "Stock no encontrado"},
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def stock_detail_view(request, pk=None):
    """
    Endpoint para obtener, actualizar o eliminar de manera suave un registro de stock específico.
    """
    try:
        # Recupera el registro de stock por su clave primaria (pk) y verifica que esté activo
        stock = Stock.objects.get(pk=pk, is_active=True)
    except Stock.DoesNotExist:
        return Response({'detail': 'Stock no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Serializa y devuelve los datos del registro de stock
        serializer = StockSerializer(stock)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Obtiene la cantidad y la razón del cambio de stock de los datos de entrada
        new_quantity = request.data.get('quantity')
        change_reason = request.data.get('change_reason', 'Actualización de stock')
        
        if new_quantity is None:
            return Response({'detail': 'El campo cantidad es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_quantity < 0:
            return Response({'detail': 'La cantidad no puede ser negativa'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Guarda la cantidad anterior para el historial y actualiza el stock
            stock_before = stock.quantity
            stock.quantity = new_quantity
            stock.save()

            # Registra el cambio en el historial de stock
            change_type = 'increase' if new_quantity > stock_before else 'decrease'
            StockHistory.objects.create(
                product=stock.product,
                subproduct=stock.subproduct,
                stock_before=stock_before,
                stock_after=new_quantity,
                change_reason=change_reason,
                change_type=change_type,
                user=request.user
            )
            
            # Serializa y devuelve los datos actualizados
            serializer = StockSerializer(stock)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # Devuelve un error si ocurre alguna excepción durante la actualización
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Marca el registro de stock como inactivo en lugar de eliminarlo permanentemente
        stock.is_active = False
        stock.save()

        # Registra la eliminación en el historial de stock
        StockHistory.objects.create(
            product=stock.product,
            subproduct=stock.subproduct,
            stock_before=stock.quantity,
            stock_after=0,
            change_reason="Eliminación suave de stock",
            user=request.user
        )

        return Response({'message': 'Stock eliminado correctamente (soft delete)'}, status=status.HTTP_204_NO_CONTENT)
