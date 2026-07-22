"""Load text from supported document formats."""

from __future__ import annotations

from pathlib import Path

from app.core.exceptions import DocumentParseError, EmptyDocumentError, UnsupportedFileTypeError
from app.rag.schemas import DocumentPage

SUPPORTED_SUFFIXES = {".pdf", ".docx", ".txt", ".md", ".markdown"}


def supported_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_SUFFIXES


def load_document(path: Path) -> list[DocumentPage]:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise UnsupportedFileTypeError(f"不支持的文件类型: {suffix}")
    if not path.exists() or path.stat().st_size == 0:
        raise EmptyDocumentError("文件为空或不存在")

    try:
        if suffix == ".pdf":
            pages = _load_pdf(path)
        elif suffix == ".docx":
            pages = _load_docx(path)
        else:
            pages = _load_text(path)
    except Exception as exc:  # noqa: BLE001 - wrapped as domain exception.
        if isinstance(exc, (UnsupportedFileTypeError, EmptyDocumentError)):
            raise
        raise DocumentParseError(f"文档解析失败: {exc}") from exc

    if not any(page.text.strip() for page in pages):
        raise EmptyDocumentError("文档没有可用文本")
    return pages


def _load_text(path: Path) -> list[DocumentPage]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [DocumentPage(text=text, page_number=1, section=_guess_section(text))]


def _load_pdf(path: Path) -> list[DocumentPage]:
    try:
        import fitz  # type: ignore[import-not-found]
    except ImportError as exc:
        raise DocumentParseError("缺少 PyMuPDF，请安装 pymupdf 后解析 PDF") from exc

    pages: list[DocumentPage] = []
    with fitz.open(path) as doc:
        for index, page in enumerate(doc, start=1):
            text = page.get_text("text")
            pages.append(
                DocumentPage(text=text, page_number=index, section=_guess_section(text)),
            )
    return pages


def _load_docx(path: Path) -> list[DocumentPage]:
    try:
        from docx import Document  # type: ignore[import-not-found]
    except ImportError as exc:
        raise DocumentParseError("缺少 python-docx，请安装后解析 DOCX") from exc

    doc = Document(path)
    paragraphs = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
    text = "\n".join(paragraphs)
    return [DocumentPage(text=text, page_number=1, section=_guess_section(text))]


def _guess_section(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.strip("# ").strip()
        if 0 < len(line) <= 40:
            return line
    return ""

