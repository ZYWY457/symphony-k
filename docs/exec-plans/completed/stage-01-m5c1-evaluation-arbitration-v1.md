# Stage 1 M5C1 — Evaluation Arbitration Records

**Version:** 1
**Status:** Implementation and required validation completed, 2026-09-08
**Scope:** [Implementation #5C1 / GitHub Issue #10](https://github.com/ZYWY457/symphony-k/issues/10), under the accepted [Stage 1 plan](../active/stage-01-domain-kernel.md), [ADR-0005](../../adr/0005-core-state-machine-semantics.md), and [Evaluation design](../../design-docs/state-machines.md#7-evaluation).

## Objective and Boundary

Implement immutable supporting records for direct and exact conflict-set-linked
Evaluation arbitration, including typed identity, disposition semantics, decision
provenance, and a pure structural compatibility predicate.

This slice does not derive an effective judgement across history, resolve one or more
conflict sets, release an Evaluation for use, record invalidation, mutate Evaluation
state/content/version, emit events, enforce authority, or add repositories/persistence.
It implements M5C1 only, not M5C2 or a seventh Stage 1 entity.

## Representation Decisions

`EvaluationArbitrationId` follows the existing nominal UUID convention and identifies
one immutable decision record; no ArbitrationVersion exists. `ArbitrationDisposition`
contains exactly UPHELD, MODIFIED and REVERSED and is independent of Evaluation state.
`EvaluationArbitrationPolicyRef` retains opaque, meaningful policy ID/version strings
without evaluating policy or granting authority.

Each `EvaluationArbitrationMemberDecision` retains an `EvaluationId`, observed
`EntityVersion`, disposition, optional prior effective judgement, and mandatory
effective judgement. UPHELD requires an equal prior judgement; MODIFIED permits no
prior judgement but requires inequality when one exists; REVERSED requires a prior
judgement and inequality. Judgements remain opaque `EvaluationVerdict` values, so no
logical-opposite taxonomy is invented.

`EvaluationArbitrationRecord` contains:

```text
arbitration_id: EvaluationArbitrationId
conflict_set_ref: EvaluationConflictSetRef | None
decisions: frozenset[EvaluationArbitrationMemberDecision]
rationale: str
evidence_refs: frozenset[EvidenceRef]
policy_ref: EvaluationArbitrationPolicyRef
decided_by: ActorIdentity
decided_at: Timestamp
correlation_id: CorrelationId
prior_arbitration_id: EvaluationArbitrationId | None
```

It requires at least one unique Evaluation decision and immutable typed provenance.
No conflict reference means direct arbitration and requires exactly one decision.
A conflict reference permits one or more decisions; exact conflict membership cannot
be proven from constructor-local data and is intentionally checked by the pure
compatibility predicate. Optional lineage rejects only immediate self-reference in
M5C1 and performs no lookup or cycle traversal. Actor type and policy reference are
provenance, not authority.

`can_arbitrate_evaluation_conflict_set` requires a conflict reference with the exact
conflict-set ID/version, equal correlation identity, exactly the member Evaluation IDs
with no omissions/extras, and an arbitration observed version equal to or later than
the corresponding conflict member version. It performs no transition, write, global
resolution, or current-version assertion.

## Tests and Boundary Evidence

Runtime tests cover nominal identity separation, the exact disposition inventory,
policy/member/record invariants, immutability, direct arbitration, one- and multi-member
conflict arbitration, every compatibility rejection, provenance-only actor categories,
lineage, and preservation of the original Evaluation/EvaluationResult. Static examples
preserve distinctions among arbitration/evaluation/conflict/correlation identities,
EntityVersion/ConflictSetVersion, verdicts and typed evidence. The prior M5B test was
updated only to stop asserting that the now-required public disposition enum is absent;
its conflict-set behavior remains unchanged.

The `Evaluation` and `EvaluationResult` source files and field models are unchanged.
Tests explicitly confirm no effective-judgement field, disposition field, arbitration
field/method, resolver, invalidation record, event, repository, controller, or
arbitration lifecycle state was introduced.

## Validation Evidence

Python 3.12.7 with the unchanged locked pytest 9.1.1, Ruff 0.16.6 and mypy 1.20.2.
No dependency, lock-file, Python-version or quality-configuration change occurred.
A repository-local ignored `.uv-cache` was used because the sandbox cannot write the
host uv cache.

| Required command | Final result |
| --- | --- |
| `uv --cache-dir .uv-cache sync --dev --locked` | Exit 0; resolved and checked 13 packages |
| `uv --cache-dir .uv-cache run pytest` | Exit 0; 1167 passed; one environment-only Pytest cache warning |
| `uv --cache-dir .uv-cache run ruff check .` | Exit 0; all checks passed |
| `uv --cache-dir .uv-cache run ruff format --check .` | Exit 0; 77 files already formatted |
| `uv --cache-dir .uv-cache run mypy src tests` | Exit 0; no issues in 45 source files |
| `git diff --check` | Exit 0; Windows LF-to-CRLF notices only |

The first full pytest run identified one stale M5B scope assertion that the public API
had no `ArbitrationDisposition`; it was removed as required by M5C1. All other 1166
tests passed in that run, and the final full suite passed. Initial focused checks also
found only import ordering and test-ignore placement, corrected without weakening
types or production validation.

## Explicit Local Commit Whitelist

- `README.md`
- `docs/exec-plans/completed/stage-01-m5c1-evaluation-arbitration-v1.md`
- `src/symphony_k/domain/__init__.py`
- `src/symphony_k/domain/evaluation_arbitration.py`
- `src/symphony_k/domain/ids.py`
- `tests/test_evaluation_arbitration.py`
- `tests/test_evaluation_conflict.py`
- `tests/test_ids.py`
- `tests/typing_examples.py`

## Completion Boundary

The implementation used only durable repository content and read-only GitHub Issue
#10. The optional `agent-reach` GitHub route documented `gh`, but the executable was
unavailable; the public GitHub Issue API supplied the same authoritative Issue and its
empty comment list. No historical conversation or external design source was used.

No architecture gap, dependency change, semantic deviation, M5C2 behavior, or remote
mutation occurred. Only the nine paths above may be staged explicitly. Inspect the
cached names, whitespace and full diff before creating one local commit, then stop.
