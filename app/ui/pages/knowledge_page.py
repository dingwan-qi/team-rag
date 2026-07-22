"""Knowledge base management page."""

from __future__ import annotations

import streamlit as st

from app.core.exceptions import TeamRAGError
from app.services.document_service import DocumentService


def render(_: int) -> None:
    st.title("知识库管理")
    service = DocumentService()

    uploaded = st.file_uploader(
        "上传课程资料",
        type=["pdf", "docx", "txt", "md", "markdown"],
        accept_multiple_files=True,
    )
    if uploaded and st.button("上传并创建索引", type="primary"):
        for file in uploaded:
            try:
                result = service.save_and_index(file.name, file.getvalue())
                if result.duplicate:
                    st.warning(f"{file.name}: {result.message}")
                else:
                    st.success(f"{file.name}: 已生成 {result.chunks} 个文档块")
            except (TeamRAGError, ValueError) as exc:
                st.error(f"{file.name}: {exc}")

    col_a, col_b = st.columns(2)
    if col_a.button("重新扫描上传目录并索引"):
        result = service.index_uploaded_files()
        st.success(f"{result.message}：{result.indexed_documents} 个文档，{result.indexed_chunks} 个片段")
    if col_b.button("刷新列表"):
        st.rerun()

    documents = service.list_documents()
    st.subheader("已上传文档")
    if not documents:
        st.info("暂无文档，请先上传课程资料。")
        return

    for document in documents:
        cols = st.columns([3, 1, 1, 1])
        cols[0].markdown(f"**{document.filename}**")
        cols[1].write(document.file_type)
        cols[2].write(f"{document.chunk_count} 块")
        if cols[3].button("删除", key=f"delete-{document.document_id}"):
            service.delete_document(document.document_id)
            st.rerun()


if __name__ == "__main__":
    render(4)
