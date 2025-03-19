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

# ⚙️ Establecer variables de entorno para Django
ENV PYTHONUNBUFFERED=1

# 🚪 Exponer el puerto donde correrá Django
EXPOSE 8000

# 🚀 Comando por defecto: Iniciar el servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
