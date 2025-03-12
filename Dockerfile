# Usa una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de requerimientos y luego instalar las dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto al contenedor
COPY . /app/

# Crear el directorio para los archivos estáticos
RUN mkdir -p /app/staticfiles

# Crear el directorio de logs
RUN mkdir -p /app/logs

# Instalar dependencias del sistema necesarias (si las hay)
RUN apt-get update && apt-get install -y gcc libpq-dev netcat-openbsd

# Asegurarse de que el script wait-for-redis.sh sea ejecutable
RUN chmod +x ./wait-for-redis.sh

# Establecer variables de entorno para Django
ENV PYTHONUNBUFFERED 1

# Asegurarse de que el directorio de archivos estáticos tiene permisos adecuados
RUN chmod -R 777 /app/staticfiles

# Exponer el puerto donde corre el servidor
EXPOSE 8000

# Ejecutar collectstatic sin pedir confirmación
RUN python manage.py collectstatic --no-input

# Copiar el script de entrada y hacerlo ejecutable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Establecer el entrypoint para elegir el proceso (Django o Celery)
ENTRYPOINT ["/entrypoint.sh"]

# Definir el comando por defecto para ejecutar Celery si no se proporciona otro comando
CMD ["celery", "-A", "inventory_management", "worker", "--loglevel=info"]
