Asistente Académico RAG - Duoc UC 🎓
Este proyecto es un asistente inteligente basado en RAG (Retrieval-Augmented Generation) diseñado para resolver dudas sobre el Reglamento Académico de Duoc UC, procesando lenguaje coloquial estudiantil y transformándolo en consultas técnicas precisas.

Tecnologías utilizadas
LLM: GPT-4o-mini (OpenAI).

Vector Database: MongoDB Atlas Vector Search.

Framework: LangChain (LCEL).

Embeddings: text-embedding-3-small.

Instalación y Configuración
Clonar el repositorio:

Bash
git clone https://github.com/Joaquiniturriaga/asistente_duoc_rag.git
cd asistente_duoc_rag
Crear y activar entorno virtual:

Bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
Instalar dependencias:

Bash
pip install -r requirements.txt
Configurar variables de entorno:
Crea un archivo .env en la raíz del proyecto basándote en el archivo .env.example y en mensaje se encuentran presente las credenciales.

Uso
Para iniciar el asistente, simplemente ejecuta el motor de chat. Nota: No es necesario ejecutar el script de ingesta, ya que el clúster de MongoDB ya contiene los datos procesados del reglamento.

Bash
python src/chat.py
Nota de Seguridad y Evaluación
Para facilitar la corrección, se ha configurado un usuario de solo lectura en el clúster de MongoDB Atlas. Usted solo debe proporcionar su propio GITHUB_TOKEN para la inferencia del modelo.


Nota para ejecución en Docker:
El sistema es compatible con Docker. Para una correcta ejecución, construya la imagen y ejecútela habilitando la terminal interactiva:

docker build -t asistente-duoc .

docker run -it --env-file .env asistente-duoc
