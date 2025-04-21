from drf_spectacular.utils import OpenApiResponse, OpenApiParameter
from apps.users.api.serializers.user_serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    PasswordResetConfirmSerializer
)

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
        401: OpenApiResponse(description="No autorizado")
    }
}

# --- Perfil de usuario ---

get_user_profile_doc = {
    "tags": ["Users"],
    "summary": "Obtener perfil",
    "operation_id": "get_user_profile",
    "description": "Retorna el perfil del usuario autenticado.",
    "security": [{"jwtAuth": []}],
    "responses": {
        200: OpenApiResponse(response=UserSerializer, description="Perfil recuperado"),
        401: OpenApiResponse(description="No autenticado")
    }
}

# --- Listado de usuarios ---

list_users_doc = {
    "tags": ["Users"],
    "summary": "Listar usuarios",
    "operation_id": "list_users",
    "description": "Retorna lista paginada de usuarios. Sólo accesible para administradores.",
    "security": [{"jwtAuth": []}],
    "parameters": [
        OpenApiParameter(name="username", location=OpenApiParameter.QUERY, description="Filtra por username", required=False, type=str),
        OpenApiParameter(name="email", location=OpenApiParameter.QUERY, description="Filtra por email", required=False, type=str),
        OpenApiParameter(name="is_active", location=OpenApiParameter.QUERY, description="Filtra por estado activo", required=False, type=bool),
        OpenApiParameter(name="is_staff", location=OpenApiParameter.QUERY, description="Filtra por rol admin", required=False, type=bool),
        OpenApiParameter(name="page", location=OpenApiParameter.QUERY, description="Número de página", required=False, type=int),
        OpenApiParameter(name="page_size", location=OpenApiParameter.QUERY, description="Tamaño de página", required=False, type=int)
    ],
    "responses": {
        200: OpenApiResponse(description="Lista paginada de usuarios"),
        403: OpenApiResponse(description="No autorizado")
    }
}

# --- Crear usuario ---

create_user_doc = {
    "tags": ["Users"],
    "summary": "Crear usuario",
    "operation_id": "create_user",
    "description": "Permite a un administrador crear un nuevo usuario.",
    "security": [{"jwtAuth": []}],
    "request": UserSerializer,
    "responses": {
        201: OpenApiResponse(response=UserSerializer, description="Usuario creado correctamente"),
        400: OpenApiResponse(description="Datos inválidos"),
        403: OpenApiResponse(description="No autorizado")
    }
}

# --- Operaciones por ID ---

manage_user_doc = {
    "tags": ["Users"],
    "summary": "Gestión de usuario",
    "operation_id": "manage_user",
    "description": "GET, PUT y DELETE de un usuario por ID.",
    "security": [{"jwtAuth": []}],
    "parameters": [
        OpenApiParameter(name="id", location=OpenApiParameter.PATH, required=True, type=int, description="ID del usuario")
    ],
    "responses": {
        200: OpenApiResponse(response=UserSerializer, description="Usuario recuperado"),
        400: OpenApiResponse(description="Datos inválidos"),
        403: OpenApiResponse(description="No autorizado"),
        404: OpenApiResponse(description="Usuario no encontrado")
    }
}

# --- Reset de contraseña ---

send_password_reset_email_doc = {
    "tags": ["Users"],
    "summary": "Enviar email de reset",
    "operation_id": "send_password_reset_email",
    "description": "Envía al usuario autenticado un enlace para restablecer la contraseña.",
    "security": [{"jwtAuth": []}],
    "responses": {
        200: OpenApiResponse(description="Correo enviado"),
        401: OpenApiResponse(description="No autenticado")
    }
}

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
