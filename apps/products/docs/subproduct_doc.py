from drf_spectacular.utils import OpenApiResponse, OpenApiParameter

# --- Documentation for listing subproducts ---
list_subproducts_doc = {
    "tags": ["Subproducts"],
    "summary": "Listar subproductos activos de un producto padre",
    "operation_id": "list_subproducts",
    "description": "Recupera una lista paginada de subproductos (productos hijo) para un producto padre específico, incluyendo el stock calculado.",
    "parameters": [
        OpenApiParameter(
            name="prod_pk",
            location=OpenApiParameter.PATH,
            description="ID del producto padre",
            required=True,
            type=int
        ),
    ],
    "responses": {
        200: OpenApiResponse(description="Lista de subproductos con stock y paginación para el producto padre"),
        404: OpenApiResponse(description="Producto padre no encontrado o inactivo")
    }
}

# --- Documentation for creating a subproduct ---
create_subproduct_doc = {
    "tags": ["Subproducts"],
    "summary": "Crear subproducto",
    "operation_id": "create_subproduct",
    "description": "Crea un nuevo subproducto asociado a un producto padre e inicializa su stock.",
    "parameters": [
        OpenApiParameter(
            name="prod_pk",
            location=OpenApiParameter.PATH,
            description="ID del producto padre",
            required=True,
            type=int
        ),
    ],
    "request": {  # Cambié 'requestBody' a 'request'
        "required": True,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/SubProductSerializer"}
            }
        }
    },
    "responses": {
        201: OpenApiResponse(description="Subproducto creado correctamente"),
        400: OpenApiResponse(description="Solicitud incorrecta - datos inválidos")
    }
}

# --- Documentation for retrieving a specific subproduct ---
get_subproduct_by_id_doc = {
    "tags": ["Subproducts"],
    "summary": "Obtener subproducto por ID",
    "operation_id": "retrieve_subproduct",
    "description": "Recupera los detalles de un subproducto específico, incluyendo su stock actual.",
    "parameters": [
        OpenApiParameter(
            name="prod_pk",
            location=OpenApiParameter.PATH,
            required=True,
            description="ID del producto padre",
            type=int
        ),
        OpenApiParameter(
            name="subp_pk",
            location=OpenApiParameter.PATH,
            required=True,
            description="ID del subproducto",
            type=int
        ),
    ],
    "responses": {
        200: OpenApiResponse(description="Detalles del subproducto"),
        404: OpenApiResponse(description="Subproducto no encontrado o producto padre inválido")
    }
}

# --- Documentation for updating a specific subproduct ---
update_subproduct_by_id_doc = {
    "tags": ["Subproducts"],
    "summary": "Actualizar subproducto",
    "operation_id": "update_subproduct",
    "description": "Actualiza los detalles de un subproducto específico y ajusta su stock si se indica.",
    "parameters": [
        OpenApiParameter(
            name="prod_pk",
            location=OpenApiParameter.PATH,
            required=True,
            description="ID del producto padre",
            type=int
        ),
        OpenApiParameter(
            name="subp_pk",
            location=OpenApiParameter.PATH,
            required=True,
            description="ID del subproducto",
            type=int
        ),
    ],
    "request": {  # Cambié 'requestBody' a 'request'
        "required": True,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/SubProductSerializer"}
            }
        }
    },
    "responses": {
        200: OpenApiResponse(description="Subproducto actualizado correctamente"),
        400: OpenApiResponse(description="Solicitud incorrecta - datos inválidos")
    }
}

# --- Documentation for deleting a subproduct ---
delete_subproduct_by_id_doc = {
    "tags": ["Subproducts"],
    "summary": "Eliminar subproducto (soft delete)",
    "operation_id": "delete_subproduct",
    "description": "Marca un subproducto específico como inactivo (soft delete), estableciendo su status en False.",
    "parameters": [
        OpenApiParameter(
            name="prod_pk",
            location=OpenApiParameter.PATH,
            required=True,
            description="ID del producto padre",
            type=int
        ),
        OpenApiParameter(
            name="subp_pk",
            location=OpenApiParameter.PATH,
            required=True,
            description="ID del subproducto",
            type=int
        ),
    ],
    "responses": {
        204: OpenApiResponse(description="Subproducto eliminado correctamente"),
        403: OpenApiResponse(description="Prohibido - Solo administradores pueden eliminar"),
        404: OpenApiResponse(description="Subproducto no encontrado")
    }
}
