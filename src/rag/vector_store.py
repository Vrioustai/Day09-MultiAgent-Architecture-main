from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb

from rag.parser import parse_policy_markdown


class ChromaPolicyStore:
    """Chroma-backed policy index dùng sentence-transformers embeddings."""

    def __init__(
        self,
        persist_directory: Path,
        embedding_model: Any,
        collection_name: str = "policy_chunks",
    ) -> None:
        persist_directory.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist_directory))
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._embedding_model = embedding_model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ensure_index(self, markdown_path: Path) -> None:
        """Rebuild index nếu collection đang rỗng."""
        if self._collection.count() == 0:
            self.rebuild(markdown_path)

    def rebuild(self, markdown_path: Path) -> None:
        """Parse markdown → embed → upsert vào Chroma."""
        text = markdown_path.read_text(encoding="utf-8")
        chunks = parse_policy_markdown(text)

        if not chunks:
            return

        # Xóa collection cũ nếu có dữ liệu
        existing = self._collection.count()
        if existing > 0:
            all_ids = self._collection.get()["ids"]
            self._collection.delete(ids=all_ids)

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []
        embeddings: list[list[float]] = []

        texts_to_embed = [c["rendered_text"] for c in chunks]
        embedded = self._embedding_model.embed_documents(texts_to_embed)

        for i, (chunk, emb) in enumerate(zip(chunks, embedded)):
            ids.append(f"chunk_{i:04d}")
            documents.append(chunk["rendered_text"])
            metadatas.append(
                {
                    "section_h2": chunk["section_h2"],
                    "section_h3": chunk["section_h3"],
                    "citation": chunk["citation"],
                }
            )
            embeddings.append(emb)

        self._collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def search(self, query: str, top_k: int = 4) -> list[dict[str, Any]]:
        """Embed query → query Chroma → trả list hits."""
        query_emb = self._embedding_model.embed_query(query)

        results = self._collection.query(
            query_embeddings=[query_emb],
            n_results=min(top_k, self._collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        hits: list[dict[str, Any]] = []
        if not results["ids"] or not results["ids"][0]:
            return hits

        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            hits.append(
                {
                    "citation": meta.get("citation", ""),
                    "section_h2": meta.get("section_h2", ""),
                    "section_h3": meta.get("section_h3", ""),
                    "content": doc,
                    "distance": round(dist, 4),
                }
            )

        return hits
