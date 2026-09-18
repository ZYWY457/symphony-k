# AI and Maintainer Handoff

This workflow is model-, account- and vendor-neutral. No chat transcript,
private memory, model state or prior account context is a source of truth. A
fresh maintainer must be able to resume from durable repository and TaskSpec
artifacts alone.

## Required resume sequence

1. Read `CONSTITUTION.md`.
2. Read `STATUS.md`.
3. Read `AGENTS.md`.
4. Read `VISION.md` and `ARCHITECTURE.md`.
5. Read `docs/V1_PRODUCT_CONTRACT.md`.
6. Read `ROADMAP.md` and `docs/DEVELOPMENT_PATH.md`.
7. Read `docs/REFERENCE_WORKFLOWS.md`.
8. Read relevant core beliefs, accepted ADRs and accepted designs.
9. Read the G2 parent plan
   `docs/exec-plans/planned/g2-trusted-evaluation-evidence.md`.
10. Read the accepted M0 design
    `docs/design-docs/g2-trusted-evaluation-evidence-boundary.md` and its
    acceptance record, then the accepted M1 lineage described below.
11. Read Issue #111 in full, execution handoff comment `5724161554`, and r4
    path-correction comment `5724343805` for the current repository refresh.
    Treat #115 only as the required future independent review gate for an exact
    #111 candidate.
12. Verify repository identity, exact launch baseline, clean worktree, allowed
    paths, readiness and remote authority before mutation.

If a required source cannot be read or the baseline conflicts with the current
TaskSpec, stop before mutation.

## Product identity and strategic continuity

Symphony-K is a framework-neutral governance and trust control plane for
agentic work. External agents, orchestrators and runtimes determine how work is
attempted. Symphony-K determines what may become authoritative, which evidence
is admissible for an exact scope, which consequential action is allowed, what
happened, and how history is reconstructed.

The long-term goal is continuous: make agentic work reliable, governable,
verifiable, attributable and reconstructable. The strategic transition changed
the ownership boundary. Earlier work leaned toward Symphony-K owning planning,
routing, scheduling, Agent/runtime execution, sandboxing and recovery
mechanics. Current product ownership focuses on authority, exact
identity/version, trusted evidence and Evaluation, consequential Effects,
authorization versus occurrence, uncertainty/reconciliation and append-only
causal history.

Historical orchestration and Stage 2 sandbox work remains attributable and
useful. It is not rewritten as an error or as if the current product identity
always existed.

A Symphony-K-owned generic Planner, Router, Agent runtime, workflow engine or
production sandbox runtime is not a mandatory v1 prerequisite. Such mechanisms
may remain external, optional or reference implementations without acquiring
governance authority.

## Integration principles

### Internal rigor, external simplicity

Symphony-K may maintain strict exact refs, immutable fingerprints, trusted
provenance, conflict history, replay, concurrency, authorization/occurrence
separation, reconciliation and causal audit records internally. Ordinary
integrators should use small supported operations, stable typed refs, trusted
adapter boundaries and caller-safe errors rather than reconstruct the complete
domain or persistence graph.

External simplicity never allows caller-controlled trust, weaker exactness or
omitted authoritative history.

### Own the semantics; reuse the mechanisms

Symphony-K owns guarantees such as:

- claim != fact;
- capability != authority;
- Evaluation != disposition;
- authorization != occurrence;
- execution failure != non-occurrence;
- uncertainty != failure;
- compensation != erasure;
- evidence exact-binds identity/version; and
- historical meaning remains causally reconstructable.

It normally reuses IAM/authentication, databases, object storage, queues/event
buses, RPC/HTTP frameworks, workflow and Agent runtimes, sandbox providers,
secret managers, logging, tracing, metrics and cloud scheduling behind thin
adapters.

Mechanism reuse does not outsource semantic authority. IAM may authenticate a
principal but cannot decide Outcome disposition or evidence eligibility. A
database stores records but does not define trust semantics. Runtime success is
not Outcome acceptance. Provider/API success is not automatically proven Effect
occurrence.

## Current accepted state

- Stage 1 governance kernel is COMPLETE; accepted boundary
  `987f927905cadcedd473f2ba3270f56908b7f6b9`.
- Constitution v0.2 and ADR-0009 are accepted.
- Strategic transition R1-R5 is COMPLETE AND HUMAN ACCEPTED; final strategic
  reconciliation is `b5ee78f7febae1346c771fa6060fcb3e18ea56f3`.
- G1/M1 governance SDK/facade is COMPLETE / ACCEPTED at
  `62133cdfc7abac6bf7d1ce4666b5953192ffc9d1`.
- G2/M0 is COMPLETE / ACCEPTED at design boundary
  `9c36fbcfac3854271af8eb15dca08f6a9ec2eca2`.
- G2/M1 is COMPLETE / ACCEPTED at implementation boundary
  `83a67c9fc98b1de7b42ad65772d8956f9b721915`.
- G2/M1 accepted-truth reconciliation is
  `67f91f00ed3d6491f4451b801a19ae20ac409905`; this does not replace the M1
  implementation boundary.
- G2/M2-M6 are NOT RELEASED.
- G3 is NOT RELEASED.
- Issue #111 revision
  `r4 - strategic-narrative-cold-start-refresh-path-correction` is the current
  released repository-refresh TaskSpec. Its candidate is not accepted until
  independent review under #115.

## Accepted G1/M1 facade boundary

The public facade provides typed exact refs for all six core entities,
caller-controlled submissions separated from trusted Stage 1
authority/context construction, supported Run/Outcome/Evaluation mutations
through an injected trusted binder, exact/current reads, caller-safe errors,
exact lineage binding, replay/idempotency and optimistic-concurrency
preservation, and explicit unsupported real Effect dispatch.

It does not expose public Run completion or Outcome acceptance, permit callers
to manufacture trusted Stage 1 authority, add lifecycle semantics or define G2
trust policy.

## Accepted G2/M0 and M1 boundary

M0 froze the trusted evidence/evaluator contract and threat boundary. M1 adds
durable evidence provenance intake with:

- caller-claim/trusted-provider separation through an injected collector and
  verifier;
- immutable `EvidenceRef` and fingerprint identity;
- exact target identity/version and evidence-dependency binding;
- current digest policy at trusted-use time;
- coherent evidence-chain read snapshots;
- append-only findings and correction/supersession provenance;
- exact replay and collision rejection;
- atomic SQLite record/operation persistence without fake lifecycle events;
  and
- caller-safe provider error sanitization.

M1 does not provide evaluator assignment, G2 Evaluation create/start/complete
integration, the M4 authoritative effective-use resolver, Outcome disposition,
Human acceptance, or Effect dispatch/occurrence/reconciliation. Evidence
registration is not lifecycle or acceptance authority.

Current G2 sequence:

```text
M0 contract and threat-boundary freeze — COMPLETE / ACCEPTED
-> M1 durable evidence provenance intake — COMPLETE / ACCEPTED
-> M2 trusted evaluator identity and assignment — NOT RELEASED
-> M3 trusted Evaluation execution/result intake — NOT RELEASED
-> M4 authoritative effective-use resolver/query — NOT RELEASED
-> M5 evidence-backed Outcome disposition bridge — NOT RELEASED
-> M6 stage acceptance/reconciliation — NOT RELEASED
```

M1 acceptance and roadmap order do not release M2.

## Historical and current TaskSpec lineage

The following distinctions are mandatory:

```text
Task discovery != execution authority
Parent plan != released TaskSpec
Design acceptance != implementation authority
Candidate existence != accepted truth
External execution success != authoritative completion
Historical accepted asset != current execution authority
Roadmap order != released TaskSpec
```

Current and historical lineage:

- Issue #79 is closed SUPERSEDED / NOT RELEASED. Its old Stage 2 runtime-first
  authority must not be reused.
- Issues #100/#102/#103 preserve G1 implementation, correction and
  reconciliation history.
- Issues #105/#106/#107 preserve M0 design, independent acceptance and
  reconciliation history.
- Issue #108 is the original M1 TaskSpec. Candidate
  `e5402b6415ab76a7fed5635949cfea335db2b5c6` is historical **NOT ACCEPTED /
  CORRECTION REQUIRED** under #109, durable record #108 comment `5723629306`.
- Issue #110 supplied forward correction
  `83a67c9fc98b1de7b42ad65772d8956f9b721915`; #112 independently accepted it,
  findings none, in #110 comment `5723875385`.
- Issue #113 reconciled accepted truth at
  `67f91f00ed3d6491f4451b801a19ae20ac409905`. Issue #114 independently accepted
  that reconciliation, findings none, in #113 comment `5724140703`; finalization
  is #113 comment `5724156994`.
- Issues #108, #110, #113 and #114 are completed historical lineage, not
  current execution authority.
- Issue #111 r4 is the current released repository/docs/metadata refresh from
  exact baseline `67f91f00ed3d6491f4451b801a19ae20ac409905`, with handoff comment
  `5724161554` and durable path-correction comment `5724343805`.
- Issue #115 is the required independent review gate after an exact #111
  candidate exists. The #111 Worker must not execute or pre-claim that review.

## Current TaskSpec boundary

Issue #111 authorizes changes only to:

```text
README.md
VISION.md
ARCHITECTURE.md
ROADMAP.md
docs/DEVELOPMENT_PATH.md
docs/V1_PRODUCT_CONTRACT.md
docs/README.md
AGENTS.md
STATUS.md
docs/AI_HANDOFF.md
pyproject.toml
docs/design-docs/g2-trusted-evaluation-evidence-boundary.md
docs/exec-plans/planned/g2-trusted-evaluation-evidence.md
```

It authorizes one local candidate with message
`docs(project): refresh strategic narrative and cold-start truth`. It does not
authorize a push, remote ref update, Issue/PR mutation, tag/release, #115 review,
source/test change or M2/G3 release.

If a current-facing contradiction requires another path, report `TASKSPEC PATH
CORRECTION REQUIRED`. If the narrative can only be made true by changing the
Constitution, accepted ADR meaning, Stage 1 lifecycles, six entities, Human
irreversible-Effect rule or source code, report `ARCHITECTURE STOP`.

## Historical Stage 2 boundary

ADR-0008 and the accepted Stage 2 M1/M1C sandbox design remain accepted
execution-provider security/conformance assets and an optional/reference path.
They do not restore the old runtime-first delivery sequence or make a
Symphony-K-owned production sandbox mandatory for v1. Future implementation
requires a fresh bounded TaskSpec, normally under G7.

## Read-only cold-start acceptance checklist

With only repository read access, a fresh maintainer must be able to report:

- what Symphony-K is and is not;
- the strategic goal that remained continuous and the ownership boundary that
  changed;
- why claims, capabilities, Evaluations, authorization and provider success do
  not automatically become authority or occurrence truth;
- which semantics Symphony-K owns and which mechanisms it normally reuses;
- accepted Stage 1, G1/M1, G2/M0 and G2/M1 boundaries;
- the rejected original M1 candidate and accepted forward correction;
- that #113/#114 are completed and #111 is the current released TaskSpec;
- that #115 is a future independent review gate;
- that M2-M6 and G3 are NOT RELEASED;
- exact allowed paths, baseline and remote-mutation boundary; and
- that no private chat or model memory is required.

## Handoff evidence

Every completed Worker/design report must identify:

```text
TaskSpec reference
TaskSpec access mode
TaskSpec precondition
starting baseline
exact candidate and parent
changed paths
validation performed/results
stale-search interpretation
unresolved risks
final repository/worktree state
remote mutation (exact action or none)
```
