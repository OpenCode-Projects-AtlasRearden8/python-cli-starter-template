"""Argparse entry point with --dry-run, config loading, and version flag.

This module is the template heart: copy it into a new project, rename the
program constant, and swap storage/commands. The pattern:

1. Parser built by build_parser() (testable; no global state).
2. Config file loaded first; CLI flags always override config values.
3. Commands mutate an in-memory document; --dry-run skips saving and
   exits with EXIT_DRY_RUN so scripts can distinguish it.
4. Exit codes come from exit_codes.py; unexpected errors exit 1.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from .. import __version__
from ..commands import todo_store
from ..config import ConfigError, load_config
from ..exit_codes import (
    EXIT_DRY_RUN,
    EXIT_FAILURE,
    EXIT_INVALID_INPUT,
    EXIT_NOT_FOUND,
    EXIT_OK,
)
from ..logging_setup import setup_logging

PROGRAM = "todolist"
DESCRIPTION = "A demo TODO companion CLI from the Asdale Dynamics LLC starter template."

logger = logging.getLogger("llc_cli_template")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROGRAM,
        description=DESCRIPTION,
        epilog="Config file keys: data_file, log_level (see sample-config.json).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROGRAM} {__version__}",
    )
    parser.add_argument(
        "--config",
        metavar="FILE",
        help="JSON config file; CLI flags override its values",
    )
    parser.add_argument(
        "--data-file",
        metavar="FILE",
        help="where the todo list is stored (overrides config)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="log verbosity (overrides config)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would happen; do not write anything (exits 5)",
    )

    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    sub_add = sub.add_parser("add", help="add a todo item")
    sub_add.add_argument("text", help="what to do (max 500 chars)")

    sub_list = sub.add_parser("list", help="list todo items")
    sub_list.add_argument("--todo-only", action="store_true", help="hide completed items")

    sub_done = sub.add_parser("done", help="mark an item complete")
    sub_done.add_argument("id", help="item id shown by 'list'")

    sub_rm = sub.add_parser("remove", help="remove an item")
    sub_rm.add_argument("id", help="item id shown by 'list'")

    return parser


def _resolve_data_file(args: argparse.Namespace) -> Path:
    return Path(args.data_file or args.config_values["data_file"])


def _cmd_add(args: argparse.Namespace) -> int:
    path = _resolve_data_file(args)
    doc = todo_store.load_store(path)
    try:
        item = todo_store.add_item(doc, args.text)
    except todo_store.TodoStoreError as exc:
        logger.error("add rejected: %s", exc)
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_INVALID_INPUT
    print(f"added {item['id']}: {item['text']}")
    if args.dry_run:
        print("[dry-run] not saved", file=sys.stderr)
        return EXIT_DRY_RUN
    todo_store.save_store(path, doc)
    logger.info("added item %s to %s", item["id"], path)
    return EXIT_OK


def _cmd_list(args: argparse.Namespace) -> int:
    path = _resolve_data_file(args)
    doc = todo_store.load_store(path)
    items = todo_store.list_items(doc, show_done=not args.todo_only)
    if not items:
        print("(no items)")
        return EXIT_OK
    for item in items:
        mark = "x" if item["done"] else " "
        print(f"[{mark}] {item['id']}  {item['text']}")
    return EXIT_OK


def _cmd_done(args: argparse.Namespace) -> int:
    path = _resolve_data_file(args)
    doc = todo_store.load_store(path)
    try:
        item = todo_store.complete_item(doc, args.id)
    except todo_store.TodoStoreError as exc:
        logger.error("done failed: %s", exc)
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_NOT_FOUND
    print(f"completed {item['id']}: {item['text']}")
    if args.dry_run:
        print("[dry-run] not saved", file=sys.stderr)
        return EXIT_DRY_RUN
    todo_store.save_store(path, doc)
    logger.info("completed item %s", item["id"])
    return EXIT_OK


def _cmd_remove(args: argparse.Namespace) -> int:
    path = _resolve_data_file(args)
    doc = todo_store.load_store(path)
    try:
        item = todo_store.remove_item(doc, args.id)
    except todo_store.TodoStoreError as exc:
        logger.error("remove failed: %s", exc)
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_NOT_FOUND
    print(f"removed {item['id']}: {item['text']}")
    if args.dry_run:
        print("[dry-run] not saved", file=sys.stderr)
        return EXIT_DRY_RUN
    todo_store.save_store(path, doc)
    logger.info("removed item %s", item["id"])
    return EXIT_OK


COMMANDS = {"add": _cmd_add, "list": _cmd_list, "done": _cmd_done, "remove": _cmd_remove}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.config_values = load_config(args.config)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_FAILURE
    level = args.log_level or args.config_values["log_level"]
    setup_logging(level, None)

    logger.debug("running command=%s argv=%s", args.command, argv)
    try:
        return COMMANDS[args.command](args)
    except todo_store.TodoStoreError as exc:
        # Corrupt/unreadable data file is not the user's argument mistake;
        # it is a runtime failure.
        logger.error("storage error: %s", exc)
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_FAILURE
    except KeyboardInterrupt:
        print(f"{PROGRAM}: interrupted", file=sys.stderr)
        return EXIT_FAILURE
    except Exception:  # noqa: BLE001 - top-level guard: log, never traceback
        logger.exception("unexpected error")
        print(f"{PROGRAM}: unexpected error (see log)", file=sys.stderr)
        return EXIT_FAILURE
