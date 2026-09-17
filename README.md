# Symphony-K

## What Symphony-K is

Symphony-K is a **framework-neutral governance/control-plane system for agentic work**.

External agents, orchestrators and execution runtimes may decide how work is attempted. Symphony-K governs what becomes authoritative truth, which evidence can justify a decision, who may authorize consequential Effects, how external actions cross the trusted boundary, and how historical facts remain attributable and reconstructable.

The accepted Stage 1 domain kernel remains the product core: Objective, Task, Run, Outcome, Evaluation and Effect stay semantically distinct; Worker claims are not facts; independent Evaluation/evidence is required for authoritative disposition; replay/concurrency/history semantics remain governed; and Effect occurrence is distinct from authorization.

## v1 direction

The post-transition v1 target is centered on:

- a stable governance SDK/facade;
- trusted independent Evaluation/evidence binding;
- exact authority and stale/superseded/cross-entity enforcement;
- a governed Effect gateway including occurrence uncertainty and reconciliation;
- durable audit reconstruction;
- adversarial/conformance evidence;
- at least one external agent/orchestrator integration; and
- at least one reference execution/provider path proving the governance boundary end to end.

The intended deployment posture is **embedded-first and service-capable**. A Python SDK may be the first integration surface; a stable local service/API and CLI may expose the same governance kernel for cross-process or non-Python consumers.

These are v1 product targets unless their implementation has separately completed and been accepted.

## What v1 no longer requires Symphony-K to own

The following are not mandatory v1 release blockers:

- a generic Planner;
- a generic Router;
- learned routing/reputation;
- multiple complete Agent runtimes; or
- a production sandbox runtime.

Planning, routing, execution and sandboxing may be supplied by external systems or reference/provider integrations. External ownership does not grant authority or make execution trusted by default.

The accepted Stage 2 sandbox architecture remains a valid technical asset: an execution-provider security/conformance boundary and optional/reference implementation path rather than Symphony-K's product identity.

## Current status

Stage 0 and Stage 1 are complete. The Human Stage 1 Exit Review is accepted.

The strategic transition to a framework-neutral governance/control-plane product has been explicitly Human approved. ADR-0009 and Constitution v0.2 are accepted. R1 acceptance reconciliation is published at `c0d08d697541675ad4f9e7f15717a0bad415b5a4`.

R2 product-definition reconciliation is **COMPLETE AND HUMAN ACCEPTED** at exact head `2b54c2672c0c400aab1f35e0245c8c4e97a62321`, after independent review **ACCEPT** on Issue #92 comment `5711134872` and explicit Human acceptance on comment `5711951534`. `VISION.md`, `ARCHITECTURE.md`, `docs/V1_PRODUCT_CONTRACT.md` and this README now define the accepted post-transition product identity. Post-transition SDK/Effect gateway/audit/conformance capabilities must not be treated as implemented merely because they are product requirements.

R3 delivery-plan reconciliation is next. `ROADMAP.md`, `docs/DEVELOPMENT_PATH.md` and the active Stage 2 delivery path still contain historical pre-transition sequencing until R3 is completed and accepted.

The Stage 2 M1 design remains a Human Accepted historical technical asset at `77acfbdaf2bed6f0536873fafc8eb7a12599da83`; runtime isolation evidence is not yet established and Stage 2 runtime code has not started.

Issue #79 remains **BLOCKED / NOT RELEASED**. No production implementation restart is authorized until the strategic reconciliation sequence completes and a fresh post-transition implementation TaskSpec is explicitly released.

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

- [Architecture](ARCHITECTURE.md) — governance kernel, integration and external execution boundaries
- [v1 Product Contract](docs/V1_PRODUCT_CONTRACT.md) — observable v1 responsibilities and acceptance boundary
- [Full roadmap](ROADMAP.md) — current historical delivery map pending R3 reconciliation
- [Complete development path](docs/DEVELOPMENT_PATH.md) — current historical stage/evidence/exit contracts pending R3 reconciliation
- [Reference workflows](docs/REFERENCE_WORKFLOWS.md) — canonical scenarios; workflow reconciliation follows in R4
- [AI and maintainer handoff](docs/AI_HANDOFF.md) — resume work without chat or account-specific memory
- [Constitution](CONSTITUTION.md) — highest-precedence project rules
- [Architecture decisions](docs/adr/README.md) — accepted ADRs including ADR-0009
- [Documentation map](docs/README.md) — core beliefs, designs and plans

Historical Stage 1 and Stage 2 work remains in accepted ADRs, design documents, completed/active Exec Plans and Git history rather than being rewritten to imply the post-transition product identity always existed.

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
