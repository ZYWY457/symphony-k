# Vision

## Mission

Build a framework-neutral governance/control-plane system for agentic work that preserves trustworthy authority, evidence, consequential Effect control and reconstructable history even when the agents, orchestrators and execution runtimes performing the work are replaceable or untrusted.

Symphony-K is not primarily a multi-agent chat framework, a generic Planner, a Router, or a sandbox runtime. Its durable role is to govern what becomes authoritative, which evidence may justify a decision, which consequential external actions may proceed, and how the resulting history remains attributable and reconstructable.

## Core Thesis

**Claims are not facts, execution is not authority, authorization is not occurrence, and compensation is not erasure.**

Agents, models, orchestrators, workflow engines, skills, tools, sandboxes and execution providers may determine how work is attempted. They do not gain authority merely by executing work or producing a result.

The governance layer should remain useful as those external systems improve, disappear or are replaced. Provider-, framework-, model- and runtime-specific details therefore remain outside core governance semantics.

## Strategic Continuity

Symphony-K's mission did not fundamentally change during the strategic
transition. Reliable agentic work remains the problem: work should be
governable, verifiable, attributable and reconstructable even when executors
are fallible or replaceable.

What changed is the ownership boundary. The pre-transition direction leaned
toward Symphony-K owning planning, routing, scheduling, Agent/runtime
execution, sandbox infrastructure and retry/failover mechanics. The current
direction lets external systems own how work is attempted while Symphony-K
owns the durable governance and trust semantics that determine what may become
authoritative and consequential. Historical runtime and orchestration designs
remain evidence and optional/reference assets; they were not an erroneous
project and are not rewritten as if the current boundary always existed.

## Desired Interaction Model

An external agent/orchestrator or Human may provide:

- a bounded Objective or Task context;
- a candidate Run/Outcome claim;
- evidence and observations;
- requested consequential Effects;
- applicable policy, budget, risk and permission context; and
- required Human decision points.

Symphony-K should then provide a bounded governance path that can:

1. record authoritative work identity and state separately from executor claims;
2. bind evidence and Evaluations to the exact candidate/entity/version they concern;
3. reject stale, superseded, cross-entity or otherwise invalid authority/evidence use;
4. support independent Evaluation and explicit authoritative disposition;
5. govern consequential Effects through preparation, authorization, dispatch/commit, receipt, occurrence, uncertainty, reconciliation and remediation;
6. preserve optimistic-concurrency, idempotency and exact-replay semantics;
7. keep historical meaning append-only;
8. expose enough durable causal history for an uninvolved reviewer to reconstruct why an important decision or external action occurred; and
9. preserve Human authority where the Constitution requires it.

## v1 Product Thesis

For v1, the product core is the accepted Stage 1 authority/evidence/history model plus production-quality integration and Effect/audit boundaries around it.

At minimum, v1 is expected to provide:

- a stable governance integration SDK/facade;
- trusted independent Evaluation/evidence binding;
- exact authority and stale/superseded/cross-entity enforcement;
- a governed Effect gateway with uncertainty and reconciliation semantics;
- durable audit reconstruction without private database/source inspection;
- adversarial/conformance evidence for authority, evidence, history, replay, concurrency and Effects;
- at least one external agent/orchestrator integration; and
- at least one reference execution/provider path proving the boundaries end to end.

These are product targets unless and until their implementation stages are completed and accepted.

## Deployment Direction

The intended posture is **embedded-first and service-capable**.

A Python SDK/facade may be the simplest first integration surface. The same governance kernel may also be exposed through a stable local service/API and CLI for cross-process or non-Python consumers.

All surfaces must preserve one semantic authority model. The Vision does not select HTTP, gRPC, an application framework, a CLI library, a vendor, a persistence engine or a deployment topology.

## Integration Philosophy

**Internal rigor, external simplicity.** Symphony-K may need exact references,
immutable fingerprints, trusted provenance, conflict history, replay,
concurrency control, authorization/occurrence separation and causal audit
records internally. An ordinary integrator should reach those guarantees
through a small supported surface rather than reconstruct the complete domain
and persistence graph. External simplicity never permits caller-controlled
trust or weaker exactness.

**Own the semantics; reuse the mechanisms.** The durable product identity is
in guarantees such as claim != fact, capability != authority, Evaluation !=
disposition, authorization != occurrence, uncertainty != failure and
compensation != erasure. IAM, storage engines, queues, transports, workflow and
Agent runtimes, sandbox providers, secret management and observability are
replaceable mechanisms that should normally remain behind thin adapters.

Mechanisms are replaceable; semantics are durable. An adapter translates
mechanism identity, evidence and receipts into the governance boundary. It
does not let a provider define authoritative disposition, promote trust,
establish Effect occurrence without sufficient evidence or rewrite history.

## Human Role

Humans remain the ultimate authority for:

- constitutional changes;
- irreversible Effects under the current Constitution;
- policy/judgment overrides within scope;
- escalated ambiguity and conflicts where Human resolution is required; and
- tightly controlled break-glass decisions.

Human authority does not include rewriting historical facts, deleting evidence provenance or pretending a confirmed Effect never occurred.

## Security Philosophy

Every Worker and external execution system is treated as potentially fallible, compromised, misconfigured, prompt-injected or intentionally untrusted.

Safety therefore depends on:

- exact authority boundaries;
- independent evidence and Evaluation;
- least privilege;
- approved execution isolation where untrusted code runs;
- governed Effects;
- durable provenance;
- concurrency and replay discipline; and
- append-only historical meaning.

An external execution provider is not trusted merely because execution is external to Symphony-K.

## Verification Philosophy

Worker output is a claim until independently supported.

Evidence must be attributable and bound to the exact candidate and version it supports. Stale or superseded Evaluation evidence cannot authorize a later state simply because it was once valid. Conflicts, arbitration, invalidation and Human decisions remain historically attributable rather than rewriting earlier records.

## Recovery Philosophy

Execution recovery and governance recovery are distinct.

External systems may own mechanical retries, workflow continuation, scheduling and provider failover. Symphony-K governs recovery when authoritative attempt identity, trusted evidence/checkpoint lineage, uncertain Effect occurrence, reconciliation, compensation, Human resolution or preservation of history is involved.

A retry cannot silently reuse authority, assume non-occurrence of an uncertain Effect, or erase a failed attempt.

## Learning Philosophy

Learning and reputation are optional for v1.

If present, they must be delayed, evidence-backed, versioned, attributable and governed. Raw audit history must never directly mutate production policy.

## What v1 Does Not Require Symphony-K to Own

The following are not mandatory v1 release blockers:

- a generic Planner;
- a generic Router;
- learned routing/reputation;
- multiple complete Agent runtimes;
- a production sandbox runtime; or
- a universal workflow engine.

They may exist as external systems, optional modules, reference integrations or later work. The accepted Stage 2 sandbox architecture remains a valuable execution-provider security/conformance asset and optional/reference implementation path.

## Long-Term Direction

The long-term system may govern work performed by coding agents, research agents, browser/computer-use agents, deterministic programs, external workflow engines, domain-specific tools, APIs, local/frontier models and Human specialists.

The long-term direction is Symphony-K as governance/trust infrastructure, not
as the runtime in which every agent must execute. The durable asset is not
ownership of every executor. It is trustworthy causal governance across:

`claim -> evidence -> Evaluation -> authority -> Effect -> occurrence -> reconciliation -> audit`.
