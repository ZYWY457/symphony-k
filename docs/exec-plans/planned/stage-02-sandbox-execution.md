# Stage 02 — Sandbox Execution

**Status:** PLANNED — not implementation authorization
**Constitutional baseline:** `constitution-v0.1`

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

1. Accept sandbox/workspace/network ADRs and executable contracts.
2. Implement provider-neutral lifecycle and command boundary with fakes.
3. Implement hardened Docker provider and artifact/telemetry paths.
4. Prove limits, denial defaults, cleanup and failure normalization.
5. Reconcile documentation and perform independent Human Exit Review.

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
