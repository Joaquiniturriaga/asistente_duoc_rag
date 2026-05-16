import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    return _llm


@tool
def calcular_estado_academico(datos: str) -> str:
    """
    Analiza el estado académico de un alumno según las reglas de Duoc UC.
    Úsala cuando el alumno proporcione notas, reprobaciones o quiera saber
    si está en riesgo académico, condicionalidad o puede titularse.
    El parámetro 'datos' debe contener la información que entregó el alumno,
    por ejemplo: 'promedio 4.2, reprobé 3 ramos este semestre'.
    """
    
    import re
    def normalizar_nota(match):
        n = match.group()
        if len(n) <= 2 and 10 <= int(n) <= 70:
            return f"{int(n)/10:.1f}"
        return n
    datos = re.sub(r'\b\d{2}\b', normalizar_nota, datos)
    prompt = (
        "Eres un orientador académico de Duoc UC. Conoces exactamente cómo funciona "
        "el sistema de evaluación:\n"
        "- Las notas de presentación (parciales) ponderan el 60% de la nota final\n"
        "- El examen final pondera el 40% de la nota final\n"
        "- Nota mínima para aprobar: 4.0 en la nota final ponderada\n"
        "- Fórmula: nota_final = (promedio_parciales × 0.6) + (examen × 0.4)\n"
        "- Para calcular nota mínima del examen: examen = (4.0 - promedio×0.6) / 0.4\n"
        "- Si el resultado es mayor a 7.0, el alumno no puede aprobar con examen\n\n"
        "IMPORTANTE: Si el alumno mencionó el nombre de un ramo, inclúyelo en la respuesta.\n\n"
        f"Datos del alumno: {datos}\n\n"
        "Entrega:\n"
        "- Promedio de presentación calculado\n"
        "- Nota mínima necesaria en el examen (o indica si es imposible aprobar)\n"
        "- Estado académico (Regular / En riesgo / No puede aprobar con examen)\n"
        "Sé directo y muestra los números. Máximo 100 palabras."
    )
    return _get_llm().invoke(prompt).content.strip()