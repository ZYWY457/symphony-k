# Stage 1 M3B — Task Model, Objective Links and Lifecycle Contract

**Version:** 1
**Status:** Implementation and required validation completed, 2026-09-06
**Scope:** [Implementation #3B / GitHub Issue #5](https://github.com/ZYWY457/symphony-k/issues/5), under the accepted [Stage 1 Exec Plan](../active/stage-01-domain-kernel.md), [ADR-0005](../../adr/0005-core-state-machine-semantics.md), and [Task design](../../design-docs/state-machines.md#4-task).

## Boundary Review

No conflict with the accepted hierarchy was found. The changes implement the existing Task concept and structural Objective relationships only. Sharing CompletionPolicyRef is the internal module cleanup explicitly required by the Issue; it changes neither policy semantics nor Objective lifecycle behavior. No new ADR or runtime dependency is required.

In scope: immutable Task snapshots, seven Task states, one typed primary Objective ID, immutable secondary Objective IDs, the shared policy reference and the closed structural Task graph.

Out of scope: Objective existence/state checks, relationship propagation, dependency graphs, execution ownership, authorization, guards, Transition Engine, version changes, events, persistence, scheduling and M4+ entities/runtime behavior.

## Bounded Steps

1. Move CompletionPolicyRef to completion.py and retain public imports and all existing validation/immutability behavior. Acceptance: original Objective tests pass and both entities use the same reference class.
2. Add Task and its structural graph. Acceptance: malformed typed fields/links are rejected; snapshots are immutable; state/version are explicit; seven states and sixteen state-to-state edges match the accepted design.
3. Test all 49 state pairs, three strict sinks, all self-loops, DRAFT-only creation, passive relationships and reference-only policy semantics. Run every required validation and inspect scope/dependency changes.

## Field Model and Decisions

| Task field | Type / meaning |
| --- | --- |
| task_id | TaskId |
| state | TaskState; required explicitly |
| version | EntityVersion; required explicitly, with no initial version convention |
| definition | Non-whitespace str, preserved exactly; no boundedness/executability heuristics |
| primary_objective_id | One required ObjectiveId; no absent/raw/multiple values or Objective objects |
| completion_policy_ref | Shared CompletionPolicyRef; no evaluation or implicit completion |
| contributes_to | frozenset[ObjectiveId], default empty; immutable unordered non-authoritative links |

Task is a frozen, slotted dataclass. Contribution input must already be a frozenset; mutable sets/lists and other collections are rejected, not silently coerced. Equal Objective IDs have set semantics, so duplicates cannot be stored. Every member must be an ObjectiveId and the primary ID must not be among them. A relationship is only a typed identifier: it does not establish existence, parent state, ownership authorization or any cross-entity transition. No reference to Objective objects or dependency graph is stored.

CompletionPolicyRef moves unchanged in meaning to `domain/completion.py`: policy_id and policy_version remain opaque non-whitespace strings, preserved as supplied, and invalid construction raises InvalidDomainValue with the same field messages. `symphony_k.domain.CompletionPolicyRef` now exports the shared class directly; objective.py also retains an explicit import alias for existing direct-module consumers. No policy engine or generic validation framework is introduced.

The private frozenset of sixteen typed state pairs is queried only through `can_task_transition(source, target)`. Invalid non-TaskState arguments raise InvalidDomainValue. `TASK_CREATION_STATE` is DRAFT; NONE is absence, not an enum member. Snapshot construction/copying is not an authoritative creation or migration, and no mutation/replacement methods are provided. The later centralized Transition Engine remains responsible for authority, guards, versions and events.

## Required Validation

```text
uv sync --dev --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
```

## Validation Evidence

Python 3.12.7, existing locked pytest 9.1.1, Ruff 0.16.6 and mypy 1.20.2; no tool configuration or dependency changes.

| Required command | Final result |
| --- | --- |
| `uv sync --dev --locked` | Exit 0; resolved/checked 13 packages |
| `uv run pytest` | Exit 0; 457 passed, no warnings |
| `uv run ruff check .` | Exit 0; all checks passed |
| `uv run ruff format --check .` | Exit 0; 51 files already formatted |
| `uv run mypy src tests` | Exit 0; no issues in 24 source files |

Tests independently enumerate all 49 state pairs and the exact sixteen accepted edges. They verify seven states with no aliases/additional states, DRAFT-only creation, all self-loops forbidden and COMPLETED/FAILED/CANCELLED as the only strict sinks. Model tests cover explicit versions, immutable fields, one required primary ObjectiveId, unique immutable secondary links, primary/secondary exclusion, rejection of raw IDs and Objective objects, and no lifecycle propagation or guard evaluation. Static examples reject TaskId as an Objective relationship and ObjectiveState/raw strings in Task queries.

All M3A tests remain unchanged and pass. Shared-reference tests confirm the public, shared-module and former Objective-module imports resolve to the same class, with unchanged fields, validation exception/messages, text preservation, equality/hashability and immutability. Objective's snapshot validation and topology were not modified.

Import sorting and formatting were applied only to the eight new/modified Python files. `git diff --check` passed; Git emits the existing Windows LF-to-CRLF notices. An unrelated working-tree edit to `git命令.txt` was observed during final inspection and left untouched by this task.

Dependencies, lock file, Constitution, accepted ADRs, core beliefs, state-machine design and Stage 1 Exec Plan are unchanged. There are no unresolved architecture conflicts or scope deviations. No Run, dependency graph, centralized Transition Engine, authority/guard execution, version mutation, events, persistence, scheduling or M4+ behavior was introduced. Structural contract tests do not establish authoritative relationship validation or lifecycle enforcement, or completion of the whole Stage 1.
