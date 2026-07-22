# API 文档

FastAPI 会自动生成 Swagger：`http://127.0.0.1:8000/docs`。

新版 Web 前端入口：`http://127.0.0.1:8000`，实际静态文件位于 `/web/start.html` 和 `/web/qa-index.html`。

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

## 用户注册

`POST /api/auth/register`

```json
{
  "username": "member5",
  "password": "password123"
}
```

返回登录 token 和用户信息。

## 用户登录

`POST /api/auth/login`

```json
{
  "username": "member5",
  "password": "password123"
}
```

返回登录 token。后续需要用户记忆的接口，在请求头中加入：

```text
Authorization: Bearer <token>
```

## 当前用户

`GET /api/auth/me`

需要 `Authorization` 请求头。

## 退出登录

`POST /api/auth/logout`

需要 `Authorization` 请求头。

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

如果请求头携带有效 `Authorization: Bearer <token>`，系统会读取该用户最近聊天记忆辅助理解当前问题，并把本轮问答保存到用户记忆中。

## 用户记忆

`GET /api/memory`

返回当前登录用户的历史聊天记忆。

`DELETE /api/memory`

清空当前登录用户的历史聊天记忆。

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
