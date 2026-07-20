"""Build the NetworkX knowledge graph from indexed chunks."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.graph.graph_builder import GraphBuilder  # noqa: E402
from app.graph.graph_store import GraphStore  # noqa: E402
from app.services.document_service import DocumentService  # noqa: E402


def main() -> None:
    service = DocumentService()
    chunks = service.retriever.all_chunks()
    graph = GraphBuilder().build(chunks)
    GraphStore().save(graph)
    print(f"知识图谱构建完成: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")


if __name__ == "__main__":
    main()
