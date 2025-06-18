#!/bin/sh
set -e

echo "🔍 Entorno activo: $DJANGO_SETTINGS_MODULE"
USE_SQLITE=${USE_SQLITE:-false}
PORT=${PORT:-8000}

# ⏳ Espera la base de datos si no es SQLite
if [ "$USE_SQLITE" != "true" ]; then
  if [ -z "$PGHOST" ] || [ -z "$PGPORT" ]; then
    echo "❌ Faltan variables PGHOST o PGPORT"
    exit 1
  fi

  echo "⏳ Esperando PostgreSQL en $PGHOST:$PGPORT..."
  until nc -z "$PGHOST" "$PGPORT"; do
    echo "⌛ Esperando conexión a PostgreSQL..."
    sleep 1
  done
  echo "✅ Conexión establecida con PostgreSQL"
else
  echo "🧪 Modo SQLite: saltando espera de base de datos"
fi

# 🛠️ Crear nuevas migraciones si es necesario
echo "🛠️ Ejecutando makemigrations..."
python manage.py makemigrations --noinput

# 🔧 Aplicar migraciones
echo "🔧 Aplicando migrate..."
python manage.py migrate --noinput

# 🚀 Iniciar aplicación según entorno
if [ "$DJANGO_SETTINGS_MODULE" = "inventory_management.settings.production" ] && [ "$USE_SQLITE" != "true" ]; then
  echo "🚀 Iniciando Gunicorn en puerto $PORT (producción)"
  exec gunicorn inventory_management.wsgi:application --bind 0.0.0.0:"$PORT"
else
  echo "🚧 Iniciando Django runserver en puerto $PORT (desarrollo)"
  exec python manage.py runserver 0.0.0.0:"$PORT"
fi
