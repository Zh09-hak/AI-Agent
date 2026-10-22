import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.rag.rag_pipeline import rag_query


def main() -> int:
    print("=" * 60)
    print("Testing RAG Pipeline")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("Test 1: Question with answer")
    print("=" * 60)
    
    question1 = "Сколько дней отпуска положено сотруднику?"
    
    result1 = rag_query(question1)
    
    print("\n--- Answer ---")
    print(result1["answer"])
    
    print("\n--- Sources ---")
    for source in result1["sources"]:
        print(f"\n[Source {source['source_number']}]")
        print(f"Filename: {source['filename']}")
        if source['page_number']:
            print(f"Page: {source['page_number']}")
        print(f"Preview: {source['text_preview'][:100]}...")
    
    print("\n" + "=" * 60)
    print("Test 2: Question without answer")
    print("=" * 60)
    
    question2 = "Какая погода сегодня в Москве?"
    
    result2 = rag_query(question2)
    
    print("\n--- Answer ---")
    print(result2["answer"])
    
    print("\n" + "=" * 60)
    print("SUCCESS: RAG pipeline works!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())