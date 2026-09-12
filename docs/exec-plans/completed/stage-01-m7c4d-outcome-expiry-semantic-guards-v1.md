# Stage 1 M7C4D — Canonical Outcome Expiry Semantic Guards

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #43 only

## Boundary

Add canonical, immutable, evidence-backed semantics for the four existing Outcome
expiry edges: `PROPOSED`, `VALIDATING`, `ACCEPTED`, and `REJECTED` to `EXPIRED`.
The implementation binds an expiry decision to the exact Outcome snapshot and
TransitionRequest correlation, accepts only Outcome lifecycle authorities as
decision-makers, and uses the request timestamp only for validity-horizon expiry.

This change does not add topology, persistence, policy evaluation, clocks,
schedulers, stale detection, cross-entity propagation, or runtime freshness.

## Bounded steps

1. Define a closed stale-basis vocabulary and immutable, evidence-backed expiry
   decision and semantic bundle types.
2. Extend the canonical Outcome guard for the four existing expiry edges and pass
   the request timestamp into it only for the horizon comparison.
3. Preserve all prior validation-start, disposition, and supersession semantics;
   retain state/version-only expiry projection.
4. Add deterministic coverage for exact binding, authority, evidence, stale bases,
   horizon boundary behavior, historical preservation, topology, and M7B gates.
5. Run every Issue #43 validation gate, explicitly stage only Issue #43 files,
   inspect the staged diff, and create exactly one local commit without remote
   mutation.

## Acceptance evidence

- Validity-horizon expiry requires `Outcome.valid_until` and a request timestamp
  at or after it; no domain clock is read.
- Assumption, dependency, and external-condition staleness need no validity
  horizon but require an exact-bound, PASSED, evidence-backed decision by an
  Outcome lifecycle authority.
- Successful expiry changes only state and EntityVersion; prior artifacts,
  evidence, provenance, acceptance/rejection meaning, and lineage remain intact.
- All eleven structural Outcome edges and the previously accepted seven canonical
  semantic edges remain unchanged.
