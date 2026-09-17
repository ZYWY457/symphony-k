# Documentation Map

Start with the root [project status](../STATUS.md), then follow the authority and reading order in [AGENTS.md](../AGENTS.md).

The accepted current product identity is a framework-neutral governance/control-plane system for agentic work. Constitution v0.2 and ADR-0009 are accepted; R2 product definition and R3 delivery path are Human accepted. R4 is reconciling canonical workflows, handoff and cold-start navigation. Issue #79 remains BLOCKED / NOT RELEASED.

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

## Product and delivery truth

- [Current status](../STATUS.md)
- [Vision](../VISION.md)
- [Architecture](../ARCHITECTURE.md)
- [v1 Product Contract](V1_PRODUCT_CONTRACT.md)
- [Canonical roadmap](../ROADMAP.md)
- [Development path](DEVELOPMENT_PATH.md)
- [Canonical reference workflows](REFERENCE_WORKFLOWS.md)

The accepted v1 critical path centers on governance facade, trusted evidence/Evaluation, governed Effect gateway and reconciliation, audit reconstruction, conformance, integrations, operational safety, hardening and v1 acceptance.

Generic Planner, Router, learned routing/reputation, multiple complete Agent runtimes and ownership of a production sandbox runtime are not mandatory v1 blockers.

## Exec Plans

- [Lifecycle rules](exec-plans/README.md)
- [Planned parent plans](exec-plans/planned/) — future or historical planning artifacts; no execution authority by themselves
- [Active plans](exec-plans/active/) — may contain historically accepted technical assets; current authority must be confirmed through `STATUS.md` and the current TaskSpec
- [Completed plans](exec-plans/completed/) — accepted historical plans

The historical Stage 2 active plan preserves accepted M1/M1C provenance but the old runtime-first implementation sequence is superseded for v1 delivery. Issue #79 must not be revived or repurposed.

## Handoff and governance templates

- [AI and maintainer handoff](AI_HANDOFF.md)
- [Durable TaskSpec template](TASKSPEC_TEMPLATE.md)
- [Human stage-exit template](STAGE_EXIT_TEMPLATE.md)
- [Independent review records](reviews/)

No private conversation or AI-specific memory replaces these durable sources.
