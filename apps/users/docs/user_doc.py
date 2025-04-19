
obtain_jwt_token_pair_doc = {
    'operation_id': 'obtain_jwt_token_pair',
    'description': 'Obtiene un par de tokens JWT (access y refresh).',
    'request': 'CustomTokenObtainPairSerializer',
    'responses': {
        200: 'Tokens emitidos correctamente',
        400: 'Solicitud incorrecta - credenciales inválidas'
    }
}

logout_user_doc = {
    'operation_id': 'logout_user',
    'description': 'Cierra sesión invalidando el refresh token.',
    'request': {
        'type': 'object',
        'properties': {
            'refresh_token': {'type': 'string'}
        }
    },
    'responses': {
        205: 'Refresh token invalidado correctamente',
        400: 'Solicitud incorrecta - refresh token faltante o inválido'
    }
}


get_user_profile_doc = {
    'operation_id': "get_user_profile",
    'description': "Recupera el perfil del usuario autenticado.",
    'responses': {
        200: "Perfil del usuario autenticado.",
        401: "No autorizado – Usuario no autenticado."
    },
}

list_users_doc = {
    'operation_id': "list_users",
    'description': "Recupera una lista de usuarios con filtros y paginación. Solo accesible por administradores.",
    'parameters': [
        {
            'name': 'username',
            'in': 'query',
            'description': 'Filtra por nombre de usuario',
            'required': False,
            'schema': {'type': 'string'}
        },
        {
            'name': 'email',
            'in': 'query',
            'description': 'Filtra por correo electrónico',
            'required': False,
            'schema': {'type': 'string'}
        },
        {
            'name': 'is_active',
            'in': 'query',
            'description': 'Filtra por estado de activación',
            'required': False,
            'schema': {'type': 'boolean'}
        },
    ],
    'responses': {
        200: "Lista paginada de usuarios."
    },
}

create_user_doc = {
    'operation_id': "create_user",
    'description': "Crea un nuevo usuario. Solo accesible por administradores.",
    'request': "UserSerializer",
    'responses': {
        201: "Usuario creado correctamente.",
        400: "Solicitud incorrecta – Datos inválidos.",
        403: "Prohibido – No tienes permiso."
    },
}

manage_user_doc = {
    'operation_id': "manage_user",
    'description': "Recupera, actualiza o elimina (soft delete) un usuario por ID.",
    'parameters': [
        {
            'name': 'pk',
            'in': 'path',
            'description': 'ID del usuario',
            'required': True,
            'schema': {'type': 'integer'}
        }
    ],
    'request': "UserSerializer",
    'responses': {
        200: "Operación realizada correctamente.",
        400: "Solicitud incorrecta – Datos inválidos.",
        403: "Prohibido – No tienes permiso.",
        404: "Usuario no encontrado."
    },
}

send_password_reset_email_doc = {
    'operation_id': 'send_password_reset_email',
    'description': 'Envía un correo con un enlace para restablecer la contraseña al usuario autenticado.',
    'request': {'type': 'object', 'properties': {}},
    'responses': {
        200: 'Correo de restablecimiento enviado correctamente.',
        401: 'No autenticado.',
    }
}

password_reset_confirm_doc = {
    'operation_id': 'password_reset_confirm',
    'description': 'Verifica el token y permite al usuario establecer una nueva contraseña.',
    'parameters': [
        {'name': 'uidb64', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
        {'name': 'token',  'in': 'path', 'schema': {'type': 'string'}, 'required': True},
    ],
    'request': {'type': 'object', 'properties': {'password': {'type': 'string'}}},
    'responses': {
        200: 'Contraseña cambiada correctamente.',
        400: 'UID o token inválido, o contraseña demasiado corta.',
    }
}