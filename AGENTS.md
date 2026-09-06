# AGENTS.md

## Purpose

This repository implements an outcome-oriented AI work orchestrator. The orchestrator manages work, not specific agents. Agents, models, skills, tools, and sandboxes are replaceable execution resources.

This file is a navigation map, not the full specification.

## Read First

Before making changes, read the documents relevant to the task:

- `CONSTITUTION.md` — highest-precedence project rules and amendment process.
- `VISION.md` — product purpose, non-goals, and long-term direction.
- `ARCHITECTURE.md` — system boundaries, core entities, planes, and invariants.
- `ROADMAP.md` — staged implementation order.
- `docs/core-beliefs/TRUST_MODEL.md` — claims, evidence, facts, judgments, policies, and trust hierarchy.
- `docs/core-beliefs/STATE_AND_AUTHORITY.md` — state machines, transition authority, invariants, and human override rules.
- `docs/core-beliefs/EXECUTION_ISOLATION.md` — worker isolation, network, credentials, and sandbox assumptions.
- `docs/core-beliefs/VERIFICATION_MODEL.md` — evidence-based dynamic verification.
- `docs/core-beliefs/FAILURE_AND_RECOVERY.md` — checkpoints, Resume, Rewind, Reassign, recovery, and handoff.
- `docs/core-beliefs/EFFECTS_AND_SIDE_EFFECTS.md` — external effects, authorization, rollback, compensation, and idempotency.
- `docs/core-beliefs/LEARNING_AND_REPUTATION.md` — audit isolation, delayed learning, reliability, and policy evolution.

## Non-Negotiable Rules

1. A worker is untrusted by default.
2. A worker MUST NOT directly control authoritative state transitions.
3. A worker MAY make structured requests, but MUST NOT grant itself permissions, budget, acceptance, or completion.
4. All worker execution MUST occur inside an approved sandbox boundary.
5. Task state, run state, checkpoints, evidence, audit history, and policy state MUST survive worker loss.
6. Worker claims are not evidence.
7. Evaluation MUST be independent from execution.
8. An evaluator MUST NOT commit external effects it validates.
9. Important external effects MUST use the Effect Controller path.
10. Irreversible effects require explicit human authorization unless a future constitutional amendment changes this rule.
11. Historical facts, evidence provenance, and audit records MUST NOT be rewritten by normal application flows.
12. Human operators MAY override policy or judgment when authorized, but MUST NOT rewrite facts or bypass constitutional invariants.
13. New agents MUST integrate through an adapter/driver boundary. Orchestrator core MUST NOT depend on agent-specific protocol details.
14. Planner output is a `TaskProposal`, not an executable `Task`.
15. No new top-level domain concept or cross-cutting dependency may be added without an ADR.

## Development Discipline

For substantial changes:

1. Determine whether the change is architectural.
2. If architectural, write or update an ADR before implementation.
3. For multi-step implementation, create a versioned plan under `docs/exec-plans/active/`.
4. Split work into bounded tasks with explicit scope, out-of-scope items, and acceptance criteria.
5. Prefer deterministic tests and objective evidence over prose assertions.
6. Do not broaden task scope opportunistically.
7. Update relevant architecture documentation in the same change when behavior or invariants change.

## Current Implementation Bias

The initial control plane is expected to use Python, a simple persistence layer, and Docker as the first sandbox provider. These are implementation choices, not permanent product identity. Interfaces MUST preserve future substitution.
