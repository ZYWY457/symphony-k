# Execution Isolation

## Principle

All worker execution occurs inside an approved sandbox boundary.

The sandbox exists because workers are not trusted. It is not merely dependency isolation.

## Sandbox Provider

Docker is the first implementation target, not the permanent abstraction.

The control plane should depend on a `SandboxProvider` abstraction so future providers may include:

- local restricted process sandboxes,
- remote hosts,
- Kubernetes workers,
- microVMs,
- hardened VM providers.

## Default Restrictions

Worker sandboxes SHOULD default to:

- non-root user,
- dropped Linux capabilities,
- no privileged mode,
- no host root filesystem mount,
- no Docker socket mount,
- CPU limits,
- memory limits,
- process limits,
- execution timeout,
- controlled writable workspace,
- minimized host integration,
- network policy enforcement.

## Network

Network access is a policy, not a Boolean.

Possible policy classes include:

- `NONE`
- `DNS_ONLY`
- `ALLOWLIST`
- `PROXY_CONTROLLED`
- `FULL_INTERNET`

The first implementation may support only a subset, but the domain model must not assume unrestricted connectivity.

## Secrets

Encryption at rest or in transit is necessary but insufficient.

Secrets should be treated as scoped capabilities.

Preferred properties:

- least privilege,
- task-bound scope,
- short lifetime,
- explicit use authorization,
- revocability,
- no broad host credential inheritance.

Where possible, workers should not receive long-lived raw secrets. A Secret/Credential Broker should issue narrow temporary credentials or proxy sensitive operations.

## Workspace and Sandbox Lifetime

A sandbox belongs to a Run.

A workspace may outlive a sandbox when recovery requires continuity across Runs.

The system must distinguish:

- execution environment lifetime,
- workspace lifetime,
- Task lifetime,
- Objective lifetime.

## Security Monitoring

A Safety Monitor may observe:

- unexpected network access,
- unusual file destruction,
- abnormal token/cost growth,
- repeated permission escalation,
- repeated tool loops,
- deviation from expected execution profile,
- suspicious external effects.

Safety monitoring operates in parallel with normal execution and may trigger a circuit breaker before task completion.
