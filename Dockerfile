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

# Actualizar pip
RUN pip install --upgrade pip

# Establecer las variables de entorno para Django
ENV PYTHONUNBUFFERED 1

# Exponer el puerto donde correrá el servidor (usamos la variable de entorno $PORT)
EXPOSE $PORT

# Iniciar el servidor de Django con Gunicorn (usando el puerto dinámico de Railway)
CMD exec gunicorn inventory_management.wsgi:application
