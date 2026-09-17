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
- Final accepted-truth reconciliation is `b5ee78f7febae1346c771fa6060fcb3e18ea56f3`, independently ACCEPTed on Issue #99 comment `5712355215`.
- ADR-0008 and the accepted Stage 2 sandbox design remain valid historical/provider-conformance assets and an optional/reference execution path.
- Issue #79 is closed **SUPERSEDED / NOT RELEASED** as not planned and must not be revived, repurposed or treated as post-transition execution authority.
- Current executable work is **Issue #100**, G1/M1 Governance SDK / Facade Foundation, revision `r1 - g1-m1-governance-facade-foundation`.
- Issue #100 is **READY — RELEASED FOR WORKER EXECUTION** from exact starting HEAD `b5ee78f7febae1346c771fa6060fcb3e18ea56f3`.
- G1 readiness does not imply implementation has started or that broader G1/G2 work is released.

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

For current G1/M1 work, the only released implementation TaskSpec is Issue #100 r1. Its exact allowed paths, baseline and validation rules control execution.

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

Historical accepted artifacts must not be rewritten to imply the current strategy always existed. Corrections and supersession are forward, attributable records.

## Remote repository mutation boundary

Repository-local work and remote effects are separate authorities. Unless explicitly authorized by the current TaskSpec or Human instruction, a Worker MUST NOT push, mutate remote refs, create/merge/close PRs, publish releases, rewrite remote history or mutate Issues.

Issue #100 releases implementation work but explicitly does not release arbitrary remote publication.

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

For Issue #100 r1 the exact expected starting HEAD is:

```text
b5ee78f7febae1346c771fa6060fcb3e18ea56f3
```

If required execution or validation cannot run, report the gap and do not fabricate evidence or claim completion.
