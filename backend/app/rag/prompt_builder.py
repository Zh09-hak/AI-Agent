def build_rag_prompt(
    query: str,
    context_chunks: list[dict],
) -> str:
    if not context_chunks:
        return f"""You are a helpful company knowledge assistant.

        The user asked: "{query}"

        You do not have any documents in your knowledge base to answer this question.
        Please respond that you cannot answer because there are no relevant documents available.

        Respond in the same language as the user's question.
        """
    
    context_parts = []
    
    for i, chunk in enumerate(context_chunks, 1):
        metadata = chunk["metadata"]
        filename = metadata.get("filename", "unknown")
        page_number = metadata.get("page_number")
        chunk_index = metadata.get("chunk_index", 0)
        
        source_info = f"[Source {i}: {filename}"
        if page_number is not None:
            source_info += f", page {page_number}"
        source_info += f", chunk {chunk_index}]"
        
        context_parts.append(f"{source_info}\n{chunk['text']}")
    
    context = "\n\n".join(context_parts)
    
    prompt = f"""You are a company knowledge assistant. You MUST follow these rules STRICTLY:

    CRITICAL RULES:
    1. Answer ONLY using information from the provided context below.
    2. DO NOT use your pretrained knowledge or general knowledge.
    3. If the context does not contain the answer, you MUST say: "I don't have enough information in the available documents to answer this question."
    4. When citing sources, use ONLY sources that actually contain the information you're citing.
    5. DO NOT add "[Source X]" if that source does not contain the relevant information.
    6. If you cannot find relevant information in the sources, explicitly say so.
    7. Respond in the same language as the user's question.

    EXAMPLE OF CORRECT BEHAVIOR:
    User: "What is our vacation policy?"
    Context: [Source 1: policy.txt] Employees get 20 days vacation.
    Correct answer: "According to [Source 1], employees get 20 days vacation."

    EXAMPLE OF INCORRECT BEHAVIOR:
    User: "What is L1 regularization?"
    Context: [Source 1: policy.txt] Employees get 20 days vacation.
    Incorrect answer: "L1 regularization is a technique... [Source 1]" 
    (The answer is correct but Source 1 doesn't contain this information!)
    Correct answer: "I don't have enough information in the available documents to answer this question."

    CONTEXT FROM COMPANY DOCUMENTS:
    {context}

    USER QUESTION:
    {query}

    INSTRUCTIONS:
    - Carefully check if the context contains information to answer the question.
    - If YES: Provide answer with correct citations [Source X] where X actually contains the information.
    - If NO: Say "I don't have enough information in the available documents to answer this question."
    - DO NOT make up information or use your general knowledge.
    - DO NOT cite sources that don't contain the relevant information.

    Answer:"""
    
    return prompt