# apps/products/docs/product_image_doc.py

from drf_spectacular.utils import OpenApiResponse, OpenApiParameter

# --- Listar imágenes de un producto ---
list_product_images_doc = {
    "tags": ["Product Images"],
    "summary": "Listar imágenes de un producto",
    "operation_id": "list_product_images",
    "description": "Obtiene todas las imágenes asociadas a un producto específico desde el servicio externo.",
    "parameters": [
        OpenApiParameter(
            name="product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del producto al cual pertenecen las imágenes."
        )
    ],
    "responses": {
        200: OpenApiResponse(
            description="Lista de imágenes recuperadas exitosamente",
            response={
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'images': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'string'},
                                        'name': {'type': 'string'},
                                        'mimeType': {'type': 'string'},
                                        'createdTime': {'type': 'string', 'format': 'date-time'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ),
        404: OpenApiResponse(description="Producto o imágenes no encontradas")
    }
}

# --- Subir una nueva imagen al producto ---
upload_product_image_doc = {
    "tags": ["Product Images"],
    "summary": "Subir imagen a producto",
    "operation_id": "upload_product_image",
    "description": "Sube una nueva imagen para un producto específico.",
    "parameters": [
        OpenApiParameter(
            name="product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del producto al cual se sube la imagen."
        )
    ],
    "requestBody": {
        "required": True,
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "file": {
                            "type": "string",
                            "format": "binary",
                            "description": "Archivo de imagen a subir"
                        }
                    },
                    "required": ["file"]
                }
            }
        }
    },
    "responses": {
        201: OpenApiResponse(description="Imagen subida exitosamente"),
        400: OpenApiResponse(description="Datos inválidos o falta de archivo"),
        404: OpenApiResponse(description="Producto no encontrado")
    }
}

# --- Eliminar una imagen de un producto ---
delete_product_image_doc = {
    "tags": ["Product Images"],
    "summary": "Eliminar imagen de producto",
    "operation_id": "delete_product_image",
    "description": "Elimina una imagen existente asociada a un producto específico.",
    "parameters": [
        OpenApiParameter(
            name="product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del producto asociado a la imagen."
        ),
        OpenApiParameter(
            name="file_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID de la imagen a eliminar."
        )
    ],
    "responses": {
        200: OpenApiResponse(description="Imagen eliminada exitosamente"),
        404: OpenApiResponse(description="Producto o imagen no encontrados")
    }
}
