# Documentation Map

Start with the root [project status](../STATUS.md), then follow the authority and reading order in [AGENTS.md](../AGENTS.md).

The accepted current product identity is a framework-neutral governance/control-plane system for agentic work. Constitution v0.2 and ADR-0009 are accepted; R2 product definition, R3 delivery path, R4 workflows/cold-start truth and R5 final disposition are Human accepted. Repository-level strategic transition R1-R5 is complete.

Final strategic accepted-truth reconciliation is `b5ee78f7febae1346c771fa6060fcb3e18ea56f3`, independently ACCEPTed on Issue #99 comment `5712355215`.

**G1/M1 Governance SDK / Facade is COMPLETE / ACCEPTED** at `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`. Issue #100 preserves the original TaskSpec and rejected initial candidate lineage; Issue #102 carries the forward correction lineage and final independent acceptance review `5714651540`. G1 accepted-truth reconciliation is `eaea5390a088a71fe4108c2b84812253032a287a`.

**G2 Trusted Evaluation and Evidence Integration is PLANNED / NOT RELEASED.** Issue #104 is the current G2 planning identity. Its parent planning contract is [G2 — Trusted Evaluation and Evidence Integration](exec-plans/planned/g2-trusted-evaluation-evidence.md). Neither Issue #104 nor that planned Exec Plan authorizes source/test implementation.

## Constitution and core beliefs

- [Constitution](../CONSTITUTION.md)
- [Trust model](core-beliefs/TRUST_MODEL.md)
- [State and authority](core-beliefs/STATE_AND_AUTHORITY.md)
- [Execution isolation](core-beliefs/EXECUTION_ISOLATION.md)
- [Verification model](core-beliefs/VERIFICATION_MODEL.md)
- [Failure and recovery](core-beliefs/FAILURE_AND_RECOVERY.md)
- [Effects and side effects](core-beliefs/EFFECTS_AND_SIDE_EFFECTS.md)
- [Learning and reputation](core-beliefs/LEARNING_AND_REPUTATION.md)

## Architecture, decisions and design

- [Architecture](../ARCHITECTURE.md)
- [Architecture Decision Records](adr/README.md)
- [Accepted ADR-0009 governance kernel decision](adr/0009-framework-neutral-agent-governance-kernel.md)
- [Design documents](design-docs/)
- [Accepted ADR-0008 sandbox boundary](adr/0008-stage-2-sandbox-execution-boundary.md)
- [Accepted Stage 2 M1/M1C sandbox design](design-docs/sandbox-execution-v1.md)

ADR-0008 and the Stage 2 design remain accepted execution-provider security/conformance assets and an optional/reference implementation path. They no longer define the mandatory v1 delivery sequence.

Issue #79 is closed **SUPERSEDED / NOT RELEASED** as not planned. Its old r2/r3 authority is historical only and must not be revived or reused as current execution authority.

## Product and delivery truth

- [Current status](../STATUS.md)
- [Vision](../VISION.md)
- [Architecture](../ARCHITECTURE.md)
- [v1 Product Contract](V1_PRODUCT_CONTRACT.md)
- [Canonical roadmap](../ROADMAP.md)
- [Development path](DEVELOPMENT_PATH.md)
- [Canonical reference workflows](REFERENCE_WORKFLOWS.md)
- [Planned G2 trusted Evaluation/evidence path](exec-plans/planned/g2-trusted-evaluation-evidence.md)

The accepted v1 critical path centers on governance facade, trusted evidence/Evaluation, governed Effect gateway and reconciliation, audit reconstruction, conformance, integrations, operational safety, hardening and v1 acceptance.

Generic Planner, Router, learned routing/reputation, multiple complete Agent runtimes and ownership of a production sandbox runtime are not mandatory v1 blockers.

G1/M1 accepted capabilities include typed exact references for all six core entities, caller-controlled DTOs separated from trusted Stage 1 authority/context construction, supported Run/Outcome/Evaluation mutation paths through an injected trusted binder, exact/current reads, caller-safe errors, replay/concurrency preservation and explicit unsupported real Effect dispatch. It does not add public Run completion or Outcome acceptance and does not define G2 trust policy.

The planned G2 path is:

```text
M0 contract/threat-boundary freeze
-> M1 durable evidence provenance intake
-> M2 trusted evaluator identity/assignment binding
-> M3 trusted Evaluation execution/result intake
-> M4 authoritative durable effective-use resolver/query
-> M5 evidence-backed Outcome disposition bridge
-> M6 stage acceptance/reconciliation
```

This sequence is planning truth, not execution authority. Each G2 implementation milestone requires its own freshly released TaskSpec. G2 does not add a universal judge, new core entity, real Effect dispatch, provider runtime, G4 audit export or G5 general conformance framework.

## Exec Plans

- [Lifecycle rules](exec-plans/README.md)
- [Planned parent plans](exec-plans/planned/) — future planning artifacts; no execution authority by themselves
- [Active plans](exec-plans/active/) — may contain historically accepted technical assets; current authority must be confirmed through `STATUS.md` and the current TaskSpec
- [Completed plans](exec-plans/completed/) — accepted historical plans

The G2 parent plan deliberately remains under `planned/` until milestone-specific implementation authority exists. The historical Stage 2 active plan preserves accepted M1/M1C provenance but the old runtime-first implementation sequence is superseded for v1 delivery. Issue #79 is historical only; future sandbox/provider reuse requires a fresh TaskSpec, normally under G7.

## Handoff and governance templates

- [AI and maintainer handoff](AI_HANDOFF.md)
- [Durable TaskSpec template](TASKSPEC_TEMPLATE.md)
- [Human stage-exit template](STAGE_EXIT_TEMPLATE.md)
- [Independent review records](reviews/)

No private conversation or AI-specific memory replaces these durable sources.
