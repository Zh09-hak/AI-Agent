import requests
import streamlit as st
import time


API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Enterprise AI Knowledge Assistant",
    page_icon="🧠",
    layout="wide",
)

st.title("Enterprise AI Knowledge Assistant")

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

st.header("💬 Chat with Documents")
st.info("Chat functionality will be implemented in the next step.")

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