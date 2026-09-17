# Project Status

## Accepted baseline

- **Project:** Symphony-K; **maturity:** pre-v1 development
- **Completed stages:** Stage 0, Stage 1
- **Stage 1:** **COMPLETE**; the final accepted implementation/governance boundary is `987f927905cadcedd473f2ba3270f56908b7f6b9`, with Human Exit acceptance recorded by GitHub Issue #75 and its ordered governance commits.
- **Latest accepted stage:** Stage 1 — Domain Kernel
- **Current accepted constitutional baseline:** `constitution-v0.2`, accepted with ADR-0009 at exact head `9c842f18ffcdd51daef8f05d9367f571df677703` after independent technical re-review **ACCEPT** on Issue #89 comment `5711016301` and explicit Human **APPROVED / ACCEPTED** on Issue #89 comment `5711029647`.
- **ADR-0009:** **ACCEPTED** — Framework-Neutral Agent Governance Kernel and External Execution Boundary.
- **Accepted R2 product definition:** `VISION.md`, `ARCHITECTURE.md`, `docs/V1_PRODUCT_CONTRACT.md` and root `README.md` at exact head `2b54c2672c0c400aab1f35e0245c8c4e97a62321`, after independent review **ACCEPT** on Issue #92 comment `5711134872` and explicit Human acceptance on Issue #92 comment `5711951534`.
- **Accepted R3 delivery path:** `ROADMAP.md`, `docs/DEVELOPMENT_PATH.md`, `docs/exec-plans/active/stage-02-sandbox-execution.md` and `STATUS.md` at exact head `f467fd75071e5d0252719539cf7323fb71de587c`, after independent review **ACCEPT** on Issue #94 comment `5712008632` and explicit Human acceptance on Issue #94 comment `5712045668`.
- **Stage 2 M1 architecture/design:** **HUMAN ACCEPTED**. ADR-0008 remains **ACCEPTED** and technically unchanged. The cumulative accepted sandbox design baseline remains `77acfbdaf2bed6f0536873fafc8eb7a12599da83` (`docs(architecture): clarify unknown frozen salvage collection`).
- Stage 2 runtime isolation evidence is **NOT YET ESTABLISHED** and runtime implementation is **NOT YET STARTED**.

## Current governance status

- **Human strategic decision:** the framework-neutral governance/control-plane transition was explicitly **APPROVED** on Issue #87 comment `5710053258`.
- **Strategic validation:** Issue #85 initial experiment -> independent **REQUEST CHANGES** -> Issue #86 correction -> independent **ACCEPT** comment `5709520565`; registered A/B/C/D/E gates passed. This evidence supported the later Human strategic decision; it was not itself product approval.
- **R1 architecture/constitution:** **COMPLETE AND HUMAN ACCEPTED**. Constitution v0.2 and ADR-0009 are current accepted governance truth.
- **R2 product definition:** **COMPLETE AND HUMAN ACCEPTED** at exact head `2b54c2672c0c400aab1f35e0245c8c4e97a62321`.
- **R2 acceptance reconciliation:** published as `771ad9bfc64ab43e624300ffffd9474eef560e77`, with independent governance review **ACCEPT** on Issue #93 comment `5711974055`.
- **R3 delivery path:** **COMPLETE AND HUMAN ACCEPTED** at exact head `f467fd75071e5d0252719539cf7323fb71de587c` after independent Delivery-Plan Review **ACCEPT** on Issue #94 comment `5712008632` and explicit Human acceptance on comment `5712045668`.
- **Current governance work:** R4 workflow/cold-start reconciliation is next. `docs/REFERENCE_WORKFLOWS.md`, `AGENTS.md`, `docs/AI_HANDOFF.md`, `docs/README.md`, `docs/adr/README.md` and materially stale navigation/index wording must be reconciled so a cold-start maintainer sees the accepted governance/control-plane model without reconstructing the transition from chat or old delivery assumptions.
- **Implementation hold:** Issue #79 remains **BLOCKED / NOT RELEASED**. R1-R3 acceptance does not authorize production implementation restart.

## Stage 2 historical technical status

- **Accepted technical asset:** ADR-0008 + cumulative Stage 2 M1/M1C design at `77acfbdaf2bed6f0536873fafc8eb7a12599da83`.
- **Historical pre-erratum accepted baseline:** `b52df98530d8ce742b07d7f6c399ccd5b54e643b`.
- **M1C acceptance:** independent technical review **ACCEPT** on Issue #83 comment `5706630764`; explicit Human erratum approval **APPROVED** on comment `5706652702`.
- **Runtime isolation evidence:** **NOT YET ESTABLISHED**.
- **Runtime code:** **NOT YET STARTED**.
- **Issue #79:** `r3 - stage-02-m2-blocked-after-unknown-collection-stop`, **BLOCKED / NOT RELEASED**.
- **Accepted R3 delivery disposition:** retain the accepted Stage 2 design as an execution-provider security/conformance and optional/reference asset while superseding the old runtime-first delivery sequencing. The old M2 path remains blocked and is not the first post-transition implementation task.

## Dispatch / review queue

- **R1 lineage:** Issue #87 Human strategic approval -> Issue #89 R1 candidate -> REQUEST CHANGES `5710385425` -> Issue #90 R1C -> corrected head `9c842f18...` -> independent technical re-review **ACCEPT** `5711016301` -> explicit Human R1 acceptance `5711029647` -> Issue #91 acceptance reconciliation.
- **R2 lineage:** Issue #92 candidate `2b54c267...` -> independent Product-Definition Review **ACCEPT** `5711134872` -> explicit Human R2 acceptance `5711951534` -> Issue #93 acceptance reconciliation `771ad9bf...` -> independent governance review **ACCEPT** `5711974055`.
- **R3 lineage:** Issue #94 candidate `f467fd75...` -> independent Delivery-Plan Review **ACCEPT** `5712008632` -> explicit Human R3 acceptance `5712045668` -> Issue #95 acceptance reconciliation.
- **Issue #79:** remains **BLOCKED / NOT RELEASED**. Its old r2 authority cannot be reused and its r3 body authorizes no mutation.
- **Next action:** execute R4 reference-workflow/cold-start/handoff reconciliation. Implementation remains blocked until R4 is accepted and R5 explicitly disposes the old implementation path and releases a fresh post-transition implementation TaskSpec.

An open or `READY` Issue does not prove that a Worker is executing it. Issue number order does not determine authority, readiness or the next task.

## Navigation

- **Roadmap:** [ROADMAP.md](ROADMAP.md) and [docs/DEVELOPMENT_PATH.md](docs/DEVELOPMENT_PATH.md)
- **v1 product target:** [docs/V1_PRODUCT_CONTRACT.md](docs/V1_PRODUCT_CONTRACT.md)
- **Canonical acceptance scenarios:** [docs/REFERENCE_WORKFLOWS.md](docs/REFERENCE_WORKFLOWS.md)

## Reading order for a new maintainer or AI

1. [CONSTITUTION.md](CONSTITUTION.md)
2. this file
3. [AGENTS.md](AGENTS.md)
4. [VISION.md](VISION.md)
5. [ARCHITECTURE.md](ARCHITECTURE.md)
6. [docs/V1_PRODUCT_CONTRACT.md](docs/V1_PRODUCT_CONTRACT.md)
7. [ROADMAP.md](ROADMAP.md)
8. [docs/DEVELOPMENT_PATH.md](docs/DEVELOPMENT_PATH.md)
9. [docs/REFERENCE_WORKFLOWS.md](docs/REFERENCE_WORKFLOWS.md)
10. relevant core beliefs, accepted ADRs and designs
11. the current active/historical stage parent plan when relevant
12. [docs/AI_HANDOFF.md](docs/AI_HANDOFF.md)
13. the concrete durable Issue TaskSpec

Completed plans preserve historical status and commit counts; they do not override this file's current project summary. This file does not override the Constitution, core beliefs, accepted ADRs, Architecture or accepted designs. If sources conflict, stop and reconcile them through the repository authority hierarchy rather than choosing silently.
