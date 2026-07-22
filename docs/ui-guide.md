# TeamRAG WebUI 说明

新版 WebUI 入口为 `app/web/start.html`，由 FastAPI 托管。启动后端后访问：

```text
http://127.0.0.1:8000
```

项目也保留 Streamlit 备用入口：`app/ui/streamlit_app.py`。

## 页面

- 开始页：使用 `photo/start.png` 背景，包含动态字幕、立即体验按钮、登录和注册卡片。
- 智能问答：聊天历史、RAG 模式选择、Top-K、模型配置展示、引用来源、检索片段和执行轨迹。
- 知识库管理：上传课程资料、索引、文档列表和删除。
- 知识图谱：构建图谱、查看节点/边、实体搜索和关系展示。
- 效果评估：对比 Native、Advanced、GraphRAG、Agentic RAG。

## 运行

新版静态前端：

```bash
uvicorn app.api.main:app --reload --port 8000
```

备用 Streamlit：

```bash
streamlit run app/ui/streamlit_app.py
```

## 说明

新版静态前端通过浏览器调用 FastAPI 接口，并使用 `/api/auth/*` 和 `/api/memory` 实现登录注册与用户记忆持久化。Streamlit 页面默认直接调用本地服务层，适合作为备用课堂演示入口。
