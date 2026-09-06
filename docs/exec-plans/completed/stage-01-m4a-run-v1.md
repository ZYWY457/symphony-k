# Stage 1 M4A — Run Snapshot, Provenance and Lifecycle Contract

**Version:** 1
**Status:** Implementation and required validation completed, 2026-09-07
**Scope:** [Implementation #4A / GitHub Issue #6](https://github.com/ZYWY457/symphony-k/issues/6), under the accepted [Stage 1 Exec Plan](../active/stage-01-domain-kernel.md), [ADR-0005](../../adr/0005-core-state-machine-semantics.md), and [Run design](../../design-docs/state-machines.md#5-run).

## Boundary Review

No conflict with the accepted hierarchy was found. This implements the existing Run concept and its structural topology without altering identity, authority or recovery semantics. Initial working tree and index were clean. Commit scope will be explicitly checked against the files of this Issue, including any unrelated changes that arrive while work proceeds.

In scope: Run snapshot, eight Run states, one typed TaskId, an opaque execution-profile reference, optional predecessor provenance, eighteen structural state-to-state edges and PENDING-only creation.

Out of scope: Outcome/M4B+, AttemptId, Task/Objective state checks, actor authority, execution configuration/runtime, scheduling, Checkpoints, recovery algorithms/execution, handoffs, Transition Engine, version mutation, events and persistence.

## Bounded Steps

1. Add the immutable Run and ExecutionProfileRef with existing M2 primitives. Acceptance: typed fields validate, state/version are explicit, self-predecessor is rejected and no mutation API exists.
2. Test the independent oracle for all 64 state pairs, exactly 18 edges, four sinks and same-Run retry versus a new attempt. Test opaque references, passive Task/predecessor IDs and no completion propagation or Outcome creation.
3. Run every Issue validation, inspect the actual staged names and diff, assert the exact commit whitelist, and commit only those files. Record the final commit hash outside the commit itself.

## Field Model and Decisions

| Run field | Type / meaning |
| --- | --- |
| run_id | RunId; the identity of this concrete attempt, not an adapter/session ID |
| task_id | One required TaskId; not a Task object or proof of existence/state |
| state | RunState, explicitly supplied |
| version | EntityVersion, explicitly supplied; no initial version convention |
| execution_profile_ref | ExecutionProfileRef(profile_id: str, profile_version: str) |
| predecessor_run_id | RunId or None; default None; cannot equal run_id |

Run and ExecutionProfileRef are frozen, slotted dataclasses. The profile reference lives in execution_profile.py and preserves two non-whitespace strings with no ID/version grammar, resolution, registry, approval flag or runtime behavior. Malformed values reuse InvalidDomainValue. No new top-level entity or runtime dependency is introduced.

Run stores identities only; it does not verify Task/predecessor existence or state, traverse predecessors, choose a recovery strategy or maintain child/successor collections. It does not infer a profile from a predecessor. RETRYING -> RUNNING is part of one Run's structural graph; a distinct attempt has a new RunId and may reference the old ID. Constructing or copying snapshots does not record authoritative history or enforce identity uniqueness across storage.

The private frozenset of eighteen typed state pairs is exposed only through can_run_transition. Non-RunState inputs raise InvalidDomainValue. RUN_CREATION_STATE is PENDING; NONE is absence, not an enum member. REASSIGNED, COMPLETED, FAILED and ABORTED are strict sinks. No new version, actor grant or event is produced by construction or queries.

Run COMPLETED means normal execution closure, not result correctness or acceptance. WAITING_FOR_VERIFICATION is a Run-level wait, not an Outcome judgment. No Outcome, acceptance field or cross-entity state propagation is added. The absence of mutation methods preserves the structural boundary but **does not fully enforce Worker authority**; authoritative Scheduler/Run Controller checks belong to M7.

## Required Validation

```text
uv sync --dev --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
git diff --check
```

## Exact Commit Scope

- README.md
- docs/exec-plans/completed/stage-01-m4a-run-v1.md
- src/symphony_k/domain/__init__.py
- src/symphony_k/domain/execution_profile.py
- src/symphony_k/domain/run.py
- tests/test_execution_profile.py
- tests/test_run.py
- tests/test_run_lifecycle.py
- tests/typing_examples.py

## Validation Evidence

Python 3.12.7 with the existing locked pytest 9.1.1, Ruff 0.16.6 and mypy 1.20.2. No dependency, lock-file or quality-configuration changes.

| Required command | Final result |
| --- | --- |
| `uv sync --dev --locked` | Exit 0; resolved/checked 13 packages |
| `uv run pytest` | Exit 0; 618 passed, no warnings |
| `uv run ruff check .` | Exit 0; all checks passed |
| `uv run ruff format --check .` | Exit 0; 57 files already formatted |
| `uv run mypy src tests` | Exit 0; no issues in 29 source files |
| `git diff --check` | Exit 0; only existing Windows LF-to-CRLF notices |

Tests independently check all 64 state pairs against exactly eighteen accepted edges and the four strict sinks. They verify eight exact enum names/values with no aliases or invented states, PENDING-only creation, explicit versions, immutable Run/profile fields, typed Task/predecessor references, self-predecessor rejection, same-identity retry snapshots and distinct-identity replacement attempts. They also verify normal Run closure does not change a Task, create an Outcome, or expose result-acceptance/recovery/mutation methods. Static examples reject wrong ID kinds, raw IDs, a Task object in task_id, and non-RunState query inputs. Existing Objective/Task tests pass unchanged.

Import sorting and formatting were applied only to the seven new/modified Python files. Accepted specifications and prior domain implementations remain unchanged. No unresolved architecture conflict, new runtime dependency, initial-version convention or scope deviation was introduced. Structural tests are not proof of Worker authority enforcement or recovery execution; those remain deferred.

## Commit Gate

Stage only the nine explicit paths above. Inspect `git diff --cached --name-status` and the staged diff; require `git diff --cached --check` to pass and the staged names to exactly match this whitelist. Verify staged blobs match the validated working files before committing. After commit, compare `git diff-tree --no-commit-id --name-only -r HEAD` with the same whitelist and report the exact hash. Unrelated working-tree or staged changes must not enter this commit.

This bounded implementation does not complete Stage 1 or claim authoritative lifecycle enforcement.
