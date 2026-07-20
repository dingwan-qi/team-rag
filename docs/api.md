# API 文档

FastAPI 会自动生成 Swagger：`http://127.0.0.1:8000/docs`。

## 健康检查

`GET /health`

返回服务状态、上传目录和向量库目录。

## 上传文档

`POST /api/documents/upload`

表单字段：

- `file`：PDF、DOCX、TXT、Markdown。

返回：

- `document_id`
- `filename`
- `chunks`
- `duplicate`
- `message`

## 文档列表

`GET /api/documents`

返回每个文档的 ID、文件名、类型、文档块数量和状态。

## 删除文档

`DELETE /api/documents/{document_id}`

删除向量库中的文档块和上传目录中的对应文件。

## 创建索引

`POST /api/knowledge-base/index`

扫描上传目录并重新写入索引。

## 构建图谱

`POST /api/knowledge-base/graph`

从当前索引中的文档块构建 NetworkX 图谱。

## 问答

`POST /api/chat`

```json
{
  "query": "RAG 的流程是什么？",
  "rag_mode": "agentic",
  "top_k": 4,
  "metadata_filter": null
}
```

`rag_mode` 支持 `native`、`advanced`、`graph`、`agentic`。

## 流式问答

`POST /api/chat/stream`

请求体同 `/api/chat`，返回 `text/plain` 字符流。

## 效果评估

`POST /api/evaluate`

```json
{
  "questions": ["RAG 的流程是什么？"],
  "top_k": 4
}
```

返回四种 RAG 模式的耗时、检索数量、引用数量和回答摘要。

