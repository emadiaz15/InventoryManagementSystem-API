# Usar imagen oficial de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias (como gcc, libpq-dev y otros)
RUN apt-get update && apt-get install -y gcc libpq-dev netcat-openbsd

# Copiar el archivo requirements.txt y luego instalar las dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Crear el directorio de logs (si no existe)
RUN mkdir -p /app/logs

# Copiar solo los archivos del proyecto (evita copiar archivos innecesarios)
COPY . /app/

# Asegurarse de que el script wait-for-redis.sh sea ejecutable
RUN chmod +x ./wait-for-redis.sh

# Establecer variables de entorno para Django (esto es útil para evitar buffering)
ENV PYTHONUNBUFFERED 1

# Exponer el puerto donde corre el servidor Django
EXPOSE 8000

# Copiar el script de entrada y hacerlo ejecutable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Establecer el entrypoint para elegir el proceso (Django o Celery)
ENTRYPOINT ["/entrypoint.sh"]

# Definir el comando por defecto para ejecutar Celery si no se proporciona otro comando
CMD ["celery", "-A", "inventory_management", "worker", "--loglevel=info"]
