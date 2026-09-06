# State and Authority

## 1. Objective State

States:

- `DRAFT`
- `ACTIVE`
- `BLOCKED`
- `SATISFIED`
- `FAILED`
- `CANCELLED`
- `EXPIRED`
- `ARCHIVED`

An Objective is a finite goal with explicit acceptance criteria or an acceptance authority.

`SATISFIED` MUST NOT be inferred solely from Task completion percentage.

## 2. Task State

States:

- `DRAFT`
- `READY`
- `IN_PROGRESS`
- `BLOCKED`
- `COMPLETED`
- `FAILED`
- `CANCELLED`

Task start and cancellation are controlled by the requester, scheduler, or authorized governance according to policy.

Workers MAY request transitions but MUST NOT directly execute authoritative Task transitions.

A Task becomes `COMPLETED` only when its Completion Policy is satisfied.

## 3. Run State

States:

- `PENDING`
- `RUNNING`
- `WAITING_FOR_VERIFICATION`
- `RETRYING`
- `REASSIGNED`
- `COMPLETED`
- `FAILED`
- `ABORTED`

All Run transitions are controlled by the scheduler/run controller.

A worker MUST NOT self-declare authoritative Run completion.

`COMPLETED` means the Run terminated normally according to execution semantics. It does not mean the result is correct.

## 4. Outcome State

States:

- `PROPOSED`
- `VALIDATING`
- `ACCEPTED`
- `REJECTED`
- `SUPERSEDED`
- `EXPIRED`

A worker MAY propose an Outcome.

Acceptance requires independent validation according to policy. Worker self-assessment is insufficient.

An accepted Outcome does not necessarily satisfy the parent Objective.

## 5. Evaluation State

States:

- `PENDING`
- `RUNNING`
- `COMPLETED`
- `CONFLICTED`
- `OVERRIDDEN`
- `INVALID`

Evaluation records are append-only in historical meaning.

An override MUST be represented by an additional arbitration or override record referencing the prior Evaluation. The previous Evaluation is not rewritten or deleted.

## 6. Effect State

States:

- `PLANNED`
- `SIMULATED`
- `PENDING_COMMIT`
- `COMMITTED`
- `ROLLED_BACK`
- `COMPENSATING`
- `COMPENSATED`
- `UNRESOLVED`

Effect commit authority is separate from worker execution and validation authority.

An Effect that occurred in the external world remains historically real even if later compensated.

## 7. Ownership and Mapping

Each Task has exactly one primary Objective.

A Task MAY contribute to additional Objectives through non-authoritative links.

Secondary contribution links do not automatically cause state transitions in other Objectives.

## 8. State Transition Authority

Default authority model:

| Object | Worker | Scheduler / Controller | Evaluator | Human / Governance |
|---|---|---|---|---|
| Objective | request only | manage operational transitions | evidence only | accept/reject/override as authorized |
| Task | request only | authoritative transitions | evidence only | cancel/redirect/override policy |
| Run | request only | authoritative transitions | verification input | abort/redirect when authorized |
| Outcome | propose only | lifecycle coordination | accept/reject recommendation or policy result | arbitrate/accept where required |
| Evaluation | provide evidence only | schedule evaluation | create evaluation records | override judgment by new record |
| Effect | propose intent only | coordinate | verify only | authorize when required |

No row grants a worker self-approval.

## 9. Constitutional Invariants

Constitutional invariants cannot be bypassed by ordinary administrator privileges.

Examples:

- audit history is append-only,
- evidence provenance is preserved,
- workers cannot approve their own results,
- evaluators cannot commit the effects they evaluate,
- committed irreversible effects cannot be rewritten as nonexistent,
- overrides themselves must be auditable.

## 10. Policy Overrides

Operational policies MAY be overridden by authorized humans.

Examples:

- budget limit,
- retry count,
- confidence threshold,
- deadline,
- model selection,
- a scoped permission rule.

Every override requires a `PolicyOverride` record containing at least:

- actor,
- reason,
- target,
- scope,
- prior policy,
- effective override,
- creation time,
- expiration when applicable,
- acknowledged risk.

High-risk overrides MAY require multi-party approval.

## 11. No Direct Database State Editing

Human and system actors should transition state through the same authoritative transition service.

Administrative interfaces MUST NOT normally perform raw status updates that bypass transition validation or audit generation.
