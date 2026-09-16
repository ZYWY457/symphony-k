# Stage 02 — Sandbox Execution

**Status:** ACTIVE - M1 architecture/design; M1A correction candidate
**Constitutional baseline:** `constitution-v0.1`

**Runtime implementation:** NOT YET STARTED

**New sandbox ADR/design:** PROPOSED / pending independent review and Human approval

**Stage 2 complete:** NO

## Activation record

Stage 2 design work was activated on 2026-09-16 by the durable TaskSpec in
GitHub Issue #77, revision `r1 - stage-02-m1-design-start`, against repository
baseline `60b647f825d2eed4dc56a4d3087f165545a1ea88`. The Issue was read directly
from GitHub at observed `updatedAt` `2026-09-16T07:50:33Z` before mutation.

This activation authorizes M1 architecture/design only. It does not accept the
proposed ADR or candidate design, authorize runtime source or test changes, or
open Stage 3. The next gate is independent review and Human approval of the
sandbox ADR/design candidate.

## Objective and why this stage exists

Provide the first enforceable Worker execution boundary. Workers are untrusted;
dependency isolation alone is insufficient, and host execution is not the
default Worker path.

## In scope

- `SandboxProvider` abstraction and first `DockerSandbox` provider;
- `Workspace` abstraction with lifetime distinct from a sandbox;
- bounded command execution, cancellation and output limits;
- CPU, memory, process and wall-time limits;
- network policy abstraction with a safe default;
- artifact collection with integrity metadata;
- teardown, cleanup, telemetry and provider-neutral failure normalization.

## Out of scope

- AgentDriver or model integration;
- scheduling, routing, verification, recovery orchestration or Effect dispatch;
- privileged containers, Docker socket exposure or host-as-Worker execution;
- remote providers and microVMs.

## Architecture boundaries

The Control Plane requests execution through a provider-neutral contract. The
Docker adapter owns Docker details. A sandbox belongs to one Run; a workspace
may survive it only under explicit trusted recovery policy. The domain kernel
does not import Docker/runtime concepts.

## Expected new interfaces and concepts

`SandboxProvider`, `SandboxSpec`, `SandboxHandle`, `Workspace`, `CommandSpec`,
`CommandResult`, `ResourceLimits`, `NetworkPolicy`, `ArtifactManifest`,
`SandboxTelemetry` and normalized sandbox failure information. Required ADRs
must approve lifecycle, network enforcement, workspace trust and resource
accounting before those contracts become implementation commitments.

The current design candidates are:

- [ADR-0008: Stage 2 Sandbox Execution Boundary](../../adr/0008-stage-2-sandbox-execution-boundary.md)
  — **Proposed**;
- [Sandbox Execution v1](../../design-docs/sandbox-execution-v1.md) —
  **Candidate - not an accepted implementation contract**.

## Cross-stage dependencies

Requires completed Stage 1, ADR-0002 and ADR-0006. It supplies Stage 3's
execution substrate and later recovery/routing health inputs.

## Security and trust requirements

Default non-root execution, dropped capabilities, no privileged mode, no host
root or Docker socket mount, controlled writable workspace, enforced resource
limits, explicit network policy, bounded output and reliable cleanup. Secrets
are absent unless a later scoped capability boundary authorizes them.

## Failure model

Normalize image/start/command/timeout/resource/network/artifact/cleanup
failures without hiding provider diagnostics. A cleanup failure is observable;
an unavailable or non-enforcing sandbox fails closed before Worker execution.

## Milestones

1. **S2-M1 current:** activation plus ADR/design candidate, followed by the
   bounded M1A correction under Issue #78; independent review and Human
   approval remain pending.
2. **S2-M2 proposed:** after approval and a new TaskSpec, implement typed
   contracts, workspace boundary and deterministic fake provider.
3. **S2-M3 proposed:** implement Docker lifecycle, enforced constraints,
   artifacts, telemetry and targeted cleanup on an eligible environment.
4. **S2-M4 proposed:** execute adverse real-Docker, crash/reopen and cleanup
   evidence plus operational documentation.
5. Reconcile milestones, perform independent Human Stage 2 Exit Review, and
   leave Stage 3 blocked until that exit is accepted and durably reconciled.

## Proposed bounded Issue decomposition

- architecture/ADR and threat-model review;
- workspace and provider ports;
- bounded command/result contract;
- Docker lifecycle and isolation defaults;
- resource/network enforcement;
- artifacts, telemetry and cleanup;
- adversarial integration tests and stage reconciliation.

Each Issue requires its own durable TaskSpec; this parent plan cannot authorize
the complete stack.

## Validation strategy

Contract tests with a fake provider; Docker integration tests; negative mount,
socket, privilege and network tests; CPU/memory/process/time enforcement;
output truncation; artifact hashes; repeated teardown; orphan/leak inspection;
and provider-failure normalization. Tests must demonstrate host isolation rather
than infer it from configuration text.

## Human Exit Review questions

- Can arbitrary bounded commands run without using the host as Worker runtime?
- Are privilege, socket, mount, resource, output and network defaults enforced?
- Can a failed or malicious Run retain authority after teardown?
- Are workspace survival and artifact trust explicit and attributable?
- Can Docker be replaced without changing domain or Control Plane semantics?

## Stage Definition of Done

Temporary Docker sandboxes execute bounded commands under demonstrably enforced
constraints, collect attributable artifacts/telemetry, normalize failures and
clean up reliably. No AgentDriver is implemented. Human Exit Review is accepted
and durably reconciled before Stage 3 activation.

## M1 candidate evidence and next gate

Issue #77 produced the two design artifacts above without runtime source, test,
dependency or Docker mutation. The candidate defines stable requirement and
future test IDs, provider operations, lifecycle and failure tables, ownership
fencing, hostile artifact handling, Linux-container enforcement claims, a
`NONE`-only initial network profile, cleanup/reopen semantics and the M2-M4
coding map.

Documentation validation for this candidate checked staged name/status,
whitespace, complete diffs, Markdown fences, tracked relative links, stale
planned-path references, current-status consistency, the twelve remaining
planned Stage 3-14 parent files, requirement/test traceability and protected
paths. Official Docker documentation was consulted on 2026-09-16; no Docker
runtime or proposed test matrix was executed.

Independent review requested changes to deadline ownership/termination,
trusted live-workspace collection and public-contract completeness. Issue #78
produced a forward M1A correction without rewriting Issue #77 history or
starting M2. The correction also records a bounded primary-source comparison of
Codex, OpenClaw and lower-footprint backend candidates without changing
ADR-0002's Docker-first decision.

Next gate: independent review and explicit Human approval of corrected
ADR-0008 and the corrected design. Until then, M1 acceptance remains pending,
Issue #79/M2 remains blocked, runtime implementation is not authorized and
Stage 2 is not complete.
