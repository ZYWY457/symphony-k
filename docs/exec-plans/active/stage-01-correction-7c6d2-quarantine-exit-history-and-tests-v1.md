# Stage 1 Correction 7C6D2 — Quarantine Exit History and Tests

**Version:** 1
**Scope:** GitHub Issue #59 — forward correction of M7C6D/M7C6D1

## Execution evidence

TaskSpec reference: GitHub Issue #59
TaskSpec access mode: materialized-handoff
TaskSpec precondition: PASS

The required baseline `d124e56d6406b7e310c5345d9dee096cd6f2fd18` was
verified before mutation, with a clean worktree and successful Git, Python, and
UV preflight.

## Bounded correction

Strengthen only the four existing non-creation quarantine exits.  Revalidate
the supplied historical quarantine context as an authentic canonical entry:
an Effect Controller recorded it, its reason and source are compatible, and
its supplied observation, original-commit, or compensation-plan lineage is
exactly bound by the relevant exit.

For compensation resume and direct completion, require the supplied historical
start event to have the exact version of the COMPENSATING snapshot that entered
quarantine.  Direct completion validates historical authorization against the
historical start controller rather than the current completion controller;
current transition authority remains independently bound by M7B1/M7B2.

Emit narrow `quarantine_context_id` and `reconciliation_id` annotations on all
four exit lifecycle events, retaining their existing remediation lineage
annotations.  Expand the dedicated suite through public `transition_entity()`
calls, including valid paths, provenance substitutions, actor separation,
S1-to-S2-to-completion lineage, and unchanged nineteen-edge topology.

## Out of scope

No creation edge, persistence/repository lookup, reconciliation or dispatch
runtime, external rollback/compensation execution, linked-Effect execution,
new state, topology change, or Stage 2 work is introduced.  This plan leaves
the prior #57 and #58 plans and the stage-completion plan unchanged.

## Candidate status

Effect non-creation candidate = 19 / 19
Stage 1 non-creation candidate = 91 / 91

Human acceptance remains pending; this correction makes no M7 or Stage 1
completion claim.
