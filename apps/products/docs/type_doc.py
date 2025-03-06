list_type_doc = {
    'operation_id': "list_types",
    'description': "Recupera una lista de todos los tipos activos con paginación, ordenados del más nuevo al más antiguo.",
    'responses': {200: "Lista de tipos activos"}
}

create_type_doc = {
    'operation_id': "create_type",
    'description': "Crea un nuevo tipo de producto.",
    'request': "TypeSerializer",
    'responses': {201: "Tipo creado correctamente", 400: "Solicitud Incorrecta - Datos inválidos"}
}

get_type_by_id_doc = {
    'operation_id': "retrieve_type",
    'description': "Recupera detalles de un tipo específico.",
    'responses': {200: "Detalles del tipo", 404: "Tipo no encontrado"}
}

update_type_by_id_doc = {
    'operation_id': "update_type",
    'description': "Actualiza detalles de un tipo específico. Solo se actualizan los campos proporcionados en la solicitud.",
    'request': "TypeSerializer",
    'responses': {200: "Tipo actualizado correctamente", 400: "Solicitud Incorrecta - Datos inválidos"}
}

delete_type_by_id_doc = {
    'operation_id': "delete_type",
    'description': "Marca un tipo específico como inactivo (soft delete).",
    'responses': {204: "Tipo eliminado (soft) correctamente", 404: "Tipo no encontrado"}
}
