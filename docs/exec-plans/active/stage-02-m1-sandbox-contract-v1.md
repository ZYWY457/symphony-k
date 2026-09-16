# Stage 02 M1 — Sandbox Execution Contract Candidate

**Status:** ACTIVE - design candidate work

**TaskSpec:** GitHub Issue #77

**TaskSpec revision:** `r1 - stage-02-m1-design-start`

**TaskSpec access mode:** `direct-read`

**Parent:** `docs/exec-plans/active/stage-02-sandbox-execution.md`

**Starting baseline:** `60b647f825d2eed4dc56a4d3087f165545a1ea88`

**Constitutional baseline:** `constitution-v0.1`

## Objective

Activate Stage 2 for design only and produce a reviewable sandbox execution
boundary. The candidate must make lifecycle, identity, ownership, workspace,
artifact, resource, network, telemetry, cleanup and failure semantics concrete
before any runtime implementation becomes eligible.

## Authority and disposition

This plan authorizes documentation and architecture-candidate work only. It
does not authorize changes under `src/` or `tests/`, dependency changes, Docker
installation or mutation, container execution, Stage 3 activation, or runtime
implementation. The planned outputs are:

```text
docs/adr/0008-stage-2-sandbox-execution-boundary.md
docs/design-docs/sandbox-execution-v1.md
```

ADR-0008 must remain Proposed and the detailed design must remain Candidate
until independent review and explicit Human approval are durably recorded.

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
| Human acceptance of proposed interface/defaults | no runtime implementation | M1 independent review / Human approval |
| Host/kernel/daemon enforcement capability | fail closed as unsupported | M3 runtime preflight and Docker integration |
| Writable storage byte/inode quota portability | do not claim ordinary volume quota | M3 profile implementation; M4 adverse proof |
| Crash/leak discovery completeness | require ownership labels plus metadata design | M3 implementation; M4 crash testing |
| Recovery reuse trust | preserved workspace remains untrusted | Stage 5 recovery design |
| Network/credential needs for AgentDriver | only `NONE`; no secrets | Stage 3 scoped network/credential design |

## Candidate completion evidence

M1 is complete only as a local documentation candidate when the exact two
ordered commits exist, validation passes, protected paths are unchanged and the
worktree is clean. That result remains pending independent review and Human
approval. It does not complete Stage 2 or authorize M2 runtime work.
