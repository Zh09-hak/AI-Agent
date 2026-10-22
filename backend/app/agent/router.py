from backend.app.agent.tools import search_documents, list_documents, summarize_document
def route_task(task: str, params: dict) -> str:
    task = task.lower()
    
    if "list" in task or "what documents" in task:
        return list_documents()
        
    elif "summarize" in task or "summary" in task:
        doc_id = params.get("document_id", "")
        if not doc_id:
            return "Please provide a document_id to summarize."
        return summarize_document(doc_id)
        
    else:
        query = params.get("query", task)
        return search_documents(query)