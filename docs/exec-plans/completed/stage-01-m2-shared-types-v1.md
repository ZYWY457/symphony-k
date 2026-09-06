# Stage 1 M2 — Shared Types Implementation Plan

**Version:** 1
**Status:** Implementation and required validation completed, 2026-09-06
**Scope:** [Implementation #2 / GitHub Issue #3](https://github.com/ZYWY457/symphony-k/issues/3), under the accepted [Stage 1 Exec Plan](../active/stage-01-domain-kernel.md), ADR-0005 and state-machine design.

## Boundary Review

No conflict with the accepted hierarchy was found. This is an implementation of existing M2 concepts, not an architecture change; the Issue explicitly permits these representation choices without a new ADR. No runtime dependencies are needed. The accepted state machines and authority rules remain unchanged.

In scope: seven ID types, actor classification/identity, UTC timestamps, non-negative versions, textual reasons, typed errors, public imports and deterministic tests.

Out of scope: the six entity classes, lifecycle enums, transitions, events, authorization, persistence, concurrency execution and all M3+ functionality.

## Bounded Steps and Acceptance

1. Implement immutable shared primitives and explicit public exports. Accept when constructors reject invalid input and different ID kinds remain distinct at runtime and under mypy.
2. Add deterministic value-object/error tests and static type examples. Accept when UUID round trips, immutability/hashability, all ten actor categories, UTC normalization, version/reason rejection and typed errors are covered without lifecycle behavior.
3. Run every Issue command and inspect scope/dependency changes. Accept when locked synchronization, pytest, Ruff lint/format and strict mypy all pass; no dependency or higher-level specification change is introduced.

## Representation Decisions

- IDs: distinct frozen, slotted dataclasses wrapping `uuid.UUID`, with a private implementation base sharing validation and `new()` / `from_string()` / `str()` behavior. Equality is type-sensitive. Direct constructors take UUID objects; parsing strings is explicit. All valid UUID versions, including nil UUID, are accepted because the baseline imposes no UUID-version restriction. `new()` explicitly generates UUID4; there are no hidden generated defaults.
- Actors: ordinary `Enum` with the ten exact accepted string values (not a string subclass), plus a frozen `ActorIdentity(ActorId, ActorType)`. Classification does not grant authority, including SYSTEM.
- Time: frozen `Timestamp(datetime)` rejects naive datetimes, normalizes aware values to `datetime.UTC`, and renders ISO 8601 with fixed microsecond precision. No implicit clock/default. Callers can round-trip using `datetime.fromisoformat(str(timestamp))`.
- Versions: frozen `EntityVersion(int)`, excluding booleans/non-integers and negatives. `next()` returns a new incremented value; no initial entity version or locking strategy is assigned.
- Reasons: frozen `TransitionReason(str)` checks for non-whitespace text but preserves the exact supplied text. No taxonomy or permission semantics.
- Errors: `DomainError` and the eight specified subclasses. `InvalidDomainValue(DomainError, ValueError)` is the single additional constructor-validation exception, so callers can distinguish malformed value objects from lifecycle rejection without inventing a domain entity or error taxonomy. Field-specific messages identify the failed input.
- Static safety: mypy checks positive examples and targeted negative examples with `type: ignore[arg-type]`. With existing strict `warn_unused_ignores`, weakening nominal ID types makes those examples fail validation. Runtime invalid-input tests deliberately bypass annotations to exercise constructor guards.
- Public typing: the standard `py.typed` marker exposes inline type information to installed-package consumers; it adds neither behavior nor a dependency. A separate consumer probe confirms nominal ID checking outside this repository's test module list.

## Required Validation

```text
uv sync --dev --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
```

## Validation Evidence

Python 3.12.7; existing locked pytest 9.1.1, Ruff 0.16.6 and mypy 1.20.2. No dependency or tooling configuration changes.

| Command | Final result |
| --- | --- |
| `uv sync --dev --locked` | Exit 0; resolved/checked 13 packages |
| `uv run pytest` | Exit 0; 128 passed |
| `uv run ruff check .` | Exit 0; all checks passed |
| `uv run ruff format --check .` | Exit 0; 41 files already formatted |
| `uv run mypy src tests` | Exit 0; no issues in 16 source files |
| `uv run ruff format src tests` | Exit 0; initial formatting applied to five new files |
| `uv run mypy --strict --no-incremental C:\Users\Administrator\AppData\Local\Temp\symphony_m2_consumer.py` | Expected exit 1; exactly one arg-type rejection for TaskId passed to an ObjectiveId parameter through the installed public API |
| `git diff --check` | Exit 0 |

The temporary negative consumer probe is outside the repository. The persistent static examples in `tests/typing_examples.py` enforce the same rejection under the normal required mypy command. First-pass Ruff and mypy found test-only style/annotation issues; these were corrected without weakening configuration, and affected checks were rerun successfully. Git reports the existing Windows LF-to-CRLF conversion notices. Validation used the existing permitted uv cache access.

The package imports only standard-library and local domain modules. Source review confirms no lifecycle entities/enums, transition rules, domain events, authorization or persistence. `pyproject.toml`, `uv.lock`, Constitution, accepted ADRs, state-machine design, core beliefs and the Stage 1 Exec Plan remain unchanged. No unresolved architecture question or M3+ implementation was introduced. Completing this bounded plan does not declare Stage 1 complete or grant human acceptance of its final result.
