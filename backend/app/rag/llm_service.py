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

llm_service = LLMService()