from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
from datetime import datetime

from backend.app.database.models import get_db, Document
from backend.app.ingestion.pipeline import ingest_document
from backend.app.schemas.document import UploadResponse, DocumentMetadata
from backend.app.ingestion.storage import vector_store
from backend.app.rag.rag_pipeline import rag_query

from backend.app.memory.conversation_memory import memory
from sqlalchemy.orm import Session as DBSession
import uuid

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. "
                   f"Allowed: PDF, DOCX, TXT"
        )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    
    document_id = f"doc_{timestamp}_{Path(file.filename).stem}"
    
    try:
        doc_info = ingest_document(
            file_path=file_path,
            filename=file.filename,
            mime_type=file.content_type,
            document_id=document_id,
        )
        
        db_document = Document(
            document_id=doc_info["document_id"],
            filename=doc_info["filename"],
            file_hash=doc_info["file_hash"],
            file_size_bytes=doc_info["file_size_bytes"],
            mime_type=doc_info["mime_type"],
            num_chunks=doc_info["num_chunks"],
            storage_path=str(file_path),
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return UploadResponse(
            message="Document uploaded and indexed successfully",
            document_id=doc_info["document_id"],
            filename=doc_info["filename"],
            num_chunks=doc_info["num_chunks"],
        )
    
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )


@router.get("/", response_model=list[DocumentMetadata])
async def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()
    
    return [
        DocumentMetadata(
            document_id=doc.document_id,
            filename=doc.filename,
            file_hash=doc.file_hash,
            file_size_bytes=doc.file_size_bytes,
            mime_type=doc.mime_type,
            num_chunks=doc.num_chunks,
            created_at=doc.created_at,
        )
        for doc in documents
    ]


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.document_id == document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {document_id}"
        )
    
    num_deleted_chunks = vector_store.delete_by_document_id(document_id)
    
    file_path = Path(document.storage_path)
    if file_path.exists():
        file_path.unlink()
    
    db.delete(document)
    db.commit()
    
    return {
        "message": f"Document {document.filename} deleted successfully",
        "chunks_deleted": num_deleted_chunks,
    }

@router.post("/chat")
async def chat(request: dict, db: DBSession = Depends(get_db)):
    question = request.get("question", "").strip()
    session_id = request.get("session_id")
    
    print(f"\n{'='*20} API CHAT REQUEST {'='*20}")
    print(f"📥 Received Session ID: {session_id}")
    print(f"❓ Question: {question}")
    print(f"{'='*58}\n")
    
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    session_id = memory.get_or_create_session(db, session_id)
    
    history = memory.get_history(db, session_id, max_messages=4)
    
    memory.add_message(db, session_id, "user", question)
    
    try:
        result = rag_query(history=history, current_query=question, top_k=5)
        memory.add_message(db, session_id, "assistant", result["answer"])
        
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "retrieved_chunks": result["retrieved_chunks"],
            "session_id": session_id,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")