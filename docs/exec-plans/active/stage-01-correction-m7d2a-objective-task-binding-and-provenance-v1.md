# Stage 1 Correction M7D2A — Objective/Task Binding and Provenance

**Version:** 1
**Status:** Active correction candidate; independent Human Review required
**TaskSpec:** [GitHub Issue #69](https://github.com/ZYWY457/symphony-k/issues/69)
**TaskSpec access mode:** `materialized-handoff`
**Starting baseline:** `ff3a37e667fb54db1ed16ef065d5b4edde8eebbe`
(`feat(domain): implement objective task creation semantics`)

## Review finding and scope

Independent Human Review of Issue #68 found two bounded M7D2 blockers:

1. the Objective acceptance-definition decision omitted the exact Objective
   goal and could therefore be replayed across different definitions; and
2. the Task Objective observation omitted typed observation time provenance.

This correction adds exact goal retention and binding to the acceptance
decision, adds an immutable `Timestamp` observation field, and completes the
direct Objective/Task regression matrix frozen by Issue #68. It does not
redesign M7D1/M7D2 or implement M7D3, M8, persistence, transactional currentness,
or repository-backed currentness.

## Implementation and validation plan

1. Extend the two supporting records with structural validation and update the
   Objective semantic validator to require all six exact bindings.
2. Preserve CURRENT/STALE snapshots, prohibit fabricated MISSING/UNRESOLVED
   snapshots, and retain same-ActorId requester relabel defenses without a
   domain wall-clock read.
3. Add isolated tests for every Objective decision/status/binding attack, every
   Task observation status/topology/scope attack, eligible creation authorities,
   exact snapshots/events/annotations, deterministic ordering/deduplication,
   and guard failure.
4. Re-run the M7D1 protocol suite, the focused M7D2 suite, the full suite, Ruff,
   formatting, mypy, and Git diff/staging checks.

## Bounded closure audit

The correction audit covers Objective four-way classification and exact
decision scope; Task semantic decisions and observation contracts; ActorId
relabel defenses; validation order; version-1 snapshot/event exact binding;
canonical reference-only annotations; the other six fail-closed variants; M7D1
regression isolation; and the M7/M8 boundary. Any finding requiring new
architecture, Issue #62 reinterpretation, M7D3–M7D5, persistence/M8, or accepted
non-creation semantic changes stops this correction instead of broadening it.

The completed audit found no additional production defect inside the frozen
Issue #68 contract. Objective exact binding now includes the goal; Task
observations retain typed observation time while preserving all four status
shapes and same-principal relabel defenses. Validation order, version-1
construction, exact event binding, canonical reference-only annotations, the
six fail-closed creation variants, and the M7/M8 boundary remain unchanged.

## Validation evidence

```text
uv sync --dev --locked                                      PASS
tests/test_creation_protocol.py                            122 passed
tests/test_creation_objective_task.py                       74 passed
full suite                                                2792 passed
ruff check .                                                PASS
ruff format --check .                                       PASS
mypy src tests                                              PASS
git diff --check                                            PASS
```

## Acceptance boundary

The production and test changes are an M7D2A candidate only. M7D1 and all 91
accepted non-creation edges remain unchanged. Implementation and local
validation do not constitute Human acceptance.

```text
Human Accepted creation edges = 0 / 8
Human Accepted integrated coverage = 91 / 99
M7 complete = NO
Stage 1 complete = NO
```
