# Symphony-K v1 Product Contract

## Authority and purpose

This contract defines the observable Symphony-K v1 product and its final acceptance expectations. It constrains future implementation where a choice would materially change the product delivered, but it does not choose low-level implementation mechanisms.

This document is subordinate to the [Constitution](../CONSTITUTION.md), the [core beliefs](README.md#constitution-and-core-beliefs), accepted ADRs and [Architecture](../ARCHITECTURE.md). It must be read with the [Roadmap](../ROADMAP.md), [Development Path](DEVELOPMENT_PATH.md), and [Reference Workflows](REFERENCE_WORKFLOWS.md). Nothing here grants implementation authority or declares a future capability implemented.

## Product identity

Symphony-K v1 is a **framework-neutral governance/control-plane product for agentic work**.

It governs authoritative Objective/Task/Run/Outcome/Evaluation/Effect state, trusted evidence and Evaluation, consequential Effect authority/occurrence, and reconstructable history while allowing external agents, orchestrators, workflow engines and execution runtimes to determine how work is attempted.

Symphony-K v1 is not primarily:

- a complete self-owned agent orchestrator;
- a generic Planner or Router;
- a multi-agent chat framework;
- an unrestricted autonomous agent;
- an LLM wrapper;
- a production sandbox product; or
- a SaaS multi-tenant control plane.

Those may be external integrations, optional/reference capabilities or post-v1 directions. They do not define the v1 product.

## Supported v1 operator and integration posture

The primary supported operator is a technically capable Human who can run Symphony-K on infrastructure they control and understand explicit governance decisions and diagnostic evidence.

The intended deployment posture is **embedded-first and service-capable**:

- a stable governance SDK/facade is a primary integration surface;
- a stable local service/API may expose the same governance kernel for cross-process or non-Python integrations; and
- a CLI/operator surface may expose the same authority model for Human operation and diagnostics.

A rich graphical interface is not required for v1.

All supported surfaces must preserve one semantic authority model. This contract does not select HTTP, gRPC, an application framework, a CLI library, authentication mechanism, process supervisor, vendor or deployment topology.

## Canonical governance boundary

The observable v1 flow is conceptually:

```text
external Human / agent / orchestrator / runtime
    -> submits bounded work context or candidate claim
    -> Symphony-K records authoritative identity/state separately from executor claims
    -> trusted independent evidence/Evaluation is bound to the exact candidate/entity/version
    -> stale/superseded/cross-entity evidence is rejected
    -> authoritative disposition is made through the governed authority path
    -> a consequential requested action becomes an Effect
    -> Effect follows governed prepare/verify/authorize/dispatch-or-commit path
    -> receipt and occurrence are recorded independently of authorization truth
    -> uncertain occurrence enters quarantine/reconciliation
    -> remediation/compensation preserves original historical occurrence
    -> causal audit export explains why the decision/action occurred
```

This is a product flow, not a new Stage 1 lifecycle table. It does not add a seventh core entity, let a Worker self-accept, make an accepted Outcome automatically complete an Objective, or combine execution, Evaluation, authorization and Effect commitment authority.

## Required v1 capabilities

At final v1 acceptance, Symphony-K must provide all of the following.

### 1. Stable governance integration SDK/facade

External callers must have a supported bounded surface for governance operations without needing private internal Python APIs or complete knowledge of the internal semantic type graph.

The exact API shape is a later design decision, but the public surface must preserve accepted authority semantics.

### 2. Trusted independent Evaluation/evidence binding

The product must support attributable evidence and persisted Evaluation independent from Worker self-report.

Authoritative disposition must bind to the exact relevant candidate/entity/version and current effective-use state.

### 3. Exact authority enforcement

The product must fail closed against at least:

- Worker self-acceptance;
- stale/superseded evidence;
- cross-entity evidence or authority substitution;
- replay of old authority as fresh permission;
- incompatible concurrent writes from the same stale version; and
- direct normal-path history erasure.

### 4. Governed Effect gateway

Consequential Effects must have durable, attributable handling for:

- request/preparation;
- verification where required;
- authorization;
- dispatch/commit attempt;
- external receipt;
- occurrence status;
- uncertain occurrence;
- quarantine/reconciliation;
- remediation/compensation; and
- safe retry or stop decisions.

Irreversible Effects require exact explicit Human authorization under Constitution v0.2 unless a future explicit constitutional amendment changes that rule.

The gateway must not infer non-occurrence merely from local failure after an external dispatch attempt.

### 5. Durable audit reconstruction

A supported operator or independent reviewer must be able to reconstruct why an important authoritative decision or consequential Effect occurred without direct database editing/inspection or private source-code knowledge.

The audit surface must retain enough attributable provenance to answer questions such as:

- what occurred;
- who/what authorized it;
- which exact evidence/judgment supported the decision;
- which earlier evidence became stale/superseded;
- whether occurrence was ever uncertain;
- what reconciliation/remediation happened; and
- why final authoritative history has its current meaning.

### 6. Adversarial/conformance evidence

Final v1 acceptance must include repeatable evidence for authority, evidence, replay, concurrency, historical meaning and Effect-governance guarantees.

Conformance claims must be evidence-based. Configuration or provider marketing claims are insufficient.

### 7. Reference integrations proving the boundary

Final v1 must include at least:

- one external agent/orchestrator integration; and
- one reference execution/provider path or conformance target.

Together they must prove the governance boundary end to end without requiring Symphony-K to own the complete execution stack.

## Observable operator capabilities

At final v1 acceptance, a supported operator can:

1. install/configure the supported deployment or embedded integration;
2. create or identify bounded authoritative work context;
3. query authoritative Objective, Task, Run, Outcome, Evaluation and Effect state;
4. distinguish external claims from accepted authoritative disposition;
5. inspect exact evidence/Evaluation provenance and effective-use status;
6. approve/reject/escalate decisions assigned to Human authority;
7. request and inspect governed consequential Effects;
8. inspect authorization separately from occurrence;
9. identify uncertain occurrence and perform/observe governed reconciliation;
10. inspect remediation/compensation without erasing original occurrence;
11. stop/restart supported operation without losing authoritative state; and
12. export enough causal audit history to reconstruct important decisions/actions.

These are target capabilities. Their presence here is not a claim that all are already implemented.

## v1 execution and sandbox boundary

Symphony-K v1 does **not** require ownership of a production sandbox runtime.

Untrusted execution still requires an approved execution-isolation boundary appropriate to the integration. That boundary may be supplied by:

- an external execution provider; or
- a Symphony-K reference/provider implementation.

ADR-0008 and the accepted Stage 2 sandbox architecture remain valid execution-provider security/conformance assets and optional/reference implementation paths.

External ownership does not make host execution trusted by default.

## Planning, routing, runtime and learning boundary

The following are not v1 release blockers:

- a Symphony-K-owned generic Planner;
- a Symphony-K-owned generic Router;
- learned routing/reputation;
- multiple complete Agent runtimes; or
- ownership of a best-in-class production sandbox runtime.

If Symphony-K later supplies these capabilities, they must obey the accepted governance boundary. External systems may supply them provided their claims, evidence and consequential actions cross Symphony-K authority/Effect boundaries where required.

## Recovery boundary

External systems may own mechanical execution recovery such as retries, workflow continuation, scheduling and provider failover.

Symphony-K v1 must govern recovery whenever it affects:

- authoritative attempt identity;
- trusted checkpoint/evidence lineage;
- Effect occurrence uncertainty;
- reconciliation;
- compensation/remediation;
- Human resolution; or
- preservation of historical facts.

A new execution attempt must not silently masquerade as an old Run when the accepted semantics require distinct attempt identity.

## Product invariants visible to the operator

The operator must observe constitutional behavior, not merely internal policy claims:

- Worker output never becomes accepted truth automatically.
- Workers cannot directly mutate authoritative lifecycle state, grant themselves authority or accept their own results.
- Important external Effects cannot bypass Effect governance.
- Irreversible Effects require exact explicit Human authorization before normal real commit.
- Confirmed occurrence remains factual even when authorization was absent, invalid or unknown.
- Stale/superseded/cross-entity evidence cannot authorize a current disposition.
- Exact replay is idempotent; old authority cannot become fresh authority.
- Concurrent stale writers cannot silently overwrite authoritative history.
- Failure, retry, recovery and reassignment do not erase historical attempts.
- Rollback and compensation remain distinguishable; compensation cannot erase original occurrence.
- Replacing an agent, orchestrator, provider or runtime does not change core governance semantics.
- Human override is explicit and audited and cannot rewrite facts or bypass the Constitution.

## v1 final acceptance contract

A fresh maintainer with no private conversation history must be able to clone the repository and, using repository documentation and supported product surfaces alone:

1. install/configure the supported deployment/integration;
2. exercise an external-agent/orchestrator governance flow;
3. submit/record candidate work and trusted independent Evaluation/evidence;
4. demonstrate authoritative disposition with exact evidence binding;
5. exercise a consequential governed Effect with required Human authorization;
6. demonstrate receipt/occurrence and an uncertainty/reconciliation case;
7. demonstrate remediation/compensation preserving occurrence history;
8. export an audit packet sufficient for independent reconstruction;
9. run the required adversarial/conformance evidence; and
10. reproduce accepted release artifacts.

No unresolved release-blocking constitutional, authority, Effect-safety or evidence-integrity defect may remain.

Creating a tag or publishing a release is a separate remote Effect requiring explicit Human authorization. Candidate acceptance does not authorize publication.

## Explicit v1 non-requirements

Unless a later accepted amendment promotes them, the following are not required for v1:

- distributed/HA control-plane clustering;
- multi-tenant SaaS;
- GPU scheduling;
- a rich web GUI;
- ownership of a production Planner/Router stack;
- learned routing/reputation;
- multiple first-party Agent runtimes;
- a remote sandbox fleet;
- a universal workflow language; or
- vendor-specific execution architecture.

Claiming an optional capability without implementation and evidence is prohibited.

## Decision ownership

| Artifact | Decision owned |
| --- | --- |
| Constitution and core beliefs | Non-negotiable authority, trust, history and safety rules |
| Accepted ADRs and Architecture | System boundaries and material architecture choices |
| This Product Contract | Observable v1 scope, operator/integration experience and final acceptance expectations |
| Roadmap | Delivery order and stage boundaries |
| Development Path | Stage entry, deliverable, evidence and exit contracts |
| Reference Workflows | Canonical acceptance scenarios and stage-to-product traceability |
| Stage/transition plans | Bounded design/implementation contract |
| Durable TaskSpecs | Authority for a concrete bounded repository mutation |

The Product Contract cannot override higher-authority artifacts, and a lower-level plan or TaskSpec cannot silently redefine this contract.

## Implementation restraint

This contract deliberately does not select a transport, application framework, CLI library, process supervisor, persistence replacement, queue, container/runtime provider, orchestrator vendor, semantic judge, frontend framework or cloud architecture.

Those choices belong to later bounded design and implementation work.
