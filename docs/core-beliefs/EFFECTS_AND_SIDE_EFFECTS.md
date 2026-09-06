# Effects and Side Effects

## Principle

External side effects are governed separately from worker reasoning and result validation.

Workers propose `EffectIntent`. A separate Effect Controller governs preparation, authorization, commit, verification, rollback, and compensation.

## Effect Intent

An EffectIntent should describe at least:

- effect type,
- target,
- intended payload or payload hash,
- required permissions,
- risk classification,
- reversibility,
- idempotency key where applicable,
- rollback or compensation plan,
- required authorization.

## Prepare–Verify–Authorize–Commit

The system should use a guarded sequence rather than claiming database-style distributed two-phase commit semantics.

### PREPARE

Generate and inspect the intended operation without committing the real external effect when possible.

Activities may include:

- dry-run,
- sandbox execution,
- staging environment execution,
- payload generation,
- target validation,
- rollback/compensation plan creation.

### VERIFY

Validate that the intended effect matches the Task and policy requirements.

### AUTHORIZE

Obtain the required policy and human approval.

Irreversible effects require explicit human authorization under the current constitution.

### COMMIT

The Effect Controller performs the real external action with scoped credentials and idempotency controls.

### VERIFY EFFECT

Do not assume API success implies desired state.

Collect an external receipt or independently re-read state when practical.

## Reversibility

Effects should be classified at least as:

- `REVERSIBLE`
- `PARTIALLY_REVERSIBLE`
- `IRREVERSIBLE`

## Rollback

Rollback is appropriate when the prior state can actually be restored.

Examples may include:

- reverting a reversible configuration,
- restoring a snapshot,
- reverting a branch or staged deployment.

## Compensation

Some effects cannot be undone even when a compensating action exists.

Examples:

- payment followed by refund,
- email followed by correction,
- public post followed by retraction.

A compensated Effect remains historically committed and must be represented as `COMPENSATED`, not falsified as `ROLLED_BACK`.

Saga-style compensation records should preserve the sequence of actions and compensations.

## Idempotency

Recovery must not duplicate external effects.

Whenever the target system allows it, commits should use stable idempotency keys tied to the logical Effect identity.

If native idempotency is unavailable, the Effect Controller should implement the strongest practical deduplication and pre-commit state check.

## Credentials

Effect commit credentials should be scoped and held by the Effect Controller or credential broker where practical, not broadly exposed to workers.

## Separation of Duties

The same component should not both:

1. generate an Effect,
2. validate the Effect,
3. authorize the Effect,
4. commit the Effect.

The system should preserve separation appropriate to risk level.
