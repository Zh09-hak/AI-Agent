from backend.app.agent.executor import execute_tool, parse_tool_call_arguments
from backend.app.agent.tool_schemas import TOOL_SCHEMAS
from backend.app.rag.llm_service import llm_service


AGENT_SYSTEM_PROMPT = """You are an enterprise knowledge assistant for a company.
You have access to tools that inspect the company's document knowledge base.

AVAILABLE TOOLS:
- list_documents: shows which documents exist (filename + document_id)
- search_documents: fast semantic search, returns raw passages
- answer_from_evidence: full RAG answer with [Source N] citations
- summarize_document: structured summary of ONE whole document (slow)
- compare_documents: compares TWO documents, optionally around a focus topic

HOW TO WORK:
1. If the user mentions documents by name but you do not know their document_id,
   call list_documents FIRST.
2. For a direct factual question, call answer_from_evidence.
3. For "summarize document X", call summarize_document.
4. For "compare X and Y", call compare_documents with both document ids.
   Add a focus if the user mentioned a specific topic.
5. You may call several tools in sequence if the task needs it.

HARD RULES:
- NEVER invent document_id values, filenames, page numbers, quotes or facts.
- Base your final answer ONLY on tool observations.
- If the knowledge base has no answer, say so explicitly and clearly.
- Do not use your own pretrained knowledge to fill gaps.
- Reply in the same language as the user's request.
- Your final message must be a clean answer for the user, with no internal reasoning."""


def run_agent(task: str, max_steps: int = 4) -> dict:
    messages: list[dict] = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    trace: list[dict] = []
    final_answer = ""
    truncated = False

    for step in range(1, max_steps + 1):
        print(f"\n[agent] ── step {step}/{max_steps} ──")
        message = llm_service.chat_with_tools(messages, tools=TOOL_SCHEMAS)

        tool_calls = message.get("tool_calls") or []

        if not tool_calls:
            final_answer = (message.get("content") or "").strip()
            print(f"[agent] final answer ({len(final_answer)} chars)")
            break

        messages.append(message)

        for call in tool_calls:
            function_block = call.get("function", {}) or {}
            tool_name = function_block.get("name", "")
            raw_args = parse_tool_call_arguments(function_block.get("arguments"))

            print(f"[agent] tool call → {tool_name}({raw_args})")
            observation, error = execute_tool(tool_name, raw_args)

            if error:
                print(f"[agent] tool ERROR → {error}")
                content = f"ERROR: {error}"
            else:
                content = observation
                print(f"[agent] observation: {len(content)} chars")

            trace.append({
                "step": step,
                "tool": tool_name,
                "arguments": raw_args,
                "observation_preview": content[:500],
                "error": error,
            })

            messages.append({"role": "tool", "content": content})

    else:
        truncated = True
        print(f"[agent] max_steps reached, forcing final answer")
        messages.append({
            "role": "user",
            "content": (
                "Stop calling tools. Using ONLY the tool observations above, "
                "give your final answer to the user now."
            ),
        })
        message = llm_service.chat_with_tools(messages, tools=None)
        final_answer = (message.get("content") or "").strip()

    return {
        "answer": final_answer,
        "steps": len(trace),
        "truncated": truncated,
        "trace": trace,
    }