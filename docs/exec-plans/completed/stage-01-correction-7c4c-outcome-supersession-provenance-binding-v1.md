# Stage 1 / Correction #7C4C1 — Outcome Supersession Provenance Binding and Canonical Coverage

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #42 only

## Historical context

This correction closes Human Code Review findings from Issue #41 (M7C4C). Issue
#41's original implementation did not create a versioned Exec Plan. This plan
records only the present correction; it does not alter or backdate that history.

## Boundary

Preserve the accepted M7C4C supersession architecture and its four canonical
Outcome `-> SUPERSEDED` edges. Strengthen only the immutable semantic bundle so
that both originating Run observations and the intended acceptance scope are
exact-bound, and reject a replacement that already has a successor link.

No new core entity, persistence, freshness lookup, policy runtime, graph store,
new Outcome edge, or lifecycle propagation is introduced.

## Bounded steps

1. Extend the existing compatibility decision with the exact source and
   replacement originating Run IDs and observed Run EntityVersions, and add an
   explicit intended acceptance-scope observation to supersession semantics.
2. Require the canonical guard to exact-bind those values, require exact scope
   agreement with the POLICY_ENGINE decision, and require a replacement with no
   existing successor link.
3. Add deterministic substitution and currentness regression coverage while
   retaining existing M7B1/M7B2, lineage, projection, topology, and expiry
   denial coverage.
4. Run the Issue #42 validation gates, inspect the explicitly staged diff, and
   create one local corrective commit without a remote mutation.

## Acceptance evidence

- A substituted originating Run ID or observed Run EntityVersion is rejected
  for either side without requiring equal Run versions.
- A substituted intended acceptance-scope identity or version is rejected.
- A replacement carrying `superseded_by_outcome_id` is rejected.
- Successful projection remains limited to source state, version, and direct
  replacement link; the replacement remains immutable.
