# Stage 1 M7C3B3 — Canonical Run Failure Closure Semantic Guards

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #35 / Implementation #7C3B3 only

## Boundary

Add canonical Run-only semantic guards for `PENDING`, `RUNNING`,
`WAITING_FOR_VERIFICATION`, and `RETRYING` to `FAILED`. The transition engine
continues to apply structural legality, M7B1 authority, M7B2 eligibility, the
canonical Run guard, then generic guards before emitting one immutable event.

## Bounded Work

1. Add the minimum immutable, exact-snapshot-bound Run decisions for a
   normalized failure classification, recovery-path closure, and the
   R-authorized FAILED selection. Reuse `RunOwnershipFencingDecision`.
2. Require all four decisions for exactly the four existing `-> FAILED` edges.
   Classification, recovery-path closure, fencing, and FAILED selection remain
   distinct; only SCHEDULER and RUN_CONTROLLER may select FAILED.
3. Preserve the ten existing canonical Run edges and deny ABORTED semantics by
   default. Do not create a successor or mutate any related entity.
4. Add deterministic tests for all successful edges, exact provenance binding,
   authority boundaries, all normalized classes, rejection behavior, and
   historical Run identity preservation.

## Out of Scope

ABORTED semantics; recovery algorithms; retry counters; successor creation;
Task, Objective, Outcome, Evaluation, or Effect mutation; persistence; process
control; credential revocation; and ADR-0006 route-health runtime behavior.

## Acceptance

Each accepted FAILED closure has exact Run/version/correlation provenance,
non-Worker authoritative failure classification, an R-authorized recovery-path
closure and FAILED selection, and non-Worker passed ownership fencing. The
central transition changes only the old Run state and version.
