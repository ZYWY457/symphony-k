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
9. Read the current planned parent contract when planning a future stage, but do not treat it as execution authority.
10. Perform the bounded current-task/review discovery below.
11. Freshly read the concrete durable TaskSpec, if any work is released.
12. Verify repository identity, baseline, readiness and remote authority independently before mutation.

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
- G1 accepted-truth reconciliation is `eaea5390a088a71fe4108c2b84812253032a287a`; Issues #100/#102/#103 are closed completed.
- Issue #100 preserves the initial TaskSpec/candidate lineage; its original candidate `36cb145fa666fa9a2218028d2d3828f28c0ed352` was NOT ACCEPTED.
- Issue #102 contains the forward correction lineage and final independent acceptance review `5714651540`.
- **G2 is PLANNED / NOT RELEASED.** Issue #104 is the current planning identity, not an implementation TaskSpec.
- The current G2 parent plan is `docs/exec-plans/planned/g2-trusted-evaluation-evidence.md`; its M0–M6 path is planning truth only and does not release source/test mutation.

## Current G2 planning path

The planned sequence is:

```text
G2/M0 contract + threat-boundary freeze
-> G2/M1 durable evidence provenance intake
-> G2/M2 trusted evaluator identity + assignment binding
-> G2/M3 trusted Evaluation execution/result intake
-> G2/M4 durable authoritative effective-use resolver/query
-> G2/M5 evidence-backed Outcome disposition bridge
-> G2/M6 stage acceptance + accepted-truth reconciliation
```

Key cold-start interpretation:

- Stage 1 already owns Evaluation lifecycle, conflict/arbitration/invalidation, effective-use derivation and Outcome disposition semantics.
- G1 already owns the public exact-ref / caller-DTO / injected-trusted-binder facade boundary.
- G2 must integrate trusted evidence/evaluator provenance and authoritative history resolution without duplicating those semantics.
- Caller-supplied evidence, evaluator identity or history completeness is not trusted by construction.
- Evaluation judgement remains distinct from Outcome disposition policy and required Human acceptance.
- G2 does not authorize real Effect dispatch; that remains G3.

Before implementing any G2 milestone, freshly read the planned parent plan and then require a separate milestone-specific TaskSpec. The parent plan cannot be used as a substitute for that TaskSpec.

## Current-task and review discovery

After reading `STATUS.md`:

1. identify the exact accepted baseline and current implementation/review/planning gate;
2. identify the exact current candidate commit, if one exists;
3. read the latest review for that exact candidate;
4. distinguish a planned parent contract from an executable TaskSpec;
5. read the concrete TaskSpec named as current work, if implementation is released;
6. inspect only predecessor/correction/dependent Issues that materially determine readiness or authority;
7. distinguish task discovery from execution authority;
8. verify whether the TaskSpec is READY, BLOCKED, superseded or baseline-mismatched;
9. verify remote mutation authority separately from local mutation authority;
10. report contradictions rather than silently selecting a convenient source.

Mandatory distinctions:

```text
Task discovery != execution authority
Planned Exec Plan != released TaskSpec
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
Issue #100 = historical initial G1/M1 TaskSpec/candidate lineage / closed completed
Issue #102 = accepted forward correction lineage / closed completed
Issue #103 = accepted-truth reconciliation / closed completed
Issue #104 = G2 planning identity only
G2 parent plan = docs/exec-plans/planned/g2-trusted-evaluation-evidence.md
G2 implementation = NOT RELEASED
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

Before implementation mutation, establish a concrete, pre-existing durable TaskSpec identity and record either `direct-read` or `materialized-handoff` as defined in `AGENTS.md`.

A title, draft, future number, parent Exec Plan, roadmap row, placeholder identity or conversation-only instruction is insufficient. Post-hoc TaskSpec creation is not retroactive authorization.

Do not use completed Issue #100, #102 or #103 as authorization for new work. Do not use Issue #104 or the planned G2 parent Exec Plan as implementation authorization. For G2, each implementation milestone needs a fresh G2/Mx TaskSpec that is explicitly released.

## Architecture or product discoveries

If work reveals a changed authority boundary, trust assumption, top-level concept, material v1 responsibility or constitutional conflict:

1. stop at the discovery boundary;
2. preserve evidence and candidate workspace;
3. propose the required ADR/amendment/Product Contract reconciliation;
4. resume only after the accepted decision and a new bounded TaskSpec.

For G2 specifically, a discovered need for a new Stage 1 lifecycle state, seventh core entity or material constitutional trust change is an architecture stop, not permission to modify `src/symphony_k/domain/**` opportunistically.

Implementation convenience must not silently redefine the accepted product.

## Historical truth and corrections

Rejected candidates, prior accepted architectures and superseded delivery plans remain historical facts. Corrections are forward records. Do not rewrite accepted history to imply the current strategy always existed.

The Stage 2 sandbox design remains accepted technical history and a reusable conformance/reference asset even though R3 superseded the old runtime-first v1 sequencing. Issue #79's old execution authority is durably superseded.

The G1/M1 implementation follows the same forward-correction rule: Issue #100's rejected initial candidate remains attributable, while Issue #102 records the accepted corrections leading to `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`.

## Exec Plan lifecycle

```text
planned/   future parent contract; may define sequencing but grants no execution authority by itself
active/    currently relevant parent contract only when STATUS/current TaskSpec says so
completed/ exited accepted historical contract
```

File location alone is not authority. `STATUS.md` plus the current TaskSpec determines current execution readiness.

## Development Issue lifecycle

```text
planning Issue / parent plan
    -> independently reviewed planning truth
    -> fresh bounded milestone TaskSpec
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
- that G1 reconciliation is complete at `eaea5390a088a71fe4108c2b84812253032a287a`;
- that Issue #104 and the G2 parent plan define planning only;
- the G2 M0–M6 planned path;
- that no G2 implementation milestone is released without a fresh TaskSpec;
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
