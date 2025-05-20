#!/bin/sh
set -e

# ⚙️ Validar variables necesarias
if [ -z "$PGHOST" ] || [ -z "$PGPORT" ]; then
  echo "❌ Variables de conexión a base de datos no definidas (PGHOST o PGPORT)"
  exit 1
fi

if [ -z "$PORT" ]; then
  echo "❌ Variable PORT no está definida (Railway la define automáticamente)"
  exit 1
fi

echo "⌛ Esperando la base de datos en $PGHOST:$PGPORT..."
until nc -z -v -w30 "$PGHOST" "$PGPORT"; do
  echo "⏳ Esperando conexión con DB..."
  sleep 1
done
echo "✅ Base de datos conectada!"

# 🧱 Migraciones
echo "🔧 Migrando 'users' primero..."
python manage.py makemigrations users
python manage.py migrate users

echo "🔧 Aplicando todas las migraciones restantes..."
python manage.py makemigrations
python manage.py migrate

# 🎯 Collect static
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# 🚀 Start server
if [ "$DJANGO_SETTINGS_MODULE" = "inventory_management.settings.production" ]; then
  echo "🚀 Iniciando Gunicorn en $PORT (modo producción)"
  exec gunicorn inventory_management.wsgi:application --bind 0.0.0.0:$PORT
else
  echo "🚧 Iniciando runserver (modo desarrollo)"
  exec python manage.py runserver 0.0.0.0:$PORT
fi
