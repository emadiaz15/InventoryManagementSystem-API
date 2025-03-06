
category_list_doc = {
    'operation_id': "list_categories",
    'description': "Recupera una lista de todas las categorías activas con paginación, ordenadas de las más recientes a las más antiguas.",
    'responses': {200: "Lista de categorías activas"}
}

create_category_doc = {
    'operation_id': "create_category",
    'description': "Crea una nueva categoría.",
    'request': "CategorySerializer",
    'responses': {201: "Categoría creada correctamente", 400: "Solicitud Incorrecta - Datos inválidos"}
}

get_category_by_id_doc = {
    'operation_id': "get_category_by_id",
    'description': "Recupera detalles de una categoría específica.",
    'responses': {200: "Detalles de la categoría", 404: "Categoría no encontrada"}
}

update_category_by_id_doc = {
    'operation_id': "update_category",
    'description': "Actualiza detalles de una categoría específica.",
    'request': "CategorySerializer",
    'responses': {200: "Categoría actualizada correctamente", 400: "Solicitud Incorrecta - Datos inválidos"}
}

delete_category_by_id_doc = {
    'operation_id': "delete_category",
    'description': "Marca una categoría específica como inactiva (soft delete).",
    'responses': {204: "Categoría eliminada (soft) correctamente", 404: "Categoría no encontrada"}
}
