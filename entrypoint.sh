#!/bin/sh

# Salir si algo falla
set -e

echo "🔧 Aplicando migraciones de base de datos..."

# Ejecuta makemigrations solo si estás en desarrollo o lo necesitás explícitamente
# Esto evita problemas si ya están generadas en producción
python manage.py makemigrations --noinput || echo "⚠️  No se generaron nuevas migraciones"

# Ejecuta todas las migraciones existentes
python manage.py migrate --noinput

echo "🚀 Iniciando servidor Django..."
exec "$@"
