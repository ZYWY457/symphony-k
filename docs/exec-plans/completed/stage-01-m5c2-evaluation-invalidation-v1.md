# Stage 1 M5C2 — Evaluation Invalidation Records

**Version:** 1
**Status:** Implementation and required validation completed, 2026-09-08
**Scope:** [Implementation #5C2 / GitHub Issue #11](https://github.com/ZYWY457/symphony-k/issues/11), under the accepted [Stage 1 plan](../active/stage-01-domain-kernel.md), [ADR-0005](../../adr/0005-core-state-machine-semantics.md), and [Evaluation design](../../design-docs/state-machines.md#7-evaluation).

## Objective and Boundary

Implement immutable supporting records that retain why an exact Evaluation projection
is proven unusable, plus a pure structural compatibility predicate. Invalidation is
supporting judgment/provenance, not a seventh Stage 1 entity or a negative verdict.

This slice does not derive effective judgment, resolve conflicts, define an
invalidation taxonomy, execute Evaluation transitions, emit events, enforce authority,
or add repositories/persistence. It implements M5C2 only; M5C3 remains deferred.

## Representation Decisions

`EvaluationInvalidationId` follows the existing nominal UUID convention and remains
distinct from Evaluation, arbitration, conflict-set and correlation identities. It
identifies one immutable record; no invalidation version or lifecycle exists.

`EvaluationInvalidationRecord` contains exactly these mandatory fields:

```text
invalidation_id: EvaluationInvalidationId
evaluation_id: EvaluationId
observed_version: EntityVersion
reason: str
evidence_refs: frozenset[EvidenceRef]
invalidated_by: ActorIdentity
invalidated_at: Timestamp
correlation_id: CorrelationId
```

The record is frozen with immutable typed values and collection. `reason` retains
meaningful free-form text because no invalidation taxonomy is accepted. At least one
typed `EvidenceRef` is mandatory: the record represents an established evidence,
provenance or method defect, or verifier failure, rather than suspicion. Actor, time
and correlation retain provenance only and grant no authority. Evaluation result,
verdict, method, target and verifier are intentionally not copied because the exact
Evaluation ID/version anchors the subject.

`can_invalidate_evaluation` returns structural compatibility only. It requires equal
Evaluation identity, exact observed/current `EntityVersion`, and source state PENDING,
RUNNING, COMPLETED or CONFLICTED. ARBITRATED and INVALID are strict sinks and return
false. The predicate does not inspect verdict content or evidence substance, mutate a
snapshot/version, authenticate an actor, resolve a conflict, emit an event or perform
a repository operation.

## History and Scope Evidence

Tests establish that constructing a record and querying compatibility leave every
Evaluation field and the original `EvaluationResult` unchanged. An unfavorable opaque
verdict such as `FAIL` remains an ordinary COMPLETED Evaluation unless separately
invalidated. Separate conflict-set membership and arbitration records are compared
before and after invalidation-record creation and remain unchanged.

Boundary tests confirm there is no invalidation state/controller/repository/event,
effective-judgment or usability resolver, conflict resolver, or arbitration precedence
logic. The prior M5C1 scope test was updated only to stop asserting that the newly
required invalidation record is absent; all arbitration behavior remains unchanged.

## Validation Evidence

Python 3.12.7 with the unchanged locked pytest 9.1.1, Ruff 0.16.6 and mypy 1.20.2.
A repository-local ignored `.uv-cache` was used because the sandbox cannot write the
host uv cache. No dependency, lock-file, Python-version or quality-configuration change
occurred.

| Required command | Final result |
| --- | --- |
| `uv --cache-dir .uv-cache sync --dev --locked` | Exit 0; resolved and checked 13 packages |
| `uv --cache-dir .uv-cache run pytest` | Exit 0; 1217 passed; one environment-only Pytest cache warning |
| `uv --cache-dir .uv-cache run ruff check .` | Exit 0; all checks passed |
| `uv --cache-dir .uv-cache run ruff format --check .` | Exit 0; 80 files already formatted |
| `uv --cache-dir .uv-cache run mypy src tests` | Exit 0; no issues in 47 source files |
| `git diff --check` | Exit 0; Windows LF-to-CRLF notices only |

Runtime tests cover identity separation, exact mandatory field shape, immutability,
reason and evidence invariants, every actor category, the four accepted and two
rejected source states, identity/version mismatch, wrong input types, historical
content preservation and the M5C2 boundary. Static examples preserve distinctions
among all required IDs, `EntityVersion`, `ConflictSetVersion`, `EvidenceRef` and
`ArtifactRef`.

## Explicit Local Commit Whitelist

- `README.md`
- `docs/exec-plans/completed/stage-01-m5c2-evaluation-invalidation-v1.md`
- `src/symphony_k/domain/__init__.py`
- `src/symphony_k/domain/evaluation_invalidation.py`
- `src/symphony_k/domain/ids.py`
- `tests/test_evaluation_arbitration.py`
- `tests/test_evaluation_invalidation.py`
- `tests/test_ids.py`
- `tests/typing_examples.py`

## Completion Boundary

The implementation used only durable repository content and read-only GitHub Issue
#11. The optional `agent-reach` GitHub route documented `gh`, but the executable was
unavailable; the public Issue was read through a read-only browser instead. No previous
conversation or external design source was used.

No architecture gap, dependency change, semantic deviation, M5C3 behavior or remote
mutation occurred. Only the nine paths above may be staged explicitly. Inspect cached
names, whitespace and full diff before creating the single local commit, then stop.
