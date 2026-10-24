import html
import re
import time
import uuid
import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Knowledge Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

.stApp, .stApp p, .stApp label, .stApp li, .stApp textarea, .stApp input, .stApp button {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
}

/* ── Chrome ─────────────────────────────────────────────── */
#MainMenu, footer, [data-testid="stDeployButton"], [data-testid="stMainMenu"] { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }
.block-container {
    max-width: 860px;
    margin: 0 auto;
    padding-top: 2.2rem;
    padding-bottom: 7rem;
}
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: rgba(127,127,127,.35); border-radius: 8px; }

/* ── Sidebar ────────────────────────────────────────────── */
section[data-testid="stSidebar"] { border-right: 1px solid rgba(127,127,127,.15); }
section[data-testid="stSidebar"] .stButton > button { width: 100%; }
.brand {
    display: flex; align-items: center; gap: .6rem;
    font-size: 1.1rem; font-weight: 600; margin: .2rem 0 1rem 0;
}
.brand-logo {
    width: 32px; height: 32px; border-radius: 10px;
    display: inline-flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #4285f4, #9b72cb 55%, #d96570);
    font-size: 1rem;
}
.side-label { font-size: .8rem; font-weight: 500; opacity: .6; margin: 1.1rem 0 .4rem 0; }
.doc-row { line-height: 1.25; padding: .15rem 0; }
.doc-name { font-size: .88rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.doc-meta { font-size: .74rem; opacity: .55; }
.status { display: flex; align-items: center; gap: .5rem; font-size: .8rem; opacity: .75; margin-top: 1.2rem; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.dot.ok { background: #34a853; box-shadow: 0 0 6px #34a853; }
.dot.bad { background: #ea4335; }

[data-testid="stFileUploaderDropzone"] {
    border-radius: 14px; border: 1.5px dashed rgba(127,127,127,.4); background: transparent;
}

/* ── Buttons ────────────────────────────────────────────── */
.stButton > button {
    border-radius: 999px;
    border: 1px solid rgba(127,127,127,.3);
    transition: background .15s ease, border-color .15s ease;
}
.stButton > button:hover { border-color: rgba(127,127,127,.7); background: rgba(127,127,127,.1); }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4285f4, #9b72cb);
    border: none; color: #fff; font-weight: 500;
}
.stButton > button[kind="primary"]:hover { filter: brightness(1.1); background: linear-gradient(135deg, #4285f4, #9b72cb); }

/* ── Hero / empty state ─────────────────────────────────── */
.hero { margin: 5vh 0 2rem 0; }
.hero-title {
    font-size: 2.8rem; font-weight: 600; line-height: 1.15; letter-spacing: -.02em;
    background: linear-gradient(90deg, #4285f4, #9b72cb 50%, #d96570);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero-sub { font-size: 2.8rem; font-weight: 600; letter-spacing: -.02em; opacity: .35; line-height: 1.15; }

/* Suggestion cards (st-key-* classes need Streamlit >= 1.39) */
[class*="st-key-sugg_"] button {
    height: 120px; width: 100%;
    border-radius: 18px; text-align: left;
    align-items: flex-start; justify-content: flex-start;
    padding: 1rem 1.1rem; white-space: normal;
    background: rgba(127,127,127,.08); border: none;
}
[class*="st-key-sugg_"] button:hover { background: rgba(127,127,127,.18); }
[class*="st-key-sugg_"] button p { font-size: .92rem; line-height: 1.4; text-align: left; }

/* ── Chat ───────────────────────────────────────────────── */
[data-testid="stChatMessage"] { background: transparent; padding: .7rem 0; gap: .9rem; }

/* User: right-aligned soft bubble, no avatar (ChatGPT / Claude style) */
[data-testid="stChatMessage"]:has([data-testid*="AvatarUser"]) { flex-direction: row-reverse; }
[data-testid*="AvatarUser"] { display: none; }
[data-testid="stChatMessage"]:has([data-testid*="AvatarUser"]) [data-testid="stChatMessageContent"] {
    background: rgba(127,127,127,.16);
    padding: .75rem 1.15rem;
    border-radius: 1.4rem 1.4rem .35rem 1.4rem;
    width: fit-content; max-width: 80%; margin-left: auto;
}

/* Assistant: no bubble, small gradient avatar */
[data-testid*="AvatarAssistant"] {
    background: linear-gradient(135deg, #4285f4, #9b72cb 55%, #d96570);
    border-radius: 10px;
}
[data-testid="stChatMessageContent"] p { line-height: 1.7; }

/* Input pill */
[data-testid="stChatInput"] {
    border-radius: 28px;
    border: 1px solid rgba(127,127,127,.3);
    box-shadow: 0 6px 28px rgba(0,0,0,.18);
}
[data-testid="stChatInput"] > div { border-radius: 28px; }
[data-testid="stChatInput"]:focus-within { border-color: rgba(138,180,248,.9); }

/* ── Sources ────────────────────────────────────────────── */
.chips { margin: .6rem 0 .2rem 0; }
.chip {
    display: inline-flex; align-items: center; gap: .4rem;
    padding: .25rem .7rem; margin: 0 .4rem .4rem 0;
    border-radius: 999px; font-size: .78rem;
    background: rgba(127,127,127,.12); border: 1px solid rgba(127,127,127,.22);
}
.chip b {
    width: 18px; height: 18px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    background: rgba(138,180,248,.25); font-size: .68rem; font-weight: 600;
}
.passage {
    font-size: .84rem; line-height: 1.55; white-space: pre-wrap;
    padding: .7rem .9rem; border-radius: 12px; margin: .3rem 0 .9rem 0;
    background: rgba(127,127,127,.09); border-left: 3px solid rgba(138,180,248,.7);
}
.passage-head { font-size: .85rem; font-weight: 500; }
.passage-meta { font-size: .75rem; opacity: .55; margin-left: .4rem; }

/* ── Misc ───────────────────────────────────────────────── */
[data-testid="stExpander"] { border-radius: 14px; border: 1px solid rgba(127,127,127,.22); }
[data-testid="stTextArea"] textarea { border-radius: 16px; }
.page-title { font-size: 1.6rem; font-weight: 600; letter-spacing: -.01em; margin: .6rem 0 .2rem 0; }
.page-sub { opacity: .6; margin-bottom: 1.2rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

ss = st.session_state
ss.setdefault("current_session_id", str(uuid.uuid4()))
ss.setdefault("messages", [])
ss.setdefault("pending_prompt", None)
ss.setdefault("agent_result", None)
ss.setdefault("agent_task", "")

SUGGESTIONS = [
    ("📝", "Summarize the key ideas from my documents"),
    ("🔎", "What are the main topics covered in my documents?"),
    ("💡", "Explain the most important concepts in simple terms"),
]
AGENT_EXAMPLES = [
    "What documents do we have?",
    "Summarize the first uploaded document",
    "Compare my two documents, focus on key differences",
]

def esc(value) -> str:
    return html.escape(str(value))


def fmt_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{num_bytes} B"


def file_icon(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return {"pdf": "📕", "docx": "📘", "txt": "📄"}.get(ext, "📄")


def stream_text(text: str):
    """Typing effect for answers that arrive from the API all at once."""
    tokens = re.split(r"(\s+)", text)
    delay = min(0.012, 2.5 / max(len(tokens), 1))
    for token in tokens:
        yield token
        time.sleep(delay)


@st.cache_data(ttl=10, show_spinner=False)
def fetch_documents() -> list[dict]:
    try:
        r = requests.get(f"{API_BASE_URL}/documents/", timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return []


@st.cache_data(ttl=15, show_spinner=False)
def api_is_healthy() -> bool:
    try:
        return requests.get(f"{API_BASE_URL}/health", timeout=5).status_code == 200
    except requests.RequestException:
        return False


def new_chat() -> None:
    ss.current_session_id = str(uuid.uuid4())
    ss.messages = []
    ss.pending_prompt = None


def queue_prompt(text: str) -> None:
    ss.pending_prompt = text


def set_agent_task(text: str) -> None:
    ss.agent_task = text


def render_sources(sources: list[dict]) -> None:
    if not sources:
        st.caption("No relevant sources were used for this answer.")
        return

    chips = "".join(
        '<span class="chip"><b>{n}</b>{name}{page}</span>'.format(
            n=esc(s["source_number"]),
            name=esc(s["filename"]),
            page=f" · p.{esc(s['page_number'])}" if s.get("page_number") else "",
        )
        for s in sources
    )
    st.markdown(f'<div class="chips">{chips}</div>', unsafe_allow_html=True)

    with st.expander(f"Show passages ({len(sources)})"):
        for s in sources:
            meta = []
            if s.get("page_number"):
                meta.append(f"page {esc(s['page_number'])}")
            if s.get("distance") is not None:
                meta.append(f"distance {s['distance']:.3f}")
            st.markdown(
                f'<div class="passage-head">[{esc(s["source_number"])}] {esc(s["filename"])}'
                f'<span class="passage-meta">{" · ".join(meta)}</span></div>'
                f'<div class="passage">{esc(s["text"])}</div>',
                unsafe_allow_html=True,
            )


def render_agent_result(data: dict) -> None:
    with st.container(border=True):
        st.markdown(data.get("answer") or "_(empty answer)_")

    if data.get("truncated"):
        st.warning("The agent reached the maximum number of steps and was stopped.")

    trace = data.get("trace", [])
    with st.expander(f"Tool trace · {len(trace)} call(s)"):
        if not trace:
            st.caption("The agent answered without calling any tool.")
        for t in trace:
            st.markdown(f"**Step {t['step']}** → `{t['tool']}`")
            st.json(t.get("arguments", {}), expanded=False)
            if t.get("error"):
                st.error(t["error"])
            if t.get("observation_preview"):
                st.text(t["observation_preview"])
            st.divider()

with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-logo">✨</span>Knowledge Assistant</div>',
        unsafe_allow_html=True,
    )
    st.button("＋  New chat", on_click=new_chat, type="primary", key="new_chat")

    st.markdown('<div class="side-label">Add a document</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None and st.button("Upload and index", key="upload_btn"):
        with st.spinner("Uploading and indexing…"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/documents/upload",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type,
                        )
                    },
                    timeout=1800,
                )
                if response.status_code == 200:
                    result = response.json()
                    fetch_documents.clear()
                    st.success(f"Uploaded {result['filename']} · {result['num_chunks']} chunks")
                else:
                    st.error(f"Upload failed: {response.text}")
            except Exception as exc:
                st.error(f"Error: {exc}")

    documents = fetch_documents()

    st.markdown(
        f'<div class="side-label">Library · {len(documents)}</div>', unsafe_allow_html=True
    )
    if documents:
        for doc in documents:
            c_info, c_del = st.columns([5, 1], vertical_alignment="center")
            with c_info:
                st.markdown(
                    f'<div class="doc-row">'
                    f'<div class="doc-name" title="{esc(doc["filename"])}">'
                    f'{file_icon(doc["filename"])} {esc(doc["filename"])}</div>'
                    f'<div class="doc-meta">{doc["num_chunks"]} chunks · '
                    f'{fmt_size(doc["file_size_bytes"])}</div></div>',
                    unsafe_allow_html=True,
                )
            with c_del:
                if st.button("✕", key=f"delete_{doc['document_id']}", help="Delete document"):
                    try:
                        dr = requests.delete(
                            f"{API_BASE_URL}/documents/{doc['document_id']}",
                            timeout=60,
                        )
                        if dr.status_code == 200:
                            fetch_documents.clear()
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {dr.text}")
                    except Exception as exc:
                        st.error(f"Error: {exc}")
    else:
        st.caption("Nothing here yet. Upload a PDF, DOCX or TXT file to get started.")

    healthy = api_is_healthy()
    st.markdown(
        f'<div class="status"><span class="dot {"ok" if healthy else "bad"}"></span>'
        f'API {"online" if healthy else "offline"}</div>',
        unsafe_allow_html=True,
    )

mode = (
    st.segmented_control(
        "Mode",
        ["💬 Chat", "🤖 Agent"],
        default="💬 Chat",
        key="mode",
        label_visibility="collapsed",
    )
    or "💬 Chat"
)

if mode == "💬 Chat":
    prompt = st.chat_input("Ask anything about your documents…")
    if prompt is None and ss.pending_prompt:
        prompt, ss.pending_prompt = ss.pending_prompt, None

    if not ss.messages and not prompt:
        st.markdown(
            '<div class="hero"><div class="hero-title">Hello there</div>'
            '<div class="hero-sub">What would you like to know?</div></div>',
            unsafe_allow_html=True,
        )
        if documents:
            cols = st.columns(len(SUGGESTIONS))
            for i, (col, (icon, text)) in enumerate(zip(cols, SUGGESTIONS)):
                with col:
                    st.button(
                        f"{icon}  {text}",
                        key=f"sugg_{i}",
                        on_click=queue_prompt,
                        args=(text,),
                    )
        else:
            st.info("Upload a document in the sidebar, then ask questions about it here.")

    for message in ss.messages:
        if message["role"] == "assistant":
            with st.chat_message("assistant", avatar="✨"):
                st.markdown(message["content"])
                render_sources(message.get("sources", []))
        else:
            with st.chat_message("user"):
                st.markdown(message["content"])

    if prompt:
        ss.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="✨"):
            answer, sources, failed = "", [], False
            with st.spinner("Thinking…"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/documents/chat",
                        json={"question": prompt, "session_id": ss.current_session_id},
                        timeout=600,
                    )
                    if response.status_code == 200:
                        result = response.json()
                        answer = result["answer"]
                        sources = result.get("sources", [])
                    else:
                        answer, failed = f"Error: {response.text}", True
                except requests.exceptions.Timeout:
                    answer, failed = "The request timed out. Try again or ask a narrower question.", True
                except Exception as exc:
                    answer, failed = f"Error: {exc}", True

            if failed:
                st.error(answer)
                ss.messages.append({"role": "assistant", "content": answer})
            else:
                st.write_stream(stream_text(answer))
                render_sources(sources)
                ss.messages.append({"role": "assistant", "content": answer, "sources": sources})

else:
    st.markdown('<div class="page-title">Agent</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-sub">Describe a task. The agent picks the tools on its own: '
        "list, search, answer, summarize or compare documents.</div>",
        unsafe_allow_html=True,
    )

    task = st.text_area(
        "Task",
        key="agent_task",
        height=110,
        label_visibility="collapsed",
        placeholder="e.g. Compare the two ML books and focus on regularization",
    )

    ex_cols = st.columns(len(AGENT_EXAMPLES))
    for i, (col, text) in enumerate(zip(ex_cols, AGENT_EXAMPLES)):
        with col:
            st.button(text, key=f"agent_ex_{i}", on_click=set_agent_task, args=(text,))

    c_slider, c_run = st.columns([3, 1], vertical_alignment="bottom")
    with c_slider:
        max_steps = st.slider("Max tool-calling steps", 1, 6, 4)
    with c_run:
        run_clicked = st.button(
            "Run agent", type="primary", disabled=not task.strip(), key="run_agent"
        )

    if run_clicked:
        ss.agent_result = None
        with st.status("Agent is working…", expanded=True) as status:
            st.write("The model is choosing tools. Large documents can take a few minutes.")
            try:
                r = requests.post(
                    f"{API_BASE_URL}/agent/task",
                    json={"task": task, "max_steps": max_steps},
                    timeout=1800,
                )
                r.raise_for_status()
                ss.agent_result = r.json()
                status.update(label="Agent finished", state="complete", expanded=False)
            except requests.RequestException as exc:
                status.update(label="Agent failed", state="error")
                st.error(f"Agent request failed: {exc}")

    if ss.agent_result:
        render_agent_result(ss.agent_result)

    st.markdown('<div class="side-label" style="margin-top:2rem">Direct tools · no LLM router</div>', unsafe_allow_html=True)

    if not documents:
        st.info("Upload at least one document to use these tools.")
    else:
        label_to_id = {d["filename"]: d["document_id"] for d in documents}
        names = list(label_to_id.keys())

        tab_sum, tab_cmp, tab_search = st.tabs(["📝 Summarize", "⚖️ Compare", "🔎 Search"])

        with tab_sum:
            choice = st.selectbox("Document", names, key="sum_choice")
            st.caption("Large documents can take 2–5 minutes (map-reduce).")
            if st.button("Summarize", key="sum_btn"):
                with st.spinner("Summarizing (map → reduce)…"):
                    try:
                        r = requests.post(
                            f"{API_BASE_URL}/agent/tool/summarize_document",
                            json={"document_id": label_to_id[choice]},
                            timeout=1800,
                        )
                        r.raise_for_status()
                        with st.container(border=True):
                            st.markdown(r.json()["result"])
                    except requests.RequestException as exc:
                        st.error(f"Summarization failed: {exc}")

        with tab_cmp:
            col_a, col_b = st.columns(2)
            with col_a:
                doc_a = st.selectbox("Document A", names, index=0, key="cmp_a")
            with col_b:
                other_names = [n for n in names if n != doc_a]
                doc_b = st.selectbox("Document B", other_names or names, index=0, key="cmp_b")
            focus = st.text_input(
                "Focus topic (optional)",
                placeholder="e.g. regularization, decision trees, overfitting",
            )
            if st.button("Compare", key="cmp_btn"):
                with st.spinner("Comparing documents…"):
                    try:
                        r = requests.post(
                            f"{API_BASE_URL}/agent/tool/compare_documents",
                            json={
                                "document_id_a": label_to_id[doc_a],
                                "document_id_b": label_to_id[doc_b],
                                "focus": focus,
                            },
                            timeout=1800,
                        )
                        r.raise_for_status()
                        with st.container(border=True):
                            st.markdown(r.json()["result"])
                    except requests.RequestException as exc:
                        st.error(f"Comparison failed: {exc}")

        with tab_search:
            query = st.text_input("Search query", placeholder="What are you looking for?")
            top_k = st.slider("Results (top_k)", 1, 10, 5)
            if st.button("Search", key="search_btn"):
                with st.spinner("Searching…"):
                    try:
                        r = requests.post(
                            f"{API_BASE_URL}/agent/tool/search_documents",
                            json={"query": query, "top_k": top_k},
                            timeout=300,
                        )
                        r.raise_for_status()
                        with st.container(border=True):
                            st.text(r.json()["result"])
                    except requests.RequestException as exc:
                        st.error(f"Search failed: {exc}")