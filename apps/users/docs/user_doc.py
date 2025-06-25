from drf_spectacular.utils import OpenApiResponse, OpenApiParameter
from apps.users.api.serializers.user_token_serializers import CustomTokenObtainPairSerializer
from apps.users.api.serializers.user_create_serializers import UserCreateSerializer
from apps.users.api.serializers.user_detail_serializers import UserDetailSerializer
from apps.users.api.serializers.user_update_serializers import UserUpdateSerializer
from apps.users.api.serializers.password_reset_serializers import PasswordResetConfirmSerializer

# --- Autenticación ---
obtain_jwt_token_pair_doc = {
    "tags": ["Auth"],
    "summary": "Obtener tokens JWT",
    "operation_id": "obtain_jwt_token_pair",
    "description": "Intercambia credenciales por un par de tokens JWT (access y refresh).",
    "request": CustomTokenObtainPairSerializer,
    "responses": {
        200: OpenApiResponse(description="Tokens emitidos correctamente"),
        400: OpenApiResponse(description="Credenciales inválidas")
    }
}

logout_user_doc = {
    "tags": ["Auth"],
    "summary": "Cerrar sesión",
    "operation_id": "logout_user",
    "description": "Invalida el refresh token, cerrando la sesión del usuario.",
    "request": {
        "type": "object",
        "properties": {
            "refresh_token": {"type": "string"}
        },
        "required": ["refresh_token"]
    },
    "responses": {
        205: OpenApiResponse(description="Token invalidado"),
        400: OpenApiResponse(description="Token inválido o faltante"),
        401: OpenApiResponse(description="No autenticado")
    }
}

# --- Perfil del usuario autenticado ---
get_user_profile_doc = {
    "tags": ["Users"],
    "summary": "Obtener perfil",
    "operation_id": "get_user_profile",
    "description": "Retorna el perfil del usuario autenticado, incluyendo la URL firmada de imagen si corresponde.",
    "responses": {
        200: OpenApiResponse(response=UserDetailSerializer, description="Perfil recuperado"),
        401: OpenApiResponse(description="No autenticado")
    }
}

# --- Listado de usuarios ---
list_users_doc = {
    "tags": ["Users"],
    "summary": "Listar usuarios",
    "operation_id": "list_users",
    "description": "Retorna lista paginada de usuarios. Solo accesible para administradores.",
    "parameters": [
        OpenApiParameter(name="username", location=OpenApiParameter.QUERY, description="Filtrar por username", required=False, type=str),
        OpenApiParameter(name="email", location=OpenApiParameter.QUERY, description="Filtrar por email", required=False, type=str),
        OpenApiParameter(name="is_active", location=OpenApiParameter.QUERY, description="Filtrar por estado activo", required=False, type=bool),
        OpenApiParameter(name="is_staff", location=OpenApiParameter.QUERY, description="Filtrar por rol administrador", required=False, type=bool),
        OpenApiParameter(name="page", location=OpenApiParameter.QUERY, description="Número de página", required=False, type=int),
        OpenApiParameter(name="page_size", location=OpenApiParameter.QUERY, description="Tamaño de página", required=False, type=int)
    ],
    "responses": {
        200: OpenApiResponse(response=UserDetailSerializer, description="Lista paginada de usuarios"),
        403: OpenApiResponse(description="No autorizado")
    }
}

# --- Crear usuario ---
create_user_doc = {
    "tags": ["Users"],
    "summary": "Crear usuario",
    "operation_id": "create_user",
    "description": "Permite a un administrador crear un nuevo usuario. Se puede subir una imagen opcional.",
    "request": UserCreateSerializer,
    "responses": {
        201: OpenApiResponse(response=UserDetailSerializer, description="Usuario creado correctamente"),
        400: OpenApiResponse(description="Datos inválidos"),
        403: OpenApiResponse(description="No autorizado")
    }
}

# --- Operaciones por ID ---
manage_user_doc = {
    "tags": ["Users"],
    "summary": "Gestión de usuario",
    "operation_id": "manage_user",
    "description": "GET, PUT y DELETE de un usuario por ID. PUT permite actualizar la imagen (solo admins o el usuario mismo).",
    "parameters": [
        OpenApiParameter(name="id", location=OpenApiParameter.PATH, required=True, type=int, description="ID del usuario")
    ],
    "request": UserUpdateSerializer,
    "responses": {
        200: OpenApiResponse(response=UserDetailSerializer, description="Usuario recuperado o actualizado"),
        400: OpenApiResponse(description="Datos inválidos"),
        403: OpenApiResponse(description="No autorizado"),
        404: OpenApiResponse(description="Usuario no encontrado")
    }
}

# --- Reset de contraseña ---
password_reset_confirm_doc = {
    "tags": ["Users"],
    "summary": "Confirmar restablecimiento",
    "operation_id": "password_reset_confirm",
    "description": "Permite establecer nueva contraseña si el token es válido.",
    "parameters": [
        OpenApiParameter(name="uidb64", location=OpenApiParameter.PATH, required=True, type=str),
        OpenApiParameter(name="token", location=OpenApiParameter.PATH, required=True, type=str)
    ],
    "request": PasswordResetConfirmSerializer,
    "responses": {
        200: OpenApiResponse(description="Contraseña cambiada correctamente"),
        400: OpenApiResponse(description="Token inválido o contraseña inválida")
    }
}

# --- Imágenes de perfil ---
image_delete_doc = {
    "tags": ["Users"],
    "summary": "Eliminar imagen de perfil",
    "operation_id": "delete_image_profile",
    "description": "Elimina la imagen de perfil del usuario desde MinIO/S3 y actualiza el modelo.",
    "parameters": [
        OpenApiParameter(name="file_id", location=OpenApiParameter.PATH, required=True, type=str, description="Key de la imagen en S3")
    ],
    "responses": {
        200: OpenApiResponse(description="Imagen eliminada correctamente"),
        404: OpenApiResponse(description="Imagen no encontrada"),
        401: OpenApiResponse(description="No autenticado")
    }
}

image_replace_doc = {
    "tags": ["Users"],
    "summary": "Reemplazar imagen de perfil",
    "operation_id": "replace_image_profile",
    "description": "Permite al usuario (o admin) reemplazar la imagen de perfil almacenada en MinIO/S3.",
    "parameters": [
        OpenApiParameter(name="file_id", location=OpenApiParameter.PATH, required=True, type=str, description="Key actual de la imagen en S3"),
        OpenApiParameter(name="user_id", location=OpenApiParameter.QUERY, required=False, type=int, description="(Solo admin) ID del usuario objetivo")
    ],
    "request": {
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "format": "binary",
                    "description": "Nuevo archivo de imagen"
                }
            },
            "required": ["file"]
        }
    },
    "responses": {
        200: OpenApiResponse(
            description="Imagen reemplazada correctamente",
            response={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "file_id": {"type": "string"}
                }
            }
        ),
        400: OpenApiResponse(description="Archivo no proporcionado"),
        403: OpenApiResponse(description="No autorizado"),
        404: OpenApiResponse(description="Usuario o imagen no encontrados"),
        500: OpenApiResponse(description="Error inesperado al reemplazar la imagen")
    }
}
