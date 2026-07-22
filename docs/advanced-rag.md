# Advanced RAG

Advanced RAG 在 Native RAG 基础上增加：

- Query Rewrite
- Hybrid Retrieval
- Lightweight Rerank
- Metadata Filter
- Context Compression

入口：

```python
from app.rag.advanced_rag import AdvancedRAG

response = AdvancedRAG().answer("这个怎么改进？", top_k=4)
```

当前重排策略是轻量可替换实现，不依赖专用模型；后续可以把 `LightweightReranker` 替换为 BGE reranker 或其他模型。

