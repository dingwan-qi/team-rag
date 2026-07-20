# GraphRAG

GraphRAG 使用 NetworkX 构建本地知识图谱，不依赖 Neo4j。

## 流程

```text
文档块 -> 实体抽取 -> 关系抽取 -> NetworkX 图谱 -> 图谱检索 -> 向量检索融合 -> 答案
```

## 文件

- `app/graph/entity_extractor.py`
- `app/graph/relation_extractor.py`
- `app/graph/graph_builder.py`
- `app/graph/graph_store.py`
- `app/graph/graph_retriever.py`
- `app/rag/graph_rag.py`

## API

- `POST /api/knowledge-base/graph`
- `GET /api/graph`
- `GET /api/graph/search?q=实体`

