# Stage 1 M6B2C — Effect Incident History

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #18 only

## Boundary

This is not an architectural change: existing Effect history and append-only
truth rules already permit immutable supporting incident findings. No seventh
core entity, Effect lifecycle state, repository, persistence, resolver,
automation, or ADR-0006 runtime behavior is in scope.

## Bounded steps

1. Add nominal Incident and Incident-record IDs plus a frozen, evidence-backed
   `EffectIncidentRecord` and the exact OPEN/CLOSED status inventory.
2. Add only pure Effect attachment and record-lineage compatibility predicates.
3. Export the public API; add runtime and strict static typing tests for
   identity separation, immutability, first-record CLOSED, all allowed lineage
   combinations, Effect-state orthogonality, and absence of resolution/authority.
4. Run all Issue #18 validation gates, explicitly stage only M6B2C files,
   inspect the staged diff, and create one local commit.

## Acceptance

Incident status remains independent from occurrence, authorization, governance,
rollback, compensation, and Effect lifecycle. History is append-only by explicit
prior-record identity; no latest-wins or effective-status logic exists.
