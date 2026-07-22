# 五名成员提交教程

本项目已经在当前目录中完成实现。五名成员领取的是已完成代码文件，不需要重新开发。每名成员只把自己的交接包复制到本地仓库，并只提交 manifest 中列出的文件。

## 通用流程

```bash
git clone 组长的GitHub仓库地址
cd team-rag

git checkout develop
git pull origin develop

git checkout -b 对应分支名称
```

然后把自己的交接包内容复制到项目根目录。注意复制时要保留原项目目录结构。

提交：

```bash
git status
git add 分配给自己的文件
git commit -m "对应的提交说明"
git push -u origin 对应分支名称
```

最后在 GitHub 创建：

```text
自己的 feature 分支 → develop
```

## 成员 1：Streamlit WebUI

- 分支：`feature/ui-webui`
- 交接包：`handoff/member-1-ui/`
- 文件清单：`handoff/manifests/member-1-files.txt`
- 提交命令：

```bash
git add app/ui docs/ui-guide.md docs/screenshots
git commit -m "feat(ui): add Streamlit RAG web interface"
git push -u origin feature/ui-webui
```

## 成员 2：文档处理和向量知识库

- 分支：`feature/document-ingestion`
- 交接包：`handoff/member-2-ingestion/`
- 文件清单：`handoff/manifests/member-2-files.txt`
- 提交命令：

```bash
git add app/ingestion app/services/document_service.py app/api/routes/documents.py app/api/routes/knowledge_base.py tests/test_loaders.py tests/test_splitter.py tests/test_ingestion.py scripts/build_index.py docs/ingestion-guide.md
git commit -m "feat(ingestion): add document parsing and vector indexing"
git push -u origin feature/document-ingestion
```

## 成员 3：Native RAG、Advanced RAG 和 Modular RAG

- 分支：`feature/native-advanced-rag`
- 交接包：`handoff/member-3-rag/`
- 文件清单：`handoff/manifests/member-3-files.txt`
- 提交命令：

```bash
git add app/retrieval app/rag/__init__.py app/rag/base.py app/rag/schemas.py app/rag/native_rag.py app/rag/advanced_rag.py app/rag/modular_rag.py tests/test_native_rag.py tests/test_advanced_rag.py docs/native-rag.md docs/advanced-rag.md
git commit -m "feat(rag): implement native and advanced RAG pipelines"
git push -u origin feature/native-advanced-rag
```

## 成员 4：GraphRAG 和知识图谱

- 分支：`feature/graphrag`
- 交接包：`handoff/member-4-graphrag/`
- 文件清单：`handoff/manifests/member-4-files.txt`
- 提交命令：

```bash
git add app/graph app/rag/graph_rag.py app/services/graph_service.py app/api/routes/graph.py scripts/build_graph.py tests/test_graph_rag.py docs/graphrag.md
git commit -m "feat(graph): implement knowledge graph and GraphRAG"
git push -u origin feature/graphrag
```

## 成员 5：Agentic RAG、FastAPI、配置和项目集成

- 分支：`feature/agentic-integration`
- 交接包：`handoff/member-5-integration/`
- 文件清单：`handoff/manifests/member-5-files.txt`
- 提交命令：

```bash
git add app/agents app/rag/agentic_rag.py app/api app/core app/services/__init__.py app/services/chat_service.py app/services/evaluation_service.py scripts/run_all.py tests/conftest.py tests/test_agentic_rag.py tests/test_api.py .github .env.example .gitignore CONTRIBUTING.md Dockerfile docker-compose.yml requirements.txt pyproject.toml README.md docs/architecture.md docs/api.md docs/git-workflow.md docs/demo-script.md docs/member-submission-guide.md
git commit -m "feat(integration): add Agentic RAG API CI and project configuration"
git push -u origin feature/agentic-integration
```

## 必须遵守

- 必须使用自己的 GitHub 账号。
- Git 本地邮箱应与自己的 GitHub 邮箱一致。
- 不要使用组长的 GitHub 账号提交。
- 不要提交不属于自己的文件。
- 不要直接提交到 `main`。
- 不要执行 force push。
- 不要把 `.env` 和 API Key 上传到 GitHub。

## 组长最终合并

建议合并顺序：

```text
1. feature/document-ingestion
2. feature/native-advanced-rag
3. feature/graphrag
4. feature/agentic-integration
5. feature/ui-webui
```

全部合并后：

```bash
git checkout develop
git pull origin develop
pip install -r requirements.txt
pytest -q
ruff check .

git checkout main
git pull origin main
git merge develop
git push origin main

git tag -a v1.0.0 -m "TeamRAG course project release"
git push origin v1.0.0
```

