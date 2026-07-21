"""Knowledge graph rendering helpers."""

from __future__ import annotations

import html

import networkx as nx
import streamlit as st


def render_graph(graph: nx.Graph, max_edges: int = 40) -> None:
    if graph.number_of_nodes() == 0:
        st.info("还没有知识图谱，请先在本页构建。")
        return
    edges = list(graph.edges(data=True))[:max_edges]
    lines = ["graph LR"]
    for source, target, data in edges:
        source_id = _node_id(str(source))
        target_id = _node_id(str(target))
        label = html.escape(str(data.get("label", "相关")))
        lines.append(f'  {source_id}["{_safe_label(source)}"] -- "{label}" --> {target_id}["{_safe_label(target)}"]')
    if len(lines) == 1:
        for node in list(graph.nodes)[:max_edges]:
            lines.append(f'  {_node_id(str(node))}["{_safe_label(node)}"]')
    st.graphviz_chart("\n".join(_to_dot(lines, edges)))


def _to_dot(_: list[str], edges: list[tuple[str, str, dict[str, object]]]) -> list[str]:
    dot = ["graph {"]
    for source, target, data in edges:
        label = str(data.get("label", "相关")).replace('"', "'")
        dot.append(f'  "{source}" -- "{target}" [label="{label}"];')
    dot.append("}")
    return dot


def _node_id(value: str) -> str:
    return "N" + "".join(str(ord(char)) for char in value[:8])


def _safe_label(value: object) -> str:
    label = str(value).replace('"', "'")
    return label[:30]

