# Stage 1 M7C4A — Canonical Outcome Validation-Start Semantic Guard

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #37 only

## Boundary

M7C4A adds the canonical Outcome-only semantic gate for exactly
`PROPOSED -> VALIDATING` to the existing M7A/M7B1/M7B2 pure transition boundary.
It consumes immutable, typed, exact-snapshot-bound observations and decisions. It
does not load or persist records, create or transition Evaluations, evaluate policy,
run validators, or mutate another lifecycle entity.

## Bounded steps

1. Define the minimal typed Outcome semantic guard, exact Outcome-snapshot-bound
   policy provenance, candidate/artifact scope, and independent Evaluation request
   observation required to start validation.
2. Require the Evaluation observation to retain its own ID/version/state, target
   the exact current Outcome ID/version, and remain in the accepted request state.
3. Require the transition engine to invoke the canonical Outcome guard after M7B1
   and M7B2 but before generic guards; all other Outcome non-creation edges remain
   semantically deny-by-default.
4. Add deterministic tests for the positive edge, exact binding, scope and policy
   rejections, independent-validation constraints, no-verdict behavior, provenance
   preservation, authority/eligibility composition, generic-guard composition,
   unchanged topology, and non-mutation of related entities.
5. Run the complete Issue #37 validation gates, stage only Issue #37 files,
   inspect the staged diff, and create one local commit without remote mutation.

## Acceptance evidence

- `PROPOSED -> VALIDATING` requires exact Outcome ID/version/source/target/
  correlation bindings; an explicit current artifact scope; an applicable,
  non-worker validation-policy decision; and an independent `PENDING` Evaluation
  request for the exact Outcome ID/version.
- Outcome and Evaluation observations retain distinct versions and cannot be
  substituted for one another.
- `VALIDATING` does not consume or fabricate a verdict, acceptance, rejection, or
  any Run, Task, Objective, Evaluation, or Effect lifecycle mutation.
- The replacement Outcome changes only state and version; producer, originating
  Run, artifact/evidence references, validity horizon, and lineage are preserved.
- No repositories, persistence, policy runtime, validation runtime, confidence
  gate, artifact storage, lifecycle topology change, or M7C4B+ semantics are added.
