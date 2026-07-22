"""Knowledge graph page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.graph.graph_builder import GraphBuilder
from app.graph.graph_retriever import GraphRetriever
from app.graph.graph_store import GraphStore
from app.services.document_service import DocumentService
from app.ui.components.graph_view import render_graph


def render(_: int) -> None:
    st.title("知识图谱")
    service = DocumentService()
    store = GraphStore()

    if st.button("从当前知识库构建图谱", type="primary"):
        chunks = service.retriever.all_chunks()
        graph = GraphBuilder().build(chunks)
        store.save(graph)
        st.success(f"构建完成：{graph.number_of_nodes()} 个节点，{graph.number_of_edges()} 条边")

    graph = store.load()
    stats = store.stats()
    cols = st.columns(2)
    cols[0].metric("节点数", stats["nodes"])
    cols[1].metric("边数", stats["edges"])

    render_graph(graph)

    entity = st.text_input("搜索实体或关系问题")
    if entity:
        hit = GraphRetriever(store).search(entity)
        st.subheader("命中实体")
        st.write("、".join(hit.matched_entities) or "未命中")
        if hit.edges:
            st.dataframe(pd.DataFrame(hit.edges), use_container_width=True)
        if hit.facts:
            st.subheader("相关关系")
            for fact in hit.facts:
                st.markdown(f"- {fact}")

    if graph.number_of_edges() > 0:
        rows = [
            {"source": source, "target": target, "label": data.get("label", "相关")}
            for source, target, data in graph.edges(data=True)
        ]
        st.subheader("图谱边列表")
        st.dataframe(pd.DataFrame(rows), use_container_width=True)


if __name__ == "__main__":
    render(4)
