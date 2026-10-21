from pathlib import Path
import pymupdf as fitz
import docx


def extract_text_from_pdf(file_path: Path) -> list[tuple[str, int | None]]:
    pages = []
    doc = fitz.open(file_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        pages.append((text, page_num + 1))
    doc.close()
    return pages


def extract_text_from_docx(file_path: Path) -> list[tuple[str, int | None]]:
    doc = docx.Document(file_path)
    full_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return [(full_text, None)]


def extract_text_from_txt(file_path: Path) -> list[tuple[str, int | None]]:
    text = file_path.read_text(encoding="utf-8")
    return [(text, None)]


def extract_text(file_path: Path, mime_type: str) -> list[tuple[str, int | None]]:
    mime_type_lower = mime_type.lower()
    
    if mime_type_lower == "application/pdf":
        return extract_text_from_pdf(file_path)
    
    elif mime_type_lower in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",):
        return extract_text_from_docx(file_path)
    
    elif mime_type_lower == "text/plain":
        return extract_text_from_txt(file_path)
    
    else:
        raise ValueError(f"Unsupported mime type: {mime_type}")