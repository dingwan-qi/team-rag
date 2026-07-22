"""User authentication and persistent chat memory."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.core.config import settings

USERNAME_RE = re.compile(r"^[A-Za-z0-9_-]{3,32}$")
SESSION_DAYS = 7


@dataclass(frozen=True)
class UserRecord:
    id: str
    username: str
    created_at: str


@dataclass(frozen=True)
class AuthResult:
    token: str
    user: UserRecord


class UserService:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or settings.user_db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def register(self, username: str, password: str) -> AuthResult:
        username = self._normalize_username(username)
        self._validate_password(password)
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        user = UserRecord(
            id=uuid.uuid4().hex,
            username=username,
            created_at=self._now(),
        )
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO users (id, username, password_hash, salt, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user.id, user.username, password_hash, salt, user.created_at),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError("用户名已存在") from exc
        return self._create_session(user)

    def login(self, username: str, password: str) -> AuthResult:
        username = self._normalize_username(username)
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, username, password_hash, salt, created_at
                FROM users
                WHERE username = ?
                """,
                (username,),
            ).fetchone()
        if row is None:
            raise ValueError("用户名或密码错误")
        expected = self._hash_password(password, row["salt"])
        if not hmac.compare_digest(expected, row["password_hash"]):
            raise ValueError("用户名或密码错误")
        return self._create_session(self._row_to_user(row))

    def get_user_by_token(self, token: str) -> UserRecord | None:
        if not token:
            return None
        token_hash = self._hash_token(token)
        now = self._now()
        with self._connect() as conn:
            conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
            row = conn.execute(
                """
                SELECT users.id, users.username, users.created_at
                FROM sessions
                JOIN users ON users.id = sessions.user_id
                WHERE sessions.token_hash = ? AND sessions.expires_at > ?
                """,
                (token_hash, now),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_user(row)

    def logout(self, token: str) -> None:
        if not token:
            return
        with self._connect() as conn:
            conn.execute("DELETE FROM sessions WHERE token_hash = ?", (self._hash_token(token),))

    def add_memory(
        self,
        user_id: str,
        role: str,
        content: str,
        rag_mode: str | None = None,
    ) -> dict[str, Any]:
        if role not in {"user", "assistant"}:
            raise ValueError("记忆角色必须是 user 或 assistant")
        content = content.strip()
        if not content:
            raise ValueError("记忆内容不能为空")
        memory = {
            "id": uuid.uuid4().hex,
            "user_id": user_id,
            "role": role,
            "content": content,
            "rag_mode": rag_mode,
            "created_at": self._now(),
        }
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO chat_memory (id, user_id, role, content, rag_mode, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    memory["id"],
                    memory["user_id"],
                    memory["role"],
                    memory["content"],
                    memory["rag_mode"],
                    memory["created_at"],
                ),
            )
        return memory

    def list_memory(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, role, content, rag_mode, created_at
                FROM chat_memory
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def memory_context(self, user_id: str, limit: int = 8) -> list[str]:
        messages = self.list_memory(user_id, limit=limit)
        context = []
        for message in messages:
            role = "用户" if message["role"] == "user" else "助手"
            content = str(message["content"]).replace("\n", " ").strip()
            if len(content) > 240:
                content = f"{content[:240]}..."
            context.append(f"{role}: {content}")
        return context

    def clear_memory(self, user_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM chat_memory WHERE user_id = ?", (user_id,))

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS chat_memory (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    rag_mode TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_chat_memory_user_created
                    ON chat_memory (user_id, created_at);
                """
            )

    def _create_session(self, user: UserRecord) -> AuthResult:
        token = secrets.token_urlsafe(32)
        created_at = self._now()
        expires_at = (datetime.now(UTC) + timedelta(days=SESSION_DAYS)).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (token_hash, user_id, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (self._hash_token(token), user.id, created_at, expires_at),
            )
        return AuthResult(token=token, user=user)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _normalize_username(self, username: str) -> str:
        username = username.strip()
        if not USERNAME_RE.fullmatch(username):
            raise ValueError("用户名需为 3-32 位字母、数字、下划线或短横线")
        return username

    def _validate_password(self, password: str) -> None:
        if len(password) < 6:
            raise ValueError("密码至少需要 6 位")

    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            200_000,
        ).hex()

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _row_to_user(self, row: sqlite3.Row) -> UserRecord:
        return UserRecord(id=row["id"], username=row["username"], created_at=row["created_at"])

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()
