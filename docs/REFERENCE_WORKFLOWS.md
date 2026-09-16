# Symphony-K Reference Workflows

## Purpose and authority

These workflows are canonical v1 product acceptance scenarios and architecture
traceability tools. They make the [v1 Product Contract](V1_PRODUCT_CONTRACT.md)
observable without selecting low-level implementations or authorizing future
stages early.

Each workflow uses existing accepted domain concepts. Mechanics that do not yet
exist remain owned by their stages and require bounded designs, ADRs and
TaskSpecs. A workflow description is not evidence that the capability is
implemented.

## Workflow A — Bounded software-maintenance Objective

### Operator intent

Deliver a bounded repository change with explicit success criteria, protected
paths, validation requirements, budget/permission constraints and a declared
remote-mutation boundary.

### Preconditions

- The Objective is finite and has acceptance criteria and authority.
- Repository identity, baseline and durable TaskSpec are concrete.
- Required execution, sandbox, toolchain and verification capabilities are
  available and eligible.
- Permissions distinguish local work from remote publication.

### Main path

1. The operator submits the bounded maintenance Objective and constraints.
2. The system records the authoritative Objective.
3. When planning is used, the Planner produces bounded TaskProposals with
   dependencies and rationale.
4. Governance reviews proposals and creates separate Tasks for approved work.
5. The Router selects an eligible execution profile and route.
6. A Run executes through an AgentDriver inside a governed sandbox/workspace.
7. The Worker produces code/document artifacts, evidence references and a
   candidate Outcome claim.
8. Independent validators perform applicable static checks, tests, diff review
   and policy checks and persist Evaluations.
9. Current, non-conflicted evidence informs Outcome and Task disposition under
   their completion policies.
10. No deployment, push or other external Effect occurs unless separately
    represented, verified and authorized.

### Human decision points

- Accept, reject or revise TaskProposals where policy requires Human review.
- Supply clarification or scoped permission/budget decisions when escalated.
- Arbitrate material verification conflict when automated policy cannot.
- Authorize any sensitive or irreversible external Effect separately.

### Expected authoritative records

Objective, proposal/review history when planning is used, Task, Run and route
binding, artifacts/evidence, candidate Outcome, Evaluations and conflicts,
completion decisions, audit events, budget/permission usage and any separately
governed Effect/receipt.

### Failure and escalation branches

- Invalid or ambiguous scope blocks planning or Task promotion.
- An ineligible/unhealthy route blocks or selects another route under policy.
- Worker/sandbox/provider loss enters the recovery workflow.
- Failed tests or insufficient evidence reject, rewind or escalate the candidate.
- Conflicting Evaluations remain conflicted until governed arbitration.
- A remote mutation request without authority remains uncommitted.

### What must never happen

- A Worker claim marks the Run, Outcome, Task or Objective accepted/completed.
- A TaskProposal executes directly.
- Host execution silently replaces the required sandbox.
- Protected paths, permissions or remote boundaries expand themselves.
- A failed/rejected candidate or prior commit is rewritten as initially valid.

### Owning stages

Stages 1–6 establish authoritative state, execution, verification, recovery and
Effects; Stages 8–9 add routing/planning; Stage 11 exposes operator actions;
Stages 12–14 prove and deliver the complete scenario.

### Final v1 acceptance evidence

A repository fixture with a durable Objective/TaskSpec; proposal and promotion
records; sandboxed Run trace; exact candidate artifacts; independently captured
test/static/diff evidence; persisted Evaluation and disposition; restart/reopen
proof; complete audit correlation; and evidence that no unauthorized remote
Effect occurred.

## Workflow B — Non-code artifact or research Objective

### Operator intent

Produce a bounded research, analysis or document/artifact outcome with explicit
questions, source/evidence requirements, freshness boundary and acceptance
criteria.

### Preconditions

- The requested result and stopping boundary are finite.
- Required data/tool access, network policy and source constraints are explicit.
- The selected route declares the necessary capabilities and permissions.
- Validation requirements distinguish source evidence from Worker narrative.

### Main path

1. The operator submits the bounded Objective and evidence expectations.
2. Governance creates Tasks directly or from approved TaskProposals.
3. The Router selects eligible tools and an AgentDriver/profile without assuming
   a particular browser or research provider.
4. The Run executes in the governed environment and produces artifacts,
   citations/evidence references and a candidate Outcome.
5. Independent validation checks required coverage, provenance, source
   integrity/freshness and stated acceptance criteria.
6. Evaluations and any conflicts are persisted before governed disposition.
7. The accepted artifact remains linked to its evidence and production history.

### Human decision points

- Approve ambiguous scope or evidence/source tradeoffs.
- Grant narrowly scoped access to restricted data or tools.
- Resolve semantic disagreement or low-confidence acceptance.
- Authorize publication or delivery when it is an external Effect.

### Expected authoritative records

Objective, Task/TaskProposal history, Run and route, source/evidence references,
artifact manifest, Outcome, Evaluations/conflict/arbitration, access/permission
decisions, acceptance decision and any publication Effect receipt.

### Failure and escalation branches

- Missing, stale or unverifiable sources leave the Outcome unaccepted.
- Tool/network denial may block, reroute or request scoped escalation.
- Conflicting evidence triggers additional validation or Human arbitration.
- Sensitive-source or privacy constraints may narrow or terminate the Task.
- Publication failure or uncertain occurrence follows Effect reconciliation.

### What must never happen

- Worker prose substitutes for required source evidence.
- Citations or provenance are fabricated to satisfy acceptance.
- A specific browser/tool provider becomes core domain semantics by implication.
- Missing access silently broadens network or credential permission.
- Artifact acceptance automatically authorizes external publication.

### Owning stages

Stages 1–6 provide state, tools/sandbox, verification, recovery and Effects;
Stages 8–9 route and plan; Stage 11 provides supported operation; Stages 12–14
prove documentation, restart and final acceptance behavior.

### Final v1 acceptance evidence

A bounded non-code fixture; explicit evidence requirements; sandboxed execution
trace; content-addressed or durably identified artifact/source evidence;
independent provenance and semantic Evaluations; conflict/low-confidence path;
operator inspection proof; and separately governed publication when exercised.

## Workflow C — Worker, sandbox or provider failure and recovery

### Operator intent

Continue or safely terminate valid work after an execution resource fails,
without losing authoritative progress, changing attempt identity silently or
duplicating an uncertain Effect.

### Preconditions

- Task and Run identity, route and policy are durably recorded.
- Authoritative state exists outside the Worker/sandbox.
- Applicable checkpoints, workspace/artifact references and evidence-chain
  anchors have explicit completeness/trust status.
- Recovery limits, budget and permissions are configured.

### Main path

1. A governed Run starts on an eligible route.
2. The Worker, sandbox, driver, provider or substrate fails.
3. Durable state and telemetry survive outside the failed resource.
4. The system normalizes and classifies the failure.
5. It assesses the latest checkpoint, candidate work and any possible Effect.
6. The Recovery Controller chooses bounded Resume, Rewind, Reassign or Human
   escalation under policy.
7. Resume continues the trustworthy interrupted Run where semantics permit;
   Rewind or Reassign creates/links a new attempt identity where required.
8. Preserved candidate material is reverified before authoritative use.
9. The operator can inspect failure, decision, predecessor/successor and
   resource/budget history.

### Human decision points

- Approve extra budget, permission or a materially different recovery route.
- Decide when failure classification or checkpoint trust is ambiguous.
- Take over or terminate work when automated recovery limits are exhausted.
- Resolve any external Effect occurrence uncertainty before replay.

### Expected authoritative records

Run and route history, normalized failure, telemetry/evidence, checkpoint
manifest/trust status, workspace/artifact references, recovery decision and
policy version, predecessor/successor Run links, budget/permission use, handoff
package and Effect reconciliation evidence when applicable.

### Failure and escalation branches

- An incomplete/corrupt checkpoint is rejected as a recovery anchor.
- Repeated equivalent failure triggers stall/loop limits and escalation.
- No eligible route leaves work blocked rather than violating constraints.
- Budget or permission exhaustion stops automatic recovery.
- Possible external occurrence quarantines replay pending reconciliation.

### What must never happen

- Worker or sandbox loss erases Task state, evidence or audit history.
- Reassign mutates the old Run into a different attempt.
- Hidden reasoning is required to reconstruct the checkpoint.
- Candidate artifacts become trusted merely because they survived.
- Route failure is treated as proof an external Effect did not occur.

### Owning stages

Stage 1 owns Run/history semantics; Stages 2–3 provide failure boundaries;
Stage 4 verifies preserved work; Stage 5 owns recovery; Stage 6 protects
Effects/budgets/permissions; Stage 8 supplies routes; Stages 11–14 expose,
exercise and accept the scenario.

### Final v1 acceptance evidence

Deterministic failure injection for Worker, sandbox and provider loss; durable
state reread after process restart; checkpoint rejection/acceptance evidence;
Resume/Rewind/Reassign traces with exact Run lineage; recovery limit behavior;
uncertain-Effect no-replay proof; and operator-visible audit reconstruction.

## Workflow D — Consequential external Effect with Human authorization

### Operator intent

Perform a consequential external change that contributes to accepted work while
preserving verification, least privilege, exact authorization, idempotency and
occurrence evidence.

### Preconditions

- A governed Task owns the planned Effect and the intended target/payload is
  exact and attributable.
- Required budget, risk, permission, reversibility, idempotency and
  rollback/compensation information exists.
- The preparing Worker has no commit authority.
- Required independent verification and Human-authorization policy is known.

### Main path

1. Accepted work produces an Effect intent through the governed boundary.
2. The Effect Controller prepares or simulates the exact intended operation.
3. Independent verification checks Task alignment, target/payload, permissions,
   risks and remediation readiness.
4. Policy obtains exact Human authorization for irreversible or configured
   sensitive actions.
5. The Effect Controller commits with scoped credentials and idempotency.
6. The system captures a receipt or independently rereads external state.
7. Occurrence, authorization and verification remain separately inspectable.
8. Required rollback, compensation or reconciliation appends linked history.

### Human decision points

- Approve or reject sensitive/irreversible commit for the exact operation.
- Acknowledge scoped policy override or break-glass risk when constitutionally
  permitted.
- Decide remediation when the desired result, receipt or occurrence is
  ambiguous.

### Expected authoritative records

Effect intent and lifecycle, exact target/payload identity or hash,
preparation/simulation artifact, evidence/Evaluations, budget/risk/permission
decision, Human authorization, commit request/idempotency key, receipt/state
observation, authorization findings and rollback/compensation records.

### Failure and escalation branches

- Failed preparation/verification or denied/expired authorization prevents
  normal commit.
- Dispatch timeout or missing receipt triggers reconciliation, not blind retry.
- Receipt mismatch or undesired result triggers investigation/remediation.
- Rollback/compensation failure remains visible and escalates.
- Confirmed unauthorized occurrence follows Workflow E.

### What must never happen

- A Worker or evaluator commits the Effect it proposes/validates.
- Irreversible normal commit proceeds without exact Human authorization.
- API success alone is treated as verified desired state.
- Retry duplicates a possibly committed Effect.
- Compensation relabels the original occurrence as nonexistent or rolled back.

### Owning stages

Stage 1 owns Effect truth/history; Stage 4 provides independent verification;
Stage 5 prevents unsafe recovery replay; Stage 6 owns runtime governance;
Stages 11–14 expose, integrate, harden and accept the scenario.

### Final v1 acceptance evidence

A safe test/stub external system; exact prepared payload and independent
Evaluation; denied and approved authorization cases; principal separation;
idempotent commit; durable receipt and external reread; restart/replay proof;
and operator inspection of authorization separately from occurrence.

## Workflow E — Unauthorized or externally observed Effect incident

### Operator intent

Record and govern evidence that an external mutation occurred or may have
occurred outside the normal authorized path, without hiding reality, inventing
attribution or turning observation into execution permission.

### Preconditions

- Independently anchored evidence identifies an external target/operation or a
  supported suspicion.
- The observer has scoped recording/incident-ingestion authority but no implied
  execution authority.
- Deduplication and provenance information are available.
- Unknown Task/Run attribution and authorization may be recorded as unknown.

### Main path

1. The system independently observes confirmed or suspected external activity.
2. It deduplicates the observation against existing Effect identity/history.
3. Confirmed occurrence is recorded as `COMMITTED`; supported uncertainty is
   recorded as `QUARANTINED` under accepted Stage 1 semantics.
4. Occurrence, incident, attribution and authorization findings remain separate.
5. Unknown attribution is preserved rather than fabricated and may be linked
   later through appended verified association.
6. Investigation gathers evidence and determines policy/safety impact.
7. Reconciliation, rollback or compensation follows a separately governed path.
8. Closure appends disposition and evidence without erasing original history.

### Human decision points

- Assess incident severity, policy violation and required containment.
- Approve sensitive remediation or compensation.
- Accept verified later attribution without rewriting the earlier unknown fact.
- Close a disproved suspicion or confirmed incident with explicit rationale.

### Expected authoritative records

Effect/incident identity, external target/operation, observer and recording
authority, observation and occurrence times where known, evidence/provenance,
deduplication result, occurrence/incident/authorization findings, quarantine or
commit event, attribution links, investigation, remediation and closure.

### Failure and escalation branches

- Insufficient evidence retains uncertainty and blocks automatic replay.
- Conflicting observations require additional verification/arbitration.
- Duplicate observations link to the existing Effect rather than create a
  second occurrence.
- Unsafe/uncertain remediation remains quarantined and escalates.
- A disproved suspicion retains a supported non-occurrence/closure record.

### What must never happen

- Missing prior authorization suppresses confirmed occurrence.
- Recording authority dispatches an external mutation or grants permission.
- Unknown actor, Task, Run or authorization is invented.
- `QUARANTINED` is treated as an occurrence verdict or automatic retry request.
- Rollback/compensation or incident closure deletes the original observation.

### Owning stages

Stage 1 owns occurrence/authorization/quarantine history; Stage 4 verifies
evidence; Stage 5 blocks unsafe replay; Stage 6 owns observation/reconciliation
runtime; Stages 11–14 expose, integrate, harden and accept incident handling.

### Final v1 acceptance evidence

Fixtures for confirmed unauthorized occurrence, uncertain suspicion,
deduplication, unknown attribution, later verified association, disproval,
quarantine reconciliation and compensation; independent evidence; process
restart/reopen proof; and operator-visible separation of occurrence,
authorization and incident status.

## Stage traceability matrix

`Enable` means the stage supplies a capability required by the workflow;
`prove` means its exit evidence must exercise the composed behavior.

| Workflow | Enables and governs | Integration/final proof |
| --- | --- | --- |
| A — Software maintenance | Stages 1–6, 8–9 | Stages 11–14 |
| B — Non-code artifact/research | Stages 1–6, 8–9 | Stages 11–14 |
| C — Failure and recovery | Stages 1–5, 8 | Stages 6, 11–14 |
| D — Authorized external Effect | Stages 1, 4–6 | Stages 11–14 |
| E — Observed Effect incident | Stages 1, 4–6 | Stages 11–14 |

Stage 0 supplies the constitutional and repository governance foundation for
all workflows. Stages 7 and 10 provide cross-cutting architecture validation
and governed reliability/learning inputs; neither is allowed to weaken any
workflow invariant. The [Roadmap](../ROADMAP.md) states the observable
capability unlocked by every Stage 0–14.
