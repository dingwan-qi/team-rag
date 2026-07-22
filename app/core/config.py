"""Runtime configuration loaded from environment variables and .env files."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _env_path(name: str, default: str) -> Path:
    value = os.getenv(name, default)
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


@dataclass(frozen=True)
class Settings:
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    embedding_model: str
    chroma_dir: Path
    upload_dir: Path
    graph_dir: Path
    user_db_path: Path
    chunk_size: int = 700
    chunk_overlap: int = 120
    default_top_k: int = 4
    vector_backend: str = "auto"

    def ensure_directories(self) -> None:
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.graph_dir.mkdir(parents=True, exist_ok=True)
        self.user_db_path.parent.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    _load_dotenv(PROJECT_ROOT / ".env")
    settings = Settings(
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_base_url=os.getenv("LLM_BASE_URL", ""),
        llm_model=os.getenv("LLM_MODEL", ""),
        embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5"),
        chroma_dir=_env_path("CHROMA_DIR", "./data/chroma"),
        upload_dir=_env_path("UPLOAD_DIR", "./data/uploads"),
        graph_dir=_env_path("GRAPH_DIR", "./data/graph"),
        user_db_path=_env_path("USER_DB_PATH", "./data/teamrag_users.sqlite3"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "700")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "120")),
        default_top_k=int(os.getenv("DEFAULT_TOP_K", "4")),
        vector_backend=os.getenv("VECTOR_BACKEND", "auto"),
    )
    settings.ensure_directories()
    return settings


settings = get_settings()
