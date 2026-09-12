# Stage 1 M7C1 — Canonical Objective Semantic Transition Guards

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #24 only

## Boundary

M7C1 adds the canonical Objective-only semantic gate to the existing M7A/M7B1/M7B2
pure transition boundary. It consumes immutable, typed, exact-snapshot-bound
decisions and evidence references. It does not evaluate policy, load state, persist
records, propagate child state, or implement semantic guards for any other entity.

## Bounded steps

1. Define the minimum Objective semantic decision and evidence-provenance types for
   the accepted Objective edges.
2. Implement one canonical Objective semantic guard bound to ObjectiveId, observed
   EntityVersion, source/target ObjectiveState, and CorrelationId.
3. Require that canonical guard explicitly for every Objective transition while
   retaining generic TransitionGuard instances only as additional checks.
4. Test every one of the accepted seventeen Objective state edges, exact binding,
   authority/eligibility/semantic composition, immutable failure behavior, no
   child propagation, and unchanged topology.
5. Run all Issue #24 validation gates, explicitly stage only M7C1 files, inspect the
   complete staged diff, and create exactly one local commit.

## Acceptance evidence

- DRAFT -> ACTIVE consumes current governance, budget, permission, and time-horizon
  decisions and rejects an elapsed Objective.valid_until.
- ACTIVE -> BLOCKED requires an explicit current blocker and current validity.
- BLOCKED -> ACTIVE requires explicit blocker resolution and refreshed activation
  eligibility.
- ACTIVE/BLOCKED -> SATISFIED separately requires the exact CompletionPolicyRef, a
  passing evidence-backed completion decision, an independence decision, designated
  acceptance, and resolved or lawfully waived completion blockers.
- FAILED, CANCELLED, EXPIRED, and ARCHIVED retain their accepted edge-specific
  decision provenance; expiry uses only TransitionRequest.timestamp.
- Missing or incompatible canonical Objective semantics reject without a new
  Objective, version, TransitionResult, or DomainEvent.
- No dependencies, topology changes, repositories, persistence, policy engines,
  external execution, ADR-0006 runtime, or M7C2+ behavior are added.
