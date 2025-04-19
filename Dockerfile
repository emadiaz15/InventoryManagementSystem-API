# Dockerfile (único para dev y prod)
FROM python:3.10.13-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev python3-dev \
    postgresql-dev jpeg-dev zlib-dev

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# copiamos el código y el entrypoint
COPY . /app/
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Build‑arg para elegir módulo de settings
ARG DJANGO_SETTINGS_MODULE=inventory_management.settings.local
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}

ENV PYTHONUNBUFFERED 1
EXPOSE ${PORT:-8000}

ENTRYPOINT ["/app/entrypoint.sh"]
