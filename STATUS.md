# Project Status

## Accepted baseline

- **Project:** Symphony-K; **maturity:** pre-v1 development
- **Completed implementation stages/milestones:** Stage 0, Stage 1, G1/M1, G2/M1
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
- **G2/M0 design:** **COMPLETE / ACCEPTED** at `9c36fbcfac3854271af8eb15dca08f6a9ec2eca2`; independent acceptance on [Issue #105 comment `5717950150`](https://github.com/ZYWY457/symphony-k/issues/105#issuecomment-5717950150) under #106. This is design acceptance, not G2 implementation or a claim of separate Human acceptance.
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

The durable strategic goal remains reliable, governable, evidence-backed,
attributable and reconstructable agentic work. The transition changed the
ownership boundary: external systems may own attempt mechanics, while
Symphony-K owns the governing semantics. Internal rigor should support external
simplicity, and mature infrastructure mechanisms should normally be reused
behind adapters without outsourcing semantic authority.

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

**G2/M0 and G2/M1 are COMPLETE / ACCEPTED. G2/M2-M6 and G3 remain NOT RELEASED.** M1 acceptance is not whole-stage G2 acceptance.

Accepted G2 parent planning contract: [`docs/exec-plans/planned/g2-trusted-evaluation-evidence.md`](docs/exec-plans/planned/g2-trusted-evaluation-evidence.md), accepted planning boundary `6434cecc2daae51d17182a7cf18184a9a8124a05`.

Accepted M0 contract: [`docs/design-docs/g2-trusted-evaluation-evidence-boundary.md`](docs/design-docs/g2-trusted-evaluation-evidence-boundary.md), exact design boundary `9c36fbcfac3854271af8eb15dca08f6a9ec2eca2`. Independent review under Issue #106: Issue #105 comment `5717950150` — **ACCEPT**, findings none.

Accepted M1 implementation boundary: `83a67c9fc98b1de7b42ad65772d8956f9b721915` (`fix(governance): harden evidence provenance trust boundary`). This is distinct from the M0 design boundary above.

Historical implementation lineage:

- #108 is the original M1 TaskSpec. Candidate `e5402b6415ab76a7fed5635949cfea335db2b5c6` remains **NOT ACCEPTED / CORRECTION REQUIRED**, per independent review #109 on [#108 comment `5723629306`](https://github.com/ZYWY457/symphony-k/issues/108#issuecomment-5723629306).
- #110 supplied the forward M1A correction `83a67c9fc98b1de7b42ad65772d8956f9b721915`; candidate evidence is [comment `5723804820`](https://github.com/ZYWY457/symphony-k/issues/110#issuecomment-5723804820).
- #112 independently **ACCEPTED** the correction, findings **none**, in [#110 comment `5723875385`](https://github.com/ZYWY457/symphony-k/issues/110#issuecomment-5723875385); [#112 closure record `5723875761`](https://github.com/ZYWY457/symphony-k/issues/112#issuecomment-5723875761) preserves completion.

Accepted M1 provides caller-claim/trusted-provider separation through an injected trusted collector/verifier; immutable provenance with exact `EvidenceRef` + record fingerprint identity; exact target identity/version binding and evidence-on-evidence resolution; current use-time digest policy; a coherent durable snapshot for trusted evidence-chain resolution; append-only trust findings and correction/supersession provenance; exact replay/idempotency and altered replay/identity collision rejection; atomic SQLite record + replay-operation registration without fake lifecycle `DomainEvent` rows; and caller-safe provider error sanitization.

M1 does not provide evaluator assignment, G2 Evaluation create/start/complete integration, the M4 effective-use resolver, Outcome disposition, Human acceptance, or Effect dispatch/occurrence/reconciliation. Registration is not lifecycle or acceptance authority.

The #112 reviewer completed exact source/diff review and accepted the correction semantics, with independent SQLite snapshot/interleaving and transaction-cleanup probes. The 78 focused and 3394 full-suite tests in #110 comment `5723804820` are Worker-reported evidence, not reviewer reruns. The reviewer could not materialize the checkout because its container could not resolve GitHub hosts; no independent repository-suite rerun is claimed.

Accepted-truth reconciliation: `67f91f00ed3d6491f4451b801a19ae20ac409905`, finalized **ACCEPTED** in [Issue #113 comment `5724156994`](https://github.com/ZYWY457/symphony-k/issues/113#issuecomment-5724156994) after independent review under #114, durable review record [comment `5724140703`](https://github.com/ZYWY457/symphony-k/issues/113#issuecomment-5724140703), findings none. This reconciliation boundary does not replace the M1 implementation boundary.

Current released TaskSpec: [#111 — strategic narrative, external simplicity and cold-start truth refresh](https://github.com/ZYWY457/symphony-k/issues/111), revision `r4 - strategic-narrative-cold-start-refresh-path-correction`, execution handoff [comment `5724161554`](https://github.com/ZYWY457/symphony-k/issues/111#issuecomment-5724161554) and durable path correction [comment `5724343805`](https://github.com/ZYWY457/symphony-k/issues/111#issuecomment-5724343805). It authorizes a repository/docs/metadata candidate only. Acceptance remains pending independent review under #115; candidate existence is not acceptance.

The planned G2 path remains:

```text
M0 contract / threat-boundary freeze — COMPLETE / ACCEPTED
-> M1 durable evidence provenance intake — COMPLETE / ACCEPTED
-> M2 trusted evaluator identity + assignment binding — NOT RELEASED
-> M3 trusted Evaluation execution/result intake — NOT RELEASED
-> M4 durable authoritative effective-use resolver/query — NOT RELEASED
-> M5 evidence-backed Outcome disposition bridge — NOT RELEASED
-> M6 stage acceptance + accepted-truth reconciliation — NOT RELEASED
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
- #105 — historical G2/M0 design execution TaskSpec; produced accepted design `9c36fbcfac3854271af8eb15dca08f6a9ec2eca2`.
- #106 — independent M0 review; ACCEPT recorded on #105 comment `5717950150`.
- #107 — M0 accepted-truth reconciliation; closed completed.
- #108 — historical original M1 TaskSpec and rejected initial candidate.
- #109 — historical independent CORRECTION REQUIRED review, #108 comment `5723629306`.
- #110 — historical M1A forward correction and durable ACCEPT record `5723875385`.
- #112 — completed independent correction review, ACCEPT, findings none.
- #113 — completed G2/M1 accepted-truth reconciliation, accepted at `67f91f00ed3d6491f4451b801a19ae20ac409905`.
- #114 — completed independent reconciliation review, ACCEPT, findings none.
- #111 — current released repository-refresh TaskSpec; candidate acceptance pending #115.
- #115 — future independent review gate for the exact #111 candidate; not executed by the #111 Worker.

## Next action

Execute only the bounded repository refresh under #111 from exact accepted
baseline `67f91f00ed3d6491f4451b801a19ae20ac409905`, then submit its exact local
candidate for independent review under #115. Do not self-review or resume
historical #108/#110/#113 work. M2-M6 and G3 remain NOT RELEASED; no M2 TaskSpec
or launch baseline is established here.

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
13. Issue #111 and execution handoff `5724161554`; #113/#114 as completed reconciliation/review authority; #108/#109/#110/#112 as historical M1 implementation/correction/acceptance evidence; #105/#106/#107 as historical M0 evidence; #115 only after an exact #111 candidate is produced and handed to an independent reviewer

Historical accepted artifacts remain historical truth but do not override the current accepted Constitution, ADR-0009, product definition, delivery path or explicit TaskSpec readiness.
