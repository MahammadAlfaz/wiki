from datetime import datetime,timezone
import os
import shutil
from langchain_community.document_loaders import PyMuPDFLoader,TextLoader,Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.retriever import get_vector_store


UPLOADE_DIR="uploads"
PENDING_DIR=os.path.join(UPLOADE_DIR,"pending")
APPROVED_DIR=os.path.join(UPLOADE_DIR,"approved")

def ensure_dirs():
    """Create upload directories if they don't exists"""
    os.makedirs(PENDING_DIR,exist_ok=True)
    os.makedirs(APPROVED_DIR,exist_ok=True)

def get_file_type(file_name:str)->str:
    "Get the file type from extension"
    ext=file_name.rsplit(".",1)[-1].lower()
    mapping={
        'pdf':'pdf',
        'txt':'txt',
        'docx':"docx"
    }
    return mapping.get(ext,"unknown")

def load_document(file_path: str, file_type: str):
    try:
       

        if file_type == "pdf":
            loader = PyMuPDFLoader(file_path)

        elif file_type == "txt":
            loader = TextLoader(file_path, encoding="utf-8")

        elif file_type == "docx":
            loader = Docx2txtLoader(file_path)

        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        return loader.load()

    except Exception as e:
        raise RuntimeError(f"Error loading document: {str(e)}")

def ingest_document(
        document_id:str,
        file_name:str,
        uploaded_by:str)->dict:
    """ 
    Ingest approved document into vector store,
    called after admin approves
    """
    file_path=os.path.join(PENDING_DIR,file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found : {file_name}")
    file_type=get_file_type(file_name)

    if file_type=="unknown":
        raise ValueError(f"Unsupported file type: {file_name}")
    print(f"Starting ingestion: {file_name}")

    documents=load_document(file_path,file_type)
    print(f"loaded {len(documents)} pages")

    splitter=RecursiveCharacterTextSplitter(
        separators=["\n\n","\n"," ",""],
        chunk_size=500,
        chunk_overlap=100
    )
    chunks=splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    for chunk in chunks:
        chunk.metadata.update({
            "document_id": document_id,
            "file_name": file_name,
            "file_type": file_type,
            "uploaded_by": uploaded_by,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "source": file_name
        })

    vector_store=get_vector_store()
    vector_store.add_documents(chunks)

    approved_path=os.path.join(APPROVED_DIR,file_name)
    shutil.move(file_path,approved_path)
    print(f'Moved {file_name} to approved folder')

    print(f"Sucessfully ingested {file_name} - {len(chunks)} chunks")

    return {
        "document_id":document_id,
        "file_name":file_name,
        "chunk_count":len(chunks),
        "status":"ingested"
    }
def delete_document(document_id:str,file_name:str)->dict:
    """
    Delete document from vector store and approved folder .
    Called when admin deltes a document.
    """
    vectore_store=get_vector_store()
    vectore_store.delete(where={"document_id": document_id})
    

    approved_path=os.path.join(APPROVED_DIR,file_name)
    if os.path.exists(approved_path):
        os.remove(approved_path)
        print(f"deleted {file_name} from approved folder")
    
    print(f"Deleted document {document_id} from vector store")

    return {
        "document_id":document_id,
        "status":"deleted"
    }
    
    


