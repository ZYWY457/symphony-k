# Stage 1 Correction 7C4A1 — Evaluation Request Snapshot Binding

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #38 only

## Boundary

Correct the M7C4A request-provenance binding defect without changing its
Outcome lifecycle topology or adding runtime, persistence, repository, or
Evaluation lifecycle behavior.

## Bounded steps

1. Strengthen the existing immutable Evaluation request provenance reference to
   carry the exact `EvaluationId` and observed Evaluation `EntityVersion`.
2. Require the Outcome Evaluation-request observation to agree with that durable
   provenance snapshot before the canonical `PROPOSED -> VALIDATING` guard can
   pass.
3. Add regression coverage for Evaluation ID and Evaluation-version substitution,
   while preserving Outcome/Evaluation version-domain independence and all
   existing M7C4A guard behavior.
4. Run the Issue #38 validation gates, stage only Issue #38 files, inspect the
   staged diff, and create one local corrective commit without remote mutation.

## Acceptance evidence

- An Evaluation request reference binds one exact `EvaluationId` and observed
  Evaluation `EntityVersion`.
- Reusing that reference with another Evaluation ID or observed Evaluation
  version is rejected by the canonical guard.
- Outcome and Evaluation version domains remain distinct, and the existing
  validation-start semantics and Outcome topology remain unchanged.
