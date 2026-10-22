import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.ingestion.storage import vector_store


def main():
    print("=" * 60)
    print("ChromaDB Diagnostic")
    print("=" * 60)
    
    total_chunks = vector_store.count_chunks()
    print(f"\nTotal chunks in database: {total_chunks}")
    
    if total_chunks == 0:
        print("\n⚠ DATABASE IS EMPTY! No documents indexed.")
        return
    
    all_chunks = vector_store.collection.get(
        include=["documents", "metadatas"]
    )
    
    print(f"\nFirst 3 chunks:")
    for i in range(min(3, len(all_chunks["ids"]))):
        chunk_id = all_chunks["ids"][i]
        text = all_chunks["documents"][i]
        metadata = all_chunks["metadatas"][i]
        
        print(f"\n--- Chunk {i+1} ---")
        print(f"ID: {chunk_id}")
        print(f"Filename: {metadata.get('filename')}")
        print(f"Text length: {len(text)} characters")
        print(f"Text preview: {text[:200]}...")
        
        if "L1" in text or "L2" in text:
            print("✓ Contains L1 or L2!")
        if "regulariz" in text.lower():
            print("✓ Contains 'regulariz*'!")


if __name__ == "__main__":
    main()