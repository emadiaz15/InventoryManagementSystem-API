from django.urls import path
from apps.users.api.views.auth import CustomTokenObtainPairView, LogoutView
from apps.users.api.views.user import (
    user_list_view, user_create_view, user_detail_view, profile_view,
    image_delete_view, image_replace_view
)
from apps.users.api.views.reset_password import password_reset_confirm

urlpatterns = [
    # Rutas para el restablecimiento de contraseña
    path('password-reset/confirm/<str:uidb64>/<str:token>/', password_reset_confirm, name='password_reset_confirm'),

    # Rutas relacionadas con autenticación
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', user_create_view, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Rutas relacionadas con el perfil y gestión de usuarios
    path('profile/', profile_view, name='profile'),
    path('list/', user_list_view, name='user_list'),
    path('<int:pk>/', user_detail_view, name='user_detail'),

    # 🖼️ Rutas del proxy de imagen
    path('image/<str:file_id>/delete/', image_delete_view, name='image_delete_proxy'),
    path('image/<str:file_id>/replace/', image_replace_view, name='image_replace_proxy'),
]
