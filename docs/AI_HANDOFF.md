# AI and Maintainer Handoff

This workflow is model-, account- and vendor-neutral. No chat transcript,
private memory, model state or prior account context is a source of truth. A
fresh maintainer must be able to resume from durable repository and TaskSpec
artifacts alone.

## Required resume sequence

1. Read `CONSTITUTION.md`.
2. Read `STATUS.md`.
3. Read `AGENTS.md`.
4. Read `VISION.md`.
5. Read `ARCHITECTURE.md`.
6. Read `ROADMAP.md`.
7. Read `docs/DEVELOPMENT_PATH.md`.
8. Read relevant `docs/core-beliefs/`, accepted ADRs and accepted designs.
9. Read the current active stage parent plan, if `STATUS.md` names one.
10. Read the concrete durable GitHub Issue TaskSpec.
11. Independently inspect repository truth before trusting any Worker report.
12. Implement only the Issue scope.
13. Run the required validation and inspect the exact candidate diff.
14. Create local commits only unless remote mutation is explicitly authorized.
15. Obtain independent Human Review before stage or status promotion.

If a referenced file or durable TaskSpec cannot be read, or the required
baseline is wrong, stop before mutation and report the failed precondition.

## Authority and current truth

Use the hierarchy in `CONSTITUTION.md`. `STATUS.md` is the compact current-status
entry point but cannot override higher-authority constitutional or architecture
artifacts. Completed plans and Git history are authoritative historical evidence,
not automatic statements of current status.

A Worker candidate is not Human Accepted truth. A local commit proves only that
a candidate object exists. Acceptance requires the independent review and
governance gate defined by its TaskSpec or parent plan. A stage is `COMPLETE`
only after independent Human Exit acceptance and a later durable governance
reconciliation updates `STATUS.md` and archives the parent plan.

## TaskSpec precondition and contradictions

Before mutation, establish a concrete, pre-existing durable Issue identity and
record either `direct-read` or `materialized-handoff` exactly as defined by
`AGENTS.md`. A title, draft, future number, placeholder identity or
conversation-only instruction is insufficient.

Stop when the TaskSpec, required baseline, repository truth or higher-authority
artifact conflicts. Report the exact sources and contradiction. Do not select a
convenient interpretation, materialize a missing Issue retroactively or backfill
governance after implementation.

## Architecture discoveries

If work reveals a new top-level concept, cross-cutting dependency, changed
authority boundary, trust assumption or constitutional conflict:

1. stop at the discovery boundary;
2. preserve evidence and the workspace without broadening the Issue;
3. propose an ADR or constitutional amendment as required by authority;
4. resume implementation only after the decision and a durable bounded TaskSpec.

Future parent plans identify expected ADRs but do not decide their contents.

## Corrections and historical truth

Rejected or failed candidates remain historical facts. A correction uses a new
Issue, commit, Evaluation or governance record that references what it corrects.
Do not amend history to imply the original candidate was accepted, erase an
Effect occurrence, replace evidence provenance or convert compensation into a
fictional rollback.

## Exec Plan lifecycle

```text
planned/   future parent contract; no execution authorization
    -> Human-approved durable activation TaskSpec and prerequisite stage exit
active/    current authorized planning/implementation parent contract
    -> milestone acceptance + independent Human Stage Exit Review
completed/ exited and accepted historical contract
```

Moving a plan does not itself authorize code. Activation and completion are
governance decisions recorded by durable TaskSpecs. Find the next work from
`STATUS.md`, then verify it against the roadmap and parent plan.

## Current development Issue lifecycle

```text
DRAFT TASKSPEC
    -> durable GitHub Issue exists
    -> Worker candidate implementation
    -> local validation
    -> Human publishes according to the current workflow
    -> independent Human Review
    -> ACCEPTED or REQUEST CHANGES
    -> correction Issue when required
    -> governance reconciliation
    -> stage exit when applicable
```

GitHub Issues are the current manual development-governance carrier, not a
future Symphony-K product-domain dependency. Remote publication is an external
effect and remains outside a Worker Task unless explicitly authorized.

## Handoff evidence

Every completed Worker report should identify the TaskSpec and access mode,
starting baseline, exact commits and parents, changed files, validation commands
and results, unresolved risks, final worktree state and every remote mutation.
If none occurred, state `remote mutation = none` explicitly.
