# Stage 06 — Budget, Risk, Permission, and Effects

**Status:** PLANNED — not implementation authorization
**Constitutional baseline:** `constitution-v0.1`

## Objective and why this stage exists

Bind execution to explicit resources and permissions, and ensure important
external mutations pass through a governed Effect Controller.

## In scope

- `BudgetProfile` and append-only ledger;
- Risk, Value, Confidence and Verifiability profiles;
- `PermissionEnvelope` and scoped capability/secret boundary;
- `EffectIntent` and Effect execution request boundary;
- Effect Controller Prepare–Verify–Authorize–Commit runtime;
- idempotency, receipts and independent effect verification;
- rollback/compensation execution records and Human approval gates.

## Out of scope

- Worker self-granted budget, permission or credentials;
- hidden external side effects inside generic tool calls;
- retroactive authorization of observed occurrence;
- conflating compensation with rollback or deleting Effect history;
- learned policy/routing.

## Architecture boundaries

Policy components decide eligibility; the Effect Controller alone owns scoped
commit credentials and dispatch. Evaluators do not commit the Effect they
validate. Stage 1 occurrence, authorization and incident histories remain
separate and append-only.

## Expected new interfaces and concepts

Budget ledger/profile, risk/value/confidence/verifiability inputs,
`PermissionEnvelope`, capability grant, `EffectIntent`, preparation artifact,
authorization decision, commit request, receipt, verification and remediation
execution records. ADRs must approve scoring semantics, credential brokering,
dispatch/reconciliation and idempotency.

## Cross-stage dependencies

Requires Stages 1–5, ADR-0004/0005 and the Effect core belief. Supplies policy
constraints to routing/planning and safe scenarios to later integration.

## Security and trust requirements

Least privilege, task/effect-bound short-lived capabilities, exact payload/
target authorization, principal separation, mandatory Human authorization for
irreversible effects, deduplication and independently anchored occurrence.

## Failure model

Budget exhaustion, policy denial, missing/expired permission, preparation or
validation failure, denied/expired Human approval, dispatch timeout, unknown
occurrence, duplicate request, receipt mismatch, rollback failure,
compensation failure and unrecoverable side effect all remain explicit.

## Milestones

1. Accept budget/profile/permission and Effect protocol ADRs.
2. Implement profiles, ledger and permission enforcement.
3. Implement preparation, validation and authorization records.
4. Implement guarded commit, receipts, idempotency and reconciliation.
5. Implement rollback/compensation execution and approval workflows.
6. Complete adversarial Effect tests and Human Exit Review.

## Proposed bounded Issue decomposition

- budget ledger and profile contracts;
- risk/value/confidence/verifiability policy boundary;
- permission envelope and credential broker design;
- Effect prepare/verify/authorize flow;
- commit/idempotency/receipt/reconciliation;
- rollback/compensation runtime;
- Human approval and constitutional security suite;
- stage reconciliation.

## Validation strategy

Ledger concurrency/replay, budget exhaustion, scoped permission matrices,
expired/revoked capability, irreversible approval negatives, evaluator/
committer identity attack, duplicate commit, lost receipt, observed unauthorized
occurrence, uncertain replay denial, true rollback and compensation history.

## Human Exit Review questions

- Can any Worker exceed budget, scope credentials or authorize itself?
- Can an important external mutation bypass the Effect Controller?
- Is irreversible commit impossible without exact Human authorization?
- Are occurrence and authorization recorded independently?
- Do retry, rollback and compensation preserve truth and avoid duplication?

## Stage Definition of Done

Budgets and permissions constrain execution; consequential Effects follow
Prepare–Verify–Authorize–Commit with receipts and idempotency; irreversible
commit is Human-authorized; remediation preserves history. Human Exit Review
and reconciliation precede Stage 7.
