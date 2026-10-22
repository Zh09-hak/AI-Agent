import re

def split_into_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 200,
) -> list[str]:

    text = " ".join(text.split())
    
    if len(text) <= chunk_size:
        return [text]
        
    sentences = split_into_sentences(text)
    
    chunks = []
    current_chunk_sentences = []
    current_chunk_length = 0
    
    for sentence in sentences:
        sentence_len = len(sentence)
        
        if sentence_len > chunk_size:
            if current_chunk_sentences:
                chunks.append(" ".join(current_chunk_sentences))
                current_chunk_sentences = []
                current_chunk_length = 0
                
            words = sentence.split()
            current_word_chunk = []
            current_word_len = 0
            for word in words:
                if current_word_len + len(word) + 1 > chunk_size:
                    chunks.append(" ".join(current_word_chunk))
                    current_word_chunk = []
                    current_word_len = 0
                current_word_chunk.append(word)
                current_word_len += len(word) + 1
                
            if current_word_chunk:
                current_chunk_sentences = current_word_chunk
                current_chunk_length = current_word_len
        else:
            if current_chunk_length + sentence_len + 1 > chunk_size and current_chunk_sentences:
                chunks.append(" ".join(current_chunk_sentences))
                overlap_sentences = []
                overlap_len = 0
                for s in reversed(current_chunk_sentences):
                    if overlap_len + len(s) + 1 > chunk_overlap:
                        break
                    overlap_sentences.insert(0, s)
                    overlap_len += len(s) + 1
                    
                current_chunk_sentences = overlap_sentences
                current_chunk_length = overlap_len
                
            current_chunk_sentences.append(sentence)
            current_chunk_length += sentence_len + 1
            
    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))
        
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