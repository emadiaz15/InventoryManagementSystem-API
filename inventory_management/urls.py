from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, HttpResponseRedirect
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
import requests

# ========================
# 🔌 DJANGO URL PATTERNS
# ========================
api_patterns = [
    path('users/', include('apps.users.api.urls')),         # Usuarios
    path('inventory/', include('apps.products.api.urls')),  # Productos
    path('cutting/', include('apps.cuts.api.urls')),        # Cortes
    path('stocks/', include('apps.stocks.api.urls')),       # Stock
]

schema_patterns = [
    path('', lambda request: HttpResponseRedirect('swagger-ui/')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/download/', SpectacularAPIView.as_view(), name='schema-download'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns = [
    path('test', lambda request: HttpResponse("Hello, World!")),
    path('', include('apps.core.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_patterns)),
    path('api/v1/docs/', include(schema_patterns)),
]

# ✅ Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
