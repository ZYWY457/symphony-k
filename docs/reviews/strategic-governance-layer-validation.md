# Strategic Governance-Layer Validation — Issue #85

## Authority and precondition

```text
TaskSpec reference: https://github.com/ZYWY457/symphony-k/issues/85
TaskSpec revision: r1 - strategic-validation-governance-layer-thesis
TaskSpec access mode: direct-read
TaskSpec updatedAt: 2026-09-17T01:29:56Z
TaskSpec precondition: PASS
Starting SHA: 8e7a86ad8ef2e94a5583ac1acb88fc86e56e02c7
Starting parent: 335a7315300c00857cb1472995e21ad37434be0a
Starting title: docs(governance): accept stage two m1c sandbox erratum
```

Issue #84's independent ACCEPT was freshly read. Issue #79 was freshly read as
`r3 - stage-02-m2-blocked-after-unknown-collection-stop`, **BLOCKED / NOT
RELEASED**. Origin and remote `main` matched the required starting SHA, the
worktree was clean, no merge/rebase state existed, and Git/Python/uv preflight
passed before mutation.

The criteria A/B/C/E below are the Issue's pre-registered criteria, applied
without post-result adjustment. Criterion D is not self-scored.

## Experimental architecture and cost

The external fake Worker, evaluator, Human fixture, trusted gateway and fake
external system remain outside `src/symphony_k`. The fake external system owns
its own target state and idempotency receipts. An opaque-port facade maps four
operations to the accepted `LifecycleService`/`SQLiteStore` boundary:

1. `submit_creation`;
2. `apply_transition`;
3. `commit_effect`;
4. `export_audit`.

The Worker receives only its Worker port and cannot obtain the gateway port.
Actor labels in requests are data, not capabilities. The gateway exact-binds
Effect identity/version, target, payload and correlation to explicit Human
authorization before changing the fake external system. The resulting Human
authorization and receipt are stored in an append-only experimental SQLite
table; Stage 1 stores the confirmed occurrence and compensation records.

Measured facade glue: **234 nonblank/non-comment lines**, 264 physical lines.
Baseline: **183 nonblank/non-comment lines**, 211 physical lines. No production
source, dependency or Stage 1 semantic file changed.

Six broad existing API types are directly exposed to the integration caller:
`CreationRequest`, `CreationContext`, `LifecycleEntityId`, `TransitionRequest`,
`TransitionContext`, and `TransitionResult`. Concrete construction also requires
knowledge of numerous exact semantic record types. The four-operation count is
good; request-construction ergonomics are materially worse than the operation
count suggests.

## Raw adversarial results

| ID | Expected | Symphony-K actual | Fair baseline actual | Difference |
|---|---|---|---|---|
| G1 | Worker claim cannot become authoritative success | SAFE: Worker port rejected lifecycle authority; durable head unchanged | SAFE: producer cannot dispose candidate | Equal protection |
| G2 | Worker cannot self-accept Outcome | SAFE: forged/relabelled port rejected | SAFE: producer identity rejected | Equal protection |
| G3 | Stale evidence cannot authorize current candidate | SAFE: exact snapshot/version guard rejected | SAFE: candidate-version mismatch rejected | Equal protection |
| G4 | Cross-entity substitution rejected | SAFE: nominal identity and exact authority binding rejected | SAFE: string identity equality rejected | Same outcome; Symphony-K has structural type/binding support |
| G5 | Old context rejected or exact idempotent replay only | SAFE: exact event replay returned the immutable original receipt without head mutation | SAFE: stale replay rejected | Symphony-K provides durable exact replay, not merely rejection |
| G6 | Sensitive Effect cannot commit without Human authorization | SAFE: gateway rejected missing authorization before external mutation | SAFE: missing approval rejected | Equal protection; gateway remains integration glue |
| G7 | Confirmed occurrence cannot be erased | SAFE: database append-only trigger rejected delete; COMMITTED remained factual | SAFE through service API; compensation retained `occurred=true` | Symphony-K enforcement is below the application API |
| G8 | At most one stale concurrent writer succeeds | SAFE: one update and one explicit conflict across independent SQLite connections | SAFE: lock+CAS produced one update and one conflict | Equal result; Symphony-K persists the history |

Enforcement result: **8 / 8 safe**.

## Raw legal-flow results

| ID | Symphony-K actual | Baseline actual |
|---|---|---|
| H1 | External Worker candidate recorded as PROPOSED through authoritative creation | Candidate recorded |
| H2 | Independent exact-target Evaluation advanced PENDING -> RUNNING -> COMPLETED with durable result evidence | Independent exact-version evaluation recorded |
| H3 | Current completed Evaluation supported ACCEPTED disposition | Current evaluation supported ACCEPTED disposition |
| H4 | Exact Human authorization gated trusted fake commit; authorization, receipt and occurrence survived database reopen | Exact Human approval gated commit and recorded occurrence |
| H5 | COMMITTED -> COMPENSATING -> COMPENSATED retained the original occurrence record | Compensation retained `occurred=true` and append history |

Legal-flow result: **5 / 5**.

## Fairness and differentiation

The baseline uses ordinary frozen Python records, application policy checks,
an append-only-by-API event log, exact version checks, a lock/CAS boundary,
Human approval records and idempotency keys. It is intentionally competent and
passes every comparable attack and legal control.

No differentiation is claimed for G1, G2, G3, G6 or G8. The bounded structural
advantages are:

- G4: nominal identity/version objects and pervasive exact-binding semantics;
- G5: durable request fingerprinting and exact idempotent replay after head
  advancement;
- G7: SQLite-level append-only enforcement plus immutable historical versions,
  rather than reliance only on service encapsulation.

These are reusable governance primitives, not proof that a senior engineer
could not rebuild similar controls. The experiment demonstrates lower risk of
omission and richer provenance, not monopoly on the guarantees.

## Audit reconstruction

The deterministic packet includes candidate A, E1, explicit supersession by B,
E1's exact-target staleness, supporting E2, conflicting E3, Stage 1 arbitration
and effective disposition, an Effect request, exact Human authorization,
external receipt, confirmed occurrence and compensation preserving occurrence.

- Blind packet: `experiments/governance_layer_validation/artifacts/blind-audit-packet.md`
- Separate answer key: `experiments/governance_layer_validation/artifacts/audit-answer-key.md`
- Machine records: `experiments/governance_layer_validation/artifacts/audit-records.json`

The seven registered questions are embedded in the packet. Occurrence
uncertainty was not modeled, and the packet says so explicitly. The deterministic
records survive SQLite close/reopen and cannot be updated/deleted through the
experimental ledger. This prepares criterion D but does not score it.

## Negative and falsifying evidence

1. Stage 1 has no production external dispatch API. The experiment must supply
   the trusted gateway and capability-port launch boundary.
2. Stage 1 records authorization/occurrence semantics, but atomicity across a
   real external commit and the local durable record is not solved. A crash after
   the external action but before local recording requires future reconciliation.
3. Human authorization and external receipt persistence required experimental
   adapter storage. The Stage 1 occurrence record alone is not a complete
   production commit controller.
4. The baseline matched all 13 safety/legal outcomes with less code and fewer
   concepts. Symphony-K's advantage is stronger reusable structure/provenance,
   not unique bounded-case behavior.
5. Four facade operations fit the target, but constructing accepted Stage 1
   request/context objects exposes a large semantic type surface. A real SDK
   would be needed before ordinary framework integrations are ergonomic.
6. The audit packet is deterministic and durable, but independent 7/7
   comprehensibility remains untested.

## Provisional criteria and recommendation

- **A — PASS (provisional):** meaningful candidate, Evaluation, disposition,
  Effect and audit governance ran without Planner, Router, AgentDriver or
  Sandbox ownership.
- **B — PASS (provisional):** G1-G8 = 8/8 safe; H1-H5 = 5/5 successful.
- **C — PASS (provisional):** G4/G5/G7 provide defensible structural advantages,
  while equal protections are explicitly not credited.
- **D — PENDING INDEPENDENT BLIND REVIEW:** the Worker does not self-score it.
- **E — PASS (provisional):** four operations, 234 measured facade lines, zero
  accepted semantic changes, zero production changes.

**NON-BINDING Worker recommendation: CONDITIONAL.** Do not amend Product
Contract/Roadmap yet. First run the independent blind review and, if it passes,
perform one bounded follow-up on gateway crash consistency and SDK ergonomics.
This is not a Human strategic decision.

Issue #79 remains **BLOCKED / NOT RELEASED**. Stage 2 runtime implementation was
**NOT STARTED by this experiment**. `remote mutation = none`.
