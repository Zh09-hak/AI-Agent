import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.ingestion.pipeline import ingest_document
from backend.app.ingestion.storage import vector_store


def main() -> int:
    test_dir = Path("data/test_docs")
    test_dir.mkdir(parents=True, exist_ok=True)
    txt_file = test_dir / "company_policy.txt"
    
    policy_text = """
    ПОЛИТИКА КОМПАНИИ О ЕЖЕГОДНОМ ОТПУСКЕ

    1. Общие положения
    Каждый сотрудник имеет право на ежегодный оплачиваемый отпуск.
    Стандартная продолжительность отпуска составляет 20 рабочих дней.

    2. Накопление отпуска
    Отпуск накапливается пропорционально отработанному времени.
    Сотрудник может использовать отпуск после 6 месяцев работы.

    3. Перенос отпуска
    Неиспользованный отпуск может быть перенесён на следующий год.
    Максимальный перенос составляет 10 дней.

    4. Отпускные выплаты
    Отпускные выплачиваются за 3 дня до начала отпуска.
    Расчёт производится на основе средней заработной платы.

    5. Больничный лист
    В случае болезни во время отпуска, отпуск продлевается.
    Необходимо предоставить больничный лист в течение 5 дней.

    6. Дополнительные дни отпуска
    Сотрудники со стажем более 5 лет получают дополнительные 5 дней.
    Сотрудники с вредными условиями труда получают дополнительные 10 дней.
    """
    
    txt_file.write_text(policy_text, encoding="utf-8")
    
    print("=" * 60)
    print("Testing Full Ingestion Pipeline")
    print("=" * 60)
    
    doc_info = ingest_document(
        file_path=txt_file,
        filename="company_policy.txt",
        mime_type="text/plain",
        chunk_size=400,
        chunk_overlap=100,
    )
    
    print("\n" + "=" * 60)
    print("Document Information:")
    print("=" * 60)
    for key, value in doc_info.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 60)
    print("Verifying Storage:")
    print("=" * 60)
    
    total_chunks = vector_store.count_chunks()
    print(f"Total chunks in vector store: {total_chunks}")
    
    doc_chunks = vector_store.get_document_chunks(doc_info["document_id"])
    print(f"Chunks for this document: {len(doc_chunks)}")
    
    for i, chunk in enumerate(doc_chunks[:2], 1):
        print(f"\n--- Chunk {i} ---")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Text preview: {chunk['text'][:100]}...")
        print(f"Metadata: {chunk['metadata']}")
    
    print("\n" + "=" * 60)
    print("SUCCESS: Full pipeline works!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())