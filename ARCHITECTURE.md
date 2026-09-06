# Architecture

## 1. Architectural Principle

The orchestrator manages work. Execution resources are replaceable.

The architecture is divided into three primary planes plus a human governance layer.

### Control Plane

Responsible for:

- Objective lifecycle,
- TaskProposal governance,
- Task lifecycle,
- planning,
- routing,
- scheduling,
- budget,
- risk,
- value,
- confidence,
- verifiability,
- permission envelopes,
- policy decisions.

### Execution Plane

Responsible for:

- AgentDriver adapters,
- models,
- skills,
- tools,
- sandboxes,
- workspaces,
- Runs,
- execution telemetry.

### Verification and Safety Plane

Responsible for:

- evidence collection,
- validation planning,
- static and dynamic verification,
- semantic and logical verification,
- confidence gating,
- anomaly detection,
- circuit breaking,
- evaluation records,
- recovery coordination,
- rollback and compensation evidence,
- audit,
- reliability and reputation inputs.

### Human Governance Layer

Humans may:

- accept or reject objectives where required,
- authorize sensitive or irreversible effects,
- resolve conflicts,
- approve policy overrides,
- perform break-glass actions under strict audit,
- amend constitutional rules.

Humans do not rewrite historical facts.

## 2. Core Domain Objects

### Objective

A finite, bounded, verifiable business or operational goal.

An Objective is not a permanent strategy or vague mission. It has a desired state and an acceptance boundary.

Example: `Restore successful payment processing for the affected payment path.`

Long-term strategy belongs in portfolio or strategic context metadata, not the core state machine.

### Task

A bounded unit of work created to contribute to an Objective.

A Task has exactly one `primary_objective` for ownership, budget attribution, and lifecycle authority. A Task MAY also have non-authoritative contribution links to other Objectives.

Contribution links MUST NOT automatically propagate authoritative state transitions across Objectives.

### Run

One concrete execution attempt for a Task using a specific execution profile.

A Task may have multiple Runs. Runs may use different agents, models, tools, skills, permissions, and sandboxes.

### Outcome

A candidate result produced by a Run.

An Outcome is not truth and is not equivalent to Objective satisfaction. It remains a candidate until independently validated and accepted according to policy.

### Evaluation

An immutable validation record concerning a Run, Outcome, Effect, or related evidence.

An Evaluation records evidence, methods, judgments, conflicts, and provenance. It is not itself an unquestionable fact.

### Effect

A planned or executed change to the external world.

Examples include sending a message, changing a remote system, publishing content, charging money, deleting a cloud resource, deploying to production, or committing another externally visible side effect.

## 3. Relationships

```text
Objective
  |
  +-- Task A
  |     +-- Run A1
  |     |     +-- Outcome A1
  |     |     +-- Evaluation(s)
  |     |     +-- Effect(s)
  |     |
  |     +-- Run A2
  |           +-- Outcome A2
  |
  +-- Task B
        +-- Run B1
```

An accepted Outcome does not automatically satisfy its Objective.

Objective completion is controlled by an `ObjectiveCompletionPolicy` which may require:

- accepted Outcomes,
- required Tasks,
- confirmed Effects,
- required Evaluations,
- absence of unresolved critical risks,
- explicit human acceptance.

Progress percentages are advisory only unless explicitly defined as authoritative by policy.

## 4. Agent Boundary

The Orchestrator does not require external agents to implement one universal wire protocol.

Instead, each integration implements an `AgentDriver` adapter.

The minimal driver contract is expected to expose concepts equivalent to:

- capabilities,
- start,
- send,
- resume,
- cancel,
- status,
- events,
- result,
- usage.

Agents may communicate internally through CLI, stdio, JSON-RPC, HTTP, WebSocket, MCP, or vendor-specific protocols. Those details MUST remain inside the driver.

Workers MAY emit structured requests such as:

- PermissionEscalationRequest,
- BudgetIncreaseRequest,
- HumanInputRequest,
- TaskClarificationRequest,
- DelegationRequest.

A worker request is never self-approval.

## 5. Planning Boundary

Planner output is a `TaskProposal`.

A TaskProposal is not executable until it passes the applicable governance path, including policy, budget, risk, permission, and other required checks.

The Planner MUST NOT obtain unlimited authority to create work, expand an Objective, allocate unlimited budget, or launch workers directly.

## 6. Execution Profiles

Routing selects an execution profile rather than only an agent.

An execution profile may include:

- agent,
- model/provider,
- skills,
- tools,
- sandbox provider and image,
- workspace strategy,
- permission envelope,
- network policy,
- secret capabilities,
- budget limit,
- timeout,
- verification requirements.

## 7. Persistence and Authority

Workers are never the authoritative system of record.

Authoritative state includes:

- Objective state,
- Task state,
- Run state,
- checkpoints,
- workspace references,
- evidence references,
- evaluation records,
- effects and receipts,
- permissions,
- cost ledger,
- audit events,
- policy versions.

This state MUST persist independently of worker processes and sandbox lifetime.

## 8. Invariant Enforcement Layers

Invariants are enforced at multiple layers.

### Database Layer

Use hard structural constraints when expressible:

- NOT NULL,
- foreign keys,
- uniqueness,
- CHECK constraints,
- immutable identifiers,
- version columns,
- transactional writes.

### Domain Transition Layer

All authoritative state changes pass through a controlled transition service. Application code MUST NOT arbitrarily assign state fields.

### Concurrency Layer

State mutation must support transaction boundaries, idempotency, and concurrency protection such as optimistic locking.

### Runtime Capability Layer

Security-sensitive restrictions must be physically enforced by sandboxes, network policy, credential brokers, and effect controllers rather than only application-level `if` statements.

## 9. Facts, Judgments, and Policies

The system distinguishes three levels:

### Facts

Historical or externally anchored facts such as:

- what action occurred,
- who requested it,
- what Effect was committed,
- what evidence artifact existed,
- what checksum or receipt was observed.

Facts are append-only and cannot be rewritten through normal governance.

### Judgments

Interpretations such as:

- whether an Outcome satisfies a requirement,
- whether a validator is reliable,
- whether a risk is acceptable.

Authorized governance may override a judgment, but the original judgment remains recorded.

### Policies

Operational rules such as:

- budget limits,
- retry thresholds,
- model preferences,
- confidence thresholds,
- approval thresholds.

Authorized humans may change or temporarily waive policy within scope.

## 10. Constitutional Invariants

The following are non-negotiable unless the constitution itself is amended:

1. Worker self-report MUST NOT be treated as proof of completion.
2. Workers MUST NOT directly mark their own authoritative Run, Task, Outcome, Evaluation, or Effect status as accepted/completed/committed.
3. An evaluator MUST NOT commit the Effect it evaluates.
4. A worker MUST NOT grant itself more permission or budget.
5. Audit records and evidence provenance MUST NOT be physically deleted through normal operations.
6. Historical Evaluations MUST NOT be silently rewritten.
7. A real committed Effect MUST NOT be relabeled as if it never occurred.
8. A compensated Effect MUST NOT be represented as a true rollback if the original side effect remained historically real.
9. Human override MUST itself be auditable.
10. All important state transitions MUST identify actor, reason, timestamp, previous state, new state, and policy context.
11. Agent-specific protocol details MUST NOT leak into orchestrator core domain semantics.
12. Work state MUST survive worker loss.
