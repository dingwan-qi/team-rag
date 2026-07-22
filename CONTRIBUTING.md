# TeamRAG 协作指南

## 分支策略

- `main`：稳定版本，只接受从 `develop` 合并。
- `develop`：功能集成分支。
- `feature/ui-webui`：成员 1，Streamlit WebUI。
- `feature/document-ingestion`：成员 2，文档处理与知识库。
- `feature/native-advanced-rag`：成员 3，Native RAG 与 Advanced RAG。
- `feature/graphrag`：成员 4，GraphRAG。
- `feature/agentic-integration`：成员 5，Agent、API、CI、Docker 和集成。

## 开发流程

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-branch
```

提交前运行：

```bash
pytest -q
ruff check .
```

推送并创建 PR：

```bash
git push -u origin feature/your-branch
```

PR 必须写清楚功能说明、测试方法和修改文件。禁止直接 force push `main`。

## 提交规范

推荐使用：

- `feat: add document upload pipeline`
- `fix: handle empty document upload`
- `test: add api route tests`
- `docs: update demo script`
- `chore: update ci config`

