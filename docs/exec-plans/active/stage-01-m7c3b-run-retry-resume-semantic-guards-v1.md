# Stage 1 M7C3B — Canonical Run Retry and Same-Attempt Resume Semantic Guards

**Version:** 1
**Status:** Active
**Scope:** Implementation #7C3B1 only

## Objective and Context

Extend the existing M7C3A Run semantic boundary with canonical, evidence-backed
guards for exactly `RUNNING -> RETRYING` and `RETRYING -> RUNNING`. `RETRYING`
prepares a Resume of the same trustworthy Run attempt; it never conceals Rewind,
Reassign, or successor-Run creation.

The accepted architecture already defines a trusted Checkpoint as a recovery
boundary. This slice represents an already-recorded trusted recovery boundary by
an opaque immutable reference only. It does not create, restore, load, or
persist a Checkpoint.

## Architecture Constraints

- Preserve the accepted 99-edge lifecycle topology and all existing M7C3A
  behavior.
- Every consumed Run decision is exact-bound to `RunId`, observed Run
  `EntityVersion`, and `CorrelationId`.
- Task and primary-Objective observations retain their own IDs and versions.
- Resume preserves RunId, TaskId, predecessor_run_id, and execution_profile_ref.
- A WORKER may supply interruption/recovery evidence but cannot authoritatively
  select Resume.
- Generic guards supplement, and cannot replace, the canonical Run guard.

## In Scope

1. Add only the immutable typed decision/reference records missing from M7C3A:
   recoverable interruption, same-attempt continuity, scoped Resume, trusted
   recovery-boundary provenance, and remaining recovery limits.
2. Define and validate the two canonical semantic bundles. Retry preparation
   requires evidence of recoverable interruption, continued same-attempt trust,
   a non-worker scoped Resume decision, a trusted recovery boundary, and
   remaining recovery limits. Resume requires validated continuity, trusted
   boundary provenance, valid grants, Task `IN_PROGRESS`, primary Objective
   `ACTIVE`, and an approved execution boundary.
3. Cover successful edges and every required rejection: stale/misbound decisions,
   worker Resume selection, changed identity/profile/predecessor, invalid
   recovery inputs, invalid related-entity observations, generic-guard
   composition, immutability, topology preservation, and deny-by-default
   remaining recovery/reassignment/failure/abort edges.
4. Run locked synchronization, scoped tests, repository-wide pytest, Ruff lint,
   repository-wide Ruff format check, and strict mypy. Explicitly stage only
   this Issue's files and make exactly one local commit.

## Out of Scope

Checkpoint restoration or manifests, recovery algorithms/controllers, Rewind,
successor Run creation, Reassign, FAILED/ABORTED semantics, repositories,
persistence, runtime execution, policy evaluation, and ADR-0006 automatic
failover. No lifecycle topology, state, or top-level domain concept changes.

## Dependencies and Risks

This work depends on the M7C3A typed exact-snapshot decision model and accepted
ADR-0005 same-attempt Retry semantics. The central risk is treating a worker
claim or a generic guard as a Resume authorization; canonical validation keeps
those concerns distinct.

## Acceptance Criteria and Evidence

- Both exact lifecycle edges accept only their canonical typed semantics.
- A state replacement can preserve the same snapshot identity only when
  canonical continuity validates the Run's Task, predecessor, and profile
  references.
- The full validation command set is green, including `ruff format --check .`.
- The staged diff contains only this plan, Run semantics/public API changes, and
  deterministic tests; one local commit is created and no remote mutation occurs.
