# Roadmap

This roadmap defines implementation order, not permanent architecture. Each stage must preserve the constitutional rules in `ARCHITECTURE.md` and `docs/core-beliefs/`.

## Stage 0 — Constitution and Repository Harness

Deliver:

- `AGENTS.md`
- `VISION.md`
- `ARCHITECTURE.md`
- `ROADMAP.md`
- core-belief documents
- ADR process
- Exec Plan process
- initial repository structure

Exit criteria:

- top-level domain boundaries are frozen for v0,
- constitutional invariants are documented,
- Codex can navigate the repository without requiring the project history to be restated in every prompt.

## Stage 1 — Domain Kernel

Implement:

- Objective,
- Task,
- Run,
- Outcome,
- Evaluation,
- Effect,
- state transition engine,
- persistence abstraction,
- audit event model,
- concurrency/version semantics.

The Stage 1 core domain objects are limited to Objective, Task, Run, Outcome, Evaluation and Effect. TaskProposal representation, lifecycle, generation and governance implementation belong to Stage 9, not Stage 1.

Exit criteria:

- domain objects can be created and transitioned only through valid paths,
- illegal transitions are rejected,
- audit history is generated for all authoritative transitions,
- worker identity has no direct state mutation path.

## Stage 2 — Sandbox Execution

Implement:

- SandboxProvider abstraction,
- DockerSandbox provider,
- workspace abstraction,
- resource limits,
- timeouts,
- network policy abstraction,
- artifact collection,
- teardown and cleanup,
- sandbox execution telemetry.

Exit criteria:

- arbitrary bounded commands can run in temporary Docker sandboxes,
- host environment is not used as the worker runtime,
- privileged mode and Docker socket exposure are prohibited by default,
- resource and network restrictions are testable.

## Stage 3 — First AgentDriver

Implement:

- AgentDriver interface,
- capability model,
- structured AgentRequest types,
- Codex adapter as the first implementation,
- session/run event ingestion,
- usage reporting,
- cancellation and resumability where supported.

Exit criteria:

- a Task can be executed by Codex through the driver boundary without Codex-specific concepts entering core domain models.

## Stage 4 — Verification Plane

Implement:

- ValidationPlanner,
- evidence collection,
- precondition checks,
- static validators,
- intermediate assertions,
- dynamic validators,
- semantic validator interface,
- confidence gate,
- evaluation conflict handling.

Exit criteria:

- system completion decisions do not rely on worker self-report,
- evidence-backed Evaluation reports are persisted,
- validation intensity can vary by Task profile.

## Stage 5 — Failure and Recovery

Implement:

- CheckpointManifest,
- trusted/incomplete checkpoint states,
- FailureClassifier,
- RecoveryController,
- Resume,
- Rewind,
- Reassign,
- HandoffPackage,
- loop/progress-stall detection,
- recovery budgets and limits.

Exit criteria:

- worker or sandbox loss does not erase Task progress,
- temporary failure can resume,
- invalid execution paths can rewind,
- unsuitable execution profiles can reassign.

## Stage 6 — Budget, Risk, Permission, and Effects

Implement:

- BudgetProfile and ledger,
- RiskProfile,
- ValueProfile,
- ConfidenceProfile,
- Verifiability profile,
- PermissionEnvelope,
- EffectIntent,
- Effect Controller,
- Prepare–Verify–Authorize–Commit flow,
- idempotency,
- rollback records,
- Saga-style compensation records,
- human approval gates.

Exit criteria:

- budget exhaustion and permission boundaries are enforced,
- important external side effects cannot bypass the Effect Controller,
- irreversible effects require configured human authorization,
- committed effects produce verifiable receipts.

## Stage 7 — Second Agent and Architecture Test

Integrate a materially different second agent runtime.

Candidate: Hermes or another multi-model agent.

Exit criteria:

- integration requires a new driver/configuration/sandbox image but no core orchestration redesign,
- routing can select between at least two agent runtimes.

Failure of this stage means the Agent abstraction is not sufficiently decoupled.

## Stage 8 — Router and Escalation

Implement:

- capability registry,
- rule-based routing,
- execution profile selection,
- cost-aware routing,
- reliability-aware routing,
- escalation and degradation strategies,
- history-backed routing inputs.

Exit criteria:

- system can choose an execution profile based on explicit constraints rather than a hard-coded agent.

## Stage 9 — Planner

Implement:

- TaskProposal representation and lifecycle as non-executable planning input,
- Objective-to-TaskProposal planning,
- bounded DAG generation,
- planning depth limits,
- planning budget,
- dependency modeling,
- proposal governance.

Exit criteria:

- Planner cannot directly launch arbitrary work,
- generated proposals pass through governance before becoming Tasks.

A TaskProposal is never directly executable; governance creates separate executable Task work.

## Stage 10 — Learning and Reputation

Implement:

- immutable audit source,
- delayed observation pipeline,
- verified experience pool,
- domain-specific reliability profiles,
- validator reliability,
- policy candidates,
- shadow mode,
- canary rollout,
- rollback of policy versions.

Exit criteria:

- raw events cannot directly mutate production policy,
- negative trust evidence propagates faster than trust recovery,
- policy changes are versioned and reversible.

## Later Stages

Potential future work:

- distributed workers,
- remote sandbox providers,
- GPU/local-model resource pools,
- microVM isolation,
- advanced schedulers,
- richer human governance UI,
- organization-level tenancy,
- external tracker adapters,
- self-hosted policy analytics,
- learned routing after sufficient reliable data exists.
