# Ejecutar las migraciones
echo "Ejecutando las migraciones..."
python manage.py makemigrations
python manage.py migrate

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar el servidor de Django o Celery dependiendo del comando
if [ "$1" = 'celery' ]; then
    exec "$@"
else
    echo "Iniciando el servidor de Django..."
    exec python manage.py runserver 0.0.0.0:8000
fi
