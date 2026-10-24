import os
import re
import requests
from openai import OpenAI

class LLMService:
    def __init__(
        self,
        base_url: str = "https://api.groq.com/openai/v1",
        model: str = "llama-3.3-70b-versatile",
        api_key: str | None = None,
    ):
        self.base_url = base_url
        self.model = model
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Set it in environment variables."
            )
        
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 1000,
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content or ""
            return content.strip()
        except Exception as e:
            raise Exception(f"LLM request failed: {e}")

    def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.0,
        max_tokens: int = 1500,
    ) -> dict:
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if tools:
                kwargs["tools"] = tools
            
            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message
            return {
                "role": message.role,
                "content": message.content or "",
                "tool_calls": message.tool_calls,
            }
        except Exception as e:
            raise Exception(f"LLM tool call failed: {e}")

    def rewrite_query(self, history: list[dict], current_query: str) -> str:
        print(f"\n{'='*20} DEBUG REWRITE {'='*20}")
        print(f"Current Query: {current_query}")
        print(f"History length: {len(history)}")

        if not history:
            print("⚠️ HISTORY IS EMPTY! Skipping LLM rewrite.")
            print(f"{'='*55}\n")
            return current_query

        history_text_parts = []
        for msg in history[-4:]:
            content = msg['content']
            if msg['role'] == 'assistant' and len(content) > 300:
                content = content[:300] + "..."
            role = "USER" if msg['role'] == 'user' else "ASSISTANT"
            history_text_parts.append(f"{role}: {content}")
        history_text = "\n".join(history_text_parts)

        prompt = f"""You are a search query rewriter. Rewrite the user's latest 
question into a standalone search query using chat history. Fix grammar, 
resolve pronouns. Output ONLY the rewritten query.

Examples:
History:
USER: What is L1 and L2?
ASSISTANT: L1 and L2 are regularization techniques.
LATEST QUESTION: What is differences between them?
REWRITTEN: What are the differences between L1 and L2 regularization?

Current Task:
History:
{history_text}
LATEST QUESTION: {current_query}
REWRITTEN:"""

        try:
            raw_output = self.generate(prompt, temperature=0.1, max_tokens=100)
            rewritten = (raw_output or "").strip().strip('"').strip("'").strip()
            print(f"RAW LLM OUTPUT:\n{raw_output}")

            if rewritten and len(rewritten) > 5 and "History:" not in rewritten:
                print(f"FINAL REWRITTEN: {rewritten}")
                print(f"{'='*55}\n")
                return rewritten
        except Exception as e:
            print(f"Warning: LLM rewrite failed: {e}")

        print("⚠️ Trying smart concatenation fallback...")
        fallback = self._smart_fallback(history, current_query)
        print(f"FALLBACK REWRITE: {fallback}")
        print(f"{'='*55}\n")
        return fallback

    def _smart_fallback(self, history: list[dict], query: str) -> str:
        user_queries = [msg["content"] for msg in history if msg["role"] == "user"]
        if not user_queries:
            return query
        first_query = user_queries[0]
        if len(query.split()) <= 8:
            if first_query.strip().lower() == query.strip().lower():
                return query
            return f"{first_query} {query}"
        return query


llm_service = LLMService()