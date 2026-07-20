"""Graph retrieval for matched entities, neighbors, and relation facts."""

from __future__ import annotations

import networkx as nx

from app.graph.entity_extractor import EntityExtractor
from app.graph.graph_store import GraphStore
from app.rag.schemas import GraphHit


class GraphRetriever:
    def __init__(
        self,
        store: GraphStore | None = None,
        extractor: EntityExtractor | None = None,
    ):
        self.store = store or GraphStore()
        self.extractor = extractor or EntityExtractor()

    def search(self, query: str, limit: int = 12) -> GraphHit:
        graph = self.store.load()
        if graph.number_of_nodes() == 0:
            return GraphHit()
        matched = self._match_entities(graph, query)
        nodes: set[str] = set(matched)
        edges: list[dict[str, str]] = []
        facts: list[str] = []

        for entity in matched:
            for neighbor in list(graph.neighbors(entity))[:limit]:
                nodes.add(neighbor)
                edge_data = graph.get_edge_data(entity, neighbor, default={})
                label = str(edge_data.get("label", "相关"))
                edges.append({"source": entity, "target": neighbor, "label": label})
                facts.append(f"{entity} -[{label}]- {neighbor}")

        return GraphHit(
            matched_entities=matched,
            nodes=sorted(nodes),
            edges=edges[:limit],
            facts=facts[:limit],
        )

    def _match_entities(self, graph: nx.Graph, query: str) -> list[str]:
        query_entities = self.extractor.extract_entities(query, limit=10)
        matched: list[str] = []
        for node in graph.nodes:
            node_text = str(node)
            if node_text in query or any(entity in node_text or node_text in entity for entity in query_entities):
                matched.append(node_text)
        if matched:
            return matched[:8]
        query_chars = set(query)
        scored = []
        for node in graph.nodes:
            overlap = len(query_chars & set(str(node)))
            if overlap:
                scored.append((overlap, str(node)))
        scored.sort(reverse=True)
        return [node for _, node in scored[:3]]

