# Stage 1 Correction M7D1C — Creation Event Version Regression

**Version:** 1
**Status:** Implemented candidate; independent Human Review pending
**TaskSpec:** [GitHub Issue #66](https://github.com/ZYWY457/symphony-k/issues/66)
**TaskSpec access mode:** `materialized-handoff`
**Starting baseline:** `a491a9622260acbc1da28df33576923e578c4860`
(`fix(domain): preserve creation event provenance annotations`)

## Scope

This is a tests/docs-only forward correction for the final regression-proof gap
found by the independent Human Review of Issue #65. That review found no
source-level M7D1 semantic defect. The only blocking finding was that the
dedicated creation suite did not directly substitute the creation event's
`entity_version` while retaining a valid version-1 entity snapshot.

This correction does not redesign the shared creation protocol, implement
M7D2, change the completion map, or accept any creation edge. Production source,
including `src/symphony_k/domain/creation.py`, remains unchanged.

## Regression Proof Added

`test_result_rejects_event_entity_version_substitution` begins with an otherwise
valid `CreationResult`, proves that its entity snapshot and event both start at
`EntityVersion(1)`, and then changes only `event.entity_version`. The test covers
both noncanonical substitutions:

```text
EntityVersion(0)
EntityVersion(2)
```

Each substitution must be rejected by `CreationResult` while the entity
snapshot remains at version 1. This directly closes the event/entity version
mismatch proof required by Issues #63–#65.

The event exact-binding negative matrix was also inspected. Timestamp had no
isolated substitution test, so
`test_result_rejects_event_timestamp_substitution` now begins with the same
valid result, changes only `event.timestamp`, and proves rejection.

No invalid multi-field fixture is used for either regression.

## Preserved Contracts

All Issue #63, #64, and #65 invariants remain preserved, including:

- exactly eight closed, typed creation request variants;
- `NONE` as absence rather than a state, snapshot, or sentinel version;
- canonical `EntityVersion(1)` creation snapshots and events;
- full typed `entity_spec` to snapshot exact binding;
- rejection of fabricated Outcome supersession lineage;
- `Evaluation` PENDING creation with `result=None`;
- exact request-scope binding for creation authority and identifier
  availability;
- no implicit SYSTEM superuser and no requester, producer, proposer, or
  observer principal relabel path to lifecycle authority;
- structurally valid immutable event annotations and the existing
  `DomainEventMetadata` structural constraints;
- a separate `create_entity()` boundary that remains fail-closed until the
  entity-specific M7D2–M7D5 semantics exist;
- isolation from `transition_entity()` and all accepted non-creation behavior;
  and
- the M7/M8 responsibility split, with no repository or persistence behavior.

The production contract already rejects a creation event unless
`event.entity_version == EntityVersion(1)`. This correction adds direct evidence
for that existing behavior; it does not alter the implementation.

## Lifecycle and Review Status

Accepted lifecycle coverage remains:

```text
non-creation accepted = 91 / 91
creation accepted     = 0 / 8
integrated accepted   = 91 / 99
```

M7D1 remains pending independent Human Review. No creation edge is accepted by
this correction. M7 and Stage 1 remain incomplete. The completion map and prior
M7D1 plans remain unchanged and active.

## Validation and Commit Boundary

The candidate must pass the focused creation-protocol suite and every locked
repository gate from Issue #66. Only this plan and
`tests/test_creation_protocol.py` may be staged, using explicit-file staging.
The resulting work is one local forward commit named:

```text
test(domain): prove creation event version exact binding
```

No remote repository state is authorized to change.
