# Project Status

## Accepted baseline

- **Project:** Symphony-K; **maturity:** pre-v1 development
- **Completed implementation stages:** Stage 0, Stage 1
- **Stage 1:** **COMPLETE**; final accepted implementation/governance boundary `987f927905cadcedd473f2ba3270f56908b7f6b9`.
- **Current accepted constitutional baseline:** Constitution v0.2 + ADR-0009, accepted at exact R1 head `9c842f18ffcdd51daef8f05d9367f571df677703`.
- **Accepted R2 product definition:** exact head `2b54c2672c0c400aab1f35e0245c8c4e97a62321`; independent review **ACCEPT** `5711134872`; Human acceptance `5711951534`.
- **Accepted R3 delivery path:** exact head `f467fd75071e5d0252719539cf7323fb71de587c`; independent review **ACCEPT** `5712008632`; Human acceptance `5712045668`.
- **Accepted R4 workflow/cold-start reconciliation:** exact head `ecccbedd68f2f0e0eff949c20b627f250ddf189e`; independent review **ACCEPT** `5712098419`; Human acceptance `5712165121`; R4A acceptance reconciliation `51137a3549388b61abfcbcbd5d70c6ec66101dae` reviewed **ACCEPT** on Issue #97 comment `5712179640`.
- **Stage 2 M1/M1C technical design:** **HUMAN ACCEPTED** at `77acfbdaf2bed6f0536873fafc8eb7a12599da83`; ADR-0008 remains **ACCEPTED**.
- Stage 2 runtime code is **NOT STARTED** and runtime isolation evidence is **NOT ESTABLISHED**.

## Current product truth

Symphony-K is a **framework-neutral governance/control-plane system for agentic work**.

External agents, orchestrators and runtimes may determine how work is attempted. Symphony-K governs authoritative state/claims, exact evidence and Evaluation, consequential Effects, occurrence uncertainty/reconciliation and durable causal history.

The accepted v1 critical path is:

```text
Stage 1 governance kernel
-> governance SDK/facade
-> trusted Evaluation/evidence integration
-> governed Effect gateway + occurrence reconciliation
-> durable audit export/reconstruction
-> adversarial/conformance suite
-> external agent/orchestrator integration
-> reference execution/provider path
-> end-to-end governance safety/recovery
-> production hardening
-> v1 acceptance
```

A generic Planner, generic Router, learned routing/reputation, multiple complete Agent runtimes and ownership of a production sandbox runtime are not mandatory v1 release blockers.

## Current governance work

- **R1 architecture/constitution:** COMPLETE AND HUMAN ACCEPTED.
- **R2 product definition:** COMPLETE AND HUMAN ACCEPTED.
- **R3 delivery path:** COMPLETE AND HUMAN ACCEPTED.
- **R4 workflow/cold-start reconciliation:** COMPLETE AND HUMAN ACCEPTED.
- **R5 final strategic disposition/release boundary:** current bounded candidate work under Issue #98. R5 finalizes the obsolete old Stage 2/#79 execution path and defines the release boundary for the first post-transition implementation slice.
- **R5 acceptance status:** PENDING independent review and explicit Human acceptance. Repository-level strategic reconciliation is not COMPLETE until that exact gate passes and final acceptance reconciliation is persisted.

## Stage 2 / Issue #79 disposition

- ADR-0008 and accepted Stage 2 M1/M1C design remain valid execution-provider security/conformance assets and an optional/reference implementation path.
- The old Stage 2 runtime-first v1 sequencing is superseded by accepted R3.
- Issue #79 remains **BLOCKED / NOT RELEASED** during R5 candidate/review.
- Its old r2/r3 execution authority is obsolete for the post-transition product and MUST NOT be revived or repurposed as G1 authority.
- After exact R5 Human Acceptance and final reconciliation, #79 may be durably marked **SUPERSEDED / NOT RELEASED** or closed as not planned; it MUST NOT be changed to READY.
- Future reference-provider implementation may reuse ADR-0008/M1/M1C only through a fresh bounded TaskSpec.

## Post-transition implementation release boundary

The first intended implementation slice is **G1 — Governance SDK / Facade Foundation**.

R5 candidate work does **not** release G1. A new durable implementation TaskSpec may be released only after exact R5 Human Acceptance and final reconciliation. That future TaskSpec must provide an exact baseline, file/test scope, milestones and execution authority.

The intended G1 foundation includes a public Python-facing governance facade, typed external claim/candidate/evidence submission, exact entity/version binding, supported read/query surfaces, and deterministic authority/evidence/replay/concurrency tests. It adds no lifecycle semantics and performs no real external Effect dispatch.

## Strategic lineage

- #85/#86 — falsification evidence and corrected independent ACCEPT.
- #87 — explicit Human strategic approval.
- #89/#90/#91 — R1 ADR-0009 + Constitution v0.2 acceptance and reconciliation.
- #92/#93 — R2 product-definition acceptance and reconciliation.
- #94/#95 — R3 delivery-path acceptance and reconciliation.
- #96/#97 — R4 workflow/cold-start acceptance and reconciliation.
- #98 — R5 final disposition/release-boundary candidate.

## Next action

Independently review the exact R5 candidate and obtain explicit Human acceptance. Until that occurs and final reconciliation is persisted, #79 remains BLOCKED / NOT RELEASED and G1 remains NOT RELEASED.

## Navigation / cold-start reading order

1. [CONSTITUTION.md](CONSTITUTION.md)
2. this file
3. [AGENTS.md](AGENTS.md)
4. [VISION.md](VISION.md)
5. [ARCHITECTURE.md](ARCHITECTURE.md)
6. [docs/V1_PRODUCT_CONTRACT.md](docs/V1_PRODUCT_CONTRACT.md)
7. [ROADMAP.md](ROADMAP.md)
8. [docs/DEVELOPMENT_PATH.md](docs/DEVELOPMENT_PATH.md)
9. [docs/REFERENCE_WORKFLOWS.md](docs/REFERENCE_WORKFLOWS.md)
10. relevant core beliefs, accepted ADRs/designs
11. [docs/AI_HANDOFF.md](docs/AI_HANDOFF.md)
12. the concrete current TaskSpec

Historical accepted artifacts remain historical truth but do not override the current accepted Constitution, ADR-0009, product definition, delivery path or explicit TaskSpec readiness.
