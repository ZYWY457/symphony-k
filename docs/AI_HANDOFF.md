# AI and Maintainer Handoff

This workflow is model-, account- and vendor-neutral. No chat transcript,
private memory, model state or prior account context is a source of truth. A
fresh maintainer must be able to resume from durable repository and TaskSpec
artifacts alone.

## Required resume sequence

1. Read `CONSTITUTION.md`.
2. Read `STATUS.md`.
3. Read `AGENTS.md`.
4. Perform the current-task and review discovery sequence below.
5. Read `VISION.md`.
6. Read `ARCHITECTURE.md`.
7. Read `docs/V1_PRODUCT_CONTRACT.md`.
8. Read `ROADMAP.md`.
9. Read `docs/DEVELOPMENT_PATH.md`.
10. Read `docs/REFERENCE_WORKFLOWS.md`.
11. Read relevant `docs/core-beliefs/`, accepted ADRs and accepted designs.
12. Read the current active stage parent plan, if `STATUS.md` names one.
13. Freshly read the concrete durable GitHub Issue TaskSpec.
14. Independently inspect repository truth before trusting any Worker report.
15. Implement only the Issue scope.
16. Run the required validation and inspect the exact candidate diff.
17. Create local commits only unless remote mutation is explicitly authorized.
18. Obtain independent Human Review before stage or status promotion.

If a referenced file or durable TaskSpec cannot be read, or the required
baseline is wrong, stop before mutation and report the failed precondition.

## Current-task and review discovery

After reading `STATUS.md` and before mutation:

1. identify the exact accepted baseline and current stage;
2. identify the exact current candidate commit, if one exists, and inspect that
   object rather than relying on a Worker summary;
3. locate and read the latest review record for that exact candidate;
4. identify and read the concrete TaskSpec named as current governance or
   execution work;
5. inspect only the predecessor, correction and dependent Issues that
   materially determine the current task's lineage, readiness, review or
   approval state;
6. distinguish repository status from the dispatch/review queue;
7. establish whether execution overlap or Worker occupancy is known from a
   durable source before accepting a write task;
8. verify readiness, release conditions, baseline and approval independently;
9. report stale, missing or contradictory pointers instead of silently choosing
   one source; and
10. never invent a correction Issue identity or future baseline.

Do not make every historical Issue mandatory reading. Related-Issue discovery
is bounded by what can materially change the current task's authority or
interpretation.

The following distinctions are mandatory:

```text
Task discovery != execution authority.
Proposal/recommendation != approval.
Open/READY != known unclaimed work.
Largest Issue number != next task.
Unknown Worker occupancy != permission to assume no overlap.
No remote-write authority != no local implementation authority.
No write capability != no read capability.
```

A lack of stated Human implementation preference is not automatically a
missing precondition when the TaskSpec explicitly asks the Worker to recommend
a bounded solution. The Worker may recommend; it may not approve its own
proposal. Local implementation is permitted only when the TaskSpec authorizes
it and the environment supports it, even if remote writes remain prohibited.
Read and write capabilities must be checked and reported separately. Workers
must report actual tool limitations and must not claim validation they did not
execute.

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

## Product intent changes

The Product Contract freezes observable v1 scope and acceptance expectations;
the Reference Workflows make that scope testable. They remain subordinate to
the Constitution, core beliefs, accepted ADRs, Architecture and accepted
designs.

If a future TaskSpec or implementation would materially change supported
operator behavior, the v1 deployment boundary, required observable capability,
or canonical workflow semantics, stop rather than optimizing the documents
around the implementation. Obtain the required Human decision and ADR/design or
Product Contract reconciliation before resuming. Low-level choices that do not
change those boundaries remain owned by their future bounded stages.

During the current strategic transition, begin with `STATUS.md` and follow its
pointer to Issue #87, the Human decision gate. The Issue #86 GO-gate evidence
supports consideration of a formal amendment; it is not Human strategic product
approval. Issue #79 remains BLOCKED / NOT RELEASED and its old Stage 2 M2 scope
must not be re-released while the decision and resulting reconciliation remain
unresolved. If the product-intent change is approved, reconcile the applicable
Constitution and ADR decisions, Architecture, Product Contract and Roadmap
hierarchy before restarting implementation.

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

## Read-only cold-start acceptance checklist

Given only the repository URL and read access, a capable fresh maintainer or AI
must be able to report, with durable source references and without prior chat
memory:

- [ ] the exact accepted baseline and current stage;
- [ ] the exact current candidate commit;
- [ ] the latest review disposition and review artifact;
- [ ] which task is current governance/review work;
- [ ] which implementation task is blocked and why;
- [ ] the exact next technical correction required;
- [ ] which facts are Human Accepted versus candidate or reviewer judgment; and
- [ ] what it can and cannot execute with its actual tools.

Pass means correct, source-backed task/state discovery and honest capability
reporting. It does not require stylistic similarity or agreement with a
preferred model. A model that misreads complete durable evidence has failed the
execution/review test; governance documents should not expand indefinitely to
make every model pass. This checklist does not certify another AI. A Human may
run a separate external cold-start read-only test after publication.

## Handoff evidence

Every completed Worker report should identify the TaskSpec and access mode,
starting baseline, exact commits and parents, changed files, validation commands
and results, unresolved risks, final worktree state and every remote mutation.
If none occurred, state `remote mutation = none` explicitly.
