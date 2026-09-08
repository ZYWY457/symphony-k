# Failure and Recovery

## Principle

All workers are temporary. All Runs may fail.

The authoritative state of work must survive worker loss, process crashes, sandbox destruction, host restart, provider outage, and reassignment.

## Checkpoint

A Checkpoint records a trusted recovery boundary.

It should contain or reference:

1. Task metadata and execution metadata,
2. portable Agent execution state,
3. reconstructible environment state and necessary incremental snapshots,
4. evidence-chain anchors.

### Portable Agent Execution State

The system must not depend on hidden model reasoning or inaccessible chain-of-thought.

Portable state may include:

- session/thread references when available,
- completed steps,
- current explicit plan,
- unresolved issues,
- explicit assumptions,
- tool call and result references,
- working notes intended for handoff,
- workspace revision,
- pending actions,
- permissions used,
- budget consumed and remaining.

### Environment State

Checkpointing should prefer reconstructible state over copying a full environment each time.

Possible references:

- container image digest,
- dependency lock hash,
- environment configuration references,
- workspace revision,
- filesystem delta,
- mounted resource references,
- selected runtime metadata.

### Trusted Checkpoint

Checkpoint creation should be logically atomic.

Only a complete manifest with consistent state, environment, and evidence references may become a trusted rewind target.

Incomplete checkpoints are not valid recovery anchors.

## Failure Classification

Recovery decisions require classification rather than a single `failed` flag.

Provider-, client-, runtime-, operating-system-, and agent-specific diagnostics
remain behind their adapters and drivers. The Control Plane consumes normalized
failure information; the detailed taxonomy for execution-route health is
deferred.

Initial classes:

- `TRANSIENT`
- `INFRA_FAILURE`
- `WORKER_FAILURE`
- `EXECUTION_FAILURE`
- `VALIDATION_FAILURE`
- `CAPABILITY_FAILURE`
- `POLICY_FAILURE`
- `BUDGET_FAILURE`
- `DEPENDENCY_FAILURE`
- `TASK_DEFINITION_FAILURE`
- `SAFETY_FAILURE`
- `UNRECOVERABLE_SIDE_EFFECT`

## Resume

Resume is used when the execution path remains trustworthy but execution was interrupted.

Typical triggers:

- network timeout,
- rate limiting,
- temporary provider outage,
- worker process crash without invalid state,
- host restart,
- scheduler resource suspension.

Resume attempts to continue from the latest trusted checkpoint without changing the fundamental execution strategy.

## Rewind

Rewind is used when the current execution path is no longer trustworthy but an earlier trusted checkpoint exists.

Possible triggers:

- validation failure caused by worker output,
- failing unit/integration tests,
- invalid output schema,
- repeated equivalent errors,
- progress stall,
- evidence suggesting a bad branch of execution.

Rewind may apply an `ExecutionProfileMutation`, such as:

- context pruning,
- prompt/template change,
- model parameter change when supported,
- model change,
- tool strategy change,
- skill change,
- planning strategy change.

Rewind attempts are bounded. Exceeding the configured limit escalates to Reassign or human intervention.

Worker self-confidence alone is not a sufficient Rewind authority signal.

## Reassign

Reassign is used when the Task remains valid but the current execution profile is no longer appropriate.

An execution-route failure normally establishes that the route is unhealthy or
ineligible for the Task; it does not by itself establish that the Task, model,
AgentDriver abstraction, repository, or toolchain is invalid. Every route must
pass base substrate and Task-specific capability preflight before repository
mutation. Route health and any future circuit breaking are runtime/control-plane
concerns, not Task lifecycle state.

Triggers may include:

- repeated Rewind failure,
- capability bottleneck,
- complexity escalation,
- newly discovered risk,
- permission requirements beyond the current envelope,
- unacceptable cost or latency,
- need for a specialist,
- need for human intervention.

Reassign may change:

- agent,
- model,
- skills,
- tools,
- sandbox,
- budget,
- permissions,
- verification requirements.

Reassign closes the prior Run as `REASSIGNED` only after a durable successor-Run
or human-handoff reference exists. The successor has a new RunId; a route change
does not silently mutate the execution identity or history of the prior Run.

## Handoff Package

A Reassign operation should create a structured handoff containing:

- TaskSpec,
- last trusted Checkpoint,
- workspace reference,
- attempt history,
- failure classification,
- failure evidence,
- evaluator feedback,
- known dead ends,
- known good findings,
- permission state,
- cost consumed,
- remaining budget,
- artifact references,
- evidence references,
- audit references.

A replacement worker should not need to rediscover validated history from scratch.

Route failure does not erase trustworthy workspace state, candidate artifacts,
checkpoints, evidence, or audit history. A successor may use preserved material
only through an explicit recovery decision and the required verification.

If an external Effect may have occurred, recovery must not blindly replay it
through another route. Occurrence evidence, deduplication, reconciliation,
authorization, and the Effect Controller path determine whether continuation is
safe; route failure is not evidence of non-occurrence.

## Loop and Progress-Stall Detection

Signals may include:

- repeated tool-call sequences,
- repeated error signatures,
- repeated nearly identical patches,
- repeated validation failures with the same root cause,
- no meaningful evidence gain,
- no meaningful workspace change,
- high semantic similarity across failed attempts.

## Recovery State Ownership

The Recovery Controller decides Resume/Rewind/Reassign according to classification and policy.

Workers may report failure or request recovery but do not select authoritative recovery state unilaterally.
