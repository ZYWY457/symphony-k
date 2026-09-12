# Stage 1 / Correction 7C6B1 — Exact-Bind Historical Effect Observation and Quarantine Provenance

**Version:** 1
**Status:** Validated local candidate
**Scope:** GitHub Issue #52 only

## Execution evidence

TaskSpec reference: GitHub Issue #52
TaskSpec access mode: materialized-handoff
TaskSpec precondition: PASS

The required Issue #51 candidate base `31afd68fdb3761cc13b7c3c7939a5022139476ad`
is the current `HEAD`. Repository command, Git, Python, and UV preflight checks
passed before this plan and any implementation mutation.

## Objective

Issue #51's overall M7C6B architecture remains accepted. This bounded correction
closes its historical-provenance binding defect: current transition scopes remain
exactly bound to the current Effect snapshot, while caller-supplied historical
observations and quarantine-entry provenance are checked for compatibility with
the immutable Effect rather than incorrectly rebound to the current snapshot.

## In scope

1. Add minimal semantic-layer compatibility checks for historical observations:
   EffectId, target, known payload, operation, deduplication, correlation, and
   non-future version binding.
2. Preserve real immutable quarantine-entry scopes for reconciliation; reject a
   fabricated `QUARANTINED -> QUARANTINED` scope.
3. Support truthful observed-origin reconciliation without fabricating a
   non-creation transition.
4. Add deterministic transition-boundary regressions for the corrected binding
   and retain the accepted M7C6A/M7C6B topology coverage.

## Out of scope

Persistence, retrieval/current-record selection, Effect creation, dispatch,
retry, rollback, compensation execution, new entities or states, and every
deferred remediation/re-entry edge remain out of scope.

## Controls and acceptance

Historical provenance may reference an earlier Effect version but never a future
version or incompatible immutable target/payload/identity. Unknown payload
remains unknown. Observation remains non-executing, `COMMITTED` remains factual
occurrence independent of authorization/governance, and no lifecycle
self-transition is introduced. All nine M7C6B edges, three M7C6A edges, seven
semantic denials, and the nineteen-edge non-creation topology remain canonical.

## Validation evidence

The default UV cache was sandbox-denied, so validation used the repository-approved
ignored `.uv-cache` fallback. All Issue-required gates passed:

- `uv sync --dev --locked` — PASS
- `uv run pytest -p no:cacheprovider` — PASS, 2497 tests
- `uv run ruff check .` — PASS
- `uv run ruff format --check .` — PASS, 153 files already formatted
- `uv run mypy src tests` — PASS, 88 source files
- `git diff --check` — PASS

The staged diff will be explicitly scoped and reviewed before exactly one local
corrective commit. No remote mutation is authorized or performed.
