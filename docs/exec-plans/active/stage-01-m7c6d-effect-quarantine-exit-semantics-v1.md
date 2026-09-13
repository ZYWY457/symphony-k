# Stage 1 M7C6D — Effect Quarantine Exit Semantics

**Version:** 1
**Status:** Validated local candidate
**Scope:** GitHub Issue #57 only

## Execution evidence

TaskSpec reference: GitHub Issue #57
TaskSpec access mode: materialized-handoff
TaskSpec precondition: PASS

The required baseline `15e952ac474a0cf109573f8760d9974abb14a9f3` was the
starting HEAD. The worktree was clean and repository command, Git, Python and
UV preflight passed before mutation.

## Boundary

Canonicalize only these existing Effect non-creation edges:

```text
QUARANTINED -> PENDING_COMMIT
QUARANTINED -> ROLLED_BACK
QUARANTINED -> COMPENSATING
QUARANTINED -> COMPENSATED
```

Every exit supplies the immutable historical `EffectQuarantineContext` that
created the current snapshot and an independently evaluated immutable
`EffectReconciliationRecord`. The record binds the exact context ID, current
snapshot version, correlation, evidence and evaluator principal; it has closed
conclusions rather than caller-supplied booleans. Quarantine remains exclusion
from automatic execution, never occurrence, authorization or remediation truth.

- `PENDING_COMMIT` requires a compatible DISPROVED occurrence observation and
  the `NO_IN_FLIGHT_OR_DUPLICATE` conclusion, followed by the normal fresh
  preparation/verification guard. Observed-origin Effects are rejected, so
  observation cannot become execution intent through re-entry.
- `ROLLED_BACK` consumes the existing independently verified restoration record
  and exact remediation authorization, plus reconciled remedial uncertainty.
- `COMPENSATING` distinguishes a new post-commit authorized plan from resume of
  the exact plan attached to a prior COMPENSATING quarantine entry. Resume is
  bound to the original compensation-start event and retains its linked Effect
  set and original-commit lineage.
- `COMPENSATED` is available only from a compensation-uncertainty entry with
  that pre-existing plan and compensation-start event; it cannot invent a
  retrospective start or authorization record.

The implementation is pure domain validation. M7B1 transition authority and
M7B2 Effect Controller eligibility remain mandatory. It adds no reconciliation,
dispatch, retry, rollback or compensation runtime, and preserves the exact
nineteen-edge Effect topology and all fifteen existing canonical edges.

## Candidate status

Effect non-creation = 19 / 19
Stage 1 non-creation = 91 / 91

This is a candidate-only implementation result. Eight authoritative creation
edges remain unresolved, so M7 and Stage 1 are not complete. This plan does not
alter `stage-01-completion-v1.md` or claim human acceptance.
