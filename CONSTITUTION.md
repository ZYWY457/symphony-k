# Project Constitution

**Version:** 0.2

**Amendment status:** Candidate pending independent review and explicit Human
acceptance of the exact amendment.

## 1. Purpose

This constitution defines the highest-level architectural, trust, safety,
governance, state-ownership, and evolution rules for Symphony-K as a
framework-neutral governance/control-plane system around agentic work.

Symphony-K governs trustworthy authority, evidence, consequential Effects and
reconstructable audit history. External planners, orchestrators, Agent runtimes
and execution providers may determine how work is attempted, but they do not
become authoritative merely by producing claims or performing execution.

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

Symphony-K governs authoritative Objectives, Tasks, Runs, Outcomes,
Evaluations, Effects, evidence, policy and Human decisions. It governs what
becomes authoritative work and how consequential Effects cross the trusted
boundary; it does not govern Agent cognition.

External planners, orchestrators and runtimes MAY determine how work is
attempted. Their claims MUST NOT become authoritative merely because they
produced them, and they MUST NOT bypass governed Effect authorization or
commitment. Agents, models, skills, tools, orchestrators and execution providers
remain replaceable resources or integrations.

### 4.2 Workers Are Untrusted

Worker intelligence, brand, provider, model strength, alignment claim, or prior success MUST NOT grant implicit trust.

Worker statements are claims, not facts.

### 4.3 Work Survives Workers

Authoritative work state MUST live outside worker processes and sandbox memory.

Worker failure, sandbox destruction, provider outage, or reassignment MUST NOT erase authoritative Task state, checkpoints, evidence, audit history, or cost history.

### 4.4 Execution Is Isolated

Untrusted Worker execution MUST occur inside an approved execution-isolation
boundary appropriate to the integration.

The boundary MAY be supplied by an external provider or a Symphony-K reference
provider. External execution does not make direct host execution trusted by
default.

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

An irreversible external Effect MUST receive explicit Human authorization before real commit unless a future explicit constitutional amendment changes this rule.

### 4.10 History Is Append-Only in Meaning

Audit records, historical Evaluations, committed Effect history, and evidence provenance MUST NOT be silently rewritten or physically deleted through normal operation.

Corrections and overrides are represented by new records referencing prior records.

### 4.11 Planning Does Not Equal Authority

Symphony-K v1 does not require a Symphony-K-owned Planner.

When Symphony-K supplies planning, Planner output remains a non-executable
`TaskProposal` and MUST pass governance before becoming a separate executable
Task. External planning output likewise MUST NOT grant itself execution,
permission, budget or lifecycle authority.

### 4.12 Governance Recovery Is a First-Class Capability

External workflow or orchestrator systems MAY own mechanical execution
recovery, including retries, workflow continuation, scheduling and provider
failover.

Symphony-K MUST govern recovery wherever authoritative attempt lineage,
evidence or checkpoint trust, Effect occurrence uncertainty, reconciliation,
compensation, Human resolution or preservation of historical facts is involved.
Recovery MUST NOT silently change attempt identity, trust an unverified
checkpoint, or blindly replay a possibly occurring Effect.

### 4.13 External Effects Are First-Class Objects

Important external side effects MUST be represented, governed, authorized, committed, verified, and audited as Effects rather than hidden inside worker tool calls.

### 4.14 Learning Is Optional, Delayed, and Governed

Raw audit history MUST NOT directly mutate production policy.

Learning and reputation are optional for v1. If present, they MUST pass through
delayed observation, verified experience, sufficient evidence, attributable
and versioned policy candidates, and controlled rollout.

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
9. Agent-, orchestrator-, provider- or runtime-specific semantics MUST NOT
   become core governance semantics.
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

## 9. Constitution v0.2 Amendment Record

Constitution v0.2 is the amendment candidate associated with
[ADR-0009](docs/adr/0009-framework-neutral-agent-governance-kernel.md).

The durable authority and evidence chain is:

- [Human strategic approval on Issue #87, comment `5710053258`](https://github.com/ZYWY457/symphony-k/issues/87#issuecomment-5710053258);
- strategic falsification and correction evidence in Issues #85 and #86; and
- [independent ACCEPT of the corrected evidence on Issue #86, comment
  `5709520565`](https://github.com/ZYWY457/symphony-k/issues/86#issuecomment-5709520565).

This amendment changes Symphony-K's product responsibility and ownership
boundary. It does not weaken the accepted trust model, reopen the six core
entities or accepted lifecycle semantics, or make execution-system claims
authoritative. In particular, Workers still cannot self-complete authoritative
work, accept their own Outcomes, grant themselves authority, or bypass governed
Effects; Evaluators still cannot commit the Effects they validate; and
historical occurrence and evidence provenance remain append-only in meaning.

The amendment is implemented first as a reviewable candidate. If independent
review or later reconciliation identifies an inconsistency, work MUST stop and
the correction or reversal MUST be made through an explicit forward ADR and
constitutional amendment. Historical governance, evidence and occurrence facts
MUST NOT be silently reverted or rewritten.
