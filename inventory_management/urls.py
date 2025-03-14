from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# Rutas de la API definidas en cada aplicación
api_patterns = [
    path('users/', include('apps.users.api.urls')),   # Rutas de la app "users"
    path('inventory/', include('apps.products.api.urls')),  # Rutas de la app "products"
    path('cutting/', include('apps.cuts.api.urls')),    # Rutas de la app "cutting"
    path('stocks/', include('apps.stocks.api.urls')),   # Rutas para los eventos de stock
    path('comments/', include('apps.comments.api.urls')),  # Rutas de la app "comments"
]

# Rutas para la documentación de la API con drf-spectacular
schema_patterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/download/', SpectacularAPIView.as_view(), name='schema-download'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns = [
    # La raíz ("") carga las rutas de la app "core" que deberían incluir la vista pública (public_home_view)
    path('', lambda request: HttpResponse("Hello, World!")),
    #path('', include('apps.core.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_patterns)),
    path('api/v1/docs/', include(schema_patterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
