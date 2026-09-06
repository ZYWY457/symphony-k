# symphony-k

An outcome-oriented AI work orchestrator. See [AGENTS.md](AGENTS.md) for the
repository documentation hierarchy and [ARCHITECTURE.md](ARCHITECTURE.md) for
system boundaries. The current implementation is the Stage 1 M1 package and
tooling bootstrap; domain behavior is not implemented yet.

## Development

Python **3.12 or newer** is required. `.python-version` selects Python 3.12 for
the development baseline. Install [uv](https://docs.astral.sh/uv/getting-started/installation/),
then run these commands from the repository root:

```text
uv sync --dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
```

`uv sync --dev` creates an isolated `.venv`, installs the project in editable
mode, and synchronizes the development tools using `uv.lock`. Python 3.12 can
be installed with `uv python install 3.12` if it is not already available.
After pulling dependency changes, run the sync command again. Use
`uv sync --dev --locked` when synchronization must reject a stale lock file.
Keep `uv.lock` under version control with dependency changes.

Use `uv run ruff format .` to apply formatting. Tool configuration lives in
`pyproject.toml`; development dependencies use the standard `dependency-groups`
table. The package has no runtime dependencies and uses the standard Hatchling
build backend. uv is a development tool, not a runtime dependency.

Package source lives in `src/symphony_k/`; `domain/` is the future Domain Kernel
boundary. Tests currently verify only that both packages import successfully.
