from apps.products.api.serializers import CategorySerializer

# Documento para listar todas las categorías activas
list_category_doc = {
    'operation_id': 'list_categories',
    'summary': 'Recupera todas las categorías activas.',
    'description': (
        'Recupera una lista paginada de todas las categorías activas. Accesible solo para usuarios autenticados.\n'
        '⚠️ Nota: Este endpoint puede entregar datos cacheados durante un breve período (TTL: 5 minutos) para optimizar el rendimiento. '
        'Los cambios recientes pueden no reflejarse de inmediato.'
    ),
    'tags': ['Categories'],
    'security': [{'jwtAuth': []}],
    'parameters': [
        {
            'name': 'name',
            'in': 'query',
            'description': 'Filtra por nombre de la categoría',
            'required': False,
            'schema': {'type': 'string'}
        },
    ],
    'responses': {
        200: {
            'description': 'Lista paginada de categorías activas.',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'count': {'type': 'integer'},
                            'next': {'type': 'string', 'format': 'uri', 'nullable': True},
                            'previous': {'type': 'string', 'format': 'uri', 'nullable': True},
                            'results': {'type': 'array', 'items': {'$ref': '#/components/schemas/CategorySerializer'}}
                        }
                    }
                }
            }
        }
    }
}

# Documento para crear una nueva categoría
create_category_doc = {
    'operation_id': 'create_category',
    'summary': 'Crea una nueva categoría.',
    'description': (
        'Crea una nueva categoría. Solo accesible para administradores.\n'
        'ℹ️ Este endpoint invalida la cache de las categorías al completarse correctamente.'
    ),
    'tags': ['Categories'],
    'security': [{'jwtAuth': []}],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/CategorySerializer'}
            }
        }
    },
    'responses': {
        201: {
            'description': 'Categoría creada correctamente.',
            'content': {
                'application/json': {
                    'schema': {'$ref': '#/components/schemas/CategorySerializer'}
                }
            }
        },
        400: {'description': 'Datos inválidos'},
        403: {'description': 'Prohibido - Solo administradores pueden crear categorías'}
    }
}

# Documento para recuperar una categoría por ID
get_category_by_id_doc = {
    'operation_id': 'retrieve_category',
    'summary': 'Recupera una categoría por su ID.',
    'description': (
        'Recupera los detalles de una categoría específica por su ID.\n'
        '⚠️ Nota: Este endpoint puede entregar datos cacheados durante un breve período (TTL: 5 minutos).'
    ),
    'tags': ['Categories'],
    'security': [{'jwtAuth': []}],
    'parameters': [
        {
            'name': 'category_pk',
            'in': 'path',
            'required': True,
            'description': 'ID de la categoría',
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {
            'description': 'Detalles de la categoría.',
            'content': {
                'application/json': {
                    'schema': {'$ref': '#/components/schemas/CategorySerializer'}
                }
            }
        },
        404: {'description': 'Categoría no encontrada'}
    }
}

# Documento para actualizar una categoría por ID
update_category_by_id_doc = {
    'operation_id': 'update_category',
    'summary': 'Actualiza una categoría.',
    'description': (
        'Actualiza los detalles de una categoría específica.\n'
        'ℹ️ Este endpoint invalida la cache de las categorías al completarse correctamente.'
    ),
    'tags': ['Categories'],
    'security': [{'jwtAuth': []}],
    'parameters': [
        {
            'name': 'category_pk',
            'in': 'path',
            'required': True,
            'description': 'ID de la categoría',
            'schema': {'type': 'integer'}
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/CategorySerializer'}
            }
        }
    },
    'responses': {
        200: {
            'description': 'Categoría actualizada correctamente.',
            'content': {
                'application/json': {
                    'schema': {'$ref': '#/components/schemas/CategorySerializer'}
                }
            }
        },
        400: {'description': 'Datos inválidos'},
        403: {'description': 'No tienes permisos para modificar esta categoría.'},
        404: {'description': 'Categoría no encontrada'}
    }
}

# Documento para eliminar (soft delete) una categoría por ID
delete_category_by_id_doc = {
    'operation_id': 'delete_category',
    'summary': 'Elimina una categoría.',
    'description': (
        'Elimina suavemente una categoría específica (soft delete). Solo usuarios administradores pueden realizar esta acción.\n'
        'ℹ️ Este endpoint invalida la cache de las categorías al completarse correctamente.'
    ),
    'tags': ['Categories'],
    'security': [{'jwtAuth': []}],
    'parameters': [
        {
            'name': 'category_pk',
            'in': 'path',
            'required': True,
            'description': 'ID de la categoría',
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        204: {'description': 'Categoría eliminada correctamente (soft).'},
        403: {'description': 'No tienes permisos para eliminar esta categoría.'},
        404: {'description': 'Categoría no encontrada'}
    }
}
