import hashlib
from pathlib import Path
from datetime import datetime

from backend.app.ingestion.extractor import extract_text
from backend.app.ingestion.chunker import create_chunks_with_metadata
from backend.app.ingestion.embedder import embedder
from backend.app.ingestion.storage import vector_store


def calculate_file_hash(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def ingest_document(
    file_path: Path,
    filename: str,
    mime_type: str,
    document_id: str | None = None,
    chunk_size: int = 800,
    chunk_overlap: int = 200,
) -> dict:
    
    if document_id is None:
        document_id = f"doc_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file_path.stem}"
    
    file_hash = calculate_file_hash(file_path)
    file_size = file_path.stat().st_size
    
    print(f"\n{'='*60}")
    print(f"Processing document: {filename}")
    print(f"Document ID: {document_id}")
    print(f"File hash: {file_hash[:16]}...")
    print(f"File size: {file_size} bytes")
    print(f"{'='*60}")
    
    print("\n[1/4] Extracting text...")
    pages = extract_text(file_path, mime_type)
    print(f"✓ Extracted {len(pages)} page(s)")
    
    print("\n[2/4] Creating chunks...")
    chunks = create_chunks_with_metadata(
        pages=pages,
        document_id=document_id,
        filename=filename,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    print(f"✓ Created {len(chunks)} chunk(s)")
    
    print("\n[3/4] Creating embeddings...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedder.embed_texts(texts)
    print(f"✓ Created {len(embeddings)} embedding(s)")
    
    print("\n[4/4] Saving to vector store...")
    num_added = vector_store.add_chunks(chunks, embeddings)
    print(f"✓ Saved {num_added} chunk(s) to vector store")
    
    return {
        "document_id": document_id,
        "filename": filename,
        "file_hash": file_hash,
        "file_size_bytes": file_size,
        "mime_type": mime_type,
        "num_chunks": num_added,
        "created_at": datetime.now().isoformat(),
    }