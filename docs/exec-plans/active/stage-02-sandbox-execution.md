# Stage 02 — Sandbox Execution

**Delivery status:** HISTORICAL / SUPERSEDED FOR CURRENT v1 SEQUENCING

**Technical status:** cumulative M1C design HUMAN ACCEPTED; runtime implementation NOT STARTED

**Historical activation constitutional baseline:** `constitution-v0.1`

**Current constitutional context:** `constitution-v0.2`

**Accepted sandbox ADR/design:** `77acfbdaf2bed6f0536873fafc8eb7a12599da83`

**Issue #79:** SUPERSEDED / NOT RELEASED; closed as not planned; historical only

## Current disposition

This parent plan remains a durable historical record of the pre-transition Stage 2 delivery path. It is no longer the active v1 implementation sequence after accepted ADR-0009 and the accepted R2-R5 strategic reconciliation.

The accepted Stage 2 architecture is not rejected or weakened. Its post-transition role is:

- an execution-provider security/conformance contract;
- an optional/reference execution implementation path;
- an evidence/provenance boundary for execution integrations; and
- a reusable technical asset for the current roadmap's reference execution/provider work.

Owning a production sandbox runtime is no longer a mandatory v1 product prerequisite.

Issue #79 was durably superseded after final R5 acceptance and is closed as not planned. Its old r2/r3 authority MUST NOT be reopened, revised to READY or reused as G1 authority.

Any future implementation of this accepted design requires a fresh bounded TaskSpec under the current post-transition roadmap, normally when G7 reference execution/provider work is reached.

## Accepted historical baseline

ADR-0008 remains Accepted and technically unchanged. The historical pre-erratum Human Accepted design baseline is:

`b52df98530d8ce742b07d7f6c399ccd5b54e643b`

The cumulative M1C technical correction is:

`77acfbdaf2bed6f0536873fafc8eb7a12599da83`

parent:

`7ff155c29de83fbcc5487698c8b72b70b2dec075`

It passed independent technical review with **ACCEPT** on Issue #83 comment `5706630764` and received explicit Human erratum approval **APPROVED** on Issue #83 comment `5706652702`.

The accepted design artifacts remain:

- [ADR-0008: Stage 2 Sandbox Execution Boundary](../../adr/0008-stage-2-sandbox-execution-boundary.md);
- [Sandbox Execution v1](../../design-docs/sandbox-execution-v1.md); and
- [M1C UNKNOWN frozen salvage correction plan](stage-02-correction-m1c-unknown-frozen-salvage-v1.md).

## Historical activation and review lineage

Stage 2 design work was activated on 2026-09-16 by Issue #77 for M1 architecture/design only. It did not authorize runtime implementation.

The sequence was:

```text
Issue #77 M1 design activation
-> Issue #78 M1A correction
-> Issue #80 continuity governance
-> Issue #81 M1B correction
-> independent technical ACCEPT
-> explicit Human M1 design approval
-> Issue #82 governance reconciliation ACCEPT
-> Issue #79 r2 released
-> Worker STOP before mutation on UNKNOWN/collection contradiction
-> Issue #79 r3 BLOCKED / NOT RELEASED
-> Issue #83 M1C correction
-> independent M1C ACCEPT
-> explicit Human erratum APPROVED
-> Issue #84 acceptance reconciliation
-> strategic transition R1-R5
-> Issue #79 final supersession comment `5712361531`
-> Issue #79 closed SUPERSEDED / NOT RELEASED as not planned
```

Runtime isolation evidence was never established and Stage 2 runtime source code was never started.

## Historical objective

The original Stage 2 objective was to provide the first enforceable Worker execution boundary: temporary policy-controlled sandboxes, bounded commands, explicit workspaces, resource/network constraints, artifact integrity, teardown and provider-neutral failures.

That technical objective remains valid when Symphony-K supplies or validates a reference execution provider. What changed is product ownership and sequencing: Symphony-K v1 no longer requires completing this runtime before the governance SDK, evidence boundary, Effect gateway, audit or conformance product capabilities.

## Preserved architecture and trust requirements

The accepted design continues to require, where this provider contract is used:

- provider-neutral sandbox/workspace/command/result contracts;
- non-root and least-privilege execution;
- no privileged container or Docker-socket trust shortcut;
- explicit workspace ownership and generation/lease fencing;
- enforceable resource/time/process/network bounds;
- bounded output and hostile-artifact handling;
- trustworthy collection quiescence evidence;
- exact replay/idempotency and operation receipts;
- observable cleanup failure and targeted destruction; and
- provider/runtime details remaining outside core governance semantics.

The accepted M1C UNKNOWN frozen-salvage semantics and their exact design/test obligations remain historical technical truth.

## Superseded historical milestones

The original delivery plan proposed:

1. M1 architecture/design acceptance — **completed and Human accepted**;
2. M2 portable sandbox contracts/fake provider — **stopped before mutation; now SUPERSEDED / NOT RELEASED**;
3. M3 Docker lifecycle and enforced constraints — **never started**;
4. M4 adversarial real-runtime evidence — **never started**; and
5. Stage 2 Exit followed by Stage 3 AgentDriver activation — **superseded as the mandatory v1 sequence**.

These milestones remain provenance; they no longer confer current implementation authority.

## Relationship to current roadmap

The current roadmap's G7 reference execution/provider stage may reuse ADR-0008 and the accepted sandbox design in whole or in part. It may also validate an external provider against the same security/conformance boundary.

Any such work must explicitly state:

- which accepted Stage 2 requirements are reused;
- which provider/runtime supplies execution;
- what isolation/provenance claims are actually evidenced;
- what remains unimplemented; and
- how the integration maps into current governance/evidence/Effect contracts.

No future TaskSpec may infer that this historical parent plan authorizes source mutation.
