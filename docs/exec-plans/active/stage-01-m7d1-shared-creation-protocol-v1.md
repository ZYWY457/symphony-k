# Stage 1 M7D1 — Shared Authoritative Creation Protocol

**Version:** 1
**Status:** Implemented candidate; independent acceptance pending
**TaskSpec:** [GitHub Issue #63](https://github.com/ZYWY457/symphony-k/issues/63)
**TaskSpec access mode:** `materialized-handoff`
**Starting baseline:** `f5f4091d16d07dd46d6a5a2566dcc7c6b5970e97`
(`docs(architecture): define authoritative creation boundary`)

## Scope

Implement only the shared M7D1 creation protocol defined by the accepted M7
architecture contract. This slice adds the closed eight-request type family,
immutable normalized request scope, creation authority decision, exact-bound
pre-M8 identifier availability observation, version-1 result contract, and a
separate overloaded `create_entity(request, context)` boundary.

The implementation has no source snapshot, source state, sentinel, `NONE`
enum, or expected version. It does not call `transition_entity` and does not
alter any accepted non-creation transition.

## Explicit fail-closed boundary

M7D1 has no entity-specific semantic validators. `create_entity` first checks
the concrete request variant, exact authority scope, eligible decision actor,
exact identifier-availability scope, and `AVAILABLE` status; it then rejects
with `InvariantViolation` because no M7D2–M7D5 canonical semantic validator is
installed. Therefore this slice closes zero creation edges and cannot create an
authoritative snapshot or success event from shared structural checks alone.

The identifier availability record is a trusted fixture-level M7 input. It is
not a repository lookup, persistence result, transaction, or durable uniqueness
guarantee; atomic insert and replay handling remain M8 responsibilities.

## Carry-forward and non-goals

Issue #62 omitted the Objective four-way classification in the Objective
creation semantics section. M7D2 must explicitly resolve and document that
four-way classification before implementing Objective creation semantics. This
slice neither infers nor implements Objective semantics.

Out of scope: all Objective/Task/Run/Outcome/Evaluation/Effect creation
semantics, repository/persistence/M8 behavior, completion-map changes, external
Effect execution, TaskProposal, remote mutation, and any claim of M7, 99/99,
or Stage 1 completion.

## Acceptance checks

- exactly eight immutable request variants are closed and type-bound;
- authority and availability each bind the full normalized scope by value;
- actor eligibility rejects worker relabeling and `SYSTEM` pseudo-superuser use;
- `CreationResult` accepts only a matching canonical version-1 snapshot and one
  `prior_state=None` event; and
- shared checks still fail closed without entity-specific semantics.
