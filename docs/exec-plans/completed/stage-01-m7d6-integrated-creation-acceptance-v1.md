# Stage 1 M7D6 — Integrated Authoritative Creation Candidate

**Version:** 1
**Status:** Completed; corrected cumulative M7 HUMAN ACCEPTED after Issue #71
**TaskSpec:** https://github.com/ZYWY457/symphony-k/issues/70
**TaskSpec access mode:** materialized-handoff
**TaskSpec precondition:** PASS
**Parent:** `2dc7f687c7e5fcb8ca37ba77a2e3791e47178213`

## Scope and validation plan

Prove all eight canonical creation paths together: Objective DRAFT, Task DRAFT,
Run PENDING, Outcome PROPOSED, Evaluation PENDING, and Effect PLANNED,
COMMITTED and QUARANTINED. Preserve 43 states and all 91 non-creation edges.

1. Exercise every variant with real semantic inputs through `create_entity`.
2. Prove exact actor matrices, SYSTEM denial, actor relabel rejection, shared
   authority/availability substitutions, semantic request replay, canonical
   version/event binding, no source state and no transition self-loop reuse.
3. Check deterministic reference-only output and all focused creation suites.
4. Run locked sync, full tests, Ruff, format, mypy, and diff checks at final HEAD.

No new lifecycle semantics, execution or persistence. Reuse of an old event
inside a changed result must fail exact binding. Global event-ID reservation,
idempotent replay and conflicting durable insert are M8 responsibilities;
pure repeatable M7 calls do not implement a hidden event registry.

## Truth boundary

```text
Human Accepted non-creation = 91 / 91
Human Accepted creation = 2 / 8
Human Accepted integrated = 93 / 99
candidate creation implementation = 8 / 8
candidate integrated implementation = 99 / 99
M7 Human Accepted = NO
Stage 1 complete = NO
```

M7D3/D4/D5/D6 remain active candidates. Human Review and subsequent governance
reconciliation are required; M8/M9 and Stage 1 Exit Review remain outstanding.

## Validation evidence

```text
uv sync --dev --locked                                  PASS
tests/test_creation_protocol.py                         122 passed
tests/test_creation_objective_task.py                    74 passed
tests/test_creation_run_outcome_evaluation.py             75 passed
tests/test_creation_planned_effect.py                    21 passed
tests/test_creation_observed_effect.py                   55 passed
tests/test_creation_integrated.py                       170 passed
full suite                                            3113 passed
ruff check .                                             PASS
ruff format --check .                                    PASS (186 files)
mypy src tests                                           PASS (103 source files)
git diff --check                                         PASS
```

All uv commands used repository-ignored `.uv-cache` following the default-cache
access denial recorded in M7D3. Dependency inputs and security gates were not
changed. Each new focused suite was invoked explicitly.

The integrated suite covers the exact eligible authority matrix, all eight
successful v1 projections, cross-family authority/availability/semantic replay,
same-principal relabeling, request causation replay before extra guards,
snapshot/content/event exact binding, version 0/2 denial, event-family/prior-state
fabrication, reference-only annotations and rejected transition self-loops.
The accepted topology remains `(17, 16, 18, 11, 10, 19)` non-creation edges.

No cross-phase production correction was necessary. The baseline comparison
contains no changes to accepted non-creation production modules or tests.
This last phase changes only this plan and the integrated test suite.

## Local stack through the parent

| Phase | Commit | Parent | Validation |
| --- | --- | --- | --- |
| 0 | `7c0704a98f05ec9a99ace763cf74e9efe30998dc` | `1b1f36d49e5f92678158c68965c4b35803f7544a` | docs-only diff; 196 focused tests; baseline full suite 2792 |
| 1 | `ecbf4e1d0e89b65557e681786abebddd6687c3f4` | `7c0704a98f05ec9a99ace763cf74e9efe30998dc` | 75 focused; 2867 full; all static gates |
| 2 | `a3551cee6b46b667e70820afb3fbb05a9290da1b` | `ecbf4e1d0e89b65557e681786abebddd6687c3f4` | 21 focused; 2888 full; all static gates |
| 3 | `2dc7f687c7e5fcb8ca37ba77a2e3791e47178213` | `a3551cee6b46b667e70820afb3fbb05a9290da1b` | 55 focused; 2943 full; all static gates |

Every completed parent commit had a clean worktree before the next phase.
All staging used explicit paths and the staged diffs were inspected. No remote
mutation, amend, squash or history rewrite was performed.

## Subsequent cumulative Human acceptance - Issue #72

Issue #70's accelerated stack received REQUEST CHANGES for the Evaluation
producer-to-creation-authority relabel defect. Issue #71 corrected that blocker.
Independent Human Review accepted the corrected cumulative result through
`8f73da617ac686254ea30fc33a6d8f81bdb406cb`: non-creation 91 / 91,
creation 8 / 8, integrated 99 / 99. M7 is HUMAN ACCEPTED.
The original candidate counts and validation above are historical evidence,
not the current acceptance boundary; Issue #70 alone was not accepted.
Archived under Issue #72 without changing the implementation contract.
M8 and M9 remain incomplete; Stage 1 is not complete.
