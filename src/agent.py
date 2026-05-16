import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor
from langchain.agents.react.agent import create_react_agent
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryMemory

from tools import buscar_reglamento, respuesta_empatica, calcular_estado_academico

load_dotenv()

os.environ["OPENAI_API_KEY"]  = os.getenv("GITHUB_TOKEN")
os.environ["OPENAI_API_BASE"] = "https://models.inference.ai.azure.com"

os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "false")
os.environ["LANGCHAIN_API_KEY"]    = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"]    = os.getenv("LANGCHAIN_PROJECT", "asistente-duoc")

#agente de skill 
TOOLS = [buscar_reglamento, respuesta_empatica, calcular_estado_academico]

SYSTEM_PROMPT = """Eres un orientador académico virtual de Duoc UC. Tu misión es ayudar
a los estudiantes a entender el reglamento académico, resolver dudas sobre procesos
institucionales y orientarlos cuando no encuentres la información exacta.

Tienes acceso a las siguientes herramientas:
{tools}

REGLAS DE DECISIÓN (OBLIGATORIAS):
1. SIEMPRE usa buscar_reglamento PRIMERO si la pregunta menciona normas, procesos, 
   eliminación, reprobación, pagos, inscripciones, ramos, becas o reglamento.
   Solo si no encuentra nada útil, usa respuesta_empatica como complemento.
2. Si el alumno expresa angustia SIN hacer una pregunta concreta → usa respuesta_empatica directamente.
3. Si el alumno entrega notas o porcentajes → usa calcular_estado_academico.
4. Para preguntas que combinan notas Y reglamento → encadena ambas tools.
NUNCA uses respuesta_empatica como reemplazo de buscar_reglamento.

Formato obligatorio:
Thought: [razonamiento sobre qué hacer]
Action: [nombre de la herramienta]
Action Input: [input para la herramienta]
Observation: [resultado]
... (repite si es necesario)
Thought: Tengo suficiente información para responder
Final Answer: [respuesta final al alumno]

Historial de conversación:
{chat_history}

Herramientas disponibles: {tool_names}

Pregunta: {input}
{agent_scratchpad}"""

# ──────────────────────────────────────────────────────────────────────────

_executor  = None
_mem_largo = None


def _crear_agente():
    llm    = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
    agent  = create_react_agent(llm=llm, tools=TOOLS, prompt=prompt)

    mem_corto = ConversationBufferWindowMemory(
        k=6,
        memory_key="chat_history",
        return_messages=True
    )
    mem_largo = ConversationSummaryMemory(
        llm=llm,
        memory_key="resumen_sesion",
        return_messages=False
    )

    executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        memory=mem_corto,
        verbose=False,
        max_iterations=6,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
        output_key="output",
    )   
    return executor, mem_largo


def inicializar():
    global _executor, _mem_largo
    if _executor is None:
        _executor, _mem_largo = _crear_agente()


def consultar(pregunta: str) -> dict:
    """
    Interfaz pública usada por app.py y la CLI.
    Retorna:
      - respuesta (str)
      - pasos     (list[str])  herramientas invocadas
      - resumen   (str)        memoria largo plazo de la sesión
    """
    inicializar()

    result = _executor.invoke({"input": pregunta})

    _mem_largo.save_context(
        {"input": pregunta},
        {"output": result["output"]}
    )

    pasos = [
        f"🔧 {action.tool}: {str(obs)[:120]}..."
        for action, obs in result.get("intermediate_steps", [])
    ]

    return {
        "respuesta": result["output"],
        "pasos":     pasos,
        "resumen":   _mem_largo.load_memory_variables({}).get("resumen_sesion", ""),
    }

def _spinner(stop_event):
    frames = ["📖 Pensando .  ", "📖 Pensando .. ", "📖 Pensando ..."]
    i = 0
    while not stop_event.is_set():
        print(f"\r{frames[i % len(frames)]}", end="", flush=True)
        stop_event.wait(0.4)
        i += 1
    print("\r" + " " * 20 + "\r", end="", flush=True)

if __name__ == "__main__":
    import threading
    inicializar()
    print("📚 Orientador Duoc UC activo. Escribe 'salir' para cerrar.\n")

    while True:
        user_input = input("Tú: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("\n[Resumen de sesión]")
            print(_mem_largo.load_memory_variables({}).get("resumen_sesion", "Sin resumen."))
            break

        stop = threading.Event()
        hilo = threading.Thread(target=_spinner, args=(stop,))
        hilo.start()
        result = consultar(user_input)
        stop.set()
        hilo.join()

        print(f"Orientador: {result['respuesta']}\n" + "─" * 50)