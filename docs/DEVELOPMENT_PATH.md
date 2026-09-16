# Symphony-K Development Path

This document is the authoritative delivery contract from repository bootstrap
through v1.0. [ROADMAP.md](../ROADMAP.md) is the compact stage map; planned and
active parent Exec Plans provide the next level of detail. This path freezes
responsibilities, trust boundaries, required evidence and exit contracts while
leaving future implementation choices to bounded Issues, accepted design work
and ADRs.

`NEXT` and `PLANNED` are sequencing facts, not execution authorization. A future
stage may move to `active/` only after prerequisite exits and a durable
Human-approved TaskSpec. Every stage becomes `COMPLETE` only after independent
Human Exit acceptance and durable governance reconciliation.

## End-to-end dependency graph

```text
Stage 0 Constitution / repository harness
   -> Stage 1 authoritative Domain Kernel
      -> Stage 2 sandbox and workspace substrate
         -> Stage 3 first AgentDriver
            -> Stage 4 independent verification
               -> Stage 5 recovery
                  -> Stage 6 budgets, permissions and Effects
                     -> Stage 7 second-runtime architecture test
                        -> Stage 8 routing and escalation
                           -> Stage 9 governed planning
                              -> Stage 10 governed learning
                                 -> Stage 11 operable application boundary
                                    -> Stage 12 end-to-end safety proof
                                       -> Stage 13 release hardening
                                          -> Stage 14 v1.0 acceptance
```

The sequence is intentionally conservative: later stages may design against
earlier accepted interfaces, but they may not treat unaccepted capabilities as
authoritative dependencies.

## Stage 0 — Constitution and Repository Harness

- **Status:** COMPLETE.
- **Purpose:** Establish the project mission, authority hierarchy, constitutional invariants and repeatable repository workflow.
- **Architectural owner / plane:** Cross-cutting Human Governance and repository governance.
- **Entry criteria:** Repository exists and Human intent is materialized.
- **Required deliverables:** Constitution, vision, architecture, roadmap, core beliefs, ADR process, Exec Plan process and initial harness.
- **Explicit non-goals:** Runtime orchestration, agents, sandboxes, verification or external Effects.
- **Major dependencies:** None.
- **Required ADR/design decisions:** Initial language, sandbox, work-not-agents and evidence-before-acceptance decisions.
- **Minimum test/evidence classes:** Document hierarchy review, repository navigation and baseline toolchain execution.
- **Human Review questions:** Are authority, trust, history and amendment boundaries explicit and internally consistent?
- **Exit criteria:** Constitutional boundaries and repository navigation are accepted; work can be planned without chat-only context.
- **What becomes authorized after exit:** Bounded Stage 1 design and implementation TaskSpecs.
- **Expected repository artifacts:** Root governance documents, `docs/core-beliefs/`, `docs/adr/`, and `docs/exec-plans/`.

## Stage 1 — Domain Kernel

- **Status:** COMPLETE — Human Exit ACCEPTED.
- **Purpose:** Provide the authoritative work-state kernel that later planes must obey.
- **Architectural owner / plane:** Control Plane domain and persistence boundary.
- **Entry criteria:** Stage 0 accepted; state-machine design and ADR-0005 accepted.
- **Required deliverables:** Objective, Task, Run, Outcome, Evaluation and Effect entities; 99 legal lifecycle edges; transition authority; immutable events/history; persistence and concurrency.
- **Explicit non-goals:** Agent execution, real verification, recovery runtime, Effect dispatch, routing, planning and UI.
- **Major dependencies:** Stage 0 and accepted ADRs 0001–0007.
- **Required ADR/design decisions:** Core state machines and initial persistence/atomicity decisions.
- **Minimum test/evidence classes:** Legal/illegal transition tests, authority and invariant tests, atomicity, replay, stale-version rejection and persistence reopen tests.
- **Human Review questions:** Can Workers mutate authority, histories be rewritten, concurrent actors overwrite, or claims substitute for independent acceptance?
- **Exit criteria:** M7/M8/M9 Human Accepted; lifecycle coverage 99 / 99; all eight Human Exit questions answered safely.
- **What becomes authorized after exit:** Stage 2 planning; Stage 2 implementation only under its own durable TaskSpec.
- **Expected repository artifacts:** Domain/persistence implementation, constitutional suite, accepted ADRs/designs and completed Stage 1 plans.

## Stage 2 — Sandbox Execution

- **Status:** NEXT.
- **Purpose:** Execute arbitrary bounded commands in disposable, policy-controlled isolation.
- **Architectural owner / plane:** Execution Plane substrate.
- **Entry criteria:** Stage 1 complete; Stage 2 parent plan activated; sandbox and network-policy ADRs/designs accepted where required; Docker/toolchain preflight passes.
- **Required deliverables:** `SandboxProvider`, first `DockerSandbox`, `Workspace`, bounded command API, CPU/memory/process/time limits, safe-default network policy, artifact collection, teardown, telemetry and normalized failures.
- **Explicit non-goals:** AgentDriver, model/vendor integration, routing, verification decisions, recovery orchestration and real Effect execution.
- **Major dependencies:** Domain Run identity, execution-profile references, ADR-0002 and ADR-0006.
- **Required ADR/design decisions:** Sandbox lifecycle, workspace ownership, network enforcement, resource accounting and failure normalization before those contracts become code.
- **Minimum test/evidence classes:** Isolation escape negatives, resource/time limit tests, network-denial tests, artifact integrity, cleanup/leak tests and host-boundary inspection.
- **Human Review questions:** Is the host excluded as Worker runtime; are privilege, Docker socket, mounts, network and teardown fail-closed?
- **Exit criteria:** Bounded commands run in temporary Docker sandboxes under demonstrably enforced constraints and cleanup.
- **What becomes authorized after exit:** Stage 3 AgentDriver work against the accepted sandbox boundary.
- **Expected repository artifacts:** Accepted ADR/designs, sandbox interfaces/provider, integration tests, operator diagnostics and a completed Stage 2 plan.

## Stage 3 — First AgentDriver

- **Status:** PLANNED.
- **Purpose:** Prove an Agent can be replaced behind a provider-neutral driver contract.
- **Architectural owner / plane:** Execution Plane adapter boundary.
- **Entry criteria:** Stage 2 accepted; AgentDriver protocol/design and Codex adapter TaskSpecs approved.
- **Required deliverables:** Capability declaration; structured `AgentRequest`, response and event contracts; `start/send/status/events/result/usage/cancel`; provider-supported resume; Codex adapter; normalized errors; Run/profile/route binding.
- **Explicit non-goals:** Core-domain vendor fields, a second Agent, learned routing, authoritative verification or direct Worker state mutation.
- **Major dependencies:** Stages 1–2 and ADR-0003/0006.
- **Required ADR/design decisions:** Driver contract, event/usage semantics, cancellation/resume guarantees and credential boundary.
- **Minimum test/evidence classes:** Contract tests, fake-driver tests, sandboxed Codex integration, cancellation, provider failure normalization, usage accuracy and no-vendor-leak architecture checks.
- **Human Review questions:** Can Codex be removed without changing core semantics; are Worker outputs still claims and requests?
- **Exit criteria:** A governed Task/Run executes through Codex and the sandbox via the driver boundary without vendor coupling in core domain.
- **What becomes authorized after exit:** Stage 4 verification runtime work.
- **Expected repository artifacts:** Driver interfaces, Codex adapter, protocol documentation, contract/integration tests and completed parent plan.

## Stage 4 — Verification Plane

- **Status:** PLANNED.
- **Purpose:** Turn candidate results and evidence into independent persisted Evaluations.
- **Architectural owner / plane:** Verification and Safety Plane.
- **Entry criteria:** Governed sandboxed Runs are available; validation and independence designs accepted.
- **Required deliverables:** `ValidationPlanner`, evidence collection, L0–L5 validator interfaces, intermediate assertions, validation profiles, semantic validation, confidence gate, persisted Evaluations and conflict/arbitration integration.
- **Explicit non-goals:** Evaluator Effect commit, Worker self-acceptance, universal LLM judge, recovery orchestration and learning-driven policy.
- **Major dependencies:** Stages 1–3 and ADR-0004/0005.
- **Required ADR/design decisions:** Evidence package, validator independence, confidence aggregation, conflict scheduling and evaluation persistence boundaries.
- **Minimum test/evidence classes:** Deterministic/static/dynamic validator tests, independence negatives, tampered evidence, conflicting verdicts, stale snapshot rejection and sandbox replay.
- **Human Review questions:** Can any producing Worker accept itself; can correlated or stale evidence pass; can an evaluator commit the Effect it validates?
- **Exit criteria:** Evidence-backed Evaluations, not Worker claims, govern candidate Outcome disposition under accepted policy.
- **What becomes authorized after exit:** Stage 5 recovery decisions may use verification evidence.
- **Expected repository artifacts:** Verification interfaces/services, evidence schema/design, validator suites, acceptance matrices and completed plan.

## Stage 5 — Failure and Recovery

- **Status:** PLANNED.
- **Purpose:** Preserve trustworthy progress and choose bounded recovery after failure.
- **Architectural owner / plane:** Verification and Safety Plane with Control/Execution coordination.
- **Entry criteria:** Runs, sandbox/driver telemetry and independent verification exist; recovery ADR/design accepted.
- **Required deliverables:** `CheckpointManifest`, trusted/incomplete checkpoint states, `FailureClassifier`, `RecoveryController`, Resume, Rewind, Reassign, `HandoffPackage`, stall detection and recovery budgets/limits.
- **Explicit non-goals:** Silent Run identity mutation, blind Effect replay, unbounded retries and Worker-selected authoritative recovery.
- **Major dependencies:** Stages 1–4 and ADR-0006.
- **Required ADR/design decisions:** Checkpoint atomicity/storage, failure taxonomy, successor Run semantics, workspace trust and recovery policy.
- **Minimum test/evidence classes:** Crash/restart, corrupted/incomplete checkpoint rejection, transient resume, invalid-path rewind, route reassignment, loop detection and uncertain-Effect replay denial.
- **Human Review questions:** Does authoritative progress survive loss; is every recovery attributable, bounded and safe around Effects?
- **Exit criteria:** Worker/sandbox/provider loss cannot erase work, and Resume/Rewind/Reassign produce auditable deterministic outcomes.
- **What becomes authorized after exit:** Stage 6 can attach budgets, permissions and Effect safety to recovery-aware execution.
- **Expected repository artifacts:** Recovery services/contracts, checkpoint/handoff designs, failure-injection suite, runbooks and completed plan.

## Stage 6 — Budget, Risk, Permission, and Effects

- **Status:** PLANNED.
- **Purpose:** Govern resource authority and consequential external mutations.
- **Architectural owner / plane:** Control Plane policy plus Effect Controller boundary.
- **Entry criteria:** Recovery-safe execution and independent verification exist; Effect protocol, permission and credential designs accepted.
- **Required deliverables:** Budget ledger; Risk, Value, Confidence and Verifiability profiles; `PermissionEnvelope`; `EffectIntent`; Effect Controller; Prepare–Verify–Authorize–Commit; receipts; idempotency; rollback/compensation records; Human approval and scoped secret/capability boundaries.
- **Explicit non-goals:** Worker-held broad credentials, retroactive authorization, conflating occurrence with permission, evaluator/committer identity collapse and raw tool-call Effects.
- **Major dependencies:** Stages 1–5, ADR-0004/0005 and Effect core beliefs.
- **Required ADR/design decisions:** Budget accounting, policy evaluation, credential broker, Effect dispatch/reconciliation, idempotency and compensation execution.
- **Minimum test/evidence classes:** Budget exhaustion, permission denial/escalation, reversible/irreversible gates, duplicate dispatch, lost receipt reconciliation, unauthorized observed occurrence and compensation history.
- **Human Review questions:** Can any important Effect bypass governance; are irreversible actions Human-authorized; does history preserve unauthorized and compensated occurrence truth?
- **Exit criteria:** Consequential Effects use the governed controller; irreversible commit requires explicit Human authorization; receipts and remediation remain auditable.
- **What becomes authorized after exit:** Stage 7 can test a second runtime against the complete execution and safety boundaries.
- **Expected repository artifacts:** Policy/effect services, schemas/designs, security tests, operator approval workflow and completed plan.

## Stage 7 — Second Agent and Architecture Test

- **Status:** PLANNED.
- **Purpose:** Falsify or validate replaceability using a materially different Agent runtime.
- **Architectural owner / plane:** Execution Plane architecture test.
- **Entry criteria:** Stages 2–6 accepted; runtime selection approved by bounded decision and TaskSpec.
- **Required deliverables:** Second driver/configuration/image, shared-contract compliance, comparable usage/error/telemetry mapping and architecture findings.
- **Explicit non-goals:** Adapter-specific core hacks, premature third runtime, vendor selection by roadmap fiat and weakened isolation/verification.
- **Major dependencies:** Stages 1–6 and the AgentDriver contract.
- **Required ADR/design decisions:** Runtime selection and any genuine contract change; Hermes remains only a candidate until approved.
- **Minimum test/evidence classes:** Cross-driver contract suite, equivalent workflow execution, failure normalization, cancellation/recovery and domain import/dependency checks.
- **Human Review questions:** Was only adapter/config/image work needed; does any core redesign signal a failed abstraction?
- **Exit criteria:** Two materially different runtime families execute through the same abstract boundaries without core orchestration redesign.
- **What becomes authorized after exit:** Stage 8 may route among heterogeneous eligible resources.
- **Expected repository artifacts:** Second adapter, shared conformance matrix, architecture review record and completed plan.

## Stage 8 — Router and Escalation

- **Status:** PLANNED.
- **Purpose:** Select eligible execution routes from explicit capability, health, policy and value constraints.
- **Architectural owner / plane:** Control Plane routing/scheduling.
- **Entry criteria:** At least two runtime families and trustworthy operational telemetry exist; routing ADR/design accepted.
- **Required deliverables:** Capability registry, `ExecutionProfile`/resolved route contract, substrate/capability health, rule-based eligibility, cost/reliability inputs, permission/budget compatibility, route/circuit health and escalation/degradation.
- **Explicit non-goals:** Learned routing before Stage 10 evidence, hard-coded vendor preference and failover that replays uncertain Effects.
- **Major dependencies:** Stages 2–7 and ADR-0006.
- **Required ADR/design decisions:** Capability schema, route health model, circuit breaking, scoring precedence and escalation authority.
- **Minimum test/evidence classes:** Eligibility matrices, unhealthy-route exclusion, policy incompatibility, cost/reliability tradeoffs, circuit behavior, no-route blocking and Effect-safe failover.
- **Human Review questions:** Is every selection explainable; can health/model identity be confused; do constraints fail closed?
- **Exit criteria:** Explicit governed constraints and health select routes; no Agent is hard-coded in orchestration core.
- **What becomes authorized after exit:** Stage 9 may propose work that later governance can route after Task creation.
- **Expected repository artifacts:** Registries/router, routing decision records, simulation tests, operational metrics and completed plan.

## Stage 9 — Planner

- **Status:** PLANNED.
- **Purpose:** Convert Objectives into bounded non-executable work proposals.
- **Architectural owner / plane:** Control Plane planning and governance boundary.
- **Entry criteria:** Governed execution, routing, budget/risk/permission inputs and proposal ADR/design exist.
- **Required deliverables:** `TaskProposal` representation/lifecycle, Objective-to-proposal generation, dependency DAG, depth/budget limits, rationale/evidence, review/governance and promotion into a separate Task.
- **Explicit non-goals:** Direct Worker launch, self-granted permissions/budget, direct Task lifecycle mutation and unbounded autonomous decomposition.
- **Major dependencies:** Stages 1 and 6–8; Stage 1 deliberately deferred this concept.
- **Required ADR/design decisions:** Proposal state/authority, DAG validity, bounded planning, duplicate/supersession and promotion transaction.
- **Minimum test/evidence classes:** DAG cycle/depth/budget rejection, proposal immutability/history, authority negatives, promotion separation and cancellation/supersession.
- **Human Review questions:** Can any proposal execute or create authority; are scope expansion and dependencies explicit and reviewable?
- **Exit criteria:** Planning yields governed `TaskProposal` objects only; accepted promotion creates distinct executable Tasks.
- **What becomes authorized after exit:** Stage 10 may learn from verified planning and execution history through governed promotion.
- **Expected repository artifacts:** Proposal domain/design, planner interfaces, governance services, deterministic boundary tests and completed plan.

## Stage 10 — Learning and Reputation

- **Status:** PLANNED.
- **Purpose:** Improve decisions from delayed verified experience without contaminating policy from raw events.
- **Architectural owner / plane:** Verification and Safety Plane policy-evolution boundary.
- **Entry criteria:** Sufficient audited planning/routing/execution/evaluation history; learning ADR/design and data-governance rules accepted.
- **Required deliverables:** Immutable audit source, delayed observation, verified experience pool, scoped agent/route/validator reliability views, asymmetric trust updates, policy candidates, shadow evaluation, canary rollout and reversible policy versions.
- **Explicit non-goals:** Direct raw-event policy mutation, global undifferentiated trust scores, instant trust recovery and opaque learned routing.
- **Major dependencies:** Stages 4, 6, 8 and 9.
- **Required ADR/design decisions:** Admission criteria, calibration, feature provenance, policy candidate authority, rollout/rollback and retention/privacy.
- **Minimum test/evidence classes:** Contamination/admission negatives, delayed labels, calibration, negative-evidence propagation, shadow comparison, canary rollback and audit reproducibility.
- **Human Review questions:** Can raw or disputed history affect production; are policy changes attributable, explainable and reversible?
- **Exit criteria:** Reputation influences decisions only via verified, versioned, auditable and reversible governance.
- **What becomes authorized after exit:** Stage 11 may expose governed policy/learning controls to operators.
- **Expected repository artifacts:** Experience pipeline, reliability views, policy rollout machinery, evaluation reports and completed plan.

## Stage 11 — Application Control Plane and Human Governance Surface

- **Status:** PLANNED.
- **Purpose:** Turn the underlying planes into an operable orchestrator application.
- **Architectural owner / plane:** Application service layer and Human Governance.
- **Entry criteria:** Core execution, verification, recovery, Effects, routing, planning and learning services accepted; API/security ADRs approved.
- **Required deliverables:** Application services, stable local API, CLI or equivalent operator entry point, Objective and proposal actions, Run/Outcome/Evaluation/Effect inspection, approvals, overrides, break-glass recording, initial identity/authorization and structured audit queries.
- **Explicit non-goals:** Direct persistence mutation from handlers, unaudited admin shortcuts, rich graphical UI as a v1 requirement and distributed tenancy.
- **Major dependencies:** Stages 1–10.
- **Required ADR/design decisions:** Service/API boundary, command/query authorization, identity model, error contract and audit-query exposure.
- **Minimum test/evidence classes:** API/CLI contracts, authorization matrices, end-user workflow tests, raw-state mutation negatives, approval/override audit and restart behavior.
- **Human Review questions:** Can an operator complete governed workflows without internal calls or database edits; are all Human decisions scoped and audited?
- **Exit criteria:** The complete governed workflow is operable through supported interfaces.
- **What becomes authorized after exit:** Stage 12 system-level integration and failure proof.
- **Expected repository artifacts:** Application services, API/CLI, operator-facing schemas, authorization tests, usage documentation and completed plan.

## Stage 12 — End-to-End Integration and Operational Safety

- **Status:** PLANNED.
- **Purpose:** Prove the planes compose safely under normal and adverse conditions.
- **Architectural owner / plane:** Cross-plane system integration and Safety.
- **Entry criteria:** Supported operator workflow and every required plane exist; scenario matrix and failure-injection design accepted.
- **Required deliverables:** Full success path; sandbox/agent recovery; verification arbitration; budget/permission handling; safe Effect commit/observation/remediation; network/substrate failure; idempotent replay; restart/reopen; correlated observability and runbooks.
- **Explicit non-goals:** New major product features, distributed/HA claims and bypassing failures to achieve a green scenario.
- **Major dependencies:** Stages 1–11.
- **Required ADR/design decisions:** System correlation IDs, operational severity/escalation and any cross-plane consistency gaps discovered.
- **Minimum test/evidence classes:** Scenario matrix, destructive/fault injection in safe environments, process restart, replay, invariant monitors, security abuse and runbook drills.
- **Human Review questions:** Do representative failures preserve constitutional invariants, durable truth and safe Effect behavior?
- **Exit criteria:** Required scenario families pass with traceable evidence and no release-blocking cross-plane safety gap.
- **What becomes authorized after exit:** Stage 13 production hardening and release engineering.
- **Expected repository artifacts:** End-to-end suite, observability correlation, operational runbooks, safety findings and completed plan.

## Stage 13 — Production Hardening and Release Engineering

- **Status:** PLANNED.
- **Purpose:** Make the accepted single-node v1 scope installable, supportable, secure and reproducible.
- **Architectural owner / plane:** Cross-cutting operations, security and release engineering.
- **Entry criteria:** End-to-end behavior accepted; deployment scope and release/security policies approved.
- **Required deliverables:** Packaging/install, configuration validation, migration policy, backup/restore, secrets boundary, logs/metrics/traces, security/dependency gates, CI release gates, artifacts/SBOM, resource baselines, crash durability, runbooks and upgrade/rollback.
- **Explicit non-goals:** Unimplemented distributed or HA guarantees, uncontrolled auto-upgrade and feature expansion.
- **Major dependencies:** Stages 1–12.
- **Required ADR/design decisions:** Supported deployment, configuration/secrets, schema compatibility, artifact signing/SBOM, support and compatibility policies.
- **Minimum test/evidence classes:** Clean install, migration and rollback, backup restore, crash/restart, security scans, dependency review, performance/load limits and reproducible build checks.
- **Human Review questions:** Are supported environments and limits honest; can operators recover data and rollback safely; are release artifacts reproducible?
- **Exit criteria:** No known production-readiness blocker for the accepted v1 scope; release gates and operational procedures pass.
- **What becomes authorized after exit:** Stage 14 scope freeze and release-candidate acceptance.
- **Expected repository artifacts:** Packaging/release configuration, SBOM/artifacts, deployment docs, runbooks, baselines and completed plan.

## Stage 14 — v1.0 Release Candidate and Final Delivery

- **Status:** PLANNED.
- **Purpose:** Freeze, verify, document and obtain Human acceptance for the first complete delivery.
- **Architectural owner / plane:** Human Governance with cross-plane release ownership.
- **Entry criteria:** Stage 13 accepted; v1 scope frozen; release-candidate TaskSpecs and final review plan approved.
- **Required deliverables:** Install/setup, operator and contributor guides, architecture/security review, end-to-end acceptance matrix, known limitations, migration/backup/restore docs, examples, release notes, version/tag rules, metadata/license audit and reproducible candidate artifacts.
- **Explicit non-goals:** Major new features, silent scope expansion and release publication without explicit Human authorization.
- **Major dependencies:** Stages 0–13.
- **Required ADR/design decisions:** Final compatibility/versioning and any release-blocking architecture/security remediation; no late decision may bypass higher authority.
- **Minimum test/evidence classes:** Fresh-clone install, complete governed workflow, release reproduction, documentation drills, security review, acceptance matrix and critical-defect audit.
- **Human Review questions:** Can a fresh maintainer operate the system from repository docs alone; are all critical constitutional/security findings resolved; are artifacts reproducible?
- **Exit criteria:** `v1.0 Human Acceptance = ACCEPTED`, critical documentation complete, reproducible artifacts, and no unresolved release blocker.
- **What becomes authorized after exit:** A separate explicitly authorized remote Effect may create the v1.0 tag/release; post-v1 planning may begin.
- **Expected repository artifacts:** Final guides, acceptance/security reports, release notes, reproducible artifacts and completed Stage 14 plan.

## Final delivery definition

A fresh maintainer can clone the repository, install the supported v1
deployment, submit and govern bounded Objectives, execute work through sandboxed
interchangeable AgentDrivers, independently verify Outcomes, recover from
bounded failures, control external Effects, inspect complete audit history, and
operate the system using repository documentation alone.

## Post-v1 backlog — non-blocking

- **Status:** POST-V1.
- **Candidates:** Distributed workers, remote sandboxes, microVMs, GPU/local-model pools, advanced scheduling, richer UI, organization/multi-tenancy, external tracker adapters, self-hosted policy analytics, evidence-supported learned routing, HA clustering and additional specialized AgentDrivers.
- **Governance:** These items are not v1 blockers and require Human roadmap amendment plus their own ADRs, plans and durable TaskSpecs before implementation.
