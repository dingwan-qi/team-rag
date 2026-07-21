"""Source rendering helpers."""

from __future__ import annotations

import streamlit as st

from app.rag.schemas import RAGResponse


def render_sources(response: RAGResponse) -> None:
    st.subheader("引用来源")
    if not response.sources:
        st.info("当前回答没有引用来源。")
        return
    for index, source in enumerate(response.sources, start=1):
        score = "" if source.score is None else f" · 相关度 {source.score:.3f}"
        st.markdown(
            f"**{index}. {source.filename}** · 页码 {source.page_number or '-'}{score}",
        )


def render_chunks(response: RAGResponse) -> None:
    st.subheader("检索片段")
    if not response.retrieved_chunks:
        st.info("没有检索到片段。")
        return
    for index, hit in enumerate(response.retrieved_chunks, start=1):
        filename = hit.chunk.metadata.get("filename", "未知文件")
        with st.expander(f"{index}. {filename} · score={hit.score:.3f}"):
            st.write(hit.chunk.text)

