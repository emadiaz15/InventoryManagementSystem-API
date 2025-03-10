from apps.cuts.api.serializers import CuttingOrderSerializer

# Documento para listar las órdenes de corte
list_cutting_orders_doc = {
    'operation_id': "list_cutting_orders",
    'description': "Recupera una lista de todas las órdenes de corte activas",
    'responses': {
        200: CuttingOrderSerializer(many=True),  # Respuesta con una lista de órdenes de corte
    },
}

# Documento para crear una orden de corte
create_cutting_order_doc = {
    'operation_id': "create_cutting_order",
    'description': "Crea una nueva orden de corte, verificando si hay suficiente stock",
    'request': CuttingOrderSerializer,  # El cuerpo de la solicitud será validado con el serializador 'CuttingOrderSerializer'
    'responses': {
        201: CuttingOrderSerializer,  # Respuesta exitosa con los detalles de la orden creada
        400: "Datos inválidos",  # Si la solicitud no es válida
        409: "Stock insuficiente",  # Si no hay suficiente stock para realizar la orden de corte
    },
}

# Documento para recuperar una orden de corte por ID
get_cutting_order_by_id_doc = {
    'operation_id': "retrieve_cutting_order",
    'description': "Recupera los detalles de una orden de corte específica",
    'responses': {
        200: CuttingOrderSerializer,  # Respuesta con los detalles de la orden de corte solicitada
        404: "Orden de corte no encontrada",  # Si no se encuentra la orden de corte
    },
}

# Documento para actualizar una orden de corte por ID
update_cutting_order_by_id_doc = {
    'operation_id': "update_cutting_order",
    'description': "Actualiza una orden de corte específica",
    'request': CuttingOrderSerializer,  # El cuerpo de la solicitud será validado con el serializador 'CuttingOrderSerializer'
    'responses': {
        200: CuttingOrderSerializer,  # Respuesta exitosa con los detalles de la orden de corte actualizada
        400: "Datos inválidos",  # Si la solicitud no es válida
    },
}

# Documento para eliminar una orden de corte por ID
delete_cutting_order_by_id_doc = {
    'methods': ['DELETE'],  # Método DELETE para eliminar
    'operation_id': "delete_cutting_order",
    'description': "Elimina suavemente una orden de corte específica",
    'responses': {
        204: "Orden de corte eliminada (soft)",  # Respuesta cuando la orden se elimina correctamente
        404: "Orden de corte no encontrada",  # Si no se encuentra la orden de corte
    },
}
