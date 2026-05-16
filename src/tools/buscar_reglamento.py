import os
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.output_parsers import StrOutputParser
from pymongo import MongoClient


def _build_retriever():
    client     = MongoClient(os.getenv("MONGO_URI"))
    collection = client["AsistenteDuoc"]["embeddings"]
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vector_search = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name="vector_index",
        text_key="text"
    )
    return vector_search.as_retriever(search_kwargs={"k": 6})


_retriever = None
_llm       = None

def _get_deps():
    global _retriever, _llm
    if _retriever is None:
        _retriever = _build_retriever()
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    return _retriever, _llm


@tool
def buscar_reglamento(consulta: str) -> str:
    """
    Busca información en el Reglamento Académico de Duoc UC.
    Úsala cuando el alumno pregunte sobre normas, requisitos, procedimientos,
    inscripción de ramos, reprobaciones, titulación, becas, permisos o
    cualquier tema que pueda estar en el reglamento oficial.
    Acepta lenguaje natural o jerga estudiantil.
    """
    retriever, llm = _get_deps()

    # Traduce jerga estudiantil → lenguaje académico formal
    traductor_prompt = (
        "Traduce esta duda de alumno a lenguaje académico formal para buscar "
        "en el reglamento. Solo entrega la traducción, sin explicaciones:\n"
    )
    query_formal = llm.invoke(traductor_prompt + consulta).content.strip()
    docs = retriever.invoke(query_formal)

    if not docs:
        return "No se encontró información relevante en el reglamento para esta consulta."

    resultado = f"[Búsqueda realizada: '{query_formal}']\n\n"
    for i, doc in enumerate(docs, 1):
        keywords = doc.metadata.get("keywords", "")
        resultado += f"--- Fragmento {i} ---\n"
        if keywords:
            resultado += f"Palabras clave: {keywords}\n"
        resultado += doc.page_content + "\n\n"

    return resultado.strip()