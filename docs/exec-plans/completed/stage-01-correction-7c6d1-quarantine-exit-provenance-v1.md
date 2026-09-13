# Stage 1 Correction 7C6D1 — Quarantine Exit Provenance

**Version:** 1  
**Scope:** GitHub Issue #58 — forward correction of M7C6D only

## Execution evidence

TaskSpec reference: GitHub Issue #58  
TaskSpec access mode: materialized-handoff  
TaskSpec precondition: PASS

The required starting HEAD was `0b10c0805e5eb788cffc7b76ea204d50566c418c`.

## Bounded correction

This correction retains the nineteen-edge topology and the accepted M7B1,
M7B2, M7C6C, and M7C6C1 semantics. It changes only the four existing
quarantine exits:

```text
QUARANTINED -> PENDING_COMMIT
QUARANTINED -> ROLLED_BACK
QUARANTINED -> COMPENSATING
QUARANTINED -> COMPENSATED
```

Every exit now exact-binds the historical quarantine entry to the immediate
prior version and one of the five legal inbound edges. Re-entry to
`PENDING_COMMIT` requires the actual `UNCERTAIN -> DISPROVED` observation
lineage anchored by the entry context; observed-origin Effects remain barred.
An evaluator cannot satisfy reconciliation independence merely by relabeling
the planned Effect producer's ActorId.

Resuming compensation requires a current, exact remediation authorization for
the pre-existing plan. The resumed transition creates a new authoritative
compensation-start event whose annotations retain the prior start-event ID.
Subsequent completion consumes that new event under the existing exact
completion checks while preserving the prior-start lineage.

## Out of scope

No external action, creation edge, completion-map modification, M8/Stage 2
work, reconciliation runtime, dispatch, retry, rollback execution, or
compensation execution is introduced.
