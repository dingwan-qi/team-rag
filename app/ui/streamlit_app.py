"""Streamlit entrypoint for TeamRAG."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ui.components.sidebar import render_sidebar  # noqa: E402
from app.ui.pages import (  # noqa: E402
    auth_page,
    chat_page,
    evaluation_page,
    graph_page,
    knowledge_page,
)

st.set_page_config(page_title="TeamRAG", page_icon="TR", layout="wide")


def main() -> None:
    current_user = auth_page.ensure_authenticated()
    if current_user is None:
        return

    page, top_k = render_sidebar(current_user)
    if page == "知识库管理":
        knowledge_page.render(top_k)
    elif page == "知识图谱":
        graph_page.render(top_k)
    elif page == "效果评估":
        evaluation_page.render(top_k)
    else:
        chat_page.render(top_k, current_user)


if __name__ == "__main__":
    main()
