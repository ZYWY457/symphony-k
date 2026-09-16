# ADR-0008: Stage 2 Sandbox Execution Boundary

## Status

Proposed.

This is a Worker-produced candidate under GitHub Issue #77, corrected forward
under Issue #78 after independent review requested changes. It is not Human
Accepted and does not authorize runtime implementation.

## Date

2026-09-16

## Context

[ADR-0002](0002-sandboxed-worker-execution.md) requires every Worker Run to use
an approved sandbox and selects Docker as the first provider.
[ADR-0006](0006-capability-based-execution-routes-and-substrate-failover.md)
requires provider-specific behavior to remain behind an adapter, route
capability preflight before mutation, and new Run identity on reassignment.
[Execution Isolation](../core-beliefs/EXECUTION_ISOLATION.md) requires a sandbox
to belong to one Run while allowing a workspace to outlive it under later
recovery authority.

Those accepted sources intentionally do not define the provider contract,
resource lifecycle, workspace representation, network subset, output behavior,
artifact trust or cleanup semantics. Stage 2 cannot safely begin runtime coding
until those choices are independently reviewed.

Docker configuration fields are not themselves isolation evidence. Docker
shares the execution environment's kernel; enforcement also depends on the
daemon, kernel, cgroups, namespaces, filesystem and storage configuration.
Unknown or unsupported enforcement must not fall back to host execution.

## Proposed decision

### Provider and authority boundary

The Control/Execution-side caller will use a provider-neutral
`SandboxProvider`. Docker details remain inside the first adapter. The trusted
adapter may communicate with the Docker daemon. A Worker container receives no
daemon socket, daemon credentials or management endpoint.

Provider objects are Execution Plane concepts, not a seventh core domain
entity. A sandbox is immutably bound to one existing `TaskId`, one existing
`RunId`, one provider-managed workspace identity and one immutable execution
profile/image/policy snapshot. Opaque handles, resource labels and a
caller-supplied `ActorType` are not authentication or authority. Every
operation must resolve trusted provider metadata and fence Task/Run/workspace
ownership before touching a resource.

The provider reports observations and candidate artifacts only. It has no
domain repository writer, transition authority, Outcome acceptance authority
or Objective completion authority. Exit code zero closes a command, not a Run,
Outcome, Task or Objective.

### Lifecycle and command model

Sandbox and command lifecycles are provider-local and separate from
`RunState`. Creation, start, command execution, inspection, cancellation,
artifact collection and destruction use typed idempotency keys and normalized
results. The initial profile permits one active command per sandbox.

Commands are an argv tuple plus a container-relative working directory,
allowlisted environment and bounded stdin bytes. Worker text is never
interpolated into a host shell. An explicitly requested shell is an argv
command inside the sandbox and grants no host-shell authority.

Timeout, disconnect and cancellation are observations, not proof that the
process tree stopped. The provider must inspect and confirm termination or
return an unknown state requiring fenced cleanup. Duplicate requests replay a
recorded result only when identity and request digest match; a conflicting
digest fails closed.

The proposed initial enforcement topology uses a minimal trusted sandbox
guardian co-located with the native Linux Docker Engine host. Before a Worker
command can start, the guardian records and arms a monotonic deadline bound to
the exact provider, Run, workspace lease, sandbox ID/generation, command ID and
request digest. It runs outside the Worker container/cgroup under a dedicated
host identity and service-manager supervision. Its authenticated local control
socket and Docker management authority are unavailable inside the container;
the adapter may start/cancel/observe the exact bound operation but may neither
extend an armed deadline nor retarget it.

The binding records the trusted host boot identity and monotonic arm/expiry
values; wall-clock time is audit metadata only. Same-boot guardian restart uses
the original expiry. A host reboot makes that monotonic value incomparable and
requires immediate unknown-state reconciliation/whole-sandbox cleanup rather
than a fabricated timeout observation.

Caller, adapter or adapter-management-channel loss therefore does not disarm
the deadline. At expiry the guardian requests TERM through the immutable image's
non-root command supervisor, waits the recorded grace interval, then escalates
to whole-container kill/removal if complete command-tree termination is not
proved. Process-group signaling alone is insufficient because descendants may
change session/group or daemonize. The sandbox is reusable only after terminal
command/stream observations and an empty owned container cgroup are confirmed;
otherwise it is `UNKNOWN`, blocks reuse and requires targeted destruction.

The trusted host kernel, service manager and Docker daemon remain prerequisites,
not observable guarantees during their own failure or compromise. Guardian
failure is detected by service-manager/metadata reconciliation and causes an
immediate whole-sandbox stop attempt plus `UNKNOWN`; runtime preflight rejects
an environment that cannot keep the guardian separately scheduled, protect its
channel/identity or enforce whole-container escalation. M3 validates the named
mechanism rather than choosing its owner.

### Initial Linux-container profile

The first supported candidate profile is a digest-pinned Linux image on an
eligible Docker Engine environment. It requires:

- an explicit non-root numeric UID/GID;
- all Linux capabilities dropped, no privileged mode and no devices;
- a read-only root filesystem and only bounded declared writable mounts;
- `no-new-privileges` and Docker's default seccomp profile;
- private process and IPC namespaces, no host networking and no published ports;
- memory plus swap ceiling, CPU quota, PID limit, wall time and separate stdout
  and stderr retention limits;
- a size- and inode-bounded tmpfs active workspace and bounded tmpfs `/tmp`;
- no host repository, home directory, authoritative database, credential store
  or Docker socket mount; and
- explicit environment allowlisting with no operator-process inheritance.

The active tmpfs workspace is ephemeral. Cross-sandbox retention is an explicit
quiesced export into provider-owned untrusted snapshot storage, then a verified
import into a later sandbox. This preserves the lifetime distinction without
claiming that an ordinary Docker volume supplies byte or inode quotas.

The adapter must prove every required capability during M3 preflight and fail
closed if it cannot. Rootless Docker may be evaluated as a defense-in-depth
deployment option, but it is not declared supported by this proposal without
the M4 matrix. Docker Desktop Linux containers on Windows/macOS may be a
development environment, but are not equivalent to native host containers and
are not an accepted supported profile until separately tested.

### Image boundary

Trusted image provisioning is separate from Worker execution. A sandbox request
uses an approved immutable digest already present on the daemon. Runtime create
must not pull an image, accept a mutable tag as identity, or inherit an
unreviewed image entrypoint. The adapter supplies the intended executable/argv
and verifies the inspected digest and non-root configuration before start.

### Network and secrets

The contract uses the existing `NONE`, `DNS_ONLY`, `ALLOWLIST`,
`PROXY_CONTROLLED` and `FULL_INTERNET` vocabulary. Only `NONE` is proposed for
initial implementation. It means no external network interface or connectivity;
container-local loopback remains. Every other requested profile returns
`UNSUPPORTED_CAPABILITY` before Worker start.

Runtime traffic is distinct from trusted image provisioning and adapter-to-
daemon control traffic. The profile uses no host networking, port publication
or inherited proxy variables. Stage 2 issues no secrets and implements no
Secret Broker. Stage 3 provider/model access requires a separate approved
network and credential design rather than enabling unrestricted internet.

### Workspace and artifact trust

Inputs are copied by trusted code from explicit IDs into a provider-owned
staging area and imported into the bounded workspace; arbitrary caller host
paths are rejected. Workspace content is exclusively leased to one sandbox at
a time. Retention is explicit, bounded and remains untrusted candidate
material. Stage 5 must authorize and verify any recovery reuse.

Artifact collection occurs only after command quiescence is confirmed. A
trusted reader walks without following links, opens beneath the workspace root
with no-follow/descriptor-relative protections, validates the opened object,
streams it once to bounded storage while hashing those exact bytes, and records
the retained byte count. Absolute/parent paths, links, special files, multiple
hardlinks, device/archive escapes, excessive size/count/depth and post-open
identity changes are rejected. A digest proves byte identity, not correctness
or acceptance; a manifest is not an Evaluation.

For the initial supported native-Linux/local-daemon profile, that reader is a
co-located trusted host collector, not Worker code and not an assumption that a
remote Docker endpoint exposes host file descriptors. It uses the authenticated
Engine management channel to resolve and freeze the exact owned container,
verifies its immutable ID/labels, init PID, process start identity, mount
namespace, workspace mount and generation, then pins and opens
`/proc/<init-pid>/root/workspace` using Linux descriptor-relative/no-follow
primitives. It rechecks identity, frozen state and mount identity before,
during and after the bounded stream. The helper's narrow daemon/read/artifact-
store authority lives only on the trusted host and is never mounted or passed
to the Worker. Native Windows, Docker Desktop and remote-daemon deployments do
not satisfy this collector contract merely by exposing a Docker API.

Normal preservation order is: freeze/quiesce while tmpfs still exists, bounded
validated export, durable manifest/snapshot commit, then sandbox removal. On
emergency stop or unexpected whole-container loss before commit, safety cleanup
wins: record artifact loss/unavailability, never report an empty success or
regenerate bytes, and keep authoritative Stage 1 state distinct from lost
candidate workspace bytes.

### Telemetry, failure and cleanup

Bounded ordered observations bind provider, Task, Run, workspace, sandbox and
command identities plus policy/image references and known timestamps. Missing
data is represented as unknown. Usage is telemetry, not a billing ledger or a
domain event.

Failures normalize unavailable substrate, unsupported capability, invalid
scope, image/start failure, nonzero exit, timeout, cancellation, resource
limit, network denial, output limit, artifact rejection, daemon disconnect and
cleanup failure. Bounded redacted provider diagnostics may accompany the
normalized failure.

Cleanup is idempotent, ownership-fenced and targeted by trusted resource
identity. Provider labels plus metadata outside Worker memory support discovery
of owned leftovers after process restart. Destruction is not reported until
absence is confirmed. Global prune, name-prefix-only deletion and removal of
unowned resources are prohibited. This is resource cleanup, not Stage 5 Run
recovery or exactly-once Effect execution.

The provider-neutral contract includes closed immutable records for workspace,
sandbox/command observations, cancellation, export, cleanup, owned-resource
reopen and in-progress operations plus per-kind observation payloads. Unknown
observation time is not process end time; unconfirmed termination has no
`ended_at` or invented exit code. Timeout cause, process disposition, output
truncation and cleanup disposition remain separate. Request IDs/idempotency
keys are allocated and durably retained by the trusted caller before dispatch;
resource IDs and observations are fenced by generation/lease and canonical
request fingerprints. A deterministic Fake may simulate these contracts but
cannot claim real enforcement capability.

## Consequences

### Positive

- The first coding batch receives concrete provider, identity and failure
  semantics without coupling the Domain Kernel to Docker.
- Host execution, unsupported network profiles and missing enforcement fail
  closed.
- Output, writable storage and artifacts are bounded independently of Worker
  cooperation.
- Workspace retention and provider restart cleanup remain possible without
  promoting surviving bytes to trusted evidence.
- Stage 3 can later integrate through typed commands and observations without
  acquiring sandbox-management authority.

### Costs and limitations

- The candidate supports only `NONE`, so it cannot yet run network-dependent
  agents or package installation.
- Bounded tmpfs reduces available workspace size and counts toward the memory
  cgroup. Quiesced export is required before sandbox teardown; a crash can lose
  unexported candidate bytes.
- Docker shares a kernel and trusts the host, daemon, administrator, approved
  image and enforcement configuration. This is not microVM isolation.
- Real enforcement and cleanup claims remain unproven until mandatory M3/M4
  Docker tests run on an eligible environment.
- Rootless Docker and Docker Desktop behavior remain unaccepted environment
  variants pending separate evidence.

## Alternatives considered

### Bind the host repository directly into the Worker container

Rejected. It exposes authoritative work and makes traversal, cleanup and blast
radius depend on Worker behavior.

### Use a normal Docker volume and call it a storage quota

Rejected. Volume persistence does not itself prove per-workspace byte/inode
enforcement. The proposed active workspace uses explicit tmpfs size/inode
bounds and exports only through a trusted boundary.

### Permit a Boolean `network_enabled`

Rejected. It collapses the accepted policy vocabulary and encourages a silent
switch to unrestricted connectivity.

### Allow multiple concurrent commands per sandbox

Deferred. It complicates cancellation, output attribution, artifact quiescence
and resource accounting without a Stage 2 requirement. The initial contract
rejects a second active command.

### Use shell command strings

Rejected. Host interpolation creates an injection boundary and blurs the
container/host distinction. Explicit argv is the default; an in-container shell
must be explicitly selected as argv.

### Treat timeout or client loss as confirmed termination

Rejected. Neither proves the container process tree stopped. Unknown state
requires inspection and fenced cleanup.

### Let the adapter process own the only deadline timer

Rejected. Adapter death would remove enforcement. The co-located guardian owns
the timer outside the Worker/adapter lifetime and retains only deadline,
signal/whole-container-stop, inspection and evidence-recording authority.

### Use Docker archive/copy or a remote API as the trusted tmpfs reader

Rejected for the initial contract. Those interfaces do not by themselves
provide the required Linux descriptor-relative traversal, continuous identity
fencing and same-byte hash/retention observation. A future collector mechanism
may replace the co-located host helper only after equivalent adverse evidence.

### Automatically trust or reuse retained workspace state

Rejected. Survival proves neither integrity nor recovery suitability. Stage 5
owns recovery authority and later verification.

### Make rootless Docker or a microVM mandatory now

Not selected. Rootless limitations need environment-specific evidence, while a
microVM would broaden v1 scope. Both remain possible provider/deployment
variants behind the same contract.

## Required evidence before acceptance

The detailed [sandbox execution candidate](../design-docs/sandbox-execution-v1.md)
defines stable requirements, future test cases and M2-M4 ownership. Acceptance
requires independent review of that traceability and explicit Human answers to:

1. Is the provider/authority boundary sufficient to keep domain transitions and
   acceptance outside the sandbox layer?
2. Are the proposed identity fencing, one-command rule and unknown-state
   semantics acceptable for M2?
3. Is bounded tmpfs plus explicit untrusted snapshot export the accepted first
   workspace strategy?
4. Is `NONE` the only accepted initial network profile?
5. Is the proposed Linux Docker environment/support boundary honest and narrow
   enough for M3/M4 evidence?

Issue #78 closes the requested candidate gaps but does not answer the approval
questions on behalf of the Human reviewer. Until the corrected decision is
accepted durably, ADR-0008 remains Proposed, M1 acceptance remains pending and
blocked Issue #79/M2 is not authorized by this correction.
