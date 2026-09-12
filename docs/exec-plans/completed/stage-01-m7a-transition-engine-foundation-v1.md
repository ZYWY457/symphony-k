# Stage 1 M7A — Transition Engine Foundation and Authoritative Domain Events

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #21 only

## Boundary

M7A implements the accepted centralized lifecycle-mutation foundation and
authoritative event representation. It operates only on caller-supplied immutable
snapshots and returns an immutable replacement plus one event. M8 retains ownership
of repository loading, persistence, transactions, compare-and-swap, and atomic
database writes. No new ADR is required because this is the planned M7 boundary.

## Bounded steps

1. Add nominal Event and causation IDs plus closed lifecycle entity/event types.
2. Add immutable event metadata, DomainEvent, transition request/context/result,
   and a typed guard protocol for later authority and semantic checks.
3. Implement one centralized pure transition function that checks the exact
   caller-supplied version, delegates structural legality to the existing six
   canonical topology helpers, creates a new snapshot, advances its version once,
   and returns exactly one matching lifecycle event.
4. Add runtime and strict static tests for all six entity families, immutable input
   preservation, deterministic rejection, canonical-helper reuse, creation/NONE
   separation, and absence of M7B+, persistence, or external execution behavior.
5. Run all Issue #21 gates, explicitly stage only M7A files, inspect the complete
   staged diff, and create exactly one local commit.

## Acceptance

No lifecycle edge or state is added, removed, or copied into a second edge table.
M7A has no permissive default guard context: callers must provide at least one typed
guard implementation, while the complete actor/semantic rules remain deferred to
M7B–M7E. A failed version, structural, constructor-invariant, or supplied guard check
returns no transition result or authoritative event. Creation is representable with
an absent prior state and never introduces `NONE` into an entity enum.
