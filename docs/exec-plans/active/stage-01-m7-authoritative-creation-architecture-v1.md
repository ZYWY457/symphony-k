# Stage 1 M7 — Authoritative Creation Architecture

**Version:** 1
**Status:** Frozen architecture contract; corrected cumulative M7 HUMAN ACCEPTED after Issue #71
**TaskSpec:** [GitHub Issue #62](https://github.com/ZYWY457/symphony-k/issues/62)
**TaskSpec access mode:** `materialized-handoff`
**Starting baseline:** `9f61877c74d79caff72efca908ab18219fd4996c`
(`docs(governance): record effect non-creation acceptance`)

## 1. Objective

Freeze the implementation boundary for the eight accepted Stage 1 creation
edges that remain after all 91 non-creation edges were independently accepted:

```text
Objective  NONE -> DRAFT
Task       NONE -> DRAFT
Run        NONE -> PENDING
Outcome    NONE -> PROPOSED
Evaluation NONE -> PENDING
Effect     NONE -> PLANNED
Effect     NONE -> COMMITTED
Effect     NONE -> QUARANTINED
```

This document is an architecture audit and implementation contract. It does not
implement creation, claim M7 completion, claim 99/99 accepted, or close Stage 1.

## 2. Governing baseline and scope

This contract is subordinate to the repository hierarchy and preserves:

- Constitution v0.1, especially untrusted workers, independent authority,
  append-only history, and governed Effects;
- the accepted 43-state, 99-edge state-machine baseline in ADR-0005 and
  `docs/design-docs/state-machines.md`;
- the accepted Stage 1 parent plan and its M7/M8 split;
- the active completion map's accepted 91 non-creation edges and eight
  unresolved creation edges; and
- the accepted separation of Effect occurrence from authorization and policy
  truth.

In scope is the future pure-domain creation boundary, its typed inputs,
authority and semantic validation, initial version, event result, attack tests,
and bounded M7 decomposition.

Out of scope is Python or test implementation, persistence, repositories, real
uniqueness lookup, transactions, external Effect execution, incident-ingestion
runtime, TaskProposal, M8, M9, Stage 2, and any remote repository mutation.

No new top-level domain entity or cross-cutting subsystem is introduced. The
creation commands, decisions, observations, and semantic inputs described below
are supporting domain types for the existing six entities.

## 3. Audit of the accepted design and current kernel

### 3.1 Accepted creation semantics

The accepted design uses `NONE` only as notation for absence before an entity
exists. Shared guards require an authorized creator, a fresh typed identifier,
valid relationships, exact provenance, and one creation lifecycle event whose
prior state is absent. Effect observation creation is explicitly exceptional:
it records confirmed or suspected external reality without inventing an
`EffectPlanned` history or establishing execution eligibility.

### 3.2 Six snapshot and topology modules

All six entity modules expose immutable snapshots with explicitly supplied
state and version. Their constructors validate representation only and do not
create authoritative work.

| Entity module | Canonical creation target | Creation-relevant snapshot facts | Audit result |
| --- | --- | --- | --- |
| `objective.py` | `DRAFT` | bounded goal data, nonempty acceptance criteria, acceptance authority, completion-policy reference, optional validity horizon | Target constant exists; ordinary topology contains only the 17 non-creation edges. |
| `task.py` | `DRAFT` | definition, exactly one primary Objective ID, completion-policy reference, immutable secondary links | Target constant exists; constructor cannot prove related Objectives exist. |
| `run.py` | `PENDING` | one Task ID, execution-profile reference, optional distinct predecessor Run ID | Target constant exists; constructor cannot prove Task/Objective state or predecessor topology. |
| `outcome.py` | `PROPOSED` | one originating Run ID, producer, nonempty artifacts, evidence and optional prior-candidate lineage | Target constant exists; constructor cannot prove Run, Task, producer, or lineage relationships. |
| `evaluation.py` | `PENDING` | explicit target and method, optional verifier, no result in PENDING | Target constant exists; constructor cannot prove target currentness, artifact scope, policy, or independence. |
| `effect.py` | `PLANNED`, `COMMITTED`, `QUARANTINED` | planned or observed immutable origin, target, optional payload; planned origin requires Task and payload; unlinked observed origin requires an explicit reason | Three targets exist; ordinary topology contains only the 19 non-creation edges. Constructors dispatch nothing. |

The creation target constants are canonical lookup data. They are not creation
APIs and do not authorize direct snapshot construction as authoritative state.

### 3.3 Current transition and semantic-guard boundary

`transition_entity(entity, request, context)` necessarily consumes an existing
snapshot. It:

1. compares `request.expected_version` with `entity.version`;
2. derives the source state from that snapshot;
3. exact-binds a `TransitionAuthorityDecision` containing an observed version
   and non-optional prior state;
4. requires an entity semantic guard bound to the same ID, version, source,
   target, and correlation; and
5. increments the source version before returning a replacement snapshot and
   one event.

Each of the six semantic-guard modules likewise defines inputs only for
non-creation `(source_state, target_state)` pairs and validates an existing
snapshot. The extensive supporting Evaluation and Effect records also bind to
observed entity versions. This is correct for the accepted 91 edges and must not
be weakened.

The transition engine already provides reusable creation-compatible pieces:

- actor-type eligibility accepts `prior_state=None` for canonical creation
  targets;
- `DomainEventMetadata` represents absence with `prior_state=None`;
- `DomainEvent` validates that absent prior state is used only for a canonical
  creation target; and
- the creation event types already exist.

It does not provide a creation execution path. In particular,
`TransitionRequest.expected_version`, `TransitionAuthorityDecision.prior_state`
and `observed_entity_version`, and every current semantic guard make it
incorrect to route creation through `transition_entity`.

### 3.4 Version and Effect-observation findings

`EntityVersion` accepts non-negative integers and increments immutably, while
the snapshot modules deliberately left initial-version selection to M7. No
current value means “not created.”

`ObservedEffectOrigin`, `EffectObservationRecord`, authorization and governance
findings, incident history, and Effect semantic guards preserve the accepted
observation provenance. Current observation semantic guards still bind an
existing Effect source state and therefore cannot directly express either
observation-only creation edge. Their provenance shapes must be reused or
specialized, not bypassed.

### 3.5 Conflict assessment

No contradiction was found among the Constitution, core beliefs, ADR-0005,
accepted state-machine design, parent plan, completion map, or current kernel.
The missing creation boundary is an intentionally deferred implementation gap.
Consequently this task does not update the completion map.

## 4. Non-negotiable creation model

`NONE` must never be represented by:

- an enum member;
- an entity snapshot;
- a fake source entity;
- a null-object or sentinel entity;
- an `EntityVersion` value; or
- a self-transition such as `DRAFT -> DRAFT`.

Absence is expressed only by invoking the dedicated creation operation and by
`DomainEventMetadata.prior_state is None` in its successful event.

Creation is not a special case inside `transition_entity`. The future public
domain boundary is a separate overloaded operation, conceptually:

```python
create_entity(
    request: CreationRequest,
    context: CreationContext,
) -> CreationResult
```

It accepts no entity snapshot and no expected entity version. It must not call
`transition_entity` with manufactured input. Existing non-creation APIs and
semantic guards remain unchanged.

## 5. Typed request contract

Creation uses exactly eight immutable request variants, one per accepted edge:

```text
ObjectiveDraftCreationRequest
TaskDraftCreationRequest
RunPendingCreationRequest
OutcomeProposedCreationRequest
EvaluationPendingCreationRequest
PlannedEffectCreationRequest
CommittedEffectObservationCreationRequest
QuarantinedEffectObservationCreationRequest
```

The request type determines the entity family and target state. A caller cannot
select another state with a generic string or supply a source state.

Every request contains:

```text
event_id
entity_id
requested_by
reason
timestamp
correlation_id
causation_id       # required creation-request identity
entity_spec        # typed fields for the resulting snapshot
semantic_input     # typed relationship/provenance guard input
```

`requested_by` records who initiated the request. It grants no authority and
may be a Worker for Outcome proposal or Effect intent/incident evidence. The
request contains neither `state`, `version`, `prior_state`, nor
`expected_version`; the request variant fixes state and the creation service
assigns version.

The immutable normalized request scope comprises its request variant, entity
type and ID, canonical target, requester, causation and correlation IDs, entity
spec, and semantic input. Authority and freshness inputs must bind that entire
scope by value. Binding only the entity ID and target is insufficient because
it would permit payload, relationship, provenance, or requester substitution.

## 6. Creation authority representation

Creation requires a distinct `CreationAuthorityDecision`; the existing
`TransitionAuthorityDecision` must not be made nullable or overloaded with
fake source/version values.

The decision contains at least:

```text
decision_ref
request_scope
decided_by
decision_status    # AUTHORIZED, DENIED, or UNRESOLVED
policy_or_grant_refs
decided_at
```

The creation service accepts only `AUTHORIZED`, exact-scope decisions. It also
applies the existing canonical actor eligibility matrix:

| Edge family | Eligible decision actor |
| --- | --- |
| Objective creation | scoped REQUESTER, SCHEDULER, POLICY_ENGINE, or HUMAN_OPERATOR |
| Task creation | scoped REQUESTER, SCHEDULER, POLICY_ENGINE, or HUMAN_OPERATOR |
| Run creation | scoped SCHEDULER or RUN_CONTROLLER |
| Outcome creation | scoped SCHEDULER or POLICY_ENGINE |
| Evaluation creation | scoped SCHEDULER or EVALUATOR |
| all Effect creation | scoped EFFECT_CONTROLLER |

Eligibility is not a grant. Actor labels supplied by a caller are not proof of
authentication or scope. A worker may be the recorded requester or producer,
but never becomes the authoritative creator by relabeling itself. `SYSTEM`
remains non-privileged unless an independently authenticated controller role
makes the decision.

`CreationContext` carries the exact authority decision, exact-bound identifier
availability input, the authenticated applying service identity, and optional
additional pure guards. The event's authoritative `actor` is `decided_by`;
requester and applying service remain separately recorded provenance.

## 7. Initial `EntityVersion` contract

Every successful creation returns the first authoritative snapshot at exactly:

```text
EntityVersion(1)
```

The creation caller cannot choose or override it. The single creation event has
the same entity version. Subsequent non-creation transitions continue to use
`.next()`, so the first transition from a created snapshot produces version 2.

Version 1 denotes the first existing authoritative projection; it does not
stand for `NONE`. `EntityVersion(0)` remains a valid typed value for existing
structural or imported snapshots under the current value type and is not an
absence sentinel. It cannot be supplied to creation, used as an expected
version for creation, or used to turn an existing version-0 snapshot into a
creation source. Any future import/migration policy is outside this contract.

## 8. M7 versus M8 identifier freshness

The accepted guard says a creation identifier is fresh, but the pure M7 domain
kernel has no authoritative repository and cannot establish global absence.
That boundary is resolved as follows.

### M7 responsibility

M7 defines an immutable, exact-request-bound identifier availability result
with `AVAILABLE`, `DUPLICATE`, and `UNRESOLVED` outcomes. `create_entity` rejects
anything other than `AVAILABLE`, wrong entity type/ID, wrong request identity,
or stale/mismatched correlation. M7 tests use trusted deterministic fixtures to
exercise this contract. The result is not caller self-attestation and must not
be described as a durable uniqueness guarantee.

That result contains at least its own stable reference, the normalized request
scope, entity type and ID, availability status, observing boundary identity,
observation time, and correlation ID. It contains no source state or entity
version. The observing identity must be an authenticated orchestration boundary,
not the requester whose proposed ID is being checked.

M7 also prevents local identity contradictions in the supplied topology, such
as self-predecessors, self-lineage, duplicate contribution identities, or a
planned Effect Run that is not associated with its Task.

### M8 responsibility

M8 performs the real authoritative lookup and insert through repository and
transaction boundaries. It must make these one atomic decision:

```text
identifier absent
+ related records current
+ entity version 1 inserted
+ exactly one creation event inserted
```

Database uniqueness constraints and transaction/concurrency semantics are the
final defense. Two concurrent requests for the same ID cannot both succeed.
An M7 result computed before an M8 collision must fail at the M8 boundary; it
must not overwrite or reinterpret the existing entity. Idempotent replay of the
same request/event identity and conflicting reuse of that identity are likewise
durable M8 concerns, while M7 freezes their required observable behavior.

This task does not implement a repository, lookup, uniqueness check, or
transaction.

## 9. Per-entity semantic contract

All relationship observations below are typed, exact-ID/version-bound inputs
from trusted orchestration boundaries. An ID alone does not prove existence or
currentness. Creation validates the immutable snapshot fields and these
semantic inputs before constructing a result.

### 9.1 Objective: `NONE -> DRAFT`

Required snapshot data:

- typed fresh Objective ID;
- nonempty goal and acceptance criteria;
- designated acceptance authority;
- completion-policy reference; and
- optional valid-until timestamp.

Required semantics:

- an evidence-backed bounded-goal decision;
- acceptance criteria and designated authority belong to this exact Objective
  definition;
- the completion-policy reference is recorded and applicable; and
- definition/request provenance and any applicable policy/grant references are
  retained.

The result is DRAFT only. Creation does not activate, satisfy, fail, cancel, or
expire the Objective.

### 9.2 Task: `NONE -> DRAFT`

Required snapshot data:

- typed fresh Task ID and bounded nonempty definition;
- exactly one primary Objective ID;
- completion-policy reference; and
- immutable, duplicate-free non-authoritative contribution Objective IDs that
  exclude the primary Objective.

Required semantics:

- a current observation proves the primary Objective exists; DRAFT creation
  does not require it to be ACTIVE;
- every contribution ID, if any, identifies an existing Objective;
- definition origin/request provenance is explicit; and
- no relationship grants budget authority or propagates an Objective state.

The primary Objective relationship is mandatory even while the Task is DRAFT.
TaskProposal is not an accepted source type and is not introduced here.

### 9.3 Run: `NONE -> PENDING`

Required snapshot data:

- typed fresh Run ID;
- exactly one Task ID;
- execution-profile reference; and
- optional distinct predecessor Run ID.

Required semantics:

- the observed Task exists and is READY or IN_PROGRESS;
- the Task's observed primary Objective exists and is ACTIVE;
- the Task and Objective observations are mutually consistent and versioned;
- a concrete attempt identity and execution-profile selection provenance are
  recorded; and
- if a predecessor is supplied, it exists, belongs to the same Task, is not the
  new Run, and has explicit recovery/reassignment lineage with no cycle.

Creation does not start execution, allocate a sandbox, authorize a worker, or
perform recovery runtime behavior.

### 9.4 Outcome: `NONE -> PROPOSED`

Required snapshot data:

- typed fresh Outcome ID;
- one originating Run ID;
- producing identity;
- at least one immutable artifact reference;
- zero or more evidence references and optional validity horizon; and
- optional prior Outcome lineage, with no replacement link on the new Outcome.

Required semantics:

- the originating Run exists at an observed version and its Task identity is
  retained;
- the producer and immutable artifact/evidence scope are bound to that Run and
  to this exact request;
- a worker proposal remains a recorded claim, not validation; and
- any prior Outcome exists, is distinct, belongs to the same Task/acceptance
  scope, links directly to this new candidate, and produces no cycle.

The result is never ACCEPTED or REJECTED, and it does not change Run, Task, or
Objective state.

### 9.5 Evaluation: `NONE -> PENDING`

Required snapshot data:

- typed fresh Evaluation ID;
- one explicit `EvaluationTargetRef`;
- a validation method; and
- optional assigned verifier, with no result.

Required semantics:

- a Run, Outcome, or Effect target exists at the exact target version; an
  Evidence target is independently anchored and carries no invented entity
  version;
- artifact/evidence/version scope, validation policy, and request provenance are
  explicit;
- either an independent EVALUATOR is assigned or an explicit assignment
  requirement is recorded; and
- any assigned verifier is not the target's producing/executing principal for
  the scope being independently validated.

PENDING means verification was requested. It does not imply a verdict,
acceptance, or that verification started.

### 9.6 Effect: `NONE -> PLANNED`

Required snapshot data:

- typed fresh Effect ID;
- `PlannedEffectOrigin` with exactly one accountable Task, proposer, and
  optional Run;
- exact target and required payload identity.

Required semantics:

- the Task exists; an optional Run exists and belongs to that Task;
- the Effect intent binds target, payload, proposer/request provenance,
  reversibility, risk, permissions, idempotency/deduplication strategy, and
  required authorization class; and
- the Effect Controller has scoped recording authority.

The result records intent only. It grants no dispatch, simulation,
PENDING_COMMIT eligibility, credentials, budget, or authorization.

### 9.7 Effect: `NONE -> COMMITTED`

Required snapshot data:

- typed fresh Effect ID;
- `ObservedEffectOrigin` with external operation identity, nonempty independent
  evidence, observer and observation time;
- exact target and payload when known; and
- verified Task/Run attribution or an explicit meaningful unlinked reason.

Required semantics:

- an `EffectObservationRecord` exact-binds the new Effect ID, resulting version
  1, external operation, target/payload, deduplication identity, correlation,
  observer, recording Effect Controller, observation/occurrence times, and
  evidence;
- occurrence status is CONFIRMED and evidence is stronger than a worker claim;
- origin, observation record, authorization finding, and optional governance or
  incident records agree exactly;
- known, denied, missing, or unknown prior authorization is recorded separately
  and never gates factual registration; and
- duplicate external-operation/deduplication identity is rejected or reconciled
  to an already registered Effect by the future M8 boundary.

The observation record's version 1 binds the real resulting projection; it is
not a fake source version and does not claim an Effect entity existed before
the external observation.

### 9.8 Effect: `NONE -> QUARANTINED`

The snapshot and provenance requirements are the observation requirements
above, plus an exact immutable quarantine context. Required semantics differ:

- occurrence status is UNCERTAIN, supported by anchored evidence;
- the quarantine reason records suspected/unknown original occurrence and the
  controlled-reconciliation context;
- occurrence is not asserted as confirmed or disproved at creation;
- any incident and authorization/governance findings remain separate; and
- blind retry and all automatic execution eligibility are absent.

A later disproval is appended as a separate occurrence/incident finding. It
does not rewrite this creation event or require another lifecycle state.

## 10. Effect observation-only boundary

`NONE -> COMMITTED` and `NONE -> QUARANTINED` are recording operations only.
Their creation code path must have no executor, credential broker, dispatch
callback, external mutation client, simulation shortcut, or conversion into a
planned intent.

They must never fabricate:

- an `EffectPlanned` event;
- Task or Run ownership when attribution is unknown;
- target, payload, actor, timestamps, or authorization;
- planning, preparation, validation, dispatch, or approval history;
- retrospective authorization; or
- permission to retry, remediate, or commit another external action.

The Effect Controller's recording authority is distinct from authority for the
observed external action. Confirmed unauthorized reality must remain recordable
as COMMITTED with separate findings. Uncertain reality must remain
QUARANTINED, even when recording it exposes a governance violation.

## 11. Successful event contract

Every successful creation returns one immutable snapshot and exactly one
authoritative lifecycle event:

| Edge | Event |
| --- | --- |
| Objective `NONE -> DRAFT` | `ObjectiveCreated` |
| Task `NONE -> DRAFT` | `TaskCreated` |
| Run `NONE -> PENDING` | `RunCreated` |
| Outcome `NONE -> PROPOSED` | `OutcomeProposed` |
| Evaluation `NONE -> PENDING` | `EvaluationRequested` |
| Effect `NONE -> PLANNED` | `EffectPlanned` |
| Effect `NONE -> COMMITTED` | `EffectCommitted` |
| Effect `NONE -> QUARANTINED` | `EffectQuarantined` |

The event uses the request's event ID, entity ID, timestamp, correlation,
causation, and reason; entity version is 1; `metadata.prior_state` is `None`;
and `metadata.new_state` is the canonical target. Its actor is the exact
authorized decision actor. Stable metadata/reference annotations retain, as
applicable:

- requester and applying-service identities;
- creation-authority decision and policy/grant references;
- identifier-availability input reference;
- relationship observation versions;
- semantic/evidence/provenance record references; and
- Effect observation, authorization, governance, incident, deduplication, and
  quarantine-context references.

Large evidence bodies do not belong in free-form annotations; events retain
stable immutable references. Creation must reject duplicate annotation keys or
metadata that disagrees with the snapshot/result.

A failed structural, authority, freshness, semantic, or additional guard emits
no success lifecycle event and returns no authoritative snapshot. A separately
attributable `TransitionRejected` audit record remains permitted but cannot
impersonate creation. Durable atomic append and idempotent replay are M8
responsibilities.

## 12. Required validation order

The future pure-domain implementation validates in this order:

1. request and context types;
2. request variant to entity family/canonical target mapping;
3. typed entity ID and structural entity spec;
4. exact request-scope binding of authority and identifier availability;
5. AUTHORIZED status and actor eligibility;
6. AVAILABLE identifier status, without overstating durable uniqueness;
7. per-entity relationship, currentness, provenance, independence, and Effect
   observation semantics;
8. any additional pure guards;
9. construction of the immutable version-1 snapshot;
10. construction of exactly one matching creation event; and
11. `CreationResult` consistency validation.

No partially constructed object is authoritative, and no failed step yields a
success event.

Typed rejection remains within the Stage 1 error model: malformed request values
raise `InvalidDomainValue`; denied, unresolved, mismatched, or ineligible
authority raises `UnauthorizedTransition`; missing related entities raise
`EntityNotFound`; inconsistent topology raises `InvalidRelationship`; failed
creation semantics or non-AVAILABLE pre-M8 identity input raises
`InvariantViolation`; and an M8 race against an otherwise valid availability
observation raises `ConcurrencyConflict`. No raw persistence exception becomes
the public domain result.

## 13. Attack matrix

| Attack or failure | Required result |
| --- | --- |
| Pass a fake `NONE` enum, null object, sentinel entity, or version as source | Reject; no such source is part of the creation API. |
| Pass a fabricated DRAFT/PENDING/etc. snapshot to `transition_entity` and request a self-loop | Reject as an illegal non-creation transition. |
| Use `EntityVersion(0)` or another caller-selected version to mean absence | Reject; creation has no version input and always returns version 1. |
| Select a target inconsistent with the request variant | Structurally impossible or reject before authority checks. |
| Reuse an authorized decision for another ID, payload, relationship, requester, request ID, or correlation | Reject exact-scope mismatch. |
| Worker relabels itself as scheduler/controller/evaluator | Reject without independently authenticated, exact-scoped authority evidence. |
| `SYSTEM` claims implicit superuser creation authority | Reject; SYSTEM alone is ineligible. |
| Identifier availability is missing, duplicate, unresolved, wrong-type, or bound to another request | Reject; do not claim freshness. |
| Two concurrent creations use one ID | M8 permits at most one atomic insert; the loser receives a concurrency/duplicate failure. |
| Reuse an event/request identity with different content | Reject; identical durable replay may return the original result only in M8. |
| Task's primary Objective is missing, wrong, stale, or duplicated as a contribution | Reject with no Task/event. |
| Secondary Objective link is used as ownership or propagates state | Reject/ignore as authority; no related lifecycle mutation. |
| Run's Task is not READY/IN_PROGRESS, its Objective is not ACTIVE, or the observations disagree | Reject with no Run/event. |
| Run predecessor is self, wrong-Task, missing, or cyclic | Reject. |
| Outcome Run is missing or producer/artifact/prior-lineage binding is substituted | Reject; worker proposal remains only request data. |
| Outcome request asks for ACCEPTED/REJECTED or changes parent state | Reject; only PROPOSED is creatable. |
| Evaluation target is missing/stale, Evidence target has an invented version, or assignment independence fails | Reject with no Evaluation/event. |
| Evaluation PENDING request carries a result | Reject. |
| Planned Effect lacks Task, payload, exact intent provenance, or has a Run from another Task | Reject; no Effect/event. |
| Planned Effect creation is treated as dispatch authorization | Reject; no execution capability is reachable from creation. |
| Observation-only Effect relies only on a worker claim or lacks external identity, evidence, deduplication, observer/recorder, or timing provenance | Reject. |
| Confirmed evidence targets QUARANTINED or uncertain evidence targets COMMITTED | Reject status/target semantic mismatch. |
| Observation origin, record, target, payload, Effect ID, resulting version, or correlation disagree | Reject exact-binding mismatch. |
| Missing/denied execution authorization is used to suppress confirmed occurrence | Reject the suppression; record COMMITTED with separate finding when all observation guards pass. |
| Observation creation fabricates planning, authorization, Task/Run attribution, or a prior lifecycle event | Reject; return only the factual creation event. |
| Observation path is wired to executor/credentials/dispatch | Architecture violation; implementation must have no such dependency or callback. |
| Unlinked observed Effect becomes executable because it was registered | Reject; later governed intent, verified attribution, and full normal guards are required. |
| A guard fails after inputs are inspected | Return no authoritative snapshot and no success event. |

## 14. Bounded M7 implementation decomposition

Each implementation slice requires its own durable TaskSpec and full repository
validation. The sequence below is architectural decomposition, not authorization
to implement it in this Run.

### M7D1 — Shared creation protocol

Define the eight request variants, normalized request scope, creation authority
decision, identifier-availability input, version-1 rule, creation result, and
separate overloaded `create_entity` boundary. Reuse event/eligibility helpers
without changing any non-creation edge.

Acceptance is limited to typed construction, exact binding, default denial,
initial-version behavior, and proof that no fake source/expected version is
accepted.

### M7D2 — Objective and Task creation semantics

Implement `ObjectiveCreated` and `TaskCreated` with bounded-definition,
acceptance/completion-policy, primary Objective, contribution, and provenance
guards. No readiness or activation behavior is added.

### M7D3 — Run, Outcome, and Evaluation creation semantics

Implement `RunCreated`, `OutcomeProposed`, and `EvaluationRequested` with exact
relationship/currentness, attempt, producer/artifact, target, method, policy,
and verifier-independence guards. No runtime execution or verification is added.

### M7D4 — Planned Effect creation

Implement `EffectPlanned` with exact Task/Run and intent provenance. Prove it
cannot authorize, dispatch, simulate, or commit an external action.

### M7D5 — Observed Effect creation

Implement observation-only `EffectCommitted` and `EffectQuarantined` creation,
reusing exact Effect provenance shapes while specializing them for absence of a
source snapshot. Cover confirmed/uncertain status, authorization/governance
separation, unlinked attribution, deduplication input, and no-executor attacks.

### M7D6 — Integrated eight-edge acceptance candidate

Run one closed-topology and attack suite over exactly the eight creation edges
and all 91 accepted non-creation edges. Confirm one event per success, default
denial for every other absent-to-state pairing, no regression of existing
semantic guards, and no claim of persistence safety.

Independent acceptance is still required before reporting M7 as complete or
99/99 accepted.

## 15. Future implementation validation gates

Each later implementation slice must run the repository's locked gates:

```text
uv sync --locked
uv run pytest -p no:cacheprovider
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
git diff --check
```

It must explicitly stage only its authorized files, inspect the complete staged
diff, and distinguish pure-domain M7 evidence from future M8 persistence and
atomicity evidence.

## 16. Acceptance criteria for this architecture contract

- Exactly the eight accepted creation edges are in scope.
- `NONE` is absence only and is never modeled as state, entity, or version.
- Creation has a dedicated API with no source snapshot or expected version.
- Request, authority, freshness, relationship, and provenance inputs are exact
  and independently scoped.
- The initial authoritative version is fixed at 1.
- M7 fixture-level identifier availability is distinguished from M8's real
  atomic uniqueness guarantee.
- Per-entity creation relationships and provenance are explicit.
- Every success yields the canonical snapshot and exactly one matching event.
- Effect observation-only creation preserves external reality without inventing
  planning, dispatch, authorization, ownership, or approval.
- The attack matrix and implementation slices are bounded and testable.
- No Python, tests, completion map, persistence, TaskProposal, external Effect,
  M8, Stage 2, or remote state is changed by this task.

## 17. Historical completion boundary after M7D2

```text
91/91 non-creation semantics = complete and accepted
authoritative creation architecture = defined by this architecture contract
M7D1 shared creation protocol = HUMAN ACCEPTED
M7D2 Objective/Task creation = HUMAN ACCEPTED cumulatively after Issue #69
creation edges HUMAN ACCEPTED = 2 / 8
integrated edges HUMAN ACCEPTED = 93 / 99
remaining six creation edges = unresolved
M7 integrated 99-edge acceptance = incomplete
M8 persistence and atomicity = incomplete
Stage 1 = incomplete
```

This document must not be cited as evidence that M7, 99/99 transitions, or
Stage 1 has been accepted or completed.

## Subsequent cumulative Human acceptance - Issue #72

Issue #70's accelerated stack received REQUEST CHANGES for the Evaluation
producer-to-creation-authority relabel defect. Issue #71 corrected that blocker.
Independent Human Review accepted the corrected cumulative result through
`8f73da617ac686254ea30fc33a6d8f81bdb406cb`: non-creation 91 / 91,
creation 8 / 8, integrated 99 / 99. M7 is HUMAN ACCEPTED.
The original candidate counts and validation above are historical evidence,
not the current acceptance boundary; Issue #70 alone was not accepted.
Status reconciled under Issue #72; the architecture contract remains active.
M8 and M9 remain incomplete; Stage 1 is not complete.
