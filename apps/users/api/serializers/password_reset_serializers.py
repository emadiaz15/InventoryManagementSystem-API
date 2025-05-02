from rest_framework import serializers


class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=4,
        write_only=True,
        required=True,
        error_messages={
            "required": "La contraseña es obligatoria.",
            "min_length": "La contraseña debe tener al menos 4 caracteres."
        }
    )
