# Stage 1 M7C6A — Canonical Effect Preparation and Commit-Eligibility Semantic Guards

**Version:** 1
**Status:** Validated local candidate
**Scope:** GitHub Issue #49 only

## Execution evidence

TaskSpec reference: GitHub Issue #49
TaskSpec access mode: materialized-handoff
TaskSpec precondition: PASS

The required accepted execution base `48243ff22362fd419d3de5de6fed629549eac0ea`
is the current `HEAD`. Repository command, Git, Python, and UV preflight checks
passed before this plan and any implementation mutation.

## Boundary

Implement canonical semantic guards for exactly these existing Effect
non-creation edges:

- `PLANNED -> SIMULATED`
- `PLANNED -> PENDING_COMMIT`
- `SIMULATED -> PENDING_COMMIT`

The work is pure domain semantics. It adds immutable typed supporting provenance
and guard validation only. It does not change Effect topology, add a core entity,
load or persist records, invoke validators, grant external execution authority,
or dispatch, retry, roll back, compensate, or otherwise cause an external
mutation. `SIMULATED` is not occurrence and `PENDING_COMMIT` is not dispatch
permission.

All other sixteen Effect non-creation edges remain denied by default at the
canonical semantic layer.

## Bounded steps

1. Add the minimal typed, immutable Effect operation-scope, simulation,
   pre-commit remediation-readiness, and simulation-bypass provenance needed to
   exact-bind an Effect snapshot, target, payload, and correlation.
2. Add `EffectSemanticGuard` and typed inputs for precisely the three scoped
   edges. Reuse the accepted M6 preparation/verification compatibility helpers;
   require exact independent verification, remediation readiness, and an
   explicit deduplication strategy before `PENDING_COMMIT`.
3. Compose the canonical guard into the transition engine after M7B1/M7B2
   authority checks and before generic guards. Keep successful Effect projection
   changes limited to state and version with the existing lifecycle events.
4. Export only the stable domain surface and add deterministic transition-level,
   topology, authority, identity-separation, and non-execution regression tests.
5. Run the Issue #49 validation gates, review the complete staged diff, stage
   only Issue #49 files, and create one local commit without remote mutation.

## Acceptance

The three scoped edges require exact semantic provenance and the existing M7B1
authority decision plus M7B2 `EFFECT_CONTROLLER` eligibility. Supporting
provenance cannot substitute for lifecycle authority. Simulation creates neither
an occurrence record nor commit/execution semantics. Pending commit carries no
dispatch authority or execution authorization. The topology remains nineteen
Effect non-creation edges, and every unscoped Effect edge remains canonical
semantic deny-by-default.

## Validation evidence

Using the repository-approved ignored `.uv-cache` fallback because the default
UV cache was sandbox-denied:

- `uv sync --dev --locked` — PASS
- `uv run pytest -p no:cacheprovider` — PASS, 2471 tests
- `uv run ruff check .` — PASS
- `uv run ruff format --check .` — PASS
- `uv run mypy src tests` — PASS
- `git diff --check` — PASS
