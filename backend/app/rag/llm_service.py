import requests
import os


class LLMService:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3:8b"
    ):
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/chat"
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 1000,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            
            data = response.json()

            content = data.get("message", {}).get("content", "")
            
            return content.strip()
        
        except requests.exceptions.ConnectionError:
            raise Exception(
                "Cannot connect to Ollama. Is Ollama running?"
            )
        
        except requests.exceptions.Timeout:
            raise Exception(
                "LLM request timed out. The model may be too slow or the prompt too long."
            )
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"LLM request failed: {e}")

    def rewrite_query(self, history: list[dict], current_query: str) -> str:
        print(f"\n{'='*20} DEBUG REWRITE {'='*20}")
        print(f"Current Query: {current_query}")
        print(f"History length: {len(history)}")
        
        if not history:
            print("⚠️ HISTORY IS EMPTY! Skipping LLM rewrite.")
            print(f"{'='*55}\n")
            return current_query
            
        print(f"Last message in history: [{history[-1]['role']}] {history[-1]['content'][:100]}...")
            
        history_text_parts = []
        for msg in history[-4:]:
            content = msg['content']
            if msg['role'] == 'assistant' and len(content) > 300:
                content = content[:300] + "..."
            history_text_parts.append(f"{msg['role'].upper()}: {content}")
            
        history_text = "\n".join(history_text_parts)
        prompt = f"""You are an AI assistant that rewrites user questions into standalone search queries based on conversation history.
Given the chat history and the latest user question, rewrite the latest question to be a clear, standalone question that captures the full context.
If the latest question is already clear and doesn't need context, return it exactly as is.
DO NOT answer the question. ONLY output the rewritten question.

CHAT HISTORY:
{history_text}

LATEST QUESTION:
{current_query}

REWRITTEN QUESTION:"""

        try:
            raw_output = self.generate(prompt, temperature=0.0, max_tokens=300)
            print(f"RAW LLM OUTPUT:\n{raw_output}")
            
            rewritten = raw_output.strip().strip('"').strip("'")
            
            if not rewritten:
                print("⚠️ LLM returned empty string. Falling back to original query.")
                print(f"{'='*55}\n")
                return current_query
                
            print(f"FINAL REWRITTEN: {rewritten}")
            print(f"{'='*55}\n")
            return rewritten
        except Exception as e:
            print(f"Warning: Query rewriting failed: {e}. Falling back to original query.")
            print(f"{'='*55}\n")
            return current_query

llm_service = LLMService()