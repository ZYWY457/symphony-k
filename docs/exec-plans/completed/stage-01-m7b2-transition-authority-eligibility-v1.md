# Stage 1 M7B2 — Canonical Transition Authority Eligibility Matrix

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #23 only

## Boundary

M7B2 encodes the accepted actor-type eligibility matrix for the six core entity
lifecycle families and composes it with the M7B1 exact-bound authority decision.
Eligibility is an additional denial boundary, never a scoped grant. M7C–M7E
semantic guards, persistence, permission policy, external execution, and lifecycle
topology changes remain out of scope.

## Bounded steps

1. Add one domain-pure canonical eligibility representation, including the
   edge-specific Evaluation rows and creation eligibility without inventing a
   `NONE` lifecycle state.
2. Require the centralized transition engine to reject an ineligible actor after
   the exact-compatible `AUTHORIZED` M7B1 decision check and before semantic
   guards.
3. Add deterministic matrix-wide tests for all accepted legal edges, focused
   transition-engine composition tests, and strict static typing examples.
4. Prove that WORKER and SYSTEM have no direct lifecycle authority, that
   HUMAN_OPERATOR is scoped rather than universal, and that the canonical
   topology remains unchanged.
5. Run every Issue #23 validation gate, explicitly stage only M7B2 files, review
   the complete staged diff, and create exactly one local commit.

## Acceptance

Objective and Task eligibility is exactly REQUESTER, SCHEDULER, POLICY_ENGINE, and
HUMAN_OPERATOR. Run eligibility is exactly SCHEDULER and RUN_CONTROLLER. Outcome
eligibility is exactly SCHEDULER and POLICY_ENGINE. Evaluation eligibility follows
the accepted per-edge V/A rows, including SCHEDULER or EVALUATOR for creation.
Effect eligibility is exactly EFFECT_CONTROLLER. Every successful executable
transition still requires an exact-bound AUTHORIZED M7B1 decision and passing
semantic guards. No lifecycle edge, runtime dependency, grant system, repository,
or M7C+ behavior is introduced.
