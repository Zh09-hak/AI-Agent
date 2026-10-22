import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    print("=" * 60)
    print("Clearing Vector Store")
    print("=" * 60)
    
    vector_store_path = Path("data/vector_store")
    
    if vector_store_path.exists():
        print(f"\nDeleting {vector_store_path}...")
        shutil.rmtree(vector_store_path)
        print("✓ Vector store cleared")
    else:
        print("\n✓ Vector store already empty")
    
    db_path = Path("data/app.db")
    
    if db_path.exists():
        print(f"\nDeleting {db_path}...")
        db_path.unlink()
        print("✓ Database cleared")
    
    print("\n" + "=" * 60)
    print("SUCCESS: All data cleared. Ready for re-indexing.")
    print("=" * 60)


if __name__ == "__main__":
    main()