# Stage 1 M9 - Constitutional Test Suite

**Version:** 1
**Status:** M9 HUMAN ACCEPTED
**TaskSpec reference:** https://github.com/ZYWY457/symphony-k/issues/72
**TaskSpec access mode:** materialized-handoff
**TaskSpec precondition:** PASS
**Parent:** `305c4170f82619b7948bed9130b875e2ffd5a9ce`

## Scope and acceptance

1. Name executable tests around worker authority, independent acceptance,
   non-propagating states and the accepted 43-state/99-edge topology.
2. Exercise durable Evaluation/Effect history, explicit human governance limits,
   transactional state/events, stale writers, uniqueness and idempotent replay.
3. Inspect imports and normal repository methods with AST/introspection; exercise
   the kernel under blocked Agent/Docker/network imports without external services.
4. Run the constitutional suite directly, all persistence suites, full pytest,
   locked sync, Ruff, format, mypy and diff checks. Stage explicit paths and make
   the fifth forward commit after reviewing its complete diff.

Reuse accepted domain inputs and bounded fixture builders. Constitutional tests
verify integration guarantees; existing detailed attack matrices remain in their
lower-level suites. Historical fixture seeding is test-only and does not create
a normal application bypass. No new feature, lifecycle edge, runtime, remote
mutation or Stage 1 reconciliation is authorized here.

M7 is Human Accepted at 99 / 99. M8 and M9 remain implementation candidates.
Stage 1 complete = NO. Stage 2 authorized = NO.

## Bounded production correction discovered by M9

Two new constitutional probes failed before correction with DID NOT RAISE
ConcurrencyConflict: Outcome acceptance could consume a supplied Evaluation
observation after its durable version/state changed, or consume a supplied
effective judgment different from the original judgment stored at the same
version. The M8C service checked its subject version but did not close this
cross-entity effective-use observation gap.

The correction is limited to `persistence/evaluation.py` and architecture wording.
Inside the existing transaction it compares the observed Evaluation's version,
state, target and verifier with the stored snapshot, rejects changing that same
Evaluation within the batch, and invokes the already accepted pure
`derive_evaluation_effective_use` with authoritative current conflict versions
and persisted arbitration/invalidation history. A mismatch is ConcurrencyConflict
with no writes. The valid acceptance/non-propagation test now supplies its actual
durable independent Evaluation as well as the trusted policy input.

This is authorized by Issue #72 section 32 and implements the accepted M5C3/M8
current-history responsibility. It changes no domain state, edge, authority,
judgment derivation semantics or architecture. No other M9 production correction
was made. M7 source remains unchanged from the required baseline.

## Final candidate validation

Locked sync PASS. Constitutional suite: 31 passed. All five persistence suites
invoked directly: 85 passed. Full suite: 3261 passed. Ruff PASS; format PASS
(209 files); mypy PASS (122 source files); unstaged/staged whitespace checks PASS.
The two failing new stale/substituted-Evaluation probes were reproduced before
the bounded correction and now pass. The earlier mypy issues were confined to
new tests and corrected before final validation.

Disposable pytest basetemp and uv cache remained under repository-ignored
`.uv-cache/`; dependency and lock inputs were unchanged. All prior phase commits
had clean worktrees before the next phase. No domain source changed.

```text
M7 Human Accepted = YES
Human Accepted lifecycle coverage = 99 / 99
M8 candidate = complete
M8 Human Accepted = NO
M9 candidate = complete
M9 Human Accepted = NO
Stage 1 complete = NO
Stage 2 authorized = NO
Remote mutation = none
```

Independent Human Review remains required. No Human Stage 1 Exit Review or
Stage 1 reconciliation was performed. The fifth commit's exact hash and final
worktree state are recorded in the external execution handoff, avoiding a
self-referential commit hash in this document.

## Local commit evidence through the M9 parent

All four commits below passed Ruff, format, mypy and diff checks. Phase 0 changed
documentation only; its full-suite result is the verified unchanged baseline.
Each commit used explicit staging and complete staged-diff inspection.

### Phase 0

```text
e59c61c54a27f3a4751fc5102c44ca0aa5379895
8f73da617ac686254ea30fc33a6d8f81bdb406cb
docs(governance): record m7 lifecycle acceptance
```

Focused: docs-only review. Full suite: 3145 baseline. Worktree after commit: clean.

Changed files (A added, M modified, R renamed):

```text
M	docs/exec-plans/active/stage-01-completion-v1.md
M	docs/exec-plans/active/stage-01-m7-authoritative-creation-architecture-v1.md
R090	docs/exec-plans/active/stage-01-correction-m7d6a-evaluation-producer-authority-relabel-v1.md	docs/exec-plans/completed/stage-01-correction-m7d6a-evaluation-producer-authority-relabel-v1.md
R076	docs/exec-plans/active/stage-01-m7d3-run-outcome-evaluation-creation-semantics-v1.md	docs/exec-plans/completed/stage-01-m7d3-run-outcome-evaluation-creation-semantics-v1.md
R071	docs/exec-plans/active/stage-01-m7d4-planned-effect-creation-semantics-v1.md	docs/exec-plans/completed/stage-01-m7d4-planned-effect-creation-semantics-v1.md
R072	docs/exec-plans/active/stage-01-m7d5-observed-effect-creation-semantics-v1.md	docs/exec-plans/completed/stage-01-m7d5-observed-effect-creation-semantics-v1.md
R085	docs/exec-plans/active/stage-01-m7d6-integrated-creation-acceptance-v1.md	docs/exec-plans/completed/stage-01-m7d6-integrated-creation-acceptance-v1.md
```

### M8A

```text
8c14229e89470e3a125bd08051d1a985161f2f8d
e59c61c54a27f3a4751fc5102c44ca0aa5379895
feat(persistence): define stage one persistence contracts
```

Focused: 23 codec. Full suite: 3168. Worktree after commit: clean.

Changed files (A added, M modified, R renamed):

```text
A	docs/adr/0007-stage-1-sqlite-persistence-and-atomicity.md
A	docs/exec-plans/active/stage-01-m8-persistence-and-atomicity-v1.md
A	src/symphony_k/persistence/__init__.py
A	src/symphony_k/persistence/_codec_types.py
A	src/symphony_k/persistence/codec.py
A	src/symphony_k/persistence/ports.py
A	tests/test_persistence_codec.py
```

### M8B

```text
560009e34c18c4e75917319de4511c32d2a603e7
8c14229e89470e3a125bd08051d1a985161f2f8d
feat(persistence): add sqlite lifecycle repository
```

Focused: 12 SQLite. Full suite: 3180. Worktree after commit: clean.

Changed files (A added, M modified, R renamed):

```text
M	docs/exec-plans/active/stage-01-m8-persistence-and-atomicity-v1.md
A	src/symphony_k/persistence/sqlite.py
A	tests/test_persistence_sqlite.py
```

### M8C

```text
305c4170f82619b7948bed9130b875e2ffd5a9ce
560009e34c18c4e75917319de4511c32d2a603e7
feat(persistence): enforce atomic lifecycle operations
```

Focused: 85 persistence. Full suite: 3230. Worktree after commit: clean.

Changed files (A added, M modified, R renamed):

```text
M	ARCHITECTURE.md
M	docs/exec-plans/active/stage-01-m8-persistence-and-atomicity-v1.md
A	src/symphony_k/persistence/_records.py
A	src/symphony_k/persistence/_storage.py
A	src/symphony_k/persistence/evaluation.py
M	src/symphony_k/persistence/ports.py
A	src/symphony_k/persistence/service.py
M	src/symphony_k/persistence/sqlite.py
A	tests/persistence_fixtures.py
A	tests/test_persistence_effect.py
A	tests/test_persistence_evaluation.py
A	tests/test_persistence_service.py
```

### M9 final commit

Title: `test(constitution): enforce stage one constitutional invariants`
Parent: `305c4170f82619b7948bed9130b875e2ffd5a9ce`
Focused: 31 constitutional and 85 persistence. Full suite: 3261. All static
and diff gates passed.

Changed files:

- `ARCHITECTURE.md`
- `src/symphony_k/persistence/evaluation.py`
- `docs/exec-plans/active/stage-01-m9-constitutional-test-suite-v1.md`
- `tests/constitutional/__init__.py`
- `tests/constitutional/test_authority_and_separation.py`
- `tests/constitutional/test_durable_history.py`
- `tests/constitutional/test_architecture.py`

## Issue #73 M8D constitutional correction evidence

The constitutional suite now includes
`test_later_effect_transition_cannot_backfill_fabricated_history`. It constructs
the committed history through the real LifecycleService, attempts to introduce a
new confirmed observation only during rollback, and proves typed rejection plus
byte/logical row equality. Existing compensation/rollback history tests now also
construct their critical Effect history through production create/transition
paths rather than relying on a boundary-only Effect snapshot.

The constitutional suite passed 32 tests and the complete suite passed 3269.
Ruff, format, mypy and diff checks passed. At the corrected Issue #73 pre-review
boundary, M9 remained a candidate pending the next independent cumulative
Human Review.

## Final Human disposition

Issue #72's M9 candidate remained pending while the cumulative M8 blocker was
unresolved. After corrected Issue #73 closed the remaining persistence
historical-truth gap, independent cumulative Human Review accepted M9.

```text
M9 HUMAN ACCEPTED
```
