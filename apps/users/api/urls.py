from django.urls import path
from apps.users.api.views.auth import CustomTokenObtainPairView, LogoutView
from apps.users.api.views.user import (user_list_view, user_create_view, user_detail_view, profile_view)
from apps.users.api.views.reset_password import send_password_reset_email, password_reset_confirm

urlpatterns = [
    # Rutas para el restablecimiento de contraseña
    path('password-reset/', send_password_reset_email, name='password_reset'),  # Enviar email con enlace para restablecer la contraseña
    path('password-reset/confirm/<str:uidb64>/<str:token>/', password_reset_confirm, name='password_reset_confirm'),  # Confirmar el restablecimiento de la contraseña

    # Rutas relacionadas con autenticación
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Obtener JWT
    path('register/',user_create_view, name='register'),  # Registro de usuarios (solo admins)
    path('logout/', LogoutView.as_view(), name='logout'),  # Cerrar sesión

    # Rutas relacionadas con el perfil y gestión de usuarios
    path('profile/', profile_view, name='profile'),  # Perfil del usuario autenticado
    path('list/', user_list_view, name='user_list'),  # Lista de usuarios (solo staff/admins)
    path('<int:pk>/', user_detail_view, name='user_detail'),  # Detalles de usuario por ID
]