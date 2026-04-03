#Version ligera de python
FROM python:3.11-slim

#Capptea de trabajo dentro del contendor
WORKDIR /app

#Requerimientos copiados para instalarlos
COPY requirements.tx .

#Instalacion de dependencias (Sin cache me funciono)

RUN pip install --no-cache-dir -r requirements.txt 

#Copiamos todo lo restante del proyecto

COPY . .

#El comando que se ejecutara al enceneder el container

CMD [ "python", "src/chat.py" ]
