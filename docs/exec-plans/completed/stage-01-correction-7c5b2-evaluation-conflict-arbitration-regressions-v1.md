# Stage 1 Correction 7C5B2 — Evaluation Conflict and Arbitration Regressions

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #48 only

## Context

Issue #47 successfully corrected root-judgement binding for the accepted M7C5B
arbitration semantics. It did not complete the requested canonical regression
hardening. This correction adds that missing transition-boundary coverage without
redesigning M7C5B or introducing M8 persistence/current-record discovery.

## In scope

- Parameterized canonical `TransitionAuthorityDecision` +
  `EvaluationSemanticGuard` + `transition_entity(...)` regressions for conflict
  binding, arbitration history, authority, projection immutability, and topology.
- A minimal production correction only if one of those regressions exposes a
  defect in the accepted M7C5B semantics.

## Out of scope

- New Evaluation edges, entities, persistence, repositories, transactions,
  current-record discovery, conflict detection, and all M8 work.

## Acceptance evidence

- Exact correlation, principal, member/version, scope/materiality, conflict-set
  extension, arbitration lineage, invalidation, and authority bindings are tested
  through the canonical M7 transition boundary.
- Evaluation transitions retain immutable original content and the exact ten-edge
  topology.
- The full repository validation suite passes; no remote mutation occurs.
