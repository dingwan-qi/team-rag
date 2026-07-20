from __future__ import annotations

from pathlib import Path

import pytest

from app.core.exceptions import EmptyDocumentError, UnsupportedFileTypeError
from app.ingestion.loaders import load_document


def test_load_txt_document(tmp_path: Path) -> None:
    path = tmp_path / "course.txt"
    path.write_text("RAG 课程资料", encoding="utf-8")

    pages = load_document(path)

    assert pages[0].text == "RAG 课程资料"
    assert pages[0].page_number == 1


def test_load_empty_document(tmp_path: Path) -> None:
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")

    with pytest.raises(EmptyDocumentError):
        load_document(path)


def test_unsupported_file_type(tmp_path: Path) -> None:
    path = tmp_path / "course.xlsx"
    path.write_text("x", encoding="utf-8")

    with pytest.raises(UnsupportedFileTypeError):
        load_document(path)

