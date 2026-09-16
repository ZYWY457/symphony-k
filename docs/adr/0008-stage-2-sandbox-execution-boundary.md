# ADR-0008: Stage 2 Sandbox Execution Boundary

## Status

Proposed.

This is a Worker-produced candidate under GitHub Issue #77, corrected forward
under Issues #78 and #81 after independent reviews requested changes. Issue
#81 is the final bounded M1B technical-contract correction for Worker execution
set observation, independent deadline enforcement, first workspace lease
bootstrap and `START_FAILED` process semantics. It is not Human Accepted and
does not authorize runtime implementation.

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

The proposed initial enforcement topology separates coordination from the
independently executable fail-safe. A minimal trusted sandbox guardian is
co-located with the native Linux Docker Engine host, but it is not the sole
timer or kill actor. Before a Worker command can start, the adapter/guardian
durably records an immutable deadline bound to the exact provider, Run,
workspace lease, sandbox ID/generation, command ID and request digest, then
arms a protected service-manager timer. Expiry invokes a minimal trusted kill
helper that verifies the exact binding and resource fingerprint before
requesting whole-sandbox termination. The guardian, timer and helper run
outside the Worker container/cgroup under protected host identities; their
authenticated control/management authority is unavailable inside the
container. The adapter may start, cancel early and observe the exact bound
operation but may neither extend an armed deadline nor retarget it.

The binding records the trusted host boot identity and monotonic arm/expiry
values; wall-clock time is audit metadata only. A same-boot guardian restart
may reconcile the existing service-manager unit but cannot change its original
expiry. A host reboot makes that monotonic value incomparable and requires
immediate unknown-state reconciliation/whole-sandbox cleanup rather than a
fabricated timeout observation.

Caller, adapter, guardian or adapter-management-channel loss therefore does
not disarm the already armed service-manager deadline. During normal operation
the guardian may request TERM through the immutable image's non-root command
supervisor and observe the recorded grace interval. At expiry the independent
timer/helper verifies the immutable binding and escalates to exact whole-
sandbox kill/stop when graceful command termination is unavailable or
unproved. Process-group signaling alone is insufficient because descendants
may change session/group or daemonize.

The initial Docker profile defines the **Worker execution set** as every
untrusted process in the sandbox PID namespace except the explicitly named
trusted PID 1 command supervisor and any separately enumerated trusted helper
authorized by this design. PID 1 reaps descendants and participates in
observation. A command may become terminal/reusable only after the trusted
boundary confirms that this Worker execution set is empty; a process-group
observation is insufficient. The live PID 1 supervisor does not make the
Worker execution set nonempty. Collection requires confirmed Worker-set
emptiness or an approved freeze/quiescence boundary while the workspace is
live. Whole-sandbox resource absence is a different fact required only for
confirmed final destruction.
Any unknown or false Worker-set observation blocks reuse and forces targeted
whole-sandbox destruction before another command.

The trusted host kernel, service manager and Docker daemon remain prerequisites,
not observable guarantees during their own failure or compromise. Guardian
exit, lost control channel and guardian unresponsiveness are distinct from
service-manager, daemon and host/kernel failure. While the service manager is
healthy, guardian failure leaves the original timer/helper armed and grants no
additional budget. Service-manager or daemon failure after start yields honest
unknown state and exact-ownership reconciliation when the substrate returns.
Runtime preflight rejects an environment that cannot independently schedule
the timer/helper, protect their identity and channel, or enforce exact whole-
sandbox escalation. M3 validates the named service-manager API, supported
versions and race resistance rather than choosing a different owner.

`create_workspace` produces a staged `READY_UNLEASED` workspace with no lease
or sandbox binding. `create_sandbox` is the one deliberate exception to the
rule that later mutations supply an existing lease: it atomically verifies the
exact unleased workspace generation/version, acquires the first trusted-
allocated lease, binds the requested sandbox identity and records the
idempotent cleanup fence before external provider create. Confirmed pre-
provider rejection acquires no lease. A post-acquisition create proven to have
created no resource may release the lease through a versioned trusted-store
transition; uncertainty retains the exact lease/binding and blocks another
sandbox until inspection and targeted cleanup resolve it.

Command terminal results explicitly record whether a Worker process started.
A confirmed no-process `START_FAILED` has `process_started=false`, no process
timestamps, duration or exit code, `termination_confirmed=false`, and exact
empty/no-stream fields. If start occurrence is unresolved, the result is
`UNKNOWN` with `process_started=None`, not `START_FAILED`; operation timing
never masquerades as process lifetime.

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

Rejected. Adapter death would remove enforcement. The co-located guardian
coordinates an immutable binding, while the protected service-manager timer
and minimal exact-bound kill helper remain executable outside the Worker,
adapter and guardian process lifetimes. Their authority is limited to the
bound deadline action, inspection and evidence recording.

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
6. Do the Worker execution-set, collection-quiescence and final resource-
   absence facts prevent both live-PID-1 contradiction and premature reuse?
7. Is the protected service-manager timer/kill-helper path sufficiently
   independent from guardian process lifetime?
8. Are first-lease bootstrap and `START_FAILED`/unknown process combinations
   complete enough for deterministic M2 implementation?

Issues #78 and #81 close their requested candidate gaps but do not answer the
approval questions on behalf of the Human reviewer. Until the corrected
decision is accepted durably, ADR-0008 remains Proposed, M1 acceptance remains
pending and blocked Issue #79/M2 is not authorized by either correction.
