from drf_spectacular.utils import OpenApiParameter, OpenApiResponse
from apps.products.api.serializers.subproduct_image_serializer import SubproductImageSerializer

# --- Subir archivos al subproducto ---
subproduct_image_upload_doc = {
    "tags": ["Subproductos - Archivos"],
    "summary": "Subir archivos al subproducto",
    "operation_id": "uploadSubproductFiles",
    "description": (
        "Sube uno o varios archivos multimedia (imágenes o PDFs) a un subproducto específico. "
        "Solo administradores pueden realizar esta acción. "
        "Los formatos permitidos son configurables vía `ALLOWED_UPLOAD_EXTENSIONS` en el entorno."
    ),
    "parameters": [
        OpenApiParameter(name="product_id", location=OpenApiParameter.PATH, required=True, type=str, description="ID del producto padre"),
        OpenApiParameter(name="subproduct_id", location=OpenApiParameter.PATH, required=True, type=str, description="ID del subproducto")
    ],
    "request": {
        "required": True,
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "file": {
                            "type": "array",
                            "items": {"type": "string", "format": "binary"},
                            "description": "Lista de archivos a subir"
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
        404: OpenApiResponse(description="Producto o subproducto no encontrado"),
        500: OpenApiResponse(description="Error inesperado al subir archivos")
    }
}

# --- Listar archivos del subproducto ---
subproduct_image_list_doc = {
    "tags": ["Subproductos - Archivos"],
    "summary": "Listar archivos del subproducto",
    "operation_id": "listSubproductFiles",
    "description": "Devuelve todos los archivos registrados en la base de datos para un subproducto.",
    "parameters": [
        OpenApiParameter(name="product_id", location=OpenApiParameter.PATH, required=True, type=str, description="ID del producto padre"),
        OpenApiParameter(name="subproduct_id", location=OpenApiParameter.PATH, required=True, type=str, description="ID del subproducto")
    ],
    "responses": {
        200: OpenApiResponse(
            description="Lista de archivos del subproducto",
            response=SubproductImageSerializer(many=True)
        ),
        404: OpenApiResponse(description="Producto o subproducto no encontrado"),
        500: OpenApiResponse(description="Error del servidor al listar archivos")
    }
}

# --- Descargar archivo del subproducto ---
subproduct_image_download_doc = {
    "tags": ["Subproductos - Archivos"],
    "summary": "Descargar archivo del subproducto",
    "operation_id": "downloadSubproductFile",
    "description": (
        "Descarga un archivo multimedia (imagen o PDF) asociado a un subproducto. "
        "Requiere autenticación y validación de asociación con el subproducto correspondiente."
    ),
    "parameters": [
        OpenApiParameter(name="product_id", location=OpenApiParameter.PATH, required=True, type=str, description="ID del producto padre"),
        OpenApiParameter(name="subproduct_id", location=OpenApiParameter.PATH, required=True, type=str, description="ID del subproducto"),
        OpenApiParameter(name="file_id", location=OpenApiParameter.PATH, required=True, type=str, description="ID del archivo a descargar"),
    ],
    "responses": {
        200: OpenApiResponse(description="Archivo descargado correctamente"),
        404: OpenApiResponse(description="Archivo no vinculado o subproducto inexistente"),
        500: OpenApiResponse(description="Error al intentar descargar el archivo")
    }
}

# --- Eliminar archivo del subproducto ---
subproduct_image_delete_doc = {
    "tags": ["Subproductos - Archivos"],
    "summary": "Eliminar archivo del subproducto",
    "operation_id": "deleteSubproductFile",
    "description": (
        "Elimina un archivo asociado a un subproducto tanto del sistema de almacenamiento como de la base de datos. "
        "Solo administradores pueden realizar esta acción."
    ),
    "parameters": [
        OpenApiParameter(name="product_id", location=OpenApiParameter.PATH, required=True, type=str, description="ID del producto padre"),
        OpenApiParameter(name="subproduct_id", location=OpenApiParameter.PATH, required=True, type=str, description="ID del subproducto"),
        OpenApiParameter(name="file_id", location=OpenApiParameter.PATH, required=True, type=str, description="ID del archivo a eliminar"),
    ],
    "responses": {
        200: OpenApiResponse(description="Archivo eliminado correctamente"),
        404: OpenApiResponse(description="Archivo no vinculado o inexistente"),
        500: OpenApiResponse(description="Error inesperado al eliminar archivo")
    }
}
