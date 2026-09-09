# Stage 1 M7C3A — Canonical Run Normal-Execution Semantic Guards

**Version:** 1
**Status:** Active
**Scope:** Implementation #7C3A only

## Boundary

M7C3A adds the canonical Run-only semantic gate for exactly four normal Run
edges in the existing M7A/M7B1/M7B2 pure transition boundary.  It consumes
immutable, typed, exact-snapshot-bound decisions and evidence references.  It
does not evaluate policy, load state, persist records, control a runtime,
change Task/Objective/Outcome state, or implement recovery, reassignment,
failure, or abort semantics.

## Bounded Steps

1. Define the minimum Run semantic decision, cross-entity observation, and
   evidence-provenance types for PENDING -> RUNNING, RUNNING ->
   WAITING_FOR_VERIFICATION, RUNNING -> COMPLETED, and
   WAITING_FOR_VERIFICATION -> COMPLETED. Acceptance: every consumed decision
   is bound to RunId, observed Run EntityVersion, and CorrelationId; Task,
   Objective, and Outcome observations retain their own IDs and versions.
2. Implement one canonical Run semantic guard for those four edges. Acceptance:
   start requires Task IN_PROGRESS, its primary Objective ACTIVE, compatible
   ownership, exact profile approval, boundary/grants/budget validity, and an
   independently trusted start confirmation; wait requires stopped execution,
   an originating candidate Outcome with evidence, and an explicit verification
   request; both completion paths retain their separate normal-closure rules.
3. Require the canonical Run guard before ordinary generic guards, while
   retaining the existing authority and eligibility gates. Acceptance:
   recovery/reassign/failure/abort edges reject because M7C3B owns their
   semantics; no Run completion decision accepts an Outcome, completes a Task,
   or satisfies an Objective.
4. Add deterministic tests for successful normal edges, exact binding and
   cross-entity-version provenance, all required negative conditions, generic
   guard composition, immutable rejection, unchanged topology, and explicit
   non-propagation.
5. Run the locked, scoped and full validation gates; stage only this Issue's
   paths; inspect staged names, diff and whitespace; create exactly one local
   commit and do not push.

## Out of Scope

Repositories, persistence, policy evaluation, runtime process control,
checkpoint recovery, Outcome/Evaluation mutation, ADR-0006 failover runtime,
and every M7C3B+ Run edge remain out of scope. No lifecycle topology, state,
or new top-level domain concept is introduced.

## Intended Commit Scope

- docs/exec-plans/active/stage-01-m7c3a-run-normal-semantic-guards-v1.md
- src/symphony_k/domain/__init__.py
- src/symphony_k/domain/run_semantics.py
- src/symphony_k/domain/transition_engine.py
- tests/test_run_semantic_transitions.py
- tests/test_transition_engine.py
