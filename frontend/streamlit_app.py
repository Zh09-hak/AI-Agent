import requests
import streamlit as str_lib # kept imports standard
import streamlit as st
import uuid

# Change this if your backend uses a different port.
API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Knowledge AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- SESSION STATE ----------

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- CHATGPT-STYLE MODERN CSS ----------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400..700;1,9..40,400..700&family=Manrope:wght@400..800&display=swap');

:root {
    --bg: #0b0d12;
    --sidebar: #10131a;
    --panel: #151923;
    --panel-2: #1b202b;
    --text: #f4f6fb;
    --muted: #9ba5b7;
    --border: rgba(255,255,255,.09);
    --accent: #8b7cff;
    --accent-2: #52d6c7;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 75% 0%, rgba(104, 87, 255, .13), transparent 34%),
        radial-gradient(ellipse at 20% 100%, rgba(47, 190, 179, .06), transparent 35%),
        var(--bg);
    color: var(--text);
}

header[data-testid="stHeader"] {
    background: rgba(11, 13, 18, .72);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #11141c 0%, #0d1016 100%);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.25rem 1rem;
}

.block-container {
    max-width: 920px;
    padding-top: 1.8rem;
    padding-bottom: 9rem;
}

h1, h2, h3, p, label {
    color: var(--text);
}

.brand {
    font-family: 'Manrope', sans-serif;
    font-size: 1.42rem;
    font-weight: 800;
    letter-spacing: -1px;
    padding: .45rem 0 1.4rem;
}

.brand span {
    background: linear-gradient(100deg, var(--accent), var(--accent-2));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.subtitle {
    color: var(--muted);
    font-size: .95rem;
    margin-top: -.6rem;
    margin-bottom: 2rem;
}

.welcome {
    text-align: center;
    padding: 6vh 1rem 2.5rem;
}

.welcome-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 74px;
    height: 74px;
    margin-bottom: 1.3rem;
    border: 1px solid rgba(139,124,255,.32);
    border-radius: 24px;
    background: linear-gradient(145deg, rgba(139,124,255,.19), rgba(82,214,199,.08));
    box-shadow: 0 12px 45px rgba(91,77,220,.12);
    font-size: 2rem;
}

.welcome h1 {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(1.8rem, 4vw, 2.5rem);
    font-weight: 800;
    letter-spacing: -1.4px;
    margin-bottom: .6rem;
}

div[data-testid="stChatMessage"] {
    background: rgba(255,255,255,.018);
    border: 1px solid rgba(255,255,255,.045);
    border-radius: 18px;
    padding: 1.05rem 1.2rem;
    margin: .7rem 0;
}

.stButton > button {
    min-height: 2.65rem;
    border-radius: 12px;
    border: 1px solid var(--border);
    background: linear-gradient(180deg, #202532, #191d27);
    color: var(--text);
    font-weight: 600;
    transition: all .18s ease;
}

.stButton > button:hover {
    border-color: rgba(139,124,255,.65);
    color: white;
    background: linear-gradient(180deg, #292740, #202332);
    transform: translateY(-1px);
}

.sidebar-label {
    font-size: .69rem;
    font-weight: 700;
    color: #7f8ba1;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    margin: 1.25rem 0 .65rem;
}
</style>
""", unsafe_allow_html=True)


# ---------- HELPERS ----------

def api_get_documents():
    try:
        response = requests.get(
            f"{API_BASE_URL}/documents/",
            timeout=10,
        )
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as exc:
        return None, str(exc)


def render_sources(sources):
    if not sources:
        return

    with st.expander(f"📚 Sources ({len(sources)})"):
        for source in sources:
            st.markdown(
                f"**[{source.get('source_number', '?')}] "
                f"{source.get('filename', 'Document')}**"
            )

            page = source.get("page_number")
            if page:
                st.caption(f"Page {page}")

            st.text(source.get("text", ""))
            st.divider()


def start_new_chat():
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.messages = []


def upload_and_index(file):
    try:
        with st.spinner("Processing document..."):
            response = requests.post(
                f"{API_BASE_URL}/documents/upload",
                files={
                    "file": (
                        file.name,
                        file.getvalue(),
                        file.type or "application/octet-stream",
                    )
                },
                timeout=120,
            )

        if response.ok:
            result = response.json()
            st.toast(f"✅ Indexed: {result.get('filename', file.name)} ({result.get('num_chunks', 0)} chunks)")
            st.rerun()
        else:
            st.error(f"Upload failed ({response.status_code}): {response.text[:300]}")

    except requests.RequestException as exc:
        st.error(f"Could not connect to the API: {exc}")


# ---------- SIDEBAR ----------

with st.sidebar:
    st.markdown(
        '<div class="brand">🧠 Knowledge<span>AI</span></div>',
        unsafe_allow_html=True,
    )

    if st.button("＋  New chat", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.markdown(
        '<div class="sidebar-label">Your knowledge base</div>',
        unsafe_allow_html=True,
    )

    documents, documents_error = api_get_documents()

    if documents_error:
        st.warning("Backend unavailable. Check that your API is running.")
    elif documents:
        st.caption(f"{len(documents)} document(s) indexed")

        for doc in documents:
            with st.expander(f"📄 {doc.get('filename', 'Document')}"):
                st.caption(f"Size: {doc.get('file_size_bytes', 0):,} bytes")
                st.caption(f"Chunks: {doc.get('num_chunks', 0)}")
                
                document_id = doc.get("document_id")

                if st.button(
                    "🗑 Delete",
                    key=f"delete_{document_id}",
                    use_container_width=True,
                ):
                    try:
                        result = requests.delete(
                            f"{API_BASE_URL}/documents/{document_id}",
                            timeout=30,
                        )

                        if result.ok:
                            st.success("Deleted.")
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {result.text[:300]}")
                    except requests.RequestException as exc:
                        st.error(f"API error: {exc}")
    else:
        st.caption("No documents uploaded yet.")

    if st.button("↻  Refresh documents", use_container_width=True):
        st.rerun()

    st.divider()

    st.markdown(
        '<div class="sidebar-label">System</div>',
        unsafe_allow_html=True,
    )

    if st.button("♡  Test API health", use_container_width=True):
        try:
            response = requests.get(
                f"{API_BASE_URL}/health",
                timeout=5,
            )
            if response.ok:
                st.success("API is online")
                st.json(response.json())
            else:
                st.error(f"API returned {response.status_code}")
        except requests.RequestException as exc:
            st.error(f"API unavailable: {exc}")


# ---------- MAIN CHAT AREA ----------

st.markdown(
    '<div class="brand">Knowledge AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Your documents. Your knowledge. One conversation.</div>',
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
        <div class="welcome-icon">✦</div>
        <h1>Your knowledge, unlocked.</h1>
        <p>Use the ＋ button on the left of the input box to add a document, or ask a question.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📄  Understand your documents**")
        st.caption("Get clear summaries of the main ideas and important details.")

    with col2:
        st.markdown("**🔎  Find the details that matter**")
        st.caption("Ask specific questions and review the source passages behind an answer.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            render_sources(message.get("sources", []))


# ---------- INPUT AREA WITH ＋ BUTTON ON THE LEFT ----------

# We use columns to place a small upload trigger button to the left of the chat input area
col_btn, col_input = st.columns([0.08, 0.92], vertical_alignment="bottom")

with col_btn:
    # Popover opens a sleek menu right above/next to the button when clicked
    with st.popover("＋", help="Attach document"):
        st.markdown("**Upload document** (PDF, DOCX, TXT)")
        uploaded_file = st.file_uploader(
            "Choose file",
            type=["pdf", "docx", "txt"],
            key="inline_doc_uploader",
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            if st.button("Upload & Index", use_container_width=True):
                upload_and_index(uploaded_file)

with col_input:
    prompt = st.chat_input("Message Knowledge AI or ask about your files...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching your documents..."):
                response = requests.post(
                    f"{API_BASE_URL}/documents/chat",
                    json={
                        "question": prompt,
                        "session_id": st.session_state.current_session_id,
                    },
                    timeout=120,
                )

            if response.ok:
                result = response.json()
                answer = result.get("answer", "No answer was returned.")
                sources = result.get("sources", [])

                st.markdown(answer)
                render_sources(sources)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })

            else:
                error_msg = f"API error ({response.status_code}): {response.text[:500]}"
                st.error(error_msg)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "sources": [],
                })

        except requests.exceptions.Timeout:
            error_msg = "The request timed out. Please try again."
            st.error(error_msg)

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "sources": [],
            })

        except requests.RequestException as exc:
            error_msg = "Cannot connect to the backend. Make sure the API server is running on port 8000."
            st.error(error_msg)
            st.caption(str(exc))

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "sources": [],
            })