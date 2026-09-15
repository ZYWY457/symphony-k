# Stage 1 Correction M7D6A — Evaluation Producer Authority Relabel Closure

**Version:** 1
**Status:** Completed; corrected cumulative M7 HUMAN ACCEPTED after Issue #71
**TaskSpec reference:** https://github.com/ZYWY457/symphony-k/issues/71
**TaskSpec access mode:** materialized-handoff
**TaskSpec precondition:** PASS
**Starting HEAD / required parent:** `a922914a31a5cd8ec7438f0546847d1c23dc96f2`

## Scope and plan

This is a forward correction within the accepted Issue #62/#70 architecture.
No new architecture or ADR is required. Production scope is `creation.py`;
tests are the M7D3 and integrated creation suites, plus this correction record.

1. Add isolated four-target producer-to-authority attacks and independent
   EVALUATOR/SCHEDULER success controls; reproduce the defect before fixing it.
2. Extend the common authority principal enumeration with every typed Evaluation
   validation-scope producing principal. Preserve exact authority binding,
   availability, semantics, guards, snapshot, event and result validation order.
3. Directly exercise the integrated known-principal relabel boundary and audit
   requester, producer, proposer and observer protection across all variants.
4. Run all six focused suites, full pytest, Ruff, format, mypy and diff checks.
   Inspect explicit staging and create exactly one local forward commit:
   `fix(domain): close evaluation creation authority relabel gap`.

Acceptance requires same-ActorId role relabel rejection as
`UnauthorizedTransition`, independent eligible authority success, unchanged
canonical malformed/absent semantic rejection, and all validation gates passing.
No M8, persistence, new states, new roles, accepted non-creation changes,
remote mutation, amend or squash is authorized.

## Preflight and governing inputs

Clean worktree; repository root `D:/CODE/ProjectFile/python/symphony-k`; exact
starting HEAD above. Git commands, Python 3.12.7 and uv 0.11.2 succeeded.
Read AGENTS, Constitution, architecture, core beliefs, M7 architecture and
M7D3/M7D6 plans. Issue #70 was read with `gh issue view` after approved read-only
network escalation; Issue #71 content was supplied by the human launch handoff.

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

Only independent cumulative Human Review can change acceptance status.

## Execution evidence

### Root cause and correction

The common authority helper enumerated spec-level provenance but omitted
Evaluation target producers stored in the typed semantic validation scope.
A distinct requester therefore left the producer ActorId outside relabel checks.
The correction adds all `EvaluationRequestScope.producing_principals` to that
helper, after exact authority scope binding and before identifier availability.
It only enumerates typed provenance; it does not run entity semantic validation
early. Absent semantics still fail via their canonical semantic path; malformed
scopes still fail structural construction. Both `create_entity` and
`CreationResult` use the corrected authority check.

The complete known-principal set is:

| Creation variant | Principals protected against same-ActorId role relabel |
| --- | --- |
| Objective DRAFT | `request.requested_by` |
| Task DRAFT | `request.requested_by` |
| Run PENDING | `request.requested_by` |
| Outcome PROPOSED | requester plus `entity_spec.producer` |
| Evaluation PENDING | requester plus every `semantic_input.validation.producing_principals` entry |
| Effect PLANNED | requester plus `entity_spec.origin.proposed_by` |
| Effect COMMITTED / QUARANTINED | requester plus `entity_spec.origin.observed_by` |

ActorId equality with a different ActorType raises `UnauthorizedTransition`.
Independent eligible EVALUATOR and SCHEDULER creation authority remains valid.

### Bounded closure audit

Audited the complete table above once against the common enumeration, request
structure, authority and result paths, and adjacent semantic independence checks.
No additional omission within the frozen Issue #62/#70 relabel contract was found.
The shared protocol directly tests distinct Outcome producer and Effect origin
principals; integrated tests retain requester attacks for all eight variants and
the complete authority matrix including SYSTEM denial. M7D3 retains producer to
assigned-verifier relabel rejection. Observed-Effect tests retain observer to
recording-controller rejection. No accepted non-creation module was modified;
43 states, 91 non-creation edges, eight creation variants and 99 total edges remain.

### Regression evidence

Before the production change, the new focused selection produced **16 failed,
8 passed**: all producer-authority attacks failed with `DID NOT RAISE
UnauthorizedTransition`, while independent authority controls passed.
The attacks cover Run, Outcome, Effect and Evidence, both eligible authority
labels, and both entries of a two-producer scope. Requester and producer ActorIds
are distinct, and each attack first proves its complete request succeeds with
independent authority.

The four new integrated cases directly attack each Evaluation target family
through `create_entity` and forged `CreationResult` reconstruction, checking the
relabel-specific exception. Each retains independent EVALUATOR/SCHEDULER controls.
Additional focused tests preserve authority scope/order and canonical absent or
malformed semantic rejection. Total new collected tests: 32.

### Validation

Default uv cache initialization was denied. All subsequent uv commands used
repository-ignored `.uv-cache`, confirmed by `git check-ignore`, for disposable
cache data only. Lock/dependency inputs and validation strength were unchanged.

```text
uv sync --dev --locked                                  PASS
tests/test_creation_protocol.py                         122 passed
tests/test_creation_objective_task.py                     74 passed
tests/test_creation_run_outcome_evaluation.py             103 passed
tests/test_creation_planned_effect.py                      21 passed
tests/test_creation_observed_effect.py                     55 passed
tests/test_creation_integrated.py                         174 passed
full pytest                                             3145 passed
ruff check .                                            PASS
ruff format --check .                                   PASS (187 files)
mypy src tests                                         PASS (103 source files)
git diff --check                                        PASS
```

Initial mypy found two errors in new negative-test argument construction; those
test expressions were corrected without changing production behavior. Final
M7D3 and full-suite reruns, Ruff, formatting and mypy all passed. Commit SHA,
parent, final staged checks and worktree status are reported in the execution
handoff after the single local commit. Remote mutation: none.

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
