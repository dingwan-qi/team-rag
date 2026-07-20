# RAG 课程资料示例

RAG 是 Retrieval-Augmented Generation 的缩写。它把检索系统和大语言模型结合起来，先从知识库中检索相关片段，再把片段作为上下文交给模型生成回答。

Native RAG 的流程包括问题输入、向量检索、上下文拼接、答案生成和引用展示。

Advanced RAG 会加入问题改写、混合检索、重排、元数据过滤和上下文压缩，适合处理表述不清或需要更充分证据的问题。

GraphRAG 通过实体和关系构建知识图谱。知识图谱适合回答人物、组织、概念之间的关系问题，并可以展示节点、边和关系路径。

Agentic RAG 使用 LangGraph 工作流，根据问题类型自动选择 Native RAG、Advanced RAG 或 GraphRAG，也可以在证据不足时执行一次问题改写和重新检索。

TeamRAG 平台包括 Streamlit WebUI、FastAPI 后端、ChromaDB 向量库、sentence-transformers 本地 Embedding、OpenAI Compatible API 和 NetworkX 知识图谱。

