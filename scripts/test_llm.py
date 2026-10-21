import os
import sys

import requests


OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")


def main() -> int:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Reply with exactly one word: LLM_OK",
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.0
        },
    }

    print(f"Testing Ollama URL: {OLLAMA_API_URL}")
    print(f"Model: {OLLAMA_MODEL}")

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
        response.raise_for_status()

        data = response.json()
        content = data.get("message", {}).get("content", "")

        print("LLM response:")
        print(content)

        if "LLM_OK" in content:
            print("SUCCESS: LLM call works.")
            return 0

        print("WARNING: LLM responded, but did not return the expected token.")
        return 0

    except requests.exceptions.ConnectionError:
        print("ERROR: cannot connect to Ollama.")
        print("Is Ollama installed and running?")
        return 1

    except requests.exceptions.RequestException as exc:
        print(f"ERROR: LLM request failed: {exc}")

        response = getattr(exc, "response", None)
        if response is not None:
            print(response.text)

        return 1


if __name__ == "__main__":
    sys.exit(main())