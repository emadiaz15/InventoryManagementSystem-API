# Usar imagen oficial de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar y instalar las dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Crear el directorio de logs
RUN mkdir -p /app/logs

# Copiar el código del proyecto
COPY . /app/

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y gcc libpq-dev netcat-openbsd

# Asegurarse de que el script wait-for-redis.sh sea ejecutable
RUN chmod +x ./wait-for-redis.sh

# Establecer variables de entorno para Django
ENV PYTHONUNBUFFERED 1

# Exponer el puerto donde corre el servidor
EXPOSE 8000

# Copiar el script de entrada
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Establecer el entrypoint para elegir el proceso
ENTRYPOINT ["/entrypoint.sh"]

# Definir el comando por defecto
CMD ["celery", "-A", "inventory_management", "worker", "--loglevel=info"]
