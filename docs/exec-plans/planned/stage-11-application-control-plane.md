# Stage 11 — Application Control Plane and Human Governance Surface

**Status:** PLANNED — not implementation authorization
**Constitutional baseline:** `constitution-v0.1`

## Objective and why this stage exists

Expose the accepted planes as an operable application so Humans can submit,
inspect, govern and audit work without raw persistence edits or internal Python
calls.

## In scope

- application service layer over domain, execution, verification, recovery and
  Effects;
- stable local service/API boundary;
- CLI or equivalent supported operator entry point;
- Objective submission/query and TaskProposal review actions;
- Run, Outcome, Evaluation and Effect inspection;
- Human approval/rejection, policy override and break-glass recording;
- initial deployment identity/authorization and structured audit queries.

## Out of scope

- direct database mutation from UI/API handlers;
- unaudited administrator shortcuts;
- rich graphical UI as a v1 requirement;
- multi-tenant organization controls and public cloud service architecture.

## Architecture boundaries

Handlers call application services; application services call authoritative
domain/controllers. Read models may optimize queries but cannot become mutation
authority. Human actions remain scoped commands with audit and policy context.

## Expected new interfaces and concepts

Application command/query services, API/CLI contracts, operator identity and
authorization context, approval/override/break-glass commands, audit query and
stable error model. New cross-cutting identity/API dependencies require ADRs.

## Cross-stage dependencies

Requires Stages 1–10. Supplies the supported operator workflow used by Stage 12
system tests and Stage 14 delivery documentation.

## Security and trust requirements

Authentication, least privilege, command/query authorization, secure defaults,
input validation, secret redaction, tamper-evident audit references and explicit
break-glass expiry/review. UI identity never bypasses domain authority.

## Failure model

Authentication/authorization failure, stale command version, service timeout,
partial client disconnect, duplicate request, unavailable subsystem and audit
query degradation are explicit. Idempotent commands do not duplicate Effects.

## Milestones

1. Accept application/API, identity and authorization ADRs.
2. Implement application service command/query boundary.
3. Implement supported local API and stable error/idempotency contracts.
4. Implement CLI/operator workflows and inspection.
5. Implement approvals, overrides, break-glass and audit queries.
6. Complete security/usability review and Human Exit Review.

## Proposed bounded Issue decomposition

- application/API and identity ADRs;
- command services;
- query/read services;
- local API;
- CLI/operator entry point;
- governance actions and audit queries;
- authorization/security tests;
- stage reconciliation.

## Validation strategy

API/CLI contract tests, authorization matrices, stale/duplicate commands,
handler dependency checks preventing direct persistence writes, full governed
operator workflow, approval and break-glass audit, redaction and restart/client
disconnect behavior.

## Human Exit Review questions

- Can an operator drive the full governed workflow through supported interfaces?
- Can any handler bypass authoritative services or mutate persistence directly?
- Are approvals, overrides and break-glass explicit, scoped and audited?
- Are identity, authorization and error semantics safe for initial deployment?
- Can audit/history be inspected without exposing secrets or rewriting facts?

## Stage Definition of Done

An operator can govern the complete workflow through a stable local API and
supported CLI/equivalent, with enforced identity/authorization and no raw state
mutation. Human Exit reconciliation precedes Stage 12.
