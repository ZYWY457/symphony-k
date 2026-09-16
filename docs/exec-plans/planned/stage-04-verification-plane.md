# Stage 04 — Verification Plane

**Status:** PLANNED — not implementation authorization
**Constitutional baseline:** `constitution-v0.1`

## Objective and why this stage exists

Make acceptance depend on independently collected evidence and governed
Evaluations rather than Worker self-report or a universal judge model.

## In scope

- `ValidationPlanner` and risk/value-aware validation profiles;
- evidence collection and provenance;
- precondition, static, intermediate and dynamic validators;
- semantic validator interface and confidence gate;
- persisted Evaluation production;
- conflict-set, arbitration, invalidation and effective-use integration;
- separation between producing Worker, evaluator and Effect committer.

## Out of scope

- Worker self-validation as authority;
- one LLM as universal truth source;
- Effect commit, recovery control and learning-driven policy;
- rewriting Evaluation content or bypassing Stage 1 currentness.

## Architecture boundaries

The verification plane consumes TaskSpec, candidate artifacts and independently
collected evidence. It produces immutable Evaluation history through domain
services. Outcome disposition remains a separate authoritative decision using
current effective-use semantics.

## Expected new interfaces and concepts

`ValidationPlanner`, `ValidationProfile`, `Validator`, `ValidationRun`,
`EvidencePackage`, `EvidenceCollector`, `SemanticValidator`, confidence result
and evaluation persistence service. ADR/design work must settle evidence
identity, validator independence and confidence aggregation.

## Cross-stage dependencies

Requires Stages 1–3 and ADR-0004/0005. Supplies trusted signals to recovery,
Effects, routing, planning and learning.

## Security and trust requirements

Evidence provenance and target/version binding are mandatory. Prefer
deterministic and independent evidence; model judgment is calibrated telemetry.
An evaluator cannot commit the Effect it validates, and a producer cannot
become independent by changing a label.

## Failure model

Classify unavailable validator, invalid evidence, stale target, tool failure,
semantic uncertainty, conflict and insufficient confidence. Missing or
conflicting evidence fails closed or escalates; it never becomes a positive
verdict by timeout.

## Milestones

1. Accept evidence, independence and validation-planning designs.
2. Implement evidence packages and deterministic validator contracts.
3. Add dynamic/intermediate and semantic validation adapters.
4. Persist Evaluations and integrate conflict/arbitration/currentness.
5. Implement confidence gating and independent acceptance scenarios.
6. Complete adversarial review and Human Exit Review.

## Proposed bounded Issue decomposition

- evidence/provenance ADR and schemas;
- validation planner/profile;
- static/precondition validators;
- dynamic/intermediate validators;
- semantic adapter and calibration boundary;
- Evaluation persistence/conflict integration;
- confidence/acceptance integration and stage reconciliation.

## Validation strategy

Deterministic fixtures, tampered/missing/stale evidence, validator isolation,
tool/environment diversity, conflicting verdicts, atomic conflict projection,
arbitration currentness, negative semantic cases and producer/evaluator/
committer identity attacks.

## Human Exit Review questions

- Can a Worker claim alone produce acceptance?
- Are evidence identity, provenance, target and version bound end to end?
- Are conflicting or stale Evaluations prevented from effective use?
- Is evaluator independence enforced by principal/component identity?
- Does validation intensity vary without weakening constitutional gates?

## Stage Definition of Done

Evidence-backed persisted Evaluations independently govern candidate Outcome
disposition, including conflicts and confidence gates. Worker self-report is
never sufficient. Human Exit Review and reconciliation precede Stage 5.
