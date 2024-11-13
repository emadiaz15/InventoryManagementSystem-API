from django.urls import path
from apps.core.views import public_home_view, dashboard_view

urlpatterns = [
    path('', public_home_view, name='home'),  # Página inicial (pública, sin autenticación)
    path('dashboard/', dashboard_view, name='dashboard'),  # Dashboard (autenticado)
]
