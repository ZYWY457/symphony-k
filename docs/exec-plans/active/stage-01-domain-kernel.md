# Stage 01 — Domain Kernel

**Status:** Draft
**Stage:** 01
**Constitution Baseline:** `constitution-v0.1`
**Primary Goal:** Establish the authoritative domain model, state machines, transition authority, invariants, domain events, and persistence boundaries that every later subsystem must obey.

---

## 1. Objective

Stage 1 establishes the smallest trustworthy kernel of the system.

The kernel MUST define and enforce the lifecycle of:

* `Objective`
* `Task`
* `Run`
* `Outcome`
* `Evaluation`
* `Effect`

It MUST also establish:

* explicit entity ownership and relationships;
* legal state transitions;
* transition authority;
* constitutional and operational invariants;
* immutable domain event generation;
* concurrency-safe transition semantics;
* persistence interfaces;
* deterministic validation of domain behavior.

Stage 1 does **not** execute AI agents.

Stage 1 does **not** evaluate real task results.

Stage 1 does **not** interact with the external world.

Its only responsibility is to make it impossible for later components to create logically invalid system state through normal application interfaces.

---

# 2. Why This Stage Exists

All future subsystems depend on this kernel:

```text
Planner
   ↓
TaskProposal
   ↓
Policy / Risk / Budget
   ↓
Task
   ↓
Scheduler
   ↓
Run
   ↓
Agent
   ↓
Outcome
   ↓
Verification
   ↓
Evaluation
   ↓
Effect Controller
```

If the meaning or lifecycle of these objects is ambiguous, every later subsystem will encode different assumptions.

Stage 1 therefore prioritizes:

```text
correctness
consistency
traceability
explicit authority
recoverability
```

over feature count.

---

# 3. Governing Documents

Implementation MUST comply with, in descending authority:

1. `CONSTITUTION.md`
2. `docs/core-beliefs/*`
3. accepted ADRs
4. `ARCHITECTURE.md`
5. this Exec Plan
6. individual implementation Issues
7. individual Codex prompts

A lower-level artifact MUST NOT override a higher-level rule.

If an implementation requirement conflicts with a constitutional rule, implementation MUST stop and produce a design escalation rather than silently working around the rule.

---

# 4. Stage 1 Scope

Stage 1 MUST implement:

## 4.1 Domain Entities

* `Objective`
* `Task`
* `Run`
* `Outcome`
* `Evaluation`
* `Effect`

## 4.2 Supporting Domain Types

At minimum:

* entity identifiers;
* actor identity / actor type;
* state enums;
* transition reason;
* timestamps;
* entity version;
* relationship references;
* completion policy references;
* provenance metadata;
* override metadata;
* immutable domain event representation.

## 4.3 State Transition Engine

A central mechanism MUST:

* validate source state;
* validate destination state;
* validate actor authority;
* validate required preconditions;
* validate entity version;
* produce a domain event;
* update state atomically;
* reject illegal transitions.

No normal application component may mutate lifecycle state directly.

## 4.4 Repository Boundaries

Persistence MUST be accessed through explicit repository interfaces.

Domain logic MUST NOT depend directly on a specific database engine.

## 4.5 Tests

Unit and integration tests MUST cover:

* every legal transition;
* representative illegal transitions;
* authority violations;
* invariant violations;
* concurrent modification protection;
* immutable event creation;
* relationship constraints.

---

# 5. Explicit Non-Goals

The following MUST NOT be implemented during Stage 1:

* Docker execution;
* sandbox management;
* Codex integration;
* any concrete `AgentDriver`;
* Hermes/OpenClaw/Grok integration;
* Planner implementation;
* `TaskProposal` generation;
* Agent Router;
* model routing;
* Budget Manager algorithms;
* Risk scoring algorithms;
* Value scoring algorithms;
* Confidence scoring algorithms;
* real Evaluator pipeline;
* LLM judge;
* Effect execution;
* Secret Broker;
* network policy enforcement;
* Checkpoint implementation;
* Resume / Rewind / Reassign execution;
* reputation scoring;
* learning pipeline;
* UI;
* GitHub Issue ingestion;
* distributed workers;
* message queues;
* Kubernetes;
* production deployment infrastructure.

If an implementation Issue begins introducing these capabilities, it has exceeded Stage 1 scope.

---

# 6. Core Domain Model

## 6.1 Objective

An `Objective` represents a finite, meaningful result requested by a human or authorized system.

An Objective MUST be:

* bounded;
* capable of eventual acceptance or failure;
* independently identifiable;
* associated with an acceptance authority;
* separate from the Tasks used to achieve it.

An Objective MUST NOT represent indefinite strategy such as:

```text
"continuously improve quality"
"become more competitive"
"always optimize costs"
```

Those belong in portfolio, strategy, policy, or contextual metadata.

Valid examples:

```text
Restore the production payment path.

Deliver Stage 1 of the orchestrator domain kernel.

Migrate service X from API v1 to API v2.
```

### Objective States

```text
DRAFT
ACTIVE
BLOCKED
SATISFIED
FAILED
CANCELLED
EXPIRED
ARCHIVED
```

### Semantics

**DRAFT**
Defined but not yet authorized for execution.

**ACTIVE**
Authorized and capable of generating or owning work.

**BLOCKED**
Still valid, but cannot currently progress.

**SATISFIED**
Its completion policy has been satisfied and its acceptance authority has accepted the objective.

**FAILED**
The requested objective cannot be achieved under the currently accepted constraints.

**CANCELLED**
Explicitly terminated before satisfaction.

**EXPIRED**
No longer valid because its allowed time horizon has ended.

**ARCHIVED**
Terminal historical state retained for long-term record keeping.

---

# 7. Task

A `Task` is an executable unit of work created in service of a primary Objective.

It represents **what must be accomplished**, not how a specific Agent attempts it.

Every Task MUST have exactly one:

```text
primary_objective_id
```

A Task MAY have zero or more non-authoritative contribution links to other Objectives.

```text
Task
├── primary_objective_id
└── contributes_to[]
```

Contribution links MUST NOT automatically propagate lifecycle state.

### Task States

```text
DRAFT
READY
IN_PROGRESS
BLOCKED
COMPLETED
FAILED
CANCELLED
```

### Semantics

**DRAFT**
Task definition exists but is not executable.

**READY**
Task definition is valid and eligible for scheduling.

**IN_PROGRESS**
At least one authorized Run is actively attempting the Task or the Task remains actively owned by execution control.

**BLOCKED**
Task cannot currently progress because of unmet dependency, missing authorization, missing input, or unresolved external condition.

**COMPLETED**
The Task's Completion Policy has been satisfied.

**FAILED**
The Task is considered unsuccessful under the currently allowed recovery policy.

**CANCELLED**
Execution is intentionally terminated.

---

# 8. Run

A `Run` is one concrete execution attempt for a Task.

A Task MAY have multiple Runs.

A Run MUST belong to exactly one Task.

A Run identifies a specific execution attempt and MUST remain historically distinguishable from all other attempts.

### Run States

```text
PENDING
RUNNING
WAITING_FOR_VERIFICATION
RETRYING
REASSIGNED
COMPLETED
FAILED
ABORTED
```

### Semantics

**PENDING**
Run exists but execution has not started.

**RUNNING**
Execution is active.

**WAITING_FOR_VERIFICATION**
Execution activity has stopped and one or more candidate Outcomes are awaiting verification.

**RETRYING**
The same execution strategy remains valid and another attempt is being prepared or initiated.

**REASSIGNED**
The current execution profile is no longer suitable and responsibility has been transferred to another execution profile or human.

**COMPLETED**
The Run lifecycle has closed normally.

This does **not** mean its Outcome is correct.

**FAILED**
The Run ended unsuccessfully and cannot continue under its current recovery path.

**ABORTED**
The Run was forcibly terminated by scheduler, policy, safety control, or authorized human action.

---

# 9. Outcome

An `Outcome` is a candidate result produced by a Run.

An Outcome is never automatically trusted.

A Run MAY produce zero, one, or multiple Outcomes.

An Outcome MUST retain provenance to the Run that produced it.

### Outcome States

```text
PROPOSED
VALIDATING
ACCEPTED
REJECTED
SUPERSEDED
EXPIRED
```

### Semantics

**PROPOSED**
A candidate result exists.

**VALIDATING**
Verification is in progress.

**ACCEPTED**
Independent verification and applicable acceptance policy determined the candidate result is acceptable.

**REJECTED**
Verification determined the candidate result is not acceptable.

**SUPERSEDED**
A newer or better Outcome replaced this Outcome without erasing its history.

**EXPIRED**
The Outcome is no longer valid because its assumptions, time window, dependencies, or external conditions are stale.

---

# 10. Evaluation

An `Evaluation` is a verification record concerning an Outcome, Run, or other explicitly supported target.

An Evaluation is:

```text
evidence
+
verifier identity
+
method
+
verdict
+
confidence
+
reasoning summary
+
provenance
```

An Evaluation is not final truth.

Evaluations MAY conflict.

Evaluation records MUST NOT be physically deleted through normal system operation.

### Evaluation States

```text
PENDING
RUNNING
COMPLETED
CONFLICTED
OVERRIDDEN
INVALID
```

### Semantics

**PENDING**
Evaluation has been requested.

**RUNNING**
Verification process is active.

**COMPLETED**
The evaluator produced a valid recorded verdict.

**CONFLICTED**
Material disagreement exists between relevant evaluation evidence or evaluators.

**OVERRIDDEN**
An authorized arbitration decision superseded the effective use of this Evaluation.

The original record MUST remain intact.

**INVALID**
The Evaluation itself is unusable because of corrupted evidence, invalid methodology, verifier failure, or other provenance defect.

---

# 11. Effect

An `Effect` represents an intended or actual mutation of external state.

Examples include:

* modifying production infrastructure;
* sending an email;
* creating a GitHub pull request;
* publishing content;
* deleting data;
* transferring money;
* invoking an external API that changes state.

Effects MUST be modeled separately from Task execution.

### Effect States

```text
PLANNED
SIMULATED
PENDING_COMMIT
COMMITTED
ROLLED_BACK
COMPENSATING
COMPENSATED
UNRESOLVED
```

### Semantics

**PLANNED**
An external side effect has been proposed.

**SIMULATED**
The expected effect has been tested or prepared without committing real-world mutation.

**PENDING_COMMIT**
Required validation has passed and the Effect is waiting for commit authorization or execution.

**COMMITTED**
The external mutation was actually executed.

**ROLLED_BACK**
A genuinely reversible Effect was restored to its prior state.

**COMPENSATING**
A compensating action for a partially reversible or irreversible Effect is currently being performed.

**COMPENSATED**
The compensating action completed.

This MUST NOT be represented as if the original Effect never occurred.

**UNRESOLVED**
The Effect cannot currently be safely rolled back or compensated.

---

# 12. Relationship Topology

Canonical relationship model:

```text
Objective
    │
    ├── owns → Task
    │            │
    │            ├── Run
    │            │    ├── Outcome
    │            │    ├── Evaluation
    │            │    └── Effect
    │            │
    │            └── Effect
    │
    └── receives non-authoritative contribution links from other Tasks
```

Required cardinality:

```text
Task     → exactly one Primary Objective
Run      → exactly one Task
Outcome  → exactly one originating Run
```

Evaluation targets MUST be explicit.

Effect provenance MUST be explicit.

No relationship may depend only on free-form text.

---

# 13. Authority Model

Stage 1 MUST define actor categories even if later components are not yet implemented.

Minimum actor types:

```text
REQUESTER
SCHEDULER
RUN_CONTROLLER
WORKER
EVALUATOR
ARBITRATOR
EFFECT_CONTROLLER
POLICY_ENGINE
HUMAN_OPERATOR
SYSTEM
```

An actor identity and actor type MUST be recorded for every lifecycle transition.

---

# 14. Worker Authority

A Worker MAY:

* report execution progress;
* emit claims;
* propose an Outcome;
* request completion;
* request additional input;
* request retry;
* request permission escalation;
* request budget escalation;
* request reassignment.

A Worker MUST NOT:

* directly mutate lifecycle state;
* mark its own Run `COMPLETED`;
* accept its own Outcome;
* override an Evaluation;
* commit an Effect through domain state mutation;
* rewrite audit history;
* grant itself permission.

Worker requests are data.

They are not authority.

---

# 15. State Transition Authority

## Objective

Requester / authorized human / policy-controlled orchestration may initiate Objective lifecycle changes.

`SATISFIED` MUST require Objective Completion Policy satisfaction and acceptance authority.

No Worker may directly transition Objective state.

---

## Task

Requester or authorized orchestration may create, activate, block, cancel, or close Tasks according to policy.

Worker may request state changes but may not perform them.

`COMPLETED` MUST only be produced after Task Completion Policy passes.

---

## Run

Only Scheduler / Run Controller / Recovery Controller-equivalent authority may transition Run lifecycle state.

Worker self-report MUST NOT change authoritative Run state.

---

## Outcome

Worker may propose an Outcome.

Independent verification and applicable acceptance policy control `ACCEPTED` or `REJECTED`.

A Worker MUST NOT accept an Outcome it produced.

---

## Evaluation

Evaluator controls normal Evaluation lifecycle.

Arbitrator or authorized Human may override the effective judgement.

Override MUST create a new auditable record and MUST NOT rewrite the original Evaluation.

---

## Effect

Effect execution authority MUST remain separate from Effect verification authority.

Worker may propose Effect intent.

Worker MUST NOT directly cause authoritative Effect state transitions through the domain model.

Actual commit authority belongs to an Effect Controller or explicitly authorized human/system boundary.

---

# 16. Constitutional Invariants

The following MUST NOT be bypassed through normal system operation.

## INV-001 — Worker Cannot Self-Complete

A Worker MUST NOT transition its own Run to `COMPLETED`.

---

## INV-002 — Worker Cannot Self-Accept

A Worker MUST NOT accept an Outcome it produced.

---

## INV-003 — Evaluation and Execution Separation

The actor responsible for execution MUST NOT be the sole authority validating that execution.

---

## INV-004 — Effect Commit and Effect Verification Separation

The component committing an Effect MUST NOT be the sole verifier of that Effect.

---

## INV-005 — Facts Are Append-Only

Historical facts MUST NOT be rewritten to create a false history.

---

## INV-006 — Evaluation History Is Preserved

An Evaluation MAY be superseded or overridden but MUST NOT be physically deleted through normal operation.

---

## INV-007 — Effect History Is Preserved

A committed Effect MUST remain historically recorded even after rollback or compensation.

---

## INV-008 — Compensation Is Not Rollback

`COMPENSATED` MUST NOT imply that the original Effect did not occur.

---

## INV-009 — Provenance Is Mandatory

Run, Outcome, Evaluation, and Effect records MUST retain explicit provenance.

---

## INV-010 — Task Has One Primary Objective

Every executable Task MUST belong to exactly one Primary Objective.

Secondary contribution relationships MUST NOT imply ownership.

---

## INV-011 — Contribution Links Do Not Propagate State

Secondary Objective contribution links MUST NOT automatically change Objective lifecycle state.

---

## INV-012 — Run Completion Does Not Imply Outcome Acceptance

A completed Run MUST NOT automatically produce an accepted Outcome.

---

## INV-013 — Outcome Acceptance Does Not Automatically Satisfy Objective

Objective satisfaction MUST be decided by its own Completion Policy and acceptance authority.

---

## INV-014 — Human Cannot Rewrite Facts

Authorized human action MAY override policy or judgement but MUST NOT rewrite provenance, historical facts, committed Effects, or prior Evaluation records.

---

## INV-015 — State Mutations Use Transition Engine

Normal application code MUST NOT directly assign lifecycle state.

---

## INV-016 — Every Transition Is Attributed

Every lifecycle transition MUST record:

* entity;
* prior state;
* new state;
* actor identity;
* actor type;
* reason;
* timestamp;
* resulting version;
* related request or decision reference when applicable.

---

# 17. Operational Policies vs Constitutional Invariants

The system MUST distinguish:

```text
FACT
JUDGEMENT
POLICY
```

## Facts

Examples:

* an Effect was committed;
* an Evaluation occurred;
* a Run produced a specific artifact;
* actor X requested transition Y.

Facts MUST NOT be rewritten.

## Judgements

Examples:

* Outcome is acceptable;
* Evaluation is reliable;
* risk is tolerable.

Judgements MAY be overridden by authorized arbitration.

The original judgement MUST remain recorded.

## Policies

Examples:

* maximum retry count;
* cost threshold;
* confidence threshold;
* acceptable model class;
* timeout.

Policies MAY change or be waived by authorized actors.

Policy changes MUST be versioned and auditable.

---

# 18. Human Override

Human governance MUST operate through explicit domain actions.

Humans MUST NOT normally mutate persistence state directly.

Human override MUST create an auditable object or event containing at minimum:

```text
override_id
actor
target
scope
reason
prior_effective_decision
new_effective_decision
timestamp
policy_version
risk_acknowledgement where applicable
```

Human override MAY change:

* policy;
* operational threshold;
* effective judgement;
* retry limit;
* budget limit;
* scheduling decision.

Human override MUST NOT:

* erase historical Evaluation;
* erase committed Effect history;
* falsify provenance;
* claim a rollback occurred when only compensation occurred;
* change evidence content while preserving the original evidence identity.

---

# 19. Break-Glass Principle

Stage 1 MAY define the domain representation of emergency `BREAK_GLASS` authorization but MUST NOT implement operational infrastructure around it.

A Break-Glass record MUST include:

* explicit actor;
* reason;
* scope;
* start time;
* expiry;
* affected entities;
* acknowledgement of elevated risk.

Break-Glass authority MUST NOT bypass constitutional facts or history preservation.

---

# 20. Completion Policies

Completion MUST be policy-driven rather than inferred from raw child counts.

Example:

```text
Objective:
  10 Tasks
  9 completed
```

MUST NOT imply:

```text
Objective = 90% satisfied
```

Progress indicators MAY exist later but MUST be non-authoritative.

A Completion Policy MAY eventually depend on:

```text
required accepted outcomes
required completed tasks
required evaluations
required committed effects
absence of unresolved critical effects
absence of blocking evaluations
human acceptance
```

Stage 1 MUST provide an interface or representation for Completion Policy evaluation.

Stage 1 does NOT need to implement a general policy language.

---

# 21. Domain Events

Every successful lifecycle mutation MUST emit an immutable domain event.

Minimum event family:

```text
ObjectiveCreated
ObjectiveActivated
ObjectiveBlocked
ObjectiveSatisfied
ObjectiveFailed
ObjectiveCancelled
ObjectiveExpired
ObjectiveArchived

TaskCreated
TaskReadied
TaskStarted
TaskBlocked
TaskCompleted
TaskFailed
TaskCancelled

RunCreated
RunStarted
RunWaitingForVerification
RunRetrying
RunReassigned
RunCompleted
RunFailed
RunAborted

OutcomeProposed
OutcomeValidationStarted
OutcomeAccepted
OutcomeRejected
OutcomeSuperseded
OutcomeExpired

EvaluationRequested
EvaluationStarted
EvaluationCompleted
EvaluationConflicted
EvaluationOverridden
EvaluationInvalidated

EffectPlanned
EffectSimulated
EffectPendingCommit
EffectCommitted
EffectRolledBack
EffectCompensationStarted
EffectCompensated
EffectUnresolved

PolicyOverrideRecorded
BreakGlassRecorded
TransitionRejected
```

Event naming may change during implementation, but semantic coverage MUST remain.

---

# 22. Event Record Requirements

Every event MUST include at minimum:

```text
event_id
event_type
entity_type
entity_id
entity_version
actor_id
actor_type
timestamp
correlation_id
causation_id
reason
metadata
```

`correlation_id` SHOULD allow all events belonging to the same higher-level operation to be grouped.

`causation_id` SHOULD identify which prior event/request caused the current event.

---

# 23. State Transition Engine

All lifecycle changes MUST use one centralized domain transition mechanism.

Conceptually:

```text
transition(
    entity,
    target_state,
    actor,
    reason,
    expected_version,
    context
)
```

The transition operation MUST:

1. load authoritative current state;
2. verify entity version;
3. verify legal transition;
4. verify actor authority;
5. verify required invariants;
6. verify required preconditions;
7. create state mutation;
8. increment entity version;
9. append domain event;
10. persist mutation and event atomically.

If any step fails:

```text
NO authoritative state mutation occurs.
```

---

# 24. Optimistic Concurrency

Every mutable aggregate root MUST expose an authoritative version.

Example:

```text
Run.version = 17
```

A mutation based on version 17 MUST fail if the stored version is already 18.

This prevents concurrent actors such as:

```text
Scheduler
Evaluator
Human
Recovery Controller
```

from silently overwriting one another.

Concurrency conflicts MUST be explicit and recoverable.

---

# 25. Persistence Boundary

Stage 1 MUST define repositories for aggregate roots.

Conceptual examples:

```text
ObjectiveRepository
TaskRepository
RunRepository
OutcomeRepository
EvaluationRepository
EffectRepository
EventRepository
```

Domain services MUST depend on repository interfaces rather than database-specific queries.

The persistence implementation MUST preserve:

* foreign-key relationships;
* version checks;
* uniqueness;
* required fields;
* append-only event behavior;
* transaction boundaries.

---

# 26. Database-Level Constraints

Where an invariant can be safely represented structurally, persistence SHOULD enforce it independently of application code.

Examples:

```text
NOT NULL
FOREIGN KEY
UNIQUE
CHECK
immutable primary IDs
version constraints
```

Examples that MUST be structurally protected:

```text
Run requires Task
Outcome requires originating Run
Task requires Primary Objective before READY
entity IDs are unique
```

Complex lifecycle and authority rules remain Domain-layer responsibilities.

---

# 27. Direct State Mutation Is Forbidden

The codebase MUST establish a structural convention preventing lifecycle mutations like:

```python
run.status = RunStatus.COMPLETED
```

outside explicitly authorized transition logic.

Tests SHOULD make accidental bypasses difficult to introduce.

Later repository review may add static checks or architectural tests.

---

# 28. Stage 1 Error Model

The kernel MUST distinguish at least:

```text
InvalidTransition
UnauthorizedTransition
InvariantViolation
ConcurrencyConflict
EntityNotFound
InvalidRelationship
CompletionPolicyNotSatisfied
ImmutableRecordViolation
```

These MUST be typed domain errors.

Generic exceptions MUST NOT be the normal mechanism for representing expected domain rejection.

---

# 29. Domain Purity

Core entity and transition rules SHOULD remain independent of:

* FastAPI;
* Docker;
* Codex;
* external model SDKs;
* web frameworks;
* GitHub;
* Redis;
* message brokers;
* UI concerns.

The Domain Kernel should remain executable under tests without any Agent, network access, or external service.

---

# 30. Stage 1 Milestones

## M1 — Repository and Python Foundation

Deliver:

* Python project skeleton;
* package structure;
* formatting/lint/type-check/test tooling;
* baseline CI-ready test command;
* domain module boundary.

No domain behavior beyond minimal scaffolding.

---

## M2 — Entity Identity and Shared Types

Deliver:

* typed entity IDs;
* actor identity;
* actor type;
* timestamps;
* versions;
* transition reason;
* shared domain errors.

Acceptance:

* no raw unvalidated state strings in domain APIs;
* IDs of different domain entity types cannot be accidentally mixed where type checking can prevent it.

---

## M3 — Objective and Task

Deliver:

* Objective entity;
* Task entity;
* relationships;
* states;
* legal transitions;
* Primary Objective enforcement;
* completion policy boundary.

Acceptance:

* all documented legal transitions pass tests;
* all representative illegal transitions fail;
* contribution links do not affect Objective status automatically.

---

## M4 — Run and Outcome

Deliver:

* Run entity;
* Outcome entity;
* Run → Task relationship;
* Outcome → Run provenance;
* lifecycle transitions;
* Worker authority restrictions.

Acceptance:

* Worker cannot self-complete Run;
* Worker cannot accept Outcome;
* Run completion does not imply Outcome acceptance.

---

## M5 — Evaluation

Deliver:

* Evaluation entity;
* immutable evaluation result history;
* conflict state;
* override relationship;
* invalidation semantics.

Acceptance:

* original Evaluation is preserved after override;
* override creates a separate auditable record;
* physical delete is unavailable through normal repository API.

---

## M6 — Effect

Deliver:

* Effect entity;
* Effect states;
* provenance;
* rollback vs compensation distinction.

Acceptance:

* `COMMITTED → COMPENSATED` cannot erase original commit history;
* `COMPENSATED` and `ROLLED_BACK` remain distinct;
* Worker cannot authoritatively commit Effect state.

No real external actions are executed in Stage 1.

---

## M7 — Transition Engine

Deliver:

* central transition service;
* transition tables/rules;
* authority checks;
* invariant checks;
* event generation.

Acceptance:

* no lifecycle state mutation is required outside transition engine;
* illegal transitions fail deterministically;
* every successful transition emits one authoritative event.

---

## M8 — Persistence and Atomicity

Deliver:

* repository interfaces;
* initial persistence implementation;
* transaction semantics;
* optimistic concurrency;
* event persistence.

Acceptance:

```text
state mutation + domain event
```

must commit atomically.

Concurrent stale update must be rejected.

---

## M9 — Constitutional Test Suite

Deliver tests specifically named around constitutional invariants.

Examples:

```text
test_worker_cannot_complete_own_run
test_worker_cannot_accept_own_outcome
test_run_completion_does_not_accept_outcome
test_effect_compensation_preserves_commit_history
test_evaluation_override_preserves_original_record
test_secondary_objective_link_does_not_propagate_state
test_human_override_cannot_rewrite_fact
test_stale_entity_version_is_rejected
```

These tests act as executable constitutional guardrails.

---

# 31. Acceptance Criteria

Stage 1 is complete only when all of the following hold.

## Domain Completeness

All six core entities exist:

```text
Objective
Task
Run
Outcome
Evaluation
Effect
```

Their relationships are explicit and tested.

---

## State Completeness

Every documented state is represented by a typed domain state.

Every legal state transition is defined.

Representative illegal transitions are tested.

---

## Authority Enforcement

The kernel rejects unauthorized transitions.

Worker restrictions are enforced by domain logic.

---

## Invariant Enforcement

All Stage 1 constitutional invariants are represented by tests.

---

## Persistence Safety

Entity relationships are structurally protected where possible.

Optimistic concurrency is enforced.

State mutation and event append are atomic.

---

## History Preservation

Evaluation and Effect histories cannot be silently rewritten.

Overrides append history rather than altering prior truth.

---

## Domain Independence

The kernel test suite runs without:

* Docker;
* Codex;
* model APIs;
* external network access.

---

## Quality Gate

At minimum:

```text
unit tests pass
integration tests pass
type checking passes
lint passes
format check passes
```

Exact tools may be chosen by implementation ADR or project configuration.

---

# 32. Stage 1 Definition of Done

Stage 1 is DONE when:

```text
the repository can represent
a complete authoritative lifecycle
from Objective creation
through Task and Run execution records
to Outcome, Evaluation, and Effect records
without executing any real Agent,
while preventing unauthorized or logically invalid
state transitions through tested domain invariants.
```

---

# 33. Codex Working Rules for This Stage

Every Codex implementation task MUST:

1. read `AGENTS.md`;
2. read `CONSTITUTION.md`;
3. read `ARCHITECTURE.md`;
4. read relevant `docs/core-beliefs/*`;
5. read this Exec Plan;
6. implement only the assigned Issue;
7. avoid adding future-stage infrastructure;
8. add or update tests for every behavioral change;
9. explain any discovered conflict with higher-level architecture instead of working around it;
10. leave the repository in a passing state.

Codex MUST NOT treat this Exec Plan as permission to implement the entire Stage in one Run.

---

# 34. Proposed Issue Decomposition

Stage 1 SHOULD initially be decomposed into bounded Issues approximately as follows:

```text
#1  Bootstrap Python project and test tooling

#2  Implement typed IDs, actors, versions, shared domain errors

#3  Implement Objective domain model and transitions

#4  Implement Task domain model and Primary Objective relationship

#5  Implement Run domain model and execution authority restrictions

#6  Implement Outcome domain model and provenance rules

#7  Implement Evaluation domain model and immutable override semantics

#8  Implement Effect domain model and rollback/compensation semantics

#9  Implement centralized transition engine

#10 Implement immutable domain event model

#11 Define repository interfaces

#12 Implement initial persistence adapter and transactions

#13 Implement optimistic concurrency protection

#14 Build constitutional invariant test suite

#15 Stage 1 architecture and documentation reconciliation
```

Actual Issue boundaries MAY be adjusted after Codex inspects the repository.

Any adjustment MUST preserve bounded scope and architectural ownership.

---

# 35. Exit Review

Before moving to Stage 2, perform a human architecture review answering:

```text
Can any Worker directly mutate authoritative lifecycle state?

Can any entity reach an impossible state through normal APIs?

Can history be rewritten instead of superseded?

Can concurrent actors silently overwrite one another?

Can an Outcome be accepted solely because its producing Worker says so?

Can a committed Effect disappear from history?

Can a secondary Objective relationship accidentally change lifecycle state?

Can Stage 1 run completely without an Agent or Docker?
```

If any answer is unsafe or ambiguous, Stage 1 remains open.

---

# 36. Deferred Design Questions

The following are intentionally deferred and MUST NOT block Stage 1 unless implementation proves a Domain Kernel assumption invalid:

* Checkpoint storage representation;
* HandoffPackage schema;
* Resume / Rewind / Reassign runtime mechanics;
* dynamic verification pipeline implementation;
* Safety Monitor implementation;
* Effect Controller execution protocol;
* Saga orchestration;
* network policy enforcement;
* Secret Broker;
* execution profiles;
* Worker capability registry;
* Planner implementation;
* Router scoring;
* Budget / Risk / Value / Confidence algorithms;
* audit-to-learning promotion pipeline;
* reputation calibration.

These belong to later Exec Plans.

---

# 37. Stage 1 Architectural Principle

The Stage 1 implementation should optimize for one property above all others:

> **Later components may request state changes, but only the Domain Kernel determines whether those changes are legal, attributable, and consistent with system history.**

The kernel is not an Agent framework.

It is the authoritative state and governance foundation upon which every future Agent capability depends.
