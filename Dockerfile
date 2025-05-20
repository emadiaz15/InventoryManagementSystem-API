# ✅ Imagen oficial de Python + Alpine
FROM python:3.10.13-alpine

# 📁 Directorio de trabajo
WORKDIR /app

# 🧰 Paquetes necesarios para compilar y conectar con Postgres
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    python3-dev \
    postgresql-dev \
    jpeg-dev \
    zlib-dev \
    netcat-openbsd

# 📦 Instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 📁 Copia el resto del proyecto
COPY . .

# ⚙️ Permisos para el entrypoint
RUN chmod +x /app/entrypoint.sh

# 🔐 Variables necesarias para Django
ENV DJANGO_SETTINGS_MODULE=inventory_management.settings.production
ENV PYTHONUNBUFFERED=1

# 🌐 Puerto expuesto (Railway mapea automáticamente el puerto)
EXPOSE 8000

# 🚀 Script de arranque
ENTRYPOINT ["/app/entrypoint.sh"]
