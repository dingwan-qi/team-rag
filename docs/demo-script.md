# 课堂演示流程

## 1. 准备环境

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts/init_project.py
python scripts/build_index.py
python scripts/build_graph.py
python scripts/run_all.py
```

打开：

- Streamlit：`http://localhost:8501`
- Swagger：`http://127.0.0.1:8000/docs`

## 2. 上传课程资料

进入“知识库管理”，上传 PDF、DOCX、TXT 或 Markdown。说明系统会保存文件、解析文本、清洗、分块、写入向量库。

## 3. 创建向量索引

点击“重新扫描上传目录并索引”，展示文档数量、块数量和处理状态。

## 4. 构建知识图谱

进入“知识图谱”，点击“从当前知识库构建图谱”，展示节点数和边数。

## 5. Native RAG 提问

进入“智能问答”，选择 Native RAG，提问：

```text
RAG 的核心流程是什么？
```

展示答案、引用来源和检索片段。

## 6. Advanced RAG 提问

选择 Advanced RAG，提问：

```text
这个怎么改进检索效果？
```

展示问题改写、混合检索、重排和上下文压缩结果。

## 7. GraphRAG 提问

选择 GraphRAG，提问：

```text
GraphRAG 和知识图谱之间有什么关系？
```

展示命中实体、关系事实和引用来源。

## 8. Agentic RAG 自动选择

选择 Agentic RAG，提问：

```text
请分析 RAG、Advanced RAG 和 GraphRAG 的区别与联系。
```

展示自动选择的 RAG 路由、Agent 执行步骤、调用工具和最终答案。

## 9. 效果评估

进入“效果评估”，运行四种 RAG 对比。展示检索耗时、回答耗时、检索结果数量、引用数量和人工评分字段。

## 10. GitHub 协作展示

展示本地分支：

```bash
git branch
```

展示五人提交记录：

```bash
git log --oneline --decorate --all --graph
```

