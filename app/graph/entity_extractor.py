"""Lightweight entity and relation extraction for GraphRAG."""

from __future__ import annotations

import itertools
import re

EN_ENTITY_RE = re.compile(r"\b[A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*){0,3}\b")
ZH_ENTITY_RE = re.compile(
    r"[\u4e00-\u9fff]{2,12}(?:算法|模型|系统|数据|网络|学习|检索|图谱|"
    r"智能|课程|方法|概念|实体|关系|文档|向量|索引|平台|工具|流程)",
)
RELATION_RE = re.compile(
    r"([\u4e00-\u9fffA-Za-z0-9 ]{2,24})"
    r"(?:是|属于|包括|依赖|影响|连接|用于|生成|构建)"
    r"([\u4e00-\u9fffA-Za-z0-9 ]{2,24})",
)


class EntityExtractor:
    def extract_entities(self, text: str, limit: int = 12) -> list[str]:
        candidates: list[str] = []
        candidates.extend(match.group(0).strip() for match in EN_ENTITY_RE.finditer(text))
        candidates.extend(match.group(0).strip() for match in ZH_ENTITY_RE.finditer(text))
        cleaned: list[str] = []
        for candidate in candidates:
            candidate = re.sub(r"\s+", " ", candidate).strip(" ，。；;:：")
            if 2 <= len(candidate) <= 40 and candidate not in cleaned:
                cleaned.append(candidate)
        return cleaned[:limit]

    def extract_relations(self, text: str) -> list[tuple[str, str, str]]:
        relations: list[tuple[str, str, str]] = []
        for match in RELATION_RE.finditer(text):
            left = _trim_entity(match.group(1))
            right = _trim_entity(match.group(2))
            if left and right and left != right:
                relations.append((left, right, "语义关系"))

        entities = self.extract_entities(text, limit=8)
        for left, right in itertools.combinations(entities[:5], 2):
            relations.append((left, right, "共现"))
        return _unique_relations(relations)


def _trim_entity(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip(" ，。；;:：")
    if len(value) > 20:
        value = value[-20:]
    return value if 2 <= len(value) <= 20 else ""


def _unique_relations(relations: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[tuple[str, str, str]] = []
    for relation in relations:
        if relation not in seen:
            seen.add(relation)
            unique.append(relation)
    return unique

