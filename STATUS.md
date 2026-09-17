# Project Status

## Accepted baseline

- **Project:** Symphony-K; **maturity:** pre-v1 development
- **Completed implementation stages:** Stage 0, Stage 1
- **Stage 1:** **COMPLETE**; final accepted implementation/governance boundary `987f927905cadcedd473f2ba3270f56908b7f6b9`.
- **Current accepted constitutional baseline:** Constitution v0.2 + ADR-0009, accepted at exact R1 head `9c842f18ffcdd51daef8f05d9367f571df677703`.
- **Accepted R2 product definition:** exact head `2b54c2672c0c400aab1f35e0245c8c4e97a62321`; independent review **ACCEPT** `5711134872`; Human acceptance `5711951534`.
- **Accepted R3 delivery path:** exact head `f467fd75071e5d0252719539cf7323fb71de587c`; independent review **ACCEPT** `5712008632`; Human acceptance `5712045668`.
- **Accepted R4 workflow/cold-start reconciliation:** exact head `ecccbedd68f2f0e0eff949c20b627f250ddf189e`; independent review **ACCEPT** `5712098419`; Human acceptance `5712165121`; R4A reconciliation `51137a3549388b61abfcbcbd5d70c6ec66101dae` reviewed **ACCEPT** on Issue #97 comment `5712179640`.
- **Accepted R5 final strategic disposition / release boundary:** exact head `1bb48657a85d746b8d0023ddd805c6cdc09703b0`; independent review **ACCEPT** on Issue #98 comment `5712222234`; final Human acceptance on Issue #98 comment `5712330240`.
- **Final strategic reconciliation commit:** `b5ee78f7febae1346c771fa6060fcb3e18ea56f3`, independently **ACCEPTED** on Issue #99 comment `5712355215`.
- **Stage 2 M1/M1C technical design:** **HUMAN ACCEPTED** at `77acfbdaf2bed6f0536873fafc8eb7a12599da83`; ADR-0008 remains **ACCEPTED**.
- Stage 2 runtime code is **NOT STARTED** and runtime isolation evidence is **NOT ESTABLISHED**.

## Strategic transition status

**Repository-level strategic transition R1–R5: COMPLETE AND HUMAN ACCEPTED.**

Symphony-K is a **framework-neutral governance/control-plane system for agentic work**. External agents, orchestrators and runtimes may determine how work is attempted. Symphony-K governs authoritative state/claims, exact evidence and Evaluation, consequential Effects, occurrence uncertainty/reconciliation and durable causal history.

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

## Legacy Stage 2 / Issue #79 disposition

- ADR-0008 and accepted Stage 2 M1/M1C design remain valid execution-provider security/conformance assets and an optional/reference implementation path.
- The old Stage 2 runtime-first v1 sequencing is superseded as current delivery authority.
- Issue #79 is **SUPERSEDED / NOT RELEASED**, closed as `not planned`, with durable supersession comment `5712361531`.
- Its old r2/r3 execution authority is historical only and MUST NOT be revived or repurposed as G1 authority.
- Future reference-provider implementation may reuse ADR-0008/M1/M1C only through a fresh bounded TaskSpec.

## Current implementation work

The first post-transition implementation slice is **G1 / M1 — Governance SDK / Facade Foundation**.

- Current executable TaskSpec identity: **Issue #100**.
- The **current Issue #100 body** is authoritative for its TaskSpec revision, execution readiness, exact launch HEAD, allowed paths, validation and remote-mutation boundary.
- Repository roadmap/status text MUST NOT be used to infer or override a different Issue #100 launch SHA.
- G1 implementation has **NOT STARTED OR COMPLETED merely because Issue #100 is released**.

The bounded G1/M1 product intent is a public Python-facing governance facade, typed external claim/candidate/evidence submission, exact entity/version binding, supported read/query surfaces, and deterministic authority/evidence/replay/concurrency tests. It adds no lifecycle semantics and performs no real external Effect dispatch.

## Strategic lineage

- #85/#86 — falsification evidence and corrected independent ACCEPT.
- #87 — explicit Human strategic approval.
- #89/#90/#91 — R1 ADR-0009 + Constitution v0.2 acceptance and reconciliation.
- #92/#93 — R2 product-definition acceptance and reconciliation.
- #94/#95 — R3 delivery-path acceptance and reconciliation.
- #96/#97 — R4 workflow/cold-start acceptance and reconciliation.
- #98 — R5 final disposition, independent ACCEPT and final Human Acceptance.
- #99 — R5A final accepted-truth reconciliation, independent ACCEPT.
- #79 — closed SUPERSEDED / NOT RELEASED, historical only.
- #100 — current G1/M1 implementation TaskSpec identity; current body controls release details.
- #101 — post-transition cold-start handoff reconciliation.

## Next action

Freshly read Issue #100 and execute only its current released revision from the exact launch HEAD stated in that Issue. After a candidate is produced, independently review it and reconcile acceptance before broader G1 or G2 work is released.

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
12. Issue #100, the current executable TaskSpec identity

Historical accepted artifacts remain historical truth but do not override the current accepted Constitution, ADR-0009, product definition, delivery path or explicit TaskSpec readiness.
