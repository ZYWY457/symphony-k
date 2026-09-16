# Roadmap

This is the canonical high-level stage map for Symphony-K. It defines delivery
order and stage boundaries, not permanent implementation choices. Detailed
contracts live in [the development path](docs/DEVELOPMENT_PATH.md) and stage
parent Exec Plans. Every stage remains subject to the Constitution, core
beliefs, accepted ADRs, and independent Human Exit Review.

## Delivery status

| Stage | Name | Status |
| ---: | --- | --- |
| 0 | Constitution and Repository Harness | COMPLETE |
| 1 | Domain Kernel | COMPLETE — Human Exit ACCEPTED |
| 2 | Sandbox Execution | NEXT |
| 3 | First AgentDriver | PLANNED |
| 4 | Verification Plane | PLANNED |
| 5 | Failure and Recovery | PLANNED |
| 6 | Budget, Risk, Permission, and Effects | PLANNED |
| 7 | Second Agent and Architecture Test | PLANNED |
| 8 | Router and Escalation | PLANNED |
| 9 | Planner | PLANNED |
| 10 | Learning and Reputation | PLANNED |
| 11 | Application Control Plane and Human Governance Surface | PLANNED |
| 12 | End-to-End Integration and Operational Safety | PLANNED |
| 13 | Production Hardening and Release Engineering | PLANNED |
| 14 | v1.0 Release Candidate and Final Delivery | PLANNED |

`PLANNED` and `NEXT` describe sequence only. Stage 2 implementation has not
started and requires a separate durable Human-approved TaskSpec before code may
change.

## Stage 0 — Constitution and Repository Harness

Established the Constitution, vision, architecture, core beliefs, ADR and Exec
Plan processes, and repository harness. **Complete.**

## Stage 1 — Domain Kernel

Established Objective, Task, Run, Outcome, Evaluation and Effect lifecycles;
transition authority; persistence; immutable history; concurrency; and
constitutional tests. Human Accepted coverage is 99 / 99 lifecycle edges.
**Complete; Human Stage 1 Exit Review accepted.**

## Stage 2 — Sandbox Execution

Establish the `SandboxProvider` and `Workspace` abstractions, a hardened first
Docker provider, bounded command execution, resource and network policy,
artifact collection, cleanup, telemetry and normalized failures. Exit proves
arbitrary bounded commands run under enforceable temporary isolation. Stage 2
does not implement an AgentDriver.

## Stage 3 — First AgentDriver

Establish the replaceable `AgentDriver` boundary and integrate Codex as the
first adapter, including capabilities, structured requests/events/results,
usage, cancellation and provider-supported resume. Exit proves a governed Run
can use the adapter and sandbox without vendor concepts entering the core.

## Stage 4 — Verification Plane

Establish validation planning, independent evidence collection, static,
dynamic and semantic validators, intermediate assertions, confidence gates,
persisted Evaluations and conflict/arbitration integration. Exit removes Worker
self-report from authoritative completion and acceptance decisions.

## Stage 5 — Failure and Recovery

Establish trusted checkpoints, normalized failure classification,
`RecoveryController`, Resume, Rewind, Reassign, handoff packages, loop detection
and bounded recovery. Exit proves authoritative work survives Worker, sandbox
and provider loss.

## Stage 6 — Budget, Risk, Permission, and Effects

Establish governed profiles and ledgers, permission envelopes, scoped
credentials, and the Effect Controller runtime with
Prepare–Verify–Authorize–Commit, receipts, idempotency, rollback and
compensation. Exit proves consequential external changes cannot bypass the
Effect path and irreversible effects retain explicit Human authorization.

## Stage 7 — Second Agent and Architecture Test

Integrate one materially different Agent runtime through the existing
boundaries. Selection is a future bounded decision; Hermes is only a candidate.
Exit requires adapter/configuration/image work rather than core redesign.

## Stage 8 — Router and Escalation

Establish capability and health registries, resolved execution routes,
constraint-based eligibility, cost/reliability-aware selection, degradation and
escalation. Exit replaces hard-coded Agent choice with explicit governed route
selection. Learned routing remains deferred until trustworthy Stage 10 inputs.

## Stage 9 — Planner

Establish bounded Objective-to-`TaskProposal` planning, dependency DAGs,
planning limits, rationale/evidence and proposal governance. A proposal is
never executable; promotion creates a separate Task only after governance.

## Stage 10 — Learning and Reputation

Establish delayed verified-experience promotion, scoped reliability views,
candidate policy generation, shadow evaluation, canaries and reversible
versioned policy. Raw audit history never directly mutates production policy.

## Stage 11 — Application Control Plane and Human Governance Surface

Establish application services, a stable local API and operator interface,
workflow inspection, approval/rejection, override and break-glass recording,
identity/authorization and audit queries. Exit lets an operator govern the
system without raw database edits or internal Python calls.

## Stage 12 — End-to-End Integration and Operational Safety

Prove complete cross-plane workflows and realistic failure scenarios, including
verification conflict, recovery, budget and permission denial, safe Effects,
unauthorized occurrence recording, replay and process restart. Add correlated
observability and operational runbooks.

## Stage 13 — Production Hardening and Release Engineering

Establish packaging, configuration, migrations, backup/restore, secrets
integration, observability, security and dependency gates, reproducible release
artifacts, performance baselines and upgrade/rollback procedures. The accepted
v1 deployment may be single-node; distributed or HA claims require separate
implementation and evidence.

## Stage 14 — v1.0 Release Candidate and Final Delivery

Freeze scope, complete operator/developer documentation and examples, perform
architecture/security and end-to-end acceptance review, publish reproducible
release artifacts, and obtain final Human v1 acceptance. Tagging or publishing
v1.0 remains a separate remote Effect requiring explicit Human authorization.

## Post-v1 non-blocking backlog

The following are candidates, not v1 blockers unless a Human roadmap amendment
changes that boundary:

- distributed workers and HA control-plane clustering;
- remote sandbox providers and microVM isolation;
- GPU and local-model resource pools;
- advanced schedulers and learned routing after sufficient evidence;
- richer governance UI and organization/multi-tenant controls;
- external tracker adapters and self-hosted policy analytics;
- additional specialized AgentDrivers.
