#!/bin/bash

# Forzar collectstatic sin input (sin confirmación)
python manage.py collectstatic --noinput

# Luego ejecutar Gunicorn
gunicorn inventory_management.wsgi:application
