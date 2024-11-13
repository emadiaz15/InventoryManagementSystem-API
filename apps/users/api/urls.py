from django.urls import path
from apps.users.api.views.auth import (
    CustomTokenObtainPairView, register_view, LogoutView
)
from apps.users.api.views.user import (
    user_list_view, user_detail_api_view, profile_view  # Importa correctamente `profile_view`
)

urlpatterns = [
    # Rutas relacionadas con autenticación
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', register_view, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Rutas relacionadas con el perfil y gestión de usuarios
    path('profile/', profile_view, name='profile'),  # Perfil del usuario actual
    path('list/', user_list_view, name='user_list'), # Lista de usuarios (solo admins)
    path('<int:pk>/', user_detail_api_view, name='user_detail'),  # Ver, actualizar o eliminar un usuario específico
]
