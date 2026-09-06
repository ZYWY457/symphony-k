# ADR-0001: Python for the Initial Control Plane

## Status

Accepted for the initial implementation.

## Context

The project requires rapid iteration across APIs, agent runtimes, Docker, model providers, persistence, evaluation, and policy logic. The control plane is expected to be predominantly I/O-bound during early stages.

## Decision

Use Python for the initial control-plane implementation.

Python is an implementation choice, not a constitutional dependency. Public domain boundaries and interfaces must permit future components to be implemented in other languages where justified.

## Consequences

Positive:

- fast iteration,
- broad integration ecosystem,
- strong compatibility with AI/agent tooling,
- straightforward testing,
- good fit for Codex-assisted development.

Constraints:

- use typed domain models,
- avoid unstructured dictionary-based core state,
- isolate performance-sensitive components behind interfaces,
- do not leak Python-specific assumptions into protocols.
