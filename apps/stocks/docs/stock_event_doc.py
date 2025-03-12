stock_event_history_doc = {
    'operation_id': 'stockEventHistory',
    'responses': {
        200: {
            'description': 'Historial de eventos de stock recuperado correctamente.',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "stock": 1,
                            "quantity_change": 10,
                            "event_type": "entrada",
                            "location": "Almacén A",
                            "created_at": "2025-03-10T12:00:00Z",
                            "user": {
                                "id": 1,
                                "username": "admin"
                            }
                        }
                    ]
                }
            }
        },
        400: {
            'description': 'Tipo de entidad no válido. Usa "product" o "subproduct".'
        },
        404: {
            'description': 'No se encontró stock o la entidad no existe.'
        },
        500: {
            'description': 'Error interno del servidor.'
        }
    },
    'parameters': [
        {
            'name': 'pk',
            'in': 'path',
            'required': True,
            'description': 'ID del producto o subproducto para el cual se obtiene el historial de eventos.',
            'schema': {
                'type': 'integer',
                'example': 1
            }
        },
        {
            'name': 'entity_type',
            'in': 'path',
            'required': True,
            'description': 'Tipo de entidad, puede ser "product" o "subproduct".',
            'schema': {
                'type': 'string',
                'example': 'product'
            }
        }
    ]
}
