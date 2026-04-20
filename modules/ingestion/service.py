import logging
from typing import List
from interfaces.document_loader import BaseDocumentLoader
from interfaces.embedder import BaseEmbedder
from interfaces.vector_store import BaseVectorStore
from core.entities import Document
from modules.ingestion.text_splitter import TextSplitter

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(
        self, 
        loader: BaseDocumentLoader, 
        embedder: BaseEmbedder, 
        vector_store: BaseVectorStore,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.loader = loader
        self.embedder = embedder
        self.vector_store = vector_store
        self.splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def process_file(self, file_path: str) -> None:
        logger.info("Ingestion started for file: %s", file_path)

        # 1. Extract
        documents = self.loader.load(file_path)
        logger.debug("Loaded %d document(s) from source", len(documents))
        
        # 2. Transform (Chunking logic goes here - simplified for this step)
        chunked_docs = self._chunk_documents(documents)
        logger.debug("Chunking produced %d document chunk(s)", len(chunked_docs))
        
        # 3. Embed
        embedded_docs = self.embedder.embed_documents(chunked_docs)
        logger.debug("Embeddings generated for %d chunk(s)", len(embedded_docs))
        
        # 4. Load
        self.vector_store.upsert(embedded_docs)
        logger.info("Ingestion finished for file: %s", file_path)

    def _chunk_documents(self, documents: List[Document]) -> List[Document]:
        return self.splitter.split_documents(documents)
