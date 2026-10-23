import json

from backend.app.database.models import Document, SessionLocal
from backend.app.ingestion.embedder import embedder
from backend.app.ingestion.storage import vector_store
from backend.app.rag.llm_service import llm_service
from backend.app.rag.prompt_builder import build_rag_prompt
from backend.app.rag.retriever import retrieve_relevant_chunks

def _resolve_document(raw_id: str) -> Document | None:
    raw_id = (raw_id or "").strip()
    if not raw_id:
        return None

    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.document_id == raw_id).first()
        if doc:
            return doc

        doc = db.query(Document).filter(Document.filename == raw_id).first()
        if doc:
            return doc

        return (
            db.query(Document)
            .filter(Document.filename.like(f"%{raw_id}%"))
            .first()
        )
    finally:
        db.close()


def _sample_evenly(items: list, max_items: int) -> list:
    if len(items) <= max_items:
        return items
    step = len(items) / max_items
    return [items[int(i * step)] for i in range(max_items)]


def _format_location(metadata: dict) -> str:
    page = metadata.get("page_number")
    if page:
        return f"page {page}"
    return f"chunk {metadata.get('chunk_index', '?')}"


def _evidence_for_document(document_id: str, focus: str, top_k: int) -> list[dict]:
    if focus.strip():
        query_embedding = embedder.embed_text(focus)
        return vector_store.search(
            query_embedding,
            top_k=top_k,
            where={"document_id": document_id},
        )

    all_chunks = vector_store.get_document_chunks(document_id)
    return _sample_evenly(all_chunks, top_k)

def list_documents() -> str:
    db = SessionLocal()
    try:
        docs = db.query(Document).order_by(Document.created_at).all()

        if not docs:
            return "The knowledge base is empty. No documents have been uploaded yet."

        lines = [f"Knowledge base contains {len(docs)} document(s):"]
        for d in docs:
            lines.append(
                f"- filename: {d.filename} | document_id: {d.document_id} | chunks: {d.num_chunks}"
            )
        return "\n".join(lines)
    finally:
        db.close()

def search_documents(query: str, top_k: int = 5) -> str:
    chunks = retrieve_relevant_chunks(query, top_k=top_k)

    if not chunks:
        return "No relevant passages were found in the knowledge base for this query."

    parts = [f"Search results for: {query!r}\n"]
    for i, c in enumerate(chunks, 1):
        md = c["metadata"]
        parts.append(
            f"[{i}] {md.get('filename')} ({_format_location(md)}) "
            f"distance={c.get('distance', 0):.3f}\n{c['text']}"
        )
    return "\n\n".join(parts)

def answer_from_evidence(question: str, top_k: int = 5) -> str:
    chunks = retrieve_relevant_chunks(question, top_k=top_k)
    prompt = build_rag_prompt(question, chunks)
    answer = llm_service.generate(prompt, temperature=0.1)

    if not chunks:
        return answer

    source_lines = ["", "Sources used:"]
    for i, c in enumerate(chunks, 1):
        md = c["metadata"]
        source_lines.append(f"[Source {i}] {md.get('filename')} ({_format_location(md)})")

    return answer + "\n".join(source_lines)

_MAP_PROMPT = """You are summarizing one section of a longer document.

SECTION TEXT:
{text}

TASK:
Write a dense factual summary of this section in at most 8 bullet points.
Keep every concrete fact, number, definition and named concept.
Do NOT add information that is not in the text.
Do NOT write an introduction or conclusion.

SUMMARY:"""

_REDUCE_PROMPT = """You are writing the final summary of the document "{filename}".

Below are summaries of consecutive sections of this document, in reading order.

{sections}

{note}

TASK:
Produce a single coherent summary of the whole document in Russian or English
(match the language of the section summaries). Use this structure:

1. One-paragraph overview of what this document is about.
2. "Key topics" — a bullet list of the main subjects covered.
3. "Most important points" — up to 8 bullets with concrete facts.
4. "Who should read this" — one sentence.

Be factual. Do NOT invent content that is absent from the section summaries.

FINAL SUMMARY:"""


def summarize_document(
    document_id: str,
    max_chunks: int = 32,
    max_batches: int = 4,
) -> str:
    
    doc = _resolve_document(document_id)
    if doc is None:
        return (
            f"ERROR: document '{document_id}' was not found. "
            f"Call list_documents first to get valid document_id values."
        )

    chunks = vector_store.get_document_chunks(doc.document_id)
    if not chunks:
        return f"ERROR: document '{doc.filename}' has no indexed chunks."

    print(f"  [summarize] {doc.filename}: {len(chunks)} chunks total")

    sampled = _sample_evenly(chunks, max_chunks)
    print(f"  [summarize] sampled {len(sampled)} chunks")

    BATCH_CHAR_LIMIT = 6000
    batches: list[str] = []
    current: list[str] = []
    current_len = 0

    for ch in sampled:
        text = ch["text"]
        if current and current_len + len(text) > BATCH_CHAR_LIMIT:
            batches.append("\n\n".join(current))
            current, current_len = [text], len(text)
        else:
            current.append(text)
            current_len += len(text)
    if current:
        batches.append("\n\n".join(current))

    note = ""
    if len(batches) > max_batches:
        batches = _sample_evenly(batches, max_batches)
        note = (
            f"NOTE: this document is long. The summary below is based on "
            f"{max_batches} sampled sections out of {len(chunks)} chunks, "
            f"so it may omit details. Mention this limitation in your answer."
        )

    print(f"  [summarize] {len(batches)} batch(es) to process")

    if len(batches) == 1:
        batch_summaries = [batches[0][:6000]]
    else:
        batch_summaries = []
        for i, batch in enumerate(batches, 1):
            print(f"  [summarize] MAP batch {i}/{len(batches)} ...")
            summary = llm_service.generate(
                _MAP_PROMPT.format(text=batch),
                temperature=0.2,
                max_tokens=500,
            )
            batch_summaries.append(summary.strip())

    sections = "\n\n".join(
        f"--- Section {i} ---\n{s}" for i, s in enumerate(batch_summaries, 1)
    )
    print(f"  [summarize] REDUCE ...")

    final = llm_service.generate(
        _REDUCE_PROMPT.format(filename=doc.filename, sections=sections, note=note),
        temperature=0.2,
        max_tokens=1200,
    )

    header = f"Summary of '{doc.filename}' (document_id: {doc.document_id})\n\n"
    return header + final.strip()

_COMPARE_PROMPT = """You are comparing two documents from a company knowledge base.

DOCUMENT A: {name_a}
{evidence_a}

DOCUMENT B: {name_b}
{evidence_b}

{focus_block}

TASK:
Compare these two documents based ONLY on the excerpts above. Produce:

1. "Common ground" — what both documents cover or agree on.
2. "Differences" — concrete differences in content, depth, terminology or recommendations.
3. "Only in A" / "Only in B" — notable points present in one document but absent in the other.
4. "Conclusion" — 2-3 sentences on how the documents relate to each other.

RULES:
- Use ONLY the excerpts provided. Never use your own knowledge.
- Cite every claim as [A] or [B].
- If the excerpts are insufficient for a meaningful comparison, say so explicitly.
- Write in the same language as the focus/question (default: English).

COMPARISON:"""


def compare_documents(
    document_id_a: str,
    document_id_b: str,
    focus: str = "",
    top_k: int = 6,
) -> str:

    doc_a = _resolve_document(document_id_a)
    doc_b = _resolve_document(document_id_b)

    if doc_a is None or doc_b is None:
        missing = document_id_a if doc_a is None else document_id_b
        return (
            f"ERROR: document '{missing}' was not found. "
            f"Call list_documents first to get valid document_id values."
        )

    if doc_a.document_id == doc_b.document_id:
        return (
            "ERROR: both arguments resolved to the same document "
            f"('{doc_a.filename}'). Provide two different documents."
        )

    chunks_a = _evidence_for_document(doc_a.document_id, focus, top_k)
    chunks_b = _evidence_for_document(doc_b.document_id, focus, top_k)

    if not chunks_a and not chunks_b:
        return "ERROR: neither document has indexed content to compare."

    def format_evidence(chunks: list[dict], label: str) -> str:
        if not chunks:
            return "(no content retrieved)"
        parts = []
        for c in chunks:
            md = c["metadata"]
            parts.append(f"[{label} — {_format_location(md)}]\n{c['text']}")
        return "\n\n".join(parts)

    focus_block = (
        f"FOCUS OF THE COMPARISON: {focus}\n"
        f"Prioritize differences and similarities related to this focus."
        if focus.strip()
        else "No specific focus was given — compare the documents overall."
    )

    prompt = _COMPARE_PROMPT.format(
        name_a=doc_a.filename,
        name_b=doc_b.filename,
        evidence_a=format_evidence(chunks_a, "A"),
        evidence_b=format_evidence(chunks_b, "B"),
        focus_block=focus_block,
    )

    print(f"  [compare] '{doc_a.filename}' vs '{doc_b.filename}' | focus={focus!r}")
    result = llm_service.generate(prompt, temperature=0.2, max_tokens=1500)

    header = f"Comparison: '{doc_a.filename}' (A) vs '{doc_b.filename}' (B)\n\n"
    return header + result.strip()

TOOL_REGISTRY: dict[str, callable] = {
    "list_documents": list_documents,
    "search_documents": search_documents,
    "answer_from_evidence": answer_from_evidence,
    "summarize_document": summarize_document,
    "compare_documents": compare_documents,
}