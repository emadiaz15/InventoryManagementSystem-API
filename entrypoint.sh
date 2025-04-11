#!/bin/sh

# Salir si algo falla
set -e

echo "🔧 Aplicando migraciones de base de datos..."
python manage.py makemigrations --noinput  # 👉 Asegúrate de incluir esto
python manage.py migrate --noinput

echo "🚀 Iniciando servidor Django..."
exec "$@"
