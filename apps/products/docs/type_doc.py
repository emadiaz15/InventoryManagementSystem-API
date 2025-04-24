from drf_spectacular.utils import OpenApiResponse, OpenApiParameter

# --- Listar tipos activos ---
list_type_doc = {
    "tags": ["Types"],
    "summary": "Listar tipos activos",
    "operation_id": "list_types",
    "description": "Recupera una lista de todos los tipos activos con paginación y filtros opcionales por nombre.",
    "parameters": [
        OpenApiParameter(name="name", location=OpenApiParameter.QUERY, description="Filtrar por nombre del tipo", required=False, type=str)
    ],
    "responses": {
        200: OpenApiResponse(description="Lista de tipos activos paginada")
    }
}

# --- Crear tipo ---
create_type_doc = {
    "tags": ["Types"],
    "summary": "Crear nuevo tipo",
    "operation_id": "create_type",
    "description": "Crea un nuevo tipo de producto. Requiere permisos de administrador.",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/Type"}
            }
        }
    },
    "responses": {
        201: OpenApiResponse(description="Tipo creado correctamente"),
        400: OpenApiResponse(description="Solicitud incorrecta - Datos inválidos"),
        403: OpenApiResponse(description="Prohibido - No tienes permisos")
    }
}

# --- Obtener tipo por ID ---
get_type_by_id_doc = {
    "tags": ["Types"],
    "summary": "Obtener tipo por ID",
    "operation_id": "get_type_by_id",
    "description": "Recupera los detalles de un tipo específico.",
    "parameters": [
        OpenApiParameter(name="type_pk", location=OpenApiParameter.PATH, required=True, description="ID del tipo", type=int)
    ],
    "responses": {
        200: OpenApiResponse(description="Detalles del tipo"),
        404: OpenApiResponse(description="Tipo no encontrado")
    }
}

# --- Actualizar tipo ---
update_type_by_id_doc = {
    "tags": ["Types"],
    "summary": "Actualizar tipo",
    "operation_id": "update_type",
    "description": "Actualiza los datos de un tipo específico. Solo administradores.",
    "parameters": [
        OpenApiParameter(name="type_pk", location=OpenApiParameter.PATH, required=True, description="ID del tipo", type=int)
    ],
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/Type"}
            }
        }
    },
    "responses": {
        200: OpenApiResponse(description="Tipo actualizado correctamente"),
        400: OpenApiResponse(description="Solicitud incorrecta - Datos inválidos"),
        403: OpenApiResponse(description="Prohibido - No tienes permisos")
    }
}

# --- Eliminar tipo (soft delete) ---
delete_type_by_id_doc = {
    "tags": ["Types"],
    "summary": "Eliminar tipo (soft delete)",
    "operation_id": "delete_type",
    "description": "Marca un tipo específico como inactivo (soft delete). Requiere permisos de administrador.",
    "parameters": [
        OpenApiParameter(name="type_pk", location=OpenApiParameter.PATH, required=True, description="ID del tipo", type=int)
    ],
    "responses": {
        204: OpenApiResponse(description="Tipo eliminado (soft) correctamente"),
        403: OpenApiResponse(description="Prohibido - No tienes permisos"),
        404: OpenApiResponse(description="Tipo no encontrado")
    }
}
