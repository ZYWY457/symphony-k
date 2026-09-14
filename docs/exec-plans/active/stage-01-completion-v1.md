# Stage 1 Completion Map

**Version:** 1
**Status:** Active
**Scope:** GitHub Issues #53, #61, and #67 — planning and governance reconciliation only

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

## Historical baseline M7 coverage

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

The accepted progress closes the normal Effect remediation family. At that
historical acceptance boundary, exactly four non-creation Effect edges remained:

```text
QUARANTINED -> PENDING_COMMIT
QUARANTINED -> ROLLED_BACK
QUARANTINED -> COMPENSATING
QUARANTINED -> COMPENSATED
```

The bounded implementation sequence at that time was first the normal
remediation family (`COMMITTED -> ROLLED_BACK`, `COMMITTED -> COMPENSATING`, and
`COMPENSATING -> COMPENSATED`), then the quarantine remediation and re-entry
family. This paragraph preserves historical sequencing context; those four
quarantine edges are no longer current unresolved work.

## Accepted non-creation completion

Through commit `9278f4a21a180e258ef2f302bf66c47977f9c860`
(`fix(domain): preserve quarantine resume completion lineage`), independent
Human Review accepted all 91 Stage 1 non-creation lifecycle edges:

| Entity | Covered / accepted non-creation edges |
| --- | ---: |
| Objective | 17 / 17 |
| Task | 16 / 16 |
| Run | 18 / 18 |
| Outcome | 11 / 11 |
| Evaluation | 10 / 10 |
| Effect | 19 / 19 |
| **Total** | **91 / 91** |

All non-creation lifecycle semantics are now complete and accepted. The four
quarantine edges listed above remain only as history of the earlier 87 / 91
boundary; they are not current unresolved work.

## Accepted M7D1 shared creation protocol

At commit `e18b22aa26514b08b6faa0ea7ab251d356b7d48f`
(`test(domain): prove creation event version exact binding`), independent Human
Review accepted the cumulative M7D1 shared authoritative creation protocol
produced by Issues #63, #64, #65, and #66.

This acceptance applies to the corrected cumulative result. It does not imply
that the original Issue #63 candidate was independently sufficient before the
Issue #64 creation binding corrections, the Issue #65 event-annotation
correction and closure audit, and the Issue #66 event-version regression proof.

The accepted lifecycle boundary is unchanged:

```text
non-creation accepted = 91 / 91
creation accepted     = 0 / 8
integrated accepted   = 91 / 99
```

M7D1 accepts only the shared protocol and its fail-closed boundary. It accepts
no authoritative creation edge. The entity-specific semantics required to
open any creation edge remain future work.

## Unresolved authoritative creation edges

All eight creation edges remain unresolved M7 work:

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

Creation structural declarations, event/metadata groundwork, and the M7D1
shared protocol exist and are Human Accepted. Authoritative creation execution
remains fail-closed because entity-specific semantics do not yet exist. The
remaining M7 boundary must enforce the canonical creation target,
entity-specific semantic invariants, relationships and provenance before
returning an immutable version-1 snapshot and exactly one creation DomainEvent.
It must never fabricate a `NONE` enum state.

Effect `NONE -> COMMITTED` and `NONE -> QUARANTINED` retain their
observation-only semantics. They must record independently anchored reality
without fabricating planning, authorization, or dispatch history.

## Remaining Stage 1 order

```text
91/91 non-creation semantics accepted
    ->
M7D1 shared creation protocol Human Accepted at
e18b22aa26514b08b6faa0ea7ab251d356b7d48f
    ->
M7D2 Objective + Task creation semantics (next implementation slice)
    ->
M7D3 Run + Outcome + Evaluation creation semantics
    ->
M7D4 Planned Effect creation semantics
    ->
M7D5 Observed Effect creation semantics
    ->
M7D6 integrated eight-edge acceptance candidate
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

```text
M7 non-creation semantics = complete and accepted
M7D1 shared creation protocol = HUMAN ACCEPTED
M7 authoritative creation = incomplete
M7 integrated 99-edge acceptance = incomplete
Stage 1 = incomplete
```

M7 remains incomplete because all eight authoritative creation edges listed
above remain unresolved. M7D2 Objective + Task is the next implementation
slice. M8 and M9 are not complete.
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
