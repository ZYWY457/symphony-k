# Stage 02 M1B — Final Sandbox Contract Correction

**Status:** CORRECTION CANDIDATE - independent review / Human approval pending

**TaskSpec:** GitHub Issue #81

**TaskSpec reference:** <https://github.com/ZYWY457/symphony-k/issues/81>

**TaskSpec revision:** `r1 - stage-02-m1b-final-contract-correction`

**TaskSpec access mode:** `direct-read`

**Observed Issue updatedAt:** `2026-09-16T12:20:53Z`

**TaskSpec precondition:** PASS

**Parent:** `docs/exec-plans/active/stage-02-sandbox-execution.md`

**Starting HEAD:** `0e93897b519b28485fe04013e4de10e673ac7dbf`

**Starting parent:** `14773447aca6b89cd323aef63982fe585493a5dc`

**Starting title:** `docs(governance): harden cold-start task discovery`

**Corrects:** the R1-R4 findings in
`docs/reviews/stage-02-m1a-613d71b-review.md` against candidate
`613d71b90c36b573578f6fffb9a6c7dd9606478f`

**Current technical candidate:** PENDING COMMIT 1; Commit 2 records the exact
technical-correction SHA.

## Objective and authority

Perform the final bounded M1 technical-contract correction without reopening
provider selection or changing observable v1 scope. This plan authorizes only
the proposed ADR/design corrections and their governance reconciliation under
Issue #81. It does not accept ADR-0008, approve the design, release or execute
Issue #79, implement runtime code/tests, or run Docker, WSL, VM, systemd,
cgroup or adverse isolation experiments.

The starting repository was clean and matched the required repository, HEAD,
parent, title and origin. Git, Python 3.12.7 and uv 0.11.2 were callable.

## Bounded correction

### R1 — execution set, quiescence and final absence

Define three non-aliasing observations: Worker execution-set emptiness while
trusted PID 1 may remain alive, live-workspace collection quiescence, and whole
sandbox/resource absence. Reuse requires the first; collection requires the
first or a verified freeze; final `DESTROYED` requires the third. False or
unknown Worker-set emptiness blocks reuse and forces targeted destruction.

### R2 — independent deadline enforcement

Keep the guardian as coordinator, but arm a protected service-manager timer and
minimal exact-bound kill helper before Worker start. The fail-safe remains
executable if the guardian exits or is unresponsive. Exact identity/fingerprint
checks prevent stale actions from targeting a replacement generation;
service-manager, daemon and host failures retain honest unknown/reconciliation
semantics.

### R3 — first workspace lease bootstrap

`create_workspace` produces `READY_UNLEASED`. `create_sandbox` atomically
acquires the first lease, binds the requested sandbox and records the receipt/
cleanup fence before provider create. Confirmed no-resource failure may release
the lease through a versioned trusted-store transition; uncertainty retains the
binding and blocks competing acquisition.

### R4 — no-process start failure

Add explicit `process_started: bool | None` semantics. Confirmed no-process
`START_FAILED` contains no process timestamps, duration, exit code or stream
references and uses exact zero/no-truncation stream counts with
`termination_confirmed=false`. Unknown start occurrence remains `UNKNOWN` and
retains cleanup/reconciliation.

## Cross-contract completion

The corrected design includes explicit typed/store walkthroughs for:

1. empty store through workspace/bootstrap/create/start/execute, Worker-set
   emptiness with PID 1 alive, live collection, reuse or destroy, and final
   whole-resource absence;
2. persisted/armed deadline through guardian failure, independent exact-bound
   action, confirmed or unknown result, and cleanup/reconciliation; and
3. provider-proved no-process start failure through exact `START_FAILED` and a
   legal retry/cleanup state.

UNIT/FAKE/DOCKER test IDs remain future specifications. They cover every R1-R4
branch and are not execution evidence from this documentation task.

## Protected boundaries

No `src/`, `tests/`, dependency, Constitution, core-belief, accepted ADR,
Architecture, product/workflow, historical review, completed Stage 1 or planned
Stage 3-14 path is modified. Stage 1 remains six entities, 43 states and 99
lifecycle edges. ADR-0002 remains Docker-first and replaceable. Initial network
support remains `NONE` only.

## Validation contract

- inspect exact changed paths, whitespace and complete staged diff before each
  commit using explicit-file staging only;
- validate Markdown fences and tracked repository-relative links/anchors;
- verify R1-R4 type/state/operation consistency and walkthrough A/B/C closure;
- verify test IDs are unique and continuous;
- verify the exact two-commit chain, titles and per-commit path whitelists;
- audit protected paths and final worktree state;
- do not claim planned UNIT/FAKE/DOCKER cases executed.

## Candidate disposition

```text
Stage 1 = COMPLETE, unchanged
Stage 2 = ACTIVE
ADR-0008 = PROPOSED
Sandbox design = corrected M1B CANDIDATE
R1-R4 = addressed by candidate; independent acceptance PENDING
Issue #79 = BLOCKED / NOT RELEASED
Stage 2 runtime code = NOT YET STARTED
Stage 2 complete = NO
Stage 3 = PLANNED / not activated
remote mutation = none
```
