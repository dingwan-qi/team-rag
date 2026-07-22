# Native RAG

Native RAG 实现标准检索增强生成流程：

```text
问题 -> 向量检索 -> Top-K 文档片段 -> 上下文 -> LLM/Mock LLM -> 答案和引用
```

入口：

```python
from app.rag.native_rag import NativeRAG

response = NativeRAG().answer("RAG 的流程是什么？", top_k=4)
```

返回结构为 `RAGResponse`，包含 `answer`、`sources`、`retrieved_chunks`、`rag_mode`、`latency`、`trace`。

