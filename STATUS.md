# Project Status

## Accepted baseline

- **Project:** Symphony-K; **maturity:** pre-v1 development
- **Completed stages:** Stage 0, Stage 1
- **Stage 1:** **COMPLETE**; the final accepted implementation/governance
  boundary is `987f927905cadcedd473f2ba3270f56908b7f6b9`, with Human Exit
  acceptance recorded by GitHub Issue #75 and its ordered governance commits.
- **Latest accepted stage:** Stage 1 — Domain Kernel
- **Current accepted constitutional baseline:** `constitution-v0.2`, accepted
  with ADR-0009 at exact head
  `9c842f18ffcdd51daef8f05d9367f571df677703` after independent technical
  re-review **ACCEPT** on Issue #89 comment `5711016301` and explicit Human
  **APPROVED / ACCEPTED** on Issue #89 comment `5711029647`.
- **ADR-0009:** **ACCEPTED** — Framework-Neutral Agent Governance Kernel and
  External Execution Boundary. It preserves accepted Stage 1 semantics while
  narrowing v1 ownership of planning, routing, Agent runtime and sandbox
  mechanisms.
- **Stage 2 M1 architecture/design:** **HUMAN ACCEPTED**. ADR-0008 remains
  **ACCEPTED** and technically unchanged. The current cumulative accepted
  sandbox design baseline is
  `77acfbdaf2bed6f0536873fafc8eb7a12599da83`
  (`docs(architecture): clarify unknown frozen salvage collection`).
- The historical pre-erratum Human Accepted baseline remains
  `b52df98530d8ce742b07d7f6c399ccd5b54e643b`
  (`docs(architecture): resolve final sandbox contract review findings`). Issue
  #79 r2 subsequently stopped before mutation on contradictory UNKNOWN
  collection rules; the accepted M1C erratum corrects that ambiguity without
  rewriting the prior acceptance.
- **M1C acceptance:** the exact corrected baseline passed
  [independent technical review with **ACCEPT**](https://github.com/ZYWY457/symphony-k/issues/83#issuecomment-5706630764)
  and received
  [explicit Human erratum approval with **APPROVED**](https://github.com/ZYWY457/symphony-k/issues/83#issuecomment-5706652702).
- Stage 2 runtime isolation evidence is **NOT YET ESTABLISHED** and runtime
  implementation is **NOT YET STARTED**.

## Current governance status

- **Human strategic decision:** the framework-neutral governance/control-plane
  transition was explicitly **APPROVED** on Issue #87 in
  [Human strategic approval comment `5710053258`](https://github.com/ZYWY457/symphony-k/issues/87#issuecomment-5710053258).
  The approval authorizes bounded reconciliation, not production implementation
  or release.
- **Completed strategic-validation cycle:** Issue #85 produced the initial
  falsification experiment and received
  [independent **REQUEST CHANGES**](https://github.com/ZYWY457/symphony-k/issues/85#issuecomment-5707299068).
  Issue #86 produced the bounded evidence correction, and its exact published
  chain received
  [independent **ACCEPT**](https://github.com/ZYWY457/symphony-k/issues/86#issuecomment-5709520565).
- **Strategic evidence result:** gates A/B/C/D/E passed under the registered
  experiment. That evidence supported consideration of an amendment; the later
  Human approval is a separate governance decision.
- **R1 architecture/constitution:** **COMPLETE AND HUMAN ACCEPTED** at exact head
  `9c842f18ffcdd51daef8f05d9367f571df677703`. ADR-0009 and Constitution v0.2
  are current accepted governance truth.
- **Current governance work:** R2 product-definition reconciliation is the next
  strategic step. `VISION.md`, `ARCHITECTURE.md`, `docs/V1_PRODUCT_CONTRACT.md`
  and the root `README.md` still carry historical pre-transition accepted
  wording until R2 is materialized, reviewed and accepted.
- **Implementation hold:** Issue #79 remains **BLOCKED / NOT RELEASED**. Its old
  Stage 2 M2 scope must not be re-released during strategic reconciliation.
  R1 acceptance does not authorize an implementation restart.

## Current Stage 2 status

- **Current stage:** Stage 2 — Sandbox Execution
- **Stage 2 activity:** **ACTIVE** at the accepted M1 design boundary; runtime
  implementation remains blocked pending completion of the strategic
  reconciliation sequence.
- **Current parent plan:**
  [docs/exec-plans/active/stage-02-sandbox-execution.md](docs/exec-plans/active/stage-02-sandbox-execution.md)
- **Current Human Accepted Stage 2 technical design baseline:**
  `77acfbdaf2bed6f0536873fafc8eb7a12599da83`
  (`docs(architecture): clarify unknown frozen salvage collection`)
- **Historical pre-erratum accepted baseline:**
  `b52df98530d8ce742b07d7f6c399ccd5b54e643b`
  (`docs(architecture): resolve final sandbox contract review findings`)
- **Correction lineage:** Issue #77 candidate -> Issue #78 / candidate
  `613d71b90c36b573578f6fffb9a6c7dd9606478f` -> independent review ->
  Issue #80 continuity governance -> Issue #81 M1B correction candidate ->
  independent cumulative M1B technical review **ACCEPT** -> explicit Human M1
  design approval -> Issue #82 governance reconciliation/review ACCEPT ->
  Issue #79 r2 pre-mutation STOP -> Issue #79 r3 BLOCKED -> Issue #83 M1C
  candidate -> independent M1C technical review **ACCEPT** -> explicit Human
  M1C erratum approval **APPROVED** -> Issue #84 acceptance reconciliation.
- **Independent cumulative M1B technical review:** **ACCEPT**, recorded on
  Issue #81 against the exact technical baseline above.
- **Previous durable review:**
  [docs/reviews/stage-02-m1a-613d71b-review.md](docs/reviews/stage-02-m1a-613d71b-review.md)
  remains **REQUEST CHANGES** against `613d71b90c36b573578f6fffb9a6c7dd9606478f`.
- **Human disposition:** **APPROVED**, recorded on Issue #81 for ADR-0008 and
  the cumulative sandbox design at the exact accepted baseline above.
- **Historical governance reconciliation:** the Issue #82 reconciliation commit
  records approval/status/history only; it does not replace or modify the
  accepted technical design baseline.
- **Issue #82 independent governance review:** **ACCEPT** against
  `7ff155c29de83fbcc5487698c8b72b70b2dec075`, recorded on Issue #82. This is
  historical approval lineage, not approval of the M1C correction.
- **Historical accepted correction plan:**
  [M1C UNKNOWN frozen salvage](docs/exec-plans/active/stage-02-correction-m1c-unknown-frozen-salvage-v1.md).
- **Current accepted corrected design:**
  `77acfbdaf2bed6f0536873fafc8eb7a12599da83`, parent
  `7ff155c29de83fbcc5487698c8b72b70b2dec075`. It permits one guarded read-only
  frozen-salvage collect while retaining
  UNKNOWN/cleanup and prohibiting reuse/export/rebinding before targeted destroy.
- **Runtime isolation evidence:** **NOT YET ESTABLISHED**.
- **Stage 2 runtime code:** **NOT YET STARTED**
- **Stage 2 complete:** **NO**

## Dispatch / review queue

- **Historical Stage 2 governance reconciliation:** Issue #84 reconciled the
  independent M1C technical review **ACCEPT** and Human erratum approval
  **APPROVED**. Its governance commit records acceptance/status/history only and
  does not replace or modify the accepted technical baseline
  `77acfbdaf2bed6f0536873fafc8eb7a12599da83`.
- **Strategic-validation lineage:** Issue #85 initial experiment -> independent
  **REQUEST CHANGES** comment `5707299068` -> Issue #86 bounded correction ->
  independent **ACCEPT** comment `5709520565`. The accepted review classifies
  gates A/B/C/D/E as PASS and reaches the registered GO gate for considering a
  formal amendment; it does not approve that amendment.
- **R1 acceptance lineage:** Issue #87 Human strategic approval -> Issue #89 R1
  candidate -> independent REQUEST CHANGES comment `5710385425` -> Issue #90
  narrow R1C correction -> corrected head `9c842f18...` -> independent technical
  re-review **ACCEPT** comment `5711016301` -> explicit Human R1 acceptance
  comment `5711029647` -> Issue #91 acceptance reconciliation.
- **Issue #79:** **BLOCKED / NOT RELEASED**, revision
  `r3 - stage-02-m2-blocked-after-unknown-collection-stop`. Its earlier r2 was
  released but stopped before mutation; no M2 code or implementation commit
  was produced. Do not reuse r2 execution authority or re-release its old M2
  scope while the required strategic reconciliation remains unresolved.
- **Next action:** execute and review R2 product-definition reconciliation for
  `VISION.md`, `ARCHITECTURE.md`, `docs/V1_PRODUCT_CONTRACT.md` and root
  `README.md`. R3 delivery-plan and R4 workflow/cold-start reconciliation remain
  subsequent bounded work. Implementation cannot restart before the required
  reconciliation and a fresh executable TaskSpec.
- **Stage 3:** **PLANNED** — not activated.

An open or `READY` Issue does not prove that a Worker is executing it. Issue
number order does not determine authority, readiness or the next task.

## Navigation

- **Roadmap:** [ROADMAP.md](ROADMAP.md) and
  [docs/DEVELOPMENT_PATH.md](docs/DEVELOPMENT_PATH.md)
- **v1 product target:**
  [docs/V1_PRODUCT_CONTRACT.md](docs/V1_PRODUCT_CONTRACT.md)
- **Canonical acceptance scenarios:**
  [docs/REFERENCE_WORKFLOWS.md](docs/REFERENCE_WORKFLOWS.md)

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
11. the current active stage parent plan, when one exists
12. [docs/AI_HANDOFF.md](docs/AI_HANDOFF.md), including candidate/review and
    bounded related-Issue discovery
13. the concrete durable Issue TaskSpec

Completed plans preserve historical status and commit counts; they do not
override this file's current project summary. This file does not override the
Constitution, core beliefs, accepted ADRs, Architecture or accepted designs. If
any sources conflict, stop and reconcile them through the repository authority
hierarchy rather than choosing silently.