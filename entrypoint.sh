#!/bin/bash
# Este script realiza las migraciones y luego inicia el servidor Django

# Ejecutar las migraciones
echo "Ejecutando las migraciones..."
python manage.py makemigrations
python manage.py migrate

# Iniciar el servidor de Django
echo "Iniciando el servidor de Django..."
exec gunicorn inventory_management.wsgi:application --bind 0.0.0.0:8000
