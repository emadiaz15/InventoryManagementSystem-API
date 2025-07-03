from drf_spectacular.utils import OpenApiResponse, OpenApiParameter

# --- Listar productos ---
list_product_doc = {
    "tags": ["Products"],
    "summary": "Listar productos activos con stock calculado",
    "operation_id": "list_products",
    "description": (
        "Recupera una lista de todos los productos activos con stock calculado. "
        "Se puede filtrar por categoría, tipo o estado. "
        "⚠️ Nota: Este endpoint puede entregar datos cacheados durante un breve período (TTL: 5 minutos) para optimizar el rendimiento. "
        "Los cambios recientes pueden no reflejarse de inmediato."
    ),
    "parameters": [
        OpenApiParameter(name="category", location=OpenApiParameter.QUERY, description="Filtra productos por ID de categoría", required=False, type=int),
        OpenApiParameter(name="type", location=OpenApiParameter.QUERY, description="Filtra productos por ID de tipo", required=False, type=int),
        OpenApiParameter(name="status", location=OpenApiParameter.QUERY, description="Filtra productos activos o inactivos", required=False, type=bool)
    ],
    "responses": {
        200: OpenApiResponse(
            description="Lista de productos con paginación",
            response= {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'count': {'type': 'integer'},
                            'next': {'type': 'string', 'format': 'uri', 'nullable': True},
                            'previous': {'type': 'string', 'format': 'uri', 'nullable': True},
                            'results': {'type': 'array', 'items': {'$ref': '#/components/schemas/Product'}}
                        }
                    }
                }
            }
        )
    }
}

# --- Crear producto ---
create_product_doc = {
    "tags": ["Products"],
    "summary": "Crear nuevo producto",
    "operation_id": "create_product",
    "description": "Crea un nuevo producto. Si se indica la cantidad de stock inicial, se crea el registro de stock asociado.",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/ProductSerializer"}
            }
        }
    },
    "responses": {
        201: OpenApiResponse(description="Producto creado correctamente"),
        400: OpenApiResponse(description="Solicitud incorrecta - Datos inválidos")
    }
}

# --- Obtener producto por ID ---
get_product_by_id_doc = {
    "tags": ["Products"],
    "summary": "Obtener detalles del producto",
    "operation_id": "retrieve_product",
    "description": (
        "Recupera detalles de un producto específico, incluyendo stock y comentarios relacionados. "
        "⚠️ Nota: Este endpoint puede entregar datos cacheados durante un breve período (TTL: 5 minutos)."
        ),
    "parameters": [
        OpenApiParameter(name="prod_pk", location=OpenApiParameter.PATH, required=True, description="ID del producto", type=int)
    ],
    "responses": {
        200: OpenApiResponse(description="Detalles del producto", response={
            'application/json': {
                'schema': {'$ref': '#/components/schemas/Product'}
            }
        }),
        404: OpenApiResponse(description="Producto no encontrado")
    }
}

# --- Actualizar producto por ID ---
update_product_by_id_doc = {
    "tags": ["Products"],
    "summary": "Actualizar producto",
    "operation_id": "update_product",
    "description": "Actualiza los datos de un producto y opcionalmente ajusta el stock si se proporciona un cambio de cantidad.",
    "parameters": [
        OpenApiParameter(name="prod_pk", location=OpenApiParameter.PATH, required=True, description="ID del producto", type=int)
    ],
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/ProductSerializer"}
            }
        }
    },
    "responses": {
        200: OpenApiResponse(description="Producto actualizado correctamente"),
        400: OpenApiResponse(description="Solicitud incorrecta - Datos inválidos")
    }
}

# --- Eliminar producto por ID (soft delete) ---
delete_product_by_id_doc = {
    "tags": ["Products"],
    "summary": "Eliminar producto (soft delete)",
    "operation_id": "delete_product",
    "description": "Elimina suavemente un producto estableciendo status en False.",
    "parameters": [
        OpenApiParameter(name="prod_pk", location=OpenApiParameter.PATH, required=True, description="ID del producto", type=int)
    ],
    "responses": {
        204: OpenApiResponse(description="Producto marcado como inactivo"),
        404: OpenApiResponse(description="Producto no encontrado")
    }
}
