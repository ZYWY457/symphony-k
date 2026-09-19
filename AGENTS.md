# AGENTS.md

## Purpose

This repository implements Symphony-K as a **framework-neutral governance/control-plane system for agentic work**. External agents, orchestrators and runtimes may decide how work is attempted. Symphony-K governs authority, evidence, Evaluation, consequential Effects and reconstructable history.

This file is a navigation and execution-governance map, not the full specification.

## Read first

Before mutation, read in this order unless the current TaskSpec narrows the scope:

1. `CONSTITUTION.md`
2. `STATUS.md`
3. `AGENTS.md`
4. `VISION.md`
5. `ARCHITECTURE.md`
6. `docs/V1_PRODUCT_CONTRACT.md`
7. `ROADMAP.md`
8. `docs/DEVELOPMENT_PATH.md`
9. `docs/REFERENCE_WORKFLOWS.md`
10. relevant core beliefs, accepted ADRs/designs
11. `docs/AI_HANDOFF.md`
12. the concrete durable TaskSpec

`STATUS.md` is the compact current-truth entry point. Historical plans and accepted technical assets remain evidence, but they do not automatically define current execution authority.

## Current strategic and execution truth

- Constitution v0.2 and ADR-0009 are accepted.
- R2 product definition, R3 delivery path, R4 workflows/cold-start truth and R5 final disposition are Human accepted.
- Repository-level strategic transition R1-R5 is COMPLETE.
- Final strategic accepted-truth reconciliation is `b5ee78f7febae1346c771fa6060fcb3e18ea56f3`, independently ACCEPTed on Issue #99 comment `5712355215`.
- ADR-0008 and the accepted Stage 2 sandbox design remain valid historical/provider-conformance assets and an optional/reference execution path.
- Issue #79 is closed **SUPERSEDED / NOT RELEASED** as not planned and must not be revived, repurposed or treated as post-transition execution authority.
- **G1/M1 Governance SDK / Facade is COMPLETE / ACCEPTED** at `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`.
- Issue #100 preserves the original G1/M1 TaskSpec and initial candidate lineage; its candidate `36cb145fa666fa9a2218028d2d3828f28c0ed352` was NOT ACCEPTED.
- Issue #102 contains the forward M1A correction lineage and independent final acceptance review `5714651540`.
- **G2/M0 is COMPLETE / ACCEPTED** at design boundary `9c36fbcfac3854271af8eb15dca08f6a9ec2eca2`.
- **G2/M1 is COMPLETE / ACCEPTED** at implementation boundary `83a67c9fc98b1de7b42ad65772d8956f9b721915`.
- G2/M1 accepted-truth reconciliation is `67f91f00ed3d6491f4451b801a19ae20ac409905`; it does not replace the implementation boundary.
- Original M1 candidate `e5402b6415ab76a7fed5635949cfea335db2b5c6` remains historical **NOT ACCEPTED / CORRECTION REQUIRED** evidence.
- Issues #108, #110, #113 and #114 are completed historical execution/review/reconciliation lineage and MUST NOT be treated as current execution authority.
- **Issue #111 r4 is completed lineage, not current execution authority:** it produced refresh candidate `f8ccac552e5b48d5b7a4df86683844d242bc8221`, which #115 reviewed with disposition CORRECTION REQUIRED (durable record: #111 comment `5724524204`). The #116 forward correction `c5eb696f9f84087c996c5ae3bb03da21a7e6d54c` was independently ACCEPTED under #117 (durable record: #116 comment `5731074937`) and is the accepted corrected refresh boundary. No candidate becomes accepted truth merely by existing; acceptance follows the recorded review gates.
- **G2/M2-M6 and G3 are NOT RELEASED.** Do not infer M2 authority from M1 acceptance or roadmap order.

## Product and integration principles

- Strategic goal continuity, ownership-boundary change: reliable, governable,
  verifiable, attributable and reconstructable agentic work remains the goal;
  current ownership focuses on governance/trust semantics rather than the whole
  planning/routing/runtime stack.
- Internal rigor, external simplicity: keep exactness, provenance, replay,
  concurrency, occurrence and causal history strict internally while exposing
  small supported operations and stable typed references.
- Own the semantics; reuse the mechanisms: own claim/fact, authority,
  Evaluation, Effect and history guarantees; normally reuse IAM, persistence,
  queue/transport, workflow/Agent runtime, sandbox, secrets and observability
  mechanisms behind thin adapters.
- Mechanism providers do not receive authoritative disposition, trust
  promotion, Effect-occurrence or history-rewrite authority.

## Accepted G1/M1 boundary

The public governance facade now provides typed exact references for all six core entities, caller-controlled DTOs separated from trusted Stage 1 authority/context construction, supported Run/Outcome/Evaluation mutations through an injected trusted binder, exact/current reads, caller-safe error translation, exact lineage binding, replay/idempotency and optimistic-concurrency preservation, and explicit unsupported real Effect dispatch.

The accepted G1/M1 surface does **not** expose public Run completion or Outcome acceptance, does not permit callers to supply trusted Stage 1 contexts as authority, does not add new lifecycle semantics and does not define G2 trust policy.

## Core authority rules

1. Workers and external runtimes are untrusted by default.
2. Worker/executor output is a claim, not authoritative truth.
3. External planners/orchestrators may propose or attempt work but MUST NOT grant themselves lifecycle, acceptance, permission, budget or Effect authority.
4. Independent Evaluation/evidence governs authoritative disposition.
5. Stale, superseded, unrelated or cross-entity evidence MUST NOT substitute for exact current evidence.
6. An evaluator MUST NOT commit the Effect it validates.
7. Important external Effects MUST use the governed Effect path.
8. Irreversible Effects require explicit Human authorization under Constitution v0.2.
9. Occurrence truth is distinct from authorization truth.
10. Uncertain Effect occurrence blocks blind retry until governed reconciliation.
11. Historical facts, evidence provenance and audit meaning are append-only.
12. External retry/failover MUST preserve correct attempt lineage and MUST NOT infer non-occurrence from execution failure.
13. Agent-, provider-, runtime- and transport-specific semantics MUST remain outside core governance semantics.
14. Planner/Router/sandbox ownership is optional/reference/future work unless a later accepted decision changes the v1 contract.

## Durable TaskSpec precondition

Before any repository mutation, a Worker must establish a concrete, pre-existing durable TaskSpec identity using either:

- `direct-read`; or
- `materialized-handoff`.

Conversation-only instructions, draft titles, future Issue numbers and placeholders are insufficient. Post-hoc TaskSpec creation does not retroactively authorize earlier work.

A discovered TaskSpec is not executable when it is blocked, unreleased, baseline-mismatched, superseded, overlapping known active work or otherwise fails its stated preconditions.

Do not infer G2/M2 authority from accepted M1 or roadmap order. Freshly read the current concrete TaskSpec named by `STATUS.md` before mutation.

Final Worker evidence must report:

```text
TaskSpec reference:
TaskSpec access mode: direct-read | materialized-handoff
TaskSpec precondition: PASS
starting baseline:
changed paths:
validation:
remote mutation:
```

## Repository continuity

No private chat, model memory, Worker report or account context is a source of truth. If conversation context conflicts with durable repository authority, stop at the conflict and reconcile it explicitly.

Candidate commits do not become accepted truth merely because they exist. Acceptance follows the review/Human gates defined by the current TaskSpec.

Historical accepted artifacts and rejected candidates must not be rewritten to imply the current strategy or implementation always existed. Corrections and supersession are forward, attributable records.

## Remote repository mutation boundary

Repository-local work and remote effects are separate authorities. Unless explicitly authorized by the current TaskSpec or Human instruction, a Worker MUST NOT push, mutate remote refs, create/merge/close PRs, publish releases, rewrite remote history or mutate Issues.

Completed #108/#110/#113/#114 work does not authorize new G2 mutation. Issue
#111 r4 authorized only its 13 documentation/metadata paths and one local
candidate (produced: `f8ccac55...`, disposed CORRECTION REQUIRED under #115);
Issue #116 authorized only `STATUS.md` and `docs/AI_HANDOFF.md` and one local
candidate (produced: `c5eb696f...`, ACCEPTED under #117). Historical TaskSpec
boundaries authorize no new work: the executable boundary is always the one
stated by the current TaskSpec Issue, discovered per `STATUS.md` /
`docs/AI_HANDOFF.md`. No historical boundary authorizes remote mutation,
self-review or M2 release.

If remote mutation occurs, report the exact action, repository/branch, affected object, authorization source and resulting reference.

## Development discipline

For substantial work:

1. verify repository identity, clean/expected baseline and TaskSpec preconditions;
2. stop on higher-authority contradiction;
3. keep changes inside the exact allowed paths;
4. use ADR/amendment process for material architecture/constitutional changes;
5. prefer deterministic evidence over prose assertions;
6. inspect the exact diff and validation results before publication;
7. do not broaden scope opportunistically;
8. do not claim implementation or validation that was not actually performed.

## Execution isolation and integrations

Untrusted execution must use an approved isolation/provenance boundary appropriate to the integration. This may be an external provider or a Symphony-K reference provider. External ownership does not make direct host execution trusted by default.

ADR-0008 and the accepted Stage 2 design remain useful as provider/security/conformance assets. They are not current authority to restart the old Stage 2 M2 implementation path.

## Execution substrate preflight

Implementation work must verify the required repository/toolchain substrate before mutation. Typical checks include:

```text
git status --short
git rev-parse --show-toplevel
git rev-parse HEAD
python --version
uv --version
```

The exact expected starting HEAD must be read freshly from the current TaskSpec. If required execution or validation cannot run, report the gap and do not fabricate evidence or claim completion.
