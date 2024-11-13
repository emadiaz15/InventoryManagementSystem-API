from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# Rutas de la API
api_patterns = [
    path('users/', include('apps.users.api.urls')),  # Rutas de la app `users`
    path('inventory/', include('apps.products.api.urls')),  # Rutas de la app `products`
    path('cutting/', include('apps.cuts.api.urls')),  # Rutas de la app `cutting`
    path('', include('apps.core.urls')),  # Rutas de la app `core` (Añadido)
]

# Rutas para la documentación de la API con drf-spectacular
schema_patterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),  # Esquema de la API en formato OpenAPI
    path('schema/download/', SpectacularAPIView.as_view(), name='schema-download'),  # Descarga directa del esquema
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # Documentación en Swagger UI
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # Documentación en ReDoc
]

# URL principal
urlpatterns = [
    path('admin/', admin.site.urls),  # Ruta al panel de administración de Django
    path('api/v1/', include(api_patterns)),  # Incluye todas las rutas de la API organizadas
    path('api-docs/', include(schema_patterns)),  # Incluye las rutas para la documentación de la API
]
