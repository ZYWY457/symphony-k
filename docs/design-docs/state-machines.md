# Core Domain State Machines

**Version:** 0.2 Stage 1 design baseline, accepted 2026-09-06

Final terminology cleanup preserves this baseline's 43 states and 99-edge topology. Evaluation arbitration uses ARBITRATED / EvaluationArbitrated; Effect quarantine uses QUARANTINED / EffectQuarantined.

**Status:** Accepted by explicit human architecture review.

**Scope:** [Stage 1 / Issue #1](https://github.com/ZYWY457/symphony-k/issues/1) produced this design specification without implementation. The human decision **"Human Architecture Review: ACCEPTED"** now accepts this baseline, [ADR-0005](../adr/0005-core-state-machine-semantics.md), and the [Stage 1 Exec Plan](../exec-plans/active/stage-01-domain-kernel.md). Implementation is authorized only within that plan and the accepted repository hierarchy. Plan acceptance is not a declaration that Stage 1 implementation is complete.

**Approved baseline:** 43 core states; 99 legal transition edges; ARBITRATED Evaluation and QUARANTINED Effect semantics; Effect occurrence separate from authorization/governance truth; Evaluation conflict-set semantics; TaskProposal deferred to Stage 9; no constitutional amendment required.

## 1. Governing Sources and Review Boundary

Read in the hierarchy established by [CONSTITUTION.md](../../CONSTITUTION.md) section 3: Constitution v0.1; all seven [core-belief documents](../README.md); accepted [ADRs 0001–0004](../adr/README.md); [ARCHITECTURE.md](../../ARCHITECTURE.md); approved designs; Exec Plan; Issue. [AGENTS.md](../../AGENTS.md), [VISION.md](../../VISION.md), and [ROADMAP.md](../../ROADMAP.md) provide navigation, intent, and staging context.

The architectural interpretations below are recorded in accepted [ADR-0005](../adr/0005-core-state-machine-semantics.md) and remain subordinate to higher-level documents. No constitutional change is needed. This specification defines domain behavior; acceptance authorizes bounded Stage 1 implementation, not later-stage execution, verification, recovery, Effects, agents or UI runtimes.

## 2. Rules Shared by Every Table

These are closed transition relations. Each comma-separated source denotes a separate edge with the same destination, authority, guards, and event. `NONE` denotes creation, not an additional entity state. No other edge, including a self-loop, is legal. The guards in this section apply to **every** row in addition to its local guards.

1. Authenticate the initiating principal and verify a scoped grant for the entity and action. A caller-supplied actor type is insufficient. Record requester identity separately from the authority making the decision and the transition service applying it. A worker request is data; only a separately authorized decision can change state.
2. Load authoritative source state, expected version, immutable relationships, relevant policy version, evidence and decision references. Creation requires a fresh identifier, valid relationships, and an authorized creator. Grants and evidence must concern the same target, artifact/payload, and applicable version.
3. Reject missing, stale, conflicting, or insufficient guard inputs. Human policy waivers must be explicit, scoped, versioned and audited. Neither a waiver nor break-glass bypasses the Constitution, independent validation, facts, or provenance.
4. Check the source/destination edge, authority, separation of duties, and all guards. Commit the new projection/version and exactly one corresponding lifecycle event atomically. Creation emits its creation event with prior state `NONE`. Preserve previous versions' historical meaning. This specifies observable behavior, not an event-sourcing implementation.
5. Each event contains the Exec Plan section 22 fields: event ID/type, entity type/ID/version, actor ID/type, timestamp, correlation ID, causation ID, reason and metadata. Also retain prior/new state, policy/authorization references, evidence references, and initiating request when present. Arbitration and policy override records are additional records, not substitutes for the lifecycle event.
6. A failed guard or stale version leaves authoritative state and its version unchanged and emits no success event. An attributable `TransitionRejected` audit record may be appended separately; it cannot imply a successful mutation. Identical retried requests return the prior result without a second transition/event; reuse of that request identity for different content is rejected.
7. A parent/child relationship does not execute another entity's transition. Completion and start decisions use a consistent, version-checked view of dependencies and grants; a concurrent invalidation must cause re-evaluation rather than acceptance using stale evidence. Multi-entity operations preserve links and audit atomically where necessary. No database transaction is claimed to make external effects atomic.

Effect observation actions require authority to record evidence, not proof of prior authority to perform the observed mutation. Missing execution authorization or unknown historical attribution is recorded explicitly, not treated as a reason to suppress reality. This distinction applies to shared guards 1–3 and the creation rule. Observation-only creation uses EffectCommitted or EffectQuarantined with prior state NONE; it does not fabricate an earlier EffectPlanned event.

### Authority notation

`O` = scoped Objective authority: REQUESTER, SCHEDULER, POLICY_ENGINE, or HUMAN_OPERATOR. `T` = scoped Task authority: REQUESTER, SCHEDULER, POLICY_ENGINE, or HUMAN_OPERATOR. These are eligibility sets, not blanket grants. The designated Objective acceptance authority is additionally required for satisfaction; Task completion needs a policy decision.

`R` = SCHEDULER or RUN_CONTROLLER. Recovery Controller decisions are carried through `R`; they do not create a worker permission or require a new actor category. Authorized human abort/redirect requests also go through `R`.

`V` = independent EVALUATOR. `A` = ARBITRATOR or HUMAN_OPERATOR with target-scoped arbitration authority. `C` = SCHEDULER or POLICY_ENGINE coordinating Outcome lifecycle; acceptance/rejection additionally requires an independent validation decision, and human acceptance where policy requires it. `E` = EFFECT_CONTROLLER, the sole Effect lifecycle boundary in this baseline. Human/system instructions reach it as requests or authorizations.

### Request versus authoritative decision matrix

`Q` means request/input only and never a lifecycle decision. `D` means eligible to authorize the indicated action, subject to the row guards and scoped grants. The transition service applies all authorized decisions; no actor edits raw state. A dash means no authority in this baseline. All D actors may also submit requests within their scope.

| Actor | Objective | Task | Run | Outcome | Evaluation | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| REQUESTER | D: O | D: T | Q: start/stop | Q: candidate review | Q: verification | Q: intent |
| SCHEDULER | D: O | D: T | D: R | D: C | D: request creation; Q otherwise | Q: preparation/commit |
| RUN_CONTROLLER | Q: progress | Q: progress | D: R | Q: register candidate | Q: verification | Q: intent |
| WORKER | Q only | Q only | Q only | Q: propose only | Q: evidence only | Q: intent only |
| EVALUATOR | Q: evidence | Q: evidence | Q: verification input | Q: independent verdict to C | D: V | Q: verify only; cannot commit same Effect |
| ARBITRATOR | Q: judgment | Q: judgment | Q: recovery advice | Q: arbitration decision to C | D: A | Q: dispute resolution |
| EFFECT_CONTROLLER | Q: receipt | Q: receipt | Q: receipt | Q: evidence | Q: independent verification | D: E |
| POLICY_ENGINE | D: O | D: T | Q: policy decision to R | D: C | Q: request/checks | Q: policy authorization to E |
| HUMAN_OPERATOR | D: O, scoped acceptance | D: T | Q: abort/redirect to R | Q: required acceptance/arbitration to C | D: A | Q: authorization to E, mandatory for irreversible commit |
| SYSTEM | Q: authenticated service input | Q | Q | Q | Q | Q |

`SYSTEM` is not a superuser. A system component needs a separately authenticated, explicitly granted controller role to make a decision. The same restriction applies to a human wishing to operate a controller boundary. Separation checks use principal/component identity and provenance, not just role names: an Effect evaluator cannot commit that Effect by switching labels, and a producing worker cannot become its independent validator.

E's scope distinguishes observation/incident recording from external execution. The former can register an unauthorized occurrence without performing it. An evaluator or worker can submit incident evidence only; neither obtains an authoritative lifecycle path or external execution permission.

## 3. Objective

States: `DRAFT`, `ACTIVE`, `BLOCKED`, `SATISFIED`, `FAILED`, `CANCELLED`, `EXPIRED`, `ARCHIVED`.

| From | To | Authority | Required Guards | Event |
| --- | --- | --- | --- | --- |
| NONE | DRAFT | O | Bounded goal; acceptance criteria, designated acceptance authority and completion-policy reference recorded | ObjectiveCreated |
| DRAFT | ACTIVE | O | Definition and governance approved; applicable budget, permissions and time horizon valid | ObjectiveActivated |
| ACTIVE | BLOCKED | O | Explicit current blocker recorded; Objective remains valid | ObjectiveBlocked |
| BLOCKED | ACTIVE | O | All blocking conditions resolved; activation eligibility rechecked | ObjectiveActivated |
| ACTIVE, BLOCKED | SATISFIED | O | Current Objective Completion Policy passes on independent evidence; designated acceptance authority accepts; completion blockers resolved or lawfully waived | ObjectiveSatisfied |
| ACTIVE, BLOCKED | FAILED | O | Evidence-backed decision that goal cannot be achieved under accepted constraints | ObjectiveFailed |
| DRAFT, ACTIVE, BLOCKED | CANCELLED | O | Authorized withdrawal/termination decision | ObjectiveCancelled |
| DRAFT, ACTIVE, BLOCKED | EXPIRED | O | Recorded validity horizon has elapsed using authoritative time; no valid extension | ObjectiveExpired |
| SATISFIED, FAILED, CANCELLED, EXPIRED | ARCHIVED | O | Retention/archival decision; prior disposition and dependent records retained | ObjectiveArchived |

`SATISFIED`, `FAILED`, `CANCELLED`, and `EXPIRED` close active work and have only the archival exit. `ARCHIVED` is a strict sink. Archival neither deletes evidence nor hides unresolved Effect obligations. A later dispute about satisfaction appends evidence and a review/corrective-work decision; it does not reopen the historical Objective.

Forbidden: `DRAFT -> SATISFIED`, `ACTIVE -> ARCHIVED`, `SATISFIED -> ACTIVE`, and any percentage/child-count-driven satisfaction. Cancellation or expiry records the Objective disposition; it does not assert that its Runs stopped or its Effects disappeared.

## 4. Task

States: `DRAFT`, `READY`, `IN_PROGRESS`, `BLOCKED`, `COMPLETED`, `FAILED`, `CANCELLED`.

| From | To | Authority | Required Guards | Event |
| --- | --- | --- | --- | --- |
| NONE | DRAFT | T | Exactly one existing primary Objective; bounded definition and provenance recorded | TaskCreated |
| DRAFT | READY | T | Definition/governance approved; completion policy defined; dependencies, budget and permissions pass; primary Objective ACTIVE | TaskReadied |
| DRAFT, READY, IN_PROGRESS | BLOCKED | T | Identified dependency, authorization, input or external blocker | TaskBlocked |
| BLOCKED | READY | T | Blockers resolved; readiness guards pass; no still-active execution ownership to resume | TaskReadied |
| READY | IN_PROGRESS | T | Primary Objective ACTIVE; authorized linked Run or execution-control ownership recorded; readiness guards remain valid | TaskStarted |
| BLOCKED | IN_PROGRESS | T | Blockers resolved; primary Objective ACTIVE; prior execution-control ownership remains valid | TaskStarted |
| IN_PROGRESS, BLOCKED | COMPLETED | T | Current Task Completion Policy passes on independent evidence; required acceptance/effects/risks checked; completion blockers resolved or lawfully waived | TaskCompleted |
| READY, IN_PROGRESS, BLOCKED | FAILED | T | Recorded failure evidence; permitted recovery exhausted or ruled out by scoped decision | TaskFailed |
| DRAFT, READY, IN_PROGRESS, BLOCKED | CANCELLED | T | Authorized termination decision; continuing execution is no longer authorized | TaskCancelled |

`COMPLETED`, `FAILED`, and `CANCELLED` are strict sinks. There is no Task archival, retry, or expiry state. Deadline expiry is a reason for a policy-controlled block/failure/cancellation, not an invented enum. New work after closure needs a new Task with explicit provenance. A Task blocked before any Run returns through READY; a Task still owned by execution control may resume IN_PROGRESS.

Forbidden: `DRAFT -> IN_PROGRESS`, `READY -> COMPLETED`, `FAILED -> READY`, and `IN_PROGRESS -> COMPLETED` merely because a Run ended. A terminal parent prevents new starts; it does not prevent collection of late evidence or recording a Task's final disposition. Cancellation revokes starts/continuations/commits, while individual Run aborts remain separately attributed transitions. A Task cancellation is not proof of physical process termination.

## 5. Run

States: `PENDING`, `RUNNING`, `WAITING_FOR_VERIFICATION`, `RETRYING`, `REASSIGNED`, `COMPLETED`, `FAILED`, `ABORTED`.

| From | To | Authority | Required Guards | Event |
| --- | --- | --- | --- | --- |
| NONE | PENDING | R | Exactly one Task; Task READY or IN_PROGRESS; Objective ACTIVE; attempt identity and execution-profile reference recorded | RunCreated |
| PENDING | RUNNING | R | Task IN_PROGRESS with execution ownership; Objective ACTIVE; approved sandbox/profile, grants and budget valid; trusted start confirmation | RunStarted |
| RUNNING | WAITING_FOR_VERIFICATION | R | Execution stopped; at least one linked candidate Outcome and evidence references durably recorded; verification requested | RunWaitingForVerification |
| RUNNING | RETRYING | R | Recoverable interruption; same attempt/path/strategy remains trustworthy; recovery decision, trusted recovery boundary and remaining limits recorded | RunRetrying |
| RETRYING | RUNNING | R | Same attempt continuity validated; trusted checkpoint reference and grants valid; Task IN_PROGRESS and Objective ACTIVE; approved execution boundary | RunStarted |
| PENDING, RUNNING, WAITING_FOR_VERIFICATION, RETRYING | REASSIGNED | R | Current ownership stopped/fenced; profile unsuitable; authorized, durable successor Run or accepted human handoff reference; transfer cannot duplicate execution authority | RunReassigned |
| RUNNING | COMPLETED | R | Independently observed normal termination and artifacts/usage persisted; no Run-level verification wait required by policy | RunCompleted |
| WAITING_FOR_VERIFICATION | COMPLETED | R | Required verification process resolved, including an unfavorable verdict; evidence retained; execution otherwise closed normally | RunCompleted |
| PENDING, RUNNING, WAITING_FOR_VERIFICATION, RETRYING | FAILED | R | Attempt cannot continue on its recovery path; failure class/evidence recorded; execution ownership ended/fenced | RunFailed |
| PENDING, RUNNING, WAITING_FOR_VERIFICATION, RETRYING | ABORTED | R | Scheduler/policy/safety/authorized-human stop decision; execution ownership ended/fenced | RunAborted |

`REASSIGNED`, `COMPLETED`, `FAILED`, and `ABORTED` are strict sinks for this Run identity. `RETRYING` is a live recovery preparation state, not a new attempt or proof of successful recovery. Resume can continue the same Run through RETRYING. Rewind that abandons a path closes the prior attempt as FAILED or ABORTED and creates a new PENDING Run with trusted-checkpoint/predecessor references. Reassign closes the old Run with a durable transfer; replacement execution starts as a new Run. A later recovery after FAILED/ABORTED creates a new Run without rewriting the old closure.

The same-strategy phrase does not allow distinct attempts to share identity. Adapter session IDs do not define Run identity. Recovery algorithms and checkpoint storage remain deferred; Stage 1 later validates domain references and decisions using fixtures.

`WAITING_FOR_VERIFICATION` records a Run-level wait, not acceptance. An Outcome may stay PROPOSED/VALIDATING after a direct normal Run completion. Verification rejection alone need not make an otherwise normally terminated Run FAILED. A verification infrastructure timeout can produce a classified Run failure when policy requires that gate; it must not fabricate an unfavorable Outcome verdict.

Forbidden: worker-triggered authoritative completion; `PENDING -> COMPLETED`; `FAILED -> RUNNING`; `REASSIGNED -> RUNNING`; `WAITING_FOR_VERIFICATION -> RUNNING` to overwrite the rejected attempt; completion that automatically accepts any Outcome. A fenced Run cannot publish further authoritative changes using stale worker credentials; late reports are evidence requests for controller reconciliation.

## 6. Outcome

States: `PROPOSED`, `VALIDATING`, `ACCEPTED`, `REJECTED`, `SUPERSEDED`, `EXPIRED`.

| From | To | Authority | Required Guards | Event |
| --- | --- | --- | --- | --- |
| NONE | PROPOSED | C | Candidate from an identified Run; immutable artifact/evidence references and producing identity; worker proposal registered as a claim | OutcomeProposed |
| PROPOSED | VALIDATING | C | Explicit validation target/artifact version, policy and independent Evaluation request | OutcomeValidationStarted |
| VALIDATING | ACCEPTED | C | Independent validation supports acceptance; no unresolved blocking conflict; current acceptance policy passes; required human acceptance recorded | OutcomeAccepted |
| VALIDATING | REJECTED | C | Independent validation or explicit arbitration supports rejection of this candidate; policy decision recorded | OutcomeRejected |
| PROPOSED, VALIDATING, ACCEPTED, REJECTED | SUPERSEDED | C | Distinct existing replacement Outcome for same Task and acceptance scope; replacement link acyclic; ACCEPTED source requires ACCEPTED replacement | OutcomeSuperseded |
| PROPOSED, VALIDATING, ACCEPTED, REJECTED | EXPIRED | C | Evidence of stale assumptions, dependencies or validity horizon; stale-input decision recorded | OutcomeExpired |

`ACCEPTED` and `REJECTED` close the initial judgment but permit supersession or expiry only. `SUPERSEDED` and `EXPIRED` are strict sinks. Supersession preserves the original originating Run; a new candidate may originate in another Run of the same Task. It does not mutate the candidate's artifacts. Acceptance is about the exact candidate and recorded evidence, not permanent universal truth.

A challenged verdict is handled by appended Evaluation/arbitration records. Reconsideration produces a distinct candidate record with explicit originating-Run and prior-candidate provenance and fresh validation. Newly invalid assumptions may expire an accepted candidate. There is no silent ACCEPTED/REJECTED toggle. Downstream completion policies read current eligible Outcomes and relevant disputes; prior Task/Objective completion events remain historical.

Forbidden: `PROPOSED -> ACCEPTED`, worker acceptance, `ACCEPTED -> REJECTED`, `EXPIRED -> ACCEPTED`, supersession cycles, or expiry used merely because validation infrastructure failed. Conflicted validation keeps the Outcome VALIDATING until arbitration, supersession, or independently justified expiry; no extra Outcome CONFLICTED state is needed.

## 7. Evaluation

States: `PENDING`, `RUNNING`, `COMPLETED`, `CONFLICTED`, `ARBITRATED`, `INVALID`.

An Evaluation has immutable recorded content and an effective lifecycle projection. Appending completion content is allowed once; previously recorded evidence, method, verdict, confidence, reasoning summary and provenance are never replaced. Later lifecycle events reference those records. No physical delete is available through normal operation.

| From | To | Authority | Required Guards | Event |
| --- | --- | --- | --- | --- |
| NONE | PENDING | SCHEDULER or V | Explicit existing target and artifact/version scope; validation method/policy and independent verifier assignment or assignment requirement | EvaluationRequested |
| PENDING | RUNNING | V | Verifier assigned, independent of target execution; required inputs available and anchored | EvaluationStarted |
| RUNNING | COMPLETED | V | Append valid verdict, method, confidence, reasoning summary, evidence and provenance; no known material unresolved conflict | EvaluationCompleted |
| RUNNING, COMPLETED | CONFLICTED | V or A | Append conflict-set identity/version, all affected member IDs/versions, target/scope, disagreement/evidence and correlation; project every affected participant consistently; retain original content | EvaluationConflicted |
| COMPLETED, CONFLICTED | ARBITRATED | A | Append scoped arbitration with arbitration_disposition (e.g. UPHELD, MODIFIED, REVERSED), prior/effective judgment, rationale, policy, actor and original Evaluation reference; for conflict members record set/version and member dispositions, and resolve every applicable conflict affecting this member before releasing its effective use | EvaluationArbitrated |
| PENDING, RUNNING, COMPLETED, CONFLICTED | INVALID | V or A | Evidence/provenance/method defect or verifier failure established; append invalidation reason/evidence; retain any recorded result | EvaluationInvalidated |

`COMPLETED` closes verification work but allows conflict, arbitration or invalidation. `CONFLICTED` awaits resolution by a new arbitration record (ARBITRATED) or proven invalidity (INVALID). `ARBITRATED` and `INVALID` are strict sinks for this Evaluation projection. Further challenges append a new Evaluation/decision referencing the old one, including the arbitration if challenged. Re-running verification creates a new Evaluation.

Arbitration of a still-CONFLICTED record need not invent a prior valid verdict: it records the prior effective conflict and the resulting decision. Separately append arbitration_disposition, such as UPHELD, MODIFIED or REVERSED, with the effective judgment. UPHELD preserves the original verdict; MODIFIED or REVERSED specifies the changed effective judgment without editing original content. If the decision still cannot establish acceptance, the Outcome remains VALIDATING. Arbitration cannot cure corrupted evidence by assertion or waive independent validation. Dispositions qualify the decision and are not additional Evaluation states.

### Conflict-set semantics

A material disagreement is a correlated set, not a flag on the detecting Evaluation alone. Record a stable conflict-set ID, version, member Evaluation IDs and observed versions, affected target/artifact/acceptance scope, disagreement/evidence references, detecting authority, timestamp and correlation ID. Preserve membership history through appended records. Different targets may participate when evidence establishes a common affected acceptance scope; mere disagreement on unrelated targets is insufficient.

Every RUNNING or COMPLETED participant whose effective use is affected transitions to CONFLICTED. Include existing CONFLICTED participants in the same set through appended membership records, without a self-transition or duplicate EvaluationConflicted event. Membership, all newly affected projections, and one lifecycle event per actual transition are committed atomically with version checks in the future kernel. Stale members reject the whole update; acceptance readers cannot observe a partial set. A later discovered affected member extends the set through a new version using the same rule. Conflicting evidence is deliberately retained, not rejected by shared guard 3 as if it were a malformed conflict-registration request.

PENDING has no verdict to conflict; any applicable open set must be considered when its result is later recorded. INVALID and ARBITRATED original verdicts are not eligible effective inputs and need not be revived; they may remain supporting evidence references. If an arbitration decision is challenged, create linked review/Evaluation records for that effective decision and correlate the dispute to the original set. Block acceptance while it remains unresolved.

Arbitration appends a set/version-linked decision with all affected members, their arbitration_disposition values and prior/effective judgments. Members remain CONFLICTED while any applicable set remains unresolved; no first-member-only resolution can silently release the rest. Fully addressed members may transition to ARBITRATED with UPHELD, MODIFIED or REVERSED disposition: the state records arbitration, while the appended disposition describes its effect on the original verdict. Proven-invalid members may transition to INVALID and remain unusable, with their membership history preserved; this alone does not resolve disagreement among remaining members. The existing edges suffice; no new state, self-loop or top-level conflict entity is introduced.

Forbidden: `COMPLETED -> RUNNING`, `CONFLICTED -> COMPLETED` by overwriting a verdict, `INVALID -> COMPLETED`, worker override, or deletion/editing of original Evaluation content. INVALID means unusable verification, not an unfavorable result: a valid negative verdict is a COMPLETED Evaluation.

## 8. Effect

States: `PLANNED`, `SIMULATED`, `PENDING_COMMIT`, `COMMITTED`, `ROLLED_BACK`, `COMPENSATING`, `COMPENSATED`, `QUARANTINED`.

`E` records domain transitions; no real action occurs in Stage 1. A domain transition alone never creates proof of an external fact. Later runtime integration must carry receipts/observations and authorization through this boundary.

`COMMITTED` means independently confirmed external occurrence. Authorization, policy compliance and safety incidents are separate appended records; a known unauthorized occurrence is still COMMITTED. It does not remain QUARANTINED merely because a governance investigation is open.

`QUARANTINED` means the Effect has left the normal automatic execution path because of uncertain occurrence, incident handling, unsafe remediation state, rollback/compensation uncertainty, or another condition requiring controlled reconciliation. It describes execution-path exclusion, not whether occurrence or an incident is unresolved. Preserve occurrence_status, incident_status and authorization findings separately in appended facts/metadata with evidence. These are not new lifecycle states or domain entities. Entry and exit still require one of the table's existing edges and its guards; this definition adds no wildcard edge.

**Execution guards:** Normal execution retains Prepare–Verify–Authorize–Commit. Before dispatch, require independently validated exact target/payload, Task execution eligibility, scoped current grants, budget/policy checks, idempotency controls, and a committing principal/component distinct from every evaluator of that Effect. Explicit human authorization is mandatory before irreversible action, including irreversible remedies. An expired/revoked authorization cannot be reused. PENDING_COMMIT alone does not grant permission. Stage 1 specifies these decisions/guards; no executor is implemented.

**Observation guards (OG):** Scoped E recording authority; independently anchored external operation/target identity and evidence; observer, recording actor, observation time and occurrence time when known; correlation/incident and deduplication references; explicit known/unknown Task/Run attribution; and separately recorded authorization/policy findings with their evidence. Confirmation requires evidence establishing occurrence, not only a worker claim. Suspected occurrence requires an anchored report/observation and explicit uncertainty, not a fabricated fact. Do not invent payload, actor, timestamps or authorization when unknown. Deduplicate against registered Effects and route later observations to the same identity; repeats append evidence without duplicating occurrence or a lifecycle event.

All transitions into COMMITTED record observed occurrence; none dispatches an action. In the normal flow, authorized dispatch precedes the observation. Exceptional ingestion can record a mutation that bypassed that flow without granting retrospective permission. These operations must be distinct from execution requests so an observation cannot invoke an executor. New unregistered observations may remain unlinked as specified in section 9; missing execution authorization, a cancelled parent or unknown attribution cannot prevent factual recording. Observed governance violations are appended separately and escalated; confirmed occurrence need not await a completed policy investigation.

| From | To | Authority | Required Guards | Event |
| --- | --- | --- | --- | --- |
| NONE | PLANNED | E | Intent, Task, optional producing Run, target/payload identity, reversibility, risk and required authorization recorded | EffectPlanned |
| NONE, PLANNED, SIMULATED | COMMITTED | E | Observation only: OG; independent evidence confirms external occurrence, including unauthorized occurrence; preserve preparation history if present; no action dispatched | EffectCommitted |
| NONE, PLANNED, SIMULATED | QUARANTINED | E | Observation only: OG; supported suspicion with uncertain occurrence; record unknown-original-commit context, no fabricated dispatch/authorization, no action or blind retry | EffectQuarantined |
| PLANNED | SIMULATED | E | Preparation/dry-run evidence without the proposed real mutation; preparation scope recorded | EffectSimulated |
| PLANNED, SIMULATED | PENDING_COMMIT | E | Independent pre-commit validation passed; payload fixed; rollback/compensation plan or reason unavailable; idempotency/deduplication strategy; bypassing simulation justified when impractical | EffectPendingCommit |
| PENDING_COMMIT | COMMITTED | E | Observation only: OG; receipt/independent observation establishes occurrence after normal dispatch or incident; record known/unknown/violating authorization separately; no action dispatched | EffectCommitted |
| PENDING_COMMIT | QUARANTINED | E | OG; dispatch may have reached external system or an incident is suspected and occurrence remains uncertain; preserve known dispatch/authorization references or explicitly unknown attribution; prohibit blind retry | EffectQuarantined |
| COMMITTED | ROLLED_BACK | E | Genuinely reversible change; authorized restoration and independent evidence prior state actually restored; original commit retained | EffectRolledBack |
| COMMITTED | COMPENSATING | E | Authorized compensating action with explicit linked governed Effect(s); original mutation cannot be truthfully erased | EffectCompensationStarted |
| COMMITTED, COMPENSATING | QUARANTINED | E | Post-commit problem, failed/uncertain rollback or compensation, or no safe remedy; retain known commit and last attempted operation context | EffectQuarantined |
| COMPENSATING | COMPENSATED | E | Independently evidenced completion of all required linked compensation actions; residual impact recorded | EffectCompensated |
| QUARANTINED | PENDING_COMMIT | E | Only unknown-original-commit context; independent reconciliation proves non-occurrence and no in-flight mutation; separately governed intent, verified Task association and full preparation/validation eligibility required; incident record alone confers no eligibility; new action requires valid authorization | EffectPendingCommit |
| QUARANTINED | COMMITTED | E | Observation only: OG; unknown-original-commit or post-commit-verification context reconciled by independent evidence of occurrence; prior authorization need not exist; keep governance findings separate; never execute again | EffectCommitted |
| QUARANTINED | ROLLED_BACK | E | Known original commit; reversible restoration established independently; uncertain remedial operations reconciled; commit history retained | EffectRolledBack |
| QUARANTINED | COMPENSATING | E | Original commit established; reconciliation excludes duplicated/in-flight compensation; safe authorized remaining compensation with linked Effect references | EffectCompensationStarted |
| QUARANTINED | COMPENSATED | E | Known original commit; previously attempted authorized compensation independently confirmed complete; full action chain retained | EffectCompensated |

`ROLLED_BACK` and `COMPENSATED` are strict sinks of this disposition; any later problem is recorded through new linked evidence/Effects and governance, not by erasing the prior disposition. `COMMITTED` closes the original mutation but permits the remedial exits above. `QUARANTINED` may remain indefinitely, including after an incident is closed; it neither asserts unknown occurrence nor grants automatic execution eligibility. Its context must distinguish occurrence facts, incident handling, post-commit verification, rollback and compensation problems. Edges requiring a known commit are forbidden until evidence establishes one, even when current state is QUARANTINED. Preserve the chronological commit observation before any remedy disposition, including discoveries made during reconciliation.

Registration of an unauthorized occurrence appends governance/safety findings alongside its factual observation. Record the assessed authorization evidence or explicit unknown status, policy references, violation/review findings, responsible principal when known, and incident correlation. Update an investigation by new findings; never backfill a grant as if it existed before the action. COMMITTED is not policy approval, desired-state verification, or sufficient evidence of Task/Objective completion. Unresolved governance issues remain visible to completion-policy and safety checks independently of the occurrence state.

If a suspected occurrence is disproved, it may remain QUARANTINED with appended occurrence_status=DISPROVED and incident_status=CLOSED, backed by the non-occurrence finding and incident-closure record. This explicitly records known non-occurrence without implying continuing uncertainty. Preserve authorization truth separately; incident closure grants no permission to dispatch. QUARANTINED -> PENDING_COMMIT is available only with the separate intent and eligibility guards above. Metadata updates append facts without lifecycle self-transitions. Repeated reports for an already COMMITTED or terminal Effect append evidence/findings without state regression.

There is no `CANCELLED`/`FAILED` Effect state. An intent withdrawn before dispatch stays at its preparation state with a recorded withdrawal/revocation decision; execution guards then fail, but incident observation remains permitted. Preparation failure likewise leaves the prior state and appends failure evidence. These are deliberately nonterminal disposition metadata, not rollback or compensation. A commit attempt with unknown outcome goes to QUARANTINED, never back to PLANNED. Real commit-in-flight protocol design remains Stage 6 work.

Forbidden: using observation-only `NONE/PLANNED/SIMULATED -> COMMITTED/QUARANTINED` edges to dispatch actions or bypass normal preparation/validation/authorization; simulation counted as actual occurrence; worker/evaluator external commitment; irreversible execution without prior explicit human authorization; `COMMITTED -> PLANNED`; direct `COMMITTED -> COMPENSATED` skipping the compensation record; `COMPENSATED -> ROLLED_BACK`; or `QUARANTINED -> PENDING_COMMIT` when any commit or in-flight mutation is possible or governed intent is absent. Rollback restores state but does not delete occurrence. Recording a violation complies with history preservation; it does not make the violating action constitutionally permissible.

## 9. Relationships and Cross-Entity Guards

| Relationship | Review decision and constraint |
| --- | --- |
| Task -> Objective | Exactly one existing primary Objective, including DRAFT Tasks; immutable ownership for this baseline. Changing ownership needs separately reviewed governance, not a free-form field update. |
| Task -> secondary Objectives | Zero or more existing contribution links; no ownership, budget authority, or automatic state propagation. |
| Run -> Task | Exactly one immutable existing Task; multiple Runs allowed; a successor references its predecessor without replacing it. |
| Outcome -> Run | Exactly one immutable originating Run, with candidate artifact and producer provenance. Multiple Outcomes per Run allowed; a late candidate may be registered after Run closure if independently anchored to that Run. |
| Evaluation -> target | Exactly one explicitly typed existing primary target: Run, Outcome, Effect, or anchored evidence; additional supporting references allowed. Capture the target content/version being evaluated. Evaluation independence checks traverse the producing Run/Effect provenance. |
| Effect -> Task / Run | Planned execution requires exactly one accountable Task; optional originating Run belongs to that Task. Observation-only incidents may initially have no verified Task/Run link: record external identity, evidence provenance and an explicit unlinked reason. Append later verified associations without rewriting initial unknown attribution or inventing a producing Run. No execution eligibility until Task ownership and normal guards exist. Task-level Effects remain allowed. |
| Evaluation -> conflict set | Explicit versioned correlation/membership record with all affected Evaluations, target scope and evidence; no free-form-only association. Preserve prior memberships and per-member decisions. |
| Arbitration / compensation links | Explicit prior Evaluation or original Effect identity; distinct record IDs; no dangling references, self-reference or cycles in replacement chains. Compensation is linked governed work, not an edit to the original payload. |

The Evaluation target details, conflict membership and Effect attribution make the topology concrete without adding top-level entities. Storage schemas remain out of scope. TaskProposal representation, lifecycle, generation and governance implementation belong to Stage 9 (Planner), outside Stage 1. TaskProposal is planning input and never directly executable; governance creates a separate Task. This boundary does not waive governance for Tasks created without a Planner in Stage 1.

Completion Policy evaluation records policy identity/version, exact target/dependency versions, independent evidence references, decision authority, pass/fail and unmet conditions. A worker Boolean or a caller-supplied `policy_passed` flag is insufficient. Required Task Outcomes, Effects, Evaluations and absence of blocking risk are evaluated for their applicable scope. If human acceptance is required, its scoped decision must also be recorded. No general policy language is introduced.

Parent cancellation/expiry blocks future starts and new external execution; controllers still collect historical observations, abort Runs, and govern authorized remediation. An in-flight external mutation may complete after cancellation, so receipts and factual COMMITTED transitions must remain recordable. No cascade changes an Outcome judgment or destroys an Effect. Closing an Objective does not discharge unresolved external obligations.

## 10. Reachability and Distinct Semantics

Each path below assumes the corresponding authorized actors and guards. Shared prefixes may be reused; all **43** declared states are covered without adding enum values.

| Entity | Witness paths from creation |
| --- | --- |
| Objective (8) | NONE -> DRAFT -> ACTIVE -> BLOCKED -> SATISFIED -> ARCHIVED; ACTIVE -> FAILED; DRAFT -> CANCELLED; DRAFT -> EXPIRED |
| Task (7) | NONE -> DRAFT -> READY -> IN_PROGRESS -> BLOCKED -> COMPLETED; READY -> FAILED; DRAFT -> CANCELLED |
| Run (8) | NONE -> PENDING -> RUNNING -> RETRYING -> RUNNING -> WAITING_FOR_VERIFICATION -> COMPLETED; PENDING -> REASSIGNED with durable handoff; PENDING -> FAILED; PENDING -> ABORTED |
| Outcome (6) | NONE -> PROPOSED -> VALIDATING -> ACCEPTED -> SUPERSEDED with replacement; VALIDATING -> REJECTED; PROPOSED -> EXPIRED |
| Evaluation (6) | NONE -> PENDING -> RUNNING -> COMPLETED -> CONFLICTED -> ARBITRATED; PENDING -> INVALID |
| Effect (8) | NONE -> PLANNED -> SIMULATED -> PENDING_COMMIT -> COMMITTED -> COMPENSATING -> COMPENSATED; COMMITTED -> ROLLED_BACK; PENDING_COMMIT -> QUARANTINED |

| Potential overlap or missing state | Resolution |
| --- | --- |
| Failure vs cancellation/abort vs blocking | Failure records unsuccessful disposition under constraints; cancellation/abort records intentional stop; blocking preserves valid work pending an explicit condition. Task BLOCKED is not Run FAILED. |
| Expiry vs failure | Expiry is loss of validity over time/assumptions for Objectives/Outcomes. Entities without EXPIRED use an attributed policy decision, not a new enum. |
| Retry vs reassignment | RETRYING continues the same trustworthy attempt; REASSIGNED closes a transfer of ownership. Neither asserts successful work. New attempts get new IDs. |
| Run wait vs Outcome validation | The former is execution-control gating; the latter is candidate assessment. Their state changes remain independent. |
| Evaluation process vs judgment | PENDING/RUNNING track work; COMPLETED means a verdict exists, not a positive verdict. CONFLICTED/ARBITRATED/INVALID qualify effective use through appended records. No destructive result-field updates. |
| Arbitration vs reversal | ARBITRATED records arbitration; arbitration_disposition separately records UPHELD, MODIFIED or REVERSED. Upholding a verdict is not mislabeled as an override. |
| Quarantine vs occurrence uncertainty | QUARANTINED excludes automatic execution. occurrence_status=DISPROVED and incident_status=CLOSED may coexist with it; occurrence, incident and authorization truth remain separate. |
| Commit vs authorization or verified desired result | COMMITTED means independently confirmed occurrence, including unauthorized mutation. Authorization/safety findings and required desired-state verification remain separate completion-policy inputs. |
| Missing Effect in-flight / denied / cancelled states | Unknown dispatch is quarantined in QUARANTINED; pre-dispatch denial/withdrawal is recorded metadata with revoked eligibility. A richer process state machine is deferred for evidence from the Stage 6 protocol. |
| Evaluation cancellation or failure state | Verifier failure makes the Evaluation INVALID with reason; an unresolved scheduling request may remain PENDING. Mere negative verdict is COMPLETED. No fabricated rejection to close a queue item. |
| No reopen states for completed work | Historical closure remains fixed; new work, candidates, evaluations and corrective Effects use new linked identities. Objective archive and Outcome supersession/expiry are the explicit post-closure exits. |

## 11. Constitutional Review and Acceptance Evidence

These are design-level checks and future test cases, not claims that a runtime test suite exists or passes.

| Check | Evidence in this specification / negative example |
| --- | --- |
| Worker cannot complete Run, accept Outcome, override Evaluation, commit Effect or mutate any lifecycle | Section 2 authority matrix grants WORKER only Q; every table excludes it from authority. Reject the same request even if it carries a claimed controller label. |
| Worker cannot grant permissions or budget | Shared guard 1 requires external scoped authority; guard 3 disallows self-waiver. Permission/budget requests have no transition edge here. |
| Run completion is distinct from Outcome acceptance | Section 5 allows normal closure with unresolved candidate assessment; later section 6 VALIDATING -> REJECTED does not reopen Run. |
| Task completion is policy-driven | Both incoming COMPLETED edges in section 4 require the Task policy and evidence. RunCompleted alone fails those guards. |
| Objective satisfaction is policy-driven | Both incoming SATISFIED edges in section 3 require Objective policy plus designated acceptance. Child counts and secondary links confer no authority. |
| Evaluation override preserves history | Section 7 requires a separate override record and immutable original verdict; CONFLICTED -> COMPLETED and editing/deleting verdicts are forbidden. |
| Effect rollback differs from compensation | Section 8 requires restoration evidence for ROLLED_BACK and linked compensating actions for COMPENSATED; original commit remains in both histories. |
| Evaluator cannot commit validated Effect | Section 2 identity separation and section 8 common guards reject this even when another verifier exists. |
| Irreversible execution requires human authorization | Section 8 execution guards require prior explicit authorization for the exact action; observation-only edges cannot dispatch actions or grant retrospective permission. |
| Unauthorized reality is recordable | Section 8 registers confirmed/suspected unregistered occurrences and reconciles prepared records; separate governance findings cannot suppress COMMITTED when occurrence is confirmed. |
| All affected Evaluations are conflicted | Section 7 versioned conflict membership, atomic per-member projections/events and set-aware arbitration prevent acceptance using an unaffected-looking participant. |
| Relationships and survival | Section 9 freezes primary ownership and provenance; shared rules retain historical records independently of workers and sandbox lifetime. |
| Human override cannot rewrite facts | Shared guard 3 and sections 7–8 retain old records; human decisions cannot erase commit evidence or invent a prior authorization. |
| Atomicity and concurrent updates | Shared rules 4–7 require version checks and state/event atomicity; stale or failed commands cannot emit success or partially update state. |

| Issue acceptance criterion | Review artifact |
| --- | --- |
| All six explicit transition matrices; authority, guards and events for every legal transition | Sections 2–8; closed relations include creation and all permissible outgoing edges. |
| Important illegal transitions | Each entity section plus default denial in section 2. |
| Every state reachable or justified | Section 10 witness paths for all 43 states. |
| Unambiguous terminal behavior | Each entity section distinguishes strict sinks from post-closure archival/supersession/remediation. |
| Worker restrictions, independent Run/Outcome, policy-driven Task/Objective | Constitutional review table above and section 9 completion inputs. |
| Append-only Evaluation history, distinct Effect remedies, consistent ownership | Sections 7–9. |
| No unresolved contradiction with Constitution | Detected Conflicts below identifies lower-level conflicts and their constitutional resolutions; Constitution is unchanged. |
| Complete requested document, findings and minimal consistency patches | This document, ADR-0005 and the referenced consistency changes; no production or later-stage implementation. |
| Human gate satisfied | Explicit human architecture acceptance on 2026-09-06 accepts the design, ADR and Exec Plan; implementation remains bounded by Stage 1 scope. |

### Verification performed for this review

An ad hoc read-only document checker, executed outside the repository on 2026-09-06, parsed the six tables, expanded grouped sources, and compared their state inventories with both the core beliefs and Exec Plan. It checked nonempty authority/guard/event cells, unique non-self edges, event names against the plan, graph reachability from NONE, and the exact strict-sink sets specified above. Revised results: Objective **18**, Task **17**, Run **19**, Outcome **12**, Evaluation **11**, Effect **22** edges: **99 total including eight creation edges**, covering **43 states**. The prior review had 93 edges (six creation edges); the six added observation edges account for the full difference. Local Markdown links and code-fence balance passed; the Constitution matched HEAD and the plan remained Draft. Whitespace checks passed. These checks establish document structure, not implemented guard enforcement.

Guard-level review also walked these scenarios:

1. **Normal execution, rejected result:** Activate an Objective; ready its Task; assign execution-control ownership and start the Task; create/start a Run in an approved execution boundary. C registers a candidate, R records normal termination with no Run-level wait required, and C starts independent validation. V completes a valid negative Evaluation, then C rejects the Outcome. Run stays COMPLETED; neither Task completion nor Objective satisfaction follows. A worker's request cannot substitute for any of these decisions.
2. **Conflict set without erased judgments:** E1 and E2 have materially conflicting recorded results for the same acceptance scope. Register a conflict set and project both as CONFLICTED in one version-checked operation, with two lifecycle events and retained original content. A later E3 extends membership and is also conflicted. Arbitration references all members and their dispositions; E2 stays CONFLICTED if another applicable set remains open, even after this set is resolved. Once fully addressed, E1 may become ARBITRATED with UPHELD and E2 with MODIFIED or REVERSED, each with immutable original content and an appended effective judgment. Outcome acceptance still needs its own guards; resolving one member alone cannot release the others.
3. **Uncertain payment and compensation:** An irreversible payment intent passes independent preparation validation and receives explicit human authorization. After dispatch the receipt is lost, so E records QUARANTINED. A repeated commit is denied while occurrence is unknown. Independent reconciliation establishes the payment, allowing COMMITTED as a historical observation; a separately governed refund then supports COMPENSATING -> COMPENSATED. The payment receipt remains recorded, and no ROLLED_BACK claim is permitted.
4. **Confirmed unauthorized, unregistered payment:** An independent receipt establishes a payment with no prior Effect registration or valid authorization. E uses NONE -> COMMITTED with receipt provenance and separate violation findings; unknown Task attribution is explicit. No EffectPlanned event, permission or executor invocation is fabricated. A later linked observation deduplicates to this Effect. Governance investigation remains open independently of COMMITTED.
5. **Suspected unregistered mutation:** An anchored incident report supports suspicion but does not establish occurrence. E records NONE -> QUARANTINED. Later independent confirmation uses QUARANTINED -> COMMITTED regardless of authorization; a disproval instead appends occurrence_status=DISPROVED and incident_status=CLOSED with supporting findings, retaining QUARANTINED without implying unknown occurrence or executing anything. A PLANNED/SIMULATED record discovered to have an out-of-band mutation follows the corresponding observation-only edge, preserving prior preparation history.

### Exact changes from the 0.1 review baseline

The earlier review's topology changes below use the current terminology. The final v0.2 semantic cleanup only renames the quarantine/arbitration states and their events and clarifies appended metadata. A normalized before/after comparison retains all 99 edges and 43 states, including identical strict sinks and creation paths.

- Added six Effect edges: NONE -> COMMITTED; NONE -> QUARANTINED; PLANNED -> COMMITTED; PLANNED -> QUARANTINED; SIMULATED -> COMMITTED; SIMULATED -> QUARANTINED. Events are EffectCommitted or EffectQuarantined respectively; authority is scoped E observation authority.
- Revised Effect guards on PENDING_COMMIT -> COMMITTED, PENDING_COMMIT -> QUARANTINED, QUARANTINED -> COMMITTED and QUARANTINED -> PENDING_COMMIT to separate observation from execution eligibility. No prior authorization guard applies to factual occurrence recording; every future dispatch still requires normal execution guards.
- Revised Evaluation guards on RUNNING/COMPLETED -> CONFLICTED and COMPLETED/CONFLICTED -> ARBITRATED for conflict-set consistency and arbitration. No Evaluation edges were added or removed; INVALID transitions preserve membership and cannot silently resolve other members.
- No states, strict sinks or other entity edges changed. TaskProposal is explicitly assigned to Stage 9; it adds no Stage 1 state or edge.

## Open Questions

1. **Human design approval resolved:** Explicit human architecture review on 2026-09-06 accepted ADR-0005, this baseline and the Stage 1 Exec Plan. No design approval remains pending for this baseline; Stage 1 completion and exit review remain future gates.
2. **Resolved stage scope:** Human review assigned all TaskProposal representation/lifecycle/generation/governance implementation to Stage 9. There is no remaining Stage 1 scope discrepancy.
3. **Later operational detail:** Commit dispatch/reconciliation, compensation chains, verification cancellation/timeouts, and trusted checkpoint representations need later-stage design. Existing state rules conservatively deny unsafe transitions in the meantime. Whether operational experience warrants extra Effect process states needs a separate ADR; no new state is required to express this baseline.

No unresolved constitutional contradiction remains in the accepted matrices. The design and Exec Plan are accepted; Stage 1 implementation must still satisfy the plan's completion criteria and exit review.

## Detected Conflicts

| Finding | Sources and impact | Resolution / status |
| --- | --- | --- |
| Effect separation weaker in plan | Exec Plan INV-004 said committer must not be the **sole** verifier; Constitution 4.7 and invariant 4 prohibit an evaluator from committing the Effect it validates at all. | Corrected plan wording to the stronger rule. Multiple validators do not excuse a violating committer. |
| Missing authority tier | Exec Plan section 3 omitted approved design documents between Architecture and Exec Plans, contrary to Constitution section 3. | Restored that tier; a proposed design/ADR is not automatically approved. |
| Draft Task ownership ambiguity | Plan sections 7/12 require one primary Objective for every Task; section 26 only mentioned protection before READY. | Structural requirement clarified to include DRAFT, consistent with core beliefs section 7 and Architecture. |
| Run retry identity ambiguity | Plan RETRYING suggested another attempt on the same Run, while Architecture defines a Run as one concrete attempt. | Plan wording clarified; ADR-0005 and section 5 distinguish continuation from a new Run. |
| Immutable Evaluation vs mutable status | Architecture calls Evaluation immutable; plan includes ARBITRATED/INVALID status transitions. | Clarified immutable content/history versus appended lifecycle projection; original records cannot be overwritten. |
| Effect uncertainty gap | Plan QUARANTINED only described inability to remedy; no listed state captured unknown original commit. | Narrow clarification in core beliefs and plan; section 8 guards exits using retained uncertainty context, without fabricating a fact. |
| Occurrence conflated with authorization | Prior review required authorization for COMMITTED and quarantined even independently confirmed unauthorized occurrence. | Human review correction: observation-only ingestion/reconciliation records COMMITTED regardless of authorization; violations remain separate, and execution gates are unchanged. |
| Conflict treated as a single Evaluation flag | Prior review did not require all affected participants to be CONFLICTED together. | Human review correction: explicit versioned conflict sets, consistent per-member projections and append-only set-aware arbitration. |
| Progress percentage authority | Architecture allowed policy to make percentages authoritative, while core beliefs forbid satisfaction solely from Task percentage and plan section 20 says progress is non-authoritative. | Removed that exception; explicit completion-policy evaluation remains required. |
| Issue numbering mismatch | Plan section 34's provisional #1 is bootstrap; actual GitHub #1 is this review. | Added a note identifying the historical decomposition and review prerequisite without inventing new GitHub numbers. |
| Roadmap TaskProposal scope | ROADMAP Stage 1 previously included TaskProposal; six-entity plan excluded generation and deferred Planner. | Resolved by human review: representation, lifecycle, generation and governance implementation all belong to Stage 9; ROADMAP and plan updated. |

## Recommended Changes

- Implement assigned Stage 1 work against accepted ADR-0005 and these tables, preserving the plan's scope, completion criteria and exit review.
- Keep the minimal accompanying Architecture, State and Authority, and Exec Plan consistency corrections. No Constitution edit or weakening of a higher-level rule is proposed.
- In later assigned kernel Issues, expand grouped edges into deterministic legal-edge tests, test representative denied edges and identity-based authority attacks, and verify atomic audit/version behavior. The tables are the review oracle, not evidence of implemented enforcement.
- Keep TaskProposal in Stage 9 as directed by human review; defer runtime mechanics and additional state proposals to the relevant later-stage ADRs and Exec Plans.
