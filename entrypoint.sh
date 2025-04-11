#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

echo "▶️ Realizando makemigrations..."
python manage.py makemigrations --noinput

echo "▶️ Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

# Ejecutar el comando principal que se pasó al contenedor
exec "$@"
