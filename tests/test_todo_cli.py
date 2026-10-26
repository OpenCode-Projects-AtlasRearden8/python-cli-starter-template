# python -m invocation style tests are fine offline; we use plain pytest.
import json

import pytest

from llc_cli_template.cli.main import build_parser, main
from llc_cli_template.commands.todo_store import (
    TodoStoreError,
    add_item,
    complete_item,
    default_store,
    find_item,
    list_items,
    load_store,
    remove_item,
    save_store,
)


# ---------- unit tests: storage layer ----------


def test_default_store_is_empty():
    assert default_store() == {"items": []}


def test_add_item_trims_and_rejects_empty(tmp_path):
    doc = default_store()
    item = add_item(doc, "  clear the porch  ")
    assert item["text"] == "clear the porch"
    assert item["done"] is False
    with pytest.raises(TodoStoreError):
        add_item(doc, "   ")


def test_add_item_rejects_over_500_chars():
    with pytest.raises(TodoStoreError):
        add_item(default_store(), "x" * 501)


def test_complete_and_find_item_roundtrip():
    doc = default_store()
    item = add_item(doc, "pay sales tax")
    done = complete_item(doc, item["id"])
    assert done["done"] is True
    assert find_item(doc, item["id"])["done"] is True
    with pytest.raises(TodoStoreError):
        find_item(doc, "nope")


def test_remove_item_removes_exactly_one():
    doc = default_store()
    a = add_item(doc, "alpha")
    b = add_item(doc, "beta")
    item = remove_item(doc, a["id"])
    assert item["text"] == "alpha"
    assert [i["id"] for i in doc["items"]] == [b["id"]]


def test_list_items_hides_done_when_asked():
    doc = default_store()
    a = add_item(doc, "alpha")
    add_item(doc, "beta")
    complete_item(doc, add_item(doc, "gamma")["id"])
    assert [i["text"] for i in list_items(doc, show_done=False)] == ["alpha", "beta"]
    assert len(list_items(doc, show_done=True)) == 3


def test_load_missing_file_returns_empty(tmp_path):
    assert load_store(tmp_path / "missing.json") == {"items": []}


def test_roundtrip_save_load(tmp_path):
    path = tmp_path / "sub" / "todos.json"
    doc = default_store()
    add_item(doc, "hello")
    save_store(path, doc)
    loaded = load_store(path)
    assert [i["text"] for i in loaded["items"]] == ["hello"]
    assert json.loads(path.read_text(encoding="utf-8"))["items"][0]["text"] == "hello"


# ---------- unit tests: argparse surface ----------


def test_parser_requires_subcommand(capsys):
    parser = build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args([])
    assert exc.value.code == 2


def test_version_flag_prints_and_exits_zeroish(capsys):
    from llc_cli_template import __version__

    parser = build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--version"])
    out = capsys.readouterr().out
    assert "todolist" in out and __version__ in out
    assert exc.value.code == 0


def test_dry_run_flag_defaults_false():
    args = build_parser().parse_args(["list"])
    assert args.dry_run is False


# ---------- end-to-end CLI tests through main() ----------


def test_main_add_then_list(tmp_path):
    data = str(tmp_path / "todos.json")
    code = main(["--data-file", data, "add", "buy bookshelf varnish"])
    assert code == 0
    code = main(["--data-file", data, "list"])
    assert code == 0


def test_main_add_dry_run_does_not_write(tmp_path):
    data = str(tmp_path / "todos.json")
    code = main(["--data-file", data, "--dry-run", "add", "email editor"])
    assert code == 5
    assert not (tmp_path / "todos.json").exists()
    doc = load_store(tmp_path / "todos.json")
    assert doc["items"] == []


def test_main_done_and_remove(tmp_path):
    data = str(tmp_path / "todos.json")
    main(["--data-file", data, "add", "print W-9"])
    main(["--data-file", data, "add", "draft chapter 2"])
    doc = load_store(tmp_path / "todos.json")
    first_id = doc["items"][0]["id"]
    second_id = doc["items"][1]["id"]
    assert main(["--data-file", data, "done", first_id]) == 0
    with pytest.raises(SystemExit) as exc:
        main(["--data-file", data, "todo", second_id])  # unknown command
    assert exc.value.code == 2
    assert main(["--data-file", data, "remove", second_id]) == 0
    after_doc = load_store(tmp_path / "todos.json")
    assert len(after_doc["items"]) == 1
    assert after_doc["items"][0]["done"] is True


def test_main_done_unknown_id_exits_not_found(tmp_path):
    data = str(tmp_path / "todos.json")
    assert main(["--data-file", data, "done", "zzzzzzzz"]) == 3


def test_main_bad_json_data_file_fails_gracefully(tmp_path):
    bad = tmp_path / "todos.json"
    bad.write_text("not json {", encoding="utf-8")
    code = main(["--data-file", str(bad), "list"])
    assert code == 1


def test_main_config_file_loads_and_cli_overrides(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"data_file": "wrong.json", "log_level": "INFO"}), encoding="utf-8")
    data = tmp_path / "right.json"
    code = main(["--config", str(config), "--data-file", str(data), "add", "use config"])
    assert code == 0
    assert data.exists()
    assert not (tmp_path / "wrong.json").exists()


def test_main_invalid_config_file_exits_failure(tmp_path):
    config = tmp_path / "config.json"
    config.write_text("{ broken", encoding="utf-8")
    assert main(["--config", str(config), "list"]) == 1


def test_main_empty_text_rejected_exits_invalid(tmp_path):
    data = str(tmp_path / "todos.json")
    assert main(["--data-file", data, "add", "   "]) == 4
    assert not (tmp_path / "todos.json").exists()
