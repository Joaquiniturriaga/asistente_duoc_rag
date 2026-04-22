import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("GITHUB_TOKEN")
os.environ["OPENAI_API_BASE"] = "https://models.inference.ai.azure.com"

session_store = {}

def get_session_history(session_id: str):
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def start_chat():
    client = MongoClient(os.getenv("MONGO_URI"))
    collection = client["AsistenteDuoc"]["embeddings"]
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    vector_search = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name="vector_index"
    )
    
    retriever = vector_search.as_retriever(search_kwargs={"k": 8})
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

    traductor_prompt = ChatPromptTemplate.from_template(
        "Eres un orientador de Duoc UC. Traduce esta duda de un alumno a lenguaje académico "
        "para buscar en el reglamento. Si usa jerga como 'echarse', 'botar', 'faltar', "
        "usa los términos técnicos correspondientes. Solo entrega la traducción:\n{input}"
    )
    traductor = traductor_prompt | llm | StrOutputParser()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un orientador académico de Duoc UC. Tu objetivo es ayudar al estudiante. "
                   "Usa el contexto del reglamento para responder de forma clara, formal y empática. "
                   "Si la información exacta no está, intenta orientar al alumno con lo que sepas "
                   "del contexto o dile que consulte a su director de carrera si el tema es muy específico."),
        MessagesPlaceholder(variable_name="history"),
        ("system", "Contexto del reglamento:\n{context}"),
        ("human", "{input}"),
    ])
    def debug_retrieval(inputs):
        user_query = inputs["input"]
        query_formal = traductor.invoke({"input": user_query})
        docs = retriever.invoke(query_formal)
        contexto = format_docs(docs)
        print(f"\n🔍 [DEBUG] Buscando: '{query_formal}'")
        return contexto

    rag_chain = (
        RunnablePassthrough.assign(
            context=debug_retrieval
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    conversational_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    print("Orientador virtual Duoc UC activo. Escribe 'salir' para cerrar.\n")
    config = {"configurable": {"session_id": "sesion_activa"}}

    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ['salir', 'exit', 'quit']: break
        if not user_input.strip(): continue

        try:
            response = conversational_chain.invoke({"input": user_input}, config=config)
            print(f"\n🤖 Orientador: {response}\n" + "-"*50)
        except Exception as e:
            print(f"\n❌ Error en la respuesta: {e}")

if __name__ == "__main__":
    start_chat()