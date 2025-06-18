# ✅ Imagen oficial de Python con Alpine
FROM python:3.10.13-alpine

# 📁 Directorio de trabajo
WORKDIR /app

# 🔧 Instala dependencias necesarias para compilar y ejecutar (Postgres, Pillow, etc.)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    python3-dev \
    postgresql-dev \
    jpeg-dev \
    zlib-dev \
    netcat-openbsd \
    curl

# 📦 Instala requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 📁 Copia el resto del código del proyecto
COPY . .

# 🔐 Da permisos de ejecución al script de arranque
RUN chmod +x /app/entrypoint.sh

# 🧠 Variables por defecto (pueden ser sobreescritas en Railway o local)
ARG DJANGO_SETTINGS_MODULE=inventory_management.settings.local
ENV DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

# 🚫 Desactiva buffering de Python para que los logs salgan en tiempo real
ENV PYTHONUNBUFFERED=1

# 🌐 Puerto por defecto (puede ser sobrescrito por Railway)
EXPOSE 8000

# 🚀 Script de arranque
ENTRYPOINT ["/app/entrypoint.sh"]
