"""OpenAI-compatible LLM client with a deterministic local fallback."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from app.core.config import settings
from app.rag.schemas import RetrievedChunk


class LLMClient:
    def generate(
        self,
        *,
        query: str,
        chunks: list[RetrievedChunk],
        graph_facts: list[str] | None = None,
    ) -> str:
        if settings.llm_api_key and settings.llm_base_url and settings.llm_model:
            try:
                return self._call_openai_compatible(query, chunks, graph_facts or [])
            except Exception as exc:  # noqa: BLE001 - degrade gracefully for demo use.
                fallback = self._fallback_answer(query, chunks, graph_facts or [])
                return f"LLM 调用失败，已切换为本地降级回答。错误: {exc}\n\n{fallback}"
        return self._fallback_answer(query, chunks, graph_facts or [])

    def _call_openai_compatible(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        graph_facts: list[str],
    ) -> str:
        endpoint = settings.llm_base_url.rstrip("/")
        if not endpoint.endswith("/chat/completions"):
            endpoint = f"{endpoint}/chat/completions" if endpoint.endswith("/v1") else (
                f"{endpoint}/v1/chat/completions"
            )
        context = "\n\n".join(
            f"[{index}] {hit.chunk.text}" for index, hit in enumerate(chunks, start=1)
        )
        facts = "\n".join(f"- {fact}" for fact in graph_facts)
        payload = {
            "model": settings.llm_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是课程资料问答助手。只能基于给定上下文回答，"
                        "答案需要简洁，并在相关句子后标注引用编号。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"问题: {query}\n\n检索上下文:\n{context}\n\n"
                        f"图谱事实:\n{facts or '无'}"
                    ),
                },
            ],
            "temperature": 0.2,
        }
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        try:
            return str(data["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError) as exc:
            raise urllib.error.URLError("LLM 返回格式不符合 OpenAI Chat Completions") from exc

    def _fallback_answer(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        graph_facts: list[str],
    ) -> str:
        if not chunks and not graph_facts:
            return "知识库中暂未检索到足够证据。请先上传并索引课程资料，或换一个更具体的问题。"
        lines = [
            f"基于当前知识库，问题“{query}”可以从以下资料片段得到线索：",
        ]
        for index, hit in enumerate(chunks[:4], start=1):
            snippet = hit.chunk.text.replace("\n", " ").strip()
            if len(snippet) > 180:
                snippet = f"{snippet[:180]}..."
            filename = hit.chunk.metadata.get("filename", "未知文件")
            lines.append(f"{index}. {snippet}（来源：{filename}）")
        if graph_facts:
            lines.append("图谱中还发现这些关系：")
            lines.extend(f"- {fact}" for fact in graph_facts[:6])
        lines.append("当前为本地降级回答；配置 LLM_API_KEY 后会调用真实大模型生成完整答案。")
        time.sleep(0.01)
        return "\n".join(lines)

