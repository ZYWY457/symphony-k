# Stage 02 M1C — UNKNOWN Frozen-Salvage Correction

**Status:** CANDIDATE — independent review and Human erratum approval PENDING.

## TaskSpec and execution precondition

```text
TaskSpec reference: https://github.com/ZYWY457/symphony-k/issues/83
TaskSpec revision: r1 - stage-02-m1c-unknown-frozen-salvage
TaskSpec access mode: direct-read
TaskSpec updatedAt: 2026-09-16T15:57:15Z
Execution readiness: READY — bounded documentation/design correction only
TaskSpec precondition: PASS
Starting HEAD: 7ff155c29de83fbcc5487698c8b72b70b2dec075
Starting parent: 21125653880e3fd16f660af96b32ce6299339b3b
Starting title: docs(governance): accept stage two m1 sandbox design
Origin: https://github.com/ZYWY457/symphony-k.git
```

The complete current Issue #83 body was read directly before mutation. Git
status was clean, root/origin/HEAD/parent/title matched, Git ran successfully,
and Python 3.12.7 plus uv 0.11.2 were callable. The complete Issue #79 body was
also freshly read at updatedAt `2026-09-16T15:57:40Z`: revision
`r3 - stage-02-m2-blocked-after-unknown-collection-stop`, BLOCKED / NOT RELEASED.
It records that #79 r2 stopped before mutation with no implementation commit.

Parent: [Stage 2](stage-02-sandbox-execution.md).
Technical input: [sandbox design](../../design-docs/sandbox-execution-v1.md).
Architectural constraint: [accepted ADR-0008](../../adr/0008-stage-2-sandbox-execution-boundary.md).

## Contradiction and bounded resolution

At historical Human Accepted design baseline
`b52df98530d8ce742b07d7f6c399ccd5b54e643b`, the design simultaneously:

- allowed collection after independently verified whole-container freeze when
  Worker-set emptiness was false/unprovable and sandbox phase became UNKNOWN;
- forbade any true quiescence sub-fact under UNKNOWN;
- limited UNKNOWN to inspect/destroy and explicitly forbade collect; and
- allowed collect from the exact independently frozen live container.

Issue #83 selects the ADR-authorized freeze alternative as one guarded,
bounded read-only salvage collect. UNKNOWN and cleanup-required remain after
success; no termination, reuse, start/execute, lease rebinding, export snapshot
or Stage 5 recovery authority follows. The accepted architecture is unchanged.
The prior Human approval remains historical truth but cannot supply an
unambiguous M2 implementation contract until this erratum is reviewed/accepted.

## Technical work and acceptance criteria

1. Close SandboxObservation invariants: UNKNOWN retains completeness UNKNOWN
   and cleanup-required, while independently proven sub-facts remain legal.
   Exact frozen salvage permits Worker-set None, quiesced true and resource-
   absent false without implying command terminality.
2. Define QUIESCENCE, QuiescenceMechanism and QuiescencePayload explicitly in
   the runtime observation union. Bind every manifest to the exact successful
   typed quiescence observation and full existing ownership/lease scope.
3. Scope collect/state/collector/cleanup rules consistently: exact live identity,
   independent freeze, continuous fencing, bounded copy, atomic commit/discard,
   retain UNKNOWN, then targeted destroy. No normal unfreeze/reuse window.
4. Preserve result vocabulary: collect uses REJECTED/UNKNOWN for failed salvage;
   source loss uses existing ArtifactPayload(LOST), never an invented collect
   disposition or empty success. Export from UNKNOWN remains prohibited.
5. Add walkthrough D using existing public operations and metadata receipts;
   update T-U07, T-F11, T-F14, T-D22/T-D23 and direct requirement traceability.

## Ordered commit plan and scope

1. `docs(architecture): clarify unknown frozen salvage collection`
   changes only the design and this plan.
2. `docs(governance): record stage two m1c correction candidate`
   changes only STATUS, the active Stage 2 parent plan and this plan; records
   the exact first-commit SHA as the M1C technical candidate.

No amend, squash, rebase, push or remote mutation. Explicit-file staging only.
No src/tests/dependency, ADR, Constitution, core-belief, product contract,
roadmap, Stage 1 history or Stage 3-14 plan changes. R2/R3/R4, provider choice
and recovery authority are out of scope. No runtime experiments are authorized.

## Validation and evidence boundary

Before each commit inspect staged name/status, whitespace and the full diff.
Check Markdown fences and tracked relative links; exact commit titles/parents/
path whitelists; protected-path and ADR-0008 blob equality; absence or explicit
scoping of old contradictory rules; typed QUIESCENCE closure; walkthrough D;
stable future-test IDs and traceability; final clean worktree.

Documentation checks are not UNIT/FAKE/DOCKER execution evidence. All catalog
cases remain future work. No Docker/systemd/cgroup/VM or adverse isolation
test is run, and no real freeze or runtime isolation is claimed.

## Candidate disposition

```text
Stage 1 = COMPLETE, unchanged
Stage 2 = ACTIVE / NOT COMPLETE
ADR-0008 = ACCEPTED and unchanged
Prior b52df985... acceptance = historical, with discovered internal ambiguity
M1C independent review = PENDING
Human approval of exact M1C erratum = PENDING
Issue #79 = BLOCKED / NOT RELEASED
M2 source code = NOT STARTED
Runtime isolation evidence = NOT YET ESTABLISHED
Stage 3 = PLANNED / not activated
remote mutation = none
```

Publication, independent review of the exact candidate, explicit Human erratum
approval and durable reconciliation must precede a newly released #79 revision.
This plan neither approves the candidate nor automatically releases M2.
