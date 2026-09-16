# Stage 2 M1A Independent Review

## Review identity and disposition

- **Reviewed candidate:**
  `613d71b90c36b573578f6fffb9a6c7dd9606478f`
- **Candidate title:**
  `docs(architecture): close sandbox execution contract gaps`
- **Corrected history:** Issue #77 candidate + Issue #78 forward correction
- **Review role:** independent AI technical/design review
- **Independent review disposition:** **REQUEST CHANGES**
- **Human disposition:** **PENDING**; this review implies neither Human rejection
  nor Human approval
- **Runtime isolation evidence from this review:** none; no Docker, container or
  adverse execution was run

## Findings

### R1 — P1 — Worker termination boundary conflicts with live PID 1 / workspace preservation

The candidate requires a trusted PID 1 command supervisor to remain alive,
allows a sandbox to return to a reusable or collection-ready state after a
command, and uses an `owned cgroup empty` condition as a reuse or cleanup gate.
If `owned cgroup` is the whole container cgroup, the live supervisor prevents
that condition. Emptying the whole container cgroup before normal collection
also conflicts with preserving the live tmpfs workspace used by the current
collector path.

A technical correction must distinguish:

```text
confirmed Worker command/descendant termination
workspace quiescence suitable for collection
whole-container termination/removal
```

A separate Worker containment subtree is one possible observation boundary,
not a decision made by this review. The correction must define the boundary
without this governance task prescribing an unreviewed implementation.

### R2 — P1 — Guardian failure lacks an independently executable deadline-enforcement path

Moving the deadline from the adapter into a co-located guardian addresses
caller or adapter loss, but restart and reconciliation do not enforce a
deadline while the guardian itself is failed or unresponsive. Persisting the
original deadline prevents a reset; it does not execute termination.

A technical correction must identify the separately protected mechanism that
detects guardian failure, the exact resource it can safely terminate, how that
binding exists before Worker start, and the evidence that distinguishes
confirmed termination from `UNKNOWN`. It need not promise survival of a
trusted-host or kernel failure; that substrate trust boundary must remain
explicit.

### R3 — P2 — Initial workspace lease/bootstrap path is incomplete

Later mutations and `create_sandbox` require an effective workspace lease, but
the current `WorkspaceSpec` and `create_workspace` path do not fully define how
the first lease ID and sandbox binding are created and returned without hidden
state mutation.

A technical correction must define one complete path from no workspace record
to a valid lease and sandbox binding, including failure, rollback and
idempotency semantics.

### R4 — P2 — `START_FAILED` process-time semantics are incomplete

The candidate correctly prohibits inventing `ended_at` when termination is
unknown, but its generic terminal-result wording and `START_FAILED` disposition
do not close the case in which no process was ever started.

A technical correction must distinguish completion of a start attempt from
process termination and define legal combinations of `started_at`, `ended_at`,
`termination_confirmed`, `exit_code` and stream fields for `START_FAILED`.

## Evidence boundary and readiness consequence

This review used repository cross-consistency inspection and primary
platform/runtime documentation where applicable. It did not execute Docker,
systemd, cgroup, process, artifact-race or resource-abuse tests. Planned M3/M4
tests are not evidence from this review, and these findings describe contract
gaps rather than empirical runtime failures.

Issue #79 therefore remains **BLOCKED** and unreleased. The next technical work,
after the Issue #80 governance handoff is accepted, is a bounded correction of
R1-R4 under a future concrete TaskSpec. This review record does not resolve the
findings or accept the candidate.
