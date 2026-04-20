import logging
from typing import List
from interfaces.embedder import BaseEmbedder
from interfaces.vector_store import BaseVectorStore
from core.entities import Document

logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(
        self, 
        embedder: BaseEmbedder, 
        vector_store: BaseVectorStore,
        top_k: int = 5
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(self, user_query: str) -> List[Document]:
        logger.debug(
            "Retrieval started (query_chars=%d, top_k=%d)",
            len(user_query),
            self.top_k,
        )

        # 1. Embed the query
        query_embedding = self.embedder.embed_text(user_query)
        logger.debug("Query embedding generated (dimensions=%d)", len(query_embedding))
        
        # 2. Vector Search
        retrieved_docs = self.vector_store.search(query_embedding, self.top_k)
        logger.debug("Vector search returned %d document(s)", len(retrieved_docs))
        
        # 3. TODO: Implement Re-ranker (e.g., Cohere, Cross-Encoder) here in V2
        # reranked_docs = self.reranker.rank(user_query, retrieved_docs)
        # return reranked_docs
        
        return retrieved_docs
