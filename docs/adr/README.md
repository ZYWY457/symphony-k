# Architecture Decision Records

Use ADRs for decisions that materially affect architecture, security, trust, state ownership, protocols, persistence, verification or governance.

Do not silently rewrite accepted ADR history. Supersede or amend forward when a material decision changes.

## Proposed decisions

None currently.

## Accepted decisions

- [ADR-0009: Framework-Neutral Agent Governance Kernel and External Execution Boundary](0009-framework-neutral-agent-governance-kernel.md)
  — **Accepted** at exact head `9c842f18ffcdd51daef8f05d9367f571df677703` after independent technical re-review **ACCEPT** on Issue #89 comment `5711016301` and explicit Human acceptance on comment `5711029647`. It defines the current product/architecture boundary: Symphony-K governs authority, evidence, Effects and audit while external systems may own planning, routing and execution mechanics.
- [ADR-0008: Stage 2 Sandbox Execution Boundary](0008-stage-2-sandbox-execution-boundary.md)
  — **Accepted** historical technical decision. Under ADR-0009 and the accepted R3 delivery plan, it remains an execution-provider security/conformance contract and optional/reference implementation path. Its technical acceptance is not revoked, but the old Stage 2 runtime-first delivery sequence is no longer the mandatory v1 path.

R1-R3 strategic reconciliation is accepted. R4 reconciles workflows and cold-start navigation; no implementation is released by this index.
