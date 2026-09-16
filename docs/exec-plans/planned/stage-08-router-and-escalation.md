# Stage 08 — Router and Escalation

**Status:** PLANNED — not implementation authorization
**Constitutional baseline:** `constitution-v0.1`

## Objective and why this stage exists

Resolve work onto eligible healthy execution routes using explicit constraints,
value and policy rather than a hard-coded Agent.

## In scope

- capability registry and execution requirement matching;
- `ExecutionProfile` and resolved execution-route contract;
- substrate, driver and capability health;
- rule-based route eligibility;
- cost- and reliability-aware routing inputs;
- permission, network, sandbox and budget compatibility;
- escalation/degradation policy and route/circuit health;
- attributable route decisions and no-route blocking.

## Out of scope

- learned routing before trustworthy Stage 10 evidence;
- vendor-special cases in Control Plane core;
- blind failover when Effect occurrence is uncertain;
- silent violation of Task locality, permission or model constraints.

## Architecture boundaries

Routing consumes normalized capabilities, health and policy. Adapters own
provider diagnostics. A route is a runtime/control-plane concept, not a seventh
Stage 1 domain entity. Reassignment creates a successor Run as required by
accepted lifecycle semantics.

## Expected new interfaces and concepts

Capability/requirement schema, registry, route candidate, resolved route,
eligibility decision, route-health observation, circuit policy, escalation and
degradation decisions. ADR-0006 is the baseline; further ADRs must settle exact
health states, scoring precedence and circuit behavior.

## Cross-stage dependencies

Requires sandbox, two drivers, verification, recovery and budget/permission/
Effect controls from Stages 2–7. Supplies governed route selection to Planner
outputs after Task promotion.

## Security and trust requirements

All hard constraints filter before optimization. Health cannot override policy;
model strength cannot override an unhealthy substrate. Decisions retain inputs,
policy version and reason. Missing capability/health evidence fails closed.

## Failure model

No eligible route, stale capability, unhealthy substrate, driver outage,
permission/budget incompatibility, circuit open, selection timeout and failure
during dispatch are distinct. Failover obeys recovery and Effect safety.

## Milestones

1. Accept capability, health, eligibility and circuit ADRs.
2. Implement registry and deterministic hard-constraint eligibility.
3. Add health collection and route/circuit state.
4. Add cost/reliability policy inputs and explainable selection.
5. Implement escalation/degradation and recovery-safe reassignment.
6. Complete simulations, failure tests and Human Exit Review.

## Proposed bounded Issue decomposition

- capability/requirements schema;
- registry and eligibility engine;
- route-health normalization and persistence;
- circuit breaker;
- cost/reliability selection policy;
- escalation/degradation and no-route handling;
- recovery/effect-safe routing integration;
- stage reconciliation.

## Validation strategy

Deterministic eligibility matrices, stale/missing capability cases, unhealthy
route exclusion, policy incompatibility, cost/reliability tradeoff fixtures,
circuit open/half-open recovery, no-route blocking, successor Run provenance
and uncertain-Effect failover denial.

## Human Exit Review questions

- Are hard constraints applied before preferences or scores?
- Can any vendor/platform detail leak into routing core?
- Is every selection and escalation reproducible from durable inputs?
- Does a route change preserve Run identity and trustworthy work?
- Can failover duplicate an Effect or exceed authority?

## Stage Definition of Done

Governed, explainable route selection uses explicit capability, health, cost,
reliability, budget and permission inputs; no Agent is hard-coded; unsafe or
impossible routing blocks/escalates. Human Exit reconciliation precedes Stage 9.
