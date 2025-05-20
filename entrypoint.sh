#!/bin/sh
set -e

echo "🔍 Entorno activo: $DJANGO_SETTINGS_MODULE"

# 🔁 Variables básicas
USE_SQLITE=${USE_SQLITE:-false}
PORT=${PORT:-8000}

# ⏳ Solo esperar DB si es PostgreSQL
if [ "$USE_SQLITE" != "true" ]; then
  if [ -z "$PGHOST" ] || [ -z "$PGPORT" ]; then
    echo "❌ Variables PGHOST/PGPORT no definidas. ¿Olvidaste definirlas en producción?"
    exit 1
  fi

  echo "⌛ Esperando la base de datos PostgreSQL en $PGHOST:$PGPORT..."
  until nc -z -v -w30 "$PGHOST" "$PGPORT"; do
    echo "⏳ Esperando conexión con PostgreSQL..."
    sleep 1
  done
  echo "✅ Conectado a PostgreSQL!"
else
  echo "🧪 Modo SQLite detectado: saltando espera de DB"
fi

# 🧱 Migraciones
echo "🔧 Migrando 'users' primero..."
python manage.py makemigrations users || true
python manage.py migrate users || true

echo "🔧 Aplicando migraciones generales..."
python manage.py makemigrations || true
python manage.py migrate || true

# 🚀 Iniciar servidor correcto según entorno
if [ "$DJANGO_SETTINGS_MODULE" = "inventory_management.settings.production" ]; then
  echo "🚀 Iniciando Gunicorn en puerto $PORT (modo producción)"
  exec gunicorn inventory_management.wsgi:application --bind 0.0.0.0:$PORT
else
  echo "🚧 Iniciando runserver en puerto $PORT (modo desarrollo)"
  exec python manage.py runserver 0.0.0.0:$PORT
fi
