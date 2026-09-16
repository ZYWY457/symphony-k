# Sandbox Execution v1

## Candidate status and authority

**Status:** Candidate - not an accepted implementation contract.

**Date:** 2026-09-16

**TaskSpec:** GitHub Issue #77, revision `r1 - stage-02-m1-design-start`

This document proposes the Stage 2 execution contract. It implements nothing,
does not report any Docker probe as executed, and does not authorize changes to
`src/` or `tests/`. [ADR-0008](../adr/0008-stage-2-sandbox-execution-boundary.md)
is Proposed. Independent review and explicit Human approval are the next gate.

Normative words in this candidate describe the proposed contract, not an
already accepted or tested implementation.

## 1. Evidence and decision taxonomy

| Class | Meaning in this document |
| --- | --- |
| Inherited requirement | Higher-authority repository rule that this design must satisfy |
| Proposed decision | Concrete M1 recommendation awaiting Human approval |
| Documented technical behavior | Behavior described by Docker's official documentation, not locally proved |
| Tested evidence | None for the proposed runtime; this TaskSpec prohibited container/probe execution |
| Unresolved question | Explicitly owned item with a fail-closed behavior and blocking milestone |

A Docker option, API response or Worker claim is not enforcement evidence. Real
claims require the M3/M4 observations and adverse tests identified below.

## 2. Inherited requirements

| ID | Requirement | Source |
| --- | --- | --- |
| SBX-R01 | Every Worker Run executes in an approved sandbox; host execution is not the default | `CONSTITUTION.md` section 4.4; `docs/adr/0002-sandboxed-worker-execution.md` |
| SBX-R02 | Docker is first provider, not permanent product identity | `docs/core-beliefs/EXECUTION_ISOLATION.md` “Sandbox Provider”; `ARCHITECTURE.md` section 6 |
| SBX-R03 | A sandbox belongs to one Run; workspace lifetime is distinct | `docs/core-beliefs/EXECUTION_ISOLATION.md` “Workspace and Sandbox Lifetime” |
| SBX-R04 | Workers do not control authoritative transitions, acceptance, permission or budget | `CONSTITUTION.md` sections 4.2, 4.5-4.7; `docs/core-beliefs/STATE_AND_AUTHORITY.md` |
| SBX-R05 | Route capability preflight precedes mutation and provider errors are normalized | `docs/adr/0006-capability-based-execution-routes-and-substrate-failover.md` |
| SBX-R06 | Default non-root, dropped capabilities, no privileged mode/root/socket mount, controlled writable paths | `docs/core-beliefs/EXECUTION_ISOLATION.md` “Default Restrictions” |
| SBX-R07 | CPU, memory, process, wall-time and output use are bounded | active Stage 2 parent “Security and trust requirements” |
| SBX-R08 | Network is typed policy; unsupported policy fails closed | `docs/core-beliefs/EXECUTION_ISOLATION.md` “Network” |
| SBX-R09 | Secrets are scoped capabilities and broad host inheritance is prohibited | `docs/core-beliefs/EXECUTION_ISOLATION.md` “Secrets” |
| SBX-R10 | Candidate artifacts/claims are not evidence or Evaluation verdicts | `docs/core-beliefs/TRUST_MODEL.md`; `docs/core-beliefs/VERIFICATION_MODEL.md` |
| SBX-R11 | Work may survive route failure only under explicit recovery and verification | `docs/core-beliefs/FAILURE_AND_RECOVERY.md`; ADR-0006 “Work and Artifact Preservation” |
| SBX-R12 | External Effect replay/commit is outside this provider | `docs/core-beliefs/EFFECTS_AND_SIDE_EFFECTS.md`; active Stage 2 parent “Out of scope” |
| SBX-R13 | Cleanup failure and unknown occurrence remain visible; history is not rewritten | `CONSTITUTION.md` sections 4.3, 4.10; active Stage 2 parent “Failure model” |
| SBX-R14 | Stage 2 proves isolation dynamically with fake and real Docker evidence | `docs/DEVELOPMENT_PATH.md` Stage 2; active Stage 2 parent “Validation strategy” |
| SBX-R15 | Stage 3 does not activate before Stage 2 Human Exit acceptance | `docs/DEVELOPMENT_PATH.md` Stage 2 exit; `docs/exec-plans/README.md` |

## 3. Planes, trust boundary and ownership

```text
trusted later orchestration caller
        |
        | typed request + authenticated service identity
        v
SandboxProvider port ---- trusted ownership metadata / observations
        |
        v
Docker adapter ---- Docker daemon API (trusted management channel)
        |
        v
Worker container (untrusted; no daemon socket/credentials/management endpoint)
```

The trusted caller planned for later stages is an application/run-control
service acting under scheduler/run-controller authority. Stage 2 supplies only
the port and records; it does not implement that later caller.

The provider has no dependency on persistence `UnitOfWork`, no lifecycle-state
setter and no right to create an authoritative DomainEvent. A later trusted
orchestration service may interpret provider observations and separately
request a legal domain transition. `exit_code == 0` means only that the
container command reported zero.

Every mutating/read operation validates this tuple against metadata held outside
Worker memory:

```text
(provider_id, task_id, run_id, workspace_id, sandbox_id[, command_id])
```

The caller authenticates to the trusted service boundary. The tuple proves
scope only after trusted lookup; a handle, container name, Docker label or
caller-supplied `ActorType` is never authorization. Resource labels are
discovery hints checked against the metadata record, not the source of truth.

## 4. Provider-neutral types

The signatures below are non-executable design notation. `TaskId`, `RunId`,
`ArtifactRef`, `EvidenceRef` and `ExecutionProfileRef` reuse the nominal/opaque
Stage 1 meanings in `src/symphony_k/domain/`. New IDs remain Execution Plane
types and do not add a domain entity or lifecycle edge.

```python
WorkspaceId = NewType("WorkspaceId", UUID)
SandboxId = NewType("SandboxId", UUID)
CommandId = NewType("CommandId", UUID)
ObservationId = NewType("ObservationId", UUID)
ProviderId = NewType("ProviderId", str)
IdempotencyKey = NewType("IdempotencyKey", UUID)
Sha256Digest = NewType("Sha256Digest", str)  # exactly "sha256:" + 64 lowercase hex
RelativePosixPath = NewType("RelativePosixPath", str)
UtcTimestamp = aware_datetime
```

All UUIDs are non-nil UUIDv4 values generated by the trusted provider boundary.
All byte counts are non-negative unsigned 64-bit integers. Durations use
integer milliseconds and are positive unless explicitly optional. Timestamps
are UTC with an offset. Relative paths use `/`, are normalized once for syntax,
and are still validated during descriptor-relative traversal.

Closed candidate enums are:

```text
EnvironmentClass = NATIVE_LINUX_DOCKER | ROOTLESS_LINUX_DOCKER |
                   DOCKER_DESKTOP_LINUX_VM | UNSUPPORTED
NetworkPolicyKind = NONE | DNS_ONLY | ALLOWLIST | PROXY_CONTROLLED |
                    FULL_INTERNET
WorkspaceRetention = DESTROY | EXPORT_FOR_REVIEW
SandboxPhase = ABSENT | ALLOCATING | CREATED | STARTING | READY | EXECUTING |
               STOPPING | STOPPED | DESTROYING | DESTROYED | UNKNOWN
CommandPhase = PENDING | STARTING | RUNNING | CANCELLING | EXITED |
               CANCELLED | UNKNOWN
CommandDisposition = EXITED_ZERO | EXITED_NONZERO | TIMED_OUT | CANCELLED |
                     START_FAILED | RESOURCE_LIMIT | UNKNOWN
```

Provider/policy/profile references are trimmed nonempty UTF-8 strings of at
most 256 bytes; `ProviderId` is restricted to lowercase ASCII letters, digits,
`.`/`-` and 1..64 characters. Relative paths are at most 4,096 UTF-8 bytes.
Command argv items are at most 32 KiB each and 128 KiB in aggregate. Environment
keys match `[A-Z_][A-Z0-9_]{0,63}`, values are at most 32 KiB each and the whole
mapping is at most 128 KiB. These bounds are validated before provider mutation.

### 4.1 Provider capabilities

```python
ProviderCapabilities(
    provider_id: ProviderId,
    contract_version: Literal["sandbox-v1"],
    environment_class: EnvironmentClass,
    supported_network_policies: frozenset[NetworkPolicyKind],
    supports_hard_memory_limit: bool,
    supports_hard_memory_swap_limit: bool,
    supports_cpu_quota: bool,
    supports_pid_limit: bool,
    supports_tmpfs_byte_limit: bool,
    supports_tmpfs_inode_limit: bool,
    supports_read_only_root: bool,
    supports_default_seccomp: bool,
    supports_no_new_privileges: bool,
    supports_private_pid_ipc: bool,
    supports_restart_discovery: bool,
    observed_at: UtcTimestamp,
    probe_evidence_refs: tuple[EvidenceRef, ...],
)
```

Capability values are trusted probe observations scoped to provider and
environment version. They expire on daemon/kernel/configuration change and do
not assert that a particular sandbox used the capability; create/start
observations must record the effective configuration too.

### 4.2 Resource, output and network limits

```python
ResourceLimits(
    cpu_millis_per_second: int,       # 100..4000; proposed default 1000
    memory_bytes: int,                # 64 MiB..8 GiB; default 512 MiB
    memory_swap_bytes: int,           # memory_bytes..8 GiB; default == memory
    pids_max: int,                    # 16..1024; default 128
    wall_time_ms: int,                # 100..3_600_000; default 900_000
    workspace_bytes: int,             # 16 MiB..2 GiB; default 512 MiB
    workspace_inodes: int,            # 128..100_000; default 50_000
    tmp_bytes: int,                   # 1 MiB..256 MiB; default 64 MiB
    tmp_inodes: int,                  # 32..20_000; default 4_096
)

OutputLimits(
    stdin_bytes: int,                 # 0..1 MiB; default 64 KiB
    stdout_retained_bytes: int,       # 0..16 MiB; default 1 MiB
    stderr_retained_bytes: int,       # 0..16 MiB; default 1 MiB
    diagnostic_retained_bytes: int,   # 1 KiB..256 KiB; default 32 KiB
)

NetworkPolicy(
    kind: NetworkPolicyKind,          # NONE | DNS_ONLY | ALLOWLIST |
                                      # PROXY_CONTROLLED | FULL_INTERNET
    policy_ref: str,
    policy_version: str,
)
```

Only `NONE` is supported initially. It creates no external network interface;
loopback inside the container remains. Every other enum value is valid contract
syntax but returns `UNSUPPORTED_CAPABILITY` before create. This distinction
prevents “known vocabulary” from being reported as implemented capability.

CPU quota and memory/PID/tmpfs ceilings are proposed hard limits when the
eligible environment proves them. CPU shares, IO weights and post-hoc usage
measurements are accounting/soft controls and cannot satisfy a hard-limit
requirement. Wall time is a trusted-controller deadline plus confirmed
termination, not a kernel quota. Output limits bound retention; continuous
draining prevents pipe backpressure while excess bytes are counted and dropped.

### 4.3 Workspace and sandbox specifications

```python
WorkspaceSpec(
    workspace_id: WorkspaceId,
    task_id: TaskId,
    run_id: RunId,
    input_snapshot_ref: ArtifactRef | None,
    retention: WorkspaceRetention,    # DESTROY | EXPORT_FOR_REVIEW
    lease_version: int,               # >= 1
)

SandboxSpec(
    sandbox_id: SandboxId,
    task_id: TaskId,
    run_id: RunId,
    workspace_id: WorkspaceId,
    execution_profile_ref: ExecutionProfileRef,
    image_digest: Sha256Digest,
    worker_uid: int,                  # 1..2^31-1; default candidate 65532
    worker_gid: int,                  # 1..2^31-1; default candidate 65532
    resources: ResourceLimits,
    outputs: OutputLimits,
    network: NetworkPolicy,
    env_allowlist: frozenset[str],
    provider_options_digest: Sha256Digest,
)

SandboxHandle(
    provider_id: ProviderId,
    sandbox_id: SandboxId,
    task_id: TaskId,
    run_id: RunId,
    workspace_id: WorkspaceId,
    generation: int,                  # >= 1; changes on recreate, never reused
)
```

Specifications are immutable after successful create. A change requires a new
sandbox identity and generation; changing route or Run requires a new `RunId`
under ADR-0006. A workspace lease is exclusive. A stale lease version or handle
generation returns `OWNERSHIP_MISMATCH` without touching the provider resource.

### 4.4 Command request and terminal result

```python
CommandRequest(
    command_id: CommandId,
    idempotency_key: IdempotencyKey,
    argv: tuple[str, ...],             # 1..256 items; each UTF-8, no NUL
    cwd: RelativePosixPath,            # beneath /workspace; default "."
    env: Mapping[str, str],            # <= 64 entries; key allowlisted
    stdin: bytes | None,               # bounded by OutputLimits.stdin_bytes
    timeout_ms: int,                   # <= ResourceLimits.wall_time_ms
)

CommandHandle(
    provider_id: ProviderId,
    sandbox_id: SandboxId,
    task_id: TaskId,
    run_id: RunId,
    workspace_id: WorkspaceId,
    sandbox_generation: int,
    command_id: CommandId,
    request_digest: Sha256Digest,
)

TerminalResult(
    command_id: CommandId,
    disposition: CommandDisposition,
    exit_code: int | None,
    started_at: UtcTimestamp | None,
    ended_at: UtcTimestamp,
    duration_ms: int | None,
    stdout_ref: ArtifactRef | None,
    stderr_ref: ArtifactRef | None,
    stdout_observed_bytes: int | None,
    stdout_retained_bytes: int,
    stdout_truncated: bool,
    stderr_observed_bytes: int | None,
    stderr_retained_bytes: int,
    stderr_truncated: bool,
    termination_confirmed: bool,
    normalized_failure: SandboxFailure | None,
    observation_refs: tuple[EvidenceRef, ...],
)
```

`argv` is passed to the container runtime API as an argument vector. It is never
concatenated into a host command. An explicit request such as
`("/bin/sh", "-lc", "...")` invokes a shell inside the sandbox only and is
subject to the same policy.

`*_observed_bytes` is exact only when the adapter saw stream EOF; disconnect or
lost telemetry makes it `None`. Retained bytes are always exact. The adapter
drains stdout and stderr concurrently until EOF or confirmed process-tree
termination, retains each prefix independently, increments observed counts
without retaining excess, and marks truncation. Output overflow does not stop
draining and does not invent a nonzero process exit; it yields
`OUTPUT_LIMIT_REACHED` telemetry/failure detail alongside the actual terminal
disposition when known.

### 4.5 Artifact collection

```python
ArtifactRequest(
    request_id: IdempotencyKey,
    include: tuple[RelativePosixPath, ...],
    max_files: int,                    # 1..10_000; default 1_000
    max_depth: int,                    # 1..64; default 32
    max_file_bytes: int,               # 1..256 MiB; default 64 MiB
    max_total_bytes: int,              # 1..1 GiB; default 256 MiB
)

ArtifactEntry(
    path: RelativePosixPath,
    kind: Literal["REGULAR_FILE", "DIRECTORY"],
    size_bytes: int,
    sha256: Sha256Digest | None,        # files only
    executable: bool,
    media_type: str | None,             # advisory, never trust authority
)

ArtifactManifest(
    manifest_id: UUID,
    task_id: TaskId,
    run_id: RunId,
    workspace_id: WorkspaceId,
    sandbox_id: SandboxId,
    command_id: CommandId | None,
    collected_at: UtcTimestamp,
    quiescence_observation_ref: EvidenceRef,
    entries: tuple[ArtifactEntry, ...],
    total_files: int,
    total_bytes: int,
    manifest_sha256: Sha256Digest,
)

ArtifactCollectionResult(
    disposition: Literal["COLLECTED", "REJECTED", "UNKNOWN"],
    manifest: ArtifactManifest | None,
    artifact_ref: ArtifactRef | None,
    rejection: SandboxFailure | None,
)
```

Directories are metadata only; archives are never implicitly expanded. If an
archive is explicitly requested as a regular file, it is collected as opaque
bytes and any future extraction must repeat path/link/size checks in a new
trusted boundary.

## 5. Provider operations

```python
class SandboxProvider(Protocol):
    def capabilities() -> ProviderCapabilities: ...
    def create_workspace(spec, key) -> WorkspaceRecord: ...
    def create_sandbox(spec, key) -> SandboxObservation: ...
    def start(handle, key) -> SandboxObservation: ...
    def execute(handle, request) -> CommandHandle | TerminalResult: ...
    def inspect(handle) -> SandboxObservation: ...
    def inspect_command(command_handle) -> CommandObservation | TerminalResult: ...
    def cancel(command_handle, key) -> CancellationResult: ...
    def collect(handle, request) -> ArtifactCollectionResult: ...
    def export_workspace(handle, key) -> WorkspaceExportResult: ...
    def destroy(handle, key) -> CleanupResult: ...
    def reopen_owned_resources(run_id) -> tuple[OwnedResourceObservation, ...]: ...
```

Every mutating call has an idempotency key stored with request digest and
result. Exact replay returns the prior result. Reuse with a different digest
returns `IDEMPOTENCY_CONFLICT`. An in-flight duplicate returns the same handle
or `OPERATION_IN_PROGRESS`; it never starts a second resource.

## 6. Provider-local state machines

These phases are observations about provider resources, not `RunState` and not
authoritative domain history.

### 6.1 Sandbox phases

```text
ABSENT -> ALLOCATING -> CREATED -> STARTING -> READY
READY -> EXECUTING -> READY
READY|EXECUTING -> STOPPING -> STOPPED
CREATED|READY|STOPPED|UNKNOWN -> DESTROYING -> DESTROYED
any nonterminal phase -> UNKNOWN when observation is lost
```

`FAILED_CREATE` is a terminal operation result, not proof that no partial
resource exists. The metadata record retains a cleanup obligation until owned
resource absence is confirmed.

### 6.2 Command phases

```text
PENDING -> STARTING -> RUNNING -> EXITED
RUNNING -> CANCELLING -> CANCELLED
STARTING|RUNNING|CANCELLING -> UNKNOWN
```

Only one command may be in `STARTING`, `RUNNING`, `CANCELLING` or `UNKNOWN` for
a sandbox. An unknown command blocks a new command until inspection proves it
terminal or fenced destruction removes the sandbox.

The approved image contains a minimal trusted PID 1 command supervisor. It
starts exactly one non-root Worker process group, reaps descendants and applies
termination to the entire group. Its control channel is adapter-owned and not
exposed as a Worker capability. `READY` after a command requires the supervisor
and provider to observe no surviving Worker process. If that cannot be proved,
the sandbox becomes `UNKNOWN`/cleanup-required and is never reused. M3/M4 must
validate this mechanism; a Docker client timeout or the end of one attached
process is insufficient.

### 6.3 Operation transition contract

| Operation | Allowed phase and ownership check | Result / duplicate behavior | Timeout, disconnect and retry | Evidence and cleanup; live resource possible? |
| --- | --- | --- | --- | --- |
| `create_workspace` | no record for ID; Task/Run exist and lease unclaimed | `WorkspaceRecord`; exact key replays | pre-response loss requires metadata lookup; never recreate blindly | allocation observations; partial staging cleanup; yes |
| `create_sandbox` | workspace lease valid; sandbox absent; all capabilities supported | `CREATED`; exact key replays; conflict rejected | inspect by immutable ID/labels before retry | effective config/image/ownership; partial container cleanup; yes |
| `start` | `CREATED`; full tuple/generation match | `READY`; repeated start on ready replays/observes | disconnect becomes `UNKNOWN`; inspect before retry | start/inspect observations; yes |
| `execute` | `READY`; no active/unknown command; cwd/env/limits valid | handle or terminal result; exact command replay | caller timeout triggers cancel workflow, not a second execute | ordered stream/start/exit evidence; yes |
| `inspect` | any known sandbox phase; full tuple match | current observation, including missing/unknown | read retry allowed; absence must match owned identity | inspected config/state; no mutation |
| `inspect_command` | known command and request digest | current/terminal observation | read retry allowed; unknown remains unknown | state/exit/stream completeness evidence |
| `cancel` | command `STARTING`, `RUNNING`, `CANCELLING` or `UNKNOWN` | confirmed cancelled, already terminal, or unknown | send TERM, bounded grace, then KILL; inspect process/container; race may return actual exit | signal/inspect evidence; yes until confirmed |
| `collect` | sandbox not executing; quiescence confirmed; lease valid | manifest/result; exact key replays | disconnect before durable manifest returns unknown; inspect storage before retry | walk/hash/copy observations; rejection cleanup; no new live process |
| `export_workspace` | not executing; retention explicitly `EXPORT_FOR_REVIEW` | immutable untrusted snapshot ref | no replay until snapshot identity checked | snapshot hash/size; partial export cleanup |
| `destroy` | owned resource in any non-destroyed phase | confirmed destroyed or cleanup failure/unknown; repeated confirmed destroy replays | target immutable provider ID; reconnect and inspect; never global prune | stop/kill/remove/absence observations; yes on failure |
| `reopen_owned_resources` | authenticated provider startup/reopen and Run scope | bounded observations only | safe repeat; does not resume Run | reconciles metadata/labels; cleanup decision remains external |

Cancellation race rule: if natural exit is observed before the cancellation
signal takes effect, return the actual `EXITED` result plus a “cancel lost race”
observation. If termination is signaled but EOF/absence cannot be confirmed,
return `UNKNOWN`, keep the cleanup obligation and block reuse.

## 7. Normalized failure contract

```python
SandboxFailure(
    code: SandboxFailureCode,
    phase: str,
    retryability: Literal["NO", "AFTER_INSPECT", "AFTER_ENVIRONMENT_CHANGE"],
    state_known: bool,
    resource_may_be_live: bool,
    safe_summary: str,
    diagnostic_ref: EvidenceRef | None,
)
```

Diagnostics are bounded to `diagnostic_retained_bytes`, redact configured
environment values, daemon credentials, host paths and secret-like values, and
remain lower-authority observations. Unknown state never becomes synthetic
success.

| Code | Trigger and terminal semantics | Retry / cleanup behavior |
| --- | --- | --- |
| `SUBSTRATE_UNAVAILABLE` | daemon/runtime cannot be reached before operation; no Worker start claimed | retry only after environment health change; inspect if request may have reached daemon |
| `UNSUPPORTED_CAPABILITY` | required hard limit, namespace, network or security mechanism absent | no start; fail closed; choose an eligible route/profile later |
| `INVALID_SCOPE` | malformed IDs/path/env/limits or impossible tuple | no provider mutation; not retryable without corrected request |
| `OWNERSHIP_MISMATCH` | trusted metadata does not match handle/resource/lease | touch nothing; security observation; not retryable with same handle |
| `IDEMPOTENCY_CONFLICT` | key reused with different request digest | touch nothing; caller defect; not retryable |
| `IMAGE_UNAVAILABLE` | approved digest is not locally present or inspect fails | no implicit pull; provisioning is separate; cleanup partial create |
| `IMAGE_POLICY_REJECTED` | mutable identity, root config, entrypoint/config or digest mismatch | no start; require approved image change |
| `CREATE_FAILED` | runtime create error | partial resource may exist; discover and targeted cleanup before retry |
| `START_FAILED` | container cannot start or effective config differs | stop/remove owned resource; no Worker execution result invented |
| `COMMAND_NONZERO_EXIT` | command reaches EOF with exit code other than zero | terminal command result, normally not provider-retryable |
| `COMMAND_START_FAILED` | argv/cwd executable cannot start after sandbox ready | terminal when confirmed; sandbox may remain reusable after inspection |
| `TIMEOUT` | trusted wall deadline reached | initiate cancel; terminal only when termination/EOF confirmed, else unknown |
| `CANCELLED` | requested termination is confirmed | terminal; retain actual signal/exit observations |
| `MEMORY_LIMIT_REACHED` | cgroup/runtime evidence shows OOM/limit event | terminal or unknown if disconnect; collect evidence and inspect before reuse |
| `PID_LIMIT_REACHED` | process creation denied/limit event observed | command may continue; cancel/inspect per policy; record exact observation |
| `CPU_LIMIT_ENFORCED` | throttling observed | telemetry, not command failure by itself; wall timeout remains independent |
| `STORAGE_LIMIT_REACHED` | tmpfs byte/block/inode exhaustion isolated by adverse fixture | terminal only from actual command result; collect evidence, then cleanup |
| `NETWORK_DENIED` | external access fails under `NONE` and adverse probe isolates network policy | expected denial observation; command result remains separate |
| `OUTPUT_LIMIT_REACHED` | either retained stream limit exceeded | continue drain; mark truncation; result can also be zero/nonzero/timeout |
| `ARTIFACT_REJECTED` | traversal/link/type/race/count/depth/size rule fails | no partial manifest; remove partial trusted copy; sandbox unchanged |
| `DAEMON_DISCONNECTED` | management channel lost after operation might have begun | state unknown; inspect by ownership after reconnect; no blind retry |
| `CLEANUP_FAILED` | stop/kill/remove/absence confirmation fails | resource may be live; persist obligation and escalate; never report destroyed |
| `INTERNAL_PROVIDER_ERROR` | adapter invariant or unexpected conversion error | fail closed; bounded diagnostic; inspect/cleanup based on last known phase |

Provider-specific messages may refine diagnostics but must not create new
Control Plane semantics without a reviewed contract version.

## 8. Workspace staging, retention and artifact safety

### 8.1 Workspace lifecycle

```text
DECLARED -> STAGING -> LEASED -> ACTIVE -> QUIESCING -> QUIESCED
QUIESCED -> EXPORTING -> EXPORTED_UNTRUSTED -> RELEASED
QUIESCED -> RELEASING -> RELEASED
any allocation/export phase -> CLEANUP_REQUIRED -> RELEASED | CLEANUP_FAILED
```

Workspace phase is provider metadata, not a domain state. `EXPORTED_UNTRUSTED`
means only that bounded bytes were captured with a manifest. It grants no
checkpoint, evidence, Outcome or recovery status.

The proposed first strategy is:

1. A trusted staging service resolves explicit input artifact IDs; caller host
   paths are never accepted.
2. It validates file type, path, count, depth and aggregate bytes into a
   provider-owned staging directory not visible to the Worker.
3. Sandbox create mounts bounded tmpfs at `/workspace` and `/tmp`, with explicit
   size/inode, uid/gid, `nosuid` and `nodev` options. `/tmp` is also `noexec`;
   `/workspace` may execute files because code Tasks require it.
4. Before Worker start, trusted adapter code imports staged regular files into
   `/workspace` and verifies the imported manifest. The host repository, home,
   SQLite store and credential directories are never mounted.
5. One sandbox owns the exclusive workspace lease. No second container mounts
   or imports it concurrently.
6. After confirmed quiescence, collection/export copies through the trusted
   reader. Normal disposition destroys tmpfs with the sandbox; explicit
   retention stores an immutable bounded snapshot outside Worker control.
7. A later sandbox may import a retained snapshot only after an explicit Stage
   5 recovery decision and required verification. A successor Run creates a new
   `WorkspaceId` owned by that `RunId` and records the source snapshot/reference;
   the original workspace ownership and old handle are never mutated or reused.

Creation failure cleanup is journaled step-by-step: staging allocation, input
copy, metadata record, container create and lease acquisition each register a
targeted compensating cleanup action. Failure never triggers broad directory
or daemon cleanup.

### 8.2 Hostile artifact algorithm

Collection requires a frozen lease plus confirmed absence of every untrusted
Worker process, or a provider-supported container freeze while the sandbox and
its tmpfs still exist. The adapter records that quiescence
observation, then uses a trusted helper outside the Worker namespace:

1. Reject empty, absolute, drive-qualified, NUL-containing, `.`/`..` escaping
   and non-normal relative request paths.
2. Open the workspace root once as a trusted directory descriptor.
3. Traverse each component descriptor-relative with no-follow semantics;
   never concatenate it into an arbitrary host path.
4. Reject symlinks, hardlinked files with link count other than one, sockets,
   FIFOs, block/character devices and any type except directory/regular file.
5. Enforce depth/file/individual/aggregate byte limits before and during copy.
6. Open the final regular file with no-follow behavior; compare identity/type
   metadata before and after the single streaming copy. Reject change.
7. Hash the exact bytes written to trusted artifact storage; `size_bytes` is the
   exact retained length. Never hash one read and export another.
8. Set trusted storage to non-executable by default while retaining an
   `executable` metadata bit from the source for later review.
9. Write the canonical manifest only after all entries and aggregate hash are
   complete. On any failure, discard partial output and emit
   `ARTIFACT_REJECTED`.

This closes simple resolve-then-open TOCTOU behavior. M4 must still attack
rename/link races and confirm the chosen OS primitives fail safely.

Archive path traversal is not applicable during v1 collection because archives
are opaque regular files. Any future extraction must reject absolute names,
parent traversal, links, special files, duplicate/colliding names, excessive
compression ratio, count, depth and aggregate expanded bytes.

## 9. Docker profile and enforceability

### 9.1 Proposed supported environment

| Environment | Candidate disposition |
| --- | --- |
| Native Linux host, Docker Engine API compatible with the implemented adapter, cgroup v2, required namespaces/seccomp/tmpfs features | M3 target; supported only after full preflight and M4 evidence |
| Rootless Docker on Linux | evaluation variant; not yet supported because resource/network/storage semantics need the same adverse matrix |
| Docker Desktop Linux containers on Windows or macOS | development-only candidate; Linux VM behavior is not claimed equivalent to native host containers |
| Native Windows containers or macOS processes | unsupported by sandbox-v1 |
| Host process fallback when Docker is absent/ineligible | prohibited |

Exact Docker Engine/API, Linux kernel and distribution versions are selected and
recorded by the M3 TaskSpec; M1 does not fabricate an untested support floor.
Any daemon/kernel/security/storage configuration change invalidates cached
capability evidence and requires preflight again.

### 9.2 Effective profile

The Docker adapter constructs the API request directly; it does not invoke a
host shell or interpolate Worker text into a CLI string. Proposed effective
properties are:

- approved `image@sha256:...` already provisioned; pull disabled;
- explicit numeric non-root user, no supplementary groups;
- `ReadonlyRootfs=true`;
- capability drop `ALL`, no capability additions;
- `Privileged=false`, no devices, no host PID, IPC or network namespace sharing;
- `no-new-privileges=true`, default seccomp retained, no unconfined override;
- `NetworkMode=none`, no exposed/published ports;
- memory and total memory+swap set to the same positive bound;
- CPU CFS quota derived from `cpu_millis_per_second`, not shares alone;
- explicit PIDs limit;
- bounded `/workspace` and `/tmp` tmpfs mounts;
- no bind mounts supplied by the Worker; no daemon socket or host root mount;
- explicit trusted supervisor entrypoint from the approved image; Worker argv
  is delivered as data to it and never extends an unreviewed image entrypoint;
- allowlisted environment values only; proxy/credential variables absent;
- healthcheck disabled unless the approved profile specifically defines a
  trusted bounded one; and
- deterministic ownership labels containing opaque IDs and schema version, with
  no secret values.

### 9.3 Requirement-to-enforcement matrix

| Requirement | Mechanism | Environment prerequisite | Observation/probe | Adverse test | Normalized result | Evidence location |
| --- | --- | --- | --- | --- | --- | --- |
| SBX-R01 no host Worker | Docker API-only execute; no local subprocess path | eligible daemon | process/cgroup/namespace identity | command tries host sentinel path | denied/missing; escape is blocker | `EVD-DKR-EXEC-*` |
| SBX-R06 non-root | numeric UID/GID plus image inspection | image supports UID | inspect config and `id` | attempt root-only write/action | permission denied or profile rejected | `EVD-DKR-UID-*` |
| SBX-R06 no privilege/caps/devices | drop ALL, unprivileged, empty devices | Linux capabilities/device cgroup | inspect effective config and `/proc` | mount, raw socket, device access | denied; unexpected success is safety failure | `EVD-DKR-PRIV-*` |
| SBX-R06 no socket/host mounts | mount allowlist constructed by adapter | daemon inspect trustworthy | inspect mounts from daemon and container | request socket/root/home mount | `INVALID_SCOPE` before create | `EVD-DKR-MOUNT-*` |
| SBX-R06 read-only root | read-only root plus bounded tmpfs paths | overlay/runtime supports flag | inspect and write probes | write outside allowed paths | read-only failure | `EVD-DKR-ROFS-*` |
| SBX-R07 memory/swap | hard cgroup memory; swap total == memory | cgroup support reported | inspect cgroup and bounded OOM fixture | allocate slightly over fixture cap | `MEMORY_LIMIT_REACHED` without host harm | `EVD-DKR-MEM-*` |
| SBX-R07 CPU | CFS quota, not shares | kernel scheduler/cgroup support | inspect quota and measured bounded load | CPU loop for fixed short duration | throttling telemetry; timeout remains separate | `EVD-DKR-CPU-*` |
| SBX-R07 PIDs | PIDs cgroup limit | kernel PIDs controller | inspect and bounded fork fixture | create up to cap+small margin | `PID_LIMIT_REACHED` | `EVD-DKR-PID-*` |
| SBX-R07 wall time | trusted monotonic timer, TERM/grace/KILL, inspect | controller clock and signal API | timestamps plus process/container inspect | bounded sleep beyond deadline | `TIMEOUT`, termination confirmed or unknown | `EVD-DKR-TIME-*` |
| SBX-R07 writable bytes/inodes | tmpfs `size`, `nr_blocks`/`nr_inodes`; memory cap | Linux tmpfs options supported | mount inspection and free/stat data | bounded writes and small-file fixture | `STORAGE_LIMIT_REACHED` | `EVD-DKR-STORE-*` |
| SBX-R07 output/log growth | attach streams drained; separate retention caps; daemon log disabled/bounded | runtime streaming API | retained/observed counts and daemon log inspect | finite stdout/stderr flood | exact truncation; no unbounded log | `EVD-DKR-OUT-*` |
| SBX-R08 network NONE | none network driver; no ports/proxies | none driver | inspect network plus route/interface view | loopback works; DNS/TCP external attempts | external denial; loopback retained | `EVD-DKR-NET-*` |
| SBX-R09 no secrets/env inheritance | explicit allowlist; construct env from empty base except reviewed runtime keys | adapter API | inspect environment with redaction | seed operator proxy/token then inspect | absent; presence is blocker | `EVD-DKR-ENV-*` |
| SBX-R10 artifact boundary | descriptor-relative no-follow quiesced collector | trusted helper primitives | manifest/copy/hash observations | traversal/link/race/device/size cases | `ARTIFACT_REJECTED` | `EVD-DKR-ART-*` |
| SBX-R13 cleanup | immutable IDs, ownership metadata/labels, targeted remove+absence check | daemon reconnect/inspect | resource inventory before/after | repeated teardown, adapter crash, daemon loss | confirmed destroyed or `CLEANUP_FAILED` | `EVD-DKR-CLEAN-*` |
| SBX-R02 replaceability | provider conformance suite has no Docker types at port | M2 fake provider | architecture/import check | second fake/provider behaviors | same normalized contract | `EVD-CONTRACT-*` |

Disk/inode pressure outside the bounded tmpfs—daemon metadata, image storage,
trusted snapshot storage and host filesystem exhaustion—remains a trusted-host
operational risk. M3 must place trusted artifact/snapshot storage under separate
operator quotas/monitoring; Stage 2 must not claim the container limit alone
protects all host storage. Ordinary Docker volumes are not treated as quota
evidence.

### 9.4 Documented versus tested Docker behavior

Official Docker documentation consulted on 2026-09-16 describes:

- containers have no resource constraints by default; memory and CPU limits
  require explicit configuration and kernel support;
- memory hard/soft and swap settings differ, and CPU shares are relative/soft;
- the `none` network creates only loopback in the container;
- bind mounts are read-write by default and reflect writes onto the host;
- `--privileged` grants broad capabilities/device access, while capabilities
  can be dropped individually or as `ALL`;
- the default seccomp profile is an allowlist-style, moderately protective
  profile and depends on daemon/kernel seccomp support;
- Linux tmpfs supports size and inode options, counts toward the memory cgroup,
  is removed when the container stops, and may use host swap; and
- environment flags can copy a named host value when no explicit value is
  supplied, so the adapter must never use that inheritance form.

Source record (all pages are the live, unversioned Docker Docs view; no stable
page revision was exposed, so the exact future Engine/kernel versions remain an
M3 evidence field):

| Official source | Consulted version marker | Access date |
| --- | --- | --- |
| <https://docs.docker.com/engine/containers/resource_constraints/> | live Docker Docs, copyright 2013-2026 | 2026-09-16 |
| <https://docs.docker.com/engine/containers/run/> | live Docker Docs, copyright 2013-2026 | 2026-09-16 |
| <https://docs.docker.com/engine/network/drivers/none/> | live Docker Docs, copyright 2013-2026 | 2026-09-16 |
| <https://docs.docker.com/engine/security/rootless/tips/> | live Docker Docs, copyright 2013-2026 | 2026-09-16 |
| <https://docs.docker.com/engine/security/seccomp/> | live Docker Docs, copyright 2013-2026 | 2026-09-16 |
| <https://docs.docker.com/engine/storage/tmpfs/> | live Docker Docs, copyright 2013-2026 | 2026-09-16 |

These are documented technical behaviors, not evidence that this machine or a
future supported environment enforces them. Docker was not installed, configured
or probed by Issue #77. M3/M4 must record exact versions and actual observations.

## 10. Network, image and secret boundaries

`NONE` applies only to Worker runtime traffic. It does not block the trusted
adapter's management channel to the daemon or a separately authorized image
provisioning service. Runtime create never pulls. Provisioning verifies the
approved digest and records source/signature/SBOM policy when later specified;
Stage 2 does not design the release supply-chain policy.

The Worker receives no raw secret, Docker credential, operator environment,
cloud metadata credential or proxy setting. Allowed environment keys are
profile-versioned and values are supplied explicitly from non-secret Task
inputs. Names matching common credential/proxy patterns are denied unless a
future accepted credential design explicitly owns them. Redaction is defense in
depth, not permission to pass secrets.

`DNS_ONLY`, `ALLOWLIST`, `PROXY_CONTROLLED` and `FULL_INTERNET` fail before
create with `UNSUPPORTED_CAPABILITY`. Stage 3 cannot silently change that. A
future design must specify egress enforcement outside Worker control, DNS
rebinding/IP resolution behavior, proxy trust, credential scope, audit and
bypass tests.

## 11. Telemetry, persistence and cleanup

### 11.1 Runtime observations

```python
RuntimeObservation(
    observation_id: ObservationId,
    sequence: int,                     # monotonic within sandbox generation
    provider_id: ProviderId,
    task_id: TaskId,
    run_id: RunId,
    workspace_id: WorkspaceId,
    sandbox_id: SandboxId,
    command_id: CommandId | None,
    generation: int,
    kind: ObservationKind,
    observed_at: UtcTimestamp,
    source_timestamp: UtcTimestamp | None,
    duration_ms: int | None,
    image_digest: Sha256Digest,
    execution_profile_ref: ExecutionProfileRef,
    network_policy_ref: str,
    resource_policy_digest: Sha256Digest,
    payload: BoundedRedactedMapping,
    completeness: Literal["COMPLETE", "PARTIAL", "UNKNOWN"],
)
```

Sequence gaps are explicit. Adapter receipt time is always present; provider
source time and duration may be unknown. Payloads have per-kind schemas and byte
limits. Telemetry includes create/start/attach/exit/signal/inspect/resource-
usage/artifact/cleanup observations, but no hidden reasoning, secret values or
unbounded daemon logs.

The trusted Stage 2 runtime store (to be implemented later) retains ownership
records, idempotency records, terminal results, manifests, cleanup obligations
and bounded observations outside Worker memory. Retention duration and storage
adapter are implementation-policy choices, but restart must reopen outstanding
owned resources without relying on a Worker report. Usage counters are
observations only; Stage 6 owns authoritative budget/cost ledgers.

These records are not Stage 1 `DomainEvent`s. A later trusted orchestration
service may attach their `EvidenceRef`s to a separately authorized domain
transition or Evaluation request. The provider cannot call persistence
`UnitOfWork` or change `RunState`.

### 11.2 Cleanup algorithm

1. Resolve the immutable ownership record and validate all supplied IDs and
   generation.
2. Inspect the provider by immutable resource ID. A missing label, changed
   label or reused name never widens the target.
3. If a command may be active, send bounded graceful termination, then forced
   termination if needed; record the race outcome.
4. Inspect until the process/container is terminal or the cleanup deadline
   expires. Deadline expiry yields unknown, not success.
5. Collect/export only if explicitly requested and quiescence is confirmed.
6. Remove exactly the owned container and provider-created ancillary resources.
7. Independently inspect for absence. Only then mark `DESTROYED`/`RELEASED`.
8. Retain a bounded cleanup obligation on disconnect/failure for startup
   discovery and operator escalation.

Repeated cleanup returns the prior confirmed result if the same identity is
absent. It never calls system/global prune, deletes by a broad name prefix or
removes resources merely because they carry a similar label. A metadata record
without a provider resource is reconciled as absent; a provider resource with
matching labels but no metadata is quarantined for operator review, not
automatically removed.

Parent-process crash scenario: Docker may continue the container. On restart,
the adapter reads outstanding metadata, queries resources by exact ownership
labels, cross-checks immutable IDs/config, marks observations as reopened and
executes only the approved targeted cleanup policy. This does not Resume a Run,
trust the workspace or infer an external Effect outcome.

## 12. Reference scenarios

Examples use candidate defaults and omit irrelevant IDs for readability.

### SCN-01 bounded success and artifact

Input: `argv=("python", "-c", "open('answer.txt','w').write('42')")`,
`cwd="."`, network `NONE`, 30 s timeout, collect `answer.txt`.

Expected: command `EXITED`, exit 0, complete bounded streams; after quiescence,
one regular-file manifest entry with size 2 and hash over bytes `42`. The
manifest is a candidate artifact record, not proof that any requirement passed.

### SCN-02 nonzero command

Input: argv for a program that exits 7 after writing to stderr.

Expected: `COMMAND_NONZERO_EXIT`, exit 7, retained stderr metadata. Sandbox may
return to ready only after EOF and terminal inspection. Run state is unchanged.

### SCN-03 stdout/stderr flood

Input: bounded fixture writes 2 MiB to each stream with 1 MiB retention limits.

Expected: both streams continue draining; observed size is 2 MiB when EOF is
seen, retained size is 1 MiB, both truncation flags true. Daemon log storage is
also inspected as disabled/bounded. No memory growth beyond the fixture bound.

### SCN-04 timeout and cancellation race

Input: bounded sleep beyond 500 ms. Controller reaches deadline, sends TERM,
waits the configured short grace, then KILL if needed.

Expected: `TIMEOUT`; terminal result only when process-tree termination and EOF
are confirmed. If the process exits naturally before TERM takes effect, actual
exit plus “cancel lost race” is returned. Disconnect yields unknown and blocks
another command.

### SCN-05 create/start disconnect uncertainty

Input: daemon response is lost after create/start request.

Expected: no blind replay. Trusted metadata and immutable labels/ID drive
inspection. The adapter either adopts the exact owned resource with a new
observation, cleans a partial resource, or records unknown/cleanup failure.

### SCN-06 wrong Run/workspace handle

Input: valid sandbox ID with another `RunId`, `WorkspaceId`, generation or lease
version.

Expected: `OWNERSHIP_MISMATCH`; no inspect beyond safe identity lookup, command,
signal, collection or deletion occurs.

### SCN-07 prohibited privilege/mount/socket

Input: request asks for privileged mode, `/` bind mount, Docker socket, device,
host namespace or added capability.

Expected: schema/profile construction returns `INVALID_SCOPE` before provider
create. Negative test asserts no Docker resource appeared.

### SCN-08 unsupported network and external denial

Input A requests `ALLOWLIST`; input B requests `NONE` then attempts loopback,
DNS and external IP TCP.

Expected A: `UNSUPPORTED_CAPABILITY` before create. Expected B: loopback works;
DNS/external path fails, with network inspection showing only the none profile.
The negative test must ensure command/image failure is not the cause of denial.

### SCN-09 hostile artifact

Input fixtures separately cover absolute/parent paths, symlink, hardlink,
rename race, FIFO/device, deep tree, too many files, one oversized file and
aggregate overflow.

Expected: each isolated case yields `ARTIFACT_REJECTED`, no partial manifest or
trusted artifact, and bounded cleanup. Executable regular files may be captured
only as non-executable stored bytes plus metadata.

### SCN-10 repeated teardown after partial failure

Input: stop succeeds, first remove response is lost, then `destroy` repeats.

Expected: inspect exact resource; return confirmed destroyed if absent or retry
the exact owned removal if present. No global prune and no unowned deletion.

### SCN-11 parent crash with leftover resource

Input: kill the adapter fixture after container start while Worker remains
bounded.

Expected: new adapter instance reads persisted obligation, cross-checks the
exact labels/ID and performs targeted cleanup. It does not declare Run failure,
Resume or Outcome disposition.

### SCN-12 retained workspace for review

Input: explicit `EXPORT_FOR_REVIEW` after confirmed quiescence.

Expected: bounded immutable snapshot plus manifest marked untrusted; active
tmpfs is destroyed. Import is refused absent a future explicit recovery
decision. Retention does not accept content.

## 13. Future test catalog

Evidence classes are deliberately separate:

- **UNIT**: pure value validation, state/idempotency/ownership rules, manifest
  algorithms and normalization; no isolation claim.
- **FAKE**: deterministic provider orchestration and failure/race semantics;
  proves contract behavior, never real isolation.
- **DOCKER**: eligible-environment integration/security/adverse tests; required
  to claim real enforcement.

| Test ID | Class | Isolated assertion | Owner |
| --- | --- | --- | --- |
| T-U01 | UNIT | all IDs/types/units/ranges reject malformed or cross-kind values | M2 |
| T-U02 | UNIT | request digest/idempotency exact replay and conflict behavior | M2 |
| T-U03 | UNIT | ownership tuple, generation and lease mismatch touch no resource | M2 |
| T-U04 | UNIT | argv/cwd/env/stdin validation prohibits host-shell/path/env injection | M2 |
| T-U05 | UNIT | failure mapping preserves unknown/retry/live-resource fields | M2 |
| T-U06 | UNIT | artifact validator rejects each hostile path/type/limit independently | M2 |
| T-F01 | FAKE | full create/start/execute/collect/destroy success ordering | M2 |
| T-F02 | FAKE | one-active-command rule and unknown-command reuse block | M2 |
| T-F03 | FAKE | create/start disconnect requires inspect before retry | M2 |
| T-F04 | FAKE | timeout/cancel/natural-exit races never invent termination | M2 |
| T-F05 | FAKE | partial create and repeated cleanup target only owned resources | M2 |
| T-F06 | FAKE | restart discovery uses durable ownership metadata, not Worker memory | M2 |
| T-F07 | FAKE | artifact/hash bytes and manifest are atomic or absent | M2 |
| T-D01 | DOCKER | command runs in container, cannot see host sentinel | M3/M4 |
| T-D02 | DOCKER | non-root/cap-drop/no-privilege/no-device/default-seccomp profile enforced | M3/M4 |
| T-D03 | DOCKER | host root/home/repository/database/socket mounts absent and requests denied | M3/M4 |
| T-D04 | DOCKER | root read-only; only bounded workspace/tmp writable | M3/M4 |
| T-D05 | DOCKER | memory+swap cap contains bounded allocation fixture | M3/M4 |
| T-D06 | DOCKER | CPU quota throttles bounded loop; shares are not used as proof | M3/M4 |
| T-D07 | DOCKER | PID cap stops bounded fork fixture without host exhaustion | M3/M4 |
| T-D08 | DOCKER | wall timeout confirms process tree termination or returns unknown | M3/M4 |
| T-D09 | DOCKER | stdout/stderr finite flood drains and truncates independently | M3/M4 |
| T-D10 | DOCKER | tmpfs byte/inode fixtures hit isolated limits | M3/M4 |
| T-D11 | DOCKER | `NONE` preserves loopback and denies DNS/external IP with no proxy/ports | M3/M4 |
| T-D12 | DOCKER | approved local digest only; missing image never pulls; entrypoint cannot elevate | M3/M4 |
| T-D13 | DOCKER | hostile artifact link/rename/type/size matrix fails closed | M3/M4 |
| T-D14 | DOCKER | daemon disconnect and adapter crash leave discoverable owned resources | M4 |
| T-D15 | DOCKER | repeated/partial teardown confirms absence and no unrelated deletion | M4 |
| T-D16 | DOCKER | retained export is bounded, immutable and not auto-reused | M4 |

Resource-abuse fixtures must be deterministic and small: cap+one-page memory,
cap+small-margin PIDs, fixed-duration CPU, fixed stream lengths, and tmpfs
cap+one-block/inode. Each runs in a disposable test environment with an outer
test deadline and host safety headroom. Issue #77 executes none of them.

Non-Docker developer runs may skip explicitly marked Docker tests. Such a skip
is a developer convenience only. Stage 2 acceptance requires all mandatory
Docker cases on an eligible recorded environment; skipped tests are not
isolation evidence.

## 14. Requirement traceability

| Requirement | Design sections | Future tests | Owning milestone |
| --- | --- | --- | --- |
| SBX-R01 approved sandbox/no host | 3, 9.2-9.3 | T-F01, T-D01 | M2 contract; M3/M4 proof |
| SBX-R02 provider replaceability | 4-5, 9.3 | T-F01-F07, architecture import check | M2 |
| SBX-R03 Run/workspace lifetime | 3, 4.3, 8 | T-U03, T-F06, T-D16 | M2/M3; Stage 5 owns reuse |
| SBX-R04 authority separation | 3, 11.1 | contract/import tests; no provider UoW dependency | M2 |
| SBX-R05 capability preflight/normalization | 4.1, 7, 9.1 | T-U05, T-F03, T-D02-D12 | M2-M4 |
| SBX-R06 privilege/mount/socket/writable boundary | 8, 9.2-9.3 | T-D02-D04 | M3/M4 |
| SBX-R07 resource/time/output bounds | 4.2, 4.4, 9.3 | T-D05-D10 | M3/M4 |
| SBX-R08 typed network/fail closed | 4.2, 9.3, 10 | T-U01, T-D11 | M2/M3/M4 |
| SBX-R09 secret/env boundary | 9.2-9.3, 10 | T-U04, env adverse probe | M2/M3/M4 |
| SBX-R10 artifact claims remain untrusted | 4.5, 8.2, 12 | T-U06, T-F07, T-D13 | M2-M4; Stage 4 evaluates |
| SBX-R11 preserved work needs recovery authority | 8.1, SCN-12 | T-D16 | M3/M4; Stage 5 recovery |
| SBX-R12 no Effect dispatch | 3, 11.1 | dependency/authority architecture test | M2; Stage 6 Effects |
| SBX-R13 observable cleanup/unknown state | 6-7, 11.2 | T-F03-F06, T-D14-D15 | M2-M4 |
| SBX-R14 dynamic isolation evidence | 9.3, 13 | T-D01-D16 | M4 and Stage 2 exit |
| SBX-R15 Stage 3 blocked | candidate status, 16-17 | governance/status review | M1 review/Stage 2 exit |

## 15. M2-M4 coding map

Paths are proposals, not authorization or a guessed future TaskSpec.

### S2-M2 — typed contracts, workspace boundary and fake provider

Prerequisite: ADR-0008 and this design explicitly Human approved in durable
governance; exact post-review baseline and separate TaskSpec.

Proposed production paths:

```text
src/symphony_k/execution/sandbox/contracts.py
src/symphony_k/execution/sandbox/failures.py
src/symphony_k/execution/sandbox/provider.py
src/symphony_k/execution/sandbox/workspace.py
src/symphony_k/execution/sandbox/artifacts.py
src/symphony_k/execution/sandbox/fake.py
```

Proposed test paths:

```text
tests/execution/sandbox/test_contracts.py
tests/execution/sandbox/test_workspace.py
tests/execution/sandbox/test_artifacts.py
tests/execution/sandbox/test_fake_provider.py
tests/constitutional/test_sandbox_authority_boundary.py
```

Success matrix: T-U01-U06 and T-F01-F07. Adverse cases cover wrong ownership,
duplicate/conflicting idempotency, active-command conflict, unknown state,
partial allocation, cancellation races and hostile artifacts. Likely commit
boundaries: (1) contracts/failures, (2) workspace/artifact algorithms, (3) fake
provider/conformance tests. Completion evidence is passing unit/fake/type/lint
gates plus architecture proof that execution code cannot mutate domain state.

### S2-M3 — Docker lifecycle, constraints, artifacts and telemetry

Prerequisite: accepted M2, eligible native Linux Docker environment, approved
immutable test image/provisioning record and fresh capability preflight.

Proposed production paths:

```text
src/symphony_k/execution/sandbox/docker/provider.py
src/symphony_k/execution/sandbox/docker/profile.py
src/symphony_k/execution/sandbox/docker/streams.py
src/symphony_k/execution/sandbox/docker/artifacts.py
src/symphony_k/execution/sandbox/docker/telemetry.py
src/symphony_k/execution/sandbox/docker/ownership.py
```

Proposed test paths:

```text
tests/integration/docker/test_lifecycle.py
tests/integration/docker/test_constraints.py
tests/integration/docker/test_network_none.py
tests/integration/docker/test_artifacts.py
tests/integration/docker/test_cleanup.py
```

Success cases cover create/start/execute/collect/export/destroy. Adverse cases
cover missing image, config mismatch, nonzero exit, each resource bound,
network denial, output flood, artifact rejection and cleanup failure. Likely
commit boundaries: (1) ownership/profile/create-start, (2) execute/streams/
cancel, (3) artifact/export, (4) telemetry/targeted cleanup. Completion evidence
includes exact Docker/kernel/cgroup/version records and T-D01-D13 results; it
does not yet close crash/reopen robustness.

### S2-M4 — adverse Docker, crash/cleanup and operations evidence

Prerequisite: accepted M3 candidate and a disposable eligible environment with
outer resource safety controls.

Proposed paths:

```text
tests/security/docker/test_isolation_adverse.py
tests/security/docker/test_resource_adverse.py
tests/security/docker/test_artifact_races.py
tests/integration/docker/test_restart_cleanup.py
docs/operations/sandbox-diagnostics.md
docs/operations/sandbox-cleanup.md
```

The matrix repeats T-D01-D13 independently and completes T-D14-D16, including
adapter crash, daemon disconnect, leftover discovery, repeated cleanup and
unrelated-resource preservation. Likely commit boundaries: (1) safe adverse
fixtures, (2) crash/reopen/cleanup, (3) operator diagnostics and evidence
reconciliation. Completion evidence is an environment-bound report with no
mandatory skips, resource inventories before/after, exact normalized results,
host-safety observations and independent review. Then the stage performs
milestone reconciliation and a separate Human Stage 2 Exit Review. Only an
accepted exit plus a new TaskSpec may activate Stage 3.

## 16. Unresolved risks and owners

| Question/risk | Current safe behavior | Owner and blocking milestone |
| --- | --- | --- |
| Are interface/default decisions acceptable? | no runtime coding | M1 independent review / Human approval; blocks M2 |
| Which exact Engine/kernel/distribution versions are supported? | no support claim | M3 TaskSpec/preflight; blocks M3 execution evidence |
| Do tmpfs `size`, block and inode options enforce correctly in the selected environment? | mark capability unsupported and do not start | M3 implementation, M4 adverse proof; blocks Stage 2 exit |
| How is trusted snapshot/artifact storage quota and retention operated? | exports remain bounded per request; operator storage limit unclaimed | M3 storage implementation, M4 operations review; blocks supported profile |
| Does rootless Docker satisfy every required control? | not supported | M4 environment variant review; non-blocking if native Linux profile passes |
| Does Docker Desktop satisfy equivalent guarantees? | development-only/unverified | future evidence; non-blocking for native Linux supported profile |
| What network/credential profile permits a real AgentDriver? | only `NONE`, no secrets | separate Stage 3 design; blocks networked AgentDriver, not Stage 2 |
| Can retained bytes become a recovery checkpoint? | no, untrusted snapshot only | Stage 5 recovery design |
| Can telemetry become cost/acceptance evidence? | no, observation only | Stage 4 verification and Stage 6 budget design |
| Is stronger-than-container isolation required for a threat class? | document Docker shared-kernel residual risk; reject unsupported Task profile | later Human architecture decision/provider ADR |

## 17. Residual trust and limitations

The design trusts the host kernel, Docker daemon, administrator, trusted
adapter, ownership/telemetry store, approved image provisioning and artifact
store. A compromised trusted host or daemon can violate every container claim.
Docker's shared kernel is a residual escape and denial-of-service risk. Resource
limits reduce blast radius but do not prove perfect isolation or protect every
host subsystem. No GPU/device, inbound port, host network, Docker-in-Docker,
secret, external egress or mutable-image use is supported.

Loss of unexported tmpfs bytes after stop/crash is acceptable candidate-work
loss, not loss of authoritative domain state. A live-resource unknown, cleanup
failure, insufficient storage guarantee or unsupported isolation capability
blocks reuse/start and requires operator/recovery handling; it never selects
the host as Worker runtime.

## 18. Approval questions and disposition

Independent review should answer:

1. Approve or reject the exact provider types, ownership tuple and one-active-
   command rule.
2. Approve or reject bounded tmpfs plus explicit untrusted export as the first
   workspace strategy.
3. Approve or reject the Linux Docker profile, immutable image boundary and
   `NONE`-only network support.
4. Confirm the failure/unknown/cancellation and cleanup contracts fail closed.
5. Confirm M2-M4 paths, evidence classes and Stage 3 gate cover every parent
   requirement without importing later-stage authority.

Candidate disposition at Issue #77 completion:

```text
ADR-0008 = PROPOSED
Sandbox design = CANDIDATE
M1 independent review / Human approval = PENDING
Stage 2 runtime implementation authorized = NO
Stage 2 complete = NO
Stage 3 = PLANNED
```
