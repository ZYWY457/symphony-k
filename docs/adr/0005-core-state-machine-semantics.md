# ADR-0005: Core State Machine Semantics

## Status

Accepted by explicit human architecture review, 2026-09-06.

Revised following human architecture review: occurrence is independent of authorization; TaskProposal is assigned to Stage 9; material Evaluation conflicts are recorded as correlated sets.

Approval record: the human decision **"Human Architecture Review: ACCEPTED"** approves the v0.2 state-machine baseline with 43 core states, 99 legal transition edges, ARBITRATED Evaluation semantics, QUARANTINED Effect semantics, separate occurrence/authorization truth, Evaluation conflict sets, and TaskProposal deferred to Stage 9. No constitutional amendment is required. This accepts the design and authorizes implementation only within the accepted Stage 1 Exec Plan and repository hierarchy; it does not declare Stage 1 implementation complete.

## Context

[Issue #1](https://github.com/ZYWY457/symphony-k/issues/1) requested a design review before implementation. The core beliefs enumerate states but do not enumerate edges. The initial Stage 1 plan left attempt identity, terminal behavior, Evaluation immutability, and uncertain Effect commits ambiguous. These affect state ownership and history semantics, so this ADR records the reviewed and accepted interpretation before implementation.

## Decision

Use the closed transition tables in [state-machines.md](../design-docs/state-machines.md) as the accepted v0.2 Stage 1 design baseline, subject to higher-level documents.

1. Retain the six entities and all 43 existing states. Unlisted transitions are forbidden; scoped authority, guards, concurrency checks, and atomic audit append are mandatory.
2. `RETRYING` prepares continuation of the same interrupted Run with its identity and strategy intact. A new execution attempt, including Rewind that discards an execution path, gets a new Run. `REASSIGNED` closes the old Run once a successor or human handoff is durably recorded. Recovery decisions are applied by scheduler/run-controller authority.
3. Closed execution states are not reopened. Objective archival and Outcome supersession/expiry preserve the earlier result. Later contradictory evidence appends a correction or dispute; it does not rewrite an earlier completion fact.
4. An Evaluation's evidence, verdict, method, and provenance are immutable recorded content. Its effective lifecycle is a versioned projection of appended records. Material conflicts record a conflict-set identity, member/version references, affected scope, evidence and correlation. All participants whose effective use is affected become CONFLICTED together; existing CONFLICTED participants gain appended membership records without a self-transition. Arbitration appends decisions covering the set and each affected member; resolving one member cannot silently release the others or unrelated open conflicts.
5. `COMMITTED` records independently confirmed occurrence, including an unauthorized mutation. Execution authorization and governance/safety findings are separate appended records. Add observation-only `NONE/PLANNED/SIMULATED -> COMMITTED/QUARANTINED` edges for confirmed/suspected incidents. Existing `PENDING_COMMIT/QUARANTINED -> COMMITTED` edges likewise record occurrence without requiring prior authorization to exist. Scoped recording authority is always required; observation never dispatches an external action or grants retroactive authorization. Normal execution still requires Prepare–Verify–Authorize–Commit, identity separation and explicit human authorization before irreversible action. QUARANTINED retains occurrence/remedy context, and reconciliation prevents blind recommit.
6. Actor labels do not confer authority. A worker cannot gain validation or commitment authority by relabeling itself. A validator of an Effect cannot commit that same Effect even if other validators exist. Human authorization of an irreversible Effect is always required under Constitution v0.1.
7. Normally planned Effects require one accountable Task. Incident observations may initially lack a Task/Run association: retain independently anchored external identity, observation provenance and an explicit unlinked reason, then append verified associations without inventing past ownership. Such records confer no execution eligibility. Conflict sets and incident/governance records are supporting audit/provenance structures under the existing entities, not new top-level entities or runtime subsystems.
8. Stage 1 contains only Objective, Task, Run, Outcome, Evaluation and Effect as core domain objects. TaskProposal representation, lifecycle, generation and governance implementation belong to Stage 9 (Planner). A TaskProposal remains planning input and is never directly executable; governed executable work is a separate Task.

## Consequences

- Final semantic cleanup retains 43 states and the same 99-edge topology. Effect quarantine uses QUARANTINED / EffectQuarantined; Evaluation arbitration uses ARBITRATED / EvaluationArbitrated. These are terminology changes, not added states or entities.
- QUARANTINED means exclusion from the normal automatic execution path pending controlled reconciliation or explicit disposition. Occurrence, incident and authorization truth remain separate appended facts/metadata; occurrence_status=DISPROVED and incident_status=CLOSED may coexist with QUARANTINED without implying unknown occurrence or execution eligibility.
- ARBITRATED records completion of arbitration, including an upheld verdict. Append an arbitration_disposition such as UPHELD, MODIFIED or REVERSED with the effective judgment and original Evaluation reference. These dispositions are metadata, not Evaluation states; original content remains immutable.
- Tables can become deterministic domain tests without implementing an agent, recovery runtime, or Effect protocol in this Issue.
- State projections may advance while historical records remain immutable; no particular database or event-sourcing architecture is selected.
- Related-entity decisions require a consistent view and durable links. External execution cannot be made atomic merely by a database transaction.
- Conflict-set membership, affected projections and per-member lifecycle events must be consistent and version-checked. Observation ingestion must deduplicate external occurrences and retain violations even when occurrence is confirmed.
- Pre-commit cancellation and verification timeout use recorded decisions and existing states for this baseline. No new state is silently invented.
- Human architecture review has approved this design and the Stage 1 Exec Plan. Implementation remains bounded by that plan; Stage 1 completion criteria and its exit review still apply. No constitutional amendment is required by these choices.

## Alternatives Considered

- Reuse a Run for every retry or reassignment: rejected because distinct attempts and profiles would lose identity.
- Mutate a completed Evaluation in place: rejected because it erases the original judgment.
- Treat commit timeout as failure or success: rejected because either asserts an unobserved fact and may duplicate an external Effect.
- Require prior authorization or a fabricated Task before recording confirmed occurrence: rejected because that would conceal unauthorized reality. Independent evidence permits factual registration, never execution.
- Mark only the Evaluation that detects a conflict: rejected because other affected verdicts would remain incorrectly eligible for acceptance.
- Add `COMMITTING`, `CANCELLED`, or separate Evaluation process/result state machines now: deferred; the review documents their tradeoffs without extending the core state inventory or later-stage runtime scope.
