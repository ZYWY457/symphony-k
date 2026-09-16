# Stage 03 — First AgentDriver

**Status:** PLANNED — not implementation authorization
**Constitutional baseline:** `constitution-v0.1`

## Objective and why this stage exists

Define a replaceable Agent execution boundary and prove it with Codex as the
first adapter. Symphony-K manages work; an Agent/provider protocol must not
become core orchestration semantics.

## In scope

- `AgentDriver` contract and capability declaration;
- structured Agent request, response and event contracts;
- start, send, status, events, result, usage and cancel operations;
- resume where the provider supports it;
- Codex adapter as first implementation;
- provider-specific error normalization;
- binding a Run to an execution profile/route without vendor leakage.

## Out of scope

- second Agent runtime, routing/scoring, Planner and learned policy;
- Worker authority over Task/Run/Outcome lifecycle;
- direct host execution or bypass of the Stage 2 sandbox;
- treating provider session state as authoritative work state.

## Architecture boundaries

Agent protocol details stay in adapters. The driver emits claims, requests,
events and usage; controllers own authoritative transitions. Durable Task/Run,
checkpoint, evidence and audit truth remains outside provider sessions.

## Expected new interfaces and concepts

`AgentDriver`, `AgentCapabilities`, `AgentRequest`, `AgentEvent`,
`AgentResult`, `UsageReport`, `DriverSessionRef` and normalized driver failure.
An accepted ADR/design must fix versioning, event ordering, cancellation and
resume guarantees before implementation.

## Cross-stage dependencies

Requires Stages 1–2 and ADR-0003/0006. Supplies execution events and usage to
verification, recovery, budgeting and routing.

## Security and trust requirements

All Agent work runs through an approved sandbox and permission envelope.
Provider credentials are scoped outside the Worker where practical. Structured
requests never self-approve permission, budget, acceptance or completion.

## Failure model

Distinguish driver/protocol/provider/session/sandbox/cancellation/capability and
usage failures. Partial event streams are untrusted until durably ingested.
Cancellation is an attributed request/outcome, not proof the provider stopped.

## Milestones

1. Accept driver protocol, capability and event-ordering design.
2. Implement contract types and a deterministic fake driver.
3. Implement sandboxed Codex adapter.
4. Add usage, cancellation, supported resume and normalized errors.
5. Prove governed end-to-end Run execution and perform Human Exit Review.

## Proposed bounded Issue decomposition

- protocol/ADR and capability schema;
- driver contracts and fake conformance suite;
- Codex start/send/events/result adapter;
- usage/cancel/resume behavior;
- Run/profile/route binding and error normalization;
- sandboxed integration proof and stage reconciliation.

## Validation strategy

Cross-implementation contract tests, event ordering/replay, schema and malformed
message rejection, cancellation races, provider failure fixtures, usage
accounting, sandbox enforcement, restart/session-reference behavior and static
checks preventing Codex-specific imports in core domain.

## Human Exit Review questions

- Can the first provider be removed without core-domain changes?
- Are Agent outputs always claims/requests rather than authority?
- Does every execution remain bound to one auditable Run and sandbox route?
- Are provider failures normalized without destroying diagnostics?
- Can loss of a provider session leave durable work truth intact?

## Stage Definition of Done

A governed Task/Run executes through Codex via the AgentDriver and Stage 2
sandbox, with structured events/results/usage and no vendor coupling in the
domain kernel. Human Exit Review and governance reconciliation precede Stage 4.
