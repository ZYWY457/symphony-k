# Verification Model

## Principle

Verification is a value-driven, evidence-based dynamic pipeline.

There is no single universal judge model. LLM judgment is one possible verifier among many.

## Validation Inputs

Validation planning may consider:

- value,
- risk,
- reversibility,
- confidence,
- verifiability,
- task type,
- historical reliability,
- available evidence,
- external effect sensitivity.

## Verification Levels

### L0 — Preconditions

Examples:

- inputs complete,
- environment available,
- dependencies present,
- permissions valid,
- budget sufficient,
- required rollback or compensation plan exists.

### L1 — Static Verification

Examples:

- schema checks,
- AST checks,
- type checks,
- lint,
- policy checks,
- diff inspection,
- dependency analysis,
- configuration checks.

### L2 — Intermediate Assertions

Validate important intermediate states, not only final outputs.

Examples:

- invariant checks during migration,
- progress counters,
- expected intermediate artifacts,
- state transition assertions,
- resource bounds.

### L3 — Dynamic Verification

Examples:

- unit tests,
- integration tests,
- API tests,
- sandbox replay,
- browser interaction,
- runtime assertions,
- independent external state reads.

Where practical, verification should reduce correlated failure by varying environment or tool path from the worker's execution path.

### L4 — Semantic and Logical Verification

Used for requirements and judgments that are not fully deterministic.

Inputs should include:

- Task specification,
- candidate Outcome,
- artifacts,
- independently collected evidence,
- relevant execution trace.

The evaluator should not rely only on the worker's narrative summary.

### L5 — Confidence Gate

Verification confidence may aggregate:

- evidence quality,
- coverage,
- validator agreement,
- validator independence,
- historical calibration,
- anomaly signals,
- missing evidence,
- task ambiguity.

Worker self-confidence is telemetry, not authority.

## Weighted Evidence

Weighted voting must not be naive majority voting.

Weights should consider:

- independence,
- domain relevance,
- historical calibration,
- correlated failure risk,
- evidence quality.

Deterministic evidence may carry more weight than multiple correlated LLM judgments.

## Conflict and Arbitration

Conflicting Evaluations produce a `CONFLICTED` state or equivalent arbitration requirement.

Resolution may include:

- additional deterministic tests,
- an independent validator,
- a domain specialist,
- a stronger semantic judge,
- human arbitration.

Overrides are appended, never silently rewritten.

## Evidence Package

A result presented for acceptance should eventually include a structured package containing:

- summary,
- artifacts,
- changes,
- evidence,
- tests,
- usage,
- cost,
- warnings,
- remaining risks,
- worker claims,
- evaluator verdicts,
- evaluator confidence,
- unresolved conflicts.
