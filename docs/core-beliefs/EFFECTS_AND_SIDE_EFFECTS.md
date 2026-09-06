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

## Occurrence, Authorization and Incident Observation

`COMMITTED` is the factual occurrence of the external mutation, independently confirmed. It MUST NOT imply that permission existed or policy was followed. Missing, invalid or unknown authorization and other safety/policy findings are recorded separately with their evidence; later correction or resolution appends records without retroactively authorizing the original action.

The Effect Controller's scoped observation/incident-ingestion action records reality and MUST NOT dispatch an external mutation. It can register a previously unregistered confirmed occurrence as COMMITTED, or a supported suspicion with uncertain occurrence as QUARANTINED. It can also reconcile PLANNED, SIMULATED, PENDING_COMMIT or QUARANTINED records when observations arrive. Prior execution authorization is not a guard on recording a fact. Recording authority, independently anchored occurrence evidence, external identity, deduplication and audit provenance remain required; worker claims alone cannot establish occurrence.

Observation records include external target/operation identity, evidence references, observer and recording authority, observation time, occurrence time when known, incident correlation, and separately assessed authorization/policy findings. Unknown attribution or authorization is explicitly unknown, never invented. Previously unregistered observations may lack Task/Run association; retain the unlinked reason and append verified associations later. No unlinked incident can become executable merely through registration.

Confirmed occurrence is recorded as COMMITTED even if a governance investigation remains open; confirmed occurrence facts persist through any later quarantine. QUARANTINED means departure from the normal automatic execution path for controlled reconciliation: uncertain occurrence, incident handling, unsafe remediation, rollback/compensation uncertainty or another recorded reconciliation condition. Quarantine is not an occurrence verdict or authorization finding.

Preserve occurrence, incident and authorization truth separately in appended facts/metadata. A disproved suspicion may remain QUARANTINED with occurrence_status=DISPROVED and incident_status=CLOSED; factual occurrence is then known to be disproved, not unknown. Retention outside the automatic path does not require a new terminal state and cannot become an execution request without separate governed intent and full preparation checks. Metadata changes do not create lifecycle self-transitions.

Normal execution still follows Prepare–Verify–Authorize–Commit with scoped credentials, idempotency, separation from the evaluator, and explicit human authorization before irreversible action. These exceptional observation paths acknowledge violations rather than permit them; recording cannot call the execution path or supply missing pre-action authorization.

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
