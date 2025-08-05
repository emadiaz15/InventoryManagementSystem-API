# ✅ Imagen base con SQLite moderno (Alpine 3.17 trae SQLite 3.38+)
FROM python:3.10-alpine3.17

# 📁 Directorio de trabajo
WORKDIR /app

# 🔧 Dependencias del sistema necesarias para compilar y ejecutar (Postgres, Pillow, etc.)
RUN apk add --no-cache \
    sqlite \
    sqlite-dev \
    gcc \
    musl-dev \
    libffi-dev \
    python3-dev \
    postgresql-dev \
    jpeg-dev \
    zlib-dev \
    netcat-openbsd \
    curl \
    build-base \
    libjpeg \
    libjpeg-turbo-dev \
    py3-pip

# ⚡ Actualiza pip para evitar problemas
RUN pip install --upgrade pip

# 📦 Copia primero solo los requirements y los instala (mejor cache)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 📁 Copia el resto del proyecto
COPY . /app

# 🔐 Permisos al script de arranque
RUN chmod +x /app/entrypoint.sh

# 🧠 Variables de entorno por defecto
ARG DJANGO_SETTINGS_MODULE=inventory_management.settings.local
ENV DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
ENV PYTHONUNBUFFERED=1

# 🌐 Puerto expuesto
EXPOSE 8000

# 🚀 Script de arranque
ENTRYPOINT ["/app/entrypoint.sh"]
