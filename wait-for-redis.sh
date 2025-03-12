#!/bin/bash
# Este script espera hasta que Redis esté disponible antes de iniciar Celery o Celery Beat

# Comprobamos si Redis está disponible en el puerto 6379
while ! nc -z redis 6379; do
  echo "Esperando a que Redis esté disponible..."
  sleep 1
done

# Cuando Redis esté disponible, iniciamos el comando que se pasó como parámetro (Celery Worker o Beat)
exec "$@"
