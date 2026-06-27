"""Environment-based configuration for llmstxt-mcp.

Everything is convention-based with sane defaults; values may be overridden via
``LLMSTXT_*`` environment variables or a ``.env`` / ``.env.local`` file.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from llmstxt_mcp.models import LogLevel


class Settings(BaseSettings):
    """Runtime configuration loaded from the environment."""

    model_config = SettingsConfigDict(
        env_prefix="LLMSTXT_",
        env_file=(".env", ".env.local"),
        extra="ignore",
    )

    index_root: Path = Field(default_factory=lambda: Path.home() / ".llms.txt.d")
    max_concurrent_fetches: int = 5
    max_full_text_size: int = 20 * 1024 * 1024  # 20 MB
    http_timeout: float = 30.0
    llms_txt_timeout: float = 15.0
    full_text_timeout: float = 60.0
    rate_limit_per_minute: int = 60
    log_level: LogLevel = "INFO"

    @property
    def index_db(self) -> Path:
        """SQLite database file with WAL mode and FTS5."""
        return self.index_root / "index.db"

    @property
    def cache_dir(self) -> Path:
        """Cached llms-full.txt directory."""
        return self.index_root / "cache"

    def ensure_dirs(self) -> None:
        """Create the index root and cache directories if missing."""
        self.index_root.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
