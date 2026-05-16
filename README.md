# 🎓 Orientador Virtual Duoc UC — Agente ReAct con LangChain

**ISY0101 — Optativo Ingeniería de Soluciones con IA · EP2**

Agente funcional basado en el patrón **ReAct (Reasoning + Acting)** que permite a estudiantes de Duoc UC consultar el Reglamento Académico en lenguaje natural, obtener orientación empática ante situaciones no cubiertas por el reglamento, y evaluar su estado académico de forma autónoma.

---

## 🏗️ Arquitectura

```
Usuario (Streamlit / CLI)
        │
        ▼
┌──────────────────────────────────────────┐
│           AgentExecutor (ReAct)           │
│                                          │
│  Thought → Action → Observation → ...   │
│                                          │
│  Tools disponibles:                      │
│  ├── buscar_reglamento                   │  ← MongoDB Atlas Vector Search
│  ├── respuesta_empatica                  │  ← LLM orientador
│  └── calcular_estado_academico           │  ← LLM razonador
└──────────────────────────────────────────┘
        │                  │
        ▼                  ▼
  Memoria Corto       Memoria Largo
  BufferWindow(k=6)   SummaryMemory
        │                  │
        └──────┬───────────┘
               ▼
        LangSmith (trazas)
```

### Patrón elegido: Skills Agent
Se optó por un único agente con herramientas especializadas (skills) en lugar de arquitecturas multi-agente (subagentes, handoffs), ya que el dominio es acotado (reglamento académico institucional) y la complejidad de orquestación no justifica el consumo adicional de tokens ni la latencia de múltiples LLMs en cadena.

---

## 📁 Estructura del proyecto

```
asistente_duoc_rag/
├── src/
│   ├── ingesta.py      # Carga PDF, genera chunks y almacena embeddings en MongoDB
│   ├── agent.py        # Agente ReAct: tools + memoria dual + función pública consultar()
│   └── app.py          # Frontend Streamlit
├── reglamento.pdf      # Reglamento Académico Duoc UC (no incluido en repo, agregar manualmente)
├── .env                # Variables de entorno (ver sección abajo)
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalación y ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/<tu-usuario>/asistente-duoc-rag.git
cd asistente-duoc-rag
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto:

```env
# GitHub Models (LLM + Embeddings)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# MongoDB Atlas
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/

# LangSmith (opcional — observabilidad)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__xxxxxxxxxxxxxxxx
LANGCHAIN_PROJECT=asistente-duoc
```

> **LangSmith:** Crear cuenta gratuita en https://smith.langchain.com y generar API key.

### 4. Ejecutar la ingesta (solo la primera vez)
Coloca `reglamento.pdf` en la raíz del proyecto y ejecuta:
```bash
cd src
python ingesta.py
```
Esto procesa el PDF, genera metadatos/keywords con el LLM y almacena los embeddings en MongoDB Atlas.

### 5. Levantar el agente

**Frontend web (recomendado):**
```bash
streamlit run src/app.py
```
Abre automáticamente en http://localhost:8501

**CLI (para pruebas rápidas):**
```bash
python src/agent.py
```

---

## 🛠️ Herramientas del agente

| Tool | Cuándo se activa | Descripción |
|------|-----------------|-------------|
| `buscar_reglamento` | Preguntas sobre normas, procesos, inscripciones | Recuperación semántica en MongoDB Atlas con traducción de jerga estudiantil |
| `respuesta_empatica` | Situaciones no cubiertas por el reglamento, angustia del alumno | Genera orientación cálida con pasos concretos hacia Coordinación/Docentes |
| `calcular_estado_academico` | El alumno provee notas o reprobaciones | Razona sobre riesgo académico, condicionalidad o eliminación |

---

## 🧠 Memoria

| Tipo | Implementación | Función |
|------|---------------|---------|
| **Corto plazo** | `ConversationBufferWindowMemory(k=6)` | Mantiene las últimas 6 interacciones para contexto inmediato |
| **Largo plazo** | `ConversationSummaryMemory` | El LLM comprime la sesión en un resumen acumulativo. Se visualiza en el sidebar del frontend. |

---

## 📊 Observabilidad con LangSmith

Con `LANGCHAIN_TRACING_V2=true` cada consulta genera una traza completa en https://smith.langchain.com que incluye:
- Razonamiento ReAct paso a paso (Thought/Action/Observation)
- Herramienta invocada y su input/output
- Latencia por paso y costo de tokens
- Historial completo de la cadena

Útil para depurar decisiones del agente y generar evidencia visual para documentación.

---

## 🔄 Flujo de decisión del agente

```
Pregunta del alumno
        │
        ▼
  ¿Menciona notas/reprobaciones?
        │ Sí → calcular_estado_academico
        │ No ↓
  ¿Es sobre reglamento/procesos?
        │ Sí → buscar_reglamento
        │             │
        │         ¿Hay resultados?
        │             │ No → respuesta_empatica
        │             │ Sí → Final Answer
        │ No ↓
  ¿Alumno angustiado/urgente?
        │ Sí → respuesta_empatica
        │ No → Final Answer directo
```

---

## 📚 Referencias

- LangChain. (2024). *AgentExecutor and ReAct*. https://python.langchain.com/docs/modules/agents/
- LangChain. (2024). *ConversationBufferWindowMemory*. https://python.langchain.com/docs/modules/memory/
- LangChain. (2024). *MongoDBAtlasVectorSearch*. https://python.langchain.com/docs/integrations/vectorstores/mongodb_atlas/
- LangSmith. (2024). *Observability for LLM applications*. https://docs.smith.langchain.com/
- Yao, S. et al. (2022). *ReAct: Synergizing Reasoning and Acting in Language Models*. https://arxiv.org/abs/2210.03629
- MongoDB. (2024). *Atlas Vector Search*. https://www.mongodb.com/docs/atlas/atlas-vector-search/