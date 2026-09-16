# Stage 07 — Second Agent and Architecture Test

**Status:** PLANNED — not implementation authorization
**Constitutional baseline:** `constitution-v0.1`

## Objective and why this stage exists

Test the work-not-agents architecture against one materially different runtime.
The result is an architecture experiment with a release gate, not a mandate to
select any named candidate.

## In scope

- bounded selection of a materially different Agent runtime;
- second AgentDriver adapter, configuration and sandbox image;
- capability, events, usage, cancellation, failure and recovery mapping;
- conformance with the same execution, verification, permission and Effect
  boundaries used by the first driver;
- documented architecture findings and contract corrections when justified.

## Out of scope

- choosing Hermes or another candidate without a separate decision;
- adapter-specific core-domain branches;
- hiding contract defects with translation hacks;
- third/fourth runtimes, routing algorithms or learned selection.

## Architecture boundaries

The accepted AgentDriver remains the sole integration boundary. Any discovered
need for a top-level concept or cross-cutting dependency requires an ADR and
Human review, not silent core redesign.

## Expected new interfaces and concepts

Prefer no new core interface. Provider-specific adapter/configuration/image and
capability mappings are expected. A runtime-selection ADR and any proposed
driver-contract revision are entry/milestone requirements.

## Cross-stage dependencies

Requires Stages 2–6 and the accepted Stage 3 driver contract. Provides the
heterogeneous resource set required by Stage 8 routing.

## Security and trust requirements

The second runtime receives no implicit trust from brand or capability. It uses
the same sandbox, permission, evidence, recovery and Effect gates. Provider
credentials and hidden state never become authoritative project truth.

## Failure model

Record unsupported capability, protocol mismatch, event loss/reordering,
provider outage, cancellation/resume difference, usage mismatch and sandbox
incompatibility. A core-redesign requirement is architectural evidence and
triggers review.

## Milestones

1. Approve runtime selection and comparison criteria.
2. Implement adapter/config/image against unchanged contracts.
3. Pass shared driver and sandbox conformance.
4. Pass verification/recovery/permission/Effect scenarios.
5. Review architecture findings and reconcile any accepted ADR changes.
6. Complete Human Exit Review.

## Proposed bounded Issue decomposition

- runtime evaluation and selection decision;
- adapter skeleton and capability mapping;
- events/results/usage/cancel/resume integration;
- sandbox and credential integration;
- shared workflow/recovery/effect conformance;
- architecture findings and stage reconciliation.

## Validation strategy

Run one shared contract suite against both drivers; compare equivalent governed
workflow traces; inject provider failures; verify cancellation/recovery and
usage; scan domain dependencies for provider coupling; and document every
capability difference explicitly.

## Human Exit Review questions

- Was a new adapter/configuration/image sufficient?
- Did any core orchestration change encode a provider-specific assumption?
- Do both runtimes obey identical authority and Effect boundaries?
- Are capability gaps explicit and safely ineligible rather than emulated?
- Does failure attribution distinguish route, driver, model and Task?

## Stage Definition of Done

Two materially different runtime families execute governed work through the
same abstract boundaries without core redesign. Any architecture failure is
resolved through accepted review, not a local hack, before Stage 8.
