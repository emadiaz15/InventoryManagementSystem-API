#!/bin/sh
set -e

echo "⌛ Esperando a que la base de datos esté lista..."
# Espera a que el puerto 5432 de la base esté abierto
until nc -z -v -w30 $PGHOST $PGPORT
do
  echo "⏳ Esperando la base de datos en $PGHOST:$PGPORT..."
  sleep 1
done

echo "✅ Base de datos disponible!"

echo "🔧 Aplicando migraciones de base de datos..."
python manage.py makemigrations --settings=inventory_management.settings.production --no-input || echo "⚠️  No se generaron nuevas migraciones"
python manage.py migrate --settings=inventory_management.settings.production --no-input

# Si el primer argumento es "celery", arranca el worker
if [ "$1" = "celery" ]; then
  shift
  echo "🚀 Iniciando Celery worker…"
  exec celery -A inventory_management "$@"
fi

# En cualquier otro caso, arranca el servidor Django
echo "🚀 Iniciando servidor Django…"
exec python manage.py runserver 0.0.0.0:8000 --settings=inventory_management.settings.production
