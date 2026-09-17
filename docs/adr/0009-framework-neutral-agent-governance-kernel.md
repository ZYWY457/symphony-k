# ADR-0009: Framework-Neutral Agent Governance Kernel and External Execution Boundary

## Status

Accepted.

The corrected R1 decision at exact head
`9c842f18ffcdd51daef8f05d9367f571df677703` received independent technical
re-review **ACCEPT** on Issue #89 comment `5711016301` and explicit Human
**APPROVED / ACCEPTED** on Issue #89 comment `5711029647`.

This acceptance does not authorize production implementation, reconcile the
Product Contract or Roadmap, or release Issue #79.

## Date

2026-09-17

## Context

Symphony-K was originally framed as a complete outcome-oriented AI work
orchestrator. Under that model it would own the critical path from planning and
routing through Agent runtime integration, sandbox execution, verification,
recovery, Effects, learning and an operator control plane. The accepted Stage 1
Domain Kernel established durable authority, evidence, lifecycle, replay,
concurrency and historical-meaning semantics, while the accepted Stage 2 design
specified a strong sandbox-provider security and conformance boundary.

Issues #85 and #86 deliberately tested a narrower strategic thesis: whether the
Stage 1 kernel provides material governance value when planning, routing,
AgentDriver and sandbox execution are external. The initial Issue #85 evidence
received REQUEST CHANGES because important adversarial and audit claims were not
yet demonstrated fairly. Issue #86 corrected those defects. Its
[independent review](https://github.com/ZYWY457/symphony-k/issues/86#issuecomment-5709520565)
accepted the corrected A/B/C/D/E results, including a 7/7 blind audit
reconstruction, while retaining material limitations: facade ergonomics, the
experimental rather than production authorization binding, and the non-atomic
external-commit/local-occurrence-recording boundary.

That evidence showed that the old Stage 2-10 mandatory sequence over-owned
important but non-differentiating mechanisms. A generic Planner, Router,
multiple complete Agent runtimes, workflow retry machinery and a best-in-class
production sandbox can be supplied by replaceable external systems without
giving those systems authority over Symphony-K truth. Keeping all of them on
the v1 critical path delayed the product capabilities that the evidence showed
to be distinctive: exact typed provenance, evidence/effective-use binding,
durable exact replay, append-only historical meaning and governed Effects.

The assets that remain independently valuable are the accepted Stage 1
semantic model, the trust and authority boundaries, the accepted execution
provider contracts, and the evidence needed to reconstruct why an
authoritative decision or consequential action occurred. On Issue #87, the
[Human strategic approval](https://github.com/ZYWY457/symphony-k/issues/87#issuecomment-5710053258)
approved changing the v1 center of gravity while preserving those assets and
their trust semantics.

## Decision

### Product identity and kernel responsibility

Symphony-K's primary architectural identity is a **framework-neutral trusted
governance kernel/control plane around untrusted or semi-trusted agentic
execution**.

The kernel owns or governs:

- authoritative `Objective`, `Task`, `Run`, `Outcome`, `Evaluation` and
  `Effect` state;
- authority decisions and the separation of execution, Evaluation,
  authorization and Effect commitment;
- exact candidate, entity, version, evidence and effective-use binding;
- rejection of stale, superseded, unrelated or cross-entity evidence and
  authority substitution;
- append-only historical meaning and attributable corrections;
- replay, idempotency, optimistic-concurrency and conflicting-write semantics;
- explicit, audited Human governance decisions and overrides;
- consequential Effect preparation, authorization, occurrence, uncertainty,
  reconciliation, remediation and compensation history; and
- causal audit reconstruction from durable authoritative and trusted
  integration records.

External systems MAY own:

- planning and task decomposition;
- routing and scheduling;
- Agent runtime loops and tool use;
- sandbox and execution-runtime implementation; and
- durable workflow, retry, continuation and provider-failover mechanisms.

External systems MUST NOT:

- promote their own claims into authoritative truth merely because they
  produced them;
- self-accept Outcomes or authoritative completion;
- substitute stale, superseded, unrelated or cross-entity evidence;
- grant themselves consequential permission, budget or authority;
- bypass governed Effect authorization and commit semantics; or
- rewrite authoritative historical facts or evidence provenance.

Managing work therefore means governing authoritative work and consequential
Effects. It does not require Symphony-K to own Agent cognition or every
mechanism used to attempt work.

### Embedded-first, service-capable posture

Symphony-K adopts an **embedded-first, service-capable** posture. The same
governance semantics must be usable through:

- a future embedded SDK/facade;
- a future stable local service/API for cross-process or non-Python consumers;
  and
- a future CLI/operator surface.

All surfaces must invoke one semantic authority model rather than implement
weaker parallel rules. This decision does not choose HTTP, gRPC, an application
framework, a CLI library or another transport/implementation detail. The
service-mode identity, authentication, authorization and process trust boundary
require a later bounded design.

### External execution and provider boundary

An execution integration supplies attempts, observations, candidate artifacts
and evidence through governed interfaces. It does not receive lifecycle,
acceptance or Effect-commit authority by virtue of executing the work.
Execution identity and provenance must remain sufficient to bind an attempt to
the correct Task, Run, policy, evidence and resulting records. An integration
that cannot provide sufficient identity, isolation or provenance must fail
conformance rather than receive a weaker trust path.

ADR-0008 and the accepted Stage 2 sandbox design remain accepted historical
technical assets. Their post-transition role is:

- an execution-provider security and conformance contract;
- an optional/reference execution path; and
- an evidence/provenance boundary for execution integrations.

They are no longer evidence that Symphony-K must own the complete production
sandbox runtime for v1 to exist. External Worker execution still requires an
approved isolation boundary appropriate to the integration; external ownership
does not make direct host execution trusted by default.

### Required and optional v1 capabilities

The following are no longer mandatory v1 release blockers:

- a Symphony-K-owned generic Planner;
- a Symphony-K-owned generic Router;
- learned routing or reputation;
- multiple complete Agent runtimes; and
- ownership of the best-in-class production sandbox runtime.

They may remain future modules, reference capabilities or external
integrations. If Symphony-K supplies planning or routing, those capabilities
must obey the same proposal, authority, evidence and Effect boundaries.

### Recovery responsibility

Recovery remains a first-class concern, divided into two categories:

1. **Execution recovery** includes retries, workflow continuation, provider
   failover and scheduler recovery. External workflow or orchestrator systems
   MAY implement these mechanisms.
2. **Governance recovery** includes authoritative attempt identity, trusted
   evidence/checkpoint lineage, uncertain Effect occurrence, reconciliation,
   compensation, Human resolution and preservation of historical facts.
   Symphony-K remains responsible for governing these semantics where they
   affect authoritative state or Effects.

External retry or failover cannot silently reuse a Run identity, promote an
untrusted checkpoint, or infer Effect non-occurrence from execution failure.
Replay across an uncertain Effect remains blocked until governed
reconciliation establishes a safe next action.

### Accepted Stage 1 semantics remain fixed

This decision preserves the accepted Stage 1 model. It does not reopen:

- the six core entities: Objective, Task, Run, Outcome, Evaluation and Effect;
- the 43 accepted states and 99 accepted lifecycle transition/creation
  variants;
- the Worker-untrusted and claims-are-not-facts boundary;
- independent Evaluation before authoritative acceptance;
- exact evidence, current-version and effective-use semantics;
- Effect occurrence as distinct from authorization;
- append-only historical meaning and attributable correction;
- rollback as distinct from compensation;
- exact replay, idempotency and optimistic-concurrency guarantees;
- provider, model and runtime neutrality; or
- explicit Human authorization for irreversible Effects under the current
  constitutional rule.

No state machine, lifecycle edge or top-level domain entity changes in R1.

## Compatibility with accepted ADRs

### ADR-0003: Manage Work, Not Agents

Preserved in principle. Core semantics remain expressed in work, authority,
evidence and Effects rather than Agent protocols. Managing work no longer
implies owning Agent execution or orchestration mechanisms; external execution
remains subordinate to the governance boundary when it seeks authoritative or
consequential action.

### ADR-0006: Capability-Based Execution Routes and Substrate Failover

Remains valid for Symphony-K-owned or reference routing where it is used,
including new Run identity and Effect-safe failover. A generic Router and
automatic substrate failover are no longer mandatory v1 capabilities. External
routing and recovery must still supply the identity and provenance needed for
governance conformance.

### ADR-0008: Stage 2 Sandbox Execution Boundary

Remains an accepted execution-provider security/conformance contract and an
optional/reference implementation path where used. Its security requirements
and historical acceptance are not weakened or rewritten. Owning the sandbox
runtime is no longer Symphony-K's product identity or a universal prerequisite
for v1.

ADR-0003, ADR-0006 and ADR-0008 are not rejected by this decision.

## Constitutional amendment impact

Constitution v0.1 named the product as a complete orchestrator and could be read
to assign Symphony-K ownership of planning, sandboxing, recovery and learning
mechanisms. The accepted Constitution v0.2 amendment changes that responsibility
boundary while preserving the trust model.

The amendment affects product-purpose and ownership wording, not the six entity
state machines or their accepted transitions. It preserves Worker distrust,
independent Evaluation, separation of duties, least privilege, Human
irreversibility authorization, governed Effects, append-only meaning,
occurrence truth, recovery-safe attempt lineage and state durability outside
Worker lifetime.

Threat and consistency analysis:

- external execution increases the risk of weak identity, incomplete evidence
  and unverifiable provenance, so integrations fail closed when required hooks
  are absent;
- multiple embedding and service surfaces risk semantic drift, so one
  authority model governs all surfaces;
- external retry engines risk duplicated Effects and false continuity, so
  attempt identity, idempotency and occurrence reconciliation stay governed;
- optional planning, routing and learning do not weaken their constraints when
  present; and
- historical accepted architecture remains attributable rather than being
  edited to imply the new responsibility boundary always existed.

## Consequences

### Positive

- Stage 1 becomes the product core rather than a precursor hidden beneath a
  complete orchestrator stack.
- The v1 critical path becomes smaller and focuses on integration, trusted
  evidence, governed Effects, audit export and conformance.
- External orchestrators, Agent runtimes and execution providers remain
  replaceable.
- The authority, evidence, Effect and audit conformance boundary becomes
  clearer and independently testable.
- The accepted Stage 2 work remains useful without defining the entire product.

### Costs and risks

- Integration-facade ergonomics remains unsolved; the accepted Stage 1 type
  surface is too broad to assume a good public SDK.
- Production Effect gateway crash consistency remains unsolved, especially the
  external-success/local-recording window and uncertain occurrence.
- External orchestrators may lack adequate stable attempt identity, evidence
  and effective-use hooks.
- The service-mode authority, identity and process boundary still needs design.
- Conformance claims must remain evidence-based; configuration or provider
  claims alone are insufficient.
- Provider integrations may fail to supply sufficient provenance and therefore
  be ineligible for authoritative use.
- Supporting embedded and service forms can create compatibility and versioning
  pressure if the common semantic boundary is not kept explicit.

## Alternatives considered

### 1. Retain the original full-orchestrator roadmap

Rejected as the mandatory v1 path. It preserves a coherent vertically owned
stack but keeps non-differentiating Planner, Router, multi-runtime and sandbox
ownership ahead of the governance capabilities supported by the strategic
evidence.

### 2. Pure embedded ledger library, permanently no service

Rejected. An embedded facade offers a small initial integration surface, but a
permanent no-service rule would exclude cross-process and non-Python consumers
and would decide a deployment limitation without sufficient evidence.

### 3. Simple policy/approval wrapper

Rejected. Approval checks without exact authoritative state, evidence binding,
occurrence truth, replay/concurrency semantics and append-only causal history
do not preserve the accepted trust model or the demonstrated differentiation.

### 4. Full pivot discarding Stage 2 and sandbox architecture

Rejected. The accepted execution isolation and provider contract remains a
valuable security, conformance, provenance and reference-execution asset.
Discarding it would erase useful technical work and weaken the integration
boundary.

### 5. Framework-neutral governance kernel

Selected. It preserves the accepted semantic and trust core, permits external
ownership of execution mechanics, supports both embedded and service use, and
retains Stage 2 as an optional/reference provider boundary.

## Migration impact

This R1 decision is accepted. Later bounded work must update the following
documents in order:

- **R2 — product and architecture:** `VISION.md`, `ARCHITECTURE.md`,
  `docs/V1_PRODUCT_CONTRACT.md` and the root `README.md`;
- **R3 — delivery plan:** `ROADMAP.md`, `docs/DEVELOPMENT_PATH.md`, affected
  planned Exec Plans and the active Stage 2 parent/status; and
- **R4 — workflows and cold-start governance:**
  `docs/REFERENCE_WORKFLOWS.md`, `STATUS.md`, `AGENTS.md`,
  `docs/AI_HANDOFF.md`, `docs/README.md`, `docs/adr/README.md` and materially
  stale navigation/index files.

R2 must redefine observable product responsibility without claiming
implementation. R3 must replace the old Stage 2-10 mandatory dependency chain
while preserving completed-stage history. R4 must make canonical workflows and
cold-start discovery describe governance of external or reference execution.
Historical completed plans and accepted technical artifacts remain historical
truth.

Issue #79 remains **BLOCKED / NOT RELEASED**. No implementation restarts until
R1-R4 have passed their required independent review and Human acceptance gates
and a fresh post-transition implementation TaskSpec is explicitly released.

## Verification and rollback posture

R1 verification was documentary: inspect the exact diff and allowed paths,
check links and Markdown structure, confirm the Constitution version and status,
and verify that protected product, architecture, roadmap, source, test and
accepted ADR contents were unchanged. It makes no runtime claim.

If later review finds that the accepted decision weakens an invariant,
misstates evidence or creates an unresolved contradiction, work must stop and
the correction must be made forward through the applicable governance process.
If an accepted transition is later reversed, a new ADR and constitutional
amendment must append the new decision and migration consequences. Historical
approvals, evidence and Effect occurrences must not be silently rewritten.