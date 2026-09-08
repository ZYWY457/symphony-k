# Stage 1 M6C — Effect Rollback and Compensation Provenance

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #19 only

## Boundary

Existing accepted Effect semantics distinguish rollback from compensation, so this
is not an architectural change and requires no ADR. This change adds only frozen,
evidence-backed supporting records and pure compatibility predicates. No record
executes a remedy, grants authorization, queries related records, or changes an
Effect lifecycle snapshot.

## Bounded steps

1. Add nominal rollback, compensation-plan, and compensation-completion IDs.
2. Add immutable rollback, compensation-plan, and compensation-completion
   provenance records, each retaining typed original commit-observation identity.
3. Add only the specified pure structural compatibility predicates; verify the
   accepted Effect topology remains unchanged.
4. Export the public API, add runtime and strict static typing coverage, run all
   Issue #19 validation gates, explicitly stage M6C files, inspect the complete
   staged diff, and create one local commit.

## Acceptance

Rollback independently records restoration. Compensation retains the original
mutation, links only distinct governed Effect IDs, and preserves residual impact.
No latest-wins precedence, repository lookup, lifecycle mutation, execution,
authorization, reconciliation, or M7 behavior exists.
