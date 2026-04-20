import logging
from typing import List
from interfaces.document_loader import BaseDocumentLoader
from interfaces.embedder import BaseEmbedder
from interfaces.vector_store import BaseVectorStore
from core.entities import Document

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(
        self, 
        loader: BaseDocumentLoader, 
        embedder: BaseEmbedder, 
        vector_store: BaseVectorStore,
        # Notice we removed chunk_size and chunk_overlap
    ):
        self.loader = loader
        self.embedder = embedder
        self.vector_store = vector_store

    def process_source(self, source_id: str) -> None:
        """
        source_id could be a file_path, a Slack channel_id, or a URL.
        """
        logger.info(f"Starting ingestion for source: {source_id}")
        
        # 1. Extract & Transform (Handled intelligently by the Slack Loader)
        documents = self.loader.load(source_id)
        
        if not documents:
            logger.warning("No documents found to ingest.")
            return

        # 2. Embed (We skip arbitrary chunking because the loader already chunked by thread!)
        logger.info("Generating embeddings...")
        embedded_docs = self.embedder.embed_documents(documents)
        
        # 3. Load to Database
        logger.info("Upserting to Vector Store...")
        self.vector_store.upsert(embedded_docs)