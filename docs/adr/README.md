# Architecture Decision Records

Use ADRs for decisions that materially affect architecture, security, trust, state ownership, protocols, persistence, verification, or governance.

Recommended structure:

- Status
- Context
- Decision
- Consequences
- Alternatives considered, when useful

Do not silently rewrite accepted ADR history. Supersede an ADR with a new ADR when the decision changes materially.

## Proposed decisions

None currently.

## Accepted decisions

- [ADR-0009: Framework-Neutral Agent Governance Kernel and External Execution Boundary](0009-framework-neutral-agent-governance-kernel.md)
  — Accepted at exact head `9c842f18ffcdd51daef8f05d9367f571df677703`
  after independent technical re-review ACCEPT on Issue #89 comment
  `5711016301` and explicit Human acceptance on comment `5711029647`. This
  acceptance does not itself release implementation or complete R2-R4
  reconciliation.
- [ADR-0008: Stage 2 Sandbox Execution Boundary](0008-stage-2-sandbox-execution-boundary.md)
  — Accepted. Its historical technical decision remains valid; under ADR-0009
  its post-transition role is an execution-provider security/conformance
  contract and optional/reference implementation path rather than mandatory
  product identity.