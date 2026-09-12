# symphony-k

An outcome-oriented AI work orchestrator. See [AGENTS.md](AGENTS.md) for the
repository documentation hierarchy and [ARCHITECTURE.md](ARCHITECTURE.md) for
system boundaries.

## Current status

Current roadmap stage: **Stage 1 — Domain Kernel**.

- Architecture source: [Stage 1 Domain Kernel plan](docs/exec-plans/active/stage-01-domain-kernel.md)
- Current completion/status source: [Stage 1 Completion Map](docs/exec-plans/active/stage-01-completion-v1.md)

Stage 1 is still in progress. Its detailed implementation history belongs in
Git history, durable Issues, task-specific Exec Plans, code, and tests rather
than a manually duplicated issue-by-issue ledger in this README.

## Development

Python **3.12 or newer** is required. `.python-version` selects Python 3.12 for
the development baseline. Install [uv](https://docs.astral.sh/uv/getting-started/installation/),
then run these commands from the repository root:

```text
uv sync --dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
```

`uv sync --dev` creates an isolated `.venv`, installs the project in editable
mode, and synchronizes the development tools using `uv.lock`. Python 3.12 can
be installed with `uv python install 3.12` if it is not already available.
After pulling dependency changes, run the sync command again. Use
`uv sync --dev --locked` when synchronization must reject a stale lock file.
Keep `uv.lock` under version control with dependency changes.

Use `uv run ruff format .` to apply formatting. Tool configuration lives in
`pyproject.toml`; development dependencies use the standard `dependency-groups`
table. The package has no runtime dependencies and uses the standard Hatchling
build backend. uv is a development tool, not a runtime dependency.

Package source lives in `src/symphony_k/`. The `symphony_k.domain` public API
provides typed IDs, actor identity/category, UTC timestamps, versions, transition
reasons and domain errors. M2 representation choices and scope are documented in
the [M2 plan](docs/exec-plans/completed/stage-01-m2-shared-types-v1.md).
Tests cover imports and value semantics; `tests/typing_examples.py` also checks
nominal ID separation under strict mypy. No runtime dependency is required.

`Objective` is an immutable snapshot with explicitly supplied state and version.
`CompletionPolicyRef` and the designated `ActorIdentity` retain references, not
policy results or permissions. `can_objective_transition` checks only structural
edge membership; `OBJECTIVE_CREATION_STATE` declares DRAFT as the sole creation
target without adding NONE to the enum. No query executes a transition, updates
a version, evaluates guards, or generates events. See the
[M3A plan](docs/exec-plans/completed/stage-01-m3a-objective-v1.md) for the field model
and validation scope.

`Task` is also an immutable snapshot with explicit state/version, one primary
`ObjectiveId` and a `frozenset[ObjectiveId]` of secondary contributions. It stores
no Objective objects and never propagates state. `can_task_transition` only
checks the sixteen structural edges; `TASK_CREATION_STATE` is DRAFT. Both entities
use `CompletionPolicyRef` from `domain/completion.py`, retaining the existing
public import. See the [M3B plan](docs/exec-plans/completed/stage-01-m3b-task-v1.md).

`RunId` identifies one concrete execution attempt. `Run` retains one `TaskId`,
an opaque `ExecutionProfileRef`, explicit state/version and optional predecessor
`RunId` provenance. `can_run_transition` checks eighteen structural edges;
`RUN_CREATION_STATE` is PENDING. Retry continues the same Run; a distinct attempt
uses a new RunId. Completion does not accept a result or complete a Task.
There is no recovery execution, and Worker authority enforcement
remains deferred to M7. See the [M4A plan](docs/exec-plans/completed/stage-01-m4a-run-v1.md).

`Outcome` is an untrusted candidate snapshot with one originating `RunId`, a
producing `ActorIdentity`, nonempty artifact references and optional evidence,
lineage and validity references. `ArtifactRef` and `EvidenceRef` are distinct
opaque values; their immutable sets neither load nor verify content.
`can_outcome_transition` checks eleven structural edges and
`OUTCOME_CREATION_STATE` is PROPOSED. Run completion cannot accept a candidate.
Verification and acceptance authority remain deferred. See the
[M4B plan](docs/exec-plans/completed/stage-01-m4b-outcome-v1.md).

`Evaluation` retains an explicit target, opaque method reference, optional
verifier and immutable original `EvaluationResult`. Entity targets use a typed
RunId/OutcomeId/EffectId plus observed EntityVersion; anchored EvidenceRef targets
have no invented entity version. Verdict and confidence retain opaque text,
without a global verdict taxonomy or numerical confidence scale. The ten-edge
query is structural only. Evaluation transition execution, effective-use derivation,
verification runtime, authority and
physical-delete enforcement remain deferred. See the
[M5A plan](docs/exec-plans/completed/stage-01-m5a-evaluation-v1.md).

`EvaluationConflictSetRecord` is immutable supporting provenance rather than a
seventh entity or lifecycle aggregate. Each version records one or more typed
Evaluation member/version references, an opaque affected scope, disagreement,
evidence, recorder/time provenance and a distinct correlation identity. A
single member requires external conflict evidence; repeated Evaluation IDs are
rejected. `can_extend_evaluation_conflict_set` checks forward, explicitly linked
append-only membership/evidence structure without mutating records, executing
Evaluation transitions or persisting history. See the
[M5B plan](docs/exec-plans/completed/stage-01-m5b-evaluation-conflict-sets-v1.md).

`EvaluationArbitrationRecord` is a separate immutable supporting record. Direct
arbitration contains exactly one member decision; conflict-linked arbitration binds an
exact `EvaluationConflictSetRef` and is checked for exact identity/correlation/member
coverage with equal-or-later observed Evaluation versions. `UPHELD`, `MODIFIED`, and
`REVERSED` describe the decision separately from `EvaluationState.ARBITRATED`, while
the prior/effective judgements, policy reference, evidence, rationale, actor, time,
correlation, and optional prior-arbitration lineage retain provenance. No API derives a
global effective judgement, resolves conflicts, mutates Evaluation content/state, or
persists history. See the
[M5C1 plan](docs/exec-plans/completed/stage-01-m5c1-evaluation-arbitration-v1.md).

`EvaluationInvalidationRecord` separately anchors one Evaluation ID and exact observed
version, a meaningful free-form reason, at least one typed evidence reference, and
actor/time/correlation provenance. `can_invalidate_evaluation` accepts only matching
PENDING, RUNNING, COMPLETED or CONFLICTED snapshots. It does not inspect verdicts,
authenticate authority, mutate Evaluation state/version, or derive conflict/arbitration
consequences. See the
[M5C2 plan](docs/exec-plans/completed/stage-01-m5c2-evaluation-invalidation-v1.md).

`derive_evaluation_effective_use` consumes one Evaluation and caller-supplied immutable
current conflict records plus complete relevant arbitration/invalidation history. It
derives `EvaluationEffectiveUseView` without selecting repository records or changing
lifecycle state. Arbitration precedence comes only from Evaluation-specific
`prior_arbitration_id` links; missing lineage and cycles are rejected, while multiple
independent terminal decisions are reported as ambiguous. Every exact supplied current
ConflictSet version must be addressed before ARBITRATED use is eligible, and INVALID
never yields an effective judgement. The resolver cannot prove that its caller supplied
complete repository history. See the
[M5C3 plan](docs/exec-plans/completed/stage-01-m5c3-evaluation-effective-use-v1.md).
