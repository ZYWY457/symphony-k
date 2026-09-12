# Stage 1 Correction 7C6A1 — Effect Producing-Principal Verifier Binding

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #50 only

## Context

This correction closes the Human Review finding from Issue #49 without
redesigning accepted M7C6A preparation semantics. The prior verifier check kept
the verifier distinct from the preparer and Effect controller, but did not bind
the verifier to the immutable producing principal in `PlannedEffectOrigin`.

## Bounded steps

1. At the canonical `PLANNED/SIMULATED -> PENDING_COMMIT` semantic boundary,
   reject an EVALUATOR whose `ActorId` equals
   `effect.origin.proposed_by.actor_id` for a `PlannedEffectOrigin`.
2. Preserve the existing EVALUATOR eligibility and preparer/verifier/controller
   principal-separation checks. Producer and preparer remain distinct provenance
   roles.
3. Add transition-boundary regressions for valid distinct producer P, preparer
   Q, verifier V, controller C; and for producer P as WORKER attempting to
   verify as EVALUATOR under the same ActorId in both planned and simulated
   flows. Retain topology and deny-by-default coverage.
4. Run the complete Issue #50 validation gates, inspect only the scoped staged
   files, and make one local corrective commit. No remote mutation is in scope.

## Out of scope

- Authentication, role issuance, persistence, M8, COMMITTED, QUARANTINED,
  rollback, compensation, runtime execution, Effect topology, and any redesign
  of M7C6A provenance records.

## Acceptance evidence

- A producing principal cannot become the independent pre-commit verifier of
  its planned Effect by changing ActorType.
- Valid P/Q/V/C principal separation continues to pass, existing preparer and
  controller separation still applies, and the exact nineteen non-creation
  Effect edges remain unchanged with sixteen unimplemented edges denied.
