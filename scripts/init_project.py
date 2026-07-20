"""Create local data folders and a sample document."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import PROJECT_ROOT, settings  # noqa: E402

SAMPLE_TEXT = """# RAG 课程资料示例

RAG 是 Retrieval-Augmented Generation 的缩写。它把检索系统和大语言模型结合起来，
先从知识库中检索相关片段，再把片段作为上下文交给模型生成回答。

Native RAG 的流程包括问题输入、向量检索、上下文拼接、答案生成和引用展示。
Advanced RAG 会加入问题改写、混合检索、重排、元数据过滤和上下文压缩。
GraphRAG 通过实体和关系构建知识图谱，适合回答人物、组织和概念之间的关系问题。
Agentic RAG 使用 LangGraph 工作流，根据问题类型自动选择检索工具和回答路径。

TeamRAG 平台包括 Streamlit WebUI、FastAPI 后端、ChromaDB 向量库和 NetworkX 知识图谱。
"""


def main() -> None:
    settings.ensure_directories()
    sample_dir = PROJECT_ROOT / "data" / "samples"
    sample_dir.mkdir(parents=True, exist_ok=True)
    sample_path = sample_dir / "rag-course.md"
    if not sample_path.exists():
        sample_path.write_text(SAMPLE_TEXT, encoding="utf-8")
    print(f"初始化完成: {sample_path}")


if __name__ == "__main__":
    main()
