# Stage 1 M7C3B4 — Canonical Run Abort Closure Semantic Guards

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #36 / Implementation #7C3B4 only

## TaskSpec and Preconditions

- TaskSpec reference: GitHub Issue #36
- TaskSpec access mode: direct-read
- TaskSpec precondition: PASS
- Execution substrate preflight: PASS (`git`, repository root, Python, and `uv`)

The launch prompt's purported materialized body was an empty placeholder. The
durable Issue was read directly before repository mutation, which is an allowed
TaskSpec access mode under `AGENTS.md`.

## Objective

Add canonical, Run-only semantic guards to the existing M7 transition boundary
for exactly these existing edges:

- `PENDING -> ABORTED`
- `RUNNING -> ABORTED`
- `WAITING_FOR_VERIFICATION -> ABORTED`
- `RETRYING -> ABORTED`

Each closure requires an evidence-backed stop basis, an R-authorized abort
decision, and evidence that execution ownership ended or is fenced. `ABORTED`
remains distinct from `FAILED` and `REASSIGNED`.

## Bounded Steps

1. Define the minimum immutable exact-snapshot-bound stop-basis and abort
   decision types, using a positive R authority allow-set and the existing
   ownership fencing decision.
2. Define the abort semantic bundle and map it to only the four existing
   `-> ABORTED` Run edges in `RunSemanticGuard`.
3. Add deterministic tests for complete closure, exact provenance, authority
   rejection, all basis categories, worker evidence/authority boundaries,
   rejected conditions, historical preservation, and non-propagation.
4. Run all Issue-required validation gates, explicitly stage only these Issue
   files, inspect the staged diff, and create one local commit without remote
   mutation.

## Out of Scope

Lifecycle topology or states; transition-engine redesign; failure/reassignment
redesign; successor Run creation; policy, safety, human, scheduler, or process
runtime; persistence; Task/Objective/Outcome/Evaluation/Effect mutation; Effect
reconciliation; and ADR-0006 automatic failover.

## Acceptance Evidence

The central transition mutates only the old Run's state and version after
M7B1/M7B2 and the canonical abort guard pass. Failed validation leaves the Run
unchanged and produces no successful lifecycle event.
