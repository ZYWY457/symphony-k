# Stage 1 M7D3 — Run, Outcome and Evaluation Creation

**Version:** 1
**Status:** Candidate; independent Human Review required
**TaskSpec:** https://github.com/ZYWY457/symphony-k/issues/70
**TaskSpec access mode:** materialized-handoff
**TaskSpec precondition:** PASS
**Parent:** `7c0704a98f05ec9a99ace763cf74e9efe30998dc`

## Scope and sequence

Implement only Run PENDING, Outcome PROPOSED and Evaluation PENDING creation.
Use immutable creation-specific observations and exact request-bound semantic
decisions. Validate shared authority/availability, then semantics, pure guards,
version-1 snapshot, canonical event and result, in that order.

1. Add typed relationship observations, registration/proposal/validation scopes
   and evidence-backed decisions in a bounded creation module.
2. Validate Run Task READY/IN_PROGRESS and primary Objective ACTIVE, profile and
   attempt selection, and complete direct predecessor lineage. Reassignment
   successor creation precedes old-Run closure; it cannot require the old Run
   already be REASSIGNED.
3. Bind Outcome producer, originating Run/Task, complete artifact/evidence scope
   and direct prior-candidate lineage with a common acceptance scope.
4. Bind Evaluation exact versioned target or unversioned anchored Evidence,
   method, policy, scope and independent verifier or assignment requirement.
5. Add success, isolated substitution, status, lineage, identity, guard and exact
   annotation tests. Run focused and full tests, Ruff, format, mypy and diff checks.

## Boundaries

No Effect creation, execution, persistence, transactional currentness, new
lifecycle states or changes to accepted non-creation semantics. Supplied
observations are M7 evidence inputs, not M8 currentness guarantees.

Human Accepted remains creation `2 / 8`, integrated `93 / 99`.
M7 and Stage 1 remain incomplete. This plan stays active pending Human Review.

## Execution preflight

Starting HEAD matched `1b1f36d49e5f92678158c68965c4b35803f7544a` with clean
worktree. Git, Python 3.12.7 and uv 0.11.2 were callable. Baseline: 2792 tests
passed. Default uv cache access was denied; repository-ignored `.uv-cache` was
used for disposable cache data without changing dependency inputs.

## Candidate validation evidence

Focused M7D3 suite: 75 passed. Full suite: 2867 passed. Ruff check, format
check, mypy (`97` source files), and diff checks passed. The existing 196
Objective/Task and shared-protocol tests also pass within the full suite.
No accepted non-creation module changed. No external execution was introduced.
