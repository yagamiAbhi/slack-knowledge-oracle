from abc import ABC, abstractmethod
from typing import List
from core.entities import Document

class BaseVectorStore(ABC):
    @abstractmethod
    def upsert(self, documents: List[Document]) -> None:
        """
        Saves a list of documents and their corresponding vector embeddings 
        to the vector database.
        """
        pass

    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int) -> List[Document]:
        """
        Searches the vector database using the provided query embedding 
        and returns the top_k most similar Documents.
        """
        pass