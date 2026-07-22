"""Reusable retrieval and trace panels."""

from __future__ import annotations

import streamlit as st

from app.rag.schemas import RAGResponse
from app.ui.components.source_card import render_chunks, render_sources


def render_retrieval_panel(response: RAGResponse) -> None:
    if response.trace:
        st.subheader("执行轨迹")
        for step in response.trace:
            tool = f" · 工具：{step.tool}" if step.tool else ""
            st.markdown(f"- **{step.name}**：{step.detail}{tool}")
    elif response.agent_steps:
        st.subheader("Agent 执行过程")
        for step in response.agent_steps:
            tool = f" · 工具：{step.tool}" if step.tool else ""
            st.markdown(f"- **{step.name}**：{step.detail}{tool}")

    if response.graph and response.graph.facts:
        st.subheader("图谱命中关系")
        for fact in response.graph.facts:
            st.markdown(f"- {fact}")

    render_sources(response)
    render_chunks(response)

