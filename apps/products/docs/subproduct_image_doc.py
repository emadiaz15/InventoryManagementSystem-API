from drf_spectacular.utils import OpenApiParameter, OpenApiResponse
from apps.products.api.serializers.subproduct_image_serializer import SubproductImageSerializer

# 📦 UPLOAD
subproduct_image_upload_doc = {
    "tags": ["Subproduct Files"],
    "summary": "Subir archivos al subproducto",
    "operation_id": "subproduct_upload_file",
    "description": "Carga uno o varios archivos al subproducto indicado.",
    "parameters": [
        OpenApiParameter(name="product_id", location=OpenApiParameter.PATH, required=True, type=str),
        OpenApiParameter(name="subproduct_id", location=OpenApiParameter.PATH, required=True, type=str),
    ],
    "request": {
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "file": {
                            "type": "array",
                            "items": {"type": "string", "format": "binary"},
                        }
                    },
                    "required": ["file"]
                }
            }
        }
    },
    "responses": {
        201: OpenApiResponse(description="Archivos subidos correctamente"),
        207: OpenApiResponse(description="Subida parcial, algunos errores"),
        400: OpenApiResponse(description="Archivos inválidos o faltantes"),
        500: OpenApiResponse(description="Error interno del servidor"),
    },
}

# 📄 LIST
subproduct_image_list_doc = {
    "tags": ["Subproduct Files"],
    "summary": "Listar archivos del subproducto",
    "operation_id": "subproduct_list_files",
    "description": "Devuelve todos los archivos registrados en la DB para un subproducto.",
    "parameters": [
        OpenApiParameter(name="product_id", location=OpenApiParameter.PATH, required=True, type=str),
        OpenApiParameter(name="subproduct_id", location=OpenApiParameter.PATH, required=True, type=str),
    ],
    "responses": {
        200: SubproductImageSerializer(many=True),
        404: OpenApiResponse(description="Producto o subproducto no encontrado"),
        500: OpenApiResponse(description="Error del servidor al listar archivos")
    }
}

# ⬇️ DOWNLOAD
subproduct_image_download_doc = {
    "tags": ["Subproduct Files"],
    "summary": "Descargar archivo de subproducto",
    "operation_id": "subproduct_download_file",
    "description": "Descarga un archivo del subproducto si está vinculado correctamente.",
    "parameters": [
        OpenApiParameter(name="product_id", location=OpenApiParameter.PATH, required=True, type=str),
        OpenApiParameter(name="subproduct_id", location=OpenApiParameter.PATH, required=True, type=str),
        OpenApiParameter(name="file_id", location=OpenApiParameter.PATH, required=True, type=str),
    ],
    "responses": {
        200: OpenApiResponse(description="Archivo descargado correctamente"),
        404: OpenApiResponse(description="Archivo no encontrado o no vinculado"),
    }
}

# 🗑️ DELETE
subproduct_image_delete_doc = {
    "tags": ["Subproduct Files"],
    "summary": "Eliminar archivo de subproducto",
    "operation_id": "subproduct_delete_file",
    "description": "Elimina un archivo del subproducto, tanto del microservicio como del sistema.",
    "parameters": [
        OpenApiParameter(name="product_id", location=OpenApiParameter.PATH, required=True, type=str),
        OpenApiParameter(name="subproduct_id", location=OpenApiParameter.PATH, required=True, type=str),
        OpenApiParameter(name="file_id", location=OpenApiParameter.PATH, required=True, type=str),
    ],
    "responses": {
        200: OpenApiResponse(description="Archivo eliminado correctamente"),
        404: OpenApiResponse(description="Archivo no vinculado"),
        500: OpenApiResponse(description="Error interno al intentar eliminar")
    }
}
