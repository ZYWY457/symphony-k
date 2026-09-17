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
9. Read the current G2 parent plan `docs/exec-plans/planned/g2-trusted-evaluation-evidence.md`.
10. Perform the bounded current-task/review discovery below.
11. Read the accepted M0 design `docs/design-docs/g2-trusted-evaluation-evidence-boundary.md` and its independent acceptance on Issue #105 comment `5717950150` under #106, then freshly read the current concrete TaskSpec Issue #108.
12. Verify repository identity, exact launch baseline, readiness and remote authority independently before mutation.

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
- G2 parent planning is accepted at `6434cecc2daae51d17182a7cf18184a9a8124a05`; Issue #104 is closed completed.
- The current G2 parent plan is `docs/exec-plans/planned/g2-trusted-evaluation-evidence.md`.
- **G2/M0 is COMPLETE / ACCEPTED** at `9c36fbcfac3854271af8eb15dca08f6a9ec2eca2`; accepted contract: [`design-docs/g2-trusted-evaluation-evidence-boundary.md`](design-docs/g2-trusted-evaluation-evidence-boundary.md).
- Independent acceptance: [Issue #105 comment `5717950150`](https://github.com/ZYWY457/symphony-k/issues/105#issuecomment-5717950150) under Issue #106 — **ACCEPT**, findings none. No separate Human acceptance is claimed; independent ACCEPT satisfies this M0 design gate.
- Issues #105/#106 preserve M0 execution/review lineage; #107 completed accepted-truth reconciliation at `6cbd6a91b27f969461cad5e22b0d7663b3a9bb7a`.
- **Issue #108 is the current G2/M1 implementation TaskSpec** for durable evidence provenance intake only.
- **G2/M1 is RELEASED FOR IMPLEMENTATION only within #108.** G2/M2-M6 and G3 remain NOT RELEASED.

## Current G2 path

```text
G2/M0 contract + threat-boundary freeze — COMPLETE / ACCEPTED
-> G2/M1 durable evidence provenance intake
-> G2/M2 trusted evaluator identity + assignment binding
-> G2/M3 trusted Evaluation execution/result intake
-> G2/M4 durable authoritative effective-use resolver/query
-> G2/M5 evidence-backed Outcome disposition bridge
-> G2/M6 stage acceptance + accepted-truth reconciliation
```

Current interpretation:

- Stage 1 already owns Evaluation lifecycle, conflict/arbitration/invalidation, effective-use derivation and Outcome disposition semantics.
- G1 already owns the public exact-ref / caller-DTO / injected-trusted-binder facade boundary.
- Accepted M0 freezes the trusted evidence/evaluator contract and threat boundary before implementation.
- M0 acceptance is documentation/design only; #107 reconciled that truth without implementing G2.
- #108 releases M1 durable evidence provenance intake only. It must preserve caller-claim versus trusted-provenance separation, append-only exact replay/collision rules, and supporting-record status outside the six lifecycle entities. It must not silently implement M2-M5.
- Caller-supplied evidence, evaluator identity or history completeness is not trusted by construction.
- Evaluation judgement remains distinct from Outcome disposition policy and required Human acceptance.
- G2 does not authorize real Effect dispatch; that remains G3.

## Current-task and review discovery

After reading `STATUS.md`:

1. identify exact accepted baseline and current gate;
2. read the accepted M0 design and independent review on #105 comment `5717950150` under #106;
3. freshly read Issue #108 and verify it is READY before implementation mutation;
4. verify its exact launch HEAD equals the executor starting HEAD;
5. restrict implementation to #108's explicit source/test allowlist;
6. verify the Worker may create only a local candidate and may not perform remote mutation;
7. distinguish M1 evidence provenance from M2 evaluator assignment, M3 Evaluation intake, M4 effective-use resolution, M5 Outcome disposition and G3 Effect behavior;
8. report any architecture-stop discovery instead of expanding scope.

Mandatory distinctions:

```text
Task discovery != execution authority
Planned Exec Plan != released TaskSpec
Design TaskSpec != implementation authority
Candidate != accepted truth
External execution success != authoritative completion
Historical accepted asset != current implementation authority
Roadmap stage != released TaskSpec
```

For the current repository state:

```text
Issue #79 = SUPERSEDED / NOT RELEASED / closed not planned
G1/M1 = COMPLETE / ACCEPTED at 62133cdfc7abac6bf7d1ce4666b5953192ffc9d1
Issue #104 = accepted G2 planning identity / closed completed
G2 parent plan = docs/exec-plans/planned/g2-trusted-evaluation-evidence.md
G2/M0 = COMPLETE / ACCEPTED at 9c36fbcfac3854271af8eb15dca08f6a9ec2eca2
Issue #105 = historical M0 design execution and durable acceptance comment 5717950150
Issue #106 = independent M0 review authority
Issue #107 = completed M0 accepted-truth reconciliation at 6cbd6a91b27f969461cad5e22b0d7663b3a9bb7a
Issue #108 = current G2/M1 durable evidence provenance implementation TaskSpec
G2/M1 = RELEASED only within #108 exact scope
G2/M2-M6 and G3 = NOT RELEASED
```

## Accepted G1/M1 facade boundary

The public facade exposes typed exact references for all six core entities, caller-controlled submissions separated from trusted Stage 1 authority/context construction, supported Run/Outcome/Evaluation mutations through an injected trusted binder, exact/current reads, caller-safe errors, stale/superseded/cross-entity and exact-lineage enforcement, replay/idempotency and optimistic-concurrency preservation, and explicit unsupported real Effect dispatch.

It does not expose public Run completion or Outcome acceptance, does not permit callers to manufacture trusted Stage 1 authority by supplying context objects, and does not define G2 trust policy.

## Preserved G2 architecture-stop conditions

The accepted M0 design reported no architecture-stop discovery. If later work concludes that trusted Evaluation/evidence requires a new Stage 1 lifecycle state, a seventh core entity, weakened exact-version/history semantics, a constitutional trust-model change, caller-controlled authority, real Effect dispatch, or a material change to the accepted product identity, stop and report an `ARCHITECTURE STOP`.

Do not convert that discovery into opportunistic domain or persistence implementation.

## TaskSpec precondition

A title, draft, parent Exec Plan, roadmap row, placeholder identity or conversation-only instruction is insufficient. Issue #108 must explicitly be READY and name the exact launch HEAD before M1 source/test mutation begins.

Issue #108 controls M1 scope and remote authority. The Worker may create only a local candidate commit and must not push, update `main`, mutate Issues/PRs, or create tags/releases. Publication and independent review remain separate Effects. Do not infer M2-M6 or G3 authority from M1 release.

## Historical truth and corrections

Rejected candidates, prior accepted architectures and superseded delivery plans remain historical facts. Corrections are forward records. Do not rewrite accepted history to imply the current strategy always existed.

The Stage 2 sandbox design remains accepted technical history and a reusable conformance/reference asset even though R3 superseded the old runtime-first v1 sequencing. Issue #79's old execution authority is durably superseded.

The G1/M1 implementation follows the same forward-correction rule: Issue #100's rejected initial candidate remains attributable, while Issue #102 records the accepted corrections leading to `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`.

G2/M0 preserves Issue #105's original execution TaskSpec and candidate lineage and Issue #106's review history, including the earlier independence-precondition failure. The substantive independent ACCEPT is #105 comment `5717950150`. #107 reconciles status metadata forward without changing the accepted M0 contract or claiming Issue closure before publication.

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
    -> Worker/design candidate
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
- the accepted product identity and v1 delivery path;
- that Issue #79 is superseded/closed and cannot be reused;
- that G1/M1 is COMPLETE / ACCEPTED at `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`;
- that G2 planning is accepted at `6434cecc2daae51d17182a7cf18184a9a8124a05`;
- the G2 M0-M6 path;
- that M0 is COMPLETE / ACCEPTED at `9c36fbcfac3854271af8eb15dca08f6a9ec2eca2`, based on independent review #105 comment `5717950150` under #106;
- that #105/#106 preserve historical execution/review and #107 completed accepted-truth reconciliation;
- that Issue #108 is the current M1 implementation TaskSpec and must name the exact launch HEAD;
- that M1 is released only for durable evidence provenance intake within #108, while M2-M6 and G3 remain unreleased;
- that M1 cannot silently implement evaluator assignment, Evaluation intake, effective-use resolution or Outcome disposition;
- what paths and remote actions are authorized.

Pass means correct, source-backed discovery without private conversation context.

## Handoff evidence

Every completed Worker/design report should identify:

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
