# Stage 1 M7B1 — Mandatory Transition Authority Decision Contract

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #22 only

## Boundary

M7B1 strengthens the M7A pure transition contract with one immutable,
exact-snapshot-bound authority decision. Authority remains distinct from the
generic semantic/invariant guard chain. This change defines no positive actor
authority rules, lifecycle topology, policy engine, repository, persistence, or
external execution behavior.

## Bounded steps

1. Add the closed `AUTHORIZED`, `DENIED`, and `UNRESOLVED` authority status and
   a frozen transition-authority decision bound to actor, core entity identity,
   observed version, source state, target state, and correlation.
2. Require the centralized transition engine to reject a missing, non-authorized,
   or incompatible decision before evaluating semantic guards.
3. Preserve request/decision/event actor identity and the existing version,
   topology, guard, immutable-snapshot, and event semantics.
4. Export only the new stable authority concepts and add runtime and strict
   static typing tests for exact binding, deny-by-default behavior, separation
   from M6 records, and absence of universal role shortcuts or M7B2+ runtime.
5. Run every Issue #22 validation gate, explicitly stage only M7B1 files, inspect
   the complete staged diff, and create exactly one local commit.

## Acceptance

A generic passing `TransitionGuard` never establishes lifecycle authority. Only
an explicit compatible `AUTHORIZED` decision permits evaluation to continue to
the semantic guard chain, and a failing semantic guard still rejects. No actor
type, including SYSTEM, HUMAN_OPERATOR, or WORKER, receives implicit authority.
