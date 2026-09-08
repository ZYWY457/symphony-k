# Stage 1 M6D — Effect Prepare, Verify, and Execution Authorization Provenance

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #20 only

## Boundary

The accepted Prepare–Verify–Authorize–Commit design already distinguishes
preparation, independent verification, prospective execution authorization, and
historical authorization findings. M6D therefore requires no ADR. It adds only
frozen supporting records and pure exact-snapshot compatibility predicates; the
records are not a seventh core entity and grant no lifecycle mutation API.

## Bounded steps

1. Add nominal preparation, verification, and execution-authorization IDs.
2. Add immutable records for preparation, successful verification, and
   prospective authorization of one exact Effect snapshot.
3. Add pure compatibility predicates based only on explicit identities, exact
   versions, and correlation, including explicit verification membership.
4. Export the public API and add runtime and strict static typing coverage for
   immutability, nominal identity, exact-version behavior, orthogonality, and the
   absence of retroactive, latest-wins, transition, policy, or execution behavior.
5. Run all Issue #20 gates, explicitly stage only M6D files, inspect the complete
   staged diff, and create exactly one local commit.

## Acceptance

Preparation, verification, and prospective execution authorization remain
separate immutable provenance facts. Verification grants no authorization;
authorization explicitly identifies its preparation and verification records and
binds to one exact Effect version. Human authorizers are representable without an
authority matrix. No record proves occurrence or historical governance, rewrites
an earlier finding, changes Effect state, executes an action, or resolves usable
authorization by time, version order, UUID order, or insertion order.
