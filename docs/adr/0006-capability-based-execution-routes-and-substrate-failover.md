# ADR 0006: Capability-Based Execution Routes and Substrate Failover

## Status

Accepted

This ADR records a human-approved architecture decision and an initial
human-prepared draft that existed before worker materialization.

## Date

2026-09-08

## Context

Symphony-K manages work rather than specific agents.

Agents, models, tools, sandboxes, and other execution resources are intended to be
replaceable. Existing architecture already establishes AgentDriver and sandbox
boundaries, but it does not yet make the execution substrate itself an explicit
independent routing dimension.

A real development incident exposed this gap.

The same bounded Task, repository, and model could not execute through one Codex
Desktop route because its Windows bundled command runtime failed during execution
preflight. No repository command could start.

The same work was then executed successfully through the Codex VS Code integration
on the same machine, against the same repository, using the same model class.

The failure therefore did not establish that:

- the Task was invalid;
- the model was incapable;
- the AgentDriver concept was unusable;
- the repository or toolchain was broken.

It established that one concrete execution route was unhealthy.

Equivalent failures can occur on any operating system or provider: runtime
incompatibility, shell failure, container failure, unavailable credentials,
network failure, toolchain mismatch, driver defects, GPU/runtime incompatibility,
or provider-specific faults.

The orchestrator must not encode provider-specific remediation for every such
failure. Agent-, operating-system-, client-, and runtime-specific diagnostics
belong behind adapter, driver, sandbox, and execution-provider boundaries.

The Control Plane instead needs a provider-independent way to determine whether
work can execute through an eligible healthy route and, when permitted, continue
that work through another route.

This decision must also preserve Run identity, auditability, verification
requirements, and Effect safety. Blind failover is unsafe when an external Effect
may already have occurred.

## Decision

Symphony-K will model execution routing around capabilities and route health rather
than around a required named agent, client, operating system, or model vendor.

### Execution Route

An Execution Route is a runtime/control-plane concept representing a resolved path
through which a Task can be attempted.

A route may bind concepts such as:

- AgentDriver;
- ModelProfile;
- ExecutionSubstrate;
- SandboxProfile;
- WorkspaceProvider;
- ToolchainProfile.

The exact runtime data model is deferred.

Execution Route is not a seventh top-level domain entity.

The authoritative Stage 1 domain remains:

- Objective;
- Task;
- Run;
- Outcome;
- Evaluation;
- Effect.

### Execution Requirements

Tasks and execution policy should express required capabilities and constraints
rather than naming a specific client or agent implementation unless that identity
is itself an explicit Task constraint.

Examples of requirements may include:

- repository read/write capability;
- Git;
- a required language/runtime version;
- Docker;
- browser access;
- GPU capability;
- permitted network scope;
- credential availability;
- sandbox properties;
- prohibition or authorization of remote mutation.

The exact capability schema is deferred.

### Route Selection

Future routing decisions may consider:

- required capabilities;
- route health;
- policy eligibility;
- security/isolation requirements;
- model capability;
- cost;
- reliability history;
- latency or capacity.

Maximum model capability does not compensate for an unhealthy execution route.

### Execution Preflight

Every execution route must pass an execution preflight before repository mutation.

Preflight has two conceptual layers:

1. Base substrate health:
   the route can start commands and access its workspace.

2. Task capability health:
   the route can satisfy the capabilities required by the current Task.

A worker that is alive is not necessarily an eligible route for a specific Task.

Failure before mutation should normally prevent work from starting through that
route.

### Failure Normalization

Provider-, client-, runtime-, operating-system-, and agent-specific errors are
translated by their responsible adapters/drivers into provider-independent failure
information consumed by the Control Plane.

The exact failure taxonomy is deferred.

The orchestrator core must not contain special-case logic such as Windows CET,
Linux glibc, Codex-specific shell failures, or vendor-specific error strings.

### Route Health and Circuit Breaking

Execution-route health belongs to runtime/control-plane state.

A repeatedly failing route may later be marked unavailable or protected by a
circuit breaker so that the scheduler does not continuously redispatch work through
a known-broken path.

Exact health states, thresholds, cooldowns, probes, persistence, and circuit-breaker
algorithms are deferred.

Failure of one route must not make unrelated otherwise-schedulable work unavailable.

### Reassignment and Run Identity

Changing to another execution route after an execution attempt has begun is a
Reassign operation.

Reassignment does not silently mutate the execution identity of the existing Run.

The prior Run records its historical disposition according to the accepted Run
lifecycle, and the successor execution receives a new RunId.

This preserves:

- which route executed which attempt;
- why execution moved;
- what artifacts existed before reassignment;
- which actor/controller authorized recovery;
- which Run produced later evidence and outcomes.

### Work and Artifact Preservation

Run or route failure does not imply destruction of useful work.

Workspace state, candidate artifacts, checkpoints, evidence, and audit history
should survive loss of a worker or execution route when they remain trustworthy.

A successor Run may continue from preserved work only through an explicit recovery
decision and appropriate verification.

The system therefore adopts the principle:

> Work survives execution-route failure.

### Effect Safety During Failover

Automatic retry or reassignment must never assume that an external Effect did not
occur merely because a worker or route failed.

If an external action may have occurred, or its occurrence is uncertain, the
orchestrator must not blindly replay that action through another route.

Effect occurrence evidence, deduplication identity, reconciliation, authorization,
and later Effect Controller guards must determine whether continuation is safe.

A route failure is not evidence of Effect non-occurrence.

### Human Recovery

Human takeover is a recovery authority, not a bypass around evidence.

A human may choose a recovery route, authorize an exceptional action when permitted,
or perform work directly.

Human takeover does not by itself satisfy required verification gates and cannot
rewrite historical facts.

Published or externally committed work remains subject to the same applicable
evidence and governance requirements.

### Managed and Local Execution

Production deployments should prefer reproducible managed execution substrates with
known toolchains and isolation boundaries.

Local desktop, IDE, workstation, or other user-controlled execution may remain a
supported Execution Provider where required by privacy, locality, development, or
operator preference.

Local execution is not assumed to provide failover capacity.

If Task policy restricts execution to a single unavailable route, the Task may
become BLOCKED rather than silently violating that constraint.

### Scope of This ADR

This ADR defines architecture only.

It does not implement:

- an ExecutionRoute class;
- an ExecutionResource registry;
- capability schemas;
- route scoring;
- automatic failover;
- circuit breakers;
- health persistence;
- driver failure enums;
- managed worker infrastructure;
- scheduler changes;
- recovery execution;
- Effect reconciliation runtime.

Those belong to later bounded implementation work.

Stage 1 Domain Kernel implementation is not expanded by this ADR.

## Consequences

### Positive

Work continuity is no longer conceptually tied to one agent vendor, client,
operating system, or runtime.

Execution failures can be isolated to their route instead of being interpreted as
Task or system failure.

The architecture remains compatible with future Codex, DeepSeek, other agent
drivers, local workers, containers, VMs, and managed execution environments.

Route health becomes separable from model capability, improving future routing,
cost control, observability, and recovery decisions.

Run history remains truthful across reassignment.

Effect failover safety is preserved rather than relying on unsafe blind retry.

### Costs

The future Control Plane will require more runtime concepts than a simple
"choose an agent" scheduler.

Capability discovery, health probing, route selection, fencing, circuit breaking,
and recovery policy will require explicit implementation.

Testing must cover heterogeneous execution routes and failure modes.

Reliable failover may require redundant execution capacity.

Some user-constrained Tasks will intentionally have no available fallback.

## Alternatives Considered

### Encode platform- and agent-specific failure handling in the orchestrator core

Rejected.

This would couple Symphony-K to Codex, Windows, Linux, DeepSeek, and future vendor
details and create an unbounded compatibility matrix.

Specific diagnostics belong behind adapters and drivers.

### Standardize exclusively on one operating system or managed Linux environment

Rejected as the architectural identity.

Managed Linux may be the preferred production substrate, but it does not eliminate
runtime, provider, network, toolchain, or infrastructure failures and would exclude
valid local/private execution requirements.

### Treat a route switch as continuation of the same Run

Rejected.

The execution identity materially changed. Reusing the same Run would weaken audit,
failure attribution, evidence provenance, and recovery history.

### Blindly retry work through another route

Rejected.

A failed route may already have performed an external Effect. Blind replay can
duplicate irreversible actions.

### Leave execution substrate implicit

Rejected.

The observed incident demonstrated that agent/model health and execution-substrate
health are independent and must be representable independently by the future
runtime architecture.

## Related Decisions

This ADR complements the existing decisions governing:

- sandboxed worker execution;
- managing work rather than specific agents;
- evidence before acceptance;
- authoritative state and Effect safety.

Existing accepted ADRs remain unchanged.

If this decision is materially replaced in the future, create a new ADR that
supersedes ADR-0006 rather than silently rewriting its accepted history.
