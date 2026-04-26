asistente_duoc_rag/
├── src/
│   ├── chat.py          # El motor del agente
│   └── ingesta.py       # Script de carga 
├── data/
│   └── reglamento.pdf   # El documento fuente
├── .env                 # Las llaves 
├── requirements.txt     # Librerías necesarias
└── README.md            # Instrucciones rápidas

2. Preparación del Entorno (Línea de Comandos)
Ejecute estos comandos en orden:

Crear el entorno virtual (VENV):

Bash
python -m venv .venv
Activar el entorno:

En Windows: .venv\Scripts\activate

En Linux/Mac: source .venv/bin/activate

Instalar dependencias:
Crea un archivo llamado requirements.txt con este contenido si no lo tienes:

Plaintext
langchain
langchain-openai
langchain-mongodb
pymongo
python-dotenv
pypdf
tiktoken
Y que ejecute:

Bash
pip install -r requirements.txt


3. Configuración de Variables de Entorno (.env)

(Mensaje de ava)