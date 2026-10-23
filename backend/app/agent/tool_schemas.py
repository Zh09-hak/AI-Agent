TOOL_SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "list_documents",
            "description": (
                "List all documents currently stored in the company knowledge base. "
                "Returns filename, document_id and chunk count for each document. "
                "ALWAYS call this first when the user mentions a document by name, "
                "because other tools require an exact document_id."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": (
                "Semantic search across ALL documents in the knowledge base. "
                "Returns raw relevant passages with filename, page number and similarity distance. "
                "Use it to gather evidence. It does NOT produce a final answer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A standalone, fully detailed search query. Resolve all pronouns before calling.",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "How many passages to return. Default 5, use up to 10 for broad topics.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "answer_from_evidence",
            "description": (
                "Retrieves relevant passages AND generates a grounded, cited answer to a question. "
                "Use this instead of search_documents when the user asks a direct factual question "
                "and you want a ready-made answer with [Source N] citations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "A standalone, fully detailed question with all pronouns resolved.",
                    },
                    "top_k": {"type": "integer", "description": "Passages to retrieve. Default 5."},
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_document",
            "description": (
                "Produce a structured summary of ONE whole document using map-reduce summarization. "
                "Use this when the user asks to summarize, give an overview of, or explain "
                "what a specific document is about. This is SLOW for large documents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "Exact document_id or filename obtained from list_documents.",
                    },
                },
                "required": ["document_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_documents",
            "description": (
                "Compare TWO different documents and explain their similarities and differences with citations. "
                "Use this when the user asks to compare, contrast, find differences, "
                "or mentions two document versions. Optionally narrow the comparison with a focus topic."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id_a": {
                        "type": "string",
                        "description": "document_id or filename of the FIRST document.",
                    },
                    "document_id_b": {
                        "type": "string",
                        "description": "document_id or filename of the SECOND document.",
                    },
                    "focus": {
                        "type": "string",
                        "description": (
                            "Optional topic to focus the comparison on, e.g. 'regularization' or 'decision trees'. "
                            "Leave empty for a general comparison."
                        ),
                    },
                },
                "required": ["document_id_a", "document_id_b"],
            },
        },
    },
]