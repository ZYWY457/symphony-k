# Stage 1 M7C2 — Canonical Task Semantic Transition Guards

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #25 only

## Boundary

M7C2 adds the canonical Task-only semantic gate to the existing M7A/M7B1/M7B2
pure transition boundary. It consumes immutable, typed, exact-snapshot-bound
decisions and evidence references. It does not evaluate policy, load state,
persist records, propagate child lifecycle state, or implement any other entity
semantic guard.

## Bounded steps

1. Define the minimum Task-specific semantic decisions for readiness, blocking,
   start/resume ownership, completion, failure, and cancellation.
2. Bind every decision to TaskId, observed Task EntityVersion, and CorrelationId;
   primary-Objective observations additionally identify the exact primary
   ObjectiveId.
3. Require a canonical Task semantic guard for each of the existing sixteen Task
   edges, before ordinary additional guards and independently of M7B1/M7B2.
4. Test all accepted Task edges; stale, cross-Task, and cross-correlation reuse;
   ownership ambiguity; exact Objective and completion-policy checks; immutable
   rejection; and no lifecycle propagation.
5. Run scoped and full deterministic validation, stage only M7C2 files, inspect
   the staged diff, and create exactly one local commit.

## Acceptance evidence

- Readiness, starts, and resumes consume explicit ownership observations; an
  unresolved/missing observation is never treated as no active ownership.
- Readiness/start/resume require evidence that exactly the Task's primary
  Objective is ACTIVE.
- Completion independently requires current CompletionPolicyRef, independent
  evidence, acceptance/effect/risk checks, and resolved or current-policy-waived
  blockers; Run closure, Outcome acceptance, percentages, and child counts are
  not semantic inputs.
- Missing or incompatible canonical Task semantics reject without a new Task,
  version, TransitionResult, or DomainEvent.
- No repositories, persistence, scheduler/runtime behavior, policy evaluation,
  child propagation, ADR-0006 runtime behavior, or M7C3+ guards are added.
