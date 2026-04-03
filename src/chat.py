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

# 1. Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("GITHUB_TOKEN")
os.environ["OPENAI_API_BASE"] = "https://models.inference.ai.azure.com"

# Store for session history
session_store = {}

def get_session_history(session_id: str):
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def start_chat():
    print("🌐 Conectando con la base de datos en MongoDB Atlas...")

    # 2. Configure Cloud Retriever
    client = MongoClient(os.getenv("MONGO_URI"))
    collection = client["AsistenteDuoc"]["embeddings"]
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    vector_search = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name="vector_index"
    )
    
    # Retrieve the 5 most relevant chunks
    retriever = vector_search.as_retriever(search_kwargs={"k": 5})

    # 3. Configure LLM and Optimized English Prompt
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an academic advisor at Duoc UC. Your goal is to help students based ONLY on the provided regulations context. If the student's question is not in the context, reply exactly: 'Estimado estudiante, esa información no se encuentra en el documento oficial.' Maintain a formal but empathetic tone. ALWAYS reply in Spanish."),
        MessagesPlaceholder(variable_name="history"),
        ("system", "Recovered context from database:\n{context}"),
        ("human", "Student query: {input}"),
    ])

    # 4. Build RAG Chain
    rag_chain = (
        RunnablePassthrough.assign(
            context=lambda x: format_docs(retriever.invoke(x["input"]))
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    # 5. Wrap with message history
    conversational_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    print("\n✅ ¡Listo! Soy tu orientador académico virtual de Duoc UC conectado a la nube.")
    print("Escribe 'salir' en cualquier momento para terminar.\n")
    
    config = {"configurable": {"session_id": "alumno_duoc_1"}}

    while True:
        user_input = input("Tú: ")
        
        if user_input.lower() in ['salir', 'exit', 'quit']:
            print("Orientador: ¡Nos vemos! Mucho éxito en tus estudios.")
            break

        if user_input.strip() == "":
            continue
        
        # Invoke the chain
        response = conversational_chain.invoke(
            {"input": user_input},
            config=config
        )

        print(f"\n🤖 Orientador: {response}\n")
        print("-" * 50)

if __name__ == "__main__":
    start_chat()