"""Chat page."""

from __future__ import annotations

import streamlit as st

from app.core.config import settings
from app.rag.schemas import RAGMode
from app.services.chat_service import ChatService
from app.services.user_service import UserService
from app.ui.components.retrieval_panel import render_retrieval_panel

MODE_LABELS: dict[str, RAGMode] = {
    "自动选择": "agentic",
    "Native RAG": "native",
    "Advanced RAG": "advanced",
    "GraphRAG": "graph",
    "Agentic RAG": "agentic",
}


def _rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
        return
    st.experimental_rerun()


def render(top_k: int, current_user: dict[str, str] | None = None) -> None:
    st.title("智能问答")
    st.caption("支持自动选择、Native、Advanced、Graph 和 Agentic 四种模式。")

    user_service = UserService()
    user_id = current_user["id"] if current_user else ""
    if current_user and st.session_state.get("memory_loaded_user_id") != user_id:
        st.session_state.messages = [
            {"role": message["role"], "content": message["content"]}
            for message in user_service.list_memory(user_id)
        ]
        st.session_state.memory_loaded_user_id = user_id

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if current_user:
        memory_cols = st.columns([4, 1])
        memory_cols[0].caption("当前用户的聊天记录会持久保存到本地用户库。")
        if memory_cols[1].button("清空记忆"):
            user_service.clear_memory(user_id)
            st.session_state.messages = []
            st.session_state.memory_loaded_user_id = user_id
            _rerun()

    with st.expander("模型配置", expanded=False):
        col_a, col_b, col_c = st.columns(3)
        col_a.text_input("模型名称", value=settings.llm_model or "未配置", disabled=True)
        col_b.text_input("API Base URL", value=settings.llm_base_url or "未配置", disabled=True)
        col_c.text_input("Embedding", value=settings.embedding_model, disabled=True)
        st.caption("请在 `.env` 中配置 LLM_API_KEY、LLM_BASE_URL 和 LLM_MODEL。")

    mode_label = st.segmented_control(
        "RAG 模式",
        list(MODE_LABELS),
        default="自动选择",
    )
    mode = MODE_LABELS[mode_label or "自动选择"]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    query = st.chat_input("请输入课程资料相关问题")
    if not query:
        return

    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    memory_context = user_service.memory_context(user_id) if current_user else []
    response = ChatService().answer(
        query,
        rag_mode=mode,
        top_k=top_k,
        memory_context=memory_context,
    )
    st.session_state.messages.append({"role": "assistant", "content": response.answer})
    if current_user:
        user_service.add_memory(user_id, "user", query, mode)
        user_service.add_memory(user_id, "assistant", response.answer, response.rag_mode)

    with st.chat_message("assistant"):
        st.markdown(response.answer)

    cols = st.columns(4)
    cols[0].metric("RAG 模式", response.rag_mode)
    cols[1].metric("耗时", f"{response.latency:.3f}s")
    cols[2].metric("片段", len(response.retrieved_chunks))
    cols[3].metric("引用", len(response.sources))

    if response.rewritten_query:
        st.info(f"改写后的问题：{response.rewritten_query}")

    render_retrieval_panel(response)


if __name__ == "__main__":
    page_top_k = st.sidebar.slider("Top-K 检索数量", min_value=1, max_value=10, value=4)
    render(page_top_k)
