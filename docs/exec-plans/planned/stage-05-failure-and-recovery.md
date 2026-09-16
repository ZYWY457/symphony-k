# Stage 05 — Failure and Recovery

**Status:** PLANNED — not implementation authorization
**Constitutional baseline:** `constitution-v0.1`

## Objective and why this stage exists

Ensure authoritative progress survives Worker, sandbox, process, host and
provider loss, and choose bounded recovery without rewriting attempt history.

## In scope

- `CheckpointManifest` and trusted versus incomplete checkpoint state;
- normalized `FailureClassifier`;
- `RecoveryController` with Resume, Rewind and Reassign;
- `HandoffPackage` and successor Run semantics;
- progress-stall and loop detection;
- recovery attempt, cost and time limits;
- workspace/artifact trust decisions and restart recovery.

## Out of scope

- Worker-selected authoritative recovery;
- reopening a closed Run or silently changing its execution route;
- blind replay of uncertain external Effects;
- unbounded retries and policy-free failover.

## Architecture boundaries

Recovery controllers request Stage 1 transitions and create new Run identities
where required. Checkpoints reference reconstructible, explicit state rather
than hidden reasoning. Route-specific diagnostics remain behind adapters.

## Expected new interfaces and concepts

`CheckpointManifest`, `CheckpointStore`, checkpoint trust status,
`FailureClassifier`, normalized failure detail, `RecoveryDecision`,
`RecoveryController`, `ExecutionProfileMutation`, `HandoffPackage` and progress
signals. ADRs must decide checkpoint atomicity/storage and recovery authority.

## Cross-stage dependencies

Requires Stages 1–4 and ADR-0006. Stage 6 must make recovery budget- and
Effect-aware; Stage 8 later selects alternative routes.

## Security and trust requirements

Checkpoint integrity and completeness are verified before use. Credentials and
hidden chain-of-thought are not checkpoint payloads. Preserved work remains
candidate material until explicitly trusted and verified. Effect uncertainty
blocks automatic replay.

## Failure model

Normalize transient, infrastructure, Worker, execution, validation, capability,
policy, budget, dependency, task-definition, safety and unrecoverable-side-
effect failures. Misclassification and exhausted recovery escalate visibly.

## Milestones

1. Accept checkpoint, failure-taxonomy and recovery authority ADRs.
2. Implement atomic checkpoint manifests and integrity validation.
3. Implement classification and bounded Resume.
4. Implement Rewind with explicit profile mutation and new attempt identity.
5. Implement Reassign/handoff/successor binding and stall detection.
6. Prove restart/failover/Effect-safety scenarios and complete Human review.

## Proposed bounded Issue decomposition

- checkpoint ADR/schema/store;
- normalized failure taxonomy;
- Resume controller;
- Rewind and profile mutation;
- Reassign/handoff/successor Run;
- stall/loop detection and recovery budgets;
- failure-injection suite and stage reconciliation.

## Validation strategy

Crash and restart tests; incomplete/corrupt/stale checkpoint rejection;
transient resume; invalid-path rewind; route reassignment; successor provenance;
loop signatures; limit exhaustion; retained artifact verification; and uncertain
Effect no-replay tests.

## Human Exit Review questions

- Does authoritative state survive every supported loss boundary?
- Are Resume, Rewind and Reassign semantically distinct and attributable?
- Is each new attempt represented by a new Run when required?
- Can untrusted checkpoints or candidate artifacts become authoritative?
- Can recovery duplicate an external Effect or exceed its policy limits?

## Stage Definition of Done

Bounded, auditable recovery survives representative losses without erasing
history, changing Run identity silently or replaying uncertain Effects. Human
Exit Review and reconciliation precede Stage 6.
