import os
import time
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_mongodb import MongoDBAtlasVectorSearch

load_dotenv(override=True)

def procesar_documentos():
    client = MongoClient(os.getenv("MONGO_URI"))
    db_name = "AsistenteDuoc"
    collection_name = "embeddings"
    collection = client[db_name][collection_name]

    loader = PyPDFLoader("reglamento.pdf")
    documentos = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=True,
        separators=["\n\n", "\n", ". ", " "]
    )
    chunks = text_splitter.split_documents(documentos)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    batch_size = 15
    for batch_idx in range(0, len(chunks), batch_size):
        batch = chunks[batch_idx:batch_idx + batch_size]
        
        batch_prompt = (
            "Genera 5 términos de búsqueda (jerga estudiantil y términos técnicos) para estos textos. "
            "Responde solo en este formato: [f1]: t1, t2... [f2]: t1, t2...\n\n"
        )
        
        for idx, chunk in enumerate(batch):
            batch_prompt += f"[f{idx+1}]:\n{chunk.page_content[:400]}\n\n"
        
        try:
            response = llm.invoke(batch_prompt)
            lines = response.content.strip().split('\n')
            
            for idx, chunk in enumerate(batch):
                try:
                    line = [l for l in lines if f"f{idx+1}" in l.lower()][0]
                    keywords = line.split(':', 1)[1].strip()
                    
                    chunk.page_content = f"Términos clave: {keywords}\nContenido: {chunk.page_content}"
                    chunk.metadata["keywords"] = keywords
                except:
                    chunk.page_content = f"Términos clave: reglamento, duoc\nContenido: {chunk.page_content}"
                
                chunk.metadata["intent"] = "Reglamento Académico"
        
        except Exception:
            for chunk in batch:
                chunk.page_content = f"Términos clave: reglamento\nContenido: {chunk.page_content}"
        
        time.sleep(1)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    MongoDBAtlasVectorSearch.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection=collection,
        index_name="vector_index"
    )

if __name__ == "__main__":
    procesar_documentos()