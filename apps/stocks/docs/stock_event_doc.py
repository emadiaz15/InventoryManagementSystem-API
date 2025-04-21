stock_event_history_doc = {
    'operation_id': 'stockEventHistory',
    'summary': 'Obtiene el historial de eventos de stock para un producto o subproducto específico.',
    'description': 'Recupera el historial de eventos de stock para un producto o subproducto específico.',
    'tags': ['Stock Events'],
    'security': [{'jwtAuth': []}],  # Aquí se aplica correctamente la seguridad
    'parameters': [
        {
            'name': 'pk',
            'in': 'path',
            'required': True,
            'description': 'ID del producto (para historial de producto) o del subproducto (para historial de subproducto)',
            'schema': {'type': 'integer', 'example': 1}
        },
        {
            'name': 'product_pk',
            'in': 'path',
            'required': False,
            'description': 'ID del producto padre (solo requerido para historial de subproducto)',
            'schema': {'type': 'integer', 'example': 1}
        },
        {
            'name': 'subproduct_pk',
            'in': 'path',
            'required': False,
            'description': 'ID del subproducto (solo requerido para historial de subproducto)',
            'schema': {'type': 'integer', 'example': 3}
        },
    ],
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
            'description': 'Solicitud incorrecta o tipo de entidad inválido.'
        },
        404: {
            'description': 'No se encontró stock o la entidad no existe.'
        },
        500: {
            'description': 'Error interno del servidor.'
        }
    }
}
