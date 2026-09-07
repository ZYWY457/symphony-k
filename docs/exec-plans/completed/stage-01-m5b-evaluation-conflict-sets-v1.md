# Stage 1 M5B — Evaluation Conflict Sets

**Version:** 1
**Status:** Implementation and required validation completed, 2026-09-07
**Scope:** [Implementation #5B / GitHub Issue #9](https://github.com/ZYWY457/symphony-k/issues/9), under the accepted [Stage 1 Exec Plan](../active/stage-01-domain-kernel.md), [ADR-0005](../../adr/0005-core-state-machine-semantics.md), and [Evaluation design](../../design-docs/state-machines.md#7-evaluation).

## Objective

Implement immutable supporting records for explicit, versioned Evaluation conflict sets and their pure append-only structural relation. Preserve the six-entity boundary and leave Evaluation snapshots unchanged.

## Context and Architecture Constraints

- Conflict sets are audit/provenance support records, not a seventh top-level entity.
- Original Evaluation content and evidence remain immutable and conflict membership is not duplicated into Evaluation.
- Actor classification records provenance but grants no authority.
- This slice stores observed versions and structural history only; it does not execute transitions or claim atomic persistence.
- Only the standard library and existing Stage 1 primitives are required. No ADR or dependency change is needed.

## In Scope

- Distinct typed `EvaluationConflictSetId` and `CorrelationId` UUID identities.
- Immutable non-negative `ConflictSetVersion`, separate from `EntityVersion`.
- Immutable member, affected-scope and exact conflict-set references.
- Complete immutable `EvaluationConflictSetRecord` snapshots with conflict-support and member-identity invariants.
- A pure append-only extension compatibility query.
- Public exports, deterministic runtime tests, strict-mypy negative examples and concise repository documentation.

## Out of Scope

- Arbitration records/dispositions, effective judgments and invalidation history.
- Evaluation transition execution, state/version mutation, events or atomic multi-record writes.
- Conflict-set lifecycle states, controllers or aggregate execution.
- Repositories, persistence and physical-delete enforcement.
- Verification runtime, scope taxonomy/equivalence, target lookup or semantic materiality judgments.
- M5C and later milestone behavior.

## Bounded Milestones

1. Add the typed identities/version and immutable conflict-set value/reference/record model.
2. Add exhaustive invariant, extension, boundary and static-type tests while leaving Evaluation unchanged.
3. Run the Issue-required validation suite, inspect only the explicit staged whitelist, and create one local commit.

## Risks and Controls

- **Accidental seventh entity:** keep the record free of state/controller/aggregate lifecycle concepts and document it as supporting provenance.
- **Two membership sources:** do not modify `Evaluation`; assert its exact field set in boundary tests.
- **History overclaim:** name the query as a structural predicate and avoid repositories, writes or events.
- **Type collapse:** use nominal ID subclasses and a separate version dataclass; add negative mypy examples.
- **Scope over-modeling:** retain one opaque non-whitespace reference without target equivalence logic.

## Acceptance Criteria

- The record enforces at least one Evaluation and requires either a second member or external conflict evidence.
- Each Evaluation identity occurs at most once per record.
- Valid extensions retain identity, correlation, scope, members and evidence; retained member versions never regress.
- Conflict-set versions need only move forward and link explicitly to the prior version; they need not be consecutive.
- All supporting values and collections are immutable and publicly exported.
- No Evaluation field, transition, arbitration/invalidation behavior, repository, event, persistence or dependency is added.
- Every required validation command passes before explicit-file staging and the single local commit.

## Completion Evidence

Record the exact field model, invariants, extension rules, validation results, explicit committed file list and local commit hash. Confirm repository-plus-Issue cold start, unchanged dependencies, no M5C behavior, explicit-file staging and no remote mutation.

## Representation Decisions

`EvaluationConflictSetId` and `CorrelationId` use the existing nominal UUID base while remaining distinct from one another and every entity ID. `ConflictSetVersion` is a separate frozen integer value, rejects booleans and negative values, and has neither a default nor a convenience increment that would suggest a starting or consecutiveness rule.

`EvaluationConflictMemberRef` contains only `evaluation_id: EvaluationId` and `observed_version: EntityVersion`. `EvaluationConflictScopeRef` preserves meaningful opaque text exactly; it neither stores targets nor proves their equivalence. `EvaluationConflictSetRef` retains an exact conflict-set ID/version pair and performs no lookup.

`EvaluationConflictSetRecord` has exactly these required fields:

```text
conflict_set_id: EvaluationConflictSetId
version: ConflictSetVersion
previous_version: ConflictSetVersion | None
members: frozenset[EvaluationConflictMemberRef]
affected_scope: EvaluationConflictScopeRef
disagreement_summary: str
evidence_refs: frozenset[EvidenceRef]
recorded_by: ActorIdentity
recorded_at: Timestamp
correlation_id: CorrelationId
```

The record is frozen with immutable nested value objects and collections. It requires at least one Evaluation member. One member is supported only when at least one external `EvidenceRef` records the opposing/material-conflict side; two or more members need no additional evidence. Each `EvaluationId` appears at most once even when different observed versions are supplied. Actor category remains unconstrained provenance and grants no authority.

`can_extend_evaluation_conflict_set` returns structural compatibility only. It requires the same conflict-set ID, a strictly later but not necessarily consecutive version, an exact previous-version link, unchanged correlation and affected scope, retention of every prior Evaluation identity, non-regression of each retained observed `EntityVersion`, and a superset of prior evidence. It permits new members, new evidence, retained member versions, advanced member versions, revised summaries and new recorder/time provenance. It mutates neither record and performs no write.

Different target categories are demonstrably representable in one conflict set: tests construct Outcome- and Effect-targeted Evaluations and store their typed IDs/observed versions under one explicit common scope. The supporting record contains no target-equality guard or target object. The M5A `Evaluation` field set and source file remain unchanged; conflict membership exists only in conflict-set records.

## Required Validation

Python 3.12.7 with the existing locked pytest 9.1.1, Ruff 0.16.6 and mypy 1.20.2. A repository-local `.tmp-uv-cache` was used because the sandbox cannot write the host uv cache; it is temporary and excluded from staging. No dependency, lock-file or quality-configuration change occurred.

| Required command | Final result |
| --- | --- |
| `uv sync --dev --locked` | Exit 0; resolved and checked 13 packages |
| `uv run pytest` | Exit 0; 1090 passed |
| `uv run ruff check .` | Exit 0; all checks passed |
| `uv run ruff format --check .` | Exit 0; 74 files already formatted |
| `uv run mypy src tests` | Exit 0; no issues in 43 source files |
| `git diff --check` | Exit 0; only Windows LF-to-CRLF notices |

Pytest emitted one environment-only warning because the restricted workspace could not update its existing `.pytest_cache`; all 1090 tests ran and passed. Runtime tests cover identity/typing, immutable values, exact field models, conflict support, membership uniqueness, every actor category, target diversity, valid extension variants and each required rejection. Static examples preserve all distinctions required by the Issue.

## Explicit Local Commit Whitelist

- `README.md`
- `docs/exec-plans/completed/stage-01-m5b-evaluation-conflict-sets-v1.md`
- `src/symphony_k/domain/__init__.py`
- `src/symphony_k/domain/evaluation_conflict.py`
- `src/symphony_k/domain/ids.py`
- `src/symphony_k/domain/version.py`
- `tests/test_evaluation_conflict.py`
- `tests/test_ids.py`
- `tests/test_version.py`
- `tests/typing_examples.py`

## Completion Boundary

The implementation needed only durable repository content and read-only GitHub Issue #9; no previous conversation history or other design source was used. It adds no seventh entity, Evaluation field/state mutation, conflict-set state/controller, arbitration/disposition/effective judgment, invalidation history, event, repository, persistence or M5C+ behavior. No unresolved architecture question or deviation was found. Stage 1 M5 remains incomplete after this bounded M5B slice.

Only the ten files above may be staged by explicit path. Inspect the cached name/status, whitespace and full diff before creating the single local commit. No push, PR/Issue mutation, remote ref change or release publication is authorized.
