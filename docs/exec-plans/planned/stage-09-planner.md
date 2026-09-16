# Stage 09 — Planner

**Status:** PLANNED — not implementation authorization
**Constitutional baseline:** `constitution-v0.1`

## Objective and why this stage exists

Convert bounded Objectives into reviewable, non-executable TaskProposals while
preserving the constitutional separation between planning and authority.

## In scope

- `TaskProposal` representation and lifecycle;
- bounded Objective-to-proposal generation;
- dependency DAG and dependency evidence;
- planning depth, breadth, time and budget limits;
- rationale, assumptions, evidence and uncertainty;
- proposal review, rejection, revision and supersession;
- governed promotion into a distinct executable Task.

## Out of scope

- proposal execution or direct Worker launch;
- Planner-granted permissions, budget, acceptance or Task lifecycle changes;
- unbounded autonomous decomposition;
- collapsing TaskProposal into Task or rewriting rejected proposal history.

## Architecture boundaries

TaskProposal is a planning object outside the six Stage 1 core entities and is
never executable. Governance validates scope, dependencies, budget, risk and
permission; accepted promotion creates a separate Task through authoritative
creation logic.

## Expected new interfaces and concepts

TaskProposal identity/content/lifecycle, proposal dependency edge/DAG,
`PlanningRequest`, `PlanningBudget`, planning evidence/rationale, review decision
and promotion record. Because this is a new top-level concept, an accepted ADR
and design are mandatory entry requirements.

## Cross-stage dependencies

Requires Stage 1 Task authority and Stage 6 budget/risk/permission plus Stage 8
routing capability inputs. Stage 10 will learn only from governed history.

## Security and trust requirements

Planner output is an untrusted proposal. Prompt/model changes confer no
authority. Limits are enforced outside the Planner. Proposal provenance,
Objective scope and dependency inputs are immutable or append-only in meaning.

## Failure model

Invalid/ambiguous Objective, DAG cycle, missing dependency, scope expansion,
budget/depth exhaustion, duplicate proposal, stale Objective, unsupported
capability and governance rejection remain explicit. Failure creates no Task.

## Milestones

1. Accept TaskProposal ADR, lifecycle and promotion design.
2. Implement representation, provenance and bounded planning request.
3. Implement DAG validation and planning limits.
4. Implement review/revision/rejection/supersession governance.
5. Implement atomic, attributable proposal-to-separate-Task promotion.
6. Complete abuse tests and Human Exit Review.

## Proposed bounded Issue decomposition

- TaskProposal ADR and design;
- proposal model/provenance;
- bounded planner adapter and limits;
- DAG validation;
- review/revision/supersession governance;
- promotion boundary and audit;
- end-to-end planning tests and stage reconciliation.

## Validation strategy

Cycle, depth, breadth, time and budget limits; malicious scope expansion;
stale/duplicate proposal; provenance and history immutability; Worker/Planner
authority attacks; rejection creates no Task; promotion creates a distinct Task
with exact approved content and normal Stage 1 constraints.

## Human Exit Review questions

- Can a TaskProposal execute or launch a Worker?
- Can the Planner grant itself budget, permissions or acceptance?
- Are decomposition limits and scope expansion externally enforced?
- Is promotion a distinct governed action with complete provenance?
- Do rejected/superseded proposals remain truthful history?

## Stage Definition of Done

Bounded planning produces durable reviewable TaskProposals only. Governance may
promote an accepted proposal into a separate Task; the Planner never executes
or acquires authority. Human Exit reconciliation precedes Stage 10.
