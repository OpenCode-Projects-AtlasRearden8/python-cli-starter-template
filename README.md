# llc-cli-template

**A copy-ready starter for every Asdale Dynamics, LLC CLI companion tool.**
Plain English, step by step, never condescending — that is how *The Massive AI Manual*
by Dylan Asdale explains AI, and it is how this template works too.

This repository gives you a working command-line tool (`todolist`, a small TODO list)
written in the exact pattern every future LLC CLI should follow. Copy the whole folder
into a new repo, rename things, and you have a tested, packaged, GitHub-Actions-ready
CLI on day one. Everything runs offline — no network calls, no secrets, no API keys.

Credit: **Asdale Dynamics, LLC** — https://dylanasdale.github.io
Licensed MIT (see `LICENSE`).

---

## What is inside

```
.
├── pyproject.toml                  # packaging: metadata, console script, test config
├── LICENSE                         # MIT, Copyright (c) 2026 Asdale Dynamics, LLC
├── README.md                       # this tutorial
├── sample-config.json              # example JSON config file for the CLI
├── .github/workflows/lint-and-test.yml  # CI: install, smoke, test, build
├── src/llc_cli_template/
│   ├── __init__.py                 # package version (single source of truth)
│   ├── cli/main.py                 # ★ argparse entry point (--dry-run, --version, --config)
│   ├── commands/todo_store.py      # ★ the worked demo command (TODO list logic)
│   ├── config.py                   # config-file loading pattern (defaults + merge)
│   ├── logging_setup.py            # structured logging (stderr and optional file)
│   ├── exit_codes.py               # shared exit-code constants
│   └── (packages: cli/, commands/)
├── tests/test_todo_cli.py          # offline pytest suite (unit + end-to-end)
└── STATUS.md                       # what was built and how it was verified
```

★ = the two files you replace first in a new project (parser and domain logic).

---

## File-by-file tutorial

### `pyproject.toml` — the packaging manuscript

This one file replaces the old `setup.py`. It tells pip:

- **who you are**: name, version, description, author (`Asdale Dynamics, LLC`),
  and the MIT licence badge;
- **what to ship**: `setuptools` finds packages under `src/` automatically;
- **what command to install**: under `[project.scripts]`, `todolist = ...main:main`
  means "put a `todolist` command on the user's PATH that calls `main()`";
- **how to test**: `pytest` is configured to look in `tests/`.

To adapt it: change `name`, the `todolist` script name, and the description. Keep
`src/` layout — it prevents a whole class of "imports work locally but not after
installing" bugs.

### `src/llc_cli_template/cli/main.py` — the argparse entry point

The most important template file. Copy this shape every time:

1. `build_parser()` constructs the parser. Keeping it in its own function makes the
   CLI testable — tests can call `build_parser().parse_args(...)` without running
   your program.
2. Global flags every LLC CLI should offer:
   - `--version` prints name and version and exits;
   - `--config FILE` loads a JSON config file (see `config.py` below);
   - `--dry-run` performs the command in memory only and exits with code `5`
     so scripts can tell a rehearsal from a real run;
   - `--log-level` chooses log verbosity;
   - `--data-file` (adapt for your domain: it is the "where does data live" flag).
3. Subcommands (`add`, `list`, `done`, `remove`) live via `add_subparsers`. Each one
   maps to a small `_cmd_*` function in `COMMANDS` — dictionaries of functions keep
   this file short.
4. `main()` orchestrates: parse → load config → set up logging → run command →
   return an exit code from `exit_codes.py`. It never lets a raw traceback escape;
   unexpected errors are logged and exit **1**.

Exit codes mean the same thing in every LLC tool (from `exit_codes.py`):

| Code | Meaning |
|------|---------|
| 0    | success |
| 1    | unexpected / storage failure |
| 2    | bad usage (argparse's own value) |
| 3    | requested item not found |
| 4    | invalid input values |
| 5    | `--dry-run` finished; nothing was written |

Write scripts against these codes once and they work for every LLC CLI.

### `src/llc_cli_template/commands/todo_store.py` — the demo domain

A TODO list stored as a plain local JSON file. Notice the style rules it shows off:

- storage functions take explicit paths and documents, raise `TodoStoreError`
  for domain problems, and **never print** — printing belongs in `main.py`;
- saving is atomic (write to a `.tmp` file, then `replace`) so a crash
  cannot corrupt the user's data;
- missing file == empty list, so a first run feels friendly.

To adapt: rename this module and its functions to your domain, update
`cli/main.py`'s subcommands, and re-point the tests.

### `src/llc_cli_template/config.py` — the config pattern

Users should not retype long options. This module holds `DEFAULT_CONFIG`
(plain defaults), then overlays any JSON file passed to `--config`.
CLI flags win over config values — always that direction, never the reverse.
Malformed config raises `ConfigError`, which `main()` reports as exit **1**.

See `sample-config.json` for the example file a user would copy and edit.

### `src/llc_cli_template/logging_setup.py` — structured logging

Logs go to **stderr** in a predictable `time LEVEL name message` format
(`--log-level DEBUG` adds function and line numbers). Keeping logs on stderr
means stdout is always clean for piping. Pass a `log_file` path if you want
persistent logs; the pattern here is copy-paste across all LLC tools.

### `.github/workflows/lint-and-test.yml` — CI

Every push runs: install the package, print the version, syntax-compile `src/`,
run a real smoke test of the CLI (`--dry-run` then a real write), run `pytest`,
and build an sdist + wheel. Matrix: Python 3.9–3.13. No network is required at
test time beyond installing dependencies.

### `tests/test_todo_cli.py` — the offline pyramid

Three layers, all offline (temporary directories via `tmp_path`):

1. **unit** — storage functions in isolation (`add_item`, `complete_item`, ...);
2. **parser** — the `--version` output, required subcommand, `--dry-run` default;
3. **end-to-end** — call `main([...])` exactly like a user would, then assert on
   returned exit codes and on-disk files, including `--dry-run` writing nothing,
   config overrides, and corrupt-file handling.

---

## Getting started (copy to a new repo in 5 minutes)

Requires Python 3.9+. Run from this folder:

```bash
# 1. Install (editable is best while developing)
pip install -e .[dev]

# 2. Try the demo command
todolist --version
todolist add "read The Massive AI Manual, chapter 2"
todolist list
todolist done <the-id-it-showed>      # note: done/exit codes per table above
todolist list --todo-only

# 3. Rehearse before writing (exit code 5, nothing saved)
todolist --dry-run add "draft the newsletter"

# 4. Use a config file
cp sample-config.json todolist.json   # edit data_file/log_level as you like
todolist --config todolist.json add "file the quarterly paperwork"

# 5. Run the offline test suite
pytest
```

### Adapting to a new LLC CLI

1. Copy the repository (minus `STATUS.md` and this sentence's reminder to update it).
2. In `pyproject.toml`: rename the package, the console script, and descriptions.
3. Rename `src/llc_cli_template/` to your new package name and update imports
   (a project-wide search of `llc_cli_template` finds them all).
4. Replace `commands/todo_store.py` with your domain logic.
5. Update `cli/main.py`: `PROGRAM`, `DESCRIPTION`, config keys, subcommands.
6. In `tests/`: search-replace the package name, then extend the three test layers.
7. Announce once in the README what the tool does, then write the tests before the
   rest of the code if you can — offline first.

---

## Verify it yourself

```bash
pytest -v          # tests pass offline
todolist --version # prints todolist 0.1.0
todolist --help    # full usage, exit codes implied
```

## Known gaps

- No type-checking job yet in CI (add `mypy` when your annotations settle).
- The "known gaps" wording is yours to update per project; keep this section honest.
- Linting is syntax-compile only; add `ruff` to the workflow when your style settles.
- No Windows/macOS runners in the matrix yet; the code is OS-independent, but CI
  only exercises Linux.

This template is maintained by **Asdale Dynamics, LLC** for beginner-friendly,
local-first AI tooling.
