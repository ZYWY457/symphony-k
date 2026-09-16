# Stage 02 — Sandbox Execution

**Status:** ACTIVE - historical M1 design HUMAN ACCEPTED; M1C CANDIDATE;
M2 BLOCKED / NOT STARTED
**Constitutional baseline:** `constitution-v0.1`

**Runtime implementation:** NOT YET STARTED

**Sandbox ADR/design:** HUMAN ACCEPTED at `b52df98530d8ce742b07d7f6c399ccd5b54e643b`

The acceptance above is historical. ADR-0008 remains Accepted and unchanged;
the design's discovered UNKNOWN collection ambiguity requires the M1C erratum
to be reviewed and accepted before it can serve as an unambiguous M2 contract.
Current M1C technical candidate:
`77acfbdaf2bed6f0536873fafc8eb7a12599da83`
(`docs(architecture): clarify unknown frozen salvage collection`), parent
`7ff155c29de83fbcc5487698c8b72b70b2dec075`.
Independent review and explicit Human erratum approval are PENDING.

**Runtime isolation evidence:** NOT YET ESTABLISHED

**Stage 2 complete:** NO

## Activation record

Stage 2 design work was activated on 2026-09-16 by the durable TaskSpec in
GitHub Issue #77, revision `r1 - stage-02-m1-design-start`, against repository
baseline `60b647f825d2eed4dc56a4d3087f165545a1ea88`. The Issue was read directly
from GitHub at observed `updatedAt` `2026-09-16T07:50:33Z` before mutation.

This activation authorized M1 architecture/design only. At activation it did
not accept the proposed ADR or candidate design, authorize runtime source or
test changes, or open Stage 3. The later cumulative M1B design baseline
`b52df98530d8ce742b07d7f6c399ccd5b54e643b` passed independent technical review
and received explicit Human M1 design approval on Issue #81. Issue #82 records
that approval without releasing M2 or opening Stage 3.

## Objective and why this stage exists

Provide the first enforceable Worker execution boundary. Workers are untrusted;
dependency isolation alone is insufficient, and host execution is not the
default Worker path.

## In scope

- `SandboxProvider` abstraction and first `DockerSandbox` provider;
- `Workspace` abstraction with lifetime distinct from a sandbox;
- bounded command execution, cancellation and output limits;
- CPU, memory, process and wall-time limits;
- network policy abstraction with a safe default;
- artifact collection with integrity metadata;
- teardown, cleanup, telemetry and provider-neutral failure normalization.

## Out of scope

- AgentDriver or model integration;
- scheduling, routing, verification, recovery orchestration or Effect dispatch;
- privileged containers, Docker socket exposure or host-as-Worker execution;
- remote providers and microVMs.

## Architecture boundaries

The Control Plane requests execution through a provider-neutral contract. The
Docker adapter owns Docker details. A sandbox belongs to one Run; a workspace
may survive it only under explicit trusted recovery policy. The domain kernel
does not import Docker/runtime concepts.

## Expected new interfaces and concepts

`SandboxProvider`, `SandboxSpec`, `SandboxHandle`, `Workspace`, `CommandSpec`,
`CommandResult`, `ResourceLimits`, `NetworkPolicy`, `ArtifactManifest`,
`SandboxTelemetry` and normalized sandbox failure information. Required ADRs
must approve lifecycle, network enforcement, workspace trust and resource
accounting before those contracts become implementation commitments.

The accepted M1 design artifacts are:

- [ADR-0008: Stage 2 Sandbox Execution Boundary](../../adr/0008-stage-2-sandbox-execution-boundary.md)
  — **Accepted**;
- [Sandbox Execution v1](../../design-docs/sandbox-execution-v1.md) —
  **historical Human Accepted M1 contract** at
  `b52df98530d8ce742b07d7f6c399ccd5b54e643b`, now carrying an unaccepted M1C
  candidate erratum under
  [the Issue #83 correction plan](stage-02-correction-m1c-unknown-frozen-salvage-v1.md).

## Cross-stage dependencies

Requires completed Stage 1, ADR-0002 and ADR-0006. It supplies Stage 3's
execution substrate and later recovery/routing health inputs.

## Security and trust requirements

Default non-root execution, dropped capabilities, no privileged mode, no host
root or Docker socket mount, controlled writable workspace, enforced resource
limits, explicit network policy, bounded output and reliable cleanup. Secrets
are absent unless a later scoped capability boundary authorizes them.

## Failure model

Normalize image/start/command/timeout/resource/network/artifact/cleanup
failures without hiding provider diagnostics. A cleanup failure is observable;
an unavailable or non-enforcing sandbox fails closed before Worker execution.

## Milestones

1. **S2-M1 accepted:** activation plus ADR/design candidate, M1A correction
   under Issue #78, and final bounded R1-R4 M1B correction under Issue #81.
   The exact technical baseline
   `b52df98530d8ce742b07d7f6c399ccd5b54e643b` passed independent cumulative
   M1B review with **ACCEPT** and received explicit Human M1 design approval.
2. **S2-M2 not started / blocked:** Issue #82 governance review accepted
   `7ff155c29de83fbcc5487698c8b72b70b2dec075`. Issue #79 r2 was then released,
   but stopped before mutation on the UNKNOWN/collection contradiction.
   Current #79 r3 is BLOCKED / NOT RELEASED. Issue #83's M1C correction must
   pass independent review and explicit Human erratum approval, with durable
   reconciliation before a new READY revision and fresh M2 launch.
3. **S2-M3 proposed:** implement Docker lifecycle, enforced constraints,
   artifacts, telemetry and targeted cleanup on an eligible environment.
4. **S2-M4 proposed:** execute adverse real-Docker, crash/reopen and cleanup
   evidence plus operational documentation.
5. Reconcile milestones, perform independent Human Stage 2 Exit Review, and
   leave Stage 3 blocked until that exit is accepted and durably reconciled.

## Proposed bounded Issue decomposition

- architecture/ADR and threat-model review;
- workspace and provider ports;
- bounded command/result contract;
- Docker lifecycle and isolation defaults;
- resource/network enforcement;
- artifacts, telemetry and cleanup;
- adversarial integration tests and stage reconciliation.

Each Issue requires its own durable TaskSpec; this parent plan cannot authorize
the complete stack.

## Validation strategy

Contract tests with a fake provider; Docker integration tests; negative mount,
socket, privilege and network tests; CPU/memory/process/time enforcement;
output truncation; artifact hashes; repeated teardown; orphan/leak inspection;
and provider-failure normalization. Tests must demonstrate host isolation rather
than infer it from configuration text.

## Human Exit Review questions

- Can arbitrary bounded commands run without using the host as Worker runtime?
- Are privilege, socket, mount, resource, output and network defaults enforced?
- Can a failed or malicious Run retain authority after teardown?
- Are workspace survival and artifact trust explicit and attributable?
- Can Docker be replaced without changing domain or Control Plane semantics?

## Stage Definition of Done

Temporary Docker sandboxes execute bounded commands under demonstrably enforced
constraints, collect attributable artifacts/telemetry, normalize failures and
clean up reliably. No AgentDriver is implemented. Human Exit Review is accepted
and durably reconciled before Stage 3 activation.

## M1 evidence, acceptance and next gate

Issue #77 produced the two design artifacts above without runtime source, test,
dependency or Docker mutation. The candidate defines stable requirement and
future test IDs, provider operations, lifecycle and failure tables, ownership
fencing, hostile artifact handling, Linux-container enforcement claims, a
`NONE`-only initial network profile, cleanup/reopen semantics and the M2-M4
coding map.

Documentation validation for this candidate checked staged name/status,
whitespace, complete diffs, Markdown fences, tracked relative links, stale
planned-path references, current-status consistency, the twelve remaining
planned Stage 3-14 parent files, requirement/test traceability and protected
paths. Official Docker documentation was consulted on 2026-09-16; no Docker
runtime or proposed test matrix was executed.

Independent review requested changes to deadline ownership/termination,
trusted live-workspace collection and public-contract completeness. Issue #78
produced a forward M1A correction without rewriting Issue #77 history or
starting M2. The correction also records a bounded primary-source comparison of
Codex, OpenClaw and lower-footprint backend candidates without changing
ADR-0002's Docker-first decision.

The durable review of candidate `613d71b90c36b573578f6fffb9a6c7dd9606478f`
then recorded REQUEST CHANGES for R1-R4. Issue #80 persisted that review and
hardened handoff continuity without changing the technical design. Issue #81
produced the final bounded M1B technical correction at
`b52df98530d8ce742b07d7f6c399ccd5b54e643b`: Worker execution-set emptiness is
separate from collection quiescence and whole-resource absence; a protected
service-manager timer/helper remains executable after guardian failure; first
workspace lease acquisition is atomic in `create_sandbox`; and no-process
`START_FAILED` has closed time/exit/stream semantics. The prior review artifact
remains historical evidence against the prior candidate and is not rewritten.

The exact cumulative M1B technical candidate
`b52df98530d8ce742b07d7f6c399ccd5b54e643b` received an
[independent technical review disposition of **ACCEPT**](https://github.com/ZYWY457/symphony-k/issues/81#issuecomment-5698811579)
and then
[explicit Human M1 design approval](https://github.com/ZYWY457/symphony-k/issues/81#issuecomment-5699311994)
for ADR-0008 and the cumulative design. This acceptance does not claim Docker,
systemd, cgroup, VM, process-race, artifact-race or resource-adverse evidence.

Issue #82's independent governance review subsequently recorded **ACCEPT**
against `7ff155c29de83fbcc5487698c8b72b70b2dec075`. The resulting #79 r2
release stopped before mutation because the design both allowed collection
after independent freeze under UNKNOWN and prohibited that observation/operation.
Issue #79 r3 records the STOP and blocks M2; Issue #83 produces the bounded
M1C technical candidate `77acfbdaf2bed6f0536873fafc8eb7a12599da83`.

M1C preserves ADR-0008 and adds typed QUIESCENCE evidence, independent exact
freeze guards and a single bounded salvage collect. Success retains UNKNOWN
and cleanup, never grants process termination/reuse/export/rebinding, and
proceeds to targeted destruction. Walkthrough D and T-U07/T-F11/T-F14/
T-D22/T-D23 describe future verification; no runtime test was run.

Next gate: separately authorized publication, independent review of that exact
M1C technical candidate, explicit Human approval of the erratum and durable
acceptance reconciliation before a new READY #79 revision. This governance
record does not accept M1C or release M2. Runtime implementation is not started,
Stage 2 remains active and incomplete, and Stage 3 remains planned.
