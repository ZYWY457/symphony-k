# Roadmap

This is the canonical high-level Stage 0–14 delivery map. It states what
observable product/system capability each stage unlocks while leaving detailed
entry, architecture, milestone and evidence decisions to the linked contracts.

Read with:

- [v1 Product Contract](docs/V1_PRODUCT_CONTRACT.md) — observable v1 scope and
  final acceptance expectations;
- [Reference Workflows](docs/REFERENCE_WORKFLOWS.md) — canonical product
  scenarios and stage traceability; and
- [Development Path](docs/DEVELOPMENT_PATH.md) — complete stage entry,
  deliverable, evidence and exit contracts.

`ACTIVE - M1 architecture/design` records authorized design work, not runtime
implementation or acceptance. Stage 2 runtime implementation has not started
and is not authorized by the current design TaskSpec.

## Delivery status

| Stage | Name | Status |
| ---: | --- | --- |
| 0 | Constitution and Repository Harness | COMPLETE |
| 1 | Domain Kernel | COMPLETE — Human Exit ACCEPTED |
| 2 | Sandbox Execution | ACTIVE - M1 architecture/design |
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

## Stage 0 — Constitution and Repository Harness

- **Status:** COMPLETE.
- **Observable capability unlocked:** A maintainer can determine the project's
  purpose, authority hierarchy, immutable rules and development process from
  repository artifacts rather than private conversation history.
- **Primary deliverables:** Constitution, vision, architecture, core beliefs,
  ADR process, Exec Plan process and repository/tooling harness.
- **Exit proof:** Constitutional invariants, document hierarchy and repository
  navigation were established and accepted before domain implementation.
- **Detailed contract:** [Constitution](CONSTITUTION.md),
  [Architecture](ARCHITECTURE.md), and [documentation map](docs/README.md).

## Stage 1 — Domain Kernel

- **Status:** COMPLETE — Human Exit ACCEPTED.
- **Observable capability unlocked:** Symphony-K can durably represent and
  govern Objective, Task, Run, Outcome, Evaluation and Effect lifecycles without
  allowing Workers or normal APIs to create unauthorized/impossible state.
- **Primary deliverables:** Six core entities, 43 states, 99 lifecycle edges,
  transition authority, immutable history/events, persistence, replay and
  optimistic concurrency.
- **Exit proof:** M7/M8/M9 Human Accepted; 99 / 99 lifecycle coverage; all eight
  Human Stage 1 Exit questions answered safely.
- **Detailed contract:** [Completed Stage 1 parent plan](docs/exec-plans/completed/stage-01-domain-kernel.md)
  and [completion map](docs/exec-plans/completed/stage-01-completion-v1.md).

## Stage 2 — Sandbox Execution

- **Status:** ACTIVE - M1 architecture/design; runtime code NOT YET STARTED;
  runtime implementation NOT AUTHORIZED by Issue #77.
- **Observable capability unlocked:** Symphony-K can run arbitrary bounded
  commands in temporary, enforceably constrained sandboxes without using the
  host as the Worker runtime.
- **Primary deliverables:** `SandboxProvider`, first Docker provider,
  `Workspace`, command/resource/time/network bounds, artifacts, cleanup,
  telemetry and normalized failures.
- **Exit proof:** Isolation, privilege, mount/socket, resource, network,
  artifact and teardown behavior pass deterministic and adversarial checks.
- **Detailed contract:** [Active Stage 2 parent](docs/exec-plans/active/stage-02-sandbox-execution.md).
- **Current gate:** independent review and Human approval of the proposed
  sandbox ADR and candidate design before a separate M2 implementation TaskSpec.

## Stage 3 — First AgentDriver

- **Status:** PLANNED.
- **Observable capability unlocked:** Symphony-K can execute a governed Run
  through the first replaceable AgentDriver without coupling the Domain Kernel
  to Codex or provider protocols.
- **Primary deliverables:** AgentDriver/capability contracts, structured
  requests/events/results, usage/cancel/resume behavior, Codex adapter and
  provider-neutral errors.
- **Exit proof:** Sandboxed Codex execution passes shared contracts and no
  vendor-specific dependency enters core domain semantics.
- **Detailed contract:** [Planned Stage 3 parent](docs/exec-plans/planned/stage-03-first-agent-driver.md).

## Stage 4 — Verification Plane

- **Status:** PLANNED.
- **Observable capability unlocked:** Symphony-K can independently verify
  candidate work and persist evidence-backed Evaluations instead of trusting
  Worker self-report.
- **Primary deliverables:** Validation planning/profiles, evidence collection,
  static/dynamic/intermediate/semantic validators, confidence gating and
  conflict/arbitration integration.
- **Exit proof:** Producer-independent evidence governs candidate disposition;
  stale, tampered, missing and conflicting evidence fail closed or escalate.
- **Detailed contract:** [Planned Stage 4 parent](docs/exec-plans/planned/stage-04-verification-plane.md).

## Stage 5 — Failure and Recovery

- **Status:** PLANNED.
- **Observable capability unlocked:** Work and authoritative history survive
  Worker, sandbox, process and provider loss, with visible bounded recovery.
- **Primary deliverables:** Trusted checkpoints, failure classification,
  RecoveryController, Resume/Rewind/Reassign, handoff packages, stall detection
  and recovery limits.
- **Exit proof:** Failure injection demonstrates durable progress, correct Run
  lineage, untrusted-checkpoint rejection and no blind replay of uncertain
  Effects.
- **Detailed contract:** [Planned Stage 5 parent](docs/exec-plans/planned/stage-05-failure-and-recovery.md).

## Stage 6 — Budget, Risk, Permission, and Effects

- **Status:** PLANNED.
- **Observable capability unlocked:** Operators can constrain resource use and
  govern consequential external changes through explicit permission,
  verification, authorization, commit and remediation history.
- **Primary deliverables:** Budget ledger/profiles, risk/value/confidence/
  verifiability inputs, permission envelopes, Effect Controller, scoped
  capabilities, idempotency, receipts, rollback/compensation and Human gates.
- **Exit proof:** Budget/permission violations fail closed; important Effects
  cannot bypass governance; irreversible commit requires exact Human
  authorization; occurrence truth remains independently durable.
- **Detailed contract:** [Planned Stage 6 parent](docs/exec-plans/planned/stage-06-budget-risk-permission-effects.md).

## Stage 7 — Second Agent and Architecture Test

- **Status:** PLANNED.
- **Observable capability unlocked:** Symphony-K can use two materially
  different Agent runtime families through the same governed product boundary.
- **Primary deliverables:** A Human-selected second adapter/configuration/image,
  shared conformance evidence and architecture findings.
- **Exit proof:** The second runtime requires no core orchestration redesign;
  any abstraction failure is reviewed rather than hidden in adapter-specific
  hacks.
- **Detailed contract:** [Planned Stage 7 parent](docs/exec-plans/planned/stage-07-second-agent-architecture-test.md).

## Stage 8 — Router and Escalation

- **Status:** PLANNED.
- **Observable capability unlocked:** Symphony-K can select an eligible healthy
  execution route from explicit capability, policy, budget, cost and reliability
  constraints instead of a hard-coded Agent.
- **Primary deliverables:** Capability registry, resolved route/profile,
  eligibility engine, substrate/capability health, cost/reliability inputs,
  circuit health and escalation/degradation policy.
- **Exit proof:** Deterministic scenarios explain each selection, block
  incompatible/no-route cases and preserve Effect-safe reassignment.
- **Detailed contract:** [Planned Stage 8 parent](docs/exec-plans/planned/stage-08-router-and-escalation.md).

## Stage 9 — Planner

- **Status:** PLANNED.
- **Observable capability unlocked:** Symphony-K can propose bounded,
  dependency-aware work for an Objective without giving the Planner execution
  or lifecycle authority.
- **Primary deliverables:** Non-executable TaskProposal lifecycle, bounded
  Objective decomposition, dependency DAG, planning limits, rationale/evidence,
  proposal governance and separate Task promotion.
- **Exit proof:** Cycles/scope/budget violations are rejected; proposals never
  execute; accepted promotion creates a distinct authoritative Task.
- **Detailed contract:** [Planned Stage 9 parent](docs/exec-plans/planned/stage-09-planner.md).

## Stage 10 — Learning and Reputation

- **Status:** PLANNED.
- **Observable capability unlocked:** Verified historical experience can
  influence routing, validation and policy through auditable, controlled and
  reversible updates rather than raw-event feedback.
- **Primary deliverables:** Delayed observation, verified experience pool,
  scoped reliability/calibration views, policy candidates, shadow evaluation,
  canary rollout and rollback.
- **Exit proof:** Raw/disputed data cannot change production policy; candidates
  are attributable, calibrated, shadow-tested, canaried and reversible.
- **Detailed contract:** [Planned Stage 10 parent](docs/exec-plans/planned/stage-10-learning-and-reputation.md).

## Stage 11 — Application Control Plane and Human Governance Surface

- **Status:** PLANNED.
- **Observable capability unlocked:** An operator can drive and inspect the
  governed workflow through supported public interfaces without database edits
  or private internal Python calls.
- **Primary deliverables:** Application services, stable local service/API,
  supported CLI, Objective/proposal actions, state/evidence inspection, Human
  approvals/overrides/break-glass, identity/authorization and audit queries.
- **Exit proof:** End-user workflows and authorization tests demonstrate that
  handlers cannot bypass authoritative services and every Human action is
  scoped/audited.
- **Detailed contract:** [Planned Stage 11 parent](docs/exec-plans/planned/stage-11-application-control-plane.md).

## Stage 12 — End-to-End Integration and Operational Safety

- **Status:** PLANNED.
- **Observable capability unlocked:** The complete product workflow remains
  governable and auditable across realistic success, failure, conflict,
  restart, permission and Effect scenarios.
- **Primary deliverables:** Required end-to-end scenario matrix, failure
  injection, cross-plane correlation/observability, invariant monitoring and
  operational runbooks.
- **Exit proof:** All [reference workflows](docs/REFERENCE_WORKFLOWS.md) and
  required adverse branches preserve constitutional invariants with traceable
  evidence.
- **Detailed contract:** [Planned Stage 12 parent](docs/exec-plans/planned/stage-12-end-to-end-operational-safety.md).

## Stage 13 — Production Hardening and Release Engineering

- **Status:** PLANNED.
- **Observable capability unlocked:** The accepted single-node v1 scope can be
  installed, configured, observed, backed up, restored, upgraded and rolled
  back reproducibly within declared support limits.
- **Primary deliverables:** Packaging/install, configuration/environment
  validation, migrations, backup/restore, secrets boundary, observability,
  security/dependency gates, artifacts/SBOM, resource baselines and runbooks.
- **Exit proof:** Fresh install, migration/rollback, backup/restore,
  crash/restart, security, reproducible build and operational drills pass with
  no production-readiness blocker.
- **Detailed contract:** [Planned Stage 13 parent](docs/exec-plans/planned/stage-13-production-hardening-release-engineering.md).

## Stage 14 — v1.0 Release Candidate and Final Delivery

- **Status:** PLANNED.
- **Observable capability unlocked:** A fresh maintainer can install and operate
  the accepted v1 product from repository documentation, demonstrate its
  canonical workflows and reproduce release artifacts.
- **Primary deliverables:** Frozen v1 scope, install/operator/contributor guides,
  architecture/security review, acceptance matrix, known limitations, examples,
  release notes, metadata audit and reproducible candidate artifacts.
- **Exit proof:** The [Product Contract](docs/V1_PRODUCT_CONTRACT.md) and all
  reference workflows are independently accepted; artifacts reproduce; no
  release-blocking constitutional/security defect remains.
- **Detailed contract:** [Planned Stage 14 parent](docs/exec-plans/planned/stage-14-v1-release-and-delivery.md).

Release/tag publication is not implied by Stage 14 candidate work. It remains a
separate remote Effect requiring explicit Human authorization.

## Post-v1 non-blocking backlog

The following remain non-blocking candidates unless a Human roadmap amendment
promotes them:

- distributed workers and HA control-plane clustering;
- remote sandbox providers and microVM isolation;
- GPU/local-model resource pools and advanced scheduling;
- richer governance UI and organization/multi-tenant controls;
- external tracker ecosystems and self-hosted policy analytics;
- evidence-supported routing enhancements beyond accepted Stage 10 scope; and
- additional specialized AgentDrivers.
