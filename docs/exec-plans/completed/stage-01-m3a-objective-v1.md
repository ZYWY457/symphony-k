# Stage 1 M3A — Objective Model and Lifecycle Contract

**Version:** 1
**Status:** Implementation and required validation completed, 2026-09-06
**Scope:** [Implementation #3A / GitHub Issue #4](https://github.com/ZYWY457/symphony-k/issues/4), under the accepted [Stage 1 Exec Plan](../active/stage-01-domain-kernel.md), [ADR-0005](../../adr/0005-core-state-machine-semantics.md), and [Objective design](../../design-docs/state-machines.md#3-objective).

## Boundary Review

No conflict with accepted higher-level documents was found. This implements the existing Objective concept and structural contract, not a new architectural decision. Existing M2 primitives are reused. No runtime dependency or accepted design change is needed.

In scope: an immutable Objective snapshot, the eight Objective states, a validated opaque completion-policy reference, typed acceptance-authority designation, optional validity boundary, and the closed structural graph.

Out of scope: Task/M3B and M4+ entities, the centralized Transition Engine, authority/guard evaluation, version mutation, events, persistence, automatic expiry, scheduling and runtime infrastructure.

## Bounded Steps

1. Add the Objective representation and pure lifecycle queries. Acceptance: required fields validate structurally, stored data is immutable, and no lifecycle-mutating method exists.
2. Verify all 64 state pairs against the 17 accepted edges, DRAFT-only creation, sink/post-closure exits, malformed inputs and reference-only governance semantics. Acceptance: deterministic tests require no network, clock or fake child entity.
3. Run all Issue commands, record evidence, and verify unchanged dependencies and accepted specifications. Completing this plan does not accept or complete the whole Stage 1.

## Field Model and Decisions

| Objective field | Type / meaning |
| --- | --- |
| objective_id | ObjectiveId |
| state | ObjectiveState, required explicitly |
| version | EntityVersion, required explicitly; no initial-value convention |
| goal | Non-whitespace str, preserved exactly; semantic boundedness is deferred |
| acceptance_criteria | Nonempty tuple[str, ...] containing non-whitespace strings; no mutable collections accepted |
| acceptance_authority | ActorIdentity; records the designation, not a grant or role eligibility decision |
| completion_policy_ref | CompletionPolicyRef; validated opaque policy_id and policy_version strings |
| valid_until | Timestamp or None; UTC boundary, no clock check or automatic expiry |

Objective and CompletionPolicyRef use frozen, slotted dataclasses. CompletionPolicyRef is the only additional supporting value object: two required non-whitespace strings preserve policy identity/version without inventing a policy language, registry or version format. It conveys no pass/fail result. Existing InvalidDomainValue handles malformed construction. No separate goal-definition type is needed because the snapshot validates its immutable text fields directly.

The private immutable frozenset of 17 typed state pairs is exposed through `can_objective_transition(source, target)`, which answers only structural membership. Invalid non-enum inputs raise InvalidDomainValue. `OBJECTIVE_CREATION_STATE` is the explicit DRAFT-only creation contract; NONE is absence, not an enum member. The constant and pure query are deliberately public contract symbols; the table remains private.

Snapshots may represent any documented state at any supplied valid EntityVersion. Constructing or copying a snapshot cannot establish authoritative history, authorization or completion. No `create`, `activate`, `complete`, `transition` or state-replacement method is added. The later Transition Engine must validate creation/transition authority and guards, assign/increment versions, and record events atomically. A future expiry guard reads the retained horizon; M3A does not require a horizon merely to represent a historical EXPIRED snapshot or inspect an expiry edge.

## Required Validation

```text
uv sync --dev --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
```

## Validation Evidence

Python 3.12.7 with the existing locked pytest 9.1.1, Ruff 0.16.6 and mypy 1.20.2. No configuration was weakened.

| Required command | Final result |
| --- | --- |
| `uv sync --dev --locked` | Exit 0; resolved/checked 13 packages |
| `uv run pytest` | Exit 0; 307 passed, no warnings |
| `uv run ruff check .` | Exit 0; all checks passed |
| `uv run ruff format --check .` | Exit 0; 45 files already formatted |
| `uv run mypy src tests` | Exit 0; no issues in 19 source files |

The new tests enumerate all 64 state pairs and verify precisely 17 accepted edges, eight distinct states with no NONE/aliases, DRAFT-only creation, all self-loops forbidden, ARCHIVED as a strict sink and only archival exits from the four closed states. Snapshot tests cover explicit versions (0, 1 and 41 without selecting a default), field/nested immutability, typed references, opaque policy identity/version, immutable criteria, optional UTC horizon, and absence of authority/expiry/version/event execution. Static examples reject TaskId in the ObjectiveId position and raw-string state query arguments.

Initial checks identified an iterator parameterization deprecation and mypy diagnostics for deliberately malformed constructor inputs in tests. The iterator was materialized and negative inputs received narrow arg-type ignores; all affected checks then passed without configuration changes. Import sorting and formatting were applied only to the five new/modified Python files. `git diff --check` passed; Git emitted only the existing Windows LF-to-CRLF notices.

Final scope inspection confirmed no changes to dependencies, lock file, accepted ADRs, state-machine design, core beliefs, Constitution or Stage 1 Exec Plan. No new Task, central Transition Engine, guards/authority execution, version mutation, events, persistence, M3B or M4+ behavior exists. No unresolved conflict or new initial-version convention was introduced. Passing these structural checks is not evidence of authoritative transition enforcement, nor completion of Stage 1.
