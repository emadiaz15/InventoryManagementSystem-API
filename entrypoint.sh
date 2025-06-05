#!/bin/sh
set -e

echo "🔍 Entorno activo: $DJANGO_SETTINGS_MODULE"

# 🔁 Variables básicas
USE_SQLITE=${USE_SQLITE:-false}
PORT=${PORT:-8000}

# ⏳ Solo esperar DB si es PostgreSQL (USE_SQLITE != "true")
if [ "$USE_SQLITE" != "true" ]; then
  # Verificar que PGHOST y PGPORT existan
  if [ -z "$PGHOST" ] || [ -z "$PGPORT" ]; then
    echo "❌ Variables PGHOST/PGPORT no definidas. ¿Olvidaste definirlas?"
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

# 🔧 Migraciones
# - Primero migramos solo la app 'users' (si existe)
echo "🔧 Migrando 'users' primero..."
python manage.py makemigrations users || true
python manage.py migrate users || true

# - Luego migraciones generales
echo "🔧 Aplicando migraciones generales..."
python manage.py makemigrations || true
python manage.py migrate || true

# 🚀 Iniciar servidor según entorno
if [ "$DJANGO_SETTINGS_MODULE" = "inventory_management.settings.production" ] && [ "$USE_SQLITE" != "true" ]; then
  echo "🚀 Iniciando Gunicorn en puerto $PORT (modo producción, Postgres)"
  exec gunicorn inventory_management.wsgi:application --bind 0.0.0.0:"$PORT"
else
  echo "🚧 Iniciando runserver en puerto $PORT (modo desarrollo o SQLite)"
  exec python manage.py runserver 0.0.0.0:"$PORT"
fi
