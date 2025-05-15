from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, HttpResponseRedirect
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
import requests

# ========================
# 🔀 PROXY FASTAPI PRODUCT
# ========================
def proxy_to_fastapi(request, path):
    fastapi_url = f"http://localhost:8001/api/v1/product/{path}"
    try:
        response = requests.request(
            method=request.method,
            url=fastapi_url,
            headers={k: v for k, v in request.headers.items() if k.lower() != 'host'},
            data=request.body,
            stream=True
        )
        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type')
        )
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error al conectar con FastAPI: {e}", status=500)

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

# ✅ FASTAPI Proxy (solo para /api/v1/product/**)
urlpatterns += [
    re_path(r'^api/v1/product/(?P<path>.*)$', proxy_to_fastapi),
]
