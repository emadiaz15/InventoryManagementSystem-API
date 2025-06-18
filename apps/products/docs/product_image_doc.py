from drf_spectacular.utils import OpenApiResponse, OpenApiParameter

# --- Subir imagen o video de producto ---
product_image_upload_doc = {
    "tags": ["Productos - Archivos"],
    "summary": "Subir imágenes o videos de un producto",
    "operation_id": "uploadProductFiles",
    "description": (
        "Sube uno o varios archivos multimedia (imágenes o videos) asociados a un producto. "
        "Solo administradores pueden realizar esta acción. "
        "Los formatos permitidos son configurables vía `ALLOWED_UPLOAD_EXTENSIONS` en el entorno."
    ),
    "parameters": [
        OpenApiParameter(
            name="product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del producto al cual se suben los archivos."
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
                            "type": "array",
                            "items": {
                                "type": "string",
                                "format": "binary"
                            },
                            "description": "Lista de archivos multimedia a subir"
                        }
                    },
                    "required": ["file"]
                }
            }
        }
    },
    "responses": {
        201: OpenApiResponse(description="Todos los archivos subidos correctamente"),
        207: OpenApiResponse(description="Algunos archivos subidos correctamente, otros fallaron"),
        400: OpenApiResponse(description="Archivos inválidos o no enviados"),
        404: OpenApiResponse(description="Producto no encontrado"),
        500: OpenApiResponse(description="Error inesperado al subir archivos")
    }
}

# --- Listar archivos multimedia del producto ---
product_image_list_doc = {
    "tags": ["Productos - Archivos"],
    "summary": "Listar archivos del producto",
    "operation_id": "listProductFiles",
    "description": (
        "Devuelve una lista de archivos multimedia (imágenes o videos) asociados a un producto. "
        "Requiere autenticación."
    ),
    "parameters": [
        OpenApiParameter(
            name="product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del producto del cual se listan los archivos"
        )
    ],
    "responses": {
        200: OpenApiResponse(
            description="Lista de archivos obtenida exitosamente",
            response={
                "application/json": {
                    "type": "object",
                    "properties": {
                        "files": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "mimeType": {"type": "string"},
                                    "createdTime": {"type": "string", "format": "date-time"}
                                }
                            }
                        }
                    }
                }
            }
        ),
        404: OpenApiResponse(description="Producto no encontrado"),
        500: OpenApiResponse(description="Error al listar archivos")
    }
}

# --- Eliminar archivo multimedia del producto ---
product_image_delete_doc = {
    "tags": ["Productos - Archivos"],
    "summary": "Eliminar archivo de producto",
    "operation_id": "deleteProductFile",
    "description": (
        "Elimina un archivo multimedia (imagen o video) asociado a un producto. "
        "Solo administradores."
    ),
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
        200: OpenApiResponse(description="Archivo eliminado correctamente"),
        404: OpenApiResponse(description="Archivo no encontrado o no vinculado al producto"),
        500: OpenApiResponse(description="Error al eliminar archivo")
    }
}

# --- Descargar archivo multimedia del producto ---
product_image_download_doc = {
    "tags": ["Productos - Archivos"],
    "summary": "Descargar archivo del producto",
    "operation_id": "downloadProductFile",
    "description": (
        "Descarga un archivo multimedia (imagen o video) vinculado a un producto. "
        "Requiere autenticación con token JWT. "
        "El archivo se devuelve como binario con cabecera `Content-Disposition: inline`. "
        "El parámetro `?force=true` permite omitir validación de asociación."
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
        ),
        OpenApiParameter(
            name="force",
            location=OpenApiParameter.QUERY,
            required=False,
            type=bool,
            description="Omitir validación de vinculación del archivo con el producto"
        )
    ],
    "responses": {
        200: OpenApiResponse(description="Archivo descargado exitosamente"),
        404: OpenApiResponse(description="Archivo no encontrado o acceso no permitido"),
        500: OpenApiResponse(description="Error inesperado al descargar archivo")
    }
}
