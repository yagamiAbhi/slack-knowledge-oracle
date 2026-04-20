import logging
import os
import uuid
from typing import List
from interfaces.document_loader import BaseDocumentLoader
from core.entities import Document
from core.registry import ProviderRegistry # <-- V2

logger = logging.getLogger(__name__)

@ProviderRegistry.register_loader("txt") # <-- V2
class TxtDocumentLoader(BaseDocumentLoader):
    def load(self, file_path: str) -> List[Document]:
        logger.debug("Loading text file: %s", file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        logger.debug("Loaded file content (chars=%d)", len(text))
            
        # We package the file into a Document entity.
        # Note: The chunking of this text will be handled by the IngestionService, 
        # keeping this loader strictly responsible for extraction only.
        doc = Document(
            id=str(uuid.uuid4()),
            text=text,
            metadata={
                "source": file_path, 
                "extension": ".txt"
            }
        )
        
        return [doc]
