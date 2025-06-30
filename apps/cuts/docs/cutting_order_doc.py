from apps.cuts.api.serializers import CuttingOrderSerializer

# Documento para listar TODAS las órdenes de corte
list_cutting_orders_doc = {
    'operation_id': 'list_cutting_orders',
    'summary': 'Recupera una lista de todas las órdenes de corte activas.',
    'description': 'Recupera una lista paginada de todas las órdenes de corte activas. Accesible para cualquier usuario autenticado.',
    'tags': ['Cutting Orders'],
    'security': [{'jwtAuth': []}],
    'parameters': [],  # Agregado: los parámetros para este endpoint, si los tuviera, deben estar aquí
    'responses': {
        200: {
            'description': 'Lista paginada de órdenes de corte activas.',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'count': {'type': 'integer'},
                            'next': {'type': 'string', 'format': 'uri', 'nullable': True},
                            'previous': {'type': 'string', 'format': 'uri', 'nullable': True},
                            'results': {'type': 'array', 'items': {'$ref': '#/components/schemas/CuttingOrderSerializer'}}
                        }
                    }
                }
            }
        }
    },
}

# Documento para listar las órdenes de corte asignadas al usuario
list_assigned_cutting_orders_doc = {
    'operation_id': 'list_assigned_cutting_orders',
    'summary': 'Recupera las órdenes de corte asignadas al usuario autenticado.',
    'description': 'Recupera una lista paginada de las órdenes de corte que están asignadas al usuario autenticado.',
    'tags': ['Cutting Orders'],
    'security': [{'jwtAuth': []}],
    'parameters': [],  # Agregado: los parámetros para este endpoint, si los tuviera, deben estar aquí
    'responses': {
        200: {
            'description': 'Lista paginada de órdenes asignadas.',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'count': {'type': 'integer'},
                            'next': {'type': 'string', 'format': 'uri', 'nullable': True},
                            'previous': {'type': 'string', 'format': 'uri', 'nullable': True},
                            'results': {'type': 'array', 'items': {'$ref': '#/components/schemas/CuttingOrderSerializer'}}
                        }
                    }
                }
            }
        }
    }
}

# Documento para crear una orden de corte
create_cutting_order_doc = {
    'operation_id': 'create_cutting_order',
    'summary': 'Crea una nueva orden de corte.',
    'description': (
        'Crea una nueva orden de corte asociada a un producto y con múltiples subproductos. '
        'Solo usuarios staff pueden crear órdenes. El campo `operator_can_edit_items` '
        'indica si el operario asignado podrá modificar los items.'
    ),
    'tags': ['Cutting Orders'],
    'security': [{'jwtAuth': []}],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/CuttingOrderSerializer'}
            }
        }
    },
    'responses': {
        201: {
            'description': 'Orden creada correctamente.',
            'content': {
                'application/json': {
                    'schema': {'$ref': '#/components/schemas/CuttingOrderSerializer'}
                }
            }
        },
        400: {'description': 'Solicitud Incorrecta - Datos inválidos'},
        403: {'description': 'Prohibido - Solo staff puede crear órdenes.'}
    },
}

# Documento para recuperar una orden de corte por ID
get_cutting_order_by_id_doc = {
    'operation_id': 'retrieve_cutting_order',
    'summary': 'Recupera una orden de corte por ID.',
    'description': 'Recupera los detalles de una orden de corte específica por su ID.',
    'tags': ['Cutting Orders'],
    'security': [{'jwtAuth': []}],
    'parameters': [
        {
            'name': 'cuts_pk',
            'in': 'path',
            'required': True,
            'description': 'ID de la orden de corte',
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {
            'description': 'Detalles de la orden de corte.',
            'content': {
                'application/json': {
                    'schema': {'$ref': '#/components/schemas/CuttingOrderSerializer'}
                }
            }
        },
        404: {'description': 'Orden de corte no encontrada'}
    },
}

# Documento para actualizar una orden de corte por ID
update_cutting_order_by_id_doc = {
    'operation_id': 'update_cutting_order',
    'summary': 'Actualiza una orden de corte.',
    'description': (
        'Actualiza una orden de corte específica.\n\n'
        '• Usuarios staff pueden modificar cualquier campo.\n'
        '• Usuarios asignados pueden actualizar solo el campo `workflow_status`'
        ' o también los `items` cuando `operator_can_edit_items` es verdadero.'
    ),
    'tags': ['Cutting Orders'],
    'security': [{'jwtAuth': []}],
    'parameters': [
        {
            'name': 'cuts_pk',
            'in': 'path',
            'required': True,
            'description': 'ID de la orden de corte',
            'schema': {'type': 'integer'}
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/CuttingOrderSerializer'}
            }
        }
    },
    'responses': {
        200: {
            'description': 'Orden actualizada correctamente.',
            'content': {
                'application/json': {
                    'schema': {'$ref': '#/components/schemas/CuttingOrderSerializer'}
                }
            }
        },
        400: {'description': 'Datos inválidos'},
        403: {'description': 'No tienes permisos para modificar esta orden.'}
    },
}

# Documento para eliminar (soft delete) una orden de corte por ID
delete_cutting_order_by_id_doc = {
    'operation_id': 'delete_cutting_order',
    'summary': 'Elimina una orden de corte.',
    'description': (
        'Elimina suavemente una orden de corte específica (soft delete). '
        'Solo usuarios staff pueden realizar esta acción.'
    ),
    'tags': ['Cutting Orders'],
    'security': [{'jwtAuth': []}],
    'parameters': [
        {
            'name': 'cuts_pk',
            'in': 'path',
            'required': True,
            'description': 'ID de la orden de corte',
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        204: {'description': 'Orden eliminada correctamente (soft).'},
        403: {'description': 'No tienes permisos para eliminar esta orden.'},
        404: {'description': 'Orden no encontrada'}
    },
}
