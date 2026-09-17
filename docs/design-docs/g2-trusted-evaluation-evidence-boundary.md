# G2 Trusted Evaluation and Evidence Boundary

Status: **G2/M0 DESIGN CANDIDATE / NOT ACCEPTED / NO IMPLEMENTATION RELEASED**.

TaskSpec: Issue #105, revision `r2 - g2-m0-design-freeze-final-handoff`.

Launch baseline: `12fabf8d79f5a7200b10f533b71b636b118fddc7`.

This document freezes the design boundary needed by G2/M1-M5. It does not
implement that boundary, release a later milestone, or change accepted Stage 1
semantics.

## 1. Scope

G2 turns attributable evidence and independent Evaluation into a supported
governance integration boundary. This design specifies:

- how a caller claim differs from independently verifiable evidence and trusted
  provenance;
- the durable identity, integrity, source, collection, principal, method and
  exact-target facts required for evidence;
- how authenticated evaluator identity, assignment provenance and independence
  facts enter the trusted boundary;
- the exact values that Evaluation creation, start, completion, effective-use
  resolution and Outcome disposition must bind;
- how G2/M4 obtains complete authoritative conflict, arbitration and
  invalidation history without trusting a caller-supplied slice; and
- which persistence extensions M1 and M2 require.

The accepted Stage 1 `Evaluation`, `EvidenceRef`, conflict, arbitration,
invalidation, effective-use and Outcome-disposition semantics remain the
semantic authority. G1 remains the caller-safe facade and trusted-binder seam.

## 2. Non-goals

This design does not:

- add a seventh core entity or any lifecycle state or transition;
- make evidence, assignment or resolver records lifecycle entities;
- define a universal evidence payload, verdict taxonomy or universal judge;
- choose a login, session, JWT, organization RBAC or service transport;
- make caller-supplied `ActorIdentity` an authentication or authorization fact;
- replace Stage 1 transition, exact-version, replay, concurrency, conflict,
  arbitration, invalidation or Outcome-disposition semantics;
- permit a favorable verdict to accept an Outcome directly;
- dispatch, commit, observe or reconcile a real external Effect;
- implement a schema, API, provider adapter or runtime; or
- release G2/M1-M5, G3, or Issue #106.

## 3. Existing surface and frozen interpretation

The current accepted surface has deliberate trust gaps that G2 must close:

| Existing surface | What it establishes | What it does not establish |
| --- | --- | --- |
| `EvidenceRef` | A non-empty opaque identity | Existence, content, integrity, source, exact scope or independent validity |
| `EvaluationMethodRef` | Opaque method identity and version | That the method ran, was assigned, or produced the result |
| `ActorIdentity` | A typed actor label used in domain records | Authentication, credential ownership, assignment, independence or authority |
| `EvaluationSubmission` | Caller claims for target, method, evidence and producing identities | Trusted evidence, evaluator assignment or authority |
| `TrustedGovernanceBinder` | A trusted seam for canonical Stage 1 requests and contexts | A concrete G2 evidence, identity or assignment provider |
| `EvaluationTargetRef` | Exact entity identity/version, or an unversioned evidence target | Currentness, repository existence or a trusted evidence anchor |
| `EvaluationResult` | Immutable original judgment content and `EvidenceRef` set | That every reference resolves to trusted provenance or matches the assignment/method/target |
| `derive_evaluation_effective_use(...)` | Accepted pure derivation over a complete current history slice | Repository completeness, current conflict-set selection or a consistent durable read |
| Stage 1 persistence validation | Current Evaluation and complete durable conflict/arbitration/invalidation checks inside existing writes | A public authoritative effective-use query or durable evidence/assignment catalog |

The G1 facade correctly preserves caller-controlled values while requiring a
trusted binder to construct authoritative contexts. G2 implementations must
extend the trusted side of that seam. They must not reinterpret G1 equality
checks as proof that caller claims are trustworthy.

## 4. Trust vocabulary

G2 uses three distinct categories:

1. **Caller claim** — caller-controlled identifiers, payloads, labels, URLs,
   digests, `ActorIdentity` values or result content. A claim may be retained for
   audit, but grants no trust or authority.
2. **Independently verifiable record** — an immutable durable record whose
   asserted bytes or external observation can be rechecked through a configured
   verification mechanism without relying on the submitting caller. It is not
   trusted for a use until exact scope and policy checks also pass.
3. **Trusted provenance** — a boundary-produced durable record created after an
   authenticated/approved collector or source, integrity verification, exact
   scope and principal provenance have passed. Trust is scoped to the recorded
   use; it is not a global endorsement of the payload, provider or principal.

Promotion is never achieved by setting a caller field such as `trusted=true`.
A trusted component may preserve a caller claim and then append its own result,
but must not rewrite the claim into provenance.

## 5. Data flow and trust boundaries

```text
UNTRUSTED / CALLER-CONTROLLED
external Worker, evaluator client, orchestrator or provider callback
        |
        | evidence claim / result claim / ActorIdentity label
        v
+--------------------- G2 TRUST BOUNDARY ----------------------+
| authenticate transport/principal where applicable             |
| collect or independently verify evidence and integrity anchor |
| establish exact target scope and producer/collector facts     |
| issue/resolve exact evaluator assignment and independence     |
| persist immutable evidence/assignment supporting records      |
| bind trusted records into canonical G1/Stage 1 inputs          |
|                                                               |
| M4 resolver, within one consistent durable observation:       |
| Evaluation head + latest applicable conflict-set versions     |
| + complete relevant arbitration/invalidation history          |
+------------------------------+--------------------------------+
                               |
                               v
        Stage 1 semantic authority and lifecycle service
        `derive_evaluation_effective_use(...)`
                               |
                               v
        exact effective-use observation + disposition policy
        + required independently authenticated Human acceptance
                               |
                               v
        Stage 1 Outcome disposition transition
```

The trust boundary may be embedded or service-backed. Its security mechanism is
replaceable, but it must output the same durable facts and exact bindings. An
external provider is not trusted merely because it is external; provider output
must enter through an approved collector/verifier adapter.

### 5.1 Responsibility separation

- A Worker or result submitter may make claims but cannot mint trusted evidence,
  assignment, independence or Human-acceptance facts.
- A collector may attest what it collected. It does not decide Evaluation or
  Outcome lifecycle authority merely by collecting it.
- An assignment authority may assign an evaluator and establish relationship
  facts. It does not manufacture evidence or commit an Effect.
- An evaluator may produce a judgment under an assignment. It cannot establish
  its own assignment or independence where policy forbids self-validation.
- The M4 resolver may load history and derive effective use. It does not decide
  Outcome policy or commit a lifecycle transition.
- Stage 1 remains the only lifecycle semantic authority.

## 6. Trusted evidence contract

### 6.1 Public claim shape

M1 may expose a transport-neutral claim shaped conceptually as follows:

```text
EvidenceSubmissionClaim
  requested_evidence_ref: EvidenceRef | absent
  target: RunRef | OutcomeRef | EffectRef | EvidenceRef
  source_locator_claim: opaque value
  integrity_anchor_claim: IntegrityAnchorClaim | absent
  observed_at_claim: timestamp | absent
  method_claim: MethodDescriptor | absent
  producing_principal_claims: principal labels[]
  caller_identity_claim: ActorIdentity
  idempotency_key: opaque value
```

Every field is a claim. A requested identity is subject to collision and replay
checks; the caller cannot reserve an identity with arbitrary metadata.

### 6.2 Trusted durable record shape

The public exact reference is:

```text
EvidenceRecordRef
  evidence_ref: EvidenceRef
  record_fingerprint: canonical digest of the complete immutable record
```

The fingerprint prevents a reference consumer from silently accepting different
metadata under the same identity. It is not a digest of the evidence payload
unless the selected integrity anchor explicitly says so.

After trusted collection or independent verification, M1 records conceptually:

```text
TrustedEvidenceRecord
  evidence_ref: EvidenceRef
  record_fingerprint: canonical digest of the complete record
  integrity_anchor: ContentDigestAnchor | ExternalImmutableAnchor
  source: source kind + stable source/provider identity + source namespace
  collector: authenticated collector principal + collector adapter/version
  collected_at: trusted boundary collection time
  observed_at: source observation time, with provenance
  target_scope: exact target identity + EntityVersion, or exact EvidenceRef
  method: method/tool/provider identities and versions when material
  producing_principals: authenticated or attributable principal refs[]
  collection_request_ref: immutable request/causation provenance
  evidence_policy: exact policy identity + version
  verification: verifier identity + mechanism/version + verified_at
  supersedes: prior evidence ref | absent
```

`record_fingerprint` is an internal exact-record comparison and replay anchor;
it does not replace the evidence integrity anchor. Canonicalization rules and
algorithm identifiers must be versioned.

### 6.3 Integrity anchor kinds

`ContentDigestAnchor` contains an algorithm identifier and digest over the exact
collected bytes or canonical representation. The algorithm must be on a trusted
configuration allowlist at collection and use time.

`ExternalImmutableAnchor` supports evidence that is not content-addressed. It
contains all of:

- stable provider/source identity and namespace;
- immutable receipt, object revision, event sequence or signed observation ID;
- the verification mechanism and version;
- the exact observed locator and any provider version/ETag/revision available;
- an authenticated provider/collector assertion or independently repeated read;
  and
- collection and observation times.

A mutable URL, database key, filename, free-form receipt string or caller claim
without an immutable provider revision/receipt or independently anchored
observation is not a trusted anchor. It may be retained only as a caller claim.

### 6.4 Identity, replay and correction rules

- `EvidenceRef` identifies one immutable provenance record, not a mutable slot.
- Repeating the same identity with the exact same canonical record is
  idempotent and returns the original record.
- Repeating the identity with any altered anchor, target, source, time,
  collector, method or principal provenance fails as an identity collision.
- A correction or refreshed observation receives a new `EvidenceRef` and may
  append a `supersedes` link; the prior record remains historical truth.
- Evidence scoped to entity version N is stale for N+1 unless a trusted policy
  explicitly produces a new evidence record for N+1. Callers cannot widen
  scope.
- An evidence target by `EvidenceRef` must resolve to its exact immutable trusted
  record; recursive substitution and unresolved references fail closed.

If later evidence proves an anchor, source or collector untrustworthy, the
system appends an `EvidenceTrustFindingRecord` against the exact
`EvidenceRecordRef`; it does not rewrite the original collection fact. The
trusted evidence resolver must include all applicable findings and fail closed
on an unresolved or adverse current finding. A superseding evidence record does
not silently restore trust to the superseded record.

## 7. Trusted evaluator and assignment contract

### 7.1 Principal identity

G2 distinguishes an authenticated `PrincipalRef` from Stage 1
`ActorIdentity`. A principal reference conceptually contains a stable principal
identifier, identity issuer/security domain and the immutable authentication or
provider assertion reference used at the boundary. Secrets and bearer
credentials are not persisted in it.

An `ActorIdentity` may be mapped into Stage 1 only after the trusted boundary has
authenticated or otherwise approved the principal and recorded the mapping.
Caller-supplied `ActorIdentity` is not authentication, assignment authority,
independence proof, Human authority or authorization.

### 7.2 Assignment record

The public exact reference is an `AssignmentRef` containing the immutable
assignment identity and complete-record fingerprint. The fingerprint has the
same collision/replay role as `EvidenceRecordRef.record_fingerprint`.

M2 records an immutable supporting record shaped conceptually as:

```text
TrustedEvaluatorAssignmentRecord
  assignment_id: stable immutable identity
  record_fingerprint: canonical digest of the complete record
  evaluation_id: exact reserved Evaluation identity
  target: exact Run/Outcome/Effect identity + EntityVersion, or trusted EvidenceRef
  method: EvaluationMethodRef plus material tool/provider version constraints
  evaluator_principal: authenticated PrincipalRef
  stage1_evaluator_identity: trusted ActorIdentity mapping
  requested_by_principal: authenticated PrincipalRef
  assigned_by_principal: authenticated assignment authority
  request_ref: immutable request/causation provenance
  assignment_policy: exact policy identity + version
  producer_relationships: exact producing/collecting principals and relation facts
  independence_decision: decision identity + status + evidence refs
  issued_at: trusted time
  not_after: expiry | absent
  supersedes: prior assignment identity | absent
```

The independence decision must be made by an authority permitted by the exact
assignment policy. At minimum it exact-binds the Evaluation identity, target,
method, assigned evaluator and known producing/collecting principals. Matching
actor IDs, shared credentials/security domain, delegated execution, or another
policy-prohibited relationship fails assignment. Unknown relationship facts
fail closed when independence is required.

### 7.3 Assignment use and replay

- An assignment is valid only for its exact Evaluation identity, target and
  method/version constraints.
- Creation, start and completion resolve the assignment from trusted storage;
  they do not accept a complete assignment record from the caller.
- Expired, revoked, superseded, unresolved or policy-version-incompatible
  assignments fail closed.
- Reuse with an altered record under the same assignment identity is an identity
  collision. Exact replay is idempotent only for the same operation and exact
  bindings.
- An assignment cannot be replayed for a different Evaluation, target snapshot,
  method version or evaluator principal.
- The assigned evaluator cannot mint its own trusted assignment or independence
  decision.

Revocation is a separate immutable `AssignmentRevocationRecord` that exact-binds
the assignment reference, revoking authority, policy identity/version, reason,
evidence and trusted time. Supersession and revocation never edit the issued
assignment. Assignment resolution must load complete applicable
supersession/revocation history and fail closed if it is incomplete or
ambiguous.

## 8. Proposed public and trusted contracts

Names below are design-level names, not frozen Python APIs. M1-M5 may refine
spelling and representation while preserving every semantic field and rule.

| Boundary | Caller-visible input/output | Trusted dependency and duty |
| --- | --- | --- |
| M1 evidence intake | `EvidenceSubmissionClaim` -> exact `EvidenceRecordRef` and caller-safe provenance view | Collector/verifier authenticates source, anchors integrity, exact-binds scope, persists immutable record |
| M1 evidence read | exact `EvidenceRecordRef` -> caller-safe record view | Loads the exact record and applicable later trust findings; no caller-supplied record body |
| M2 assignment request/read | assignment request claim -> exact `AssignmentRef` and caller-safe view | Authenticates principals, evaluates independence under exact policy, persists immutable assignment |
| M3 Evaluation create/start/complete | existing G1-style submissions plus exact evidence/assignment refs | Resolves records, checks current validity and exact bindings, constructs canonical Stage 1 request/context |
| M4 effective-use query | exact `EvaluationRef` or current Evaluation ID -> `AuthoritativeEffectiveUseView` | Loads a consistent authoritative history slice and invokes Stage 1 derivation |
| M5 Outcome disposition | exact Outcome validation lineage + exact effective-use observation + policy request + Human decision where required | Revalidates all current bindings in the write transaction and invokes Stage 1 disposition semantics |

Trusted inputs returned to a G1 binder must be immutable values loaded or
produced inside the trusted boundary. A caller may refer to their identities,
but cannot supply their authoritative bodies.

## 9. Exact binding contract

| Operation | Values that must be exact-bound | Fail-closed checks |
| --- | --- | --- |
| Evidence intake | Evidence identity; full integrity anchor; source/provider; collector/version; observed and collected times; exact target identity/version; material method/tool/provider versions; producing/collecting principals | Identity collision; unverifiable/mutable anchor; unknown source; target mismatch/currentness failure; missing material version; caller-declared trust |
| Assignment issuance | Assignment identity; Evaluation identity; exact target/version; evaluator principal and Stage 1 mapping; producer/collector relations; method/version constraints; assignment policy/version; request/issuer; independence decision; validity | Fabricated or unauthenticated principal; self-assignment; prohibited/unknown relationship; stale target/method/policy; duplicate altered identity |
| Evaluation creation | Evaluation ID and initial version; exact target/version; method/version; assignment ID; trusted evidence record refs/anchors; producer provenance; creation request/correlation | Assignment/evidence unresolved, stale, revoked or cross-scoped; target no longer current; binder changes caller fields; replay differs |
| Evaluation start | Exact `EvaluationRef`; persisted target and method; current assignment; assigned evaluator; independence decision; input evidence records | Stale Evaluation version; evaluator substitution; assignment expiry/revocation; input or target mismatch |
| Result completion | Exact pre-transition `EvaluationRef`; persisted target; exact assignment/evaluator; method/tool/provider versions actually used; exact evidence refs and anchors; immutable `EvaluationResult`; completion decision provenance | Result/evidence/method/evaluator substitution; new or missing evidence; stale target or Evaluation; altered exact replay |
| Conflict/invalidation/arbitration | Exact Evaluation/member versions; current conflict-set identity/version; complete member set; arbitration lineage; invalidation identities; policy/version and evidence refs | Omitted history; stale conflict set; cross-Evaluation record; incomplete/ambiguous lineage; partial multi-member write |
| M4 effective-use resolution | Exact current Evaluation snapshot; latest version of every applicable conflict set; all relevant arbitration and invalidation records; one durable observation token; Stage 1 derived view | Incomplete or inconsistent history; concurrent change; duplicate identities; ambiguous terminal arbitration; unresolved conflicts; invalidation |
| M5 Outcome disposition | Exact `OutcomeValidationLineage`; exact Outcome version; exact Evaluation/version/target; M4 view and durable observation token; disposition policy identity/version/decision; authenticated Human decision when required | Favorable verdict used alone; stale Outcome/Evaluation/history; candidate substitution; policy substitution; fabricated Human/evaluator identity |

An exact binding is equality over typed identities and versions, not similarity,
shared correlation alone, or a caller assertion. When an opaque provider or
method version materially affects reproducibility or trust, it is part of the
binding.

## 10. Trust-source responsibility table

| Fact | Allowed authoritative source | Caller role | Durable requirement |
| --- | --- | --- | --- |
| Evidence bytes/content digest | Approved collector or independent verifier | May nominate payload/location | Exact algorithm + digest and collection provenance |
| External receipt/revision | Authenticated provider adapter or independent observation mechanism | May nominate locator/receipt | Provider namespace, immutable ID/revision, verification mechanism/version and times |
| Observation time | Trusted collector/provider receipt | May claim a time | Preserve source time and boundary collection time distinctly |
| Target identity/version | Authoritative repository plus trusted binder | Supplies desired exact ref | Re-resolve exact/current snapshot where currentness is required |
| Producing/collecting principal | Authenticated integration/collector mapping | May provide labels | Persist stable principal refs and mapping provenance |
| Evaluator identity | Authenticated identity/provider boundary | May claim identity | Persist principal ref and Stage 1 identity mapping |
| Evaluator assignment | Authorized assignment provider under exact policy | May request assignment | Immutable assignment, issuer, policy/version, validity and request provenance |
| Independence/relationship | Authorized policy decision using trusted principal/relationship facts | May disclose relationships | Exact decision, facts/evidence, decider and policy/version |
| Method/tool/provider version | Assignment plus trusted execution/result adapter | May request/claim method | Persist assigned and actually used identities/versions; require compatibility |
| Evaluation lifecycle | Stage 1 transition engine and lifecycle service | May request transition | Exact version, authority decision, semantic guard, event and receipt |
| Effective-use eligibility | M4 authoritative loader plus Stage 1 derivation | May request query | Consistent history basis and observation token |
| Outcome disposition policy | Trusted policy authority/provider | May request disposition | Exact policy/version, decision and evidence |
| Required Human acceptance | Independently authenticated Human authority | Cannot be supplied by Worker/evaluator label | Exact Human principal, scope, decision, time and policy-decision binding |

No single row implies authority over another row.

## 11. Authoritative effective-use resolver boundary

M4 must expose a resolver that accepts an exact `EvaluationRef` or resolves a
current Evaluation ID itself. Callers do not supply conflict sets, arbitration
records, invalidation records, a `complete=true` flag, or an
`EvaluationEffectiveUseView` as authoritative input.

Within one persistence-consistent observation, the resolver must:

1. load the exact current Evaluation snapshot, or reject a stale exact ref;
2. enumerate every conflict-set identity whose durable current version contains
   the Evaluation, then select exactly one latest authoritative version per ID;
3. load all arbitration records required for the Evaluation-specific lineage,
   including referenced priors needed to prove completeness and ordering;
4. load all invalidation records for the Evaluation;
5. validate identities, versions, membership, lineage, uniqueness and referential
   consistency;
6. call the accepted Stage 1 `derive_evaluation_effective_use(...)` unchanged;
7. return the exact Evaluation/version, derived view, exact history basis and a
   durable observation token/revision; and
8. expose only caller-safe provenance, never credentials or private provider
   assertions.

The persistence adapter must provide either a transactional consistent snapshot
or an equivalent revision/watermark plus recheck that proves all reads belonged
to one authoritative observation. A series of unrelated repository reads with
no completeness/currentness proof is insufficient.

The returned `AuthoritativeEffectiveUseView` therefore contains, at minimum,
the exact `EvaluationRef`, Stage 1 `EvaluationEffectiveUseView`, exact current
conflict-set refs, supporting and terminal arbitration IDs, invalidation IDs,
and the durable observation token/revision. The history identifiers are a basis
for audit and stale-write detection, not a caller-reusable assertion of
completeness.

The resolver fails closed, returning no eligible effective judgment, when:

- history enumeration cannot prove completeness;
- no unique latest conflict-set version exists;
- a referenced record is missing, duplicated, cross-scoped or inconsistent;
- arbitration lineage is incomplete, cyclic or has ambiguous terminal records;
- an applicable conflict is unresolved;
- any applicable invalidation exists;
- the Evaluation or supporting history changes during resolution; or
- storage/provider failure prevents an authoritative read.

M5 must not trust a previously returned view by value. Its disposition write
must transactionally verify the exact Evaluation/version and history observation
token (or recompute under the same write transaction), matching the existing
Stage 1 persistence pattern that compares the supplied observation with durable
current effective use.

## 12. Persistence impact decision

**Decision: G2 requires new durable governance/integration supporting records
and typed query ports. Existing lifecycle repository ports are not sufficient.**

The reason is structural:

- `EvidenceRef` intentionally stores no integrity, source, collection, target,
  method or principal provenance;
- `ActorIdentity` intentionally proves no authentication or assignment;
- existing `Repository` ports expose only the six lifecycle entities and exact
  versions;
- the closed supporting-record persistence set currently includes Evaluation
  conflict/arbitration/invalidation and Effect records, not trusted evidence or
  evaluator assignment; and
- M4 needs authoritative enumeration and consistent-snapshot queries that the
  current `EvaluationRepository` interface does not expose.

M1 therefore owns an evidence-provenance record contract, exact-read/query port,
append-only/idempotent persistence behavior and adapter migration. M2 owns the
parallel evaluator-principal/assignment contract and port. M4 owns authoritative
history-enumeration and consistent-observation ports for current conflict,
arbitration and invalidation history.

These are supporting governance/integration records under the existing six
entities. They have immutable identities, append-only correction/revocation
records and exact references, but no independent lifecycle state machine. They
must not be added to `LifecycleEntity`, the 43-state inventory or the 99 accepted
transition/creation variants. SQL/table/codec choices and migrations are deferred
to separately released implementation TaskSpecs.

Persistence invariants for future implementation are:

- canonical encoding and closed type registration;
- unique immutable identity and exact-replay idempotency;
- altered replay rejected without overwriting the original;
- append-only correction, supersession and revocation meaning;
- atomic persistence with the authoritative operation where a partial write
  could create false trust;
- exact historical readback and authoritative current/history enumeration;
- optimistic concurrency or consistent-snapshot protection; and
- no public raw-write path.

## 13. Adversarial matrix

| Attack or failure | Required detection/binding | Required outcome |
| --- | --- | --- |
| Fabricated evaluator identity | Authenticate principal and load trusted mapping; ignore caller label as authority | Reject before assignment/use; retain claim only if audit policy requires |
| Fabricated trusted assignment | Resolve immutable assignment from trusted store and verify issuer/policy | Reject; caller-provided assignment body or `trusted` flag is non-authoritative |
| Worker self-validation | Compare authenticated evaluator with producer/collector/Worker relationships under exact policy | Reject or mark independence unresolved; no Evaluation start/completion where independence is required |
| Same evidence identity with altered integrity metadata | Compare complete canonical record fingerprint and anchor | Reject as identity collision; preserve original record |
| Stale evidence against newer entity version | Compare evidence target scope with exact current/required target version | Reject; require newly collected/rebound evidence record |
| Cross-entity or cross-candidate evidence substitution | Compare typed target identity/version and Outcome validation lineage | Reject even if method, digest or correlation matches |
| Method/version substitution | Compare assignment, evidence collection method and actual result method/tool/provider versions | Reject; no compatible-by-name fallback |
| Omitted conflict/arbitration/invalidation history | Resolver enumerates authoritative history itself | Fail closed; caller cannot manufacture completeness |
| Stale conflict-set version | Select durable latest version in consistent observation | Reject stale reference/view and require re-resolution |
| Ambiguous arbitration | Stage 1 derivation plus complete lineage detects multiple terminals/inconsistency | Return ineligible with no effective judgment |
| Replay of old assignment/evidence authority | Check exact Evaluation/target/method/policy scope, validity and supersession/revocation | Reject as stale/cross-scoped; exact same operation only may be idempotent |
| Favorable verdict used as direct Outcome acceptance | Require M4 eligible view plus explicit disposition-policy decision and Stage 1 transition | Reject direct acceptance; judgment and policy remain separate |
| Required Human acceptance fabricated by Worker/evaluator identity | Authenticate Human principal independently and exact-bind decision to policy/Outcome/Evaluation | Reject; actor label cannot satisfy Human authority |
| Mutable external locator presented as integrity proof | Require immutable provider revision/receipt or independently anchored observation | Keep as caller claim or reject authoritative use |
| Collector fabricates source or time | Require approved collector identity/version and verifiable provider assertion where policy demands | Reject or keep below trusted-provenance grade; audit collector failure |
| Assignment for target A reused on target B | Exact-bind assignment to Evaluation ID, typed target/version and method | Reject regardless of evaluator identity |
| Result adds unregistered evidence | Resolve every result `EvidenceRef` and compare exact approved scope | Reject completion |
| Evidence or assignment changes during use | Immutable records plus transactional currentness/revocation checks | Conflict/fail closed; no stale success |
| Cross-Evaluation arbitration/invalidation substitution | Verify exact Evaluation/member identities and observed versions | Reject inconsistent history |
| Partial multi-member conflict/arbitration update | Preserve Stage 1 atomic batch requirement | Roll back all affected records/transitions |
| Provider/storage unavailable or history enumeration incomplete | Treat inability to prove as absence of authority, not absence of conflict | Return unavailable/ineligible; never optimistic success |

## 14. Milestone implications

### M1 — Durable evidence provenance intake

M1 may implement the public claim, trusted evidence record, integrity-anchor
variants, collector/verifier boundary, exact read/query port, durable adapter and
adversarial identity/scope/replay tests frozen here. It must not implement
evaluator assignment or treat evidence registration as Evaluation authority.

### M2 — Trusted evaluator identity and assignment binding

M2 may implement principal mapping, assignment provider/record, independence
facts, policy/version binding, validity/revocation read behavior and adversarial
self-assignment/substitution tests. It must not create a general identity product
or let `ActorIdentity` become authentication.

### M3 — Trusted Evaluation execution/result intake

M3 may connect exact M1 evidence and M2 assignment records to existing G1
Evaluation create/start/complete operations. It must use Stage 1 transitions and
preserve caller/trusted separation, exact replay and optimistic concurrency.

### M4 — Durable authoritative effective-use resolver/query

M4 may implement the authoritative history loader, consistent observation token,
caller-safe result and fail-closed cases in section 11. It must call, not replace,
`derive_evaluation_effective_use(...)`.

### M5 — Evidence-backed Outcome disposition bridge

M5 may bind the exact M4 observation to `OutcomeValidationLineage`, an exact
disposition-policy identity/version/decision and independently authenticated
Human acceptance when required, then invoke existing Stage 1 disposition
semantics. A verdict or resolver view alone is insufficient.

Every milestone still requires a fresh durable TaskSpec, exact launch baseline,
allowed paths and independent acceptance. This design candidate releases none of
them.

## 15. Unresolved questions

There are no unresolved architecture or trust-boundary questions blocking M0.
The following are intentionally deferred bounded implementation selections, not
permission to weaken this contract:

- concrete class, table, index and migration names;
- the initial digest-algorithm and external-provider allowlists;
- the first embedded/service authentication adapter and transport;
- the canonical encoding version and observation-token representation; and
- caller-safe error and pagination shapes for history/provenance queries.

Each choice belongs to the milestone that implements it and must preserve the
frozen semantic fields, fail-closed behavior and framework-neutral boundary.

## 16. ARCHITECTURE STOP

**Status: none discovered.** This design can be implemented with supporting
governance/integration records and ports under the existing six entities and
accepted Stage 1 semantics.

Future work must stop before implementation and obtain a separate durable ADR or
governance decision if it discovers a requirement for any of the following:

- a seventh core domain entity;
- a new Objective, Task, Run, Outcome, Evaluation or Effect lifecycle state or
  transition;
- weakened exact-version, append-only history, replay or currentness semantics;
- caller-controlled trust, authentication, assignment or authority;
- a constitutional trust-model change;
- real Effect dispatch, occurrence or reconciliation behavior inside G2; or
- a material change to Symphony-K's framework-neutral governance/control-plane
  identity.

Provider-specific inability to supply stable identity, integrity or provenance
is not grounds to weaken this design. That provider or evidence form must fail
conformance or remain a caller claim.
