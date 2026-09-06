# Learning and Reputation

## Principle

The system must not learn production policy directly from raw execution history.

Audit history and learning data are separate domains.

## Data Flow

```text
Raw Audit Log
    |
    v
Delayed Observation / Review
    |
    v
Verified Experience Pool
    |
    v
Candidate Policy / Reliability Update
    |
    v
Shadow Evaluation
    |
    v
Canary Rollout
    |
    v
Versioned Production Policy
```

## Admission to Verified Experience

Experience should not enter the trusted learning pool until applicable conditions are met, such as:

- sufficient observation delay,
- no unresolved dispute,
- sufficient sample size for aggregated claims,
- outcome confirmation,
- evidence integrity,
- domain relevance,
- post-effect stability where relevant.

## Asymmetric Trust

Risk trust is asymmetric:

- strong negative evidence may reduce trust quickly,
- trust recovery requires repeated verified positive performance.

This prevents unstable oscillation after one good or bad sample.

## Reputation Scope

Do not use a single global score when domain-specific reliability is available.

Reliability profiles may be tracked for:

- Agent,
- Model,
- Skill,
- Tool,
- ExecutionProfile,
- Validator,
- combinations such as Agent x Model x TaskType.

Example dimensions:

- Python backend,
- frontend,
- infrastructure,
- research,
- security validation,
- database migration.

## Validator Reputation

Evaluators and validators are themselves fallible and must be calibrated.

Signals include:

- historical disagreement with later verified outcomes,
- human override frequency,
- domain-specific accuracy,
- correlated failure patterns,
- false positive and false negative behavior.

Validator weights may change over time, but only through the governed learning path.

## Policy Evolution

Policy updates should be:

- versioned,
- reviewable,
- attributable,
- testable against historical data,
- deployable in shadow mode,
- deployable through canary rollout,
- reversible.

No learning component receives authority to silently mutate production policy.

## Audit Separation

Raw audit records are immutable evidence sources. Derived features, reputation scores, and policies may be recomputed or superseded without changing the source history.
