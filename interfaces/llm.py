from abc import ABC, abstractmethod
from typing import List, Dict
from core.entities import Document

class BaseLLM(ABC):
    @abstractmethod
    def generate(self, prompt: str, context: List[Document], chat_history: List[Dict]) -> str:
        """
        Generates a text response based on the final prompt, 
        the retrieved context documents, and the user's chat history.
        """
        pass