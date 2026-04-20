import logging
import requests
from typing import List
from interfaces.embedder import BaseEmbedder
from core.entities import Document
from core.registry import ProviderRegistry # <-- V2

logger = logging.getLogger(__name__)

@ProviderRegistry.register_embedder("ollama") # <-- V2
class OllamaEmbedder(BaseEmbedder):
    def __init__(self, model_name: str, base_url: str = "http://127.0.0.1:11434"):
        self.model_name = model_name
        self.base_url = base_url

    def _embed_text(self, text: str, emit_logs: bool = True) -> List[float]:
        if emit_logs:
            logger.debug(
                "Requesting embedding from Ollama (model=%s, input_chars=%d)",
                self.model_name,
                len(text),
            )
        payload = {
            "model": self.model_name,
            "prompt": text
        }
        
        response = requests.post(f"{self.base_url}/api/embeddings", json=payload, timeout=60)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            error_message = response.text
            try:
                error_message = response.json().get("error", response.text)
            except ValueError:
                pass
            raise RuntimeError(
                f"Ollama embedding failed for model '{self.model_name}': {error_message}"
            ) from exc
        
        embedding = response.json()["embedding"]
        if emit_logs:
            logger.debug("Embedding received (dimensions=%d)", len(embedding))
        return embedding

    def embed_text(self, text: str) -> List[float]:
        return self._embed_text(text, emit_logs=True)

    def embed_documents(self, documents: List[Document]) -> List[Document]:
        logger.debug(
            "Embedding %d document chunk(s) with Ollama model %s",
            len(documents),
            self.model_name,
        )

        total_docs = len(documents)
        for index, doc in enumerate(documents, start=1):
            doc.embedding = self._embed_text(doc.text, emit_logs=False)
            if index % 50 == 0 or index == total_docs:
                logger.debug("Embedding progress: %d/%d chunk(s)", index, total_docs)

        logger.debug("Attached embeddings to %d document chunk(s)", len(documents))
        return documents
