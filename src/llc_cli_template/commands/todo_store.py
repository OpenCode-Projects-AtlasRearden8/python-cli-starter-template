"""TODO list storage: the worked demo command authors adapt.

Storage is a plain JSON file (local-first, no secrets, no personal
data beyond what the user writes themselves). New LLC CLIs replace this
module with their own domain logic but keep the shape: small functions
that take explicit paths, raise ValueError for bad input, and never
print -- printing belongs in cli.main.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List


class TodoStoreError(Exception):
    """Domain error carrying a stable machine reason code."""


def default_store() -> Dict[str, Any]:
    """A fresh, empty todo list document."""
    return {"items": []}


def load_store(path: Path) -> Dict[str, Any]:
    """Load the todo document; missing file yields an empty list document."""
    if not path.exists():
        return default_store()
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TodoStoreError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("items"), list):
        raise TodoStoreError(f"{path} is not a todo document (expected {{'items': []}})")
    return doc


def save_store(path: Path, doc: Dict[str, Any]) -> None:
    """Persist the document atomically (write temp, then replace)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def find_item(doc: Dict[str, Any], item_id: str) -> Dict[str, Any]:
    for item in doc["items"]:
        if item["id"] == item_id:
            return item
    raise TodoStoreError(f"no item with id {item_id!r}")


def add_item(doc: Dict[str, Any], text: str) -> Dict[str, Any]:
    text = text.strip()
    if not text:
        raise TodoStoreError("item text must not be empty")
    if len(text) > 500:
        raise TodoStoreError("item text must be 500 characters or fewer")
    item = {"id": str(uuid.uuid4())[:8], "text": text, "done": False}
    doc["items"].append(item)
    return item


def complete_item(doc: Dict[str, Any], item_id: str) -> Dict[str, Any]:
    item = find_item(doc, item_id)
    item["done"] = True
    return item


def remove_item(doc: Dict[str, Any], item_id: str) -> Dict[str, Any]:
    item = find_item(doc, item_id)
    doc["items"].remove(item)
    return item


def list_items(doc: Dict[str, Any], show_done: bool = True) -> List[Dict[str, Any]]:
    items = list(doc["items"])
    if not show_done:
        items = [i for i in items if not i["done"]]
    items.sort(key=lambda i: (i["done"], i["text"].lower()))
    return items
