"""Build a lightweight NetworkX knowledge graph from document chunks."""

from __future__ import annotations

import networkx as nx

from app.graph.entity_extractor import EntityExtractor
from app.graph.relation_extractor import RelationExtractor
from app.rag.schemas import DocumentChunk


class GraphBuilder:
    def __init__(self, extractor: EntityExtractor | None = None):
        self.extractor = extractor or EntityExtractor()
        self.relation_extractor = RelationExtractor(self.extractor)

    def build(self, chunks: list[DocumentChunk]) -> nx.Graph:
        graph = nx.Graph()
        for chunk in chunks:
            entities = self.extractor.extract_entities(chunk.text)
            for entity in entities:
                graph.add_node(
                    entity,
                    label=entity,
                    documents=_append_unique(
                        graph.nodes[entity].get("documents", []) if entity in graph else [],
                        chunk.document_id,
                    ),
                )
            for left, right, label in self.relation_extractor.extract(chunk.text):
                graph.add_node(left, label=left)
                graph.add_node(right, label=right)
                if graph.has_edge(left, right):
                    graph[left][right]["weight"] = graph[left][right].get("weight", 1) + 1
                else:
                    graph.add_edge(
                        left,
                        right,
                        label=label,
                        weight=1,
                        chunk_id=chunk.id,
                        filename=str(chunk.metadata.get("filename", "")),
                    )
        return graph


def _append_unique(values: list[str], value: str) -> list[str]:
    if value not in values:
        values.append(value)
    return values
