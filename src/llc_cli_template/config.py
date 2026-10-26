"""Config-file loading pattern.

Every LLC CLI accepts an optional JSON config file so users can persist
settings instead of repeating long command lines. This module is the
standard way to load one: copy it into new projects unchanged.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "data_file": "todo_items.json",
    "log_level": "INFO",
}


class ConfigError(Exception):
    """Raised when a config file cannot be read or parsed."""


def deep_merge(base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    """Merge ``extra`` on top of ``base`` without mutating either input."""
    result = dict(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: str | None) -> Dict[str, Any]:
    """Load defaults, then overlay a user config file if one is given.

    Returns a fresh dict with user values overriding defaults.
    Raises ConfigError for unreadable or invalid JSON files.
    """
    config = dict(DEFAULT_CONFIG)
    if not path:
        return config
    config_path = Path(path)
    try:
        raw = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Cannot read config file {config_path}: {exc}") from exc
    try:
        user_values = json.loads(raw or "{}")
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {config_path}: {exc}") from exc
    if not isinstance(user_values, dict):
        raise ConfigError(f"Config file {config_path} must contain a JSON object")
    return deep_merge(config, user_values)
