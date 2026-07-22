"""Relation extraction adapter used by the graph builder."""

from __future__ import annotations

from app.graph.entity_extractor import EntityExtractor


class RelationExtractor:
    def __init__(self, entity_extractor: EntityExtractor | None = None):
        self.entity_extractor = entity_extractor or EntityExtractor()

    def extract(self, text: str) -> list[tuple[str, str, str]]:
        return self.entity_extractor.extract_relations(text)

