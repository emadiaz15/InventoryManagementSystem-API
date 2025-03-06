list_product_doc = {
    'operation_id': "list_products",
    'description': "Recupera una lista de todos los productos o filtra por categoría o tipo.",
    'parameters': [
        {
            'name': 'category',
            'in': 'query',
            'description': 'Filtra productos por ID de categoría',
            'required': False,
            'schema': {'type': 'integer'}
        },
        {
            'name': 'type',
            'in': 'query',
            'description': 'Filtra productos por ID de tipo',
            'required': False,
            'schema': {'type': 'integer'}
        },
        {
            'name': 'status',
            'in': 'query',
            'description': 'Filtra productos activos',
            'required': False,
            'schema': {'type': 'boolean'}
        },
    ],
    'responses': {
        200: "Lista de productos con paginación y filtrados según los parámetros"
    }
}

create_product_doc = {
    'operation_id': "create_product",
    'description': "Crea un nuevo producto. Si se incluye 'stock_quantity', se creará un registro de Stock inicial.",
    'request': "ProductSerializer",
    'responses': {
        201: "Producto creado correctamente",
        400: "Solicitud Incorrecta - Datos inválidos"
    }
}

get_product_by_id_doc = {
    'operation_id': "retrieve_product",
    'description': "Recupera detalles de un producto específico, incluyendo su stock y comentarios.",
    'responses': {
        200: "Detalles del producto",
        404: "Producto no encontrado"
    }
}

update_product_by_id_doc = {
    'operation_id': "update_product",
    'description': "Actualiza los detalles de un producto específico y opcionalmente actualiza stock.",
    'request': "ProductSerializer",
    'responses': {
        200: "Producto actualizado correctamente",
        400: "Solicitud Incorrecta - Datos inválidos"
    }
}

delete_product_by_id_doc = {
    'methods': ['DELETE'],
    'operation_id': "delete_product",
    'description': "Elimina suavemente un producto específico estableciendo status en False.",
    'responses': {
        204: "Producto marcado como inactivo",
        404: "Producto no encontrado"
    },
}