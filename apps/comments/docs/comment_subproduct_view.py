# Documentation for listing comments of a subproduct
list_comments_doc = {
    'operation_id': "list_subproduct_comments",
    'description': "Recupera una lista de todos los comentarios activos para un subproducto, ordenados del más reciente al más antiguo",
    'parameters': [
        {
            'name': 'subproduct_id',
            'in': 'path',
            'description': 'ID del subproducto hijo',
            'required': True,
            'schema': {'type': 'integer'}
        },
    ],
    'responses': {
        200: "Lista de comentarios activos ordenados del más reciente al más antiguo",
        404: "Subproducto no encontrado"
    }
}


# Documentation for creating a comment on a subproduct
create_comment_doc = {
    'operation_id': "create_subproduct_comment",
    'description': "Crea un nuevo comentario sobre un subproducto",
    'request': "SubproductCommentSerializer",
    'responses': {
        201: "Comentario creado correctamente",
        400: "Solicitud incorrecta - Datos inválidos"
    }
}


# Documentation for retrieving a specific subproduct comment
get_comment_by_id_doc = {
    'operation_id': "retrieve_subproduct_comment",
    'description': "Recupera los detalles de un comentario específico de un subproducto",
    'responses': {
        200: "Detalles del comentario",
        404: "Comentario no encontrado"
    }
}


# Documentation for updating a specific subproduct comment
update_comment_doc = {
    'operation_id': "update_subproduct_comment",
    'description': "Actualiza un comentario específico de un subproducto",
    'request': "SubproductCommentSerializer",
    'responses': {
        200: "Comentario actualizado correctamente",
        400: "Solicitud incorrecta - Datos inválidos"
    }
}

# Documentation for deleting a specific subproduct comment
delete_comment_doc = {
    'operation_id': "delete_subproduct_comment",
    'description': "Elimina suavemente un comentario de subproducto, estableciendo su estado como inactivo (soft delete)",
    'responses': {
        204: "Comentario eliminado correctamente (soft delete)",
        404: "Comentario no encontrado"
    }
}
