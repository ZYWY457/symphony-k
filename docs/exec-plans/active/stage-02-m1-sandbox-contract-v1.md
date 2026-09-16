# Stage 02 M1 — Sandbox Execution Contract

**Status:** M1 ARCHITECTURE/DESIGN HUMAN ACCEPTED; Stage 2 remains active

**TaskSpec:** GitHub Issue #77

**TaskSpec revision:** `r1 - stage-02-m1-design-start`

**TaskSpec access mode:** `direct-read`

**Parent:** `docs/exec-plans/active/stage-02-sandbox-execution.md`

**Starting baseline:** `60b647f825d2eed4dc56a4d3087f165545a1ea88`

**Constitutional baseline:** `constitution-v0.1`

**Accepted technical design baseline:**
`b52df98530d8ce742b07d7f6c399ccd5b54e643b`

**Independent cumulative M1B technical review:** **ACCEPT**, recorded on
[Issue #81](https://github.com/ZYWY457/symphony-k/issues/81#issuecomment-5698811579)

**Human M1 design approval:** **APPROVED**, recorded on
[Issue #81](https://github.com/ZYWY457/symphony-k/issues/81#issuecomment-5699311994)

## Objective

Activate Stage 2 for design only and produce a reviewable sandbox execution
boundary. The candidate must make lifecycle, identity, ownership, workspace,
artifact, resource, network, telemetry, cleanup and failure semantics concrete
before any runtime implementation becomes eligible.

## Authority and disposition

This plan originally authorized documentation and architecture-candidate work
only. It did not authorize changes under `src/` or `tests/`, dependency
changes, Docker installation or mutation, container execution, Stage 3
activation, or runtime implementation. The planned outputs were:

```text
docs/adr/0008-stage-2-sandbox-execution-boundary.md
docs/design-docs/sandbox-execution-v1.md
```

At candidate production, ADR-0008 had to remain Proposed and the detailed
design had to remain Candidate until independent review and explicit Human
approval were durably recorded. Those gates were later satisfied on Issue #81
for the exact baseline above and reconciled by Issue #82. This does not release
Issue #79 or establish runtime isolation evidence.

## TaskSpec and preflight evidence

- Repository: `ZYWY457/symphony-k`.
- Issue URL: `https://github.com/ZYWY457/symphony-k/issues/77`.
- Fresh direct read observed Issue `updatedAt` `2026-09-16T07:50:33Z`.
- Required starting HEAD: `60b647f825d2eed4dc56a4d3087f165545a1ea88`.
- Required parent: `d7132d9fcb7a04172549e8e054982c4b683e95d5`.
- Required title: `docs(governance): harden product intent handoff`.
- Worktree was clean; Git, Python 3.12.7 and uv 0.11.2 were callable.
- ADR-0008 was unused at the required baseline.
- Docker was not probed because this is a design-only TaskSpec and explicitly
  prohibits Docker mutation and resource-abuse probes.

TaskSpec precondition: PASS.

## In scope

- activate the Stage 2 parent for M1 architecture/design;
- define provider-neutral typed contracts and lifecycle semantics;
- recommend a first fail-closed Linux-container profile behind a replaceable
  Docker adapter;
- specify workspace staging, ownership, retention and hostile artifact handling;
- specify `NONE` as the only initially supported runtime network profile;
- define bounded telemetry, failure normalization and targeted cleanup;
- produce requirement/test traceability and the proposed M2-M4 coding map;
- record source verification, evidence classes, limitations and approval questions.

## Out of scope and protected boundaries

- runtime code, executable tests or prototypes;
- changes to Stage 1 domain or persistence semantics;
- AgentDriver, verification runtime, recovery decisions, Effect dispatch,
  Secret Broker, routing, planning, UI/API or Stage 3 work;
- Docker installation/configuration, image pull/build, container launch or
  resource-abuse execution;
- Constitution, core-belief, Architecture or Product Contract rewrites;
- remote repository, Issue, PR, branch, tag or release mutation.

Protected paths include `src/`, `tests/`, `pyproject.toml`, `uv.lock`, accepted
ADRs 0001-0007, completed Stage 1 plans and planned Stage 3-14 parents.

## Governing constraints

- Workers remain untrusted; provider observations are not authoritative domain
  transitions or acceptance evidence.
- A sandbox belongs to one Run, while workspace lifetime is separate and any
  later reuse requires Stage 5 recovery authority and verification.
- The trusted control-side Docker adapter may reach the daemon; the Worker must
  not receive its socket, credentials or management endpoint.
- Handles and caller-supplied actor labels grant no authority. Every provider
  operation requires trusted metadata lookup plus Run/workspace ownership fencing.
- Unknown execution or cleanup state remains unknown and fails closed; timeout
  or client disconnect is not proof of process termination.
- Docker is a first provider, not product identity or proof of perfect isolation.

## Proposed decisions to review

1. One active command per sandbox, with explicit conflict rejection.
2. Opaque execution-plane UUID identities bound to existing `TaskId` and `RunId`.
3. Staged inputs plus a provider-managed writable workspace; never an
   unrestricted host repository/home/database mount.
4. Digest-pinned approved images, explicit entrypoint/argv and no implicit pull.
5. Linux containers with non-root user, dropped capabilities, no privileged or
   device access, read-only root, controlled writable paths, no-new-privileges,
   default seccomp, private PID/IPC namespaces and mandatory resource limits.
6. `NONE` as the initial supported network profile; all other typed policies
   fail closed until separately designed and implemented.
7. Quiesced artifact collection through a trusted reader with hostile metadata
   rejection and hashes over exactly the retained bytes.
8. Provider-owned resource labels plus external ownership metadata for targeted,
   idempotent reopen/cleanup; never global prune.

Alternatives and tradeoffs must be explicit in the ADR/design candidate rather
than silently treated as accepted facts.

## Milestones

1. Activate parent/current-status governance in an isolated commit.
2. Add Proposed ADR-0008 and Candidate sandbox design.
3. Add complete lifecycle, enforceability, scenario and traceability matrices.
4. Validate links, structure, scope, wording and staged diffs.
5. Stop after the two local candidate commits for independent review.

## Validation contract

- inspect `git diff --check`, name/status and statistics;
- inspect every changed file and every staged diff before commit;
- use only explicit-file staging;
- validate Markdown fences and tracked relative links;
- confirm the moved parent has no stale planned-path reference;
- confirm current status is consistent across repository navigation files;
- confirm twelve Stage 3-14 parent plans remain under `planned/`;
- confirm requirement/test traceability and candidate-versus-accepted language;
- confirm no protected path changed from the required baseline;
- do not claim that future unit/fake/Docker tests executed.

## Risk ownership

| Risk or unresolved decision | Safe M1 disposition | Blocking owner |
| --- | --- | --- |
| Human acceptance of interface/defaults | accepted at exact baseline; no runtime isolation evidence | Resolved by Issue #81 independent review and Human approval |
| Host/kernel/daemon enforcement capability | fail closed as unsupported | M3 runtime preflight and Docker integration |
| Writable storage byte/inode quota portability | do not claim ordinary volume quota | M3 profile implementation; M4 adverse proof |
| Crash/leak discovery completeness | require ownership labels plus metadata design | M3 implementation; M4 crash testing |
| Recovery reuse trust | preserved workspace remains untrusted | Stage 5 recovery design |
| Network/credential needs for AgentDriver | only `NONE`; no secrets | Stage 3 scoped network/credential design |

## Candidate completion evidence

M1 first became complete as a local documentation candidate when the exact two
ordered commits existed, validation passed, protected paths were unchanged and
the worktree was clean. That candidate later passed independent cumulative M1B
technical review and received explicit Human approval at the exact accepted
baseline. M1 design acceptance does not complete Stage 2 or authorize M2
runtime work.

### Produced design artifacts

- [ADR-0008: Stage 2 Sandbox Execution Boundary](../../adr/0008-stage-2-sandbox-execution-boundary.md)
  — Accepted.
- [Sandbox Execution v1](../../design-docs/sandbox-execution-v1.md) — Human
  Accepted M1 architecture/design contract at
  `b52df98530d8ce742b07d7f6c399ccd5b54e643b`.

The detailed design owns requirement IDs `SBX-R01` through `SBX-R15`, future
test IDs `T-U01` through `T-U06`, `T-F01` through `T-F07`, and `T-D01` through
`T-D16`. Those tests are specifications only; none executed in M1.

### Actual M1 validation evidence

- TaskSpec direct-read identity/revision and exact starting baseline passed.
- Repository command runner, Git, Python 3.12.7 and uv 0.11.2 passed preflight.
- ADR-0008 collision check passed before mutation.
- Official Docker resource, run, none-network, rootless, seccomp and tmpfs
  documentation was consulted on 2026-09-16; claims are marked documented, not
  locally tested.
- Markdown fences and tracked relative links passed repository-local inspection.
- No stale planned Stage 2 parent reference remains; twelve Stage 3-14 parent
  files remain under `planned/`.
- Cached name/status, cached whitespace and full cached diff were inspected
  before each local commit.
- Baseline-to-candidate protected-path audit confirms no `src/`, `tests/`,
  dependency, Constitution, core-belief, accepted ADR, Architecture, Product
  Contract/reference workflow, completed Stage 1 or planned Stage 3-14 change.
- No Docker command, container/image/daemon mutation, resource-abuse fixture or
  Stage 1 test suite was run for this documentation-only task.

### Proposed implementation sequence

```text
S2-M1 accepted design at b52df98530d8ce742b07d7f6c399ccd5b54e643b
  -> Issue #82 governance reconciliation
  -> explicit READY revision of currently BLOCKED Issue #79
S2-M2 typed contracts + workspace/artifacts + fake provider
S2-M3 Docker lifecycle + constraints + telemetry/cleanup
S2-M4 adverse Docker + crash/reopen + operational evidence
  -> milestone reconciliation
  -> independent Human Stage 2 Exit Review
  -> Stage 3 only after accepted exit and its own TaskSpec
```

The design document lists proposed production/test paths, prerequisites, likely
commit boundaries and completion evidence for M2-M4. Those are planning inputs,
not executable Issues or implementation authority.

## Independent review and M1A correction

Independent review of the Issue #77 candidate requested three corrections:

1. name an enforcement owner that survives caller/adapter loss and define
   whole-sandbox termination and race evidence;
2. define how a trusted collector actually reads the live bounded tmpfs and
   order preservation before normal removal; and
3. complete every public result/observation/store type and lifecycle rule used
   by the M2 boundary.

GitHub Issue #78, revision `r1 - stage-02-m1a-contract-closure`, authorizes the
bounded forward correction recorded in
`stage-02-correction-m1a-sandbox-contract-closure-v1.md`. The correction also
adds the requested primary-source backend comparison. It does not change the
Issue #77 TaskSpec or commits, accept ADR-0008/the design, authorize Issue #79,
or alter the Docker-first decision. M1 acceptance remained pending at that
historical M1A boundary.

## Independent review, continuity governance and M1B correction

The durable independent review in
`../../reviews/stage-02-m1a-613d71b-review.md` records REQUEST CHANGES against
candidate `613d71b90c36b573578f6fffb9a6c7dd9606478f` for:

1. Worker execution-set termination versus collection quiescence and final
   whole-sandbox absence;
2. independently executable deadline enforcement after guardian failure;
3. the first workspace lease/sandbox-binding bootstrap; and
4. confirmed no-process `START_FAILED` time/exit/stream semantics.

Issue #80 persisted that review and current queue truth; it did not resolve the
findings. GitHub Issue #81, revision
`r1 - stage-02-m1b-final-contract-correction`, authorizes the bounded final M1B
correction recorded in
`stage-02-correction-m1b-final-contract-v1.md`. Its technical commit is
`b52df98530d8ce742b07d7f6c399ccd5b54e643b`.

The design now walks the empty-store/bootstrap/success lifecycle, guardian-
failure deadline lifecycle and no-process start-failure lifecycle using defined
types, states, operations and metadata receipts. Added UNIT/FAKE/DOCKER cases
remain future specifications, not evidence executed by M1B. The old review
artifact remains REQUEST CHANGES evidence against the old candidate. The exact
M1B baseline `b52df98530d8ce742b07d7f6c399ccd5b54e643b` subsequently received
independent technical review **ACCEPT** and explicit Human M1 design approval on
Issue #81. Issue #79 remains BLOCKED / NOT RELEASED, runtime code remains NOT
STARTED, Stage 2 remains active and incomplete, and Stage 3 remains planned.
