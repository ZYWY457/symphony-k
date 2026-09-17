# G2 — Trusted Evaluation and Evidence Integration

Status: **G2 implementation PLANNED / NOT RELEASED; G2/M0 COMPLETE / ACCEPTED**.

Accepted M0 design: [`g2-trusted-evaluation-evidence-boundary.md`](../../design-docs/g2-trusted-evaluation-evidence-boundary.md)
at exact boundary `9c36fbcfac3854271af8eb15dca08f6a9ec2eca2`.
Independent acceptance: [Issue #105 comment `5717950150`](https://github.com/ZYWY457/symphony-k/issues/105#issuecomment-5717950150)
under Issue #106 — **ACCEPT**, findings none. This records independent design
acceptance, not separate Human acceptance or implementation completion.
Issue #105 preserves design execution; #106 preserves review; #107 is the
bounded accepted-truth reconciliation TaskSpec.

**G2/M1 is PLANNED / NOT RELEASED.** A fresh bounded TaskSpec with an exact
launch baseline is required before source/test mutation. M1 starts with durable
evidence provenance intake under the accepted M0 contract and must not silently
implement M2-M5.

Planning authority: Issue #104 — `G2 Planning — Trusted Evaluation and Evidence Delivery Path`.

Planning baseline: `eaea5390a088a71fe4108c2b84812253032a287a`.

Accepted prerequisite: G1/M1 implementation boundary `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`, independently accepted on Issue #102 comment `5714651540`.

This parent Exec Plan defines G2 sequencing and evidence expectations. It is not implementation authority. Every implementation milestone requires its own fresh durable TaskSpec with an exact starting HEAD, allowed paths, validation, adversarial tests, and remote-mutation boundary.

## Objective

Turn trusted independent Evaluation/evidence from an internal semantic capability into a supported governance integration boundary without weakening Stage 1 authority, exact-version, conflict, arbitration, invalidation, effective-use, replay, concurrency, or history semantics.

G2 must make it possible for a supported integration to answer, from durable authoritative state rather than caller assertion:

- what evidence was observed;
- by which collector/source and under which method/version;
- which exact Run/Outcome/Effect or Evaluation target snapshot the evidence concerns;
- which evaluator identity/assignment is trusted for the Evaluation;
- whether the Evaluation result is exact, current, conflicted, arbitrated, invalidated, or eligible for effective use;
- which exact effective judgement and policy decision may support an Outcome disposition.

## Existing accepted substrate

### Stage 1

Stage 1 already provides the semantic authority that G2 must reuse:

- Evaluation lifecycle and exact `EntityVersion` semantics;
- Evaluation result content and `EvidenceRef` references;
- conflict-set, arbitration and invalidation records;
- `derive_evaluation_effective_use(...)` over a complete history slice;
- persistence validation that binds current Evaluation snapshots to authoritative conflict/arbitration/invalidation history;
- Outcome validation/disposition semantic records that consume exact Evaluation observations, effective-use state, policy decisions and optional Human acceptance.

G2 must not duplicate these semantics in a parallel state machine.

### G1

G1 already provides:

- exact public refs for Objective, Task, Run, Outcome, Evaluation and Effect;
- caller-controlled Evaluation/evidence submission DTOs;
- an injected trusted binder boundary for canonical Stage 1 request/context construction;
- supported Evaluation creation, start and result-submission paths;
- exact/current reads and caller-safe normalized errors;
- stale, superseded, cross-entity, replay and optimistic-concurrency preservation.

G2 extends the trusted integration boundary around these surfaces; it does not replace them.

## Threat model and trust boundary

G2 must remain safe when a caller or external Worker:

- fabricates an evaluator identity or claims independence it does not have;
- submits an `EvidenceRef` whose content/source cannot be trusted;
- reuses evidence collected for a different entity, candidate, version, method or policy context;
- submits evidence that was valid for an older snapshot but is stale for the current disposition;
- omits conflict, arbitration or invalidation history to manufacture a favorable effective judgement;
- substitutes an Evaluation result produced by a different method/version or target;
- replays an old trusted assignment or prior authority as if it were current;
- attempts to convert a favorable Evaluation verdict directly into Outcome acceptance without a separate disposition-policy decision;
- supplies a Worker self-report and labels it independent evidence.

The system must fail closed at these boundaries.

## Core architectural rules

1. **Evidence submission is not trust.** A caller-supplied reference or payload is a claim until provenance and integrity are established by a trusted collector/provider or independently verifiable durable record.
2. **Evidence should be immutable-addressable where practical.** Content digests, immutable external receipt IDs, signed provider identifiers or equivalent stable anchors are preferred. G2 must not require one universal content store.
3. **Exact scope is mandatory.** Trusted evidence and Evaluation results must bind to exact target identity/version plus relevant method/policy version where applicable.
4. **Evaluator trust is produced inside the trusted boundary.** Caller-controlled `ActorIdentity` values are claims, not authentication or assignment authority.
5. **Independence is explicit provenance.** Worker and evaluator identities, execution path, collector/source and assignment relationship must be attributable enough to detect prohibited self-validation and obvious correlated substitution.
6. **No universal judge.** Evaluation methods remain opaque/versioned. Deterministic tests, external state reads, specialist tools, Humans and semantic/LLM evaluators may coexist.
7. **No caller-manufactured completeness.** A public effective-use resolver must load authoritative current conflict/arbitration/invalidation history itself; callers cannot assert that their supplied history slice is complete.
8. **Judgment and policy remain distinct.** An Evaluation verdict does not itself decide Outcome acceptance/rejection. Outcome disposition continues to require the existing Stage 1 policy-decision semantics and Human acceptance where required.
9. **Stage 1 remains lifecycle authority.** G2 may bind trusted inputs, resolve durable evidence/effective-use state and expose supported operations, but it must not bypass Stage 1 creation/transition authority.
10. **No real Effect dispatch.** G2 may evaluate an Effect target, but authorization/dispatch/occurrence/reconciliation is G3.

## Planned milestone path

### G2/M0 — Contract and threat-boundary freeze

**Status: COMPLETE / ACCEPTED** at `9c36fbcfac3854271af8eb15dca08f6a9ec2eca2`,
independently reviewed under #106 on #105 comment `5717950150`. The requirements
below preserve the historical M0 delivery contract; acceptance releases no
implementation milestone.

**Purpose:** freeze the integration contract before implementation.

Required design decisions:

- public trusted-evidence record/reference shape;
- trusted collector/source provenance boundary;
- evaluator principal and assignment provenance;
- exact target/version/method binding rules;
- integrity anchors and supported external-evidence references;
- caller-visible trusted/effective-use query shape;
- unsupported cases that must fail closed;
- whether any persistence extension is required and why it does not alter Stage 1 semantics.

Required evidence:

- reviewed data-flow/trust-boundary diagram;
- adversarial matrix covering fabrication, stale evidence, substitution, omitted history, replay and self-validation;
- explicit confirmation that no new core entity/lifecycle is introduced.

Exit: reviewed contract only. No later milestone is released automatically.

### G2/M1 — Durable evidence provenance intake

**Purpose:** create a supported governance-layer intake/catalog for evidence provenance.

The milestone should support, at minimum:

- stable evidence identity/reference;
- integrity anchor where available;
- collector/source identity and source kind;
- observation/collection timestamp;
- exact target identity/version scope;
- method/tool/provider identity/version when material;
- producing/collecting principal provenance;
- durable readback sufficient for later Evaluation binding.

The record/catalog may live in the governance/integration layer and may require persistence support, but must not become a seventh core lifecycle entity.

Adversarial evidence:

- same evidence ID with altered integrity metadata fails;
- evidence for target A cannot bind to target B;
- evidence for version N cannot silently authorize version N+1;
- caller self-labeling evidence as trusted is insufficient;
- replay is idempotent only for an exact identical provenance record.

### G2/M2 — Trusted evaluator identity and assignment binding

**Purpose:** make evaluator identity/assignment an authenticated or boundary-produced fact rather than a caller claim.

The milestone should define/inject a trusted provider that can bind:

- evaluator principal;
- Evaluation method identity/version;
- assignment/request provenance;
- relationship to producer/Worker sufficient to enforce declared independence constraints;
- relevant authorization/policy decision provenance already expected by Stage 1.

Adversarial evidence:

- fabricated privileged/evaluator `ActorIdentity` cannot obtain assignment;
- Worker cannot self-assign as independent evaluator where policy forbids it;
- stale assignment/method version fails closed;
- assignment for one Evaluation/target cannot be replayed for another.

### G2/M3 — Trusted Evaluation execution/result intake

**Purpose:** connect G1 Evaluation create/start/complete surfaces to durable evidence and evaluator provenance.

Required behavior:

- Evaluation creation binds exact target and trusted assignment;
- result completion binds exact Evaluation version, exact target snapshot, method/version and evidence provenance;
- every referenced evidence item is resolvable through the trusted provenance surface;
- Stage 1 transition engine remains the lifecycle authority;
- unsupported trust states fail closed rather than being downgraded to caller claims.

Adversarial evidence:

- result with stale Evaluation version rejected;
- target substitution rejected;
- evidence substitution rejected;
- method/version substitution rejected;
- producing/evaluator principal substitution rejected;
- identical exact replay preserves existing idempotency semantics.

### G2/M4 — Durable effective-use resolver/query

**Purpose:** expose authoritative effective-use state without requiring callers to provide or understand complete private history.

Current Stage 1 `derive_evaluation_effective_use(...)` is pure and intentionally cannot prove repository completeness. G2 therefore needs a supported resolver that:

- loads the exact current Evaluation snapshot;
- loads authoritative current applicable conflict-set versions;
- loads relevant arbitration history;
- loads relevant invalidation history;
- invokes the accepted Stage 1 derivation;
- returns a caller-safe view with exact Evaluation/version and provenance references;
- fails closed on incomplete, inconsistent or ambiguous durable history.

Adversarial evidence:

- omitted conflict history cannot manufacture eligibility;
- stale conflict-set version rejected;
- ambiguous terminal arbitration remains ineligible;
- invalidated Evaluation remains ineligible;
- cross-Evaluation arbitration/invalidation substitution rejected;
- concurrent change after observation causes conflict/version mismatch rather than stale success.

### G2/M5 — Evidence-backed Outcome disposition bridge

**Purpose:** provide a supported trusted integration path from current effective Evaluation state into the existing Outcome disposition semantics.

Required behavior:

- bind the exact `OutcomeValidationLineage`;
- bind exact Evaluation snapshot and authoritative effective-use view;
- bind an explicit disposition-policy identity/version and decision;
- require Human acceptance when the existing policy decision says it is required;
- invoke the accepted Stage 1 Outcome transition semantics rather than writing state directly;
- expose ACCEPTED/REJECTED only after all exact evidence/effective-use/policy/authority preconditions hold.

Adversarial evidence:

- favorable verdict alone cannot self-accept an Outcome;
- stale/superseded Outcome cannot be accepted through old evidence;
- Evaluation for candidate A cannot dispose candidate B;
- stale effective-use observation fails closed;
- policy version/decision substitution rejected;
- required Human acceptance cannot be fabricated by Worker/evaluator identity.

### G2/M6 — Stage acceptance and reconciliation

**Purpose:** independently prove the whole G2 boundary before G3 release.

Required evidence:

- focused G2 legal-flow suite;
- full regression suite;
- adversarial matrix from M0 executed against the supported public boundary;
- independent security/trust review;
- Human stage-exit acceptance where governance rules require it;
- durable accepted-truth reconciliation updating status/roadmap/handoff docs.

Only after M6 reconciliation may G3 be considered for release.

## Delivery path table

| Order | Milestone | Primary contract | Depends on | Release condition |
| ---: | --- | --- | --- | --- |
| 0 | M0 Contract/threat freeze | trust model + public integration contract | accepted G1 | COMPLETE / ACCEPTED under #105/#106; design only |
| 1 | M1 Evidence provenance | durable trusted evidence reference/catalog | M0 accepted | fresh M1 TaskSpec |
| 2 | M2 Evaluator binding | trusted evaluator/assignment provider | M0, normally M1 | fresh M2 TaskSpec |
| 3 | M3 Evaluation intake | exact evidence + assignment + result lifecycle binding | M1/M2 | fresh M3 TaskSpec |
| 4 | M4 Effective-use resolver | authoritative durable history -> effective-use view | M3 + existing Stage 1 history | fresh M4 TaskSpec |
| 5 | M5 Outcome disposition bridge | effective use + policy + optional Human acceptance -> Stage 1 disposition | M4 | fresh M5 TaskSpec |
| 6 | M6 Exit/reconciliation | adversarial evidence + accepted-truth reconciliation | M1-M5 accepted | explicit exit/reconciliation authority |

Parallelism is allowed only when a future TaskSpec proves that shared contracts and protected paths do not overlap unsafely. Roadmap order does not imply automatic release.

## Expected implementation ownership

Likely G2 code ownership, subject to each milestone TaskSpec, is primarily:

- `src/symphony_k/governance/**` for public/trusted integration contracts and resolvers;
- `src/symphony_k/persistence/**` only if durable provenance storage/query cannot be expressed through existing ports, and only through an explicitly authorized milestone;
- tests focused on the G2 public boundary plus existing Stage 1 regression suites.

`src/symphony_k/domain/**` should remain unchanged unless M0 proves a true semantic gap. Any required new Stage 1 semantic concept, lifecycle change or constitutional trust change stops G2 implementation and requires a separate architecture/governance decision before code mutation.

## Non-goals

G2 does not implement:

- a universal evidence schema or verdict taxonomy;
- a full identity/authentication product, login/session/JWT stack or organization RBAC system;
- generic Planner, Router, scheduler or Agent runtime;
- sandbox/provider runtime;
- real Effect authorization/dispatch/occurrence/reconciliation;
- audit export/reconstruction productization;
- the general cross-stage conformance framework;
- a seventh core entity;
- new Objective/Task/Run/Outcome/Evaluation/Effect lifecycle states.

## Stage exit contract

G2 is complete only when a fresh maintainer can, through supported governance surfaces and durable records:

1. register/resolve independently attributable evidence for an exact target/version;
2. establish a trusted evaluator assignment independently of caller self-assertion;
3. create/start/complete an Evaluation whose result exactly binds trusted evidence and method provenance;
4. query authoritative current effective-use state without supplying private history slices;
5. demonstrate conflict/arbitration/invalidation effects on eligibility;
6. disposition an Outcome only through exact effective-use + policy + required Human authority;
7. demonstrate stale/superseded/cross-entity/tampered/replayed substitutions fail closed; and
8. reproduce the accepted G2 adversarial evidence from repository instructions.

G2 acceptance does not authorize G3 or real external Effect dispatch.