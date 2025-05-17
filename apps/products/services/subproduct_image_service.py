import os
import uuid
from datetime import datetime
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from apps.products.api.repositories.subproduct_file_repository import SubproductFileRepository
from apps.products.models import SubproductImage  # 👈 necesario para registrar url

# -------------------------------------------------------------------
# ⚙️ URL base de tu microservicio FastAPI
# -------------------------------------------------------------------
FASTAPI_BASE_URL = getattr(settings, "DRIVE_API_BASE_URL", None)
if not FASTAPI_BASE_URL:
    raise ImproperlyConfigured("Falta la variable DRIVE_API_BASE_URL en configuración.")

# -------------------------------------------------------------------
# 📁 Generador de nombres únicos para archivos
# -------------------------------------------------------------------
def generate_unique_filename(subproduct_id: str, original_name: str) -> str:
    ext = os.path.splitext(original_name)[1]
    now = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    uid = uuid.uuid4().hex[:6]
    return f"{subproduct_id}_{now}_{uid}{ext}"

# -------------------------------------------------------------------
# ✅ Verificación de vínculo entre archivo y subproducto
# -------------------------------------------------------------------
def is_file_linked_to_subproduct(subproduct_id: str, file_id: str) -> bool:
    return SubproductFileRepository.exists(subproduct_id=int(subproduct_id), file_id=file_id)

# -------------------------------------------------------------------
# 🚀 Subida de archivo (Actualizado)
# -------------------------------------------------------------------
def upload_subproduct_file(file, product_id: str, subproduct_id: str, token: str) -> dict:
    """
    POST /subproduct/{product_id}/{subproduct_id}/upload
    """
    url = f"{FASTAPI_BASE_URL.rstrip('/')}/subproduct/{product_id}/{subproduct_id}/upload"
    filename = generate_unique_filename(subproduct_id, file.name)

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
    file_url = data.get("url") or None
    file_name = data.get("filename") or filename
    mime_type = data.get("mimeType", "application/octet-stream")

    if not file_id:
        raise ValueError("No se recibió 'file_id' desde FastAPI")

    # ✅ Nuevo uso del repositorio centralizado
    if not SubproductFileRepository.exists(int(subproduct_id), file_id):
        SubproductFileRepository.create(
            subproduct_id=int(subproduct_id),
            drive_file_id=file_id,
            url=file_url,
            name=file_name,
            mime_type=mime_type
        )

    return {"file_id": file_id, "url": file_url}


# -------------------------------------------------------------------
# 📂 Listado de archivos del subproducto
# -------------------------------------------------------------------
def list_subproduct_files(product_id: str, subproduct_id: str, token: str) -> list:
    """
    GET /subproduct/{product_id}/{subproduct_id}/list
    """
    url = f"{FASTAPI_BASE_URL.rstrip('/')}/subproduct/{product_id}/{subproduct_id}/list"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("images", [])

# -------------------------------------------------------------------
# ⬇️ Descarga de archivo
# -------------------------------------------------------------------
def download_subproduct_file(product_id: str, subproduct_id: str, file_id: str, token: str) -> tuple[bytes, str, str]:
    """
    GET /subproduct/{product_id}/{subproduct_id}/download/{file_id}
    """
    url = f"{FASTAPI_BASE_URL.rstrip('/')}/subproduct/{product_id}/{subproduct_id}/download/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "application/octet-stream")
    filename = file_id  # fallback

    # Try to extract filename from Content-Disposition
    disposition = resp.headers.get("Content-Disposition", "")
    if "filename=" in disposition:
        filename = disposition.split("filename=")[-1].strip('"')

    return resp.content, filename, content_type

# -------------------------------------------------------------------
# 🗑️ Eliminación de archivo
# -------------------------------------------------------------------
def delete_subproduct_file(product_id: str, subproduct_id: str, file_id: str, token: str) -> None:
    """
    DELETE /subproduct/{product_id}/{subproduct_id}/delete/{file_id}
    """
    url = f"{FASTAPI_BASE_URL.rstrip('/')}/subproduct/{product_id}/{subproduct_id}/delete/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(url, headers=headers)
    resp.raise_for_status()
    SubproductFileRepository.delete(file_id=file_id)
