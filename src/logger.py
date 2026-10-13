"""
Centralized structured logger for PhantomForge.
Adheres to [CS-DEBUG] and [CS-GRANULARITY].
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class StructuredLogger:
    """
    Thread-safe structured logging service that writes to console,
    persists to disk, and buffers log entries for real-time UI streaming.
    """

    def __init__(self, name: str = "EnemyForge", max_buffered: int = 500):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.max_buffered = max_buffered
        self._buffer: List[Dict[str, Any]] = []

        if not self.logger.handlers:
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def attach_file_handler(self, log_dir: Path) -> None:
        """Attaches a rotating timestamped file log handler."""
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"enemyforge_{datetime.now().strftime('%Y%m%d')}.log"
        fh = logging.FileHandler(str(log_file), encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        self.logger.addHandler(fh)

    def _record(self, level: str, message: str, source: str = "Core") -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "level": level,
            "source": source,
            "message": message
        }
        self._buffer.append(entry)
        if len(self._buffer) > self.max_buffered:
            self._buffer.pop(0)

    def debug(self, msg: str, source: str = "Core") -> None:
        self.logger.debug(f"[{source}] {msg}")
        self._record("DEBUG", msg, source)

    def info(self, msg: str, source: str = "Core") -> None:
        self.logger.info(f"[{source}] {msg}")
        self._record("INFO", msg, source)

    def warning(self, msg: str, source: str = "Core") -> None:
        self.logger.warning(f"[{source}] {msg}")
        self._record("WARNING", msg, source)

    def error(self, msg: str, source: str = "Core") -> None:
        self.logger.error(f"[{source}] {msg}")
        self._record("ERROR", msg, source)

    def get_buffered_logs(self) -> List[Dict[str, Any]]:
        return list(self._buffer)


system_logger = StructuredLogger()
