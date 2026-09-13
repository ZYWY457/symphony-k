# Stage 1 Completion Map

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #53 — planning and governance reconciliation only

## Purpose and baseline

This is the durable current completion map for Stage 1 at baseline commit
`58a5c1644b58cc6ad24440bfc3c07dd8817bc5e5`
(`fix(domain): bind historical effect observation provenance`). It supplements,
rather than replaces, the accepted parent plan:
[Stage 01 — Domain Kernel](stage-01-domain-kernel.md).

The accepted architecture remains unchanged: six core entities, 43 states, 99
legal lifecycle edges including eight creation edges, and 91 non-creation edges.
`NONE` remains absence of a lifecycle state, not an enum value.

This plan is a status and sequencing artifact. It does not authorize one Run to
implement the remaining Stage 1 work. Each future implementation boundary
requires its own durable TaskSpec.

## Current M7 coverage

At the baseline, canonical authoritative semantic execution covers 84 of 91
non-creation edges:

| Entity | Covered / accepted non-creation edges |
| --- | ---: |
| Objective | 17 / 17 |
| Task | 16 / 16 |
| Run | 18 / 18 |
| Outcome | 11 / 11 |
| Evaluation | 10 / 10 |
| Effect | 12 / 19 |
| **Total** | **84 / 91** |

The seven remaining non-creation edges are Effect remediation and controlled
re-entry work:

```text
COMMITTED -> ROLLED_BACK
COMMITTED -> COMPENSATING
COMPENSATING -> COMPENSATED

QUARANTINED -> PENDING_COMMIT
QUARANTINED -> ROLLED_BACK
QUARANTINED -> COMPENSATING
QUARANTINED -> COMPENSATED
```

## Accepted progress after the baseline

The original baseline above remains the historical `84 / 91` record. Through
commit `e0da5b1a32455de9c01f85b46a69c4fc057fbc01`
(`fix(domain): bind effect remediation authorization provenance`), accepted
canonical authoritative semantic execution covers 87 of 91 non-creation edges:

| Entity | Covered / accepted non-creation edges |
| --- | ---: |
| Objective | 17 / 17 |
| Task | 16 / 16 |
| Run | 18 / 18 |
| Outcome | 11 / 11 |
| Evaluation | 10 / 10 |
| Effect | 15 / 19 |
| **Total** | **87 / 91** |

The accepted progress closes the normal Effect remediation family. Exactly four
non-creation Effect edges remain:

```text
QUARANTINED -> PENDING_COMMIT
QUARANTINED -> ROLLED_BACK
QUARANTINED -> COMPENSATING
QUARANTINED -> COMPENSATED
```

The likely bounded implementation sequence is first the normal remediation
family (`COMMITTED -> ROLLED_BACK`, `COMMITTED -> COMPENSATING`, and
`COMPENSATING -> COMPENSATED`), then the quarantine remediation and re-entry
family. These are planning boundaries only; no future GitHub Issue numbers are
reserved here.

## Unresolved authoritative creation work

The eight accepted creation edges remain unresolved M7 work:

```text
Objective:  NONE -> DRAFT
Task:       NONE -> DRAFT
Run:        NONE -> PENDING
Outcome:    NONE -> PROPOSED
Evaluation: NONE -> PENDING
Effect:     NONE -> PLANNED
            NONE -> COMMITTED
            NONE -> QUARANTINED
```

Creation structural declarations and event/metadata groundwork exist, but
authoritative creation execution does not. Its future M7 boundary must enforce
the canonical creation target, authority, entity-specific semantic invariants,
relationships and provenance, immutable initial snapshot, initial-version
semantics, and exactly one creation DomainEvent. It must never fabricate a
`NONE` enum state.

Effect `NONE -> COMMITTED` and `NONE -> QUARANTINED` retain their
observation-only semantics. They must record independently anchored reality
without fabricating planning, authorization, or dispatch history.

## Remaining Stage 1 order

```text
M7 Effect normal remediation
    ->
M7 Effect quarantine remediation/re-entry
    ->
91/91 non-creation semantics
    ->
M7 authoritative creation closure
    ->
M7 integrated 99-edge acceptance
    ->
M8 Persistence and Atomicity
    ->
M9 Constitutional Test Suite
    ->
Stage 1 reconciliation
    ->
Human Stage 1 Exit Review
    ->
Stage 2 only after acceptance
```

M8 retains the accepted parent-plan ownership: repository interfaces, an
initial persistence adapter, authoritative loading/currentness, optimistic
concurrency, transaction semantics, atomic state and lifecycle-event
persistence, structural persistence constraints, and required history and
uniqueness guarantees. M8 is not satisfied by the current in-memory domain
semantics.

M9 remains the already-defined Constitutional Test Suite from the accepted
parent plan. It is not a new milestone. Its executable invariants must confirm
the constitutional restrictions alongside the completed lifecycle work.

## Exit boundary

Stage 1 is not complete, and M7 is not complete. M8 and M9 are not complete.
The required human Stage 1 Exit Review remains the final acceptance boundary;
Stage 2 is entirely out of scope until that review accepts Stage 1.

No real Agent execution or real external Effect execution is introduced by this
plan or by the remaining Stage 1 completion work.

## Acceptance for this plan

- The map remains consistent with the accepted Stage 1 architecture and parent
  plan.
- Future work uses separately materialized durable TaskSpecs and bounded
  implementation plans.
- Completion claims distinguish current structural declarations from
  authoritative execution, and do not declare Stage 1, M7, M8, or M9 complete.
