# apps/products/api/docs/subproduct_image_doc.py

from drf_spectacular.utils import OpenApiResponse, OpenApiParameter

# --- Subir imagen o video de subproducto ---
subproduct_image_upload_doc = {
    "tags": ["Subproductos - Archivos"],
    "summary": "Subir imagen o video de subproducto",
    "operation_id": "uploadSubproductFile",
    "description": (
        "Sube un archivo multimedia (imagen o video) asociado a un subproducto. "
        "Solo administradores pueden realizar esta acción. "
        "Formatos permitidos: JPEG, PNG, WEBP, MP4, MOV, AVI, WEBM, MKV."
    ),
    "parameters": [
        OpenApiParameter(
            name="product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del producto padre al cual pertenece el subproducto."
        ),
        OpenApiParameter(
            name="subproduct_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del subproducto al cual se sube el archivo."
        ),
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
        404: OpenApiResponse(description="Producto o subproducto no encontrado")
    }
}

# --- Listar archivos (imágenes/videos) del subproducto ---
subproduct_image_list_doc = {
    "tags": ["Subproductos - Archivos"],
    "summary": "Listar archivos del subproducto",
    "operation_id": "listSubproductFiles",
    "description": (
        "Devuelve una lista de archivos multimedia (imágenes/videos) vinculados a un subproducto específico."
    ),
    "parameters": [
        OpenApiParameter(
            name="product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del producto padre del subproducto."
        ),
        OpenApiParameter(
            name="subproduct_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del subproducto cuyos archivos se listan."
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Lista de archivos obtenida exitosamente",
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
        500: OpenApiResponse(description="Error interno del servidor"),
        404: OpenApiResponse(description="Producto o subproducto no encontrado")
    }
}

# --- Descargar archivo multimedia del subproducto ---
subproduct_image_download_doc = {
    "tags": ["Subproductos - Archivos"],
    "summary": "Descargar archivo del subproducto",
    "operation_id": "downloadSubproductFile",
    "description": (
        "Devuelve un archivo multimedia (imagen o video) vinculado a un subproducto. "
        "Usa un token JWT temporal para validar el acceso. "
        "El archivo se sirve como binario protegido con cabecera `Content-Disposition` inline."
    ),
    "parameters": [
        OpenApiParameter(
            name="product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del producto padre del subproducto"
        ),
        OpenApiParameter(
            name="subproduct_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del subproducto al que pertenece el archivo"
        ),
        OpenApiParameter(
            name="file_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del archivo a descargar"
        ),
    ],
    "responses": {
        200: OpenApiResponse(description="Archivo binario descargado exitosamente"),
        404: OpenApiResponse(description="Archivo no encontrado"),
        500: OpenApiResponse(description="Error inesperado al descargar archivo")
    }
}

# --- Eliminar archivo multimedia del subproducto ---
subproduct_image_delete_doc = {
    "tags": ["Subproductos - Archivos"],
    "summary": "Eliminar archivo del subproducto",
    "operation_id": "deleteSubproductFile",
    "description": "Elimina un archivo específico (imagen o video) de un subproducto. Solo administradores.",
    "parameters": [
        OpenApiParameter(
            name="product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del producto padre del subproducto"
        ),
        OpenApiParameter(
            name="subproduct_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del subproducto asociado al archivo"
        ),
        OpenApiParameter(
            name="file_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=str,
            description="ID del archivo a eliminar"
        ),
    ],
    "responses": {
        200: OpenApiResponse(description="Archivo eliminado exitosamente"),
        404: OpenApiResponse(description="Producto, subproducto o archivo no encontrado"),
        500: OpenApiResponse(description="Error al eliminar archivo")
    }
}
