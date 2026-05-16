import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    return _llm


@tool
def respuesta_empatica(situacion: str) -> str:
    """
    Úsala cuando la información NO está en el reglamento o cuando el alumno
    expresa angustia, confusión o urgencia.
    Genera una respuesta orientadora, tranquilizadora y con pasos concretos
    para que el alumno sepa a quién acudir.
    Recibe la descripción de la situación del alumno.
    """
    prompt = (
        "Eres un orientador empático de Duoc UC. El alumno tiene la siguiente situación "
        "y no existe información exacta en el reglamento:\n\n"
        f"{situacion}\n\n"
        "Genera una respuesta que:\n"
        "1. Valide cómo se siente el alumno (1 oración)\n"
        "2. Explique que este tipo de casos se resuelve directamente con apoyo presencial\n"
        "3. Indique 2-3 pasos concretos: ir a Coordinación de Carrera, "
        "contactar al docente, o usar la plataforma de Solicitudes en Línea\n"
        "4. Cierre con una frase alentadora\n"
        "Tono: cálido, claro, profesional. Máximo 120 palabras."
    )
    return _get_llm().invoke(prompt).content.strip()