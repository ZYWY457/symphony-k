# Stage 12 — End-to-End Integration and Operational Safety

**Status:** PLANNED — not implementation authorization
**Constitutional baseline:** `constitution-v0.1`

## Objective and why this stage exists

Prove that all planes preserve constitutional behavior when composed and when
realistic faults, retries, conflicts and restarts occur.

## In scope

- Objective -> Proposal -> Task -> Run -> Outcome -> Evaluation -> disposition;
- sandbox failure/checkpoint recovery and Agent failure/reassignment;
- verification conflict/arbitration and Human escalation;
- budget exhaustion and permission denial/escalation;
- safe Effect commit/receipt, unauthorized observed occurrence and remediation;
- network/substrate failure, idempotent replay and process restart/reopen;
- system correlation, observability and operational runbooks.

## Out of scope

- major feature development;
- distributed/HA guarantees not already implemented;
- disabling safety checks to make scenarios pass;
- synthetic happy-path evidence as a substitute for failure injection.

## Architecture boundaries

This stage integrates accepted interfaces; it does not collapse plane ownership.
Any cross-plane inconsistency requiring a new concept or dependency triggers an
ADR and bounded correction rather than an integration-only workaround.

## Expected new interfaces and concepts

Prefer test/operations artifacts over domain concepts: end-to-end scenario
contract, cross-plane correlation convention, invariant monitor, failure-
injection harness and operational severity/escalation record. Any new
cross-cutting runtime concept requires ADR approval.

## Cross-stage dependencies

Requires Human-accepted Stages 1–11. Supplies evidence and runbooks for release
hardening and v1 acceptance.

## Security and trust requirements

Fault injection occurs in controlled environments. Tests assert authority,
history, evidence, isolation, credential and Effect invariants at every boundary.
Observability is redacted and attributable; audit remains durable across restart.

## Failure model

Every required scenario includes injected failures, expected classification,
recovery/escalation, durable evidence and prohibited outcomes. Unclassified or
non-reproducible failures block exit.

## Milestones

1. Approve scenario matrix, correlation and failure-injection design.
2. Prove normal governed workflow.
3. Prove execution/recovery and verification-conflict families.
4. Prove budget/permission/Effect safety families.
5. Prove network/substrate/replay/restart durability.
6. Complete observability/runbooks, invariant audit and Human Exit Review.

## Proposed bounded Issue decomposition

- scenario/correlation design;
- happy-path system workflow;
- sandbox/agent recovery scenarios;
- verification/arbitration scenarios;
- budget/permission scenarios;
- Effect commit/incident/remediation scenarios;
- replay/restart/network scenarios;
- runbooks, security audit and stage reconciliation.

## Validation strategy

Automated end-to-end matrix, deterministic failure injection where possible,
invariant assertions during intermediate states, independent state rereads,
restart/reopen tests, idempotent replay, receipt verification, audit correlation
and Human-run operational drills.

## Human Exit Review questions

- Does every scenario preserve authority, isolation, evidence and history?
- Can any restart, retry or failover duplicate or erase an Effect?
- Are conflicts and low confidence escalated rather than guessed away?
- Do correlated traces reconstruct decisions without relying on Worker reports?
- Can operators execute the runbooks and reach the documented safe state?

## Stage Definition of Done

All required scenario families survive realistic fault injection without a
constitutional violation; evidence, observability and runbooks are complete;
no unresolved cross-plane safety blocker remains. Human reconciliation precedes
Stage 13.
