import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.ingestion.embedder import embedder
from backend.app.ingestion.storage import vector_store

#test
def main() -> int:
    print("=" * 60)
    print("Testing Semantic Search")
    print("=" * 60)
    query = "Сколько дней отпуска положено сотруднику?"
    
    print(f"\nQuery: {query}")
    print("\nCreating query embedding...")
    
    query_embedding = embedder.embed_text(query)
    
    print(f"✓ Query embedding created (dimension: {len(query_embedding)})")
    
    print("\nSearching for relevant chunks...")
    results = vector_store.search(query_embedding, top_k=3)
    
    print(f"✓ Found {len(results)} relevant chunk(s)")
    
    print("\n" + "=" * 60)
    print("Search Results:")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Document: {result['metadata']['filename']}")
        print(f"Distance: {result['distance']:.4f}")
        print(f"Text preview: {result['text'][:200]}...")
    
    print("\n" + "=" * 60)
    print("SUCCESS: Semantic search works!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())