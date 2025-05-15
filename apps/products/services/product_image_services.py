import os
import uuid
from datetime import datetime
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from apps.products.models import ProductImage
from apps.products.api.repositories.product_file_repository import ProductFileRepository

# -------------------------------------------------------------------
# ⚙️ Configuración: URL del microservicio externo
# -------------------------------------------------------------------
DRIVE_API_BASE_URL = getattr(settings, "DRIVE_API_BASE_URL", None)
if not DRIVE_API_BASE_URL:
    raise ImproperlyConfigured("Falta la variable DRIVE_API_BASE_URL en configuración.")

# -------------------------------------------------------------------
# 📁 Generador de nombres únicos para archivos
# -------------------------------------------------------------------
def generate_unique_filename(product_id: str, original_name: str) -> str:
    ext = os.path.splitext(original_name)[1]
    now = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    uid = uuid.uuid4().hex[:6]
    return f"{product_id}_{now}_{uid}{ext}"

# -------------------------------------------------------------------
# ✅ Verificación de vínculo entre archivo y producto
# -------------------------------------------------------------------
def is_file_linked_to_product(product_id: str, file_id: str) -> bool:
    return ProductImage.objects.filter(product_id=product_id, drive_file_id=file_id).exists()

# -------------------------------------------------------------------
# 🚀 Subida de archivo
# -------------------------------------------------------------------
def upload_product_file(file, product_id: str, token: str) -> dict:
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/product/{product_id}/upload"
    filename = generate_unique_filename(product_id, file.name)

    file.seek(0)
    file_bytes = file.read()
    files = {
        "file": (
            filename,
            file_bytes,
            getattr(file, "content_type", "application/octet-stream")
        )
    }

    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.post(url, headers=headers, files=files)
    resp.raise_for_status()
    data = resp.json()

    file_id = data.get("file_id")
    if not file_id:
        raise ValueError("No se recibió 'file_id' desde Drive API")

    # 🔗 Vincular automáticamente si no está aún registrado
    if not ProductFileRepository.exists(product_id=int(product_id), file_id=file_id):
        ProductFileRepository.create(product_id=int(product_id), drive_file_id=file_id)

    return {"file_id": file_id}

# -------------------------------------------------------------------
# 📂 Listado de archivos del producto
# -------------------------------------------------------------------
def list_product_files(product_id: str, token: str) -> list:
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/product/{product_id}/list"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("images", [])

# -------------------------------------------------------------------
# ⬇️ Descarga de archivo
# -------------------------------------------------------------------
def download_product_file(product_id: int, file_id: str, token: str) -> tuple[bytes, str, str]:
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/product/{product_id}/download/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"FastAPI error: {response.status_code} - {response.text}")

    filename = response.headers.get("Content-Disposition", "").split("filename=")[-1].strip('"')
    content_type = response.headers.get("Content-Type", "application/octet-stream")
    return response.content, filename, content_type

# -------------------------------------------------------------------
# 🗑️ Eliminación de archivo
# -------------------------------------------------------------------
def delete_product_file(product_id: str, file_id: str, token: str) -> dict:
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/product/{product_id}/delete/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(url, headers=headers)
    resp.raise_for_status()
    return resp.json()
