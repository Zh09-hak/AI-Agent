import uuid

import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Enterprise AI Knowledge Assistant",
    page_icon="🧠",
    layout="wide",
)

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🧠 Enterprise AI Knowledge Assistant")

def fetch_documents() -> list[dict]:
    try:
        r = requests.get(f"{API_BASE_URL}/documents/", timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return []


def render_sources(sources: list[dict]) -> None:
    if not sources:
        st.caption("ℹ️ No relevant sources were used for this answer.")
        return

    with st.expander(f"📚 View Sources ({len(sources)})"):
        for s in sources:
            st.write(f"**[Source {s['source_number']}]** {s['filename']}")
            if s.get("page_number"):
                st.write(f"Page: {s['page_number']}")
            if s.get("distance") is not None:
                st.caption(f"similarity distance: {s['distance']:.3f}")
            st.text(s["text"])
            st.divider()


def render_agent_result(data: dict) -> None:
    st.subheader("Answer")
    st.markdown(data.get("answer") or "_(empty answer)_")

    if data.get("truncated"):
        st.warning("⚠️ Agent reached the maximum number of steps and was forced to stop.")

    trace = data.get("trace", [])
    with st.expander(f"🔧 Tool trace ({len(trace)} call(s))"):
        if not trace:
            st.caption("Agent answered without calling any tool.")
        for t in trace:
            st.markdown(f"**Step {t['step']} → `{t['tool']}`**")
            st.json(t.get("arguments", {}))
            if t.get("error"):
                st.error(t["error"])
            st.text(t.get("observation_preview", ""))
            st.divider()

with st.sidebar:
    st.header("Document Management")

    st.subheader("Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a file (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
    )

    if uploaded_file is not None:
        if st.button("Upload and Index"):
            with st.spinner("Uploading and indexing document..."):
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
                        st.success(f"✓ Uploaded: {result['filename']}")
                        st.info(f"Created {result['num_chunks']} chunks")
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as exc:
                    st.error(f"Error: {exc}")

    st.divider()

    st.subheader("📚 Uploaded Documents")
    documents = fetch_documents()

    if documents:
        for doc in documents:
            with st.expander(f"📄 {doc['filename']}"):
                st.write(f"**ID:** `{doc['document_id']}`")
                st.write(f"**Size:** {doc['file_size_bytes']:,} bytes")
                st.write(f"**Chunks:** {doc['num_chunks']}")
                st.write(f"**Created:** {doc['created_at']}")

                if st.button("🗑️ Delete", key=f"delete_{doc['document_id']}"):
                    with st.spinner("Deleting..."):
                        try:
                            dr = requests.delete(
                                f"{API_BASE_URL}/documents/{doc['document_id']}",
                                timeout=60,
                            )
                            if dr.status_code == 200:
                                st.success("Deleted!")
                                st.rerun()
                            else:
                                st.error(f"Delete failed: {dr.text}")
                        except Exception as exc:
                            st.error(f"Error: {exc}")
    else:
        st.info("No documents uploaded yet")

    st.divider()

    mode = st.radio(
        "Mode",
        ["💬 Chat (RAG)", "🤖 Agent"],
        help="Chat — Fast RAG with memory. Agent — the model chooses the tools itself.",
    )

    if st.button("🔄 Start New Chat"):
        st.session_state.current_session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()


if mode == "💬 Chat (RAG)":
    st.header("💬 Chat with Documents")
    st.caption("Retrieval-Augmented Generation with dialogue memory and follow-up question rewriting.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                render_sources(message.get("sources", []))

    if prompt := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Rewriting query → searching → generating..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/documents/chat",
                        json={
                            "question": prompt,
                            "session_id": st.session_state.current_session_id,
                        },
                        timeout=600,
                    )

                    if response.status_code == 200:
                        result = response.json()
                        answer = result["answer"]
                        sources = result.get("sources", [])

                        st.markdown(answer)
                        render_sources(sources)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        })
                    else:
                        error_msg = f"Error: {response.text}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg,
                        })

                except requests.exceptions.Timeout:
                    st.error("Request timed out.")
                except Exception as exc:
                    st.error(f"Error: {exc}")

else:
    st.header("🤖 AI Agent with Tools")
    st.caption(
        "Agent makes a decision what instrument to call: `list_documents`, `search_documents`, "
        "`answer_from_evidence`, `summarize_document` or `compare_documents`."
    )

    st.subheader("🧭 Autonomous agent")

    task = st.text_area(
        "Describe the task",
        height=90,
        placeholder=(
            "Например:\n"
            "• What documents do we have?\n"
            "• Summarize ML_book.pdf\n"
            "• Compare Top 100 ML Interview Questions and ML_book, focus on regularization"
        ),
    )
    max_steps = st.slider("Max tool-calling steps", 1, 6, 4)

    if st.button("🚀 Run agent", type="primary", disabled=not task.strip()):
        with st.status("Agent is working...", expanded=True) as status:
            st.write(f"Task: {task}")
            st.write("The LLM is deciding which tools to call. Large documents may take minutes.")
            try:
                r = requests.post(
                    f"{API_BASE_URL}/agent/task",
                    json={"task": task, "max_steps": max_steps},
                    timeout=1800,
                )
                r.raise_for_status()
                data = r.json()
                status.update(label="Agent finished", state="complete")
                render_agent_result(data)
            except requests.RequestException as exc:
                status.update(label="Agent failed", state="error")
                st.error(f"Agent request failed: {exc}")

    st.divider()

    st.subheader("⚡ Direct tool invocation")
    st.caption("Deterministic path: we choose the tool ourselves; the LLM router is not involved.")

    if not documents:
        st.info("Upload at least one document to use these actions.")
    else:
        label_to_id = {d["filename"]: d["document_id"] for d in documents}
        names = list(label_to_id.keys())

        tab_sum, tab_cmp, tab_search = st.tabs(["📝 Summarize", "⚖️ Compare", "🔎 Search"])

        with tab_sum:
            choice = st.selectbox("Document to summarize", names, key="sum_choice")
            st.caption("⏱ For large documents, this may take 2–5 minutes (map-reduce).")
            if st.button("📝 Summarize document"):
                with st.spinner("Summarizing document (MAP → REDUCE)..."):
                    try:
                        r = requests.post(
                            f"{API_BASE_URL}/agent/tool/summarize_document",
                            json={"document_id": label_to_id[choice]},
                            timeout=1800,
                        )
                        r.raise_for_status()
                        st.markdown(r.json()["result"])
                    except requests.RequestException as exc:
                        st.error(f"Summarization failed: {exc}")

        with tab_cmp:
            col_a, col_b = st.columns(2)
            with col_a:
                doc_a = st.selectbox("Document A", names, index=0, key="cmp_a")
            with col_b:
                other_names = [n for n in names if n != doc_a]
                doc_b = st.selectbox(
                    "Document B",
                    other_names or names,
                    index=0,
                    key="cmp_b",
                )
            focus = st.text_input(
                "Focus topic (optional)",
                placeholder="For Example: regularization, decision trees, overfitting",
            )
            if st.button("⚖️ Compare documents"):
                with st.spinner("Comparing documents..."):
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
                        st.markdown(r.json()["result"])
                    except requests.RequestException as exc:
                        st.error(f"Comparison failed: {exc}")

        with tab_search:
            query = st.text_input("Search query")
            top_k = st.slider("top_k", 1, 10, 5)
            if st.button("🔎 Search"):
                with st.spinner("Searching..."):
                    try:
                        r = requests.post(
                            f"{API_BASE_URL}/agent/tool/search_documents",
                            json={"query": query, "top_k": top_k},
                            timeout=300,
                        )
                        r.raise_for_status()
                        st.text(r.json()["result"])
                    except requests.RequestException as exc:
                        st.error(f"Search failed: {exc}")

st.divider()
if st.button("Test API Health"):
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if r.status_code == 200:
            st.success("✓ API is healthy")
            st.json(r.json())
        else:
            st.error("API is not responding")
    except Exception as exc:
        st.error(f"Error: {exc}")