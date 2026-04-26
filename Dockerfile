# Versión ligera de python 
FROM python:3.11-slim

# Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Instalamos dependencias del sistema necesarias (si las hubiera, por ahora slim está bien)
# Copiamos primero los requerimientos para aprovechar la caché de capas de Docker
COPY requirements.txt .

# Instalación de dependencias
RUN pip install --no-cache-dir -r requirements.txt 

# Copiamos todo lo restante del proyecto
COPY . .

# El comando que se ejecutará al encender el contenedor
# Usamos -u para que el output de la terminal sea fluido
CMD [ "python", "-u", "src/chat.py" ]