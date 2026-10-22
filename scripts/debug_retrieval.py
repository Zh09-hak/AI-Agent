import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.rag.retriever import retrieve_relevant_chunks


def main():
    print("=" * 60)
    print("Debug: Checking what retriever returns")
    print("=" * 60)
    
    query = "What is L1 regularizator and compare it to L2"
    
    print(f"\nQuery: {query}\n")
    
    chunks = retrieve_relevant_chunks(query, top_k=5)
    
    print(f"Retrieved {len(chunks)} chunks:\n")
    
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        print(f"--- Chunk {i} ---")
        print(f"Filename: {metadata.get('filename')}")
        print(f"Page: {metadata.get('page_number')}")
        print(f"Distance: {chunk.get('distance', 'N/A')}")
        print(f"Text preview: {chunk['text'][:200]}...")
        print()
    
    has_l1 = any("L1" in chunk["text"] for chunk in chunks)
    has_l2 = any("L2" in chunk["text"] for chunk in chunks)
    has_regulariz = any("regulariz" in chunk["text"].lower() for chunk in chunks)
    
    print("=" * 60)
    print("Analysis:")
    print("=" * 60)
    print(f"Contains 'L1': {has_l1}")
    print(f"Contains 'L2': {has_l2}")
    print(f"Contains 'regulariz*': {has_regulariz}")
    
    if not (has_l1 and has_l2):
        print("\n⚠ WARNING: Retriever did not find chunks about L1/L2 regularization!")
        print("This means either:")
        print("1. Your document doesn't contain information about L1/L2")
        print("2. The embedding model is not finding relevant chunks")
        print("3. The chunk size/overlap is too small")


if __name__ == "__main__":
    main()