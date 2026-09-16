# Stage 10 — Learning and Reputation

**Status:** PLANNED — not implementation authorization
**Constitutional baseline:** `constitution-v0.1`

## Objective and why this stage exists

Improve routing, validation and policy from delayed verified experience without
allowing raw audit events or one recent result to mutate production behavior.

## In scope

- immutable audit source and derived learning boundary;
- delayed observation/review and verified experience promotion;
- agent, route, tool and validator reliability views by domain;
- rapid negative-evidence propagation and slow trust recovery;
- policy candidate generation;
- shadow evaluation, canary rollout and reversible policy versions;
- attributable data/provenance and policy-governance decisions.

## Out of scope

- raw history directly changing production policy;
- a single global reputation score;
- unverifiable model self-rating;
- opaque learned routing or irreversible automatic rollout;
- rewriting source audit records when derived views change.

## Architecture boundaries

Audit history is immutable source data. Verified experience, derived features,
reputation views and policies are separate versioned domains. Production policy
changes only through authorized governance and controlled rollout.

## Expected new interfaces and concepts

Observation/review record, verified experience item, admission decision,
reliability view, calibration report, policy candidate, shadow result, canary
decision and policy version. ADRs must govern admission, privacy/retention,
calibration and rollout authority.

## Cross-stage dependencies

Requires trustworthy Evaluation, routing, Effect and planning histories from
Stages 4, 6, 8 and 9. Stage 11 exposes Human governance; Stage 12 proves safety.

## Security and trust requirements

Provenance, observation delay, dispute state, sample sufficiency and domain
relevance gate admission. Poisoning, correlated failures and feedback loops are
explicit threats. Trust recovery requires repeated verified evidence.

## Failure model

Insufficient/delayed labels, disputed outcomes, provenance loss, sample
scarcity, drift, calibration failure, shadow regression, canary incident and
rollback failure block promotion. Source audit remains unchanged.

## Milestones

1. Accept learning-data, admission, calibration and rollout ADRs.
2. Implement delayed observation and verified-experience admission.
3. Implement scoped reliability and validator calibration views.
4. Implement policy candidates and historical/shadow evaluation.
5. Implement canary rollout, monitoring and rollback.
6. Complete poisoning/drift review and Human Exit Review.

## Proposed bounded Issue decomposition

- learning governance/privacy ADRs;
- delayed observation and admission;
- scoped reliability views;
- validator calibration;
- policy candidate generation;
- shadow evaluator;
- canary/rollback controller;
- adversarial data tests and stage reconciliation.

## Validation strategy

Admission negatives, delayed-label fixtures, disputed/outlier history,
provenance tampering, correlated samples, asymmetric trust tests, calibration,
historical replay, shadow comparison, canary abort and exact rollback to prior
policy version.

## Human Exit Review questions

- Can raw or disputed history influence production decisions?
- Are reliability claims scoped, calibrated and reproducible?
- Does strong negative evidence reduce trust faster than recovery?
- Is every policy change versioned, reviewed, monitored and reversible?
- Can poisoning or feedback loops cross the verified-experience boundary?

## Stage Definition of Done

Learning affects production only through verified experience and auditable,
shadow-tested, canaried, reversible policy versions. Raw audit truth stays
immutable. Human Exit reconciliation precedes Stage 11.
