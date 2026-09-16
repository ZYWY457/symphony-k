# Stage 1 Correction M8D - Effect Historical Provenance

**Version:** 1
**Status:** correction candidate complete; independent Human Review required
**TaskSpec reference:** https://github.com/ZYWY457/symphony-k/issues/73
**TaskSpec access mode:** materialized-handoff
**TaskSpec precondition:** PASS
**Required parent:** `9de2d81135412f7f02da009a1dd3cb09fb77b365`

## Governance history

The initial Issue #73 execution stopped before repository mutation because its
same-S1 acceptance condition contradicted the accepted M7 version binding. Human
Review corrected the TaskSpec: `PLANNED(vN) -> SIMULATED(vN+1)` records S1 bound
to vN, while `SIMULATED(vN+1) -> PENDING_COMMIT(vN+2)` records a distinct S2
bound to vN+1. M7 remains Human Accepted and unchanged.

## Scope

1. Classify each accepted Effect semantic input by lifecycle role, not record
   class, as current-operation provenance or required historical provenance.
2. Add an internal exact-record lookup and an Effect-specific persistence
   validator that runs inside the authoritative transaction before the pure
   transition and before provenance insertion.
3. Bind historical original commit observations, compensation plans, quarantine
   contexts, prior observations/incidents and prior authorization provenance to
   durable supporting history and existing lifecycle events where applicable.
4. Add focused and constitutional regressions built through the real lifecycle
   service, including the corrected S1/S2 sequence.

No domain source, lifecycle topology, event vocabulary, creation semantics or
external Effect execution is in scope.

## Verification plan

Before the production correction, reproduce a later transition backfilling a
fabricated original commit observation or compensation plan. After correction,
run every focused persistence suite, the constitutional suite, the full suite,
Ruff, format checking, mypy and staged/unstaged diff checks required by Issue
#73. Stage explicit paths and create one forward local commit only.

## Complete Effect transition provenance classification

Classification follows lifecycle meaning. A record class may be current on one
edge and historical on another.

| Edge | NEW_IN_THIS_OPERATION | HISTORICAL_REQUIRED |
|---|---|---|
| `PLANNED -> SIMULATED` | simulation S1 bound to the PLANNED snapshot | none |
| `PLANNED -> PENDING_COMMIT` | preparation, verification, remediation readiness, accepted simulation bypass | none |
| `SIMULATED -> PENDING_COMMIT` | simulation S2 bound to the current SIMULATED snapshot, preparation, verification, remediation readiness | none; S1 is not consumed |
| `PLANNED -> COMMITTED` | occurrence observation, authorization finding, optional governance finding | none |
| `SIMULATED -> COMMITTED` | occurrence observation, authorization finding, optional governance finding | none |
| `PENDING_COMMIT -> COMMITTED` | occurrence observation, authorization finding, optional governance finding | none |
| `QUARANTINED -> COMMITTED` | new confirmed observation, authorization finding, optional governance finding | quarantine entry context and all prior observation/incident/original-commit/plan references consumed from that entry |
| `PLANNED -> QUARANTINED` | quarantine context, uncertain observation, optional incident | none |
| `SIMULATED -> QUARANTINED` | quarantine context, uncertain observation, optional incident | none; prior simulation is not consumed by this semantic input |
| `PENDING_COMMIT -> QUARANTINED` | quarantine context, uncertain observation, optional incident | none |
| `COMMITTED -> QUARANTINED` | quarantine context and optional incident | original confirmed commit observation that established the current COMMITTED path |
| `COMPENSATING -> QUARANTINED` | quarantine context and optional incident | original confirmed commit observation and compensation plan that established the current COMPENSATING path |
| `COMMITTED -> ROLLED_BACK` | rollback record and current remediation authorization | original confirmed commit observation |
| `COMMITTED -> COMPENSATING` | compensation plan and current remediation authorization | original confirmed commit observation |
| `COMPENSATING -> COMPENSATED` | completion record and current completion authorization | original confirmed commit observation, compensation plan, exact compensation-start event; for a resumed path also prior authorization, quarantine context and reconciliation lineage |
| `QUARANTINED -> PENDING_COMMIT` | disproved observation, reconciliation, preparation, verification, readiness and applicable current bypass provenance | quarantine context, prior uncertain observation and any retained entry incident |
| `QUARANTINED -> ROLLED_BACK` | reconciliation, rollback record and current remediation authorization | quarantine context, original confirmed commit observation and retained entry references |
| `QUARANTINED -> COMPENSATING` | reconciliation and current resume/new-plan authorization; a NEW_PLAN plan is also current | quarantine context and original commit observation; RESUME_EXISTING_PLAN additionally requires the prior plan and exact prior compensation-start event |
| `QUARANTINED -> COMPENSATED` | reconciliation and completion record | quarantine context, original commit observation, compensation plan, exact compensation-start event and exact historical start authorization |

Stored quarantine-context references are also checked according to their entry
meaning: its uncertain observation and incident were recorded with the entry;
its original commit observation was recorded by a COMMITTED event; and its plan
was recorded by a COMPENSATING event.

## Evidence

The pre-fix original-commit substitution regression failed with `DID NOT RAISE
ConcurrencyConflict`, proving that a structurally valid O2 was backfilled by the
later rollback. After the bounded persistence correction, O2 is rejected before
writes and the exact durable O1 path succeeds.

Final focused evidence: codec 23, SQLite 12, service 42, Evaluation 5, Effect
10, and constitutional 32 passed. The full suite passed all 3269 tests. Locked
sync, Ruff, format (211 files), mypy (123 source files) and the unstaged diff
check passed. The correction changes no domain source.
