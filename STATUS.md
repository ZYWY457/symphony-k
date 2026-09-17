# Project Status

## Accepted baseline

- **Project:** Symphony-K; **maturity:** pre-v1 development
- **Completed implementation stages:** Stage 0, Stage 1, G1/M1
- **Stage 1:** **COMPLETE**; final accepted implementation/governance boundary `987f927905cadcedd473f2ba3270f56908b7f6b9`.
- **Current accepted constitutional baseline:** Constitution v0.2 + ADR-0009, accepted at exact R1 head `9c842f18ffcdd51daef8f05d9367f571df677703`.
- **Accepted R2 product definition:** exact head `2b54c2672c0c400aab1f35e0245c8c4e97a62321`; independent review **ACCEPT** `5711134872`; Human acceptance `5711951534`.
- **Accepted R3 delivery path:** exact head `f467fd75071e5d0252719539cf7323fb71de587c`; independent review **ACCEPT** `5712008632`; Human acceptance `5712045668`.
- **Accepted R4 workflow/cold-start reconciliation:** exact head `ecccbedd68f2f0e0eff949c20b627f250ddf189e`; independent review **ACCEPT** `5712098419`; Human acceptance `5712165121`; R4A reconciliation `51137a3549388b61abfcbcbd5d70c6ec66101dae` reviewed **ACCEPT** on Issue #97 comment `5712179640`.
- **Accepted R5 final strategic disposition / release boundary:** exact head `1bb48657a85d746b8d0023ddd805c6cdc09703b0`; independent review **ACCEPT** on Issue #98 comment `5712222234`; final Human acceptance on Issue #98 comment `5712330240`.
- **Final strategic reconciliation commit:** `b5ee78f7febae1346c771fa6060fcb3e18ea56f3`, independently **ACCEPTED** on Issue #99 comment `5712355215`.
- **Accepted G1/M1 governance facade implementation boundary:** `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`; Issue #102 independent acceptance review `5714651540`.
- **G1 accepted-truth reconciliation:** `eaea5390a088a71fe4108c2b84812253032a287a`; Issues #100/#102/#103 are closed completed.
- **Accepted G2 planning boundary:** `6434cecc2daae51d17182a7cf18184a9a8124a05`; Issue #104 planning review `5715084007`; Issue #104 is closed completed.
- **Stage 2 M1/M1C technical design:** **HUMAN ACCEPTED** at `77acfbdaf2bed6f0536873fafc8eb7a12599da83`; ADR-0008 remains **ACCEPTED**.
- Stage 2 runtime code is **NOT STARTED** and runtime isolation evidence is **NOT ESTABLISHED**.

## Strategic transition status

**Repository-level strategic transition R1–R5: COMPLETE AND HUMAN ACCEPTED.**

Symphony-K is a **framework-neutral governance/control-plane system for agentic work**. External agents, orchestrators and runtimes may determine how work is attempted. Symphony-K governs authoritative state/claims, exact evidence and Evaluation, consequential Effects, occurrence uncertainty/reconciliation and durable causal history.

The accepted v1 critical path is:

```text
Stage 1 governance kernel
-> G1 governance SDK/facade
-> G2 trusted Evaluation/evidence integration
-> G3 governed Effect gateway + occurrence reconciliation
-> G4 durable audit export/reconstruction
-> G5 adversarial/conformance suite
-> G6 external agent/orchestrator integration
-> G7 reference execution/provider path
-> G8 end-to-end governance safety/recovery
-> G9 production hardening
-> G10 v1 acceptance
```

A generic Planner, generic Router, learned routing/reputation, multiple complete Agent runtimes and ownership of a production sandbox runtime are not mandatory v1 release blockers.

## Legacy Stage 2 / Issue #79 disposition

- ADR-0008 and accepted Stage 2 M1/M1C design remain valid execution-provider security/conformance assets and an optional/reference implementation path.
- The old Stage 2 runtime-first v1 sequencing is superseded as current delivery authority.
- Issue #79 is **SUPERSEDED / NOT RELEASED**, closed as `not planned`, with durable supersession comment `5712361531`.
- Its old r2/r3 execution authority is historical only and MUST NOT be revived or repurposed as G1 authority.
- Future reference-provider implementation may reuse ADR-0008/M1/M1C only through a fresh bounded TaskSpec.

## G1/M1 accepted implementation truth

**G1 / M1 — Governance SDK / Facade Foundation is COMPLETE / ACCEPTED.**

Accepted implementation boundary: `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`.

Historical implementation lineage is preserved:

- Issue #100 produced original candidate `36cb145fa666fa9a2218028d2d3828f28c0ed352`; independent review comment `5714146581` found a trust-boundary defect, so that candidate was **NOT ACCEPTED**.
- Issue #102 carried the forward M1A correction. Candidate `d09681e7463aa567c576b7b40237d9097a53a572` corrected caller/trusted-context separation but required one exact-version lineage fix; review comment `5714460554` recorded that blocker.
- Final forward correction `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1` was independently **ACCEPTED** on Issue #102 comment `5714651540`.

The accepted G1/M1 facade provides:

- typed exact references for Objective, Task, Run, Outcome, Evaluation and Effect;
- caller-controlled submission DTOs separated from trusted Stage 1 authority/context construction;
- supported Run/Outcome/Evaluation mutation paths through an explicitly injected trusted binder;
- exact identity/version binding including immediate lineage references;
- exact/current reads and caller-safe normalized errors;
- preserved replay/idempotency and optimistic-concurrency semantics; and
- explicit unsupported real Effect dispatch, with no public Run-completion or Outcome-acceptance operation.

G1/M1 does not add new Stage 1 lifecycle semantics or G2 evidence-trust policy.

## Current delivery gate

**G2 — Trusted Evaluation and Evidence Integration remains PLANNED. G2/M0 design freeze is the only milestone being prepared for release.**

Accepted G2 parent planning contract: [`docs/exec-plans/planned/g2-trusted-evaluation-evidence.md`](docs/exec-plans/planned/g2-trusted-evaluation-evidence.md), accepted planning boundary `6434cecc2daae51d17182a7cf18184a9a8124a05`.

Current concrete TaskSpec: **Issue #105 — G2 / M0 — Trusted Evaluation and Evidence Contract / Threat-Boundary Freeze**.

Issue #105 is design-only. It authorizes only the exact documentation paths and remote boundary stated in its body once the TaskSpec is revised to READY with an exact launch HEAD. It does not authorize `src/**`, `tests/**`, M1-M5 implementation, real Effect work, or Stage 1 semantic changes.

The planned G2 path remains:

```text
M0 contract / threat-boundary freeze
-> M1 durable evidence provenance intake
-> M2 trusted evaluator identity + assignment binding
-> M3 trusted Evaluation execution/result intake
-> M4 durable authoritative effective-use resolver/query
-> M5 evidence-backed Outcome disposition bridge
-> M6 stage acceptance + accepted-truth reconciliation
```

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
- #100 — original G1/M1 TaskSpec and rejected initial implementation candidate lineage; closed completed after accepted correction/reconciliation.
- #101 — post-transition cold-start handoff reconciliation.
- #102 — G1/M1A forward trust-boundary correction and final accepted implementation evidence; closed completed.
- #103 — G1/M1 accepted-truth reconciliation; closed completed.
- #104 — G2 parent planning identity; closed completed after accepted planning reconciliation.
- #105 — current G2/M0 design-only TaskSpec.

## Next action

Finalize the G2/M0 launch handoff, then revise Issue #105 to **READY** using that exact launch HEAD. The M0 executor may then produce only the design candidate defined by #105. M1-M5 remain NOT RELEASED.

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
10. [docs/exec-plans/planned/g2-trusted-evaluation-evidence.md](docs/exec-plans/planned/g2-trusted-evaluation-evidence.md)
11. relevant core beliefs, accepted ADRs/designs
12. [docs/AI_HANDOFF.md](docs/AI_HANDOFF.md)
13. current concrete TaskSpec Issue #105

Historical accepted artifacts remain historical truth but do not override the current accepted Constitution, ADR-0009, product definition, delivery path or explicit TaskSpec readiness.
