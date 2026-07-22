from __future__ import annotations

from app.ingestion.splitter import split_text


def test_split_text_with_overlap() -> None:
    text = "0123456789" * 30

    chunks = split_text(text, chunk_size=50, chunk_overlap=10)

    assert len(chunks) > 1
    assert chunks[0][-10:] == chunks[1][:10]


def test_split_empty_text() -> None:
    assert split_text("   ") == []

