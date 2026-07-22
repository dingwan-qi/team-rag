"""Evaluation page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services.evaluation_service import DEFAULT_QUESTIONS, EvaluationService


def render(top_k: int) -> None:
    st.title("效果评估")
    raw_questions = st.text_area(
        "测试问题",
        value="\n".join(DEFAULT_QUESTIONS),
        height=120,
    )
    questions = [line.strip() for line in raw_questions.splitlines() if line.strip()]
    if st.button("运行四种 RAG 对比", type="primary"):
        with st.spinner("正在评估..."):
            result = EvaluationService().evaluate(questions, top_k=top_k)
        rows = [
            {
                "问题": row.question,
                "模式": row.rag_mode,
                "耗时": row.latency,
                "检索结果数": row.retrieval_count,
                "引用数": row.citation_count,
                "人工评分": row.human_score or "",
                "回答摘要": row.answer[:120],
            }
            for row in result.rows
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        st.caption("人工评分字段用于课堂演示时现场填写或导出后补充。")


if __name__ == "__main__":
    page_top_k = st.sidebar.slider("Top-K 检索数量", min_value=1, max_value=10, value=4)
    render(page_top_k)
