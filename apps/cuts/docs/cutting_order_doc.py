from apps.cuts.api.serializers import CuttingOrderSerializer

# Documento para listar TODAS las órdenes de corte
list_cutting_orders_doc = {
    'operation_id': 'list_cutting_orders',
    'description': (
        'Recupera una lista paginada de todas las órdenes de corte activas. '
        'Accesible para cualquier usuario autenticado.'
    ),
    'responses': {
        200: 'Lista paginada de órdenes de corte activas.'
    },
}

# Documento para listar las órdenes de corte asignadas al usuario
list_assigned_cutting_orders_doc = {
    'operation_id': 'list_assigned_cutting_orders',
    'description': (
        'Recupera una lista paginada de las órdenes de corte que están asignadas '
        'al usuario autenticado.'
    ),
    'responses': {
        200: CuttingOrderSerializer(many=True)
    },
}

# Documento para crear una orden de corte
create_cutting_order_doc = {
    'operation_id': 'create_cutting_order',
    'description': (
        'Crea una nueva orden de corte. Solo usuarios staff pueden crear órdenes de corte.'
    ),
    'request': CuttingOrderSerializer,
    'responses': {
        201: CuttingOrderSerializer,
        400: 'Datos inválidos',
        403: 'Forbidden - El usuario no tiene permisos para crear órdenes.'
    },
}

# Documento para recuperar una orden de corte por ID
get_cutting_order_by_id_doc = {
    'operation_id': 'retrieve_cutting_order',
    'description': 'Recupera los detalles de una orden de corte específica por su ID.',
    'responses': {
        200: CuttingOrderSerializer,
        404: 'Orden de corte no encontrada'
    },
}

# Documento para actualizar una orden de corte por ID
update_cutting_order_by_id_doc = {
    'operation_id': 'update_cutting_order',
    'description': (
        'Actualiza una orden de corte específica. '
        '• Staff puede modificar cualquier campo. '
        '• Usuario asignado solo puede actualizar el campo workflow_status.'
    ),
    'request': CuttingOrderSerializer,
    'responses': {
        200: CuttingOrderSerializer,
        400: 'Datos inválidos',
        403: 'Forbidden - No tienes permisos para modificar esta orden.'
    },
}

# Documento para eliminar (soft delete) una orden de corte por ID
delete_cutting_order_by_id_doc = {
    'methods': ['DELETE'],
    'operation_id': 'delete_cutting_order',
    'description': (
        'Elimina suavemente una orden de corte específica (soft delete). '
        'Solo usuarios staff pueden realizar esta acción.'
    ),
    'responses': {
        204: 'Orden de corte eliminada correctamente (soft).',
        403: 'Forbidden - No tienes permisos para eliminar esta orden.',
        404: 'Orden de corte no encontrada',
    },
}
