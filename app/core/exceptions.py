"""Domain exceptions used across the application."""


class TeamRAGError(Exception):
    """Base exception for expected TeamRAG failures."""


class UnsupportedFileTypeError(TeamRAGError):
    """Raised when an uploaded file type is unsupported."""


class EmptyDocumentError(TeamRAGError):
    """Raised when a document has no usable text."""


class DocumentParseError(TeamRAGError):
    """Raised when a document cannot be parsed."""


class DuplicateDocumentError(TeamRAGError):
    """Raised when the same document content was already indexed."""


class LLMError(TeamRAGError):
    """Raised when an LLM provider call fails."""

