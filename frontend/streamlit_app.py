import requests
import streamlit as st
import time
import uuid

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
                    files = {"file": uploaded_file.getvalue()}
                    response = requests.post(
                        f"{API_BASE_URL}/documents/upload",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✓ Uploaded: {result['filename']}")
                        st.info(f"Created {result['num_chunks']} chunks")
                        
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {response.text}")
                
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.divider()
    
    st.subheader("📚 Uploaded Documents")
    
    if st.button("Refresh List"):
        st.rerun()
    try:
        response = requests.get(f"{API_BASE_URL}/documents/")
        
        if response.status_code == 200:
            documents = response.json()
            
            if documents:
                for doc in documents:
                    with st.expander(f"📄 {doc['filename']}"):
                        st.write(f"**ID:** {doc['document_id']}")
                        st.write(f"**Size:** {doc['file_size_bytes']:,} bytes")
                        st.write(f"**Chunks:** {doc['num_chunks']}")
                        st.write(f"**Created:** {doc['created_at']}")
                        
                        if st.button(f"🗑️ Delete", key=f"delete_{doc['document_id']}"):
                            with st.spinner("Deleting..."):
                                delete_response = requests.delete(
                                    f"{API_BASE_URL}/documents/{doc['document_id']}"
                                )
                                
                                if delete_response.status_code == 200:
                                    st.success("Deleted!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Delete failed")
            else:
                st.info("No documents uploaded yet")
        else:
            st.error("Failed to fetch documents")
    
    except Exception as e:
        st.error(f"Error: {e}")

    st.divider()
    if st.button("🔄 Start New Chat"):
        st.session_state.current_session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

st.header("💬 Chat with Documents")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message:
            if message.get("sources"):
                with st.expander("📚 View Sources"):
                    for source in message["sources"]:
                        st.write(f"**[Source {source['source_number']}]** {source['filename']}")
                        if source.get('page_number'):
                            st.write(f"Page: {source['page_number']}")
                        st.text(source['text'])
                        st.divider()
            else:
                st.caption("ℹ️ No relevant sources found in the knowledge base.")

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/documents/chat",
                    json={
                        "question": prompt,
                        "session_id": st.session_state.current_session_id
                    },
                    timeout=120,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result["answer"]
                    sources = result["sources"]
                    
                    st.markdown(answer)
                    if result.get("sources"):
                        with st.expander("📚 View Sources"):
                            for source in result["sources"]:
                                st.write(f"**[Source {source['source_number']}]** {source['filename']}")
                                if source.get('page_number'):
                                    st.write(f"Page: {source['page_number']}")
                                st.text(source['text'])
                                st.divider()
                    else:
                        st.info("ℹ️ The assistant could not find relevant documents to answer this specific question.")
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
                error_msg = "Request timed out. The LLM is taking too long to respond."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                })
            
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                })

st.divider()
if st.button("Test API Health"):
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            st.success("✓ API is healthy")
            st.json(response.json())
        else:
            st.error("API is not responding")
    except Exception as e:
        st.error(f"Error: {e}")