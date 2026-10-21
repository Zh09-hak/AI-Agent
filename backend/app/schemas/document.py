from datetime import datetime
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    file_hash: str = Field(..., description="SHA256 hash of the file to avoid duplicates")
    file_size_bytes: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the file")
    num_chunks: int = Field(..., description="Number of chunks created from this document")
    created_at: datetime = Field(..., description="When the document was indexed")
    
    class Config:
        from_attributes = True


class ChunkMetadata(BaseModel):
    document_id: str = Field(..., description="Parent document ID")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    filename: str = Field(..., description="Parent document filename")
    page_number: int | None = Field(None, description="Page number if available")
    chunk_index: int = Field(..., description="Position of this chunk in the document")
    total_chunks: int = Field(..., description="Total number of chunks in the document")


class UploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    num_chunks: int