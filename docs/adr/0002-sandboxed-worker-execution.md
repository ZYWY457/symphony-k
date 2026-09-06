# ADR-0002: Sandboxed Worker Execution

## Status

Accepted.

## Context

Workers may be fallible, compromised, prompt-injected, misconfigured, or intentionally untrusted. Host execution would create unacceptable blast radius and dependency contamination.

## Decision

All worker Runs execute inside an approved sandbox boundary.

Docker is the first SandboxProvider implementation.

## Consequences

- host execution is not the default worker path,
- permissions and credentials must be scoped,
- network access is policy-controlled,
- sandbox and workspace lifetimes are modeled separately,
- future stronger isolation such as microVMs remains possible.
