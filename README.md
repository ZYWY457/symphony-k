# Symphony-K

## What Symphony-K is

Symphony-K is a **framework-neutral governance and trust control plane for
agentic work**. It is not another generic Agent orchestrator.

External agents, orchestrators and execution runtimes decide how work is
attempted. Symphony-K determines what may become authoritative, which evidence
is admissible for the exact scope under judgment, which consequential action is
allowed, what happened, and how the causal history can be reconstructed.

```text
external agent / orchestrator / runtime
        -> attempts work
        -> claims / evidence / requested Effects
        -> Symphony-K governance boundary
        -> authority / trusted evidence / Evaluation
        -> Effect governance / occurrence / reconciliation
        -> causal audit history
```

The accepted Stage 1 domain kernel remains the product core: Objective, Task, Run, Outcome, Evaluation and Effect stay semantically distinct; Worker claims are not facts; independent Evaluation/evidence is required for authoritative disposition; replay/concurrency/history semantics remain governed; and Effect occurrence is distinct from authorization.

Two principles shape the product:

- **Internal rigor, external simplicity.** Exact references, immutable
  fingerprints, trusted provenance, replay, concurrency, occurrence and causal
  history may require strict internals. Common integrations should still use a
  small supported surface and stable typed references. Simplicity must hide
  complexity behind trusted boundaries, never weaken governance invariants.
- **Own the semantics; reuse the mechanisms.** Symphony-K owns claim-versus-fact,
  authority, Evaluation, Effect occurrence, uncertainty and append-only-history
  semantics. It normally reuses IAM, databases, storage, queues, transports,
  workflow/Agent runtimes, sandbox providers, secret managers and observability
  through thin adapters.

Reusing a mechanism does not outsource semantic authority. IAM may establish
who authenticated; it does not decide which Outcome is authoritative. A
database persists records; it does not define trust eligibility. Runtime or API
success is neither Outcome acceptance nor proof that an Effect occurred.

## Strategic continuity

The long-term goal has remained substantially continuous: make agentic work
reliable, governable, evidence-backed, attributable and reconstructable. The
strategic transition changed the ownership boundary, not that goal.

The pre-transition direction leaned toward owning planning, routing,
scheduling, Agent/runtime execution, sandboxing and retry/failover mechanics.
That work remains valid historical design evidence. The current product focus
is the governance layer around exact identity/version, trusted evidence and
Evaluation, authoritative disposition, consequential Effects, uncertainty and
reconciliation, and append-only causal history.

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
- R5 final strategic disposition/release-boundary reconciliation is **COMPLETE AND HUMAN ACCEPTED** at `1bb48657a85d746b8d0023ddd805c6cdc09703b0`.
- Final strategic accepted-truth reconciliation is `b5ee78f7febae1346c771fa6060fcb3e18ea56f3`, reviewed **ACCEPT** on Issue #99 comment `5712355215`.
- Repository-level strategic transition R1-R5 is complete.
- Issue #79 is closed **SUPERSEDED / NOT RELEASED** as not planned; its old Stage 2 M2 authority is historical only and cannot be reused as post-transition execution authority.
- **G1 / M1 — Governance SDK / Facade Foundation is COMPLETE / ACCEPTED** at `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`; Issue #102 independent acceptance review is comment `5714651540`.
- The original Issue #100 candidate `36cb145fa666fa9a2218028d2d3828f28c0ed352` remains historical **NOT ACCEPTED** evidence; Issue #102 contains the forward correction lineage.
- **G2/M0 is COMPLETE / ACCEPTED** at `9c36fbcfac3854271af8eb15dca08f6a9ec2eca2`.
- **G2/M1 is COMPLETE / ACCEPTED** at implementation boundary `83a67c9fc98b1de7b42ad65772d8956f9b721915`; accepted-truth reconciliation is `67f91f00ed3d6491f4451b801a19ae20ac409905`.
- The original G2/M1 candidate `e5402b6415ab76a7fed5635949cfea335db2b5c6` remains historical **NOT ACCEPTED / CORRECTION REQUIRED** evidence.
- **G2/M2-M6 are NOT RELEASED. G3 is NOT RELEASED.**
- Issue #111 revision
  `r4 - strategic-narrative-cold-start-refresh-path-correction` is the current
  released repository-refresh TaskSpec. Its candidate does not become accepted
  truth until independent review under #115.
- Stage 2 runtime isolation evidence is not established and Stage 2 runtime code has not started.

The accepted G1 facade exposes typed exact entity/version references, caller-controlled submission DTOs separated from trusted authority/context construction, supported Run/Outcome/Evaluation mutations through an injected trusted binder, exact/current reads, caller-safe errors, replay/concurrency preservation and explicit unsupported real Effect dispatch. It does not add public Run completion or Outcome acceptance and does not define G2 trust policy.

Read [STATUS.md](STATUS.md) for the compact authoritative current summary.

External execution may be powerful, autonomous or provider-managed. It still cannot self-promote claims into authoritative truth, substitute stale evidence, grant itself consequential authority, erase occurrence history or bypass governed Effects.

## Project navigation

- [Status](STATUS.md) — current accepted baseline and released/blocked work
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
