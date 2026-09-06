# symphony-k

An outcome-oriented AI work orchestrator. See [AGENTS.md](AGENTS.md) for the
repository documentation hierarchy and [ARCHITECTURE.md](ARCHITECTURE.md) for
system boundaries. The current implementation includes Stage 1 M1 tooling,
M2 shared value types, and M3A Objective snapshots and structural lifecycle topology.
Authoritative transition execution remains deferred to the Transition Engine.

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

Package source lives in `src/symphony_k/`. The `symphony_k.domain` public API
provides typed IDs, actor identity/category, UTC timestamps, versions, transition
reasons and domain errors. M2 representation choices and scope are documented in
the [M2 plan](docs/exec-plans/completed/stage-01-m2-shared-types-v1.md).
Tests cover imports and value semantics; `tests/typing_examples.py` also checks
nominal ID separation under strict mypy. No runtime dependency is required.

`Objective` is an immutable snapshot with explicitly supplied state and version.
`CompletionPolicyRef` and the designated `ActorIdentity` retain references, not
policy results or permissions. `can_objective_transition` checks only structural
edge membership; `OBJECTIVE_CREATION_STATE` declares DRAFT as the sole creation
target without adding NONE to the enum. No query executes a transition, updates
a version, evaluates guards, or generates events. See the
[M3A plan](docs/exec-plans/completed/stage-01-m3a-objective-v1.md) for the field model
and validation scope.
