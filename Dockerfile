# 🐍 Usar una imagen ligera de Python 3.10
FROM python:3.10.13-alpine

# 📂 Establecer el directorio de trabajo
WORKDIR /app

# ⚙️ Instalar compiladores y librerías necesarias
RUN apk add --no-cache gcc musl-dev libffi-dev python3-dev \
    postgresql-dev jpeg-dev zlib-dev

# 📦 Copiar e instalar dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 🔥 Copiar el resto del código
COPY . /app/

# 🛠️ Entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

# ⚙️ Configuración final
ENV PYTHONUNBUFFERED 1
EXPOSE $PORT