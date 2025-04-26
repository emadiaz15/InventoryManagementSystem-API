import os
import sys
from dotenv import load_dotenv
from pathlib import Path

def main():
    """Run administrative tasks."""
    # Cargar variables de entorno desde un archivo si existe
    BASE_DIR = Path(__file__).resolve().parent
    dotenv_path = BASE_DIR / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path)

    # Si no existe DJANGO_SETTINGS_MODULE en variables de entorno, usar 'inventory_management.settings.local' por defecto
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings.local')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
