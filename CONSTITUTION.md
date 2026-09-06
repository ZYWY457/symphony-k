# Project Constitution

**Version:** 0.1

## 1. Purpose

This constitution defines the highest-level architectural, trust, safety, governance, state-ownership, and evolution rules for the outcome-oriented AI work orchestrator.

Its purpose is to prevent implementation convenience, agent behavior, local prompts, or future feature pressure from silently changing the system's foundational guarantees.

## 2. Normative Language

The terms `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` are normative.

- `MUST` / `MUST NOT`: constitutional or required architecture behavior.
- `SHOULD` / `SHOULD NOT`: default engineering rule; deviation requires documented reason.
- `MAY`: permitted but optional behavior.

## 3. Authority and Precedence

When instructions conflict, the following precedence applies:

1. `CONSTITUTION.md`
2. documents under `docs/core-beliefs/`
3. accepted ADRs under `docs/adr/`
4. `ARCHITECTURE.md`
5. approved design documents
6. active Exec Plans
7. Issues / task specifications
8. local prompts / worker instructions

A lower-level instruction MUST NOT override a higher-level rule.

If an implementation request conflicts with this hierarchy, the work MUST stop at the conflicting boundary and produce an explicit governance or architecture change request instead of silently violating the rule.

## 4. Constitutional Principles

### 4.1 Manage Work, Not Agents

The orchestrator manages Objectives, Tasks, Runs, Outcomes, Evaluations, Effects, evidence, policy, and execution profiles.

Agents, models, skills, tools, and sandboxes are replaceable execution resources.

### 4.2 Workers Are Untrusted

Worker intelligence, brand, provider, model strength, alignment claim, or prior success MUST NOT grant implicit trust.

Worker statements are claims, not facts.

### 4.3 Work Survives Workers

Authoritative work state MUST live outside worker processes and sandbox memory.

Worker failure, sandbox destruction, provider outage, or reassignment MUST NOT erase authoritative Task state, checkpoints, evidence, audit history, or cost history.

### 4.4 Execution Is Sandboxed

Worker Runs MUST execute inside an approved sandbox boundary.

Host execution is not the default trusted path.

### 4.5 Least Privilege

Permissions are granted according to Task requirements, risk, policy, and authorization—not according to worker identity.

Workers MUST NOT grant themselves additional permission, budget, or external authority.

### 4.6 Evidence Before Acceptance

A worker MUST NOT validate its own result as authoritative truth.

Verification is independent, evidence-based, dynamic, and proportional to value, risk, reversibility, confidence, and verifiability.

### 4.7 Separate Execution, Verification, Authorization, and Commitment

Where risk warrants separation, the same actor or component SHOULD NOT simultaneously control:

- execution,
- validation,
- authorization,
- external effect commitment.

An evaluator MUST NOT commit the Effect it evaluates.

### 4.8 Human Authority Has Boundaries

Authorized humans MAY override policy and judgment.

Humans MUST NOT use normal application flows to rewrite historical facts, erase evidence provenance, falsify a committed Effect, or bypass constitutional invariants.

### 4.9 Irreversible Effects Require Human Authorization

Under Constitution v0.1, an irreversible external Effect MUST receive explicit human authorization before real commit.

### 4.10 History Is Append-Only in Meaning

Audit records, historical Evaluations, committed Effect history, and evidence provenance MUST NOT be silently rewritten or physically deleted through normal operation.

Corrections and overrides are represented by new records referencing prior records.

### 4.11 Planning Does Not Equal Authority

A Planner produces `TaskProposal` objects.

A TaskProposal MUST pass governance before becoming executable work.

### 4.12 Recovery Is a First-Class System Capability

The system MUST distinguish recoverable interruption from invalid execution paths and unsuitable execution profiles.

Recovery semantics include Resume, Rewind, and Reassign and must rely on trusted checkpoints and persisted evidence.

### 4.13 External Effects Are First-Class Objects

Important external side effects MUST be represented, governed, authorized, committed, verified, and audited as Effects rather than hidden inside worker tool calls.

### 4.14 Learning Is Delayed and Governed

Raw audit history MUST NOT directly mutate production policy.

Learning must pass through delayed observation, verified experience, sufficient evidence, versioned policy candidates, and controlled rollout.

Trust reduction may occur rapidly after strong negative evidence. Trust recovery SHOULD require repeated verified evidence.

## 5. Core Domain Separation

The following concepts MUST remain semantically distinct:

- `Objective`: finite business or operational goal.
- `Task`: bounded unit of work with one primary Objective.
- `Run`: one concrete execution attempt.
- `Outcome`: candidate result of a Run.
- `Evaluation`: validation record concerning evidence, Run, Outcome, or Effect.
- `Effect`: external-world side effect or change.

No implementation may collapse these concepts merely for storage or API convenience if doing so destroys their authority or lifecycle distinctions.

## 6. Constitutional Invariants

At minimum:

1. A worker MUST NOT directly transition itself to authoritative completion or acceptance.
2. A worker MUST NOT accept its own Outcome.
3. A worker MUST NOT grant itself permission or budget.
4. An evaluator MUST NOT commit the Effect it validates.
5. Historical facts and audit provenance MUST NOT be silently rewritten.
6. A committed irreversible Effect MUST NOT later be represented as if it never occurred.
7. Compensation MUST NOT be mislabeled as true rollback when historical side effects remain real.
8. Human overrides MUST be explicit and audited.
9. Agent-specific runtime semantics MUST NOT become core orchestration semantics.
10. Planner output MUST remain a proposal until governed.
11. State transitions MUST go through authoritative transition logic and produce audit information.
12. Important external effects MUST use the governed Effect path.
13. Work state MUST remain recoverable independently of worker lifetime.

## 7. Amendment Process

A constitutional change requires:

1. an explicit ADR proposing the amendment,
2. motivation and threat/consistency analysis,
3. identification of affected invariants and state machines,
4. migration implications,
5. verification and rollback plan for implementation,
6. explicit human approval,
7. constitution version increment.

A normal Issue, Exec Plan, pull request, agent request, or prompt MUST NOT amend the constitution implicitly.

## 8. Implementation Freedom

The constitution intentionally does not freeze replaceable implementation choices such as:

- Python versus another control-plane language,
- Docker versus future sandbox providers,
- SQLite versus PostgreSQL,
- a specific queue,
- a specific agent,
- a specific model,
- a specific UI,
- a specific semantic judge.

Those choices may evolve through ADRs as long as constitutional behavior remains intact.
