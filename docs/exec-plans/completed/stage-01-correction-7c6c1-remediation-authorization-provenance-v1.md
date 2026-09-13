# Stage 1 Correction 7C6C1 — Remediation Authorization Provenance Binding

**Version:** 1
**Status:** Validated local candidate
**Scope:** GitHub Issue #55 only

## Execution evidence

TaskSpec reference: GitHub Issue #55
TaskSpec access mode: materialized-handoff
TaskSpec precondition: PASS

The required baseline `2b339ed458c66305c2f222e0dd78149b98a461a3` was
the starting `HEAD`, with subject
`feat(domain): canonicalize effect remediation semantics`. The worktree was
clean, and the repository command runner, Git, repository-root resolution,
Python, and UV preflight checks passed before this plan or any other repository
mutation.

## Objective

Close the bounded authorization defects in the Issue #54 remediation semantic
guards without changing their accepted rollback, compensation-plan, linked
Effect, or compensation-start-event lineage behavior.

## Architecture constraints

- A `PlannedEffectOrigin` producing principal cannot authorize its own remedy
  by changing `ActorType`; principal identity is the security boundary.
- Remediation policy and human authorization are immutable provenance inputs,
  distinct from M7 lifecycle authority and from normal commit authorization.
- Policy authorization identifies the exact policy and version. Both policy
  and human records preserve the recording principal and decision/recording
  timestamps.
- This correction does not change the accepted nineteen-edge Effect topology
  and requires no ADR or new top-level domain concept.

## In scope

1. Add an immutable remediation-policy identity/version reference and complete
   policy/human authorization record provenance.
2. Exact-bind human authorization to the policy reference as well as the
   existing decision reference and remediation scope.
3. Reject a planned Effect producer relabeled as either the policy or human
   remediation authorizer on rollback and compensation paths.
4. Add deterministic construction, exact-binding, relabeling, and preservation
   regressions while retaining the exact compensation-start-event lineage and
   plan-substitution protections from Issue #54.

## Out of scope

- quarantine remediation or re-entry;
- creation paths, M8, Stage 2, persistence, or external execution;
- policy-engine implementation;
- permission, risk, or budget runtime behavior;
- Effect topology changes or updates to
  `docs/exec-plans/active/stage-01-completion-v1.md`.

## Milestones

1. Extend the immutable remediation authorization value types and exports.
2. Tighten the canonical remediation guard at the existing authorization
   boundary.
3. Add focused regressions and run the complete repository validation gates.
4. Explicitly stage only Issue #55 files, inspect the full staged diff, and
   create exactly one local commit without remote mutation.

## Risks and controls

- **ActorType relabeling could bypass separation:** compare stable `ActorId`
  values against the immutable planned producer for both authorizer roles.
- **Authorization substitution could lose exact policy provenance:** use a
  dedicated frozen policy identity/version reference and require exact equality
  across policy and human records.
- **Correction could regress Issue #54 lineage:** retain and rerun the existing
  compensation start-event and plan/link substitution tests unchanged.

## Acceptance criteria

- Policy and human remediation authorization records reject incomplete or
  incorrectly typed policy/version, actor, and timestamp provenance.
- A planned Effect producer cannot authorize its own rollback or compensation
  by relabeling itself as `POLICY_ENGINE` or `HUMAN_OPERATOR`.
- A human authorization with a substituted policy identity/version is rejected.
- Existing exact restoration, plan, linked Effect, original observation, and
  compensation-start-event bindings remain enforced.
- All repository tests, lint, format, type checking, and diff-integrity gates
  pass.

## Required completion evidence

- `uv sync --dev --locked`
- `uv run pytest -p no:cacheprovider`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy src tests`
- `git diff --check`
- explicit staged name/status and full staged diff review
- one local commit with no remote mutation

## Decisions

This is a corrective implementation of the accepted Effect authority and
provenance model in `CONSTITUTION.md`, the core beliefs, and ADR-0005. It adds no
architectural concept and therefore requires no ADR.

## Validation evidence

The repository-local ignored `.uv-cache` held only disposable UV cache data;
dependency and lock inputs were unchanged. All Issue #55 gates passed on the
final candidate:

- `uv sync --dev --locked` — PASS, 13 packages checked
- `uv run pytest -p no:cacheprovider` — PASS, 2550 tests
- `uv run ruff check .` — PASS
- `uv run ruff format --check .` — PASS, 157 files already formatted
- `uv run mypy src tests` — PASS, 89 source files
- `git diff --check` — PASS

The focused remediation suite passed 53 tests, including six producer/authorizer
relabeling cases across rollback, compensation start, and compensation
completion. Existing exact compensation-start-event lineage and plan/linked
Effect substitution regressions remain unchanged and passing.
