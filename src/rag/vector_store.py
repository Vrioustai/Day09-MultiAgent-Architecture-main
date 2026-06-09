from __future__ import annotations

from pathlib import Path
from typing import Any


class ChromaPolicyStore:
    """Student scaffold for the real Chroma-backed policy index."""

    def __init__(
        self,
        persist_directory: Path,
        embedding_model: Any,
        collection_name: str = "policy_chunks",
    ) -> None:
        # TODO 1:
        # - tạo PersistentClient
        # - get_or_create_collection
        # - lưu embedding_model để dùng cho add/query
        raise NotImplementedError("Student TODO: initialize Chroma")

    def ensure_index(self, markdown_path: Path) -> None:
        # TODO 2:
        # - nếu collection rỗng thì rebuild từ markdown
        raise NotImplementedError

    def rebuild(self, markdown_path: Path) -> None:
        # TODO 3:
        # - parse markdown thành chunks
        # - embed documents bằng all-MiniLM-L6-v2
        # - add ids/documents/metadatas/embeddings vào collection
        raise NotImplementedError

    def search(self, query: str, top_k: int = 4) -> list[dict[str, Any]]:
        # TODO 4:
        # - embed query
        # - query Chroma
        # - trả list hits có citation, content, distance
        raise NotImplementedError
