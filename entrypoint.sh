# Esperar que Redis esté disponible
./wait-for-redis.sh

# Si el primer argumento es "celery", iniciar el worker
if [ "$1" = 'celery' ]; then
    exec celery -A inventory_management worker --loglevel=info
else
    # De lo contrario, ejecutar el servidor de Django
    exec gunicorn inventory_management.wsgi:application --bind 0.0.0.0:8000
fi
