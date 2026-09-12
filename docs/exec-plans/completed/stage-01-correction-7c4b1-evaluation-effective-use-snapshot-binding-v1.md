# Stage 1 Correction 7C4B1 — Evaluation Effective-Use Snapshot Binding

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #40 only

## Boundary

Correct the M7C4B effective-use provenance binding without changing Outcome
lifecycle topology, Evaluation derivation, persistence, policy execution, or
cross-entity mutation.

## Bounded steps

1. Add a minimum immutable Outcome-side effective-use snapshot provenance value
   that binds Evaluation identity, version, lifecycle state, target, and view.
2. Require the Outcome observation to agree exactly with that provenance and
   require COMPLETED/ARBITRATED structural compatibility with the existing
   effective-use view semantics.
3. Add deterministic regressions for cross-state relabeling, version
   substitution, and retained M7C4B behavior.
4. Run the Issue #40 validation gates, stage only Issue #40 files, inspect the
   staged diff, and create one local corrective commit without remote mutation.

## Acceptance evidence

- A disposition consumes one exact Evaluation effective-use snapshot.
- COMPLETED and ARBITRATED views cannot be relabeled across lifecycle states.
- The original PENDING request version remains distinct from the later observed
  Evaluation snapshot version, and Outcome topology remains unchanged.
