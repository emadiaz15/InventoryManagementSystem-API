from drf_spectacular.utils import OpenApiResponse, OpenApiParameter

# --- Subir imagen o video de producto ---
product_image_upload_doc = {
    "tags": ["Productos - Archivos"],
    "summary": "Subir imagen o video de producto",
    "operation_id": "uploadProductFile",
    "description": (
        "Sube un archivo multimedia (imagen o video) asociado a un producto. "
        "Solo administradores pueden realizar esta acción. "
        "Formatos permitidos: JPEG, PNG, WEBP, MP4, MOV, AVI, WEBM, MKV."
    ),
    "parameters": [
        OpenApiParameter(
            name="product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del producto al cual se sube el archivo."
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
                            "description": "Archivo multimedia a subir"
                        }
                    },
                    "required": ["file"]
                }
            }
        }
    },
    "responses": {
        201: OpenApiResponse(description="Archivo subido exitosamente"),
        400: OpenApiResponse(description="Archivo inválido o falta archivo"),
        500: OpenApiResponse(description="Error inesperado al subir el archivo"),
        404: OpenApiResponse(description="Producto no encontrado")
    }
}

# --- Listar archivos (imágenes/videos) del producto ---
product_image_list_doc = {
    "tags": ["Productos - Archivos"],
    "summary": "Listar archivos del producto",
    "operation_id": "listProductFiles",
    "description": (
        "Devuelve una lista de archivos multimedia (imágenes/videos) vinculados a un producto específico."
    ),
    "parameters": [
        OpenApiParameter(
            name="product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del producto del cual se listan los archivos."
        )
    ],
    "responses": {
        200: OpenApiResponse(
            description="Lista de archivos obtenida exitosamente",
            response={
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'files': {
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
        500: OpenApiResponse(description="Error interno del servidor"),
        404: OpenApiResponse(description="Producto no encontrado")
    }
}

# --- Eliminar archivo multimedia del producto ---
product_image_delete_doc = {
    "tags": ["Productos - Archivos"],
    "summary": "Eliminar archivo del producto",
    "operation_id": "deleteProductFile",
    "description": "Elimina un archivo específico (imagen o video) de un producto. Solo administradores.",
    "parameters": [
        OpenApiParameter(
            name="product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del producto asociado al archivo"
        ),
        OpenApiParameter(
            name="file_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del archivo a eliminar"
        )
    ],
    "responses": {
        200: OpenApiResponse(description="Archivo eliminado exitosamente"),
        404: OpenApiResponse(description="Producto o archivo no encontrado"),
        500: OpenApiResponse(description="Error al eliminar archivo")
    }
}

# --- Descargar archivo multimedia del producto ---
product_image_download_doc = {
    "tags": ["Productos - Archivos"],
    "summary": "Descargar archivo del producto",
    "operation_id": "downloadProductFile",
    "description": (
        "Devuelve un archivo multimedia (imagen o video) vinculado a un producto. "
        "Usa un token JWT temporal para validar el acceso. "
        "El archivo se sirve como binario protegido con cabecera `Content-Disposition` inline."
    ),
    "parameters": [
        OpenApiParameter(
            name="product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del producto al que pertenece el archivo"
        ),
        OpenApiParameter(
            name="file_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del archivo a descargar"
        )
    ],
    "responses": {
        200: OpenApiResponse(
            description="Archivo binario descargado exitosamente (image/video)",
        ),
        404: OpenApiResponse(description="Archivo no encontrado"),
        500: OpenApiResponse(description="Error inesperado al descargar archivo")
    }
}
