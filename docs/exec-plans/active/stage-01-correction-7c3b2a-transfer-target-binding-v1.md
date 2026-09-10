# Stage 1 / Correction #7C3B2A — Transfer Target Binding

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #34 only

## Objective

Bind each `RunTransferExclusivityDecision` to the exact successor Run snapshot
or accepted human-handoff reference selected by `RunReassignmentSemantics`.

## Bounded Work

1. Add immutable, typed target provenance to the existing exclusivity decision
   and reject absent, ambiguous, incomplete, or untyped targets at construction.
2. Require exact target-kind and target-value equality in the existing
   reassignment guard, preserving the old Run snapshot and correlation checks.
3. Add deterministic regression tests for target substitution, malformed target
   shapes, worker exclusion, and retained reassignment/lifecycle behavior.
4. Run the required repository validation gates and create one local corrective
   commit without remote mutation.

## Out of Scope

Reassignment redesign; repositories or freshness lookups; runtime fencing,
locks, successor creation, handoff delivery, persistence, and Effect behavior.

## Acceptance Evidence

A passed decision for one durable transfer target cannot authorize a different
successor ID/version, a different handoff, or the opposite target kind.
