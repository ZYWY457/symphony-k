# Roadmap

This is the canonical high-level delivery map for Symphony-K v1 after the accepted strategic transition.

Read with:

- [v1 Product Contract](docs/V1_PRODUCT_CONTRACT.md) — observable v1 scope and final acceptance expectations;
- [Development Path](docs/DEVELOPMENT_PATH.md) — entry, evidence and exit contracts for the current delivery sequence;
- [G2 planned parent plan](docs/exec-plans/planned/g2-trusted-evaluation-evidence.md) — current planning-only decomposition of trusted Evaluation/evidence integration; and
- [Reference Workflows](docs/REFERENCE_WORKFLOWS.md) — canonical accepted governance-boundary scenarios.

The accepted Constitution v0.2 and ADR-0009 define Symphony-K as a framework-neutral governance/control-plane product for agentic work. External agents, orchestrators and execution runtimes may determine how work is attempted; Symphony-K governs authoritative state, evidence, decisions, consequential Effects and reconstructable history.

## Current delivery status

| Stage | Name | Status |
| ---: | --- | --- |
| 0 | Constitution and Repository Harness | COMPLETE |
| 1 | Domain Kernel | COMPLETE — Human Exit ACCEPTED |
| G1 | Governance SDK / Facade | COMPLETE / ACCEPTED — M1 at `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1` |
| G2 | Trusted Evaluation and Evidence Integration | PLANNED / NOT RELEASED — path planning via Issue #104 |
| G3 | Governed Effect Gateway and Occurrence Reconciliation | PLANNED |
| G4 | Audit Export and Causal Reconstruction | PLANNED |
| G5 | Adversarial and Conformance Suite | PLANNED |
| G6 | External Agent / Orchestrator Integration | PLANNED |
| G7 | Reference Execution / Provider Path | PLANNED |
| G8 | End-to-End Operational Safety and Governance Recovery | PLANNED |
| G9 | Production Hardening and Release Engineering | PLANNED |
| G10 | v1 Acceptance and Final Delivery | PLANNED |

G1/M1 accepted implementation lineage is preserved through Issue #100 and Issue #102. The original Issue #100 candidate `36cb145fa666fa9a2218028d2d3828f28c0ed352` was not accepted; Issue #102 carried the forward trusted-boundary and exact-version corrections; final candidate `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1` was independently accepted on comment `5714651540`. Accepted-truth reconciliation is `eaea5390a088a71fe4108c2b84812253032a287a`.

Issue #79 is **SUPERSEDED / NOT RELEASED**, closed as not planned, and is historical only. Its old Stage 2 M2 authority is obsolete for the post-transition product and is not an implementation TaskSpec for any current stage.

## Stage 0 — Constitution and Repository Harness

- **Status:** COMPLETE.
- **Historical capability:** repository authority hierarchy, constitutional invariants, ADR/Exec Plan process and repeatable repository workflow.
- **Current relevance:** Constitution v0.2 and accepted ADR-0009 govern the post-transition product direction.

## Stage 1 — Domain Kernel

- **Status:** COMPLETE — Human Exit ACCEPTED.
- **Capability:** authoritative Objective, Task, Run, Outcome, Evaluation and Effect lifecycles; authority separation; immutable historical meaning; persistence; replay; optimistic concurrency; evidence/effective-use semantics.
- **Role after transition:** this is the product core rather than a precursor hidden beneath a complete orchestrator stack.
- **Accepted boundary:** `987f927905cadcedd473f2ba3270f56908b7f6b9` plus its durable Stage 1 acceptance lineage.

## G1 — Governance SDK / Facade

- **Status:** COMPLETE / ACCEPTED.
- **Accepted implementation boundary:** `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`.
- **Acceptance evidence:** Issue #102 independent acceptance review comment `5714651540`.
- **Goal achieved:** a stable bounded public integration surface over accepted Stage 1 semantics without requiring callers to construct trusted internal authority/context objects.
- **Accepted capabilities:** typed exact references for Objective/Task/Run/Outcome/Evaluation/Effect; caller-controlled claim/candidate/evidence DTOs; injected trusted binder for Stage 1 request/context construction; supported Run/Outcome/Evaluation mutation paths; exact/current reads; caller-safe errors; stale/superseded/cross-entity and exact-lineage rejection; replay/idempotency and optimistic-concurrency preservation; explicit unsupported real Effect dispatch.
- **Preserved authority boundary:** no public Run completion or Outcome acceptance operation; no caller-supplied trusted Stage 1 context; no new lifecycle semantics.
- **Historical correction lineage:** Issue #100 initial candidate remained NOT ACCEPTED; Issue #102 carried the accepted forward correction rather than rewriting history.

## G2 — Trusted Evaluation and Evidence Integration

- **Status:** PLANNED / NOT RELEASED.
- **Planning authority:** Issue #104; parent path at [`docs/exec-plans/planned/g2-trusted-evaluation-evidence.md`](docs/exec-plans/planned/g2-trusted-evaluation-evidence.md).
- **Entry criteria for implementation:** accepted G1 facade plus a fresh milestone-specific durable TaskSpec that explicitly releases implementation from an exact baseline. Issue #104 and the parent plan do not release code mutation.
- **Goal:** make independent Evaluation/evidence a supported trusted integration boundary rather than a caller-supplied assertion or private-history exercise.
- **Core sequence:** evidence provenance -> trusted evaluator assignment -> exact Evaluation result intake -> authoritative effective-use resolution -> evidence-backed Outcome disposition -> stage acceptance/reconciliation.
- **Required outcome:** exact candidate/entity/version/method/policy binding; durable evidence provenance; evaluator identity/assignment provenance; stale/superseded/cross-entity/tamper rejection; authoritative conflict/arbitration/invalidation-aware effective-use resolution; policy-separated Outcome disposition.
- **Exit proof:** legal evidence-backed disposition succeeds while fabricated evaluator, stale/tampered/substituted evidence, omitted history, stale effective-use, policy substitution and replayed authority fail closed.
- **Non-goals:** universal judge/evidence taxonomy, full authentication product, new Stage 1 lifecycle/core entity, real Effect dispatch, provider/sandbox runtime, G4 audit export or G5 cross-stage conformance framework.

### G2 planned milestone path

| Milestone | Name | Exit focus | Release state |
| --- | --- | --- | --- |
| M0 | Contract and threat-boundary freeze | reviewed trust/data-flow contract + adversarial matrix | PLANNED / NOT RELEASED |
| M1 | Durable evidence provenance intake | immutable/stable provenance, exact scope and tamper/substitution negatives | PLANNED / NOT RELEASED |
| M2 | Trusted evaluator identity and assignment binding | no caller-fabricated evaluator/independence/assignment authority | PLANNED / NOT RELEASED |
| M3 | Trusted Evaluation execution/result intake | exact target/method/evidence/principal binding through Stage 1 lifecycle authority | PLANNED / NOT RELEASED |
| M4 | Durable effective-use resolver/query | authoritative complete current history, conflict/arbitration/invalidation aware | PLANNED / NOT RELEASED |
| M5 | Evidence-backed Outcome disposition bridge | effective use + policy + required Human input -> existing Stage 1 disposition | PLANNED / NOT RELEASED |
| M6 | Stage acceptance and reconciliation | adversarial review + durable accepted-truth reconciliation | PLANNED / NOT RELEASED |

Roadmap order, Issue #104, and the existence of this plan do not authorize any G2 implementation milestone.

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

The historical Stage 2 runtime implementation path is superseded for current delivery sequencing. Runtime code was never started. Issue #79 is closed **SUPERSEDED / NOT RELEASED** as not planned and cannot be reused or silently revised into a post-transition implementation task. Future reuse of the technical design requires a fresh TaskSpec, normally under G7 reference execution/provider work.

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
