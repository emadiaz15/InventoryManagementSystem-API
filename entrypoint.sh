#!/bin/sh
set -e

# Detectar ambiente (DEV o PROD)
if [ "$DJANGO_SETTINGS_MODULE" = "inventory_management.settings.production" ]; then
  echo "⌛ Esperando a que la base de datos esté lista en $PGHOST:$PGPORT..."

  until nc -z -v -w30 "$PGHOST" "$PGPORT"
  do
    echo "⏳ Aún esperando la base de datos en $PGHOST:$PGPORT..."
    sleep 1
  done

  echo "✅ Base de datos disponible!"
else
  echo "💻 Ambiente de desarrollo detectado, no esperamos base de datos externa (SQLite usado)"
fi

echo "🔧 Aplicando migraciones..."

# 🧠 Aseguramos que users esté migrado antes que otras dependencias
python manage.py makemigrations users
python manage.py migrate users

# Luego migramos todo lo demás
python manage.py makemigrations
python manage.py migrate --noinput

# 🚀 Modo celery (opcional)
if [ "$1" = "celery" ]; then
  shift
  echo "🚀 Iniciando Celery worker..."
  exec celery -A inventory_management "$@"
fi

# 🚀 Iniciar servidor Django
echo "🚀 Iniciando servidor Django..."
exec python manage.py runserver 0.0.0.0:8000
