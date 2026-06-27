"""Structured logging setup.

Logs are emitted as JSON on **stderr**. stdout is reserved for the MCP stdio
protocol — writing logs there would corrupt the transport.
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from llmstxt_mcp.models import LogLevel


def configure_logging(level: LogLevel = "INFO") -> None:
    """Configure structlog through stdlib logging on stderr."""
    logging.basicConfig(format="%(message)s", stream=sys.stderr, level=level)
    structlog.configure(
        cache_logger_on_first_use=True,
        logger_factory=structlog.stdlib.LoggerFactory(),
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
    )
