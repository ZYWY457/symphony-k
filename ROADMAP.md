# Roadmap

This is the canonical high-level delivery map for Symphony-K v1 after the accepted strategic transition.

Read with:

- [v1 Product Contract](docs/V1_PRODUCT_CONTRACT.md) — observable v1 scope and final acceptance expectations;
- [Development Path](docs/DEVELOPMENT_PATH.md) — entry, evidence and exit contracts for the current delivery sequence; and
- [Reference Workflows](docs/REFERENCE_WORKFLOWS.md) — canonical accepted governance-boundary scenarios.

The accepted Constitution v0.2 and ADR-0009 define Symphony-K as a framework-neutral governance/control-plane product for agentic work. External agents, orchestrators and execution runtimes may determine how work is attempted; Symphony-K governs authoritative state, evidence, decisions, consequential Effects and reconstructable history.

## Current delivery status

| Stage | Name | Status |
| ---: | --- | --- |
| 0 | Constitution and Repository Harness | COMPLETE |
| 1 | Domain Kernel | COMPLETE — Human Exit ACCEPTED |
| G1 | Governance SDK / Facade | NEXT — NOT YET RELEASED |
| G2 | Trusted Evaluation and Evidence Integration | PLANNED |
| G3 | Governed Effect Gateway and Occurrence Reconciliation | PLANNED |
| G4 | Audit Export and Causal Reconstruction | PLANNED |
| G5 | Adversarial and Conformance Suite | PLANNED |
| G6 | External Agent / Orchestrator Integration | PLANNED |
| G7 | Reference Execution / Provider Path | PLANNED |
| G8 | End-to-End Operational Safety and Governance Recovery | PLANNED |
| G9 | Production Hardening and Release Engineering | PLANNED |
| G10 | v1 Acceptance and Final Delivery | PLANNED |

`NEXT — NOT YET RELEASED` is planning status only. It does not authorize implementation. G1 may be released only through a fresh durable implementation TaskSpec after exact R5 Human Acceptance and final strategic reconciliation.

Issue #79 remains **BLOCKED / NOT RELEASED** during the R5 gate. Its old Stage 2 M2 authority is obsolete for the post-transition product and is not the implementation TaskSpec for G1 or any other post-transition stage.

## Stage 0 — Constitution and Repository Harness

- **Status:** COMPLETE.
- **Historical capability:** repository authority hierarchy, constitutional invariants, ADR/Exec Plan process and repeatable repository workflow.
- **Current relevance:** Constitution v0.2 and accepted ADR-0009 now govern the post-transition product direction.

## Stage 1 — Domain Kernel

- **Status:** COMPLETE — Human Exit ACCEPTED.
- **Capability:** authoritative Objective, Task, Run, Outcome, Evaluation and Effect lifecycles; authority separation; immutable historical meaning; persistence; replay; optimistic concurrency; evidence/effective-use semantics.
- **Role after transition:** this is the product core rather than a precursor hidden beneath a complete orchestrator stack.
- **Accepted boundary:** `987f927905cadcedd473f2ba3270f56908b7f6b9` plus its durable Stage 1 acceptance lineage.

## G1 — Governance SDK / Facade

- **Status:** NEXT — NOT YET RELEASED.
- **Goal:** expose a stable bounded public integration surface over accepted Stage 1 semantics without requiring callers to understand the full internal semantic graph.
- **Required outcome:** external callers can submit claims/candidates/evidence, bind them to exact authoritative identities/versions and query governed results through one semantic authority model.
- **Initial implementation slice after R5:** public Python-facing facade; typed claim/candidate/evidence submission; exact identity/version binding; supported read/query surfaces; deterministic authority-bypass, stale/superseded/cross-entity, replay and concurrency tests.
- **Non-goals for the first slice:** new lifecycle semantics, real external Effect dispatch, generic Planner/Router ownership, Agent runtime ownership or sandbox-runtime ownership.
- **Deployment posture:** embedded-first; service/API and CLI surfaces may expose the same kernel later or in parallel without weaker semantics.
- **Exit proof:** public-contract tests demonstrate that the facade cannot bypass transition authority, evidence binding, replay or history rules.

## G2 — Trusted Evaluation and Evidence Integration

- **Status:** PLANNED.
- **Goal:** make independent Evaluation/evidence a production integration boundary rather than an experimental harness.
- **Required outcome:** exact candidate/entity/version/effective-use binding, stale/superseded/cross-entity rejection, independent evaluator identity/provenance and durable evidence references.
- **Exit proof:** adversarial stale/substitution/tamper cases fail closed while legal evidence-backed disposition succeeds.

## G3 — Governed Effect Gateway and Occurrence Reconciliation

- **Status:** PLANNED.
- **Goal:** govern consequential external actions across authorization, dispatch, receipts, occurrence uncertainty, reconciliation and remediation.
- **Required outcome:** request/prepare -> verify -> authorize -> dispatch/commit -> receipt/observe -> reconcile -> remediate/compensate; irreversible Effects retain exact Human authorization.
- **Critical proof:** external-success/local-recording crash windows and lost/ambiguous receipts cannot cause blind replay or false non-occurrence claims.

## G4 — Audit Export and Causal Reconstruction

- **Status:** PLANNED.
- **Goal:** make durable causal history consumable without direct database or private-source inspection.
- **Required outcome:** machine-readable provenance graph plus human-readable reconstruction covering claims, evidence, decisions, authority, Effects, occurrence, reconciliation and remediation.
- **Exit proof:** a fresh reviewer can reconstruct registered scenarios from exported records alone.

## G5 — Adversarial and Conformance Suite

- **Status:** PLANNED.
- **Goal:** turn authority/evidence/history/Effect guarantees into executable proof.
- **Required coverage:** self-authority, stale/superseded evidence, cross-entity substitution, replay/idempotency, concurrency, history-erasure attempts, unauthorized Effects, uncertain occurrence and compensation semantics.
- **Exit proof:** conformance results are reproducible and tied to exact product versions/configuration.

## G6 — External Agent / Orchestrator Integration

- **Status:** PLANNED.
- **Goal:** prove Symphony-K can govern a real external agent/orchestrator without owning its planning, routing or runtime loop.
- **Required outcome:** at least one supported integration provides stable attempt identity, claims, evidence hooks and governed Effect requests.
- **Exit proof:** no framework-specific semantics leak into the core governance model and the integration cannot self-promote authority.

## G7 — Reference Execution / Provider Path

- **Status:** PLANNED.
- **Goal:** prove the execution/provider boundary end to end with one reference path.
- **Required outcome:** an external or Symphony-K reference provider supplies isolation, provenance and execution observations sufficient for governance conformance.
- **Stage 2 asset reuse:** accepted ADR-0008 and the cumulative Stage 2 sandbox design at `77acfbdaf2bed6f0536873fafc8eb7a12599da83` remain valid provider/security/conformance assets. Owning a production sandbox runtime is not a v1 prerequisite.

## G8 — End-to-End Operational Safety and Governance Recovery

- **Status:** PLANNED.
- **Goal:** demonstrate that realistic success, failure, restart, stale evidence, conflict, uncertain Effect and recovery scenarios preserve constitutional truth.
- **Required outcome:** execution recovery may be external, while authoritative attempt lineage, evidence trust, occurrence uncertainty, reconciliation, compensation and Human resolution remain governed.
- **Exit proof:** accepted reference workflows and adverse branches preserve authority and reconstructable history.

## G9 — Production Hardening and Release Engineering

- **Status:** PLANNED.
- **Goal:** make the accepted v1 scope installable, observable, recoverable, upgradeable and reproducible within declared support limits.
- **Required outcome:** packaging, configuration validation, migrations, backup/restore, secrets boundary, observability, dependency/security gates, reproducible artifacts and operator runbooks.
- **Exit proof:** fresh install, restart, migration/rollback, backup/restore and security drills pass without release-blocking defects.

## G10 — v1 Acceptance and Final Delivery

- **Status:** PLANNED.
- **Goal:** independently demonstrate the accepted Product Contract and canonical workflows from repository documentation alone.
- **Required outcome:** frozen supported scope, acceptance matrix, known limitations, install/operator/contributor guides, architecture/security review and reproducible candidate artifacts.
- **Exit proof:** all required product-contract obligations and accepted reference workflows are independently accepted; no release-blocking constitutional/security defect remains.

Release/tag publication remains a separate remote Effect requiring explicit Human authorization.

## Historical pre-transition delivery map

The following stages were part of the previously accepted full-orchestrator roadmap. They are preserved here as historical planning provenance, not as current v1 prerequisites or active authority:

- Stage 2 — Sandbox Execution;
- Stage 3 — First AgentDriver;
- Stage 4 — Verification Plane;
- Stage 5 — Failure and Recovery;
- Stage 6 — Budget, Risk, Permission, and Effects;
- Stage 7 — Second Agent and Architecture Test;
- Stage 8 — Router and Escalation;
- Stage 9 — Planner;
- Stage 10 — Learning and Reputation;
- Stage 11 — Application Control Plane and Human Governance Surface;
- Stage 12 — End-to-End Integration and Operational Safety;
- Stage 13 — Production Hardening and Release Engineering;
- Stage 14 — v1.0 Release Candidate and Final Delivery.

Their historical Exec Plans, ADRs, accepted designs and Git history remain attributable. Generic Planner, Router, learned routing/reputation, multiple complete Agent runtimes and production sandbox ownership may return as optional/reference/post-v1 capabilities through later bounded decisions; they are not mandatory v1 release blockers.

## Stage 2 historical disposition

ADR-0008 and the Human Accepted Stage 2 M1/M1C technical design remain valid. Their current role is an execution-provider security/conformance contract, an evidence/provenance boundary and an optional/reference implementation path.

The historical Stage 2 runtime implementation path is superseded for current delivery sequencing. Runtime code was never started. Issue #79 remains BLOCKED / NOT RELEASED during R5 and cannot be reused or silently revised into the first post-transition implementation task. After accepted R5 final reconciliation it may be marked SUPERSEDED / NOT RELEASED or closed as not planned; future reuse of the technical design requires a new TaskSpec.

## Post-v1 / optional backlog

Non-blocking candidates include:

- Symphony-K-owned generic Planner or Router modules;
- learned routing/reputation;
- additional Agent runtimes and specialized adapters;
- additional sandbox providers, remote sandboxes or microVMs;
- distributed/HA control-plane deployment;
- richer governance UI and organization/multi-tenant controls;
- GPU/local-model resource pools and advanced scheduling; and
- broader policy analytics or external tracker ecosystems.
