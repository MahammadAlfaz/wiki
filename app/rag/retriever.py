import os

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings


CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "chroma_db")


def get_retriever(k:int=5):
    """
    Get Vector store retriever .
    k=number of docs to retrieve per  query 
    """
    vector_db=Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=GoogleGenerativeAIEmbeddings(
            model='models/embedding-001',
            google_api_key=settings.GOOGLE_API_KEY
        ),  
        collection_name='wiki_docs'
    )
    return vector_db.as_retriever(search_kwargs={'k':k})

def get_vector_store():
    """Get vector store directly for adding documents"""
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=GoogleGenerativeAIEmbeddings(
            model='models/embedding-001',
            google_api_key=settings.GOOGLE_API_KEY
        ),
        collection_name="wiki_docs"
    )