# Usa una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de requerimientos y luego instalar las dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Crear los directorios necesarios y asignar permisos
RUN mkdir -p /app/staticfiles /app/logs && chmod -R 777 /app/staticfiles /app/logs

# Copiar el código del proyecto al contenedor
COPY . /app/

# Establecer las variables de entorno para Django
ENV PYTHONUNBUFFERED 1

# Exponer el puerto donde correrá el servidor
EXPOSE 8000

# Ejecutar las migraciones y colectar los archivos estáticos
RUN python manage.py migrate --no-input
RUN python manage.py collectstatic --no-input

# Copiar el script de entrada y hacerlo ejecutable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Establecer el entrypoint para elegir el proceso (Django o Celery)
ENTRYPOINT ["/entrypoint.sh"]

# Definir el comando por defecto para ejecutar Celery si no se proporciona otro comando
CMD ["celery", "-A", "inventory_management", "worker", "--loglevel=info"]
