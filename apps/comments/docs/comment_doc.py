# Documentation for listing comments of a product or subproduct
list_comments_doc = {
    'operation_id': "list_comments",
    'description': "Recupera una lista de todos los comentarios activos para un producto o subproducto, ordenados del más reciente al más antiguo",
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'description': 'ID del producto padre',
            'required': True,
            'schema': {'type': 'integer'}
        },
        {
            'name': 'subproduct_id',
            'in': 'path',
            'description': 'ID del subproducto hijo (opcional)',
            'required': False,
            'schema': {'type': 'integer'}
        },
    ],
    'responses': {
        200: "Lista de comentarios activos ordenados del más reciente al más antiguo",
        404: "Producto o subproducto no encontrado"
    }
}


# Documentation for creating a comment on a product or subproduct
create_comment_doc = {
    'operation_id': "create_comment",
    'description': "Crea un nuevo comentario sobre un producto o subproducto",
    'request': "CommentSerializer",
    'responses': {
        201: "Comentario creado correctamente",
        400: "Solicitud incorrecta - Datos inválidos"
    }
}


# Documentation for retrieving a specific comment
get_comment_by_id_doc = {
    'operation_id': "retrieve_comment",
    'description': "Recupera los detalles de un comentario específico",
    'responses': {
        200: "Detalles del comentario",
        404: "Comentario no encontrado"
    }
}


# Documentation for updating a specific comment
update_comment_doc = {
    'operation_id': "update_comment",
    'description': "Actualiza un comentario específico",
    'request': "CommentSerializer",
    'responses': {
        200: "Comentario actualizado correctamente",
        400: "Solicitud incorrecta - Datos inválidos"
    }
}

# Documentation for deleting a specific comment
delete_comment_doc = {
    'operation_id': "delete_comment",
    'description': "Elimina suavemente un comentario, estableciendo su estado como inactivo (soft delete)",
    'responses': {
        204: "Comentario eliminado correctamente (soft delete)",
        404: "Comentario no encontrado"
    }
}



