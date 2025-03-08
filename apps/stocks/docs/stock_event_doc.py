stock_event_history_doc = {
    'operation_id': "get_stock_event_history",
    'description': "Obtiene el historial de eventos de stock para un producto o subproducto. Los eventos incluyen entradas, salidas y ajustes.",
    'parameters': [
        {
            'name': 'pk',
            'in': 'path',
            'description': 'ID del producto o subproducto',
            'required': True,
            'schema': {'type': 'integer'}
        },
        {
            'name': 'entity_type',
            'in': 'path',
            'description': 'Tipo de entidad (producto o subproducto)',
            'required': True,
            'schema': {'type': 'string', 'enum': ['product', 'subproduct']}
        }
    ],
    'responses': {
        200: "Historial de eventos de stock obtenido correctamente",
        400: "Tipo de entidad no válido o parámetros incorrectos",
        404: "Producto o subproducto no encontrado"
    }
}
