## Asistente Virtual RAG - Duoc UC

Este proyecto es una solución basada en Inteligencia Artificial (LLM) y un pipeline RAG (Retrieval-Augmented Generation) diseñada para actuar como orientador académico virtual. El sistema responde preguntas basándose exclusivamente en el reglamento institucional de Duoc UC, evitando alucinaciones.

## Arquitectura y Tecnologías
* **Lenguaje:** Python 3.11+
* **Framework LLM:** LangChain
* **Modelo LLM:** GPT-4o-mini (vía GitHub Models / Azure)
* **Embeddings:** text-embedding-3-small
* **Base de Datos Vectorial:** MongoDB Atlas Vector Search

## ⚙️ Instrucciones de Instalación y Ejecución Local

Para probar este proyecto en tu máquina local, sigue estos pasos:

### 1. Clonar el repositorio
Abre tu terminal y clona este proyecto:
```bash
git clone 
cd asistente_duoc_rag




2. Crear y activar un entorno virtual
Es una buena práctica aislar las dependencias del proyecto y la verdad mas comodo y no tener dependencias generales.

En Windows:

Bash
python -m venv venv
.\venv\Scripts\activate
En Mac/Linux:

Bash
python3 -m venv venv
source venv/bin/activate

3. Luego instalar las dependencias 
con el ntorno vitual activado, instala las librerias que estan en requirements.txt

pip install -r requirements.txt


4. Configurar Variables de Entorno (.env)

El proyecto requiere conectarse a MongoDB Atlas y a la API de inferencia. Crea un archivo llamado .env en la raíz del proyecto y agrega tus credenciales con el siguiente formato:

Fragmento de código
# Conexión a la base de datos MongoDB Atlas
MONGO_URI=mongodb+srv://<db_username>:<db_password>@cluster0.ejz1rlv.mongodb.net/?appName=Cluster0

# Credenciales para el modelo (usando GitHub Models/Azure)
GITHUB_TOKEN=token
OPENAI_API_BASE=[https://models.inference.ai.azure.com](https://models.inference.ai.azure.com)


5. Ejecución del Sistema
El proyecto consta de dos partes lógicas. Si la base de datos en MongoDB ya contiene los vectores, puedes saltar directo al Paso B.

A. Fase de Ingesta (Opcional si los datos ya están en la nube):
Lee el PDF, lo fragmenta y lo sube a MongoDB Atlas como vectores.

Bash
python src/ingesta.py
B. Fase de Chat (Orientador Académico):
Inicia la interfaz de consola para conversar con el agente RAG.

Bash
python src/chat.py
Escribe tu pregunta (ej. "¿Cuál es la asistencia mínima para aprobar?") o escribe salir para terminar el programa.