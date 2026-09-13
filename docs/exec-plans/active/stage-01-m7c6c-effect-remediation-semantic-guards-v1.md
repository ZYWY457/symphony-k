# Stage 1 M7C6C — Canonical Effect Remediation Semantic Guards

**Version:** 1
**Status:** Validated local candidate
**Scope:** GitHub Issue #54 only

## Execution evidence

TaskSpec reference: GitHub Issue #54
TaskSpec access mode: materialized-handoff
TaskSpec precondition: PASS

The required baseline `5fca1fac717d29c41fa900ea1bff080b6b88edc5` is
the starting `HEAD`. The worktree was clean and the repository command runner,
Git, Python, and UV preflight checks passed before this plan or any other
repository mutation.

## Boundary

Canonicalize exactly these existing Effect non-creation edges:

- `COMMITTED -> ROLLED_BACK`
- `COMMITTED -> COMPENSATING`
- `COMPENSATING -> COMPENSATED`

This is pure Stage 1 domain semantics. It preserves the accepted nineteen-edge
Effect topology, the original COMMITTED occurrence, the distinction between
rollback and compensation, M7B1 exact lifecycle authority, M7B2
`EFFECT_CONTROLLER` eligibility, and the four deferred quarantine
remediation/re-entry denials. It adds no persistence, external execution,
rollback, compensation, Saga runtime, policy engine, or Stage 2 behavior.

## Bounded steps

1. Add the minimum immutable typed remediation-authorization decision needed to
   exact-bind either the actual restoration operation or the exact compensation
   plan. Keep this authorization distinct from normal commit authorization and
   M7 lifecycle authority, and retain explicit human authorization when the
   decision says constitutional or policy rules require it.
2. Extend `EffectSemanticGuard` with exact-bound rollback,
   compensation-start, and compensation-completion inputs. Reuse the accepted
   M6C rollback, plan, completion, and compatibility types; require compatible
   historical original-commit observation provenance and principal-identity
   separation for independent verification.
3. Bind `COMMITTED -> COMPENSATING` to the exact plan, linked compensating
   Effect identities, original commit, and remediation authorization through
   narrow immutable lifecycle-event annotations. Require
   `COMPENSATING -> COMPENSATED` to consume the actual compensation-start event
   and reject plan, linked-identity, or start-lineage substitution.
4. Compose the three edges after M7B1/M7B2 and before generic guards. Successful
   Effect projection changes only state and version and emits exactly one
   existing appropriate lifecycle event; no external action is invoked.
5. Add deterministic transition-boundary regressions for exact provenance,
   authorization, human requirements, principal separation, event lineage,
   state projection, topology, strict sinks, M7 composition, the four retained
   semantic denials, and the full cross-domain suite.
6. Run all Issue #54 validation gates, inspect the complete diff, explicitly
   stage only Issue files, inspect the staged name/status and full staged diff,
   and create exactly one local commit without remote mutation.

## Acceptance

Canonical Effect semantic coverage becomes a candidate fifteen of nineteen
non-creation edges. Rollback requires independently verified restoration and
authorization for its exact restoration operation. Compensation start requires
authorization for the exact plan and records stable plan/start lineage;
completion requires independent completion evidence for that same lineage and
preserves residual impact. `COMMITTED -> COMPENSATED` remains structurally
forbidden, `ROLLED_BACK` and `COMPENSATED` remain strict sinks, and the four
quarantine remediation/re-entry edges remain semantic deny-by-default.

Only independent Human Review may accept this candidate or update the Stage 1
completion map. This Worker Run does not claim M7 or Stage 1 complete.

## Validation evidence

The default UV cache was sandbox-denied, so validation used only the
repository-approved ignored `.uv-cache` fallback. All Issue #54 gates passed:

- `uv sync --dev --locked` — PASS
- `uv run pytest -p no:cacheprovider` — PASS, 2538 tests
- `uv run ruff check .` — PASS
- `uv run ruff format --check .` — PASS, 156 files already formatted
- `uv run mypy src tests` — PASS, 89 source files
- `git diff --check` — PASS
