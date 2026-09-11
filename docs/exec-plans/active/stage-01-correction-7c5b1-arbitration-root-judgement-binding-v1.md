# Stage 1 Correction 7C5B1 — Arbitration Root-Judgement Binding

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #47 only

## Purpose

This correction closes the Human Code Review findings from Issue #46 without
redesigning the accepted M7C5B conflict/arbitration architecture.

## Bounded steps

1. Strengthen the existing pure Evaluation-specific effective-use lineage
   derivation so a root arbitration for an Evaluation with an original
   `EvaluationResult` has a `prior_effective_judgement` exactly equal to that
   immutable original verdict.
2. Retain the existing root `MODIFIED`-with-`None` structural path when the
   conflicted Evaluation has no original result.
3. Add M7 transition-boundary regressions for direct and conflict-linked root
   arbitration, including omitted/substituted prior rejection, original-result
   immutability, and the no-original-result path.
4. Run the complete Issue #47 validation gates, stage only correction files,
   inspect the staged diff, and create one local corrective commit. No remote
   mutation is in scope.

## Acceptance evidence

- Existing original judgements cannot be omitted or substituted at the first
  Evaluation-specific arbitration decision.
- The no-original-result `CONFLICTED -> ARBITRATED` path remains valid only
  through existing structural semantics.
- The correction uses the canonical shared effective-use lineage rather than a
  duplicate Transition Engine rule; Evaluation's ten-edge topology is unchanged.
