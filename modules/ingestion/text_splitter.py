from __future__ import annotations

import logging
from typing import List

from core.entities import Document

logger = logging.getLogger(__name__)


class TextSplitter:
    """Simple fixed-size splitter with overlap for long documents."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_documents(self, documents: List[Document]) -> List[Document]:
        chunked_documents: List[Document] = []

        for doc in documents:
            text = doc.text or ""
            if len(text) <= self.chunk_size:
                chunked_documents.append(doc)
                logger.debug(
                    "Document %s retained as single chunk (chars=%d)",
                    doc.id,
                    len(text),
                )
                continue

            start = 0
            chunk_index = 0
            step = self.chunk_size - self.chunk_overlap

            while start < len(text):
                end = start + self.chunk_size
                chunk_text = text[start:end]
                if not chunk_text.strip():
                    break

                chunked_documents.append(
                    Document(
                        id=f"{doc.id}:{chunk_index}",
                        text=chunk_text,
                        metadata={**doc.metadata, "chunk_index": chunk_index},
                    )
                )

                chunk_index += 1
                start += step

            logger.debug(
                "Document %s split into %d chunk(s) (chars=%d, chunk_size=%d, overlap=%d)",
                doc.id,
                chunk_index,
                len(text),
                self.chunk_size,
                self.chunk_overlap,
            )

        return chunked_documents
