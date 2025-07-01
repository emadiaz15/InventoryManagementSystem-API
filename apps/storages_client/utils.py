
"""Utilidades públicas para operaciones comunes de almacenamiento."""

from .services.s3_file_access import generate_presigned_url

__all__ = ["generate_presigned_url"]

