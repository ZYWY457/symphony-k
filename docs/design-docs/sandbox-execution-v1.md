# Sandbox Execution v1

## Candidate status and authority

**Status:** Candidate - not an accepted implementation contract.

**Date:** 2026-09-16

**TaskSpec history:** GitHub Issue #77, revision
`r1 - stage-02-m1-design-start`; corrected forward by GitHub Issue #78,
revision `r1 - stage-02-m1a-contract-closure`

This document proposes the Stage 2 execution contract. It implements nothing,
does not report any Docker probe as executed, and does not authorize changes to
`src/` or `tests/`. [ADR-0008](../adr/0008-stage-2-sandbox-execution-boundary.md)
is Proposed. Issue #78 closes requested review gaps but does not accept the
decision. Independent review and explicit Human approval remain the next gate.

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
RequestId = NewType("RequestId", UUID)
OperationId = NewType("OperationId", UUID)
WorkspaceLeaseId = NewType("WorkspaceLeaseId", UUID)
ManifestId = NewType("ManifestId", UUID)
ProviderId = NewType("ProviderId", str)
IdempotencyKey = NewType("IdempotencyKey", UUID)
Sha256Digest = NewType("Sha256Digest", str)  # exactly "sha256:" + 64 lowercase hex
RelativePosixPath = NewType("RelativePosixPath", str)
UtcTimestamp = aware_datetime
```

Resource/request/idempotency UUIDs are non-nil UUIDv4 values allocated by the
trusted orchestration request boundary before dispatch and persisted with the
request envelope; observation, operation and manifest UUIDs are generated by
the trusted provider/store boundary. Production allocation uses the configured
cryptographic OS random source. A deterministic factory may be injected only
at a test composition root; choosing an ID never grants authority and a Worker-
supplied value is not accepted as a production allocation.
All byte counts are non-negative unsigned 64-bit integers. Durations use
integer milliseconds and are positive unless explicitly optional. Timestamps
are UTC with an offset. Relative paths use `/`, are normalized once for syntax,
and are still validated during descriptor-relative traversal.
Generations, lease/store versions and observation sequences are positive
unsigned 64-bit integers and must not wrap; exhaustion rejects new work. Exit
codes and signal numbers, where present, are signed 32-bit integers validated
against the selected platform contract.

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
WorkspacePhase = DECLARED | STAGING | LEASED | ACTIVE | QUIESCING | QUIESCED |
                 EXPORTING | EXPORTED_UNTRUSTED | RELEASING | RELEASED |
                 CLEANUP_REQUIRED | CLEANUP_FAILED | UNKNOWN
OperationDisposition = IN_PROGRESS | SUCCEEDED | REJECTED | FAILED | UNKNOWN
CancellationDisposition = CANCEL_REQUESTED | CANCELLED | ALREADY_TERMINAL |
                          UNKNOWN
ExportDisposition = EXPORTED | REJECTED | LOST | UNKNOWN
CleanupDisposition = DESTROYED | ALREADY_ABSENT | FAILED | UNKNOWN
CapabilityProvenance = REAL_PROBE | SIMULATED
ObservationCompleteness = COMPLETE | PARTIAL | UNKNOWN
OwnedResourceKind = WORKSPACE_STAGING | CONTAINER | ARTIFACT_PARTIAL |
                    SNAPSHOT_PARTIAL | GUARDIAN_DEADLINE
OperationKind = CAPABILITIES | CREATE_WORKSPACE | CREATE_SANDBOX | START |
                EXECUTE | INSPECT | INSPECT_COMMAND | CANCEL | COLLECT |
                EXPORT_WORKSPACE | DESTROY | REOPEN_OWNED_RESOURCES
FailurePhase = PREFLIGHT | WORKSPACE_STAGING | CREATE | START | EXECUTE |
               CANCEL | COLLECT | EXPORT | DESTROY | INSPECT | REOPEN
```

Every public record is a frozen value object. Sequences are tuples, sets are
frozensets, maps are immutable sorted-key maps, byte strings are copied, and no
record exposes provider-owned mutable collections. Canonical encoding is
versioned UTF-8 JSON with explicit enum/nominal-ID tags, sorted map keys, sorted
set encodings, decimal integers, no floats and no omitted semantic fields.
`None` is encoded explicitly where it changes meaning. This encoding is used
for request fingerprints and manifest hashes; Python object hashes or map
iteration order are never used.

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
    supports_co_located_linux_collector: bool,
    supports_external_deadline_guardian: bool,
    provenance: CapabilityProvenance,
    observed_at: UtcTimestamp,
    probe_evidence_refs: tuple[EvidenceRef, ...],
)
```

`REAL_PROBE` capability values are trusted probe observations scoped to provider and
environment version. They expire on daemon/kernel/configuration change and do
not assert that a particular sandbox used the capability; create/start
observations must record the effective configuration too.
`SIMULATED` is reserved for deterministic Fake/conformance behavior. A Fake
must report `environment_class=UNSUPPORTED`, `provenance=SIMULATED` and cannot
be selected as a real isolation route regardless of individual Boolean values.

### 4.2 Resource, output and network limits

```python
ResourceLimits(
    cpu_millis_per_second: int,       # 100..4000; proposed default 1000
    memory_bytes: int,                # 64 MiB..8 GiB; default 512 MiB
    memory_swap_bytes: int,           # memory_bytes..8 GiB; default == memory
    pids_max: int,                    # 16..1024; default 128
    wall_time_ms: int,                # 100..3_600_000; default 900_000
    termination_grace_ms: int,        # 0..30_000; default 2_000
    termination_confirm_ms: int,      # 100..60_000; default 10_000
    cleanup_deadline_ms: int,         # 100..120_000; default 30_000
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
The grace/confirmation/cleanup bounds are immutable parts of the effective
resource policy and request fingerprint. They cannot be increased after
command start; an authorized cancellation may only shorten execution.

### 4.3 Workspace and sandbox specifications

```python
WorkspaceSpec(
    workspace_id: WorkspaceId,
    task_id: TaskId,
    run_id: RunId,
    input_snapshot_ref: ArtifactRef | None,
    retention: WorkspaceRetention,    # DESTROY | EXPORT_FOR_REVIEW
    generation: int,                  # >= 1; never reused for this identity
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
    workspace_generation: int,
    lease_id: WorkspaceLeaseId,
    lease_version: int,
    generation: int,                  # >= 1; changes on recreate, never reused
)

WorkspaceRecord(
    provider_id: ProviderId,
    workspace_id: WorkspaceId,
    task_id: TaskId,
    run_id: RunId,
    generation: int,
    phase: WorkspacePhase,
    retention: WorkspaceRetention,
    lease_id: WorkspaceLeaseId | None,
    lease_version: int,
    leased_sandbox_id: SandboxId | None,
    input_snapshot_ref: ArtifactRef | None,
    exported_snapshot_ref: ArtifactRef | None,
    cleanup_required: bool,
    version: int,                     # optimistic store version, >= 1
    last_observation_ref: EvidenceRef | None,
)

SandboxObservation(
    handle: SandboxHandle,
    phase: SandboxPhase,
    observed_at: UtcTimestamp,
    provider_resource_id: str | None, # bounded opaque adapter value
    worker_processes_present: bool | None,
    owned_cgroup_empty: bool | None,
    effective_profile_digest: Sha256Digest | None,
    cleanup_required: bool,
    completeness: ObservationCompleteness,
    failure: SandboxFailure | None,
    observation_ref: EvidenceRef,
)
```

Specifications are immutable after successful create. A change requires a new
sandbox identity and generation; changing route or Run requires a new `RunId`
under ADR-0006. A workspace lease is exclusive. A stale lease version or handle
generation returns `OWNERSHIP_MISMATCH` without touching the provider resource.
`LEASED`/`ACTIVE` require non-null `lease_id`, `leased_sandbox_id` and matching
lease version; released workspaces have neither. `DESTROYED` observations must
report no Worker processes and an empty owned cgroup. `UNKNOWN` must use
`completeness=UNKNOWN`, require cleanup and cannot assert either absence field.

### 4.4 Command request and terminal result

```python
CommandRequest(
    request_id: RequestId,
    command_id: CommandId,
    idempotency_key: IdempotencyKey,
    argv: tuple[str, ...],             # 1..256 items; each UTF-8, no NUL
    cwd: RelativePosixPath,            # beneath /workspace; default "."
    env: Mapping[str, str],            # <= 64 entries; key allowlisted
    stdin: bytes | None,               # bounded by OutputLimits.stdin_bytes
    timeout_ms: int,                   # <= ResourceLimits.wall_time_ms
    termination_grace_ms: int,         # <= ResourceLimits.termination_grace_ms
)

DeadlineBinding(
    provider_id: ProviderId,
    task_id: TaskId,
    run_id: RunId,
    workspace_id: WorkspaceId,
    workspace_generation: int,
    lease_id: WorkspaceLeaseId,
    lease_version: int,
    sandbox_id: SandboxId,
    sandbox_generation: int,
    command_id: CommandId,
    request_digest: Sha256Digest,
    host_boot_id: str,                 # 1..128 ASCII, trusted host value
    armed_at_monotonic_ns: int,
    deadline_monotonic_ns: int,
    grace_ms: int,
    confirmation_ms: int,
    recorded_at: UtcTimestamp,         # audit only, never deadline authority
    binding_digest: Sha256Digest,
)

CommandHandle(
    provider_id: ProviderId,
    sandbox_id: SandboxId,
    task_id: TaskId,
    run_id: RunId,
    workspace_id: WorkspaceId,
    workspace_generation: int,
    lease_id: WorkspaceLeaseId,
    lease_version: int,
    sandbox_generation: int,
    command_id: CommandId,
    request_digest: Sha256Digest,
    deadline_binding_digest: Sha256Digest,
)

CommandObservation(
    handle: CommandHandle,
    phase: CommandPhase,
    observed_at: UtcTimestamp,
    started_at: UtcTimestamp | None,
    process_ended_at: UtcTimestamp | None,
    exit_code: int | None,
    termination_confirmed: bool,
    stream_eof_confirmed: bool,
    deadline_armed: bool,
    deadline_expired: bool,
    completeness: ObservationCompleteness,
    failure: SandboxFailure | None,
    observation_ref: EvidenceRef,
)

TerminalResult(
    command_id: CommandId,
    disposition: CommandDisposition,
    exit_code: int | None,
    started_at: UtcTimestamp | None,
    ended_at: UtcTimestamp | None,
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

A confirmed terminal process result requires `termination_confirmed=true`, a
non-null actual `ended_at`, stream EOF or explicitly partial stream evidence,
and the disposition-permitted exit-code combination below. An `UNKNOWN` result
has `termination_confirmed=false`, `ended_at=None`, `exit_code=None` and a
state-unknown failure. `observed_at` belongs to observations only and never
substitutes for the process end time.

| Disposition | Exit code | Required cause/result relationship |
| --- | --- | --- |
| `EXITED_ZERO` | exactly 0 | natural process exit confirmed |
| `EXITED_NONZERO` | nonzero signed 32-bit | natural/program exit confirmed |
| `START_FAILED` | `None` | no process start; failed start confirmed |
| `TIMED_OUT` | actual code when observed, otherwise `None` | deadline caused termination; timeout failure retained separately |
| `CANCELLED` | actual code when observed, otherwise `None` | accepted cancel caused termination |
| `RESOURCE_LIMIT` | actual code when observed, otherwise `None` | independently observed limit event caused/preceded termination |
| `UNKNOWN` | `None` | termination unconfirmed; no `ended_at` |

Output truncation is orthogonal: any confirmed disposition may have either
stream truncated while preserving the actual exit status. Cleanup outcome is
never embedded in `TerminalResult`; it is returned by `destroy`.

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
    manifest_id: ManifestId,
    task_id: TaskId,
    run_id: RunId,
    workspace_id: WorkspaceId,
    workspace_generation: int,
    sandbox_id: SandboxId,
    sandbox_generation: int,
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
    failure: SandboxFailure | None,
)

OperationInProgress(
    operation_id: OperationId,
    request_id: RequestId,
    idempotency_key: IdempotencyKey,
    operation_kind: OperationKind,
    request_digest: Sha256Digest,
    accepted_at: UtcTimestamp,
    last_observed_at: UtcTimestamp,
    retry_after_ms: int | None,        # 0..60_000 advisory value
    observation_ref: EvidenceRef,
)

CancellationResult(
    disposition: CancellationDisposition,
    command: CommandObservation | TerminalResult,
    cancellation_requested_at: UtcTimestamp,
    signal_observation_refs: tuple[EvidenceRef, ...],
    sandbox_reusable: bool,
    failure: SandboxFailure | None,
)

WorkspaceExportResult(
    disposition: ExportDisposition,
    workspace_id: WorkspaceId,
    workspace_generation: int,
    sandbox_id: SandboxId,
    sandbox_generation: int,
    manifest: ArtifactManifest | None,
    snapshot_ref: ArtifactRef | None,
    committed_at: UtcTimestamp | None,
    source_lost: bool,
    partial_output_discarded: bool,
    failure: SandboxFailure | None,
    observation_refs: tuple[EvidenceRef, ...],
)

CleanupResult(
    disposition: CleanupDisposition,
    sandbox: SandboxObservation,
    removed_resource_kinds: tuple[OwnedResourceKind, ...],
    preservation: WorkspaceExportResult | None,
    absence_confirmed_at: UtcTimestamp | None,
    cleanup_obligation_retained: bool,
    failure: SandboxFailure | None,
    observation_refs: tuple[EvidenceRef, ...],
)

OwnedResourceObservation(
    resource_kind: OwnedResourceKind,
    provider_id: ProviderId,
    task_id: TaskId,
    run_id: RunId,
    workspace_id: WorkspaceId,
    workspace_generation: int,
    sandbox_id: SandboxId | None,
    sandbox_generation: int | None,
    provider_resource_id: str,
    metadata_version: int,
    observed_at: UtcTimestamp,
    ownership_match: Literal["MATCH", "MISMATCH", "UNVERIFIABLE"],
    cleanup_required: bool,
    completeness: ObservationCompleteness,
    failure: SandboxFailure | None,
    observation_ref: EvidenceRef,
)
```

`COLLECTED` requires both manifest and artifact reference and no failure;
`REJECTED` requires a failure and neither output; `UNKNOWN` has neither output
and a state-unknown failure. `EXPORTED` similarly requires manifest, snapshot
and `committed_at`; `LOST` requires `source_lost=true` with no output.
`DESTROYED`/`ALREADY_ABSENT` require `absence_confirmed_at`, no retained cleanup
obligation and no failure. `FAILED`/`UNKNOWN` require a failure and retain an
obligation whenever a resource may be live. All tuples and diagnostics use the
bounds already defined; provider resource IDs are opaque UTF-8 up to 512 bytes.

`CANCEL_REQUESTED` contains a nonterminal command observation and never marks
the sandbox reusable. `CANCELLED` contains a confirmed cancelled terminal
result. `ALREADY_TERMINAL` contains the actual prior terminal result without
relabeling it. `UNKNOWN` contains an unknown command observation/result,
`sandbox_reusable=false` and a state-unknown failure. An owned resource with
`ownership_match!=MATCH` may be reported or quarantined but cannot be mutated;
`cleanup_required=true` becomes actionable only after an independent exact
metadata match.

Directories are metadata only; archives are never implicitly expanded. If an
archive is explicitly requested as a regular file, it is collected as opaque
bytes and any future extraction must repeat path/link/size checks in a new
trusted boundary.

## 5. Provider operations

```python
MutationContext(
    request_id: RequestId,
    idempotency_key: IdempotencyKey,
    expected_workspace_generation: int | None,
    expected_lease_id: WorkspaceLeaseId | None,
    expected_lease_version: int | None,
    expected_sandbox_generation: int | None,
)

class SandboxProvider(Protocol):
    def capabilities() -> ProviderCapabilities: ...
    def create_workspace(
        spec: WorkspaceSpec, context: MutationContext,
    ) -> WorkspaceRecord | OperationInProgress: ...
    def create_sandbox(
        spec: SandboxSpec, context: MutationContext,
    ) -> SandboxObservation | OperationInProgress: ...
    def start(
        handle: SandboxHandle, context: MutationContext,
    ) -> SandboxObservation | OperationInProgress: ...
    def execute(
        handle: SandboxHandle, request: CommandRequest,
    ) -> CommandHandle | TerminalResult | OperationInProgress: ...
    def inspect(handle: SandboxHandle) -> SandboxObservation: ...
    def inspect_command(
        command_handle: CommandHandle,
    ) -> CommandObservation | TerminalResult: ...
    def cancel(
        command_handle: CommandHandle, context: MutationContext,
    ) -> CancellationResult | OperationInProgress: ...
    def collect(
        handle: SandboxHandle, request: ArtifactRequest,
        context: MutationContext,
    ) -> ArtifactCollectionResult | OperationInProgress: ...
    def export_workspace(
        handle: SandboxHandle, request: ArtifactRequest,
        context: MutationContext,
    ) -> WorkspaceExportResult | OperationInProgress: ...
    def destroy(
        handle: SandboxHandle, context: MutationContext,
    ) -> CleanupResult | OperationInProgress: ...
    def reopen_owned_resources(
        provider_id: ProviderId, task_id: TaskId, run_id: RunId,
        limit: int,  # 1..1_000
    ) -> tuple[OwnedResourceObservation, ...]: ...
```

Every mutating call has an idempotency key stored with request digest and
result. Exact replay returns the prior result. Reuse with a different digest
returns `IDEMPOTENCY_CONFLICT`. An in-flight duplicate returns the same handle
or `OPERATION_IN_PROGRESS`; it never starts a second resource.

The trusted caller obtains `request_id` and `idempotency_key` from its
production allocator and persists the complete immutable request before the
first provider call. It reuses both after a lost response. The provider stores
the key under `(provider_id, operation_kind, authoritative ownership scope)`.
The request fingerprint is the SHA-256 of the canonical encoding of contract
version, operation kind, request ID, full ownership tuple, workspace generation,
lease ID/version, sandbox generation and every semantic parameter, including
all ordered argv/include values and sorted map/set content. It excludes only
the idempotency key itself. Same key/same digest replays; same key/different
digest conflicts; same request ID under another key also conflicts.

Only `create_workspace` permits all expected generation/lease/sandbox fields to
be `None`; its new identity/generation live in `WorkspaceSpec`. Every later
mutation requires workspace generation, lease ID/version and, once allocated,
sandbox generation. Presence/absence combinations outside that rule are
`INVALID_SCOPE` before provider mutation.

All operations first compare expected generation and lease against one
authoritative metadata snapshot. On a successful mutation the store atomically
writes the new phase/version, operation receipt and cleanup obligation before
the result is exposed. Provider-side mutation followed by store uncertainty is
`UNKNOWN` and requires inspect/reconciliation; it is never rolled back in
memory and reported absent. Reads return one immutable snapshot. No operation
may widen ownership from provider labels or a caller handle.

### 5.1 Public-operation completeness checklist

| Operation | Defined result | State/consistency rule | Planned tests |
| --- | --- | --- | --- |
| `capabilities` | `ProviderCapabilities` | provenance/version scoped; Fake is simulated | T-U01, architecture import check |
| `create_workspace` | `WorkspaceRecord` / `OperationInProgress` | declared through leased or cleanup-required; exact replay | T-U02-T-U03, T-F01, T-F05 |
| `create_sandbox` | `SandboxObservation` / `OperationInProgress` | absent/allocating/create; partial failure retains obligation | T-F01, T-F03, T-F05 |
| `start` | `SandboxObservation` / `OperationInProgress` | created/starting to ready, stopped or unknown | T-F01, T-F03 |
| `execute` | `CommandHandle` / `TerminalResult` / in-progress | ready only; deadline armed first; one active/unknown command | T-F01-T-F04, T-F08-T-F10 |
| `inspect` | `SandboxObservation` | exact identity/generation; read-only snapshot | T-U03, T-F03 |
| `inspect_command` | `CommandObservation` / `TerminalResult` | observation time never invents process end | T-U05, T-F04 |
| `cancel` | `CancellationResult` / in-progress | STARTING/RUNNING/CANCELLING/UNKNOWN; race preserves actual result | T-F04, T-F10 |
| `collect` | `ArtifactCollectionResult` / in-progress | quiesced/frozen identity; atomic manifest or none | T-U06, T-F07, T-F11 |
| `export_workspace` | `WorkspaceExportResult` / in-progress | durable commit before normal removal; loss explicit | T-F07, T-F11 |
| `destroy` | `CleanupResult` / in-progress | targeted whole sandbox; absence required for success | T-F05-T-F06, T-F08-T-F09 |
| `reopen_owned_resources` | tuple of `OwnedResourceObservation` | bounded query; observation only, no implicit cleanup/Run recovery | T-F06 |

## 6. Provider-local state machines

These phases are observations about provider resources, not `RunState` and not
authoritative domain history.

### 6.1 Sandbox phases

```text
ABSENT -> ALLOCATING -> CREATED -> STARTING -> READY
READY -> EXECUTING -> READY
READY|EXECUTING -> STOPPING -> STOPPED
ALLOCATING|CREATED|STARTING|READY|EXECUTING|STOPPING|STOPPED|UNKNOWN
    -> DESTROYING -> DESTROYED
any nonterminal phase -> UNKNOWN when observation is lost
```

`FAILED_CREATE` is a terminal operation result, not proof that no partial
resource exists. The metadata record retains a cleanup obligation until owned
resource absence is confirmed.

### 6.2 Command phases

```text
PENDING -> STARTING -> RUNNING -> EXITED
STARTING|RUNNING -> CANCELLING -> CANCELLED
STARTING|RUNNING|CANCELLING -> EXITED (natural/process result wins race)
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

The PID 1 supervisor is not the deadline owner. A minimal host guardian on the
same native Linux host as the Docker daemon runs outside the Worker cgroup under
a dedicated OS identity and service-manager supervision. Before the adapter may
release the Worker start gate, the guardian durably records and arms a monotonic
deadline plus grace/confirmation bounds for the exact provider, Run, workspace
generation/lease, sandbox ID/generation, command ID and request digest. Its
local authenticated socket is accessible only to the adapter service identity;
the Worker has no socket, token, host PID namespace, daemon endpoint or signal
permission for either trusted process. The adapter may request earlier cancel
but cannot extend, disable or retarget an armed deadline.

The guardian survives API caller/adapter loss and, at expiry, requests TERM of
the Worker process group, observes for the immutable grace, then requests
whole-container kill and targeted removal if the supervisor does not prove an
empty command tree. Container/cgroup containment—not process group membership—
covers descendants that call `setsid`, change groups or daemonize. A terminal
command result requires actual process exit plus stream completion evidence;
sandbox reuse additionally requires the exact owned cgroup to be empty. Failure
to confirm either yields `UNKNOWN`, retains the deadline/cleanup obligation and
forces whole-sandbox destruction before any reuse.

Caller loss changes no state. Adapter or adapter-to-guardian channel loss leaves
the already armed guardian active. Adapter-to-daemon management loss leaves the
deadline active but may make the later result `UNKNOWN`; the guardian retries
only the bound action and retains evidence. Guardian process failure is detected
by the service manager and authoritative outstanding-deadline record; restart
on the same host boot re-arms no later than the recorded monotonic deadline. A
boot-ID change makes the old monotonic value incomparable and triggers immediate
whole-sandbox reconciliation/stop rather than fabricating elapsed time. Any
other uncertainty triggers immediate whole-sandbox stop. Failure/compromise of
the trusted host kernel, service manager or daemon is outside the promise while
that substrate is unavailable;
after recovery every affected resource is unknown and targeted cleanup is
required. Preflight rejects an environment that cannot isolate/schedule the
guardian, protect its channel, store the binding or perform whole-container
escalation.

The material alternative is an independently protected in-container watchdog.
It is not selected because sharing the Worker cgroup lets CPU/PID/memory pressure
attack deadline enforcement and makes whole-container escalation depend on the
same failing boundary. M3 may validate the named guardian mechanism and exact
platform APIs, not defer ownership again.

Create failure is an operation result, not a sandbox phase. When inspection
proves no provider resource, the record returns to `ABSENT`; when a partial
resource exists it remains `ALLOCATING`/`UNKNOWN` with cleanup required until
`destroy`. Start failure may return to confirmed `CREATED` only if no Worker
process began and the effective resource is intact; otherwise it becomes
`STOPPED` or `UNKNOWN` and only inspect/destroy are permitted. `UNKNOWN` permits
inspect and targeted destroy only; no start, execute, collect or reuse.

### 6.3 Operation transition contract

| Operation | Allowed phase and ownership check | Result / duplicate behavior | Timeout, disconnect and retry | Evidence and cleanup; live resource possible? |
| --- | --- | --- | --- | --- |
| `create_workspace` | no record for ID; Task/Run exist and lease unclaimed | `WorkspaceRecord`; exact key replays | pre-response loss requires metadata lookup; never recreate blindly | allocation observations; partial staging cleanup; yes |
| `create_sandbox` | workspace lease valid; sandbox absent; all capabilities supported | `CREATED`; exact key replays; conflict rejected | inspect by immutable ID/labels before retry | effective config/image/ownership; partial container cleanup; yes |
| `start` | `CREATED`; full tuple/generation match | `READY`; repeated start on ready replays/observes | confirmed no-process failure may remain `CREATED`; otherwise `STOPPED`/`UNKNOWN`, inspect before retry | start/inspect observations; yes |
| `execute` | `READY`; no active/unknown command; cwd/env/limits valid | handle or terminal result; exact command replay | guardian deadline must be armed before start gate; caller loss changes nothing | binding plus ordered stream/start/exit evidence; yes |
| `inspect` | any known sandbox phase; full tuple match | current observation, including missing/unknown | read retry allowed; absence must match owned identity | inspected config/state; no mutation |
| `inspect_command` | known command and request digest | current/terminal observation | read retry allowed; unknown remains unknown | state/exit/stream completeness evidence |
| `cancel` | command `STARTING`, `RUNNING`, `CANCELLING` or `UNKNOWN` | typed cancel-requested, confirmed cancelled, already terminal, or unknown | guardian shortens deadline; TERM/grace then whole-container kill if needed; race may return actual exit | signal/cgroup/container evidence; yes until confirmed |
| `collect` | sandbox not executing; quiescence confirmed; lease valid | manifest/result; exact key replays | disconnect before durable manifest returns unknown; inspect storage before retry | walk/hash/copy observations; rejection cleanup; no new live process |
| `export_workspace` | not executing; retention explicitly `EXPORT_FOR_REVIEW` | immutable untrusted snapshot ref | no replay until snapshot identity checked | snapshot hash/size; partial export cleanup |
| `destroy` | owned resource in any non-destroyed phase | confirmed destroyed or cleanup failure/unknown; repeated confirmed destroy replays | target immutable provider ID; reconnect and inspect; never global prune | stop/kill/remove/absence observations; yes on failure |
| `reopen_owned_resources` | authenticated provider startup/reopen and Run scope | bounded observations only | safe repeat; does not resume Run | reconciles metadata/labels; cleanup decision remains external |

Cancellation race rule: acceptance of a cancel request is not cancellation.
If a natural exit is observed before the first effective signal, return the
actual `EXITED` result plus a “cancel lost race” observation. If an effective
cancel signal caused the confirmed termination, return `CANCELLED` while
retaining the observed signal/exit code. If the monotonic deadline was the first
cause, return `TIMED_OUT` even if a later cancel arrived. Simultaneous/partially
observed ordering is `UNKNOWN`; never infer the winner from receipt timestamps.
If termination, stream EOF or owned-cgroup emptiness cannot be confirmed, keep
the cleanup obligation, block reuse and destroy the whole sandbox.

## 7. Normalized failure contract

```python
SandboxFailure(
    code: SandboxFailureCode,
    phase: FailurePhase,
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
6. On the normal artifact-preserving path, collection/export first freezes or
   quiesces the Worker while tmpfs still exists, performs the bounded validated
   export, durably commits its manifest/snapshot, and only then removes the
   sandbox/tmpfs. Explicit retention stores an immutable bounded snapshot
   outside Worker control.
7. A later sandbox may import a retained snapshot only after an explicit Stage
   5 recovery decision and required verification. A successor Run creates a new
   `WorkspaceId` owned by that `RunId` and records the source snapshot/reference;
   the original workspace ownership and old handle are never mutated or reused.

Creation failure cleanup is journaled step-by-step: staging allocation, input
copy, metadata record, container create and lease acquisition each register a
targeted compensating cleanup action. Failure never triggers broad directory
or daemon cleanup.

### 8.2 Hostile artifact algorithm

The initial supported reader is a co-located trusted collector on the native
Linux Docker Engine host. It has a dedicated host UID/service, authenticated
local Engine access, read-only access needed for the target process/mount
namespace and write-only bounded artifact-store capability. It has no domain
transition authority. No daemon socket, management token, collector binary
control channel, host `/proc`, artifact-store credential or broad host path is
mounted or copied into the Worker.

The adapter resolves the exact container by immutable provider ID and ownership
metadata, compares Run/workspace/sandbox generations and lease, obtains the
container init PID from the authenticated local Engine API, and validates the
PID start identity, cgroup and mount-namespace identity. It then freezes the
exact container through the Engine API and confirms the frozen state. Because
the collector is outside the container/cgroup, it continues while the Worker is
frozen. It pins the process identity where the selected kernel supports pidfds,
opens `/proc/<init-pid>/root/workspace` once, records the directory/mount
identity, and traverses from that descriptor with Linux `openat2`-style beneath,
no-symlink/no-magic-link/no-cross-device constraints plus post-open metadata
checks. M3 selects and probes the exact primitives; inability to provide them
fails preflight. A remote Docker endpoint, native Windows process or Docker
Desktop VM does not grant the caller equivalent host `/proc`/descriptor access
and is unsupported by this initial collector profile.

Collection requires this continuously fenced frozen lease, or confirmed absence
of every untrusted Worker process while the exact container/tmpfs remains. The
collector revalidates provider/container/PID/mount/generation/freeze identity
before every root traversal batch and again before commit. A generation change,
unfreeze, PID reuse, mount replacement, container stop/removal or management
disconnect aborts the operation, discards partial trusted output and returns
`UNKNOWN`/`LOST` as applicable. The adapter records quiescence and then:

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

The one streaming copy feeds both the digest accumulator and the bounded
artifact-store writer; the stored object is sealed and its returned digest/
length compared before the manifest transaction commits. There is no second
source read. Directories contribute canonical metadata only. Renamed paths are
accepted only when their already-open descriptor still has the same identity
and requested relative name remains valid at final revalidation; otherwise the
whole result is rejected. Links and special files are never copied.

After success or failure, unfreeze occurs only if the exact container identity
and generation still match and no emergency destruction is pending. Unfreeze
failure makes the sandbox unknown and triggers targeted destruction. If safety
requires emergency whole-container stop, or the container/tmpfs disappears
before durable export commit, artifact preservation is abandoned: record
`ExportDisposition.LOST`/unavailability, discard partial output, perform safety
cleanup and never report an empty export or reconstruct fictional bytes. Loss
of these untrusted candidate bytes is distinct from authoritative Stage 1 state,
which remains outside the sandbox.

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
| Native Linux host with co-located local Docker Engine and guardian/collector, compatible API, cgroup v2 and required namespaces/seccomp/tmpfs/openat2/pidfd/procfs features | M3 target; supported only after full preflight and M4 evidence |
| Rootless Docker on Linux | evaluation variant; not yet supported because resource/network/storage semantics need the same adverse matrix |
| Docker Desktop Linux containers on Windows or macOS | development-only candidate; Linux VM behavior is not claimed equivalent to native host containers |
| Native Windows containers or macOS processes | unsupported by sandbox-v1 |
| Remote Docker Engine endpoint | unsupported by initial collector/deadline profile; transport does not supply local host descriptors or isolation |
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
- co-located host guardian deadline binding armed before Worker release, plus a
  separately privileged co-located collector used only while the exact
  container is frozen.

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
| SBX-R07 wall time | external guardian monotonic timer, TERM/grace, whole-container kill/remove | protected co-located service, local daemon API, cgroup containment | deadline binding, guardian health, process/container/cgroup inspect | adapter death, management loss, setsid/daemon descendant, stale identity, guardian interference | `TIMEOUT` only with cause/termination proof; otherwise `UNKNOWN` and destroy | `EVD-DKR-TIME-*` |
| SBX-R07 writable bytes/inodes | tmpfs `size`, `nr_blocks`/`nr_inodes`; memory cap | Linux tmpfs options supported | mount inspection and free/stat data | bounded writes and small-file fixture | `STORAGE_LIMIT_REACHED` | `EVD-DKR-STORE-*` |
| SBX-R07 output/log growth | attach streams drained; separate retention caps; daemon log disabled/bounded | runtime streaming API | retained/observed counts and daemon log inspect | finite stdout/stderr flood | exact truncation; no unbounded log | `EVD-DKR-OUT-*` |
| SBX-R08 network NONE | none network driver; no ports/proxies | none driver | inspect network plus route/interface view | loopback works; DNS/TCP external attempts | external denial; loopback retained | `EVD-DKR-NET-*` |
| SBX-R09 no secrets/env inheritance | explicit allowlist; construct env from empty base except reviewed runtime keys | adapter API | inspect environment with redaction | seed operator proxy/token then inspect | absent; presence is blocker | `EVD-DKR-ENV-*` |
| SBX-R10 artifact boundary | frozen exact container plus co-located `/proc/<pid>/root` descriptor-relative collector | local native Linux Engine, protected helper, procfs/openat2-class primitives | continuous container/PID/mount/generation/freeze fencing and same-stream store/hash | disappearance, stale identity, freeze failure, partial copy, rename/link/device/size, emergency stop | atomic collected/exported result or rejected/unknown/lost; never empty success | `EVD-DKR-ART-*` |
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
or probed by Issues #77/#78. M3/M4 must record exact versions and actual
observations.

### 9.5 Bounded upstream sandbox/backend comparison

Primary documentation and repository metadata were rechecked on 2026-09-16.
This is provider-selection input inside the existing design, not a source audit,
benchmark or decision to replace Docker. No upstream runtime code is copied or
vendored.

| Candidate | Documented enforcement and locality | Install/admin and controls relevant here | Artifact/reuse fit and evidence gap |
| --- | --- | --- | --- |
| Codex local platform-native sandbox | Local spawned commands inherit a platform boundary: macOS Seatbelt; Linux/WSL2 bubblewrap (or documented bundled helper requiring unprivileged user namespaces); native Windows `elevated` uses lower-privilege users, filesystem permissions, firewall/local policy and private desktop, while `unelevated` uses a restricted token, ACLs and weaker offline controls | macOS is documented out of box; Linux/WSL normally installs `bubblewrap`; Windows `elevated` needs administrator-approved setup while `unelevated` is a fallback. Filesystem/network permission modes and approvals are documented, but approval is distinct from enforcement | Useful mechanism evidence for a local Agent client, not documented as a reusable general-purpose provider with Symphony-K identities, durable deadline guardian, resource ceilings, tmpfs export or targeted reopen/cleanup. Codex cloud/ChatGPT Work managed execution is a separate boundary and is not compared as the local sandbox |
| OpenClaw configured tool sandboxes | Agent sandbox mode default is `off`; backend default is Docker when sandboxing applies. Docker/Podman run local containers; SSH executes on the selected remote host; OpenShell/Crabbox are managed candidates. Gateway, native plugins and control-plane RPC remain outside the tool sandbox | Docker defaults document no egress, read-only root, drop-all capabilities, init and no-new-privileges; workspace modes/binds may expose host paths. Podman reuses Docker settings with rootless/user-mapping constraints. SSH keys/host setup provide transport, while network/isolation depend on that host. Tool policy/approval gates do not become runtime isolation | Filesystem bridges/binds and backend-specific sync can move files, but they do not establish this design's hostile tmpfs collector, deadline, resource, ownership or atomic manifest contract. Default-off mode, writable binds, Gateway-side plugins/MCP tools and backend differences are explicit escape/trust paths to evaluate, not inherited guarantees |
| Docker Engine on native Linux | Local shared-kernel containers with daemon/cgroups/namespaces/seccomp/tmpfs; this design adds the guardian, collector, metadata and adverse proof | Engine/kernel/cgroup features and daemon access are required on the trusted Linux host; no Docker installation is needed for M1A/M2 portable contracts. Filesystem/network/process/resource controls are profile-dependent, not implied by installation | Only candidate matching the accepted first-provider decision and named co-located collector topology; artifact preservation still needs custom trusted code and M3/M4 evidence |
| Docker Desktop Linux containers | Containers run through Docker Desktop's Linux VM/WSL layer rather than a native Windows sandbox. Resource Saver behavior differs: on Windows WSL it pauses the Engine but does not stop the shared WSL VM | Desktop/VM/WSL installation and administration are additional prerequisites. Startup/idle behavior and configured limits are not memory measurements | Development candidate only. It lacks direct proof for the native-Linux host collector/guardian path and is not an accepted equivalent environment |
| Podman or remote managed sandbox | Podman is an alternative container engine (rootless or machine-backed); managed backends may provide remote isolation. SSH alone is only transport to a host | Each requires its own capability probe, administrative boundary, resource/network policy and authenticated management channel | Legitimate future adapter candidates behind `SandboxProvider`, not M1A/M2 implementations. None may claim Symphony-K artifact/deadline/reopen semantics from product naming alone |

Source/version record:

| Upstream | Exact observation | Primary sources and license disposition |
| --- | --- | --- |
| OpenAI Codex | repository `openai/codex` main `2aff7208fe95f331d9bb966bbd265c36ee5ecebf` (2026-09-16), release `rust-v0.154.0` | [Sandbox docs](https://learn.chatgpt.com/docs/sandboxing), [Windows sandbox docs](https://learn.chatgpt.com/docs/windows/windows-sandbox), repository Apache-2.0 `LICENSE`. Documentation, not source review, supports the mechanism statements. Any future copied/modified code would require Apache-2.0 license/notice compliance and change notices; none is reused here |
| OpenClaw | repository `openclaw/openclaw` main `33c15b86fea2baea6ff264eb97539a85c889e1ab` (2026-09-16), package/release `2026.9.4` / `v2026.9.4` | Exact documentation paths at that commit: [`modes-scope-and-backend.md`](https://github.com/openclaw/openclaw/blob/33c15b86fea2baea6ff264eb97539a85c889e1ab/docs/gateway/sandboxing/modes-scope-and-backend.md), [`supported-capability-matrix.md`](https://github.com/openclaw/openclaw/blob/33c15b86fea2baea6ff264eb97539a85c889e1ab/docs/gateway/sandboxing/supported-capability-matrix.md), [`docker-backend.md`](https://github.com/openclaw/openclaw/blob/33c15b86fea2baea6ff264eb97539a85c889e1ab/docs/gateway/sandboxing/docker-backend.md), [`podman-backend.md`](https://github.com/openclaw/openclaw/blob/33c15b86fea2baea6ff264eb97539a85c889e1ab/docs/gateway/sandboxing/podman-backend.md). MIT `LICENSE` requires copyright/license notice retention in copies/substantial portions and points to third-party notices; none is reused here |
| Docker documentation | `docker/docs` main `c2c3b7da47f49610d7b62aab90a9618ad2a6bee1` (2026-09-16) | [`tmpfs` documentation](https://docs.docker.com/engine/storage/tmpfs/) and [Desktop Resource Saver](https://docs.docker.com/desktop/use-desktop/resource-saver/); docs repository Apache-2.0. Docker component/runtime licensing must be reviewed separately before distribution; no Docker code is reused here |

No RAM, latency or startup saving is asserted. Configured memory/tmpfs limits
are ceilings, not measurements or necessarily reservations; page cache/tmpfs,
Worker workload, Engine and VM/WSL costs must not be conflated. M3 comparison
evidence, if authorized, records platform/OS/kernel/backend/version/security
profile, idle-host baseline, engine/VM idle overhead, per-active-sandbox
incremental and peak resident/committed memory, tmpfs/data/page-cache treatment,
cold and warm startup, teardown release curve, concurrency, workload, sampling
method and security-profile equivalence. Until measured on equivalent workloads,
all candidate resource/latency costs remain **unmeasured**.

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
    payload: ObservationPayload,
    completeness: ObservationCompleteness,
)

ObservationKind = CAPABILITY | LIFECYCLE | PROCESS | STREAM |
                  RESOURCE_USAGE | ARTIFACT | CLEANUP | CONTROL_CHANNEL

CapabilityPayload(
    capability_digest: Sha256Digest,
    provenance: CapabilityProvenance,
    probe_names: tuple[str, ...],      # <= 64 names, each <= 64 ASCII
)
LifecyclePayload(
    operation_kind: OperationKind,
    prior_phase: SandboxPhase | CommandPhase | WorkspacePhase,
    observed_phase: SandboxPhase | CommandPhase | WorkspacePhase,
    request_digest: Sha256Digest,
    provider_resource_id: str | None,
)
ProcessPayload(
    event: Literal["START_GATE_RELEASED", "STARTED", "NATURAL_EXIT",
                   "TERM_SENT", "KILL_SENT", "CGROUP_EMPTY", "LOST"],
    signal: int | None,
    exit_code: int | None,
    process_started_at: UtcTimestamp | None,
    process_ended_at: UtcTimestamp | None,
    termination_confirmed: bool,
)
StreamPayload(
    stream: Literal["STDOUT", "STDERR"],
    observed_bytes: int | None,
    retained_bytes: int,
    truncated: bool,
    eof_confirmed: bool,
    artifact_ref: ArtifactRef | None,
)
ResourceUsagePayload(
    cpu_usage_us: int | None,
    memory_current_bytes: int | None,
    memory_peak_bytes: int | None,
    pids_current: int | None,
    workspace_used_bytes: int | None,
    workspace_used_inodes: int | None,
    limit_event: SandboxFailureCode | None,
)
ArtifactPayload(
    disposition: Literal["COLLECTED", "EXPORTED", "REJECTED", "LOST"],
    manifest_id: ManifestId | None,
    artifact_ref: ArtifactRef | None,
    total_files: int | None,
    total_bytes: int | None,
    source_lost: bool,
)
CleanupPayload(
    action: Literal["TERM", "KILL_CONTAINER", "REMOVE", "UNFREEZE",
                    "DISCARD_PARTIAL", "CONFIRM_ABSENCE"],
    resource_kind: OwnedResourceKind,
    provider_resource_id: str,
    absence_confirmed: bool,
)
ControlChannelPayload(
    channel: Literal["ADAPTER_GUARDIAN", "ADAPTER_DAEMON",
                     "GUARDIAN_DAEMON"],
    event: Literal["BOUND", "LOST", "RESTORED", "AUTH_REJECTED"],
    deadline_binding_digest: Sha256Digest | None,
)

ObservationPayload = CapabilityPayload | LifecyclePayload | ProcessPayload |
                     StreamPayload | ResourceUsagePayload | ArtifactPayload |
                     CleanupPayload | ControlChannelPayload
```

Sequence gaps are explicit. Adapter receipt time is always present; provider
source time and duration may be unknown. The `kind` must match exactly one
payload class above. Encoded payloads are at most 32 KiB; tuples retain at most
64 elements and free-form strings use the previously defined diagnostic/string
bounds. Telemetry includes create/start/attach/exit/signal/inspect/resource-
usage/artifact/cleanup observations, but no hidden reasoning, secret values or
unbounded daemon logs.

The provider-neutral runtime metadata boundary is:

```python
OperationScope(
    provider_id: ProviderId,
    task_id: TaskId,
    run_id: RunId,
    workspace_id: WorkspaceId,
    workspace_generation: int,
    lease_id: WorkspaceLeaseId | None,
    lease_version: int,
    sandbox_id: SandboxId | None,
    sandbox_generation: int | None,
    command_id: CommandId | None,
)

OperationReceipt(
    operation_id: OperationId,
    operation_kind: OperationKind,
    request_id: RequestId,
    idempotency_key: IdempotencyKey,
    scope: OperationScope,
    request_digest: Sha256Digest,
    disposition: OperationDisposition,
    result: WorkspaceRecord | SandboxObservation | CommandHandle |
            TerminalResult | CancellationResult | ArtifactCollectionResult |
            WorkspaceExportResult | CleanupResult | None,
    failure: SandboxFailure | None,
    created_at: UtcTimestamp,
    updated_at: UtcTimestamp,
    version: int,
)

class SandboxMetadataStore(Protocol):
    def get_workspace(id: WorkspaceId) -> WorkspaceRecord | None: ...
    def get_sandbox(id: SandboxId) -> SandboxObservation | None: ...
    def get_operation(scope: OperationScope, key: IdempotencyKey) -> OperationReceipt | None: ...
    def begin_operation(
        scope: OperationScope, context: MutationContext,
        operation_kind: OperationKind, request_digest: Sha256Digest,
    ) -> OperationReceipt: ...
    def append_observation(observation: RuntimeObservation) -> None: ...
    def complete_operation(
        operation_id: OperationId, expected_version: int,
        result: OperationReceipt,
    ) -> None: ...
    def record_cleanup_obligation(
        resource: OwnedResourceObservation, expected_version: int,
    ) -> None: ...
    def list_outstanding(
        provider_id: ProviderId, run_id: RunId, limit: int,
    ) -> tuple[OwnedResourceObservation, ...]: ...
```

`OperationReceipt` is frozen and contains operation/request/key/scope/digest,
`IN_PROGRESS|SUCCEEDED|REJECTED|FAILED|UNKNOWN`, immutable result-or-failure,
created/updated timestamps and optimistic version. `begin_operation` atomically
compares generation/lease/version, rejects conflicting replay, and records the
in-progress receipt plus any cleanup obligation. `complete_operation` atomically
appends the terminal observation/result and advances the resource record;
version conflict never overwrites history. Observation append is ordered and
deduplicated by `(sandbox_id, generation, sequence, observation_id)`.
`IN_PROGRESS` has neither result nor failure; `SUCCEEDED` has exactly one result
and no failure; `REJECTED`/`FAILED` have no result and one failure;
`UNKNOWN` has no result and a `state_known=false` failure. Timestamps are
monotonic in record history (`updated_at >= created_at`) and version starts at
one and increases exactly once per successful compare-and-set.

M2 implements these provider-neutral value/port contracts and an in-memory
store/Fake for deterministic semantic tests. Reconstructing a new Fake from an
immutable exported test snapshot is **contract simulation**, not physical crash
durability or real isolation. M3 must add the durable runtime metadata adapter,
transaction/reopen behavior, guardian/collector bindings and crash evidence
before provider restart claims are real. Retention duration and operator quota
remain M3 policy, but all records are bounded outside Worker memory. The common
contracts/ports import no Docker, OpenClaw or Codex SDK and require no Docker
executable merely to import or run M2 unit/Fake tests. Usage counters remain
observations only; Stage 6 owns authoritative budget/cost ledgers.

These records are not Stage 1 `DomainEvent`s. A later trusted orchestration
service may attach their `EvidenceRef`s to a separately authorized domain
transition or Evaluation request. The provider cannot call persistence
`UnitOfWork` or change `RunState`.

### 11.2 Cleanup algorithm

1. Resolve the immutable ownership record and validate all supplied IDs and
   workspace/sandbox generations, lease and request fingerprint.
2. Inspect the provider by immutable resource ID. A missing label, changed
   label or reused name never widens the target.
3. If a command may be active, verify the guardian binding, request bounded
   graceful termination, then whole-container kill if complete command-tree
   termination is not confirmed; record the causal/race observations.
4. Inspect until the command is terminal and owned cgroup empty, or the cleanup
   deadline expires. Deadline expiry yields unknown, not success or reuse.
5. On the normal preservation path, freeze/quiesce the exact live container,
   collect/export, and commit the durable manifest/snapshot before removal.
6. On emergency stop, guardian/control failure or unexpected whole-container
   loss before export commit, record explicit artifact loss/unavailability and
   proceed with safety cleanup; never synthesize an empty successful export.
7. Remove exactly the owned container and provider-created ancillary resources.
8. Independently inspect provider and owned cgroup absence. Only then mark
   `DESTROYED`/`RELEASED`.
9. Retain a bounded cleanup obligation on disconnect/failure for startup
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

Guardian failure or stale/mismatched deadline identity never transfers control
to a Worker or an arbitrary container name. The reconciler rejects the stale
binding, marks the affected resource unknown and uses only the independently
verified current ownership record for whole-sandbox cleanup. If the trusted
host/kernel itself is unavailable, no termination or collection observation is
promised during the outage; recovery treats every possibly live resource as
unknown until exact inspection succeeds.

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
exit plus “cancel lost race” is returned. Cancellation during `STARTING` enters
`CANCELLING`; deadline-vs-cancel ordering follows the first independently
observed cause. Disconnect yields unknown and blocks another command.

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

### SCN-13 adapter loss and escaped process group

Input: after the host guardian arms the exact deadline and releases start, kill
the adapter fixture with no immediate restart; the bounded Worker forks a child
that changes session/process group. Variants drop the adapter-daemon channel,
attempt to reach/signal/starve the guardian and replay a stale binding.

Expected: the independent guardian still reaches the original deadline. TERM
may be attempted, but any unproved tree emptiness escalates to exact whole-
container kill/removal. A stale binding cannot target a new generation.
Interference or lost confirmation yields `UNKNOWN`, blocks reuse and preserves
the cleanup obligation; trusted-host loss itself is not reported as observed
termination.

### SCN-14 workspace loss during preservation

Input variants stop/remove the exact container during export, substitute stale
container/generation identity, fail freeze/unfreeze, interrupt the store after a
partial copy, present unsafe metadata, or trigger emergency destruction before
snapshot commit.

Expected: continuous fencing aborts; partial trusted bytes and manifest are
discarded. The result is rejected, unknown or explicitly `LOST` according to
the observation, never a successful empty export. Safety cleanup proceeds and
authoritative Stage 1 state remains available outside the sandbox.

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
| T-F06 | FAKE | reconstructed immutable store snapshot simulates restart discovery from ownership metadata, not Worker memory (not physical durability) | M2 |
| T-F07 | FAKE | artifact/hash bytes and manifest are atomic or absent | M2 |
| T-F08 | FAKE | armed deadline survives adapter death with no restart and produces only bound timeout/unknown cleanup semantics | M2 |
| T-F09 | FAKE | management-channel loss and guardian/control interference cannot disable or retarget enforcement | M2 |
| T-F10 | FAKE | stale deadline identity and STARTING/natural-exit/cancel races preserve actual causality or unknown | M2 |
| T-F11 | FAKE | workspace disappearance, stale container identity, freeze failure and partial copy commit no manifest | M2 |
| T-F12 | FAKE | unsafe metadata or emergency termination before preservation records rejection/loss, never empty success | M2 |
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
| T-D17 | DOCKER | adapter death with no restart does not disarm the external deadline | M3/M4 |
| T-D18 | DOCKER | adapter/guardian/daemon channel loss retains bound enforcement and unknown-state cleanup | M3/M4 |
| T-D19 | DOCKER | descendant changing process group/session or daemonizing cannot survive whole-container escalation | M3/M4 |
| T-D20 | DOCKER | Worker cannot signal, authenticate to, reconfigure or starve away the protected guardian | M4 |
| T-D21 | DOCKER | stale deadline generation and timeout/cancel/natural-exit races never target/relabel another command | M3/M4 |
| T-D22 | DOCKER | co-located collector continuously fences container/PID/mount/freeze identity and discards partial output | M3/M4 |
| T-D23 | DOCKER | workspace disappearance, freeze/unfreeze failure, unsafe metadata and emergency stop report rejection/unknown/loss | M4 |

Resource-abuse fixtures must be deterministic and small: cap+one-page memory,
cap+small-margin PIDs, fixed-duration CPU, fixed stream lengths, and tmpfs
cap+one-block/inode. Each runs in a disposable test environment with an outer
test deadline and host safety headroom. Issues #77/#78 execute none of them.

Non-Docker developer runs may skip explicitly marked Docker tests. Such a skip
is a developer convenience only. Stage 2 acceptance requires all mandatory
Docker cases on an eligible recorded environment; skipped tests are not
isolation evidence.

## 14. Requirement traceability

| Requirement | Design sections | Future tests | Owning milestone |
| --- | --- | --- | --- |
| SBX-R01 approved sandbox/no host | 3, 9.2-9.3 | T-F01, T-D01 | M2 contract; M3/M4 proof |
| SBX-R02 provider replaceability | 4-5, 9.3, 9.5 | T-F01-T-F12, architecture import check | M2 |
| SBX-R03 Run/workspace lifetime | 3, 4.3, 8 | T-U03, T-F06, T-F11-T-F12, T-D16, T-D22-T-D23 | M2/M3; Stage 5 owns reuse |
| SBX-R04 authority separation | 3, 11.1 | contract/import tests; no provider UoW dependency | M2 |
| SBX-R05 capability preflight/normalization | 4.1, 7, 9.1 | T-U05, T-F03, T-D02-D12 | M2-M4 |
| SBX-R06 privilege/mount/socket/writable boundary | 8, 9.2-9.3 | T-D02-D04 | M3/M4 |
| SBX-R07 resource/time/output bounds | 4.2, 4.4, 6.2, 9.3 | T-F08-T-F10, T-D05-T-D10, T-D17-T-D21 | M2-M4 |
| SBX-R08 typed network/fail closed | 4.2, 9.3, 10 | T-U01, T-D11 | M2/M3/M4 |
| SBX-R09 secret/env boundary | 9.2-9.3, 10 | T-U04, env adverse probe | M2/M3/M4 |
| SBX-R10 artifact claims remain untrusted | 4.5, 8.2, 11.2, 12 | T-U06, T-F07, T-F11-T-F12, T-D13, T-D22-T-D23 | M2-M4; Stage 4 evaluates |
| SBX-R11 preserved work needs recovery authority | 8.1-8.2, SCN-12, SCN-14 | T-F11-T-F12, T-D16, T-D22-T-D23 | M2-M4; Stage 5 recovery |
| SBX-R12 no Effect dispatch | 3, 11.1 | dependency/authority architecture test | M2; Stage 6 Effects |
| SBX-R13 observable cleanup/unknown state | 6-7, 11.2 | T-F03-T-F12, T-D14-T-D23 | M2-M4 |
| SBX-R14 dynamic isolation evidence | 9.3, 13 | T-D01-T-D23 | M4 and Stage 2 exit |
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

Success matrix: T-U01-U06 and T-F01-T-F12. Adverse cases cover wrong ownership,
duplicate/conflicting idempotency, active-command conflict, unknown state,
partial allocation, adapter/deadline failures, cancellation races, preservation
loss and hostile artifacts. Likely commit
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
src/symphony_k/execution/sandbox/docker/guardian.py
src/symphony_k/execution/sandbox/docker/collector.py
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
includes exact Docker/kernel/cgroup/version records and T-D01-D13 plus
T-D17-T-D19/T-D21-T-D22 results; it
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

The matrix repeats T-D01-D13 and T-D17-T-D22 independently and completes
T-D14-T-D16/T-D20/T-D23, including adapter crash, daemon disconnect, deadline
interference, artifact loss, leftover discovery, repeated cleanup and unrelated-
resource preservation. Likely commit boundaries: (1) safe adverse
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
| Can the selected Linux host provide protected guardian scheduling, local daemon control, cgroup-empty proof and the required pidfd/procfs/openat2 collector primitives? | capability unsupported; no Worker start | M3 preflight/implementation and M4 T-D17-T-D23; blocks supported profile |
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

Loss of unexported tmpfs bytes after stop/crash/emergency termination is
recorded candidate-work loss, not loss of authoritative domain state and never
a successful empty export. A live-resource unknown, cleanup
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

Candidate disposition after Issue #78's forward correction of the Issue #77
candidate:

```text
ADR-0008 = PROPOSED
Sandbox design = CANDIDATE
M1 independent review / Human approval = PENDING
M2 / Issue #79 = BLOCKED; NOT STARTED
Stage 2 runtime implementation authorized by this correction = NO
Stage 2 complete = NO
Stage 3 = PLANNED
```
