"""Persistence for the NetworkX knowledge graph."""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
from networkx.readwrite import json_graph

from app.core.config import settings


class GraphStore:
    def __init__(self, directory: Path | None = None):
        self.directory = directory or settings.graph_dir
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "knowledge_graph.json"

    def save(self, graph: nx.Graph) -> None:
        data = json_graph.node_link_data(graph)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> nx.Graph:
        if not self.path.exists():
            return nx.Graph()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return json_graph.node_link_graph(data)

    def stats(self) -> dict[str, int]:
        graph = self.load()
        return {"nodes": graph.number_of_nodes(), "edges": graph.number_of_edges()}

