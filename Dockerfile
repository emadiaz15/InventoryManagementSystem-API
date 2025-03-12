# Usar una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo requirements.txt y realizar la instalación de dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el archivo .env al contenedor
COPY .env /app/.env

# Copiar el resto de los archivos del proyecto al contenedor
COPY . /app/

# Crear los directorios necesarios y asignar permisos
RUN mkdir -p /app/staticfiles /app/logs && chmod -R 777 /app/staticfiles /app/logs

# Hacer ejecutable el archivo entrypoint.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Comando por defecto
CMD ["celery", "-A", "inventory_management", "worker", "--loglevel=info"]
