import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient

# 1. Cargar variables de entorno
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("GITHUB_TOKEN")
os.environ["OPENAI_API_BASE"] = "https://models.inference.ai.azure.com"

def procesar_documentos():
    print("1. Conectando a MongoDB Atlas...")
    client = MongoClient(os.getenv("MONGO_URI"))
    db_name = "AsistenteDuoc"
    collection_name = "embeddings"
    collection = client[db_name][collection_name]

    print("2. Cargando documento(s) local(es)...")
    loader = PyPDFLoader("reglamento.pdf") 
    documentos = loader.load()

    print("3. Fragmentando (Chunking) el texto...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documentos)

    print(f"4. Generando vectores y subiendo {len(chunks)} fragmentos a la nube...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Guardar en MongoDB Atlas
    MongoDBAtlasVectorSearch.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection=collection,
        index_name="vector_index"
    )
    print("✅ ¡Éxito! Vectores guardados permanentemente en MongoDB Atlas.")

if __name__ == "__main__":
    procesar_documentos()