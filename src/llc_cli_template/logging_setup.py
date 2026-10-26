"""Structured logging setup.

Structured logs go to stderr (never stdout) so stdout stays reserved for
command output that scripts can pipe. Copy this module into new projects
unchanged.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
_DEBUG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"

LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


def setup_logging(level: str = "INFO", log_file: str | None = None) -> None:
    """Configure root logging with a structured format.

    level     -- DEBUG/INFO/WARNING/ERROR (unknown names fall back to INFO)
    log_file  -- optional path; when given, records are also written there
    """
    level_name = str(level).upper()
    if level_name == "DEBUG":
        fmt = _DEBUG_FORMAT
    else:
        fmt = _LOG_FORMAT
    level_num = LEVELS.get(level_name, logging.INFO)

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))

    logging.basicConfig(level=level_num, format=fmt, handlers=handlers, force=True)
    logging.getLogger("llc_cli_template").debug("Logging initialised at %s", level_name)
