def chunk_text(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 200,
) -> list[str]:

    text = " ".join(text.split())
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    
    return chunks


def create_chunks_with_metadata(
    pages: list[tuple[str, int | None]],
    document_id: str,
    filename: str,
    chunk_size: int = 800,
    chunk_overlap: int = 200,
) -> list[dict]:

    chunks = []
    chunk_index = 0
    
    for text, page_number in pages:
        text_chunks = chunk_text(text, chunk_size, chunk_overlap)
        
        for text_chunk in text_chunks:
            chunk_id = f"{document_id}_chunk_{chunk_index}"
            
            chunk_data = {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "filename": filename,
                "page_number": page_number,
                "chunk_index": chunk_index,
                "text": text_chunk,
            }
            
            chunks.append(chunk_data)
            chunk_index += 1

    total_chunks = len(chunks)
    for chunk in chunks:
        chunk["total_chunks"] = total_chunks
    
    return chunks