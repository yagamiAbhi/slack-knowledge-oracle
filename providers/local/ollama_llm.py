import logging
import requests
from typing import List, Dict
from interfaces.llm import BaseLLM
from core.entities import Document
from core.registry import ProviderRegistry # <-- V2

logger = logging.getLogger(__name__)

@ProviderRegistry.register_llm("ollama") # <-- V2
class OllamaLLM(BaseLLM):
    def __init__(self, model_name: str, temperature: float = 0.1, base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.temperature = temperature
        self.base_url = base_url

    def generate(self, prompt: str, context: List[Document], chat_history: List[Dict]) -> str:
        logger.debug(
            "Calling Ollama chat API (model=%s, context_docs=%d, history_messages=%d)",
            self.model_name,
            len(context),
            len(chat_history),
        )

        # 1. Format the context from retrieved documents
        context_text = "\n\n---\n\n".join([doc.text for doc in context])
        
        # 2. Build the final instruction
        final_instruction = (
            f"Use the following context to answer the user.\n\n"
            f"Context:\n{context_text}\n\n"
            f"User Prompt: {prompt}"
        )
        
        # 3. Prepare the conversation history
        messages = chat_history.copy()
        messages.append({"role": "user", "content": final_instruction})
        
        # 4. Call the local Ollama Chat API
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature
            }
        }
        
        response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=300)
        response.raise_for_status() # Raise an error if the request fails

        answer = response.json()["message"]["content"]
        logger.debug("Ollama response received (chars=%d)", len(answer))
        return answer
