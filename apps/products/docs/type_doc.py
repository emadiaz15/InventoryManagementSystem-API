from drf_spectacular.utils import OpenApiResponse, OpenApiParameter

# --- Listar tipos activos ---
list_type_doc = {
    "tags": ["Types"],
    "summary": "Listar tipos activos",
    "operation_id": "list_types",
    "description": (
        "Recupera una lista de todos los tipos activos con paginación y filtros opcionales por nombre. "
        "⚠️ Nota: Este endpoint puede entregar datos cacheados durante un breve período (TTL: 5 minutos) para optimizar el rendimiento. "
        "Los cambios recientes pueden no reflejarse de inmediato."
    ),
    "parameters": [
        OpenApiParameter(name="name", location=OpenApiParameter.QUERY, description="Filtrar por nombre del tipo", required=False, type=str)
    ],
    "responses": {
        200: OpenApiResponse(description="Lista de tipos activos paginada")
    }
}

# --- Crear nuevo tipo ---
create_type_doc = {
    "tags": ["Types"],
    "summary": "Crear nuevo tipo",
    "operation_id": "create_type",
    "description": (
        "Crea un nuevo tipo de producto. Requiere permisos de administrador. "
        "Esta acción invalidará automáticamente la cache del listado de tipos para reflejar el cambio."
    ),
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
    "description": (
        "Recupera los detalles de un tipo específico. "
        "⚠️ Nota: Este endpoint puede entregar datos cacheados durante 5 minutos. "
        "Los cambios recientes pueden no reflejarse de inmediato."
    ),
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
    "description": (
        "Actualiza los datos de un tipo específico. Solo administradores. "
        "Esta acción invalidará automáticamente la cache relacionada al tipo."
    ),
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
    "description": (
        "Marca un tipo específico como inactivo (soft delete). Requiere permisos de administrador. "
        "Esta acción invalidará automáticamente la cache del listado de tipos."
    ),
    "parameters": [
        OpenApiParameter(name="type_pk", location=OpenApiParameter.PATH, required=True, description="ID del tipo", type=int)
    ],
    "responses": {
        204: OpenApiResponse(description="Tipo eliminado (soft) correctamente"),
        403: OpenApiResponse(description="Prohibido - No tienes permisos"),
        404: OpenApiResponse(description="Tipo no encontrado")
    }
}
