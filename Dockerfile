# Usa una imagen oficial de Python optimizada
FROM python:3.10.13-alpine

# Establece el directorio de trabajo
WORKDIR /app

# Instala las dependencias necesarias del sistema
RUN apk add --no-cache gcc musl-dev libffi-dev python3-dev \
    postgresql-dev jpeg-dev zlib-dev

# Copia las dependencias y las instala
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación
COPY . /app/

# Copia el entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Variables de entorno importantes
ARG DJANGO_SETTINGS_MODULE=inventory_management.settings.local
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
ENV PYTHONUNBUFFERED=1

# Expone el puerto configurado en Railway o por defecto 8000
EXPOSE ${PORT:-8000}

# Usa un entrypoint personalizado
ENTRYPOINT ["/app/entrypoint.sh"]
