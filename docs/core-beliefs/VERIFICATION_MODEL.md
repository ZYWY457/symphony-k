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

Materially conflicting Evaluations MUST be linked by a persisted conflict-set identity and correlation, with member IDs/versions, affected target/acceptance scope, disagreement and evidence references. Every participant whose effective use is affected by the unresolved conflict MUST be projected as `CONFLICTED`, not only the Evaluation that discovered the disagreement. Original content and evidence remain intact.

Record membership, affected projections and per-member lifecycle events consistently with version checks; acceptance must not read a partly updated conflict set. Already-CONFLICTED members receive appended membership records without self-transitions. A PENDING Evaluation with no result is not a conflicting verdict; INVALID/ARBITRATED historical content may be referenced as evidence but is not reinstated as an effective verdict.

Resolution may include:

- additional deterministic tests,
- an independent validator,
- a domain specialist,
- a stronger semantic judge,
- human arbitration.

Overrides are appended, never silently rewritten.

Arbitration references the conflict-set version, all affected members and the disposition/effective judgment for each. A member remains CONFLICTED while any applicable conflict set is unresolved; resolving one member or set cannot silently unblock another. Fully addressed members may become ARBITRATED by appended arbitration, or INVALID on proven defect, preserving original records. ARBITRATED does not imply a changed verdict: separately record arbitration_disposition (for example UPHELD, MODIFIED or REVERSED) and the effective judgment for each member. These are metadata values, not lifecycle states. Further challenges to an effective arbitration decision use new linked records, not edits to the old judgment.

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
