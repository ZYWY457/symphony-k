# Symphony-K

## What Symphony-K is

Symphony-K is a **framework-neutral governance/control-plane system for agentic work**.

External agents, orchestrators and execution runtimes may decide how work is attempted. Symphony-K governs what becomes authoritative truth, which evidence can justify a decision, who may authorize consequential Effects, how external actions cross the trusted boundary, and how historical facts remain attributable and reconstructable.

The accepted Stage 1 domain kernel remains the product core: Objective, Task, Run, Outcome, Evaluation and Effect stay semantically distinct; Worker claims are not facts; independent Evaluation/evidence is required for authoritative disposition; replay/concurrency/history semantics remain governed; and Effect occurrence is distinct from authorization.

## v1 direction

The accepted v1 target is centered on:

- a stable governance SDK/facade;
- trusted independent Evaluation/evidence binding;
- exact authority and stale/superseded/cross-entity enforcement;
- a governed Effect gateway including occurrence uncertainty and reconciliation;
- durable audit reconstruction;
- adversarial/conformance evidence;
- at least one external agent/orchestrator integration; and
- at least one reference execution/provider path proving the governance boundary end to end.

The deployment posture is **embedded-first and service-capable**. A Python SDK may be the first integration surface; a stable local service/API and CLI may expose the same governance kernel for cross-process or non-Python consumers.

These are v1 requirements, not claims that the post-transition implementation already exists.

## What v1 no longer requires Symphony-K to own

The following are not mandatory v1 release blockers:

- a generic Planner;
- a generic Router;
- learned routing/reputation;
- multiple complete Agent runtimes; or
- a production sandbox runtime.

Planning, routing, execution and sandboxing may be supplied by external systems or reference/provider integrations. External ownership does not grant authority or make execution trusted by default.

The accepted Stage 2 sandbox architecture remains a valid execution-provider security/conformance asset and optional/reference path rather than Symphony-K's product identity.

## Current status

Stage 0 and Stage 1 are complete. The Human Stage 1 Exit Review is accepted.

- Constitution v0.2 and ADR-0009 are accepted.
- R2 product-definition reconciliation is **COMPLETE AND HUMAN ACCEPTED** at `2b54c2672c0c400aab1f35e0245c8c4e97a62321`.
- R3 delivery-path reconciliation is **COMPLETE AND HUMAN ACCEPTED** at `f467fd75071e5d0252719539cf7323fb71de587c`.
- R4 workflow/cold-start reconciliation is **COMPLETE AND HUMAN ACCEPTED** at `ecccbedd68f2f0e0eff949c20b627f250ddf189e`.
- R5 final strategic disposition/release-boundary reconciliation is the current candidate under Issue #98 and still requires independent review plus explicit Human acceptance.
- Issue #79 remains **BLOCKED / NOT RELEASED** during the R5 gate. Its old Stage 2 M2 authority is obsolete for the post-transition product and cannot be reused as G1 authority.
- The first intended post-transition implementation slice is **G1 — Governance SDK / Facade Foundation**, but it is **NOT RELEASED** by the R5 candidate. A separate fresh TaskSpec may be released only after R5 acceptance and final reconciliation.
- Stage 2 runtime isolation evidence is not established and Stage 2 runtime code has not started.

Read [STATUS.md](STATUS.md) for the compact authoritative current summary.

## Architectural boundary

```text
external agent / orchestrator / runtime
        |
        | claims, candidate outcomes, evidence, requested Effects
        v
Symphony-K governance boundary
        |
        +--> authoritative state / exact authority
        +--> trusted independent Evaluation/evidence
        +--> governed Effect authorization/occurrence/reconciliation
        +--> durable causal audit
```

External execution may be powerful, autonomous or provider-managed. It still cannot self-promote claims into authoritative truth, substitute stale evidence, grant itself consequential authority, erase occurrence history or bypass governed Effects.

## Project navigation

- [Status](STATUS.md) — current accepted baseline, strategic gate and blocked/released work
- [Architecture](ARCHITECTURE.md) — governance kernel, integration and external execution boundaries
- [v1 Product Contract](docs/V1_PRODUCT_CONTRACT.md) — observable v1 responsibilities and acceptance boundary
- [Roadmap](ROADMAP.md) — accepted governance-centered v1 delivery map
- [Development path](docs/DEVELOPMENT_PATH.md) — accepted delivery contracts and evidence/exit boundaries
- [Reference workflows](docs/REFERENCE_WORKFLOWS.md) — canonical governance-boundary acceptance scenarios
- [AI and maintainer handoff](docs/AI_HANDOFF.md) — cold-start resume workflow without private memory
- [Constitution](CONSTITUTION.md) — highest-precedence project rules
- [Architecture decisions](docs/adr/README.md) — accepted ADRs including ADR-0009
- [Documentation map](docs/README.md) — core beliefs, designs and plans

Historical Stage 1 and Stage 2 work remains in accepted ADRs, design documents, Exec Plans and Git history rather than being rewritten to imply the post-transition product identity always existed.

## Development commands

Python **3.12 or newer** is required. `.python-version` selects Python 3.12 for the development baseline. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run from the repository root:

```text
uv sync --dev --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
```

`uv sync --dev` may be used when intentionally updating dependency resolution; keep `uv.lock` under version control with dependency changes. Tool configuration lives in `pyproject.toml`, package source in `src/symphony_k/`, and tests in `tests/`.
