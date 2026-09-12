# Stage 1 M7C5B — Canonical Evaluation Conflict and Arbitration Semantic Guards

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #46 only

## Boundary

Complete the four existing Evaluation lifecycle edges: `RUNNING -> CONFLICTED`,
`COMPLETED -> CONFLICTED`, `COMPLETED -> ARBITRATED`, and
`CONFLICTED -> ARBITRATED`. This work exact-binds immutable conflict-set and
arbitration history supplied by the caller, and returns only an in-memory
Evaluation-specific multi-member projection. It neither loads records nor
selects current records, persists projections/events, or provides transaction
atomicity; those concerns remain M8.

## Bounded steps

1. Add narrow immutable semantic inputs for complete conflict participant
   observations/projections and arbitration history slices.
2. Extend the canonical Evaluation guard to validate exact snapshot,
   authority-principal, full-member scope/materiality, extension, and
   arbitration provenance for exactly the four target edges.
3. Reuse M5 conflict/arbitration/effective-use logic to enforce exact
   conflict-set versions, lineage terminality, and multi-conflict blocking.
4. Add deterministic transition tests for successful and rejected conflict and
   arbitration cases, retaining prior six-edge and cross-entity regression
   coverage.
5. Run every Issue #46 validation gate, stage only Issue #46 files, inspect the
   staged diff, and create exactly one validated local commit without remote
   mutation.

## Acceptance evidence

- Conflict registration has exact full participant observations and identifies
  all, and only, RUNNING/COMPLETED participants that need a CONFLICTED
  projection; already-CONFLICTED members create no self-transition.
- Arbitration has exactly one current subject decision and only succeeds when
  the supplied complete history gives its intended arbitration the one terminal
  effective judgment with no unresolved applicable conflict or invalidation.
- Evaluation retains its original result, target, method, and verifier; a
  successful local lifecycle transition changes only state/version and emits
  the existing event contract.
- No repository lookup, persistence, generic transaction facility, or M8
  freshness claim is added.
