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
10. Freshly read the concrete durable TaskSpec.
11. Verify repository identity, baseline, readiness and remote authority independently before mutation.

If a required source cannot be read or the baseline conflicts with the TaskSpec, stop before mutation.

## Current accepted product and delivery truth

- Constitution v0.2 and ADR-0009 are accepted.
- R2 product definition, R3 delivery path, R4 workflows/cold-start truth and R5 final disposition are Human accepted.
- Repository-level strategic transition R1-R5 is COMPLETE.
- Final accepted-truth reconciliation is `b5ee78f7febae1346c771fa6060fcb3e18ea56f3`, independently ACCEPTed on Issue #99 comment `5712355215`.
- Symphony-K is a framework-neutral governance/control-plane system for agentic work.
- External agents/orchestrators/runtimes may decide how work is attempted; their claims do not become authoritative merely because they produced them.
- The accepted v1 delivery path centers on governance facade, trusted Evaluation/evidence, governed Effect gateway and reconciliation, audit export, conformance, external integration, reference provider path, operational safety, hardening and v1 acceptance.
- Generic Planner, Router, learned routing/reputation, multiple complete Agent runtimes and ownership of a production sandbox runtime are not mandatory v1 prerequisites.
- ADR-0008 and the accepted Stage 2 M1/M1C design remain accepted provider/security/conformance assets and an optional/reference execution path.
- Issue #79 is closed **SUPERSEDED / NOT RELEASED** as not planned; its old Stage 2 M2 authority must not be reused or repurposed.
- Current executable implementation TaskSpec is Issue #100 r1, **READY — RELEASED FOR WORKER EXECUTION**, from exact baseline `b5ee78f7febae1346c771fa6060fcb3e18ea56f3`.

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
Issue #100 r1 = READY implementation authority for G1/M1 only
required starting HEAD = b5ee78f7febae1346c771fa6060fcb3e18ea56f3
```

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

For current G1/M1 implementation, use Issue #100 revision `r1 - g1-m1-governance-facade-foundation`. It authorizes only its exact source/test paths and does not authorize remote publication, G2, real Effect dispatch or changes to Stage 1 domain/persistence semantics.

## Architecture or product discoveries

If work reveals a changed authority boundary, trust assumption, top-level concept, material v1 responsibility or constitutional conflict:

1. stop at the discovery boundary;
2. preserve evidence and candidate workspace;
3. propose the required ADR/amendment/Product Contract reconciliation;
4. resume only after the accepted decision and a new bounded TaskSpec.

Implementation convenience must not silently redefine the accepted product.

## Historical truth and corrections

Rejected candidates, prior accepted architectures and superseded delivery plans remain historical facts. Corrections are forward records. Do not rewrite accepted history to imply the current strategy always existed.

The Stage 2 sandbox design remains accepted technical history and a reusable conformance/reference asset even though R3 superseded the old runtime-first v1 sequencing. Issue #79's old execution authority is now durably superseded.

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
- that Issue #100 r1 is the current READY G1/M1 TaskSpec;
- exact starting baseline `b5ee78f7febae1346c771fa6060fcb3e18ea56f3`;
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
