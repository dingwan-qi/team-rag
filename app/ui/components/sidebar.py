"""Shared Streamlit sidebar controls."""

from __future__ import annotations

import streamlit as st

from app.core.config import settings
from app.services.user_service import UserService


def render_sidebar(current_user: dict[str, str]) -> tuple[str, int]:
    st.sidebar.title("TeamRAG")
    st.sidebar.caption(f"当前用户：{current_user['username']}")
    if st.sidebar.button("退出登录"):
        token = st.session_state.get("auth_token")
        if token:
            UserService().logout(token)
        for key in ("auth_token", "current_user", "messages", "memory_loaded_user_id"):
            st.session_state.pop(key, None)
        _rerun()

    st.sidebar.divider()
    page = st.sidebar.radio(
        "页面",
        ["智能问答", "知识库管理", "知识图谱", "效果评估"],
        label_visibility="collapsed",
    )
    st.sidebar.divider()
    top_k = st.sidebar.slider("Top-K 检索数量", min_value=1, max_value=10, value=4)
    st.sidebar.caption(f"Embedding: {settings.embedding_model}")
    st.sidebar.caption(f"向量库: {settings.chroma_dir}")
    if settings.llm_api_key:
        st.sidebar.success("已配置大模型 API")
    else:
        st.sidebar.info("未配置 API Key，使用本地降级回答")
    return page, top_k


def _rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
        return
    st.experimental_rerun()
