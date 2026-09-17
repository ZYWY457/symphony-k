# Symphony-K

## What Symphony-K is

Symphony-K is an outcome-oriented AI work orchestrator. It governs bounded
Objectives, Tasks, Runs, Outcomes, Evaluations and external Effects across
replaceable agents, models, tools and sandboxes. Workers are untrusted;
authoritative state, independent evidence, Human authority and auditable
history remain outside Worker control.

## Current status

Stage 0 and Stage 1 are complete. The Human Stage 1 Exit Review is accepted.
The Stage 2 M1 design remains a Human Accepted historical technical asset at
`77acfbdaf2bed6f0536873fafc8eb7a12599da83`; runtime isolation evidence is not
yet established and runtime code has not started. Issues #85 and #86 completed
the strategic-validation evidence cycle, but the resulting GO gate supports
considering a formal product/roadmap amendment and is not Human product
approval. Issue #87 is the current Human decision gate, and Issue #79 remains
BLOCKED / NOT RELEASED. The product identity above remains the accepted
historical wording pending an explicit Human decision and reconciliation.

Read [STATUS.md](STATUS.md) for the compact authoritative current summary.

## Project navigation

- [Architecture](ARCHITECTURE.md) — planes, domain boundaries and invariants
- [v1 Product Contract](docs/V1_PRODUCT_CONTRACT.md) — observable product,
  operator and deployment acceptance boundary
- [Full roadmap](ROADMAP.md) — canonical Stage 0–14 map
- [Complete development path](docs/DEVELOPMENT_PATH.md) — entry, evidence and
  exit contracts for every stage through v1.0
- [Reference workflows](docs/REFERENCE_WORKFLOWS.md) — canonical product
  acceptance scenarios and stage traceability
- [AI and maintainer handoff](docs/AI_HANDOFF.md) — resume work without chat or
  account-specific memory
- [Constitution](CONSTITUTION.md) — highest-precedence project rules
- [Documentation map](docs/README.md) — core beliefs, ADRs, designs and plans

Historical Stage 1 detail remains in
[completed Exec Plans](docs/exec-plans/completed/) and Git history rather than
being duplicated here.

## Development commands

Python **3.12 or newer** is required. `.python-version` selects Python 3.12 for
the development baseline. Install
[uv](https://docs.astral.sh/uv/getting-started/installation/), then run from the
repository root:

```text
uv sync --dev --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
```

`uv sync --dev` may be used when intentionally updating dependency resolution;
keep `uv.lock` under version control with dependency changes. Tool configuration
lives in `pyproject.toml`, package source in `src/symphony_k/`, and tests in
`tests/`.
