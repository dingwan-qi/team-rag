"""Build the vector index from uploaded and sample documents."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import PROJECT_ROOT, settings  # noqa: E402
from app.services.document_service import DocumentService  # noqa: E402


def main() -> None:
    settings.ensure_directories()
    sample_dir = PROJECT_ROOT / "data" / "samples"
    for path in sample_dir.glob("*"):
        if path.is_file():
            target = settings.upload_dir / path.name
            if not target.exists():
                shutil.copy2(path, target)
    result = DocumentService().index_uploaded_files()
    print(
        f"{result.message}: {result.indexed_documents} documents, "
        f"{result.indexed_chunks} chunks, backend={result.backend}",
    )


if __name__ == "__main__":
    main()
