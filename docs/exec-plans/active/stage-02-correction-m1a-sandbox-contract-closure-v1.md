# Stage 02 M1A — Sandbox Contract Closure Correction

**Status:** CORRECTION CANDIDATE - independent review / Human approval pending

**TaskSpec:** GitHub Issue #78

**TaskSpec revision:** `r1 - stage-02-m1a-contract-closure`

**TaskSpec access mode:** `direct-read`

**Observed Issue updatedAt:** `2026-09-16T09:02:22Z`

**Parent:** `docs/exec-plans/active/stage-02-sandbox-execution.md`

**Corrects:** Issue #77 M1 candidate at
`243bc63bc37758f4621181364c26fbcadfdcb871`

**Constitutional baseline:** `constitution-v0.1`

## Objective and authority

Close the three independent review findings without reopening Stage 2 scope:
deadline/termination ownership, a real trusted live-workspace read channel, and
complete public M2 result/state/store contracts. Add the bounded upstream
comparison requested by the TaskSpec as provider-selection evidence only.

This plan authorizes documentation correction only. It does not accept
ADR-0008 or the detailed design, execute blocked Issue #79, implement a sandbox
provider, install or operate Docker/WSL/a VM, change Stage 1 semantics, or
replace ADR-0002's first provider.

## TaskSpec and preflight evidence

- Repository: `ZYWY457/symphony-k`.
- Issue URL: `https://github.com/ZYWY457/symphony-k/issues/78`.
- Fresh complete direct read observed `updatedAt`
  `2026-09-16T09:02:22Z`.
- Required starting HEAD:
  `243bc63bc37758f4621181364c26fbcadfdcb871`.
- Required parent: `3c42c3f95c141a52d1d733917a5956481088af1f`.
- Required title: `docs(architecture): specify sandbox execution contract`.
- Origin resolved to `https://github.com/ZYWY457/symphony-k.git`; worktree was
  clean; Git, Python 3.12.7 and uv 0.11.2 were callable.
- Docker/WSL/VM/administrator access was not probed or required.

TaskSpec precondition: PASS.

## Bounded correction

### Finding A — enforcement and termination

Name a co-located trusted Linux host guardian, outside the Worker cgroup, as
the monotonic deadline owner. It arms before Worker start and persists an exact
Run/workspace/sandbox-generation/command/request binding. Caller or adapter loss
does not disarm it. TERM is followed by bounded grace and whole-container
kill/removal when command-tree termination cannot be proved. Container/cgroup
absence, not process-group signaling alone, is the reuse boundary.

### Finding B — workspace read channel

Keep bounded tmpfs. On the initial native-Linux/local-daemon profile, a
co-located privileged collector obtains the verified container init PID from
the authenticated Docker Engine API, freezes the exact container, pins and
opens `/proc/<pid>/root/workspace` with Linux descriptor/openat2-style
no-follow traversal, revalidates identity/generation/mount/freeze throughout,
and streams the retained bytes while hashing the same stream. Normal removal
follows durable manifest/snapshot commit. Emergency loss records unavailable
candidate artifacts and performs safety cleanup without fictional export.

### Finding C — implementation-ready public contract

Define all result/observation/operation/store types, immutable bounded
representations, legal value combinations, request identity/fingerprint rules,
generation/lease fencing, STARTING cancellation, unknown/terminal timestamps,
cleanup independence, typed observation payloads and operation completeness.
M2 owns provider-neutral values/ports plus an in-memory semantic Fake; M3 owns
durable runtime metadata and physical restart/Docker evidence.

## Upstream comparison boundary

Primary documentation was rechecked on 2026-09-16. Repository HEAD/release and
license metadata were observed for OpenAI Codex, OpenClaw and Docker docs. No
upstream runtime code was copied, vendored or claimed audited. The comparison
does not report memory/latency savings; it defines later M3 measurement fields
and preserves the approved Docker-first/substitutable-provider boundary.

## Planned evidence additions

The corrected design extends the existing test catalog for adapter death with
no restart, management loss, process-group escape, supervisor/control-channel
interference, stale deadline identity, STARTING/natural-exit/cancel races,
workspace disappearance, stale container identity, freeze failure, partial
copy, unsafe metadata and emergency loss before preservation. They remain
future UNIT/FAKE/DOCKER specifications, not executed evidence.

## Validation and disposition

Required validation is documentation-only: whitespace, exact changed paths,
full staged diff, Markdown fences, tracked links/anchors, state/type/operation
consistency, traceability, candidate wording and protected-path audit. Stage 1
tests and all future sandbox adverse cases are deliberately not executed.

Final candidate truth:

```text
Stage 1 = COMPLETE, unchanged
Stage 2 = ACTIVE - M1A correction candidate
ADR-0008 = PROPOSED
Sandbox design = corrected CANDIDATE
M1 acceptance = PENDING
M2 code = NOT STARTED
Issue #79 = BLOCKED
Stage 2 complete = NO
Stage 3 = PLANNED
```
