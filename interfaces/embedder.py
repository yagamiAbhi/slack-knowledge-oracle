from abc import ABC, abstractmethod
from typing import List
from core.entities import Document

class BaseEmbedder(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Generates a vector embedding for a single string.
        Useful for embedding the user's search query.
        """
        pass
        
    @abstractmethod
    def embed_documents(self, documents: List[Document]) -> List[Document]:
        """
        Generates and attaches embeddings to a list of Document objects.
        Returns the updated list of Documents.
        """
        pass