# 🎓 Orientador Virtual Duoc UC

**ISY0101 — Optativo Ingeniería de Soluciones con IA · EP2**

Agente conversacional basado en el patrón **ReAct (Skills Agent)** que permite a estudiantes de Duoc UC consultar el Reglamento Académico en lenguaje natural, calcular su estado académico y recibir orientación empática cuando no hay información exacta disponible.

---

## 📁 Estructura

```
asistente_duoc_rag/
├── src/
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── buscar_reglamento.py       # Búsqueda semántica en MongoDB Atlas
│   │   ├── respuesta_empatica.py      # Orientación cuando no hay info en reglamento
│   │   └── calcular_estado_academico.py  # Cálculo de notas y riesgo académico
│   ├── ingesta.py   # Procesa el PDF y guarda embeddings en MongoDB
│   ├── agent.py     # AgentExecutor ReAct + memoria dual
│   └── app.py       # Frontend Streamlit

```

---

## 🔄 Flujo del agente

```
Pregunta del alumno
        │
        ▼
  AgentExecutor (ReAct loop)
  Thought → Action → Observation → ...
        │
        ├── notas / reprobaciones   →  calcular_estado_academico
        ├── reglamento / procesos   →  buscar_reglamento (MongoDB Atlas)
        │        └── sin resultados →  respuesta_empatica
        └── angustia / urgencia     →  respuesta_empatica
        │
        ▼
  Final Answer al alumno
        │
        ▼
  Memoria corto plazo  →  ConversationBufferWindowMemory (k=6)
  Memoria largo plazo  →  ConversationSummaryMemory (resumen comprimido)
        │
        ▼
  LangSmith (trazas automáticas)
```

---

## ⚙️ Instalación

```bash
# 1. Clonar y entrar al proyecto
git clone https://github.com/Joaquiniturriaga/asistente_duoc_rag
cd asistente-duoc-rag

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## 🔑 Variables de entorno

Crea un archivo `.env` en la raíz con:

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/

# LangSmith — observabilidad (cuenta gratuita en smith.langchain.com)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__xxxxxxxxxxxxxxxx
LANGCHAIN_PROJECT=asistente-duoc
```
o mejor aun solo consultar directamente todo ingestado en mongo db
---


**Paso 1 — Levantar el agente**

```bash
# Frontend web
streamlit run src/app.py

# CLI para pruebas
python src/agent.py
```

---

## 🛠️ Tools disponibles

| Tool | Trigger | Qué hace |
|------|---------|----------|
| `buscar_reglamento` | Preguntas sobre normas, procesos, inscripciones | Busca en MongoDB Atlas con traducción de jerga estudiantil |
| `respuesta_empatica` | Angustia del alumno o info no disponible | Orienta con pasos concretos hacia Coordinación o Docentes |
| `calcular_estado_academico` | El alumno da notas o reprobaciones | Calcula promedio ponderado (60/40) y nota mínima de examen |

---

## 🧠 Memoria

| Tipo | Clase | Función |
|------|-------|---------|
| Corto plazo | `ConversationBufferWindowMemory(k=6)` | Mantiene las últimas 6 interacciones |
| Largo plazo | `ConversationSummaryMemory` | Resumen comprimido de la sesión completa |

---

## 📚 Referencias

- LangChain. (2024). *AgentExecutor and ReAct*. https://python.langchain.com/docs/modules/agents/
- LangChain. (2024). *Memory*. https://python.langchain.com/docs/modules/memory/
- LangChain. (2024). *MongoDB Atlas Vector Search*. https://python.langchain.com/docs/integrations/vectorstores/mongodb_atlas/
- LangSmith. (2024). *Observability*. https://docs.smith.langchain.com/
- Yao, S. et al. (2022). *ReAct: Synergizing Reasoning and Acting in Language Models*. https://arxiv.org/abs/2210.03629
- MongoDB. (2024). *Atlas Vector Search*. https://www.mongodb.com/docs/atlas/atlas-vector-search/