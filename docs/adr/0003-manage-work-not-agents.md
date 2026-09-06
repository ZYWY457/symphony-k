# ADR-0003: Manage Work, Not Agents

## Status

Accepted.

## Context

Tying orchestration semantics to one agent runtime or model would recreate vendor and protocol lock-in and undermine the long-term value of the system.

## Decision

Core orchestration semantics are expressed in terms of Objectives, Tasks, Runs, Outcomes, Evaluations, Effects, execution profiles, evidence, and policy.

Agent-specific behavior is isolated behind AgentDriver adapters.

## Consequences

- new agents should not require core redesign,
- routing selects execution profiles rather than hard-coded providers,
- model and agent ecosystems can evolve independently from the control plane.
