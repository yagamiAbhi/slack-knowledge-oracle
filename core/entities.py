from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class Document:
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[list[float]] = None