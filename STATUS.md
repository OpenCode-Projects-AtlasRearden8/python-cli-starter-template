# STATUS.md

## What was built

A copy-ready template repository for Asdale Dynamics, LLC CLI companion tools:
a tested, packaged Python CLI (`todolist` — a worked demo TODO-list command that
new authors adapt) implementing the house CLI pattern:

- argparse entry point (`src/llc_cli_template/cli/main.py`) with `--version`,
  `--config FILE`, `--dry-run`, `--log-level`, and subcommands
  (`add`, `list`, `done`, `remove`)
- config-file loading pattern (`config.py`): JSON defaults + overlay; CLI flags win
- structured logging (`logging_setup.py`): stderr-only, DEBUG adds function/line
- shared exit codes (`exit_codes.py`): 0/1/2/3/4/5 documented in the README
- packaging via `pyproject.toml` with console script `todolist` (src/ layout)
- GitHub Actions workflow `.github/workflows/lint-and-test.yml`
  (Python 3.9–3.13 matrix: install, version, compileall, smoke, pytest, build)
- offline pytest suite (`tests/test_todo_cli.py`): 19 tests
  (storage units, parser surface, end-to-end through `main()`)
- README tutorial explaining every file plus an adaptation guide
- MIT `LICENSE` with the exact line "Copyright (c) 2026 Asdale Dynamics, LLC";
  Asdale Dynamics, LLC credited in the README
- No secrets, API keys, or personal data anywhere.

## How to run it

```bash
pip install -e .[dev]     # from this folder
todolist --version
todolist add "example item"
todolist list
todolist done <id>
todolist --dry-run add "rehearsal"    # exits 5, writes nothing
pytest
```

## Verification results (performed in this session)

- `pytest -v`: **19 passed** in ~0.06s (offline).
- `python -m build`: sdist and wheel built successfully
  (`llc_cli_template-0.1.0.tar.gz`, `.whl`); build artifacts removed afterwards.
- Console script installed in a scratch venv: `todolist --version`
  → `todolist 0.1.0`; smoke run `--dry-run add` exited 5 and wrote nothing;
  real `add` + `list` worked; leftover demo data file cleaned up.
- Compile check of `src/` passes (`python -m compileall src -q`).

## Known gaps

- CI is untested against real GitHub runners (this machine cannot push); the
  workflow mirrors the verified local steps.
- Linting in CI is `compileall` only; add `ruff`/`mypy` when project style settles.
- No Windows/macOS runners in the matrix yet.
