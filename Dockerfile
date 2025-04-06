# 🐍 Usar una imagen ligera de Python 3.10
FROM python:3.10-slim

# 📂 Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# 📦 Copiar solo el archivo de dependencias primero (para aprovechar la caché)
COPY requirements.txt /app/

# 📥 Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# 🔥 Copiar el resto del código del proyecto Django al contenedor
COPY . /app/

# === INICIO: Añadido para Entrypoint y Migraciones ===

# Copiar el script de entrypoint
COPY entrypoint.sh /app/entrypoint.sh

# Dar permisos de ejecución al script
RUN chmod +x /app/entrypoint.sh

# Establecer el entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# === FIN: Añadido para Entrypoint y Migraciones ===

# Establecer las variables de entorno para Django
ENV PYTHONUNBUFFERED 1

# Exponer el puerto donde correrá el servidor (usamos la variable de entorno $PORT)
EXPOSE $PORT

# Iniciar el servidor de Django con Gunicorn (usando el puerto dinámico de Railway)
CMD exec gunicorn inventory_management.wsgi:application
