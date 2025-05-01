import os
import requests
from django.conf import settings
from apps.drive.utils.jwt_utils import generate_jwt

# --- Configuración ---
DRIVE_API_BASE_URL = getattr(settings, "DRIVE_API_BASE_URL", None)
if not DRIVE_API_BASE_URL:
    raise Exception("Falta la variable DRIVE_API_BASE_URL en configuración.")

# --- Servicios de imágenes de productos ---

def upload_product_image(file, product_id: str):
    token = generate_jwt()
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/product/{product_id}/upload"
    files = {
        "file": (file.name, file, getattr(file, "content_type", "application/octet-stream"))
    }
    headers = {"x-api-key": f"Bearer {token}"}

    response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()
    return response.json()

def list_product_images(product_id: str):
    token = generate_jwt()
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/product/{product_id}/list"
    headers = {"x-api-key": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["images"]

def download_product_image(product_id: str, file_id: str):
    token = generate_jwt()
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/product/{product_id}/download/{file_id}"
    headers = {"x-api-key": f"Bearer {token}"}

    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()
    return response.content  # bytes

def delete_product_image(product_id: str, file_id: str):
    token = generate_jwt()
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/product/{product_id}/delete/{file_id}"
    headers = {"x-api-key": f"Bearer {token}"}

    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return {"message": "Imagen eliminada exitosamente"}

def replace_product_image(product_id: str, file_id: str, new_file):
    token = generate_jwt()
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/product/{product_id}/replace/{file_id}"
    files = {
        "file": (new_file.name, new_file, getattr(new_file, "content_type", "application/octet-stream"))
    }
    headers = {"x-api-key": f"Bearer {token}"}

    response = requests.put(url, headers=headers, files=files)
    response.raise_for_status()
    return response.json()
