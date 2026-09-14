# Stage 1 M7D2 — Objective and Task Creation Semantics

**Version:** 1
**Status:** Active implementation candidate; independent Human Review required
**TaskSpec:** [GitHub Issue #68](https://github.com/ZYWY457/symphony-k/issues/68)
**TaskSpec access mode:** `materialized-handoff`
**Starting baseline:** `6eaf549792507e020a429d4abafd1750496de02a`
(`docs(governance): record m7d1 creation protocol acceptance`)

## Scope

Implement exactly Objective `NONE -> DRAFT` and Task `NONE -> DRAFT` through
the accepted M7D1 creation protocol. Both successful paths return an immutable
version-1 snapshot and exactly one matching canonical creation event. The other
six creation variants remain deterministically fail closed.

## Four-way Objective classification

1. **Constructor invariant:** `Objective` and `ObjectiveCreationSpec` validate
   only structural representation: typed fields, nonempty text/criteria, and
   typed authority, policy, and optional time values.
2. **Creation semantic invariant:** typed PASSED decisions must establish that
   the exact requested goal is bounded, the exact acceptance criteria and
   designated authority are bound together, and the exact completion policy is
   applicable.
3. **Typed supporting provenance:** each decision retains its own typed stable
   reference, independent deciding identity, nonempty immutable evidence
   references, and exact Objective/request causation/correlation scope.
4. **Future M8 authoritative fact:** repository-backed absence, related-record
   currentness, atomic version-1 insert, event append, uniqueness, and replay
   remain outside this pure-domain slice.

## Task semantics

Task creation requires PASSED exact-bound definition and completion-policy
decisions. One typed relationship observation must cover the primary Objective
and one must cover every contribution Objective. The observation set must
exactly equal the request relationships. Only `CURRENT` observations succeed;
`MISSING` raises `EntityNotFound`, while `STALE` and `UNRESOLVED` fail closed.
A current DRAFT primary Objective is valid: creation adds no readiness,
activation, state propagation, or relationship-derived authority.

## Implementation steps

1. Add closed creation-semantic decision, provenance, and relationship types.
2. Extend only Objective/Task creation inputs and compose their exact semantic
   validation into `create_entity` after shared authority/availability checks.
3. Run additional pure guards, construct canonical version-1 snapshots/events,
   and emit deterministic reference-only annotations.
4. Add the direct Objective/Task success and attack regression matrix while
   preserving all M7D1 tests and the six unopened creation variants.
5. Run every locked validation gate, stage only authorized files, inspect the
   staged diff, and create the one requested local forward commit.

## Out of scope

Run, Outcome, Evaluation, or Effect creation; Task readiness; Objective
activation; state propagation; repository loading; persistence; transactions;
durable uniqueness; M8; TaskProposal; execution; external Effects; and changes
to accepted non-creation semantics or the Stage 1 completion map.

## Acceptance boundary

This Run produces an M7D2 candidate for independent Human Review. Candidate
implemented edges are Objective plus Task, while Human Accepted creation edges
remain `0 / 8` and Human Accepted integrated coverage remains `91 / 99` until
that review accepts the candidate. It does not complete M7 or Stage 1.
