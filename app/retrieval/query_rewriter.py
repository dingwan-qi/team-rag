"""Query rewriting for Advanced RAG and Agentic RAG retries."""

from __future__ import annotations


class QueryRewriter:
    def rewrite(self, query: str) -> str:
        stripped = query.strip()
        if len(stripped) < 8:
            return f"{stripped} 课程资料中的定义、背景、步骤和例子"
        unclear_markers = {"这个", "那个", "它", "他们", "怎么回事", "关系"}
        if any(marker in stripped for marker in unclear_markers):
            return f"{stripped} 请结合课程资料补全相关概念、主体、关系和上下文"
        return stripped

