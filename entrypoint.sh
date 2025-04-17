#!/bin/sh
set -e

echo "🔧 Aplicando migraciones de base de datos..."
python manage.py makemigrations products users cuts stocks --no-input \
  || echo "⚠️  No se generaron nuevas migraciones"
python manage.py migrate --no-input

# Si el primer argumento es "celery", arranca el worker
if [ "$1" = "celery" ]; then
  shift
  echo "🚀 Iniciando Celery worker…"
  exec celery -A inventory_management "$@"
fi

# En cualquier otro caso, arranca el servidor Django
echo "🚀 Iniciando servidor Django…"
exec python manage.py runserver 0.0.0.0:8000
