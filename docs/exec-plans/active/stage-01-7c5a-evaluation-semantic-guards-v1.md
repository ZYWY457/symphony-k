# Stage 1 / 7C5A — Canonical Evaluation Semantic Guards

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #44 only

## Objective

Add canonical, typed semantic enforcement for six existing Evaluation lifecycle
edges: start, completion, and invalidation.  The transition engine remains pure
and continues to require independently evaluated M7B1 authority and M7B2 actor
eligibility before semantic validation.

## Context and constraints

- The accepted Evaluation topology remains exactly ten non-creation edges.
- Reuse `Evaluation`, `EvaluationTargetRef`, `EvaluationMethodRef`,
  `EvaluationResult`, `EvaluationInvalidationRecord`, and
  `can_invalidate_evaluation`.
- Evaluation content and historical provenance remain immutable; successful
  projection may only bind a verifier at start, append one result at completion,
  or change state/version on invalidation.
- No repository, policy runtime, authentication service, validator execution,
  conflict-set execution, arbitration execution, Outcome propagation, or M8
  loading/persistence is introduced.
- The four conflict/arbitration edges remain structurally legal and
  canonical-semantically deny-by-default.

## Milestones

1. Define minimal immutable, exact-snapshot-bound Evaluation semantic provenance
   for verifier independence, input readiness, completion/conflict clearance,
   and the existing invalidation record.
2. Add `EvaluationSemanticGuard` for only PENDING -> RUNNING, RUNNING ->
   COMPLETED, and the four accepted invalidation edges.
3. Integrate the guard into the centralized transition engine before generic
   guards, with narrow verifier/result projections.
4. Add deterministic regression coverage for successful paths, substitutions,
   authority/eligibility composition, preservation, topology, and deferred-edge
   denial.
5. Run the full Issue #44 validation gates, inspect the scoped staged diff, and
   create one local commit without remote mutation.

## Acceptance evidence

- Start exact-binds an EVALUATOR verifier, independent evidence and input
  readiness; a preassigned verifier cannot be replaced.
- Completion exact-binds a nonempty-evidence original result and an explicit
  conflict-clearance decision, while preserving target/method/verifier and
  keeping verdict content opaque.
- Invalidation exact-binds the durable invalidation record to the request and
  preserves any existing original result and conflict history.
- M7B1, M7B2, generic guard composition, immutable snapshots, and all
  non-Evaluation semantic regressions remain intact.
