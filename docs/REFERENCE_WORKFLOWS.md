# Symphony-K Reference Workflows

## Purpose and authority

These workflows are canonical v1 acceptance scenarios for the accepted
framework-neutral governance/control-plane product. They describe observable
behavior across the governance boundary without requiring Symphony-K to own the
external planner, orchestrator, Agent runtime or production sandbox.

A workflow description is a product acceptance target, not evidence that the
capability is implemented. Implementation requires a fresh durable TaskSpec and
the applicable design/review gates.

## Common governance boundary

```text
external agent / orchestrator / runtime
    -> claims, candidate Outcomes, evidence, requested Effects
    -> Symphony-K binds Task/Run/entity/version/provenance
    -> trusted independent Evaluation/evidence
    -> authoritative disposition
    -> governed Effect authorization/dispatch/receipt/occurrence
    -> uncertainty/reconciliation/remediation when required
    -> durable causal audit reconstruction
```

External execution may decide how work is attempted. It never gains authority
merely by producing a result, choosing a route, retrying work or reporting tool
success.

## Workflow A — External execution submits a candidate Outcome

### Intent

Allow an external agent/orchestrator to attempt bounded work while Symphony-K
retains authority over the resulting state and disposition.

### Main path

1. A bounded Task and Run identity exist under Symphony-K governance.
2. An external runtime receives the execution context and attempts the work.
3. The runtime submits artifacts, evidence references and a candidate Outcome.
4. Symphony-K binds the submission to the exact Task, Run, entity versions,
   execution identity and provenance.
5. Independent Evaluation checks the applicable evidence and acceptance rules.
6. Only current, eligible, non-conflicted evidence may support authoritative
   disposition.
7. The authoritative Outcome/Task decision is appended through governed state
   transitions.
8. The complete causal record remains reconstructable without trusting the
   producing runtime's narrative.

### Must fail closed

- Worker self-report is treated as acceptance.
- A candidate from another Run or entity is substituted.
- A stale or superseded Evaluation is reused.
- An external orchestrator directly marks authoritative completion.

### Acceptance evidence

A reference integration demonstrates candidate submission, exact provenance
binding, independent Evaluation, authoritative disposition and audit
reconstruction from supported public surfaces.

## Workflow B — Stale, superseded or cross-entity evidence

### Intent

Demonstrate that evidence cannot be replayed or substituted to obtain authority.

### Main path

1. A candidate disposition references exact evidence and entity versions.
2. One test case supplies stale evidence, one superseded evidence, and one
   evidence record belonging to another entity/Run.
3. Symphony-K re-derives current effective use under the accepted Stage 1
   semantics.
4. Every invalid substitution fails closed or enters explicit governed conflict
   handling; none authorizes the requested disposition.
5. The rejection reason and provenance remain inspectable.

### What must never happen

- Caller-supplied judgment overrides current evidence status.
- Matching text/content alone substitutes for exact identity/version binding.
- A prior accepted Evaluation silently regains authority after supersession.

## Workflow C — Consequential Effect with exact Human authorization

### Intent

Perform a consequential external change while preserving separation of
proposal, Evaluation, authorization, dispatch and occurrence.

### Main path

1. Governed work produces an exact Effect request with target/payload identity.
2. The Effect gateway prepares or validates the exact intended operation.
3. Independent Evaluation verifies policy, permissions, evidence and applicable
   remediation readiness.
4. For an irreversible Effect, exact Human authorization is recorded before
   normal real commit.
5. Dispatch uses scoped authority and an idempotency identity.
6. Receipt and/or independent external observation is recorded.
7. Authorization truth and occurrence truth remain separate.
8. Remediation, rollback where real, or compensation appends new history rather
   than erasing occurrence.

### What must never happen

- The producing Worker or evaluator commits the Effect it proposes/validates.
- Irreversible normal commit proceeds without exact Human authorization.
- Tool/API success alone is treated as verified desired state.
- Compensation rewrites the original Effect as never having occurred.

## Workflow D — Dispatch succeeds but occurrence recording is uncertain

### Intent

Handle the crash-consistency window where an external action may have happened
but a local authoritative occurrence/receipt update is missing or uncertain.

### Main path

1. The Effect gateway dispatches an idempotently identified operation.
2. The external endpoint may have applied the operation.
3. Before Symphony-K can durably establish occurrence, the process/connection
   fails or the receipt is unavailable.
4. The Effect enters an explicit uncertain/quarantined reconciliation state
   according to accepted semantics.
5. Automatic blind retry is blocked.
6. Reconciliation uses external readback, receipts, provider evidence and Human
   decision where required.
7. The eventual occurrence/remediation result is appended with provenance.

### What must never happen

- Dispatch failure is inferred to mean non-occurrence.
- A retry duplicates a possibly occurring Effect.
- Uncertainty is hidden by mutating the previous event.

## Workflow E — External retry, failover and attempt lineage

### Intent

Permit an external orchestrator to own mechanical retries/failover without
allowing it to rewrite authoritative attempt identity or Effect safety.

### Main path

1. An external orchestrator attempts a governed Run and encounters failure.
2. Mechanical retry/failover policy may choose another executor or substrate.
3. Where accepted Run semantics require a new attempt, Symphony-K records a new
   Run/attempt identity and predecessor relationship.
4. Surviving artifacts/checkpoints remain claims until their trust and evidence
   lineage is verified.
5. If any Effect occurrence is uncertain, retry across that boundary remains
   blocked pending reconciliation.
6. Audit history explains the original attempt, failure, successor attempt and
   evidence reused or rejected.

### What must never happen

- External failover mutates an old Run into a different attempt.
- Provider failure proves an Effect did not occur.
- A surviving checkpoint becomes trusted merely because the orchestrator kept
   it.

## Workflow F — Durable causal audit reconstruction

### Intent

Allow a fresh operator/reviewer to explain why an authoritative decision or
external Effect occurred without reading private database tables, source code or
hidden model reasoning.

### Required reconstruction

For a selected Outcome or Effect, supported public audit surfaces must identify:

- governing Objective/Task/Run lineage;
- producing execution identity and provenance;
- candidate/result identity and relevant versions;
- exact evidence and Evaluation effective use;
- conflicts/arbitration or Human decisions when applicable;
- Effect preparation/authorization/dispatch/receipt/occurrence/reconciliation;
- policy/version context sufficient to explain the authoritative decision.

A 7/7-style successful reconstruction or its future equivalent must be based on
published supported records, not private implementation inspection.

## Workflow G — Reference execution/provider path

### Intent

Prove the external execution boundary end to end using at least one supported
reference provider path without making that provider Symphony-K's product
identity.

### Main path

1. The reference provider executes a bounded attempt under its approved
   isolation/provenance contract.
2. It returns candidate artifacts/evidence through the same governance facade
   available to other integrations.
3. Symphony-K applies the same authority, Evaluation, Effect and audit rules as
   for any external provider.
4. Provider-specific metadata remains at the integration boundary.
5. Replacing the provider must not change core domain semantics.

ADR-0008 and the accepted Stage 2 sandbox design may supply this reference or
conformance path. Their acceptance does not make ownership of a production
sandbox runtime a v1 prerequisite.

## v1 traceability

The accepted governance-centered delivery path is:

```text
Stage 1 governance kernel
-> governance SDK/facade
-> trusted Evaluation/evidence integration
-> governed Effect gateway and occurrence reconciliation
-> durable audit export/reconstruction
-> adversarial/conformance suite
-> external agent/orchestrator integration
-> reference execution/provider path
-> end-to-end governance safety/recovery
-> production hardening
-> v1 acceptance
```

Workflows A-G are acceptance scenarios across that path. Generic Planner,
generic Router, learned routing/reputation, multiple complete Agent runtimes and
ownership of a production sandbox runtime are optional/reference/future
capabilities, not mandatory workflow prerequisites.
