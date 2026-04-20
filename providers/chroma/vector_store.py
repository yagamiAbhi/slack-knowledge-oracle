import logging
import chromadb
from typing import List
from interfaces.vector_store import BaseVectorStore
from core.entities import Document
from core.registry import ProviderRegistry # <-- V2

logger = logging.getLogger(__name__)

@ProviderRegistry.register_vector_store("chroma") # <-- V2
class ChromaVectorStore(BaseVectorStore):
    def __init__(self, collection_name: str, persist_directory: str = "./chroma_db"):
        # This creates a local SQLite-backed database on your hard drive
        logger.debug(
            "Initializing ChromaDB client (collection=%s, path=%s)",
            collection_name,
            persist_directory,
        )
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Note: We do not pass an embedding function to Chroma here. 
        # Why? Because our architecture explicitly handles embeddings via the 
        # BaseEmbedder interface *before* sending data to the vector store.
        self.collection = self.client.get_or_create_collection(name=collection_name)
        logger.info("Chroma collection ready: %s", self.collection.name)

    def upsert(self, documents: List[Document]) -> None:
        if not documents:
            return

        # Unpack our Document entities into lists for Chroma
        ids = [doc.id for doc in documents]
        texts = [doc.text for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        embeddings = [doc.embedding for doc in documents]

        # Insert or update in Chroma
        self.collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        logger.info(
            "Upserted %d document(s) into Chroma collection '%s'",
            len(documents),
            self.collection.name,
        )

    def search(self, query_embedding: List[float], top_k: int) -> List[Document]:
        # Query Chroma using the raw vector
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Repackage the Chroma results back into our standard Document entities
        retrieved_docs = []
        if results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                doc = Document(
                    id=results['ids'][0][i],
                    text=results['documents'][0][i],
                    metadata=results['metadatas'][0][i] if results['metadatas'] else {},
                    embedding=None # We don't strictly need the embedding back for text generation
                )
                retrieved_docs.append(doc)

        logger.debug(
            "Chroma search completed (top_k=%d, returned=%d)",
            top_k,
            len(retrieved_docs),
        )
        return retrieved_docs
