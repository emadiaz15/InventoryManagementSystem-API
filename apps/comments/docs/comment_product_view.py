# Documentation for listing comments of a product
list_comments_doc = {
    'operation_id': "list_product_comments",
    'description': "Recupera una lista de todos los comentarios activos para un producto, ordenados del más reciente al más antiguo",
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'description': 'ID del producto padre',
            'required': True,
            'schema': {'type': 'integer'}
        },
    ],
    'responses': {
        200: "Lista de comentarios activos ordenados del más reciente al más antiguo",
        404: "Producto no encontrado"
    }
}


# Documentation for creating a comment on a product
create_comment_doc = {
    'operation_id': "create_product_comment",
    'description': "Crea un nuevo comentario sobre un producto",
    'request': "ProductCommentSerializer",
    'responses': {
        201: "Comentario creado correctamente",
        400: "Solicitud incorrecta - Datos inválidos"
    }
}


# Documentation for retrieving a specific product comment
get_comment_by_id_doc = {
    'operation_id': "retrieve_product_comment",
    'description': "Recupera los detalles de un comentario específico de un producto",
    'responses': {
        200: "Detalles del comentario",
        404: "Comentario no encontrado"
    }
}


# Documentation for updating a specific product comment
update_comment_doc = {
    'operation_id': "update_product_comment",
    'description': "Actualiza un comentario específico de un producto",
    'request': "ProductCommentSerializer",
    'responses': {
        200: "Comentario actualizado correctamente",
        400: "Solicitud incorrecta - Datos inválidos"
    }
}

# Documentation for deleting a specific product comment
delete_comment_doc = {
    'operation_id': "delete_product_comment",
    'description': "Elimina suavemente un comentario de producto, estableciendo su estado como inactivo (soft delete)",
    'responses': {
        204: "Comentario eliminado correctamente (soft delete)",
        404: "Comentario no encontrado"
    }
}
