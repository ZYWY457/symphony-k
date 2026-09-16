# Symphony-K v1 Product Contract

## Authority and purpose

This contract defines the observable Symphony-K v1 product and its final
acceptance expectations. It constrains future implementation where a choice
would materially change the product delivered, but it does not choose low-level
implementation mechanisms.

This document is subordinate to the [Constitution](../CONSTITUTION.md), the
[core beliefs](README.md#constitution-and-core-beliefs), accepted ADRs,
[Architecture](../ARCHITECTURE.md), and accepted designs. It must be read with
the [Roadmap](../ROADMAP.md), [Development Path](DEVELOPMENT_PATH.md), and
[Reference Workflows](REFERENCE_WORKFLOWS.md). Nothing here grants execution
authority or declares a future capability implemented.

## Product identity

Symphony-K v1 is a **single-node, self-hosted/local-first,
outcome-oriented AI work orchestrator for bounded computer-mediated work**.

It manages work, not agents. A requester supplies bounded Objectives and
constraints; Symphony-K governs work across replaceable execution resources
while keeping authoritative state, evidence, acceptance authority, external
Effect authority, and audit history outside untrusted Workers.

Symphony-K v1 is not primarily:

- multi-agent chat;
- an IDE plugin;
- an autonomous unrestricted agent;
- an LLM wrapper;
- a generic workflow-language engine; or
- a SaaS multi-tenant control plane.

Those may be integrations or post-v1 directions. They do not define the v1
product.

## Supported v1 operator

The primary supported operator is a technically capable Human who can install
and operate one Symphony-K node on infrastructure they control. The operator
understands explicit configuration, can inspect diagnostic evidence, and owns
the Human decisions required by policy.

Automation may use stable programmatic interfaces, but Human governance must be
operable without editing the database or calling private internal Python APIs.
A rich graphical interface is not required for v1.

## Required operator surfaces

The v1 product provides:

- a stable local service/API boundary;
- a supported CLI operator surface; and
- repository documentation sufficient to install, configure, operate,
  stop/restart, inspect, troubleshoot and recover the supported deployment.

The future bounded designs for Stage 11 and Stage 13 decide protocols,
frameworks, transports, process supervision and packaging. This contract does
not select those mechanisms. A graphical UI remains optional/post-v1 unless a
Human roadmap amendment promotes it.

## Canonical governed work lifecycle

The observable v1 flow is conceptually:

```text
Human/System submits a bounded Objective
    -> the system records the authoritative Objective
    -> the Planner may propose bounded TaskProposal(s)
    -> applicable Human/policy governance reviews proposals
    -> an accepted proposal becomes a separate Task
    -> the Router selects an eligible ExecutionProfile and route
    -> a Run executes through an AgentDriver in a governed sandbox/workspace
    -> the Worker produces claims, artifacts and a candidate Outcome
    -> independent verification collects evidence and persists Evaluation(s)
    -> conflicts or low confidence escalate or arbitrate under policy
    -> accepted disposition contributes to Task/Objective completion policy
    -> a consequential external change becomes governed Effect work
    -> normal Effect execution follows Prepare -> Verify -> Authorize -> Commit
    -> receipt, occurrence, reconciliation and remediation remain durable
    -> sufficient audit history remains inspectable
```

This is a product flow, not a new lifecycle table. It does not add a Stage 1
entity or edge, make TaskProposal executable, allow an accepted Outcome to
automatically complete an Objective, or combine execution, verification,
authorization and commitment authority.

## Required observable capabilities

At final v1 acceptance, a supported operator can:

1. install and start the supported single-node deployment;
2. submit a bounded Objective with success criteria and applicable budget,
   risk, time, permission and Human-approval constraints;
3. query authoritative Objective, Task, Run, Outcome, Evaluation and Effect
   state;
4. review TaskProposals when planning is used and distinguish a proposal from
   the separate Task created after governance;
5. approve, reject or escalate decisions assigned to Human governance;
6. observe route and Run progress without treating Worker self-report as fact;
7. inspect artifacts, evidence, Evaluations and effective conflict/arbitration
   status;
8. observe low-confidence or materially conflicting verification escalation;
9. inspect failure classification, checkpoints, recovery decisions and
   Resume/Rewind/Reassign history;
10. approve or reject sensitive and irreversible Effect authorization where
    required;
11. inspect Effect preparation evidence, authorization, receipts, occurrence,
    quarantine, reconciliation, rollback and compensation history without
    conflating those facts;
12. stop and restart/reopen the application without losing authoritative state;
    and
13. query enough attributable audit history to reconstruct why important
    decisions and external actions occurred.

These are target capabilities. Their presence here is not a claim that they are
implemented before the owning stages have completed and passed Human review.

## v1 deployment boundary

The required initial delivery scope is:

- one supported Symphony-K node;
- self-hosted/local-first operation on operator-controlled infrastructure;
- Docker as the first sandbox substrate, without making Docker the permanent
  product identity; and
- an accepted persistence adapter behind database-neutral domain boundaries.

The current Stage 1 SQLite adapter may support this deployment where accepted,
but this contract does not freeze SQLite as a permanent product choice.

The following are not required for v1 unless a later Human roadmap amendment
promotes them:

- distributed workers or HA/control-plane clustering;
- a remote sandbox fleet or microVM isolation;
- multi-tenant SaaS or organization tenancy;
- GPU scheduling;
- a rich web GUI;
- an external tracker ecosystem;
- cloud-specific deployment architecture; or
- learned routing beyond the accepted Stage 10 boundary.

Lack of these capabilities is not a v1 release blocker. Claiming them without
implementation and evidence is prohibited.

## Product invariants visible to the operator

The operator must observe constitutional behavior, not merely internal policy
claims:

- Worker output never becomes accepted truth automatically.
- Workers cannot directly mutate authoritative lifecycle state, grant
  themselves authority or accept their own results.
- Important external Effects cannot bypass Effect governance.
- Irreversible Effects require configured, exact Human authorization before
  normal commit.
- Confirmed occurrence remains factual even when authorization was absent or
  unknown.
- Failure, retry, recovery and reassignment do not silently erase or rewrite
  history.
- Recovery produces attributable decisions and new attempt identities where
  required rather than pretending failure did not occur.
- Accepted, rejected, conflicted, corrected and arbitrated evidence remains
  auditable in historical meaning.
- Rollback and compensation remain distinguishable; compensation cannot erase
  original occurrence.
- Replacing a route, provider, model, AgentDriver or sandbox does not change
  core domain semantics.
- Raw audit/learning history cannot directly mutate production policy.
- Human override is explicit and audited and cannot rewrite facts or bypass the
  Constitution.

## v1 final acceptance contract

A fresh maintainer with no private conversation history must be able to clone
the repository and, using repository documentation alone:

1. install and configure the supported deployment;
2. start it and verify environment readiness;
3. operate the canonical governed work lifecycle;
4. exercise required Human governance and Effect decisions;
5. stop, restart and reopen it without losing authoritative history;
6. inspect evidence, decisions, recovery and Effect history; and
7. reproduce the accepted release artifacts.

The final Stage 12–14 acceptance process must demonstrate every canonical
scenario in [Reference Workflows](REFERENCE_WORKFLOWS.md). No unresolved
release-blocking constitutional or security defect may remain. Known
limitations must be explicit and must not conceal a failed required capability.

Creating a tag or publishing a release is a separate remote Effect requiring
explicit Human authorization. Candidate acceptance does not authorize
publication.

## Decision ownership

The durable documents have distinct responsibilities:

| Artifact | Decision owned |
| --- | --- |
| Constitution and core beliefs | Non-negotiable authority, trust, history and safety rules |
| Accepted ADRs and Architecture | System boundaries and material architecture choices |
| This Product Contract | Observable v1 scope, operator experience and final acceptance expectations |
| Roadmap | Delivery order and stage boundaries |
| Development Path | Stage entry, deliverable, evidence and exit contracts |
| Reference Workflows | Canonical acceptance scenarios and stage-to-product traceability |
| Stage parent plans | Bounded architecture/implementation contract for one stage |
| Durable TaskSpecs | Authority for a concrete bounded repository mutation |

The Product Contract cannot override a higher-authority artifact, and a lower-
level plan or TaskSpec cannot silently redefine the Product Contract. If a
future implementation cannot satisfy this contract without changing accepted
architecture or observable v1 scope, the Worker must stop and seek the required
Human, ADR or design reconciliation.

## Implementation restraint

This contract deliberately does not select an HTTP framework, CLI library,
process supervisor, packaging mechanism, replacement database, message bus,
container orchestrator, second Agent runtime, browser provider, semantic judge,
router formula, learning algorithm, frontend framework or cloud architecture.
Those choices belong to future bounded design and implementation work.
