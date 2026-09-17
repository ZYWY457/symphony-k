# Documentation Map

Start with the root [project status](../STATUS.md), then follow the authority and
reading order in [AGENTS.md](../AGENTS.md).

The current governance work is the strategic-transition Human decision gate in
Issue #87, not a Stage 2 implementation release. The accepted Stage 2 M1 design
remains a historical technical asset, while the current product-identity
documents retain their accepted historical wording until explicit Human
approval and the required hierarchy reconciliation.

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
- [Design documents](design-docs/)
- [Accepted ADR-0008 sandbox boundary](adr/0008-stage-2-sandbox-execution-boundary.md)
- [Accepted Stage 2 M1 sandbox execution design](design-docs/sandbox-execution-v1.md)

Accepted ADRs and designs remain subordinate to the Constitution and core
beliefs. Material architecture changes use a new ADR rather than silently
rewriting accepted history.

## Current status and development path

- [Current status](../STATUS.md)
- [v1 Product Contract](V1_PRODUCT_CONTRACT.md)
- [Canonical roadmap](../ROADMAP.md)
- [Complete Stage 0–14 development path](DEVELOPMENT_PATH.md)
- [Canonical reference workflows](REFERENCE_WORKFLOWS.md)

## Exec Plans

- [Lifecycle rules](exec-plans/README.md)
- [Planned parent plans](exec-plans/planned/) — future contracts, no execution
  authorization
- [Active Stage 2 plans](exec-plans/active/) — accepted M1 technical history;
  the old M2 release path remains blocked during strategic reconciliation
- [Completed plans](exec-plans/completed/) — accepted historical plans

The normal lifecycle is `planned -> active -> completed`, with durable Human
activation and exit gates.

## Handoff and governance templates

- [AI and maintainer handoff](AI_HANDOFF.md)
- [Durable TaskSpec template](TASKSPEC_TEMPLATE.md)
- [Human stage-exit template](STAGE_EXIT_TEMPLATE.md)
- [Independent review records](reviews/) — durable review evidence when a
  review materially controls current execution or readiness

No private conversation or AI-specific memory replaces these durable sources.
