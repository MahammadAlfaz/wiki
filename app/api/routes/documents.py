
import os
import shutil
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_admin
from app.db.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.services.ingest_service import ingest_document


router = APIRouter(prefix="/documents", tags=["documents"])

PENDING_DIR = "uploads/pending"
APPROVED_DIR = "uploads/approved"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed .Use PDF ,DOCX, or TXT.",
        )
    existing = db.query(Document).filter(Document.file_name == file.filename).first()
    if existing:
        raise HTTPException(
            status_code=409, detail="A document with this filename already exists"
        )
    os.makedirs(PENDING_DIR, exist_ok=True)
    file_path = os.path.join(PENDING_DIR, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    doc = Document(
        file_name=file.filename,
        file_type=ext.lstrip("."),
        file_path=file_path,
        uploaded_by=current_user.id,
        status=DocumentStatus.pending,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "message": "Document uploaded successfully , awaiting admin review",
        "document_id": doc.id,
    }


@router.get("/pending")
def get_pending(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    docs = db.query(Document).filter(Document.status == DocumentStatus.pending).all()
    return [_doc_to_dict(d) for d in docs]


@router.post("/approve/{doc_id}")
def approve_document(
    doc_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    doc = _get_doc_or_404(doc_id, db)

    if doc.status != DocumentStatus.pending:
        raise HTTPException(status_code=400, detail=f"Document is already {doc.status}")
    os.makedirs(APPROVED_DIR, exist_ok=True)
    
    

    try:
        result = ingest_document(
            document_id=str(doc.id),
            file_name=doc.file_name,
            uploaded_by=str(doc.uploaded_by)
        )
        chunk_count=result.get("chunk_count",0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    new_path = os.path.join(APPROVED_DIR, doc.file_name)
    doc.status = DocumentStatus.approved
    doc.file_path = new_path
    doc.reviewed_by = admin.id
    doc.reviewed_at = datetime.now(timezone.utc)
    doc.chunk_count = chunk_count
    doc.ingested_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Document approved and ingested", "chunks": chunk_count}


@router.post("/reject/{doc_id}")
def reject_document(
    doc_id: int,
    reason: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    doc = _get_doc_or_404(doc_id, db)

    if doc.status != DocumentStatus.pending:
        raise HTTPException(status_code=400, detail=f"Document is already {doc.status}")
    doc.status = DocumentStatus.rejected
    doc.reviewed_by = admin.id
    doc.reviewed_at = datetime.now(timezone.utc)
    doc.rejection_reason = reason
    db.commit()

    return {"message": "Document rejected", "reason": reason}


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    doc = _get_doc_or_404(doc_id, db)

    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    db.delete(doc)
    db.commit()

    return {"message": "Document deleted successfully"}


@router.get("/all")
def list_all_documents(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [_doc_to_dict(d) for d in docs]


def _get_doc_or_404(doc_id: int, db: Session) -> Document:
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


def _doc_to_dict(d: Document) -> dict:
    return {
        "id": d.id,
        "file_name": d.file_name,
        "file_type": d.file_type,
        "file_path": d.file_path,
        "uploaded_by": d.uploaded_by,
        "status": d.status,
        "reviewed_by": d.reviewed_by,
        "reviewed_at": d.reviewed_at,
        "rejection_reason": d.rejection_reason,
        "chunk_count": d.chunk_count,
        "ingested_at": d.ingested_at,
        "created_at": d.created_at,
    }
