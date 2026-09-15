# Stage 1 M7D5 — Observed Effect Creation

**Version:** 1
**Status:** Candidate; independent Human Review required
**TaskSpec:** https://github.com/ZYWY457/symphony-k/issues/70
**TaskSpec access mode:** materialized-handoff
**TaskSpec precondition:** PASS
**Parent:** `a3551cee6b46b667e70820afb3fbb05a9290da1b`

## Scope and sequence

Register confirmed occurrence as COMMITTED and uncertain occurrence as
QUARANTINED, with exactly one v1 event. Preserve occurrence, authorization and
governance as separate dimensions. Unauthorized confirmed occurrence remains
recordable. Worker self-report cannot anchor occurrence.

1. Reuse EffectObservationRecord, authorization/governance findings and incident
   records, exact-bound to the resulting version 1, not a fabricated source.
2. Add a creation-only immutable quarantine context using the accepted reason
   vocabulary. Existing transition context requires a source state and cannot
   be reused for absence; no existing non-creation type changes.
3. Bind immutable origin/target/payload, operation/dedup identity, observer,
   recorder, times, evidence, request identity, and known Task/Run attribution.
4. Prove observation substitution and worker/relabel rejection, separate truth
   dimensions, exact annotations, guard failures and no execution dependencies.
5. Run focused/full tests and all static/diff gates before the local commit.

No planning history, authorization grant, dispatch, retry, persistence or
reconciliation runtime. Later disproval appends history through existing
lifecycle semantics; it cannot rewrite creation. M8 handles durable deduplication.
Human Accepted remains creation `2 / 8`, integrated `93 / 99`.

## Candidate validation evidence

Focused observed Effect suite: 55 passed. Full suite: 2943 passed.
Ruff, format (184 files), mypy (102 source files), and diff checks passed.
The shared creation architecture regression inspects every creation module for
external dependencies and forbidden execution calls. All accepted non-creation
tests remain passing. Repository-ignored `.uv-cache` remains the cache fallback.
