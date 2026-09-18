# Architecture

## 1. Architectural Principle

Symphony-K is a **framework-neutral governance/control plane for agentic work**.

It governs authoritative work state, evidence, decisions, consequential Effects and reconstructable history. External agents, orchestrators, workflow engines and execution providers may determine how work is attempted, but they do not become authoritative merely because they executed work or produced a claim.

The accepted Stage 1 Domain Kernel remains the semantic core. Planning, routing, Agent runtime and sandbox ownership are replaceable integration concerns rather than mandatory v1 product identity.

### Internal rigor, external simplicity

Internal complexity may grow as needed to preserve correctness; external
integration complexity should trend downward. Exact identity/version,
immutable fingerprints, trusted provenance, conflict history, replay,
concurrency, authorization/occurrence separation, reconciliation and causal
audit remain strict inside the boundary. Common callers should use small
supported operations, stable typed references and caller-safe errors rather
than understand the full domain graph, persistence schema or supporting-record
model.

External simplicity MUST NOT weaken governance invariants. Complexity is hidden
behind SDK, service and adapter boundaries; trust and exactness are not removed.

### Own the semantics; reuse the mechanisms

Symphony-K owns the semantic guarantees that define the product: claim is not
fact, capability is not authority, Evaluation is not disposition,
authorization is not occurrence, execution failure is not non-occurrence,
uncertainty is not failure, compensation is not erasure, evidence exact-binds
identity/version, and history remains causally reconstructable.

It should normally reuse mature infrastructure mechanisms:

```text
IAM / database / object storage / queue / RPC or HTTP framework /
workflow or Agent runtime / sandbox / secrets / observability
                              |
                              v
                    thin adapters/providers
                              |
                              v
               Symphony-K governance semantics
```

An adapter translates mechanism identity, evidence, observations and receipts
into stable Symphony-K inputs. It MUST NOT redefine authoritative disposition,
promote caller/provider claims to trusted fact, declare Effect occurrence
without admissible evidence or rewrite historical meaning.

## 2. Primary Architectural Boundaries

### Governance Kernel

Owns or governs:

- authoritative Objective, Task, Run, Outcome, Evaluation and Effect state;
- lifecycle authority and controlled state transitions;
- exact entity/candidate/version/authority binding;
- evidence/effective-use semantics;
- stale, superseded and cross-entity protection;
- optimistic concurrency, idempotency and exact replay;
- append-only historical meaning;
- explicit Human governance decisions; and
- durable provenance needed for audit reconstruction.

The kernel is provider-, model-, Agent-, orchestrator- and runtime-neutral.

### Integration SDK / Facade

Provides a bounded public surface for external callers so they do not need to understand the complete internal semantic type graph.

Conceptually it must support operations equivalent to:

- record/submit candidate work claims;
- record trusted independent Evaluation/evidence;
- request authoritative disposition;
- request governed Effects;
- record/perform required Human authorization through trusted authority paths;
- reconcile Effect occurrence; and
- export causal audit information.

Exact API shape remains a later bounded design.

The listed operations are a conceptual target surface, not a claim that v1 or
all later milestones are implemented. Current accepted capability is tracked
in `STATUS.md`.

### Verification and Evidence Boundary

Independent verification remains separate from Worker execution.

This boundary is responsible for:

- attributable evidence ingestion;
- Evaluation persistence;
- exact binding to the candidate/entity/version under judgment;
- effective-use checks;
- conflict, invalidation and arbitration history;
- stale/superseded evidence rejection; and
- preventing substituted evidence from becoming authority.

An evaluator does not receive Effect-commit authority merely because it validates an Outcome or Effect.

### Governed Effect Gateway

Consequential external actions cross a trusted gateway rather than being hidden inside Worker tool calls.

The gateway must preserve distinct facts for:

- Effect request/preparation;
- required verification;
- authorization;
- dispatch/commit attempt;
- external receipt;
- occurrence confirmation;
- uncertain occurrence;
- quarantine/reconciliation; and
- remediation, compensation or safe retry decisions.

Authorization and occurrence are separate truths. A confirmed Effect remains historically real even if authorization was absent, invalid or later judged unsafe.

Irreversible external Effects require explicit Human authorization under Constitution v0.2 unless a future explicit constitutional amendment changes that rule.

### Audit and Conformance Surface

The system must expose enough durable information for a fresh reviewer to reconstruct why an authoritative decision or consequential action occurred without direct database or private-source inspection.

Conformance evidence should exercise:

- authority isolation;
- exact evidence binding;
- stale/superseded evidence behavior;
- cross-entity substitution resistance;
- replay/idempotency;
- optimistic concurrency;
- append-only history; and
- Effect authorization/occurrence/reconciliation guarantees.

## 3. External Execution Boundary

External systems MAY own:

- task decomposition and planning;
- routing and scheduling;
- Agent runtime loops and tool use;
- workflow continuation and retries;
- sandbox/runtime implementation; and
- provider failover.

They MUST NOT:

- promote their own claims directly into authoritative truth;
- self-accept Outcomes or authoritative completion;
- grant themselves permission, budget or Effect authority;
- substitute evidence or authority across entities/versions;
- bypass governed Effects; or
- rewrite authoritative historical facts.

External execution does not imply trust. Untrusted Worker execution must still occur inside an approved execution-isolation boundary appropriate to the integration.

## 4. Embedded-First, Service-Capable Posture

The same governance semantics must be usable through:

- an embedded SDK/facade;
- a stable local service/API for cross-process or non-Python consumers; and
- a CLI/operator surface.

These surfaces must share one semantic authority model rather than implement parallel weaker rules.

This architecture does not select HTTP, gRPC, a web framework, a CLI library, an authentication mechanism, a queue or a deployment vendor. Service-mode identity, authentication, authorization and process-trust boundaries require later bounded design.

Authentication infrastructure may establish a principal, but Symphony-K still
decides what that identity is authorized to do in governance semantics.
Persistence engines store authoritative records but do not decide claim versus
fact or current trust eligibility. Workflow/Agent runtimes execute attempts but
cannot accept Outcomes. Provider API success is evidence input, not automatic
proof of Effect occurrence.

## 5. Core Domain Objects

### Objective

A finite, bounded, verifiable business or operational goal with an explicit acceptance boundary.

### Task

A bounded unit of work with exactly one `primary_objective` for ownership, budget attribution and lifecycle authority. Non-authoritative contribution links may exist but must not propagate authoritative state automatically.

### Run

One concrete execution attempt for a Task. A Task may have multiple Runs, including Runs performed by different external or reference execution systems.

A reassignment/failover that represents a new attempt creates a successor Run rather than silently reusing attempt identity.

### Outcome

A candidate result produced by a Run.

An Outcome is a claim, not truth. It remains non-authoritative until governed disposition based on valid independent evidence and authority.

### Evaluation

An immutable validation record concerning evidence, a Run, Outcome, Effect or related claim.

Its recorded content is append-only in meaning. Effective use may change through appended conflict, invalidation or arbitration records; prior judgments are not rewritten.

Stale, superseded or cross-entity Evaluation evidence cannot authorize a current disposition.

### Effect

A planned, attempted or observed change to the external world.

Examples include publishing content, sending a message, changing a remote system, charging money, deleting a cloud resource or deploying to production.

Occurrence and authorization remain separate. `COMMITTED` denotes independently confirmed occurrence, not moral or policy approval. `QUARANTINED` represents controlled reconciliation for uncertain occurrence, incidents or unsafe/uncertain remediation.

Compensation/remediation does not erase original occurrence.

## 6. Relationships

```text
Objective
  |
  +-- Task
        |
        +-- Run
              |
              +-- Outcome
              +-- Evaluation(s)
              +-- Effect(s)
```

An accepted Outcome does not automatically complete its Objective. Objective satisfaction remains controlled by explicit completion policy and authority.

## 7. Planning and Routing Boundary

Symphony-K v1 does not require a Symphony-K-owned Planner or generic Router.

If Symphony-K supplies planning, Planner output remains a non-executable `TaskProposal` that must pass governance before becoming a separate Task.

External planning output likewise grants no execution, budget, permission or lifecycle authority by itself.

If Symphony-K supplies routing, route choice remains a replaceable execution concern constrained by governance requirements. External routers may choose execution resources provided they preserve attempt identity/provenance and cannot bypass authority/evidence/Effect boundaries.

## 8. Execution and Sandbox Boundary

ADR-0008 and the accepted Stage 2 sandbox architecture remain accepted technical assets.

Their post-transition role is:

- an execution-provider security/conformance contract;
- an evidence/provenance boundary for execution integrations; and
- an optional/reference execution implementation path.

Owning a production sandbox runtime is not Symphony-K's v1 product identity.

External providers that cannot supply sufficient identity, isolation, provenance or evidence hooks fail conformance rather than receive a weaker trust path.

## 9. Recovery Boundary

Recovery is split into two categories.

### Execution Recovery

External workflow/orchestrator systems may own retries, continuation, scheduling and provider failover.

### Governance Recovery

Symphony-K remains responsible where recovery affects:

- authoritative attempt identity;
- checkpoint/evidence trust;
- Effect occurrence uncertainty;
- reconciliation;
- compensation;
- Human resolution; or
- preservation of historical facts.

A retry may not infer Effect non-occurrence merely from local failure. Replay across uncertain occurrence remains blocked until reconciliation establishes a safe next action.

## 10. Persistence and Authority

Workers and external orchestrators are never the authoritative system of record.

Authoritative state includes:

- lifecycle state and versions;
- evidence/evaluation provenance;
- authority decisions;
- Effects, receipts and occurrence records;
- policy/context references;
- audit events; and
- replay/concurrency receipts.

This state must survive Worker/runtime lifetime.

The accepted Stage 1 implementation uses database-neutral repository/UnitOfWork boundaries with SQLite as the current adapter behind the domain boundary. Persistence technology may evolve without changing accepted semantic guarantees.

## 11. Invariant Enforcement

### Structural / Persistence Layer

Use hard constraints where expressible: foreign keys, uniqueness, immutable identifiers, version columns, transactional writes and append-only protections.

### Domain Authority Layer

All authoritative state changes pass through accepted creation/transition logic. Callers do not receive arbitrary state setters.

### Evidence Layer

Authoritative disposition re-derives validity from durable current evidence/effective-use state rather than trusting caller-supplied stale observations.

### Concurrency / Replay Layer

Mutations use exact operation identity, idempotency and version protection so stale or competing writers cannot silently overwrite authority.

### Runtime / Effect Capability Layer

Security-sensitive external actions must cross trusted execution/effect boundaries rather than depend only on application-level policy checks.

## 12. Facts, Judgments and Policies

### Facts

Externally anchored or historical facts such as occurrence, receipts, evidence existence and actor/action provenance are append-only in meaning.

### Judgments

Evaluations and Human decisions may be corrected, superseded or arbitrated through new attributable records; original judgments remain historical facts.

### Policies

Operational policy may evolve through authorized change, but policy changes do not rewrite historical facts or grant retroactive authorization.

## 13. Constitutional Invariants

At minimum:

1. Worker self-report is never proof of authoritative completion.
2. Workers cannot accept their own Outcomes or grant themselves authority.
3. Evaluators cannot commit Effects they validate.
4. Historical facts and evidence provenance cannot be silently rewritten.
5. Confirmed occurrence cannot later be represented as non-occurrence.
6. Compensation is not historical erasure or true rollback when occurrence remains real.
7. Human override is explicit and audited.
8. Agent/orchestrator/provider/runtime semantics remain outside core governance semantics.
9. Important external actions use the governed Effect path.
10. Authoritative work state survives Worker/runtime loss.

## 14. v1 Architectural Target

The post-transition v1 architecture is complete only when evidence exists for all of the following product boundaries:

```text
accepted Stage 1 governance kernel
    -> stable integration SDK/facade
    -> trusted Evaluation/evidence boundary
    -> governed Effect gateway + occurrence reconciliation
    -> durable audit export
    -> adversarial/conformance suite
    -> external orchestrator integration
    -> reference execution/provider path
    -> end-to-end operational safety
```

This section is a target architecture, not a claim that these post-Stage-1 capabilities are already implemented.
