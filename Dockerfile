# Usar una imagen oficial de Python como base
FROM python:3.10-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo requirements.txt al contenedor
COPY requirements.txt /app/

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto Django al contenedor
COPY . /app/

# Instalar dependencias de sistemas operativos si es necesario (como Redis y Celery)
RUN apt-get update && apt-get install -y gcc libpq-dev netcat-openbsd

# Asegurarse de que el script wait-for-redis.sh sea ejecutable
RUN chmod +x ./wait-for-redis.sh

# Establecer las variables de entorno para Django
ENV PYTHONUNBUFFERED 1

# Exponer el puerto donde correrá el servidor
EXPOSE 8000

# Definir el comando por defecto para el contenedor
# Si el contenedor se ejecuta como backend, correrá el servidor Django
# Si se ejecuta como worker de Celery, esperará a que Redis esté disponible
CMD ["./wait-for-redis.sh", "celery", "-A", "inventory_management", "worker", "--loglevel=info"]
