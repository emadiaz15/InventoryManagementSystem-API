#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

# Ejecutar las migraciones de Django
# --noinput evita que pida confirmaciones interactivas
echo "Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

# Ejecutar el comando principal que se pasó al contenedor
# (En tu caso, será: python manage.py runserver 0.0.0.0:8000)
exec "$@"