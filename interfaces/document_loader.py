from abc import ABC, abstractmethod
from typing import List
from core.entities import Document

class BaseDocumentLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> List[Document]:
        """
        Loads a file from the given path and returns a list of parsed Document objects.
        """
        pass