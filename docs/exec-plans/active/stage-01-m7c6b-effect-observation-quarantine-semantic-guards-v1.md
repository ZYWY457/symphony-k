# Stage 1 M7C6B — Canonical Effect Observation and Quarantine Semantic Guards

**Version:** 1
**Status:** Validated local candidate
**Scope:** GitHub Issue #51 only

## Execution evidence

TaskSpec reference: GitHub Issue #51
TaskSpec access mode: materialized-handoff
TaskSpec precondition: PASS

The required accepted Issue #50 base `c888d779521696c52c2690b70e5ff29d0949644c`
is the current `HEAD`. Repository command, Git, Python, and UV preflight checks
passed before this plan and any implementation mutation.

## Objective and architecture constraints

Canonicalize exactly nine existing non-creation Effect edges: four observation
edges into `COMMITTED` and five controlled-reconciliation edges into
`QUARANTINED`. `COMMITTED` remains independently confirmed occurrence, not
authorization, governance compliance, safety, or acceptance. `QUARANTINED`
remains exclusion from automatic execution, not an occurrence verdict.

The implementation is pure Stage 1 domain semantics. It must retain immutable
Effect origin, target and payload; use exact M7B1 authority decisions and M7B2
`EFFECT_CONTROLLER` eligibility; preserve separate immutable observation,
authorization, governance, incident, attribution and remediation provenance;
and emit only existing lifecycle projections/events. It must not load history,
persist, deduplicate repository-wide, dispatch, retry, roll back, compensate,
authorize an action, or call an external system.

## In scope

1. Add a minimal immutable observation scope that exact-binds an Effect snapshot,
   source/destination, target, correlation, external-operation and
   deduplication identities.
2. Add evidence-backed, bounded quarantine context for uncertain occurrence,
   post-commit problems, and compensation/remediation uncertainty.
3. Extend `EffectSemanticGuard` to validate the nine scoped edges, independent
   confirmed/uncertain observation provenance, authorization/governance binding,
   reconciliation lineage, and producing-principal separation.
4. Extend transition-engine canonical coverage from the existing three M7C6A
   edges to exactly twelve Effect non-creation edges, leaving seven semantic
   deny-by-default.
5. Add deterministic transition-level regression coverage, export the stable
   domain surface, run every Issue #51 validation gate, review the complete
   staged diff, and make exactly one local commit.

## Out of scope

- Effect creation and `NONE` transitions;
- persistence, current-record selection, durable uniqueness, transactionality,
  or repository-wide deduplication;
- dispatch, retry, execution, rollback, compensation, remediation, or policy
  evaluation;
- the seven remaining remediation/re-entry edges;
- new states, new core entities, a policy DSL, or a generic unit of work.

## Risks and controls

- Observation could be mistaken for execution: semantic input has no executor
  or execution-authorization path; tests assert only state/version projection.
- Facts could be conflated with judgment: confirmation requires separate
  immutable observation, authorization finding, and optional governance finding
  without constraining confirmed occurrence to favorable statuses.
- Reconciliation could authorize replay: quarantine contexts bind the exact
  operation/deduplication identity and no retry/dispatch interface is added.
- Caller-supplied history could be ambiguous: supplied lineage is checked using
  existing explicit compatibility helpers; no latest-wins resolver is added.

## Acceptance evidence

- All nine Issue #51 edges have exact-bound canonical semantics; combined M7C6
  coverage is twelve of nineteen non-creation edges.
- The remaining seven edges are semantic deny-by-default while structural
  topology remains nineteen edges.
- Confirmed observation is independently anchored and does not infer favorable
  authorization/governance or mutate historical Effect content.
- Pre-commit quarantine requires uncertain occurrence; post-commit and
  compensation quarantine retain known occurrence/remediation context; and
  reconciliation records reality without executing again.
- Required validation gates pass and the local commit is scoped to this Issue.

## Validation evidence

Using the repository-approved ignored `.uv-cache` fallback because the default
UV cache was sandbox-denied:

- `uv sync --dev --locked` — PASS
- `uv run pytest -p no:cacheprovider` — PASS, 2490 tests
- `uv run ruff check .` — PASS
- `uv run ruff format --check .` — PASS, 152 files already formatted
- `uv run mypy src tests` — PASS, 88 source files
- `git diff --check` — PASS
