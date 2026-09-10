# Stage 1 M7C3B2 — Canonical Run Reassignment Semantic Guards

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #33 / Implementation #7C3B2 only

## Objective

Extend the existing `RunSemanticGuard` with the four accepted reassignment
edges: `PENDING`, `RUNNING`, `WAITING_FOR_VERIFICATION`, and `RETRYING` to
`REASSIGNED`.  The old immutable Run closes only after exact-snapshot-bound,
evidence-backed recovery decisions establish R-authorized reassignment,
ownership fencing, current-route unsuitability, exactly one durable transfer
target, and transfer exclusivity.

## Bounded Work

1. Add immutable Run-scoped decisions and durable references/observations for
   reassignment, fencing, route unsuitability, successor Runs, accepted human
   handoffs, and exclusivity.  Every consumed decision binds the exact old Run
   ID, observed version, and correlation; a successor observation retains its
   own version.
2. Add one reassignment semantic bundle and map it to exactly the four existing
   reassignment edges in the current canonical guard.  Require SCHEDULER or
   RUN_CONTROLLER for Reassign selection, non-Worker authority for the other
   authoritative determinations, a PENDING distinct successor linked to the
   old Run and same Task, or one accepted human handoff—but never both.
3. Keep M7B1 authority and M7B2 eligibility ahead of the semantic guard and
   retain all previous normal, retry, and resume semantics unchanged.  No
   lifecycle topology, repositories, runtime operations, successor creation,
   or Effect behavior is added.
4. Add deterministic tests for every accepted edge and required rejection,
   historical old-Run preservation, no successor mutation, and deny-by-default
   failed/aborted paths.
5. Run locked dependency synchronization, scoped tests, full tests, Ruff lint
   and format checks, strict mypy; explicitly stage only this Issue's files and
   create one local commit without remote mutation.

## Out of Scope

Replacement execution, scheduling, persistence/loading, process/credential
fencing, distributed locks, handoff delivery, Task/Objective/Outcome/Effect
mutation, failed/aborted semantics, Rewind, and ADR-0006 route-health runtime.

## Acceptance Evidence

The central transition engine only changes the old Run state and version after
the canonical guard passes.  The guard consumes no latest-wins data and never
creates or transitions a successor.  All required repository validation gates
must pass before the one local commit.
