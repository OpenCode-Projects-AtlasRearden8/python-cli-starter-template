"""Exit codes every LLC CLI should use.

Keep names identical across projects so scripts written against one tool
keep working with the next. Copy into new projects unchanged.
"""

from __future__ import annotations

import sys

EXIT_OK = 0
EXIT_FAILURE = 1  # unexpected internal error
EXIT_USAGE = 2  # argparse already uses this for bad arguments
EXIT_NOT_FOUND = 3  # item/file the user asked for does not exist
EXIT_INVALID_INPUT = 4  # user provided bad or conflicting values
EXIT_DRY_RUN = 5  # --dry-run finishing without writing (informational)


def exit_with(code: int) -> "NoReturn":  # type: ignore[name-defined]
    """Exit the process with a known code (helper for tests and scripts)."""
    sys.exit(code)
