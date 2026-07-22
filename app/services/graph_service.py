"""Service layer for graph building, listing, and querying."""

from __future__ import annotations

from app.graph.graph_builder import GraphBuilder
from app.graph.graph_retriever import GraphRetriever
from app.graph.graph_store import GraphStore
from app.rag.schemas import GraphBuildResponse, GraphDataResponse, GraphHit
from app.services.document_service import DocumentService


class GraphService:
    def __init__(
        self,
        document_service: DocumentService | None = None,
        store: GraphStore | None = None,
    ):
        self.document_service = document_service or DocumentService()
        self.store = store or GraphStore()

    def build_graph(self) -> GraphBuildResponse:
        chunks = self.document_service.retriever.all_chunks()
        graph = GraphBuilder().build(chunks)
        self.store.save(graph)
        return GraphBuildResponse(
            nodes=graph.number_of_nodes(),
            edges=graph.number_of_edges(),
            message="知识图谱构建完成",
        )

    def get_graph(self) -> GraphDataResponse:
        graph = self.store.load()
        nodes = [
            {"id": str(node), "label": str(data.get("label", node))}
            for node, data in graph.nodes(data=True)
        ]
        edges = [
            {
                "source": str(source),
                "target": str(target),
                "label": str(data.get("label", "相关")),
            }
            for source, target, data in graph.edges(data=True)
        ]
        return GraphDataResponse(nodes=nodes, edges=edges)

    def search(self, query: str) -> GraphHit:
        return GraphRetriever(self.store).search(query)

