"""Heuristic routing policy for Agentic RAG."""

from __future__ import annotations

GRAPH_MARKERS = {"关系", "关联", "人物", "组织", "实体", "路径", "影响", "依赖", "连接"}
ADVANCED_MARKERS = {"比较", "分析", "为什么", "如何", "怎么", "不清楚", "多个", "步骤", "总结"}


def choose_route(query: str) -> str:
    if any(marker in query for marker in GRAPH_MARKERS):
        return "graph"
    if any(marker in query for marker in ADVANCED_MARKERS) or len(query) > 28:
        return "advanced"
    return "native"

