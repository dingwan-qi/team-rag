"""Vector retrieval with ChromaDB when available and a JSON fallback."""

from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from contextlib import suppress
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.rag.schemas import DocumentChunk, DocumentSummary, RetrievedChunk
from app.retrieval.base import cosine_similarity, metadata_matches, tokenize


class HashingEmbedder:
    """Small local embedder used when sentence-transformers is unavailable."""

    def __init__(self, dimensions: int | None = None):
        dimensions = dimensions or int(os.getenv("HASHING_EMBEDDING_DIM", "512"))
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in tokenize(text):
            index = int(hashlib.sha1(token.encode("utf-8")).hexdigest(), 16) % self.dimensions
            vector[index] += 1.0
        return vector


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]

        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        vector = self.model.encode(text, normalize_embeddings=True)
        return [float(value) for value in vector]


def create_embedder() -> HashingEmbedder | SentenceTransformerEmbedder:
    backend = os.getenv("EMBEDDING_BACKEND", "hashing").lower().replace("_", "-")
    if backend not in {"sentence-transformers", "sentence-transformer", "st"}:
        return HashingEmbedder()
    try:
        return SentenceTransformerEmbedder(settings.embedding_model)
    except Exception:  # noqa: BLE001 - local fallback is intentional.
        return HashingEmbedder()


class JsonVectorStore:
    def __init__(self, directory: Path):
        self.directory = directory
        self.path = directory / "index.json"
        self.directory.mkdir(parents=True, exist_ok=True)
        self.embedder = create_embedder()

    @property
    def backend_name(self) -> str:
        return "json-hashing"

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"chunks": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        data = self._load()
        existing = {item["id"]: item for item in data["chunks"]}
        for chunk in chunks:
            item = chunk.model_dump()
            item["embedding"] = self.embedder.embed(chunk.text)
            existing[chunk.id] = item
        data["chunks"] = list(existing.values())
        self._save(data)

    def search(
        self,
        query: str,
        top_k: int = 4,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[RetrievedChunk]:
        query_embedding = self.embedder.embed(query)
        scored: list[RetrievedChunk] = []
        for item in self._load()["chunks"]:
            chunk = DocumentChunk(
                id=item["id"],
                document_id=item["document_id"],
                text=item["text"],
                metadata=item.get("metadata", {}),
            )
            if not metadata_matches(chunk.metadata, metadata_filter):
                continue
            score = cosine_similarity(query_embedding, item.get("embedding", []))
            scored.append(RetrievedChunk(chunk=chunk, score=score))
        scored.sort(key=lambda result: result.score, reverse=True)
        return scored[:top_k]

    def all_chunks(self) -> list[DocumentChunk]:
        return [
            DocumentChunk(
                id=item["id"],
                document_id=item["document_id"],
                text=item["text"],
                metadata=item.get("metadata", {}),
            )
            for item in self._load()["chunks"]
        ]

    def delete_document(self, document_id: str) -> int:
        data = self._load()
        before = len(data["chunks"])
        data["chunks"] = [
            item for item in data["chunks"] if item.get("document_id") != document_id
        ]
        self._save(data)
        return before - len(data["chunks"])

    def list_documents(self) -> list[DocumentSummary]:
        grouped: dict[str, list[DocumentChunk]] = defaultdict(list)
        for chunk in self.all_chunks():
            grouped[chunk.document_id].append(chunk)
        summaries: list[DocumentSummary] = []
        for document_id, chunks in grouped.items():
            first = chunks[0]
            summaries.append(
                DocumentSummary(
                    document_id=document_id,
                    filename=str(first.metadata.get("filename", "")),
                    file_type=str(first.metadata.get("file_type", "")),
                    chunk_count=len(chunks),
                ),
            )
        return sorted(summaries, key=lambda item: item.filename)


class ChromaVectorStore:
    def __init__(self, directory: Path):
        import chromadb  # type: ignore[import-not-found]

        self.client = chromadb.PersistentClient(path=str(directory))
        self.collection = self.client.get_or_create_collection("teamrag")
        self.embedder = create_embedder()

    @property
    def backend_name(self) -> str:
        return "chromadb"

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        ids = [chunk.id for chunk in chunks]
        with suppress(Exception):
            self.collection.delete(ids=ids)
        self.collection.add(
            ids=ids,
            documents=[chunk.text for chunk in chunks],
            metadatas=[_flat_metadata(chunk) for chunk in chunks],
            embeddings=[self.embedder.embed(chunk.text) for chunk in chunks],
        )

    def search(
        self,
        query: str,
        top_k: int = 4,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[RetrievedChunk]:
        where = {key: value for key, value in (metadata_filter or {}).items() if value}
        result = self.collection.query(
            query_embeddings=[self.embedder.embed(query)],
            n_results=top_k,
            where=where or None,
        )
        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        hits: list[RetrievedChunk] = []
        for chunk_id, text, metadata, distance in zip(ids, docs, metadatas, distances, strict=False):
            document_id = str(metadata.get("document_id", ""))
            chunk = DocumentChunk(
                id=str(chunk_id),
                document_id=document_id,
                text=str(text),
                metadata=dict(metadata),
            )
            hits.append(RetrievedChunk(chunk=chunk, score=1.0 / (1.0 + float(distance))))
        return hits

    def all_chunks(self) -> list[DocumentChunk]:
        result = self.collection.get()
        chunks: list[DocumentChunk] = []
        for chunk_id, text, metadata in zip(
            result.get("ids", []),
            result.get("documents", []),
            result.get("metadatas", []),
            strict=False,
        ):
            chunks.append(
                DocumentChunk(
                    id=str(chunk_id),
                    document_id=str(metadata.get("document_id", "")),
                    text=str(text),
                    metadata=dict(metadata),
                ),
            )
        return chunks

    def delete_document(self, document_id: str) -> int:
        existing = self.collection.get(where={"document_id": document_id})
        ids = existing.get("ids", [])
        if ids:
            self.collection.delete(ids=ids)
        return len(ids)

    def list_documents(self) -> list[DocumentSummary]:
        grouped: dict[str, list[DocumentChunk]] = defaultdict(list)
        for chunk in self.all_chunks():
            grouped[chunk.document_id].append(chunk)
        return [
            DocumentSummary(
                document_id=document_id,
                filename=str(chunks[0].metadata.get("filename", "")),
                file_type=str(chunks[0].metadata.get("file_type", "")),
                chunk_count=len(chunks),
            )
            for document_id, chunks in grouped.items()
        ]


def _flat_metadata(chunk: DocumentChunk) -> dict[str, str | int | float | bool]:
    metadata: dict[str, str | int | float | bool] = {"document_id": chunk.document_id}
    for key, value in chunk.metadata.items():
        if isinstance(value, (str, int, float, bool)):
            metadata[key] = value
        elif value is not None:
            metadata[key] = str(value)
    return metadata


class VectorRetriever:
    def __init__(self, directory: Path | None = None):
        directory = directory or settings.chroma_dir
        if settings.vector_backend in {"auto", "chroma"}:
            try:
                self.store: ChromaVectorStore | JsonVectorStore = ChromaVectorStore(directory)
                return
            except Exception:
                if settings.vector_backend == "chroma":
                    raise
        self.store = JsonVectorStore(directory)

    @property
    def backend_name(self) -> str:
        return self.store.backend_name

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        self.store.add_chunks(chunks)

    def search(
        self,
        query: str,
        top_k: int = 4,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[RetrievedChunk]:
        return self.store.search(query, top_k, metadata_filter)

    def all_chunks(self) -> list[DocumentChunk]:
        return self.store.all_chunks()

    def delete_document(self, document_id: str) -> int:
        return self.store.delete_document(document_id)

    def list_documents(self) -> list[DocumentSummary]:
        return self.store.list_documents()
