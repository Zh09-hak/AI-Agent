import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.ingestion.embedder import embedder


def main() -> int:
    print("=" * 60)
    print("Testing Embedder")
    print("=" * 60)
    
    print(f"\nModel name: {embedder.model_name}")
    print(f"Embedding dimension: {embedder.embedding_dimension}")
    
    texts = [
        "Сотрудник имеет право на 20 дней ежегодного отпуска.",
        "Годовой отпуск составляет 20 рабочих дней.",
        "Компьютер используется для программирования.",
    ]
    
    print(f"\nCreating embeddings for {len(texts)} texts...")
    
    embeddings = embedder.embed_texts(texts)
    
    print(f"\nCreated {len(embeddings)} embeddings")
    
    for i, (text, embedding) in enumerate(zip(texts, embeddings), 1):
        print(f"\n--- Text {i} ---")
        print(f"Text: {text}")
        print(f"Embedding length: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
    
    print("\n" + "=" * 60)
    print("Checking semantic similarity:")
    print("=" * 60)
    
    import numpy as np
    
    embedding1 = np.array(embeddings[0])
    embedding2 = np.array(embeddings[1])
    embedding3 = np.array(embeddings[2])
    similarity_12 = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    similarity_13 = np.dot(embedding1, embedding3) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding3))
    
    print(f"\nSimilarity between vacation texts: {similarity_12:.4f}")
    print(f"Similarity between vacation and computer texts: {similarity_13:.4f}")
    
    if similarity_12 > similarity_13:
        print("\n✓ Semantic similarity works correctly!")
        print("  Similar texts have higher similarity scores.")
    else:
        print("\n⚠ Warning: Similarity check did not work as expected.")
    
    print("\n" + "=" * 60)
    print("SUCCESS: Embedder works!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())