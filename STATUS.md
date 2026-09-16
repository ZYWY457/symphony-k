# Project Status

## Accepted baseline

- **Project:** Symphony-K; **maturity:** pre-v1 development
- **Completed stages:** Stage 0, Stage 1
- **Stage 1:** **COMPLETE**; the final accepted implementation/governance
  boundary is `987f927905cadcedd473f2ba3270f56908b7f6b9`, with Human Exit
  acceptance recorded by GitHub Issue #75 and its ordered governance commits.
- **Latest accepted stage:** Stage 1 — Domain Kernel
- **Current constitutional baseline:** `constitution-v0.1`
- **Historical Stage 2 M1 architecture/design:** **HUMAN ACCEPTED**. ADR-0008 is
  **ACCEPTED**, and the exact accepted sandbox design baseline is
  `b52df98530d8ce742b07d7f6c399ccd5b54e643b`
  (`docs(architecture): resolve final sandbox contract review findings`).
- That prior acceptance remains historical truth. Issue #79 r2 stopped before
  mutation on contradictory UNKNOWN collection rules; the baseline cannot serve
  as an unambiguous M2 contract until the M1C erratum is reviewed and accepted.
- **Current M1C technical candidate:**
  `77acfbdaf2bed6f0536873fafc8eb7a12599da83`
  (`docs(architecture): clarify unknown frozen salvage collection`), under
  Issue #83. Independent review and Human approval of the exact erratum are
  **PENDING**. ADR-0008 remains Accepted and unchanged.
- Stage 2 runtime isolation evidence is **NOT YET ESTABLISHED** and runtime
  implementation is **NOT YET STARTED**.

## Current Stage 2 status

- **Current stage:** Stage 2 — Sandbox Execution
- **Stage 2 activity:** **ACTIVE**
- **Current parent plan:**
  [docs/exec-plans/active/stage-02-sandbox-execution.md](docs/exec-plans/active/stage-02-sandbox-execution.md)
- **Historical accepted Stage 2 technical design baseline:**
  `b52df98530d8ce742b07d7f6c399ccd5b54e643b`
  (`docs(architecture): resolve final sandbox contract review findings`)
- **Correction lineage:** Issue #77 candidate -> Issue #78 / candidate
  `613d71b90c36b573578f6fffb9a6c7dd9606478f` -> independent review ->
  Issue #80 continuity governance -> Issue #81 M1B correction candidate ->
  independent cumulative M1B technical review **ACCEPT** -> explicit Human M1
  design approval -> Issue #82 governance reconciliation/review ACCEPT ->
  Issue #79 r2 pre-mutation STOP -> Issue #79 r3 BLOCKED -> Issue #83 M1C
  candidate (review and Human erratum approval PENDING).
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
- **Current correction plan:**
  [M1C UNKNOWN frozen salvage](docs/exec-plans/active/stage-02-correction-m1c-unknown-frozen-salvage-v1.md).
- **Current corrected design candidate:**
  `77acfbdaf2bed6f0536873fafc8eb7a12599da83`, parent
  `7ff155c29de83fbcc5487698c8b72b70b2dec075`; candidate only, not Human Accepted.
  It permits one guarded read-only frozen-salvage collect while retaining
  UNKNOWN/cleanup and prohibiting reuse/export/rebinding before targeted destroy.
- **Runtime isolation evidence:** **NOT YET ESTABLISHED**.
- **Stage 2 runtime code:** **NOT YET STARTED**
- **Stage 2 complete:** **NO**

## Dispatch / review queue

- **Current review work:** independently review the exact Issue #83 M1C
  technical candidate `77acfbdaf2bed6f0536873fafc8eb7a12599da83` after publication;
  explicit Human approval of the exact erratum remains PENDING. The later
  governance commit records candidate pointers only, not acceptance.
- **Issue #78:** candidate history/correction source; not itself proof of
  acceptance.
- **Issue #79:** **BLOCKED / NOT RELEASED**, revision
  `r3 - stage-02-m2-blocked-after-unknown-collection-stop`. Its earlier r2 was
  released but stopped before mutation; no M2 code or implementation commit
  was produced. Do not reuse r2 execution authority.
- **Next action:** publish under separate authority, independently review the
  exact M1C candidate, obtain Human erratum approval, and durably reconcile
  acceptance before a new explicit READY revision and fresh #79 launch.
  This candidate reconciliation does not release M2.
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
