# Stage 1 M5C3 — Evaluation Effective-Use Derivation

**Version:** 1
**Status:** Implementation and required validation completed, 2026-09-08
**Scope:** [Implementation #5C3 / GitHub Issue #12](https://github.com/ZYWY457/symphony-k/issues/12), under the accepted [Stage 1 plan](../active/stage-01-domain-kernel.md), [ADR-0005](../../adr/0005-core-state-machine-semantics.md), and [Evaluation design](../../design-docs/state-machines.md#7-evaluation).

## Objective and Boundary

Implemented an immutable derived view and pure resolver for one already-recorded
Evaluation. The caller supplies the current applicable ConflictSet versions and
complete relevant arbitration and invalidation history. The resolver performs no
lookup, persistence, transition, event emission, authority check, version selection,
or lifecycle mutation, and cannot prove repository completeness.

No ADR was required: this completes the already accepted M5 derived semantics without
adding an authoritative entity, lifecycle state, cross-cutting dependency, or M6+
behavior. Only the standard library and existing Stage 1 domain primitives are used.

## Derived View and Input Contract

`EvaluationEffectiveUseView` is frozen and contains the subject Evaluation ID,
original/effective judgements, exact applicable/unresolved ConflictSet references,
supporting arbitration IDs, optional terminal arbitration ID, ambiguity flag,
invalidation IDs, and eligibility flag. Its invariants prevent unresolved conflicts
outside the applicable set, an effective-use flag without a judgement, and any
effective terminal result when arbitration is ambiguous.

`derive_evaluation_effective_use` accepts only typed immutable frozensets. Each
supplied current conflict record must contain the subject and each ConflictSet ID may
appear at most once; duplicate versions are rejected rather than selected. Every
invalidation must concern the subject. Arbitration records without a decision for the
subject are excluded from its judgement lineage. They remain usable only to establish
that a referenced prior record was supplied but does not affect this Evaluation.

The input is explicitly a caller-provided complete current history slice. M5C3 neither
queries storage nor determines which ConflictSet version is current. M8 repository
logic remains responsible for authoritative current-version selection and history
completeness.

## Arbitration Lineage and Consistency

Arbitration identity is checked for uniqueness. A relevant record's
`prior_arbitration_id` creates a precedence edge only when the referenced supplied
record also contains a decision for this Evaluation. An absent referenced record makes
the relevant lineage incomplete and is rejected. A supplied unrelated prior creates
no precedence. Cycles are rejected with `InvariantViolation`.

Heads are derived solely from those explicit edges. More than one head, whether from
disconnected roots or a fork, yields `arbitration_ambiguous=True`, no terminal ID, no
effective judgement, and no eligibility. Equal judgement values do not collapse this
provenance ambiguity. Neither timestamps, versions, insertion/iteration order nor IDs
participate in precedence.

For a unique chain, a first decision cannot claim a prior judgement different from the
original and cannot invent one when the Evaluation has no original result. Every later
decision's prior judgement must exactly equal the preceding decision's effective
judgement. The existing structurally valid MODIFIED-with-None decision may establish a
judgement on a no-original-result path.

## Conflict, Invalidation, and Lifecycle Rules

A current conflict is resolved only by an existing arbitration structurally compatible
with its exact ID/version through `can_arbitrate_evaluation_conflict_set`. Direct or
older-version arbitration does not cover it. Every unresolved applicable conflict is
retained; resolving X never removes Y. CONFLICTED stays ineligible even when all sets
are addressed. ARBITRATED is eligible only with one derived terminal judgement, no
ambiguity, every exact current conflict addressed, and no invalidation history.

PENDING and RUNNING have no effective judgement and reject subject arbitration
history. COMPLETED uses its original judgement only when no conflict, arbitration, or
invalidation history is supplied; an unfavorable opaque judgement remains eligible.
ARBITRATED requires relevant arbitration history. INVALID requires same-Evaluation
invalidation provenance and never returns an effective judgement. All historical
inputs remain visible in the derived view and unchanged.

## Test and Boundary Evidence

Thirty-eight deterministic tests cover baseline and negative verdicts, PENDING/RUNNING,
one/two conflicts, partial and exact multi-conflict coverage, stale conflict versions,
direct and linear lineage, absence of timestamp precedence, missing lineage, unrelated
prior records, cycles, disconnected/forked/equal-value ambiguity, judgement-chain
consistency, no-original establishment, all lifecycle gates, invalidation, input scope,
typed collections, duplicate history identities, immutable history, exact view fields,
and absence of repository, transition, event, authority, current-selection, or
latest-wins behavior. Static mypy
examples preserve the view, verdict, conflict-reference, and history collection types.

## Validation Evidence

Python 3.12.7 with unchanged locked pytest 9.1.1, Ruff 0.16.6 and mypy 1.20.2.
A repository-local ignored `.uv-cache` was used because the sandbox cannot write the
host cache.

| Required command | Final result |
| --- | --- |
| `uv --cache-dir .uv-cache sync --dev --locked` | Exit 0; resolved and checked 13 packages |
| `uv --cache-dir .uv-cache run pytest` | Exit 0; 1255 passed; one environment-only Pytest cache warning |
| `uv --cache-dir .uv-cache run ruff check .` | Exit 0; all checks passed |
| `uv --cache-dir .uv-cache run ruff format --check .` | Exit 0; 83 files already formatted |
| `uv --cache-dir .uv-cache run mypy src tests` | Exit 0; no issues in 49 source files |
| `git diff --check` | Exit 0; Windows LF-to-CRLF notices only |

## Explicit Local Commit Whitelist

- `README.md`
- `docs/exec-plans/completed/stage-01-m5c3-evaluation-effective-use-v1.md`
- `src/symphony_k/domain/__init__.py`
- `src/symphony_k/domain/evaluation_effective_use.py`
- `tests/test_evaluation_effective_use.py`
- `tests/typing_examples.py`

## Completion Boundary

The implementation used only durable repository content and read-only GitHub Issue
#12. The required `agent-reach` GitHub route documented `gh`, but that executable was
unavailable; the public Issue was read through a read-only browser. No previous
conversation or external design source was used.

No dependency change, semantic deviation, unresolved architecture question,
repository/current-record discovery, transition execution, event, M6+ behavior, or
remote mutation occurred. Only the six paths above may be staged explicitly. Inspect
the cached names, whitespace, and full diff before creating the single local commit.
