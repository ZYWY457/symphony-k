# AI and Maintainer Handoff

This workflow is model-, account- and vendor-neutral. No chat transcript, private memory, model state or prior account context is a source of truth. A fresh maintainer must be able to resume from durable repository and TaskSpec artifacts alone.

## Required resume sequence

1. Read `CONSTITUTION.md`.
2. Read `STATUS.md`.
3. Read `AGENTS.md`.
4. Read `VISION.md` and `ARCHITECTURE.md`.
5. Read `docs/V1_PRODUCT_CONTRACT.md`.
6. Read `ROADMAP.md` and `docs/DEVELOPMENT_PATH.md`.
7. Read `docs/REFERENCE_WORKFLOWS.md`.
8. Read relevant core beliefs, accepted ADRs and accepted designs.
9. Perform the bounded current-task/review discovery below.
10. Freshly read the concrete durable TaskSpec, if any work is released.
11. Verify repository identity, baseline, readiness and remote authority independently before mutation.

If a required source cannot be read or the baseline conflicts with the TaskSpec, stop before mutation.

## Current accepted product and delivery truth

- Constitution v0.2 and ADR-0009 are accepted.
- R2 product definition, R3 delivery path, R4 workflows/cold-start truth and R5 final disposition are Human accepted.
- Repository-level strategic transition R1-R5 is COMPLETE.
- Final strategic accepted-truth reconciliation is `b5ee78f7febae1346c771fa6060fcb3e18ea56f3`, independently ACCEPTed on Issue #99 comment `5712355215`.
- Symphony-K is a framework-neutral governance/control-plane system for agentic work.
- External agents/orchestrators/runtimes may decide how work is attempted; their claims do not become authoritative merely because they produced them.
- The accepted v1 delivery path centers on governance facade, trusted Evaluation/evidence, governed Effect gateway and reconciliation, audit export, conformance, external integration, reference provider path, operational safety, hardening and v1 acceptance.
- Generic Planner, Router, learned routing/reputation, multiple complete Agent runtimes and ownership of a production sandbox runtime are not mandatory v1 prerequisites.
- ADR-0008 and the accepted Stage 2 M1/M1C design remain accepted provider/security/conformance assets and an optional/reference execution path.
- Issue #79 is closed **SUPERSEDED / NOT RELEASED** as not planned; its old Stage 2 M2 authority must not be reused or repurposed.
- **G1/M1 is COMPLETE / ACCEPTED** at `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`.
- Issue #100 preserves the initial TaskSpec/candidate lineage; its original candidate `36cb145fa666fa9a2218028d2d3828f28c0ed352` was NOT ACCEPTED.
- Issue #102 contains the forward correction lineage and final independent acceptance review `5714651540`.
- **G2 is PLANNED / NOT RELEASED** and requires a fresh durable TaskSpec before implementation mutation.
- Issue #103 is the current governance/documentation reconciliation and does not release G2.

## Current-task and review discovery

After reading `STATUS.md`:

1. identify the exact accepted baseline and current implementation/review gate;
2. identify the exact current candidate commit, if one exists;
3. read the latest review for that exact candidate;
4. read the concrete TaskSpec named as current work;
5. inspect only predecessor/correction/dependent Issues that materially determine readiness or authority;
6. distinguish task discovery from execution authority;
7. verify whether the TaskSpec is READY, BLOCKED, superseded or baseline-mismatched;
8. verify remote mutation authority separately from local mutation authority;
9. report contradictions rather than silently selecting a convenient source.

Mandatory distinctions:

```text
Task discovery != execution authority
Candidate != accepted truth
Open/READY != known unclaimed work
External execution success != authoritative completion
Dispatch failure != Effect non-occurrence
Historical accepted asset != current implementation authority
Roadmap stage != released TaskSpec
```

For the current repository state:

```text
Issue #79 = SUPERSEDED / NOT RELEASED / closed not planned
G1/M1 = COMPLETE / ACCEPTED at 62133cdfc7abac6bf7d1ce4666b5953192ffc9d1
Issue #100 = historical initial G1/M1 TaskSpec/candidate lineage
Issue #102 = accepted forward correction lineage
Issue #103 = governance/documentation reconciliation only
G2 = PLANNED / NOT RELEASED
```

## Accepted G1/M1 facade boundary

The public facade exposes typed exact references for all six core entities, caller-controlled submissions separated from trusted Stage 1 authority/context construction, supported Run/Outcome/Evaluation mutations through an injected trusted binder, exact/current reads, caller-safe errors, stale/superseded/cross-entity and exact-lineage enforcement, replay/idempotency and optimistic-concurrency preservation, and explicit unsupported real Effect dispatch.

It does not expose public Run completion or Outcome acceptance, does not permit callers to manufacture trusted Stage 1 authority by supplying context objects, and does not define G2 trust policy.

## Governance boundary for external execution

External execution may submit:

- claims;
- candidate Outcomes;
- artifacts/evidence;
- requested Effects;
- retry/failover observations.

Symphony-K must bind those submissions to exact authoritative identities and versions, apply independent Evaluation/evidence, govern consequential Effects and preserve causal audit history. External systems cannot self-accept, self-authorize, substitute stale evidence, rewrite history or bypass Effect governance.

## TaskSpec precondition

Before mutation, establish a concrete, pre-existing durable TaskSpec identity and record either `direct-read` or `materialized-handoff` as defined in `AGENTS.md`.

A title, draft, future number, placeholder identity or conversation-only instruction is insufficient. Post-hoc Issue creation is not retroactive authorization.

Do not use completed Issue #100 or Issue #102 as authorization for new work. For G2, a fresh G2 TaskSpec must first be created and explicitly released.

## Architecture or product discoveries

If work reveals a changed authority boundary, trust assumption, top-level concept, material v1 responsibility or constitutional conflict:

1. stop at the discovery boundary;
2. preserve evidence and candidate workspace;
3. propose the required ADR/amendment/Product Contract reconciliation;
4. resume only after the accepted decision and a new bounded TaskSpec.

Implementation convenience must not silently redefine the accepted product.

## Historical truth and corrections

Rejected candidates, prior accepted architectures and superseded delivery plans remain historical facts. Corrections are forward records. Do not rewrite accepted history to imply the current strategy always existed.

The Stage 2 sandbox design remains accepted technical history and a reusable conformance/reference asset even though R3 superseded the old runtime-first v1 sequencing. Issue #79's old execution authority is durably superseded.

The G1/M1 implementation follows the same forward-correction rule: Issue #100's rejected initial candidate remains attributable, while Issue #102 records the accepted corrections leading to `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`.

## Exec Plan lifecycle

```text
planned/   future/historical parent contract; no execution authority by itself
active/    currently relevant parent contract only when STATUS/current TaskSpec says so
completed/ exited accepted historical contract
```

File location alone is not authority. `STATUS.md` plus the current TaskSpec determines current execution readiness.

## Development Issue lifecycle

```text
DRAFT TASKSPEC
    -> durable Issue exists
    -> explicit READY release
    -> Worker candidate
    -> validation
    -> publication when authorized
    -> independent review
    -> Human acceptance when required
    -> acceptance reconciliation
    -> next bounded TaskSpec
```

GitHub Issues are the current manual development-governance carrier, not a future Symphony-K product-domain dependency.

## Read-only cold-start acceptance checklist

Given only repository read access, a fresh maintainer/AI must be able to report:

- the accepted Constitution/ADR baseline;
- the accepted product identity;
- the accepted v1 delivery path and workflows;
- that strategic transition R1-R5 is complete;
- which Stage 2 assets remain accepted and what role they now have;
- that Issue #79 is superseded/closed and cannot be reused;
- that G1/M1 is COMPLETE / ACCEPTED at `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`;
- that Issue #100's initial candidate was rejected and Issue #102 carries the accepted forward correction lineage;
- that G2 is PLANNED / NOT RELEASED and requires a fresh TaskSpec;
- what work and remote actions are actually authorized.

Pass means correct, source-backed discovery without private conversation context.

## Handoff evidence

Every completed Worker report should identify:

```text
TaskSpec reference
TaskSpec access mode
starting baseline
exact commits and parents
changed paths
validation performed/results
unresolved risks
final repository/worktree state
remote mutation (exact action or none)
```
