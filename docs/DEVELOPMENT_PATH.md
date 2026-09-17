# Symphony-K Development Path

This document is the authoritative delivery contract from the accepted Stage 1 governance kernel through v1.0 after the strategic transition.

[ROADMAP.md](../ROADMAP.md) is the compact delivery map. Parent Exec Plans and bounded TaskSpecs provide the next level of detail. No stage is executable merely because it is listed here.

The accepted Constitution v0.2, ADR-0009 and R2 Product Contract define the current product boundary: Symphony-K governs authoritative claims/state, trusted evidence and Evaluation, consequential Effects and reconstructable history while external agents, orchestrators and execution runtimes may determine how work is attempted.

Strategic transition R1-R5 is COMPLETE AND HUMAN ACCEPTED. Final strategic accepted-truth reconciliation is `b5ee78f7febae1346c771fa6060fcb3e18ea56f3`.

## Current dependency graph

```text
Stage 0 repository/constitutional harness — COMPLETE
   -> Stage 1 governance Domain Kernel — COMPLETE
      -> G1 governance SDK/facade — COMPLETE / ACCEPTED
         -> G2 trusted Evaluation/evidence integration — PLANNED / NOT RELEASED
            -> G3 governed Effect gateway + occurrence reconciliation
               -> G4 audit export / causal reconstruction
                  -> G5 adversarial + conformance suite
                     -> G6 external agent/orchestrator integration
                        -> G7 reference execution/provider path
                           -> G8 end-to-end operational safety / governance recovery
                              -> G9 production hardening
                                 -> G10 v1 acceptance
```

This is the current v1 critical path. The historical Stage 2–14 full-orchestrator sequence is no longer a mandatory dependency chain.

## General stage rules

Every new stage requires:

1. a durable parent plan or equivalent bounded design contract;
2. exact entry baseline and protected-path scope;
3. independent review of architecture/security/trust-sensitive changes;
4. explicit Human acceptance where the stage changes product/architecture/governance commitments;
5. reproducible evidence for stated guarantees; and
6. durable status reconciliation before dependent work is released.

No stage may infer authority from roadmap order alone. The current TaskSpec body controls readiness and exact launch baseline.

## Stage 0 — Constitution and Repository Harness

- **Status:** COMPLETE.
- **Purpose:** establish authority hierarchy, constitutional invariants, ADR/Exec Plan process and cold-start repository continuity.
- **Current significance:** Constitution v0.2 is the accepted constitutional baseline.

## Stage 1 — Governance Domain Kernel

- **Status:** COMPLETE — Human Exit ACCEPTED.
- **Purpose:** provide the authoritative state/evidence/history semantics every later surface must obey.
- **Required accepted capabilities:** Objective, Task, Run, Outcome, Evaluation and Effect separation; lifecycle authority; immutable historical meaning; persistence; exact replay; optimistic concurrency; evidence/effective-use semantics.
- **Exit evidence:** 99/99 lifecycle coverage and accepted Stage 1 Human Exit review.
- **Current significance:** product core, not merely a precursor to an owned orchestrator runtime.

## G1 — Governance SDK / Facade

- **Status:** COMPLETE / ACCEPTED.
- **Accepted implementation boundary:** `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`.
- **Acceptance evidence:** Issue #102 independent acceptance review comment `5714651540`.
- **Historical lineage:** Issue #100 initial candidate `36cb145fa666fa9a2218028d2d3828f28c0ed352` was NOT ACCEPTED; Issue #102 carried the forward trusted-boundary and exact-version corrections.
- **Purpose achieved:** provide a bounded stable public integration surface over accepted governance semantics.
- **Accepted deliverables:** typed exact refs for Objective/Task/Run/Outcome/Evaluation/Effect; caller-controlled external submission DTOs; injected trusted binder for Stage 1 request/context construction; supported Run/Outcome/Evaluation mutation paths; exact/current reads; caller-safe errors; exact identity/version and lineage binding; stale/superseded/cross-entity rejection; replay/idempotency and optimistic-concurrency preservation; explicit unsupported real Effect dispatch.
- **Preserved non-goals:** no new lifecycle semantics, no public Run completion or Outcome acceptance, no real external Effect dispatch, no generic Planner/Router, no Agent runtime or sandbox-runtime ownership, and no G2 trust-policy semantics.
- **Exit criterion:** satisfied by accepted implementation plus independent review; durable reconciliation is carried by Issue #103.

## G2 — Trusted Evaluation and Evidence Integration

- **Status:** PLANNED / NOT RELEASED.
- **Entry criteria:** accepted G1 facade and a fresh released G2 TaskSpec with exact baseline and bounded scope.
- **Purpose:** bind external/independent verification to exact authoritative candidates and effective-use state.
- **Required deliverables:** trusted evaluator/evidence identities; exact entity/candidate/version binding; evidence provenance; stale/superseded/invalidation handling; cross-entity substitution rejection; durable effective-use references.
- **Non-goals:** universal semantic judge, Worker self-validation, provider-specific core semantics.
- **Minimum evidence:** stale, superseded, tampered, unrelated and substituted evidence fail closed; legal current evidence supports disposition.
- **Exit criterion:** authoritative decisions can depend on independent external evidence without weakening Stage 1 trust rules.
- **Authority note:** G2 is not executable until its own fresh TaskSpec is explicitly released.

## G3 — Governed Effect Gateway and Occurrence Reconciliation

- **Status:** PLANNED.
- **Entry criteria:** G1/G2 accepted and Effect gateway design approved.
- **Purpose:** govern consequential external actions across the trusted boundary.
- **Required deliverables:** Effect request/prepare, verification, authorization, dispatch/commit, receipt/observation, occurrence status, uncertainty/quarantine, idempotency, reconciliation, remediation and compensation; exact Human authorization where constitutionally required.
- **Non-goals:** Worker-held unrestricted production credentials, retroactive authorization, treating dispatch failure as proof of non-occurrence.
- **Minimum evidence:** duplicate dispatch, lost receipt, external-success/local-recording crash, unauthorized observed occurrence, reconciliation and compensation scenarios.
- **Exit criterion:** uncertain occurrence cannot be blindly replayed and confirmed occurrence cannot be erased or falsified.

## G4 — Audit Export and Causal Reconstruction

- **Status:** PLANNED.
- **Entry criteria:** durable G1–G3 authoritative/integration records exist.
- **Purpose:** export complete attributable causal history without private database/source inspection.
- **Required deliverables:** machine-readable provenance graph, human-readable narrative, stable record references, redaction/export policy and deterministic reconstruction.
- **Minimum evidence:** blind reviewer reconstructs registered authority/evidence/Effect scenarios from export alone.
- **Exit criterion:** consequential decisions/actions are explainable from durable public audit artifacts.

## G5 — Adversarial and Conformance Suite

- **Status:** PLANNED.
- **Entry criteria:** stable public governance/evidence/Effect/audit contracts.
- **Purpose:** encode Symphony-K guarantees as executable conformance evidence.
- **Required deliverables:** test harness and result format covering authority separation, stale/superseded evidence, cross-entity substitution, replay/idempotency, concurrency, history erasure, Effect authorization/occurrence uncertainty and compensation.
- **Minimum evidence:** deterministic legal and adversarial matrices with exact version/configuration attribution.
- **Exit criterion:** claimed guarantees are independently reproducible rather than documentation-only assertions.

## G6 — External Agent / Orchestrator Integration

- **Status:** PLANNED.
- **Entry criteria:** G1–G5 accepted; one integration target selected by bounded decision.
- **Purpose:** prove framework-neutral governance over an external system that owns how work is attempted.
- **Required deliverables:** adapter/integration mapping attempt identity, claims, candidate outputs, evidence hooks and Effect requests into stable Symphony-K contracts.
- **Non-goals:** moving framework-specific agent semantics into the core, making the external orchestrator authoritative.
- **Exit criterion:** end-to-end governed work succeeds and adversarial integration cases cannot bypass authority/evidence/Effect rules.

## G7 — Reference Execution / Provider Path

- **Status:** PLANNED.
- **Entry criteria:** provider/conformance contract selected; accepted ADR-0008/Stage 2 design reused where applicable.
- **Purpose:** prove one execution path can provide sufficient isolation, identity, provenance and observations for governance.
- **Required deliverables:** reference provider or external provider adapter, conformance mapping, evidence/provenance binding and operational diagnostics.
- **Historical asset:** Stage 2 M1/M1C sandbox design at `77acfbdaf2bed6f0536873fafc8eb7a12599da83` remains valid as a security/conformance boundary.
- **Non-goals:** requiring Symphony-K to own the production sandbox runtime or complete the old Stage 2 M2–M4 path.
- **Exit criterion:** one reference execution/provider path proves the accepted boundary end to end.

## G8 — End-to-End Operational Safety and Governance Recovery

- **Status:** PLANNED.
- **Entry criteria:** G1–G7 accepted and canonical reference workflows stable.
- **Purpose:** prove authority/history safety across realistic failure and recovery conditions.
- **Required deliverables:** end-to-end scenario matrix, restart/reopen, failure injection, uncertain Effect recovery, compensation, Human escalation, correlation/observability and runbooks.
- **Non-goals:** requiring Symphony-K to own generic workflow retry/scheduling engines.
- **Exit criterion:** execution recovery may be external while authoritative attempt/evidence/Effect history remains correct and reconstructable.

## G9 — Production Hardening and Release Engineering

- **Status:** PLANNED.
- **Entry criteria:** supported end-to-end product path accepted.
- **Purpose:** make v1 deployable and operable within declared support limits.
- **Required deliverables:** packaging/install, configuration validation, migrations, backup/restore, secrets boundary, logging/metrics, security/dependency gates, reproducible artifacts and operator documentation.
- **Exit criterion:** fresh install, restart, backup/restore, upgrade/rollback and security drills pass without release-blocking defects.

## G10 — v1 Acceptance and Final Delivery

- **Status:** PLANNED.
- **Entry criteria:** G1–G9 complete; Product Contract and canonical workflows stable.
- **Purpose:** independently demonstrate the complete accepted v1 product.
- **Required deliverables:** acceptance matrix, known limitations, architecture/security review, install/operator/contributor guides, examples and reproducible release-candidate artifacts.
- **Exit criterion:** a fresh maintainer can install, operate, inspect and reproduce the accepted product from repository documentation alone; all required Product Contract/workflow cases pass.

Publication of a tag/release is a separate remote Effect requiring explicit Human authorization.

## Historical Stage 2 sandbox plan disposition

The historical Stage 2 parent and accepted technical design remain durable provenance. ADR-0008 and the cumulative M1/M1C design are not rejected or rewritten.

Their post-transition role is an execution-provider security/conformance contract, an optional/reference implementation path and a source of evidence/provenance requirements for G7.

The old Stage 2 runtime implementation path is superseded for current v1 sequencing. Runtime code was not started. Issue #79 is closed **SUPERSEDED / NOT RELEASED** as not planned; its old r2/r3 execution authority is historical only and must never be re-released in place as post-transition implementation authority.

## Historical pre-transition stages

The former Stage 2–14 chain (Sandbox -> AgentDriver -> Verification -> Recovery -> Effects -> second Agent -> Router -> Planner -> Learning -> application control plane -> E2E -> hardening -> release) is historical planning provenance only.

Completed or accepted historical artifacts keep their original truth. Planned stages do not become implemented, rejected technical work is not erased, and optional future Planner/Router/Learning/runtime work requires new bounded authority if revisited.
