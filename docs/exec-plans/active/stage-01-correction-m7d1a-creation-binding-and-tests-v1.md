# Stage 1 Correction M7D1A — Creation Binding and Regression Matrix

**Version:** 1
**Status:** Implemented candidate; independent acceptance pending
**TaskSpec:** [GitHub Issue #64](https://github.com/ZYWY457/symphony-k/issues/64)
**TaskSpec access mode:** `materialized-handoff`
**Starting baseline:** `5cd51f7d2e028eb9bd12172f4d3daaa0d47d3846`
(`feat(domain): add authoritative creation protocol`)

## Scope

This is a bounded forward correction to the Issue #63 M7D1 candidate. It does
not amend or revert that candidate, and it does not implement M7D2 or any
entity-specific creation semantics.

The correction tightens only the shared M7D1 creation protocol:

- `CreationResult` must exact-bind the returned immutable snapshot content to
  the exact `request.entity_spec`, not only the entity family, ID, state and
  version.
- New `Outcome PROPOSED` snapshots must not carry a fabricated
  `superseded_by_outcome_id`; replacement lineage remains a later transition
  concern.
- Creation authority relabel attacks are rejected when the same principal
  `ActorId` attempts to acquire lifecycle creation authority by changing only
  `ActorType`.
- Relabel protection covers the common requester, the Outcome producer, planned
  Effect proposer and observed Effect observer. It deliberately does not invent
  unsupported blanket separation rules for all embedded actors.
- `create_entity()` remains fail-closed after all shared checks because no
  entity-specific creation validators are installed in M7D1.

## Out Of Scope

- Objective, Task, Run, Outcome, Evaluation or Effect creation semantics.
- Repository lookup, persistence, transactions, atomic uniqueness or M8
  behavior.
- Completion-map updates.
- External Effect execution, dispatch, credential, authorization or remediation
  behavior.
- Remote repository mutation.
- Claims that M7D1 is independently accepted, that any creation edge is
  accepted, that 99/99 edges are accepted, that M7 is complete or that Stage 1
  is complete.

## Regression Coverage

The direct Issue #63 regression matrix is completed with isolated deterministic
tests for:

- denied and unresolved creation authority decisions;
- all identifier availability statuses and representative substitutions;
- all eight request-family to target mappings;
- `CreationResult` family, ID, state, spec and version substitutions;
- rejection of version `0` creation results;
- creation event invariants;
- requester, Outcome producer and Effect origin principal relabeling;
- default fail-closed behavior for all eight request families; and
- representative preservation of the existing non-creation transition boundary.

## Validation Gates

Run the repository gates from the governing M7 architecture contract:

```text
uv sync --locked
uv run pytest -p no:cacheprovider
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
git diff --check
```

Use explicit-file staging only. Do not use `git add .` or `git add -A`.

## Completion Boundary

Accepted lifecycle coverage remains:

```text
91 / 99
```

This correction is not evidence that M7D1, any creation edge, M7, the integrated
99-edge lifecycle matrix or Stage 1 has been independently accepted or completed.
