# Documentation for listing subproducts
list_subproducts_doc = {
    'operation_id': "list_subproducts",
    'description': "Recupera una lista de subproductos (productos hijo) para un producto padre específico con paginación",
    'parameters': [
        {
            'name': 'product_pk',
            'in': 'path',
            'description': 'ID del producto padre',
            'required': True,
            'schema': {'type': 'integer'}
        },
    ],
    'responses': {
        200: "Lista de subproductos con paginación para el producto padre",
        404: "Producto padre no encontrado o inactivo"
    }
}

# Documentation for creating a subproduct
create_subproduct_doc = {
    'operation_id': "create_subproduct",
    'description': "Crea un nuevo subproducto (producto hijo) asociado a un producto padre",
    'request': "ProductSerializer",
    'responses': {
        201: "Subproducto creado correctamente",
        400: "Solicitud Incorrecta - Datos inválidos"
    }
}

# Documentation for retrieving a specific subproduct
get_subproduct_by_id_doc = {
    'operation_id': "retrieve_subproduct",
    'description': "Recupera los detalles de un subproducto específico",
    'responses': {
        200: "Detalles del subproducto",
        404: "Subproducto no encontrado"
    }
}

# Documentation for updating a specific subproduct
update_product_by_id_doc = {
    'operation_id': "update_subproduct",
    'description': "Actualiza los detalles de un subproducto específico",
    'request': "ProductSerializer",
    'responses': {
        200: "Subproducto actualizado correctamente",
        400: "Solicitud Incorrecta - Datos inválidos"
    }
}

# Documentation for deleting a subproduct
delete_product_by_id_doc = {
    'operation_id': "delete_subproduct",
    'description': "Elimina suavemente un subproducto, estableciendo su status en False",
    'responses': {
        204: "Subproducto eliminado correctamente",
        404: "Subproducto no encontrado"
    },
}
