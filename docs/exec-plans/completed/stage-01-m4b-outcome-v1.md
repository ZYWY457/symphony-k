# Stage 1 M4B — Outcome Snapshot, Candidate Provenance and Lifecycle Contract

**Version:** 1
**Status:** Implementation and required validation completed, 2026-09-07
**Scope:** [Implementation #4B / GitHub Issue #7](https://github.com/ZYWY457/symphony-k/issues/7), under the accepted [Stage 1 Exec Plan](../active/stage-01-domain-kernel.md), [ADR-0005](../../adr/0005-core-state-machine-semantics.md), and [Outcome design](../../design-docs/state-machines.md#6-outcome).

## Boundary Review

No conflict with the accepted hierarchy was found. This implements the existing Outcome entity and its structural contract only, using standard-library and existing M2 primitives. No architectural amendment, storage policy or new runtime dependency is needed. Initial index and working tree were clean.

In scope: immutable candidate snapshots; six Outcome states; one originating RunId; producer provenance; small opaque ArtifactRef/EvidenceRef values; candidate lineage; optional validity boundary; eleven structural state-to-state edges; PROPOSED-only creation.

Out of scope: duplicated Task ownership, Run lookup/mutation, producer authorization, Evaluation/conflict sets, verification/acceptance policy, Transition Engine, events, persistence, artifact/evidence storage or loading, URI/hash/serialization protocols and all M5+ work.

## Bounded Steps

1. Add immutable references and Outcome representation. Accept when provenance is typed, artifacts are nonempty, collections are immutable and lineage cannot self-reference.
2. Add independent tests for all 36 state pairs, eleven edges, post-judgment exits, two strict sinks and passive provenance. Replace only the two obsolete M4A assertions that the Outcome type is absent; keep Run behavior unchanged and verify completed Run/candidate independence with actual candidate snapshots.
3. Run every Issue validation, inspect staged names and diff against the explicit whitelist, create one local commit, then verify committed names/content match the inspected index. No git push or other remote mutation is authorized.

## Field Model and Decisions

| Outcome field | Type / meaning |
| --- | --- |
| outcome_id | OutcomeId |
| run_id | One required originating RunId; no Task ownership field or Run object |
| state | OutcomeState, explicitly supplied; construction is not a transition |
| version | EntityVersion, explicitly supplied; no initial-value convention |
| producer | ActorIdentity for the producing/proposing principal; any accepted category, no acceptance authority |
| artifact_refs | Required nonempty frozenset[ArtifactRef] |
| evidence_refs | frozenset[EvidenceRef], default empty; does not imply independent verification |
| valid_until | Timestamp or None, default None; no automatic expiry |
| prior_outcome_id | OutcomeId or None, default None; earlier candidate from which this one was reconsidered/derived |
| superseded_by_outcome_id | OutcomeId or None, default None; replacement identity, required for a SUPERSEDED snapshot |

Outcome, ArtifactRef and EvidenceRef are frozen, slotted dataclasses. Each reference wraps one non-whitespace opaque string named value, preserving supplied text without selecting syntax or accessing content. Artifact and evidence references are nominally distinct even for the same string. Equality/hashability are ordinary value-object semantics, not a content-hashing protocol.

Collections use frozenset because no artifact/evidence ordering has domain meaning in this Issue; duplicate equal references cannot be stored. Input must already be a frozenset of the correct reference type. Mutable or other collections, empty artifacts and mixed/wrong reference types are rejected with InvalidDomainValue. Evidence may remain empty in any represented state: deciding what evidence justifies that state is a later guard, not a constructor assertion.

The two lineage fields serve different purposes: prior_outcome_id preserves the provenance of a new candidate before any supersession decision, while superseded_by_outcome_id retains the replacement on the old candidate. Neither field is automatically derived from or synchronized with the other. Both validate type/non-self-reference only; SUPERSEDED requires a replacement ID as a local representation invariant. Other states may carry passive lineage references without automatically changing state. Existence, acyclicity, same Task/scope and replacement acceptance are deferred cross-record guards. Originating Run and all old snapshots remain unchanged.

The private frozenset of eleven typed pairs is exposed only through can_outcome_transition; raw/non-OutcomeState inputs are rejected. OUTCOME_CREATION_STATE is PROPOSED and NONE is not a state. ACCEPTED and REJECTED only exit to SUPERSEDED or EXPIRED; those latter states are strict sinks. No acceptance, mutation or replacement method is added.

Candidates and producer-supplied evidence remain untrusted. No Boolean trusted/verified/approved fields exist. Constructing an ACCEPTED snapshot or returning True for a structural edge does not authorize acceptance or establish its evidence. Worker self-acceptance enforcement remains M7's responsibility. Completed Runs can have zero or multiple candidates in any represented state; no state propagates to Run, Task or Objective.

## Required Validation

```text
uv sync --dev --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
git diff --check
```

## Local Commit Whitelist

- README.md
- docs/exec-plans/completed/stage-01-m4b-outcome-v1.md
- src/symphony_k/domain/__init__.py
- src/symphony_k/domain/candidate_refs.py
- src/symphony_k/domain/outcome.py
- tests/test_candidate_refs.py
- tests/test_outcome.py
- tests/test_outcome_lifecycle.py
- tests/test_run.py
- tests/typing_examples.py

## Validation Evidence

Python 3.12.7 with existing locked pytest 9.1.1, Ruff 0.16.6 and mypy 1.20.2. No dependency, lock-file or quality-configuration changes.

| Required command | Final result |
| --- | --- |
| `uv sync --dev --locked` | Exit 0; resolved/checked 13 packages |
| `uv run pytest` | Exit 0; 782 passed, no warnings |
| `uv run ruff check .` | Exit 0; all checks passed after shortening one comment |
| `uv run ruff format --check .` | Exit 0; 63 files already formatted |
| `uv run mypy src tests` | Exit 0; no issues in 34 source files |
| `git diff --check` | Exit 0; only existing Windows LF-to-CRLF notices |

Independent tests cover all 36 state pairs, exactly eleven edges, six exact states/no aliases, PROPOSED-only creation, two strict sinks and the restricted ACCEPTED/REJECTED exits. Model tests cover explicit versions, immutable origin/producer/content references, nonempty typed artifacts, empty/untrusted evidence, duplicate elimination, all producer categories, typed non-self lineage, required replacement identity for SUPERSEDED, and optional/non-automatic expiry. Tests represent multiple independently identified candidates for a completed Run and show that constructing acceptance snapshots does not mutate Run, Task or Objective. Static examples reject mixed artifact/evidence references, wrong origin/identity types and raw state strings.

Only the obsolete M4A assertions that Outcome/OutcomeState do not exist were replaced; all Run lifecycle/model code remains unchanged and its tests pass. The new tests retain Run/candidate independence with actual Outcomes. No Evaluation or acceptance framework is needed to represent VALIDATING or ACCEPTED snapshots.

Import sorting and formatting were applied only to the eight new/modified Python files. An overlong comment was shortened and lint rerun successfully; no quality setting was relaxed. Accepted documentation and prior domain implementations are unchanged. No unresolved architecture conflict, runtime dependency, storage protocol, initial-version convention or scope deviation was introduced. Authoritative acceptance and Worker self-acceptance enforcement remain deferred to M7.

## Local Commit and Remote Boundary

The actual staged list and diff must match the ten-file whitelist above, and staged blobs must match the validated working files. Run `git diff --cached --name-status` and `git diff --cached --check` before committing; compare `git diff-tree --no-commit-id --name-only -r HEAD` and committed blobs to that inspected scope afterward. Report the exact local hash outside the commit itself.

Remote access for this Issue is limited to reading the GitHub Issue. No git push, PR/Issue mutation, remote branch/tag mutation or release publication is authorized or performed by this work. Stop after the validated local commit; human publication remains separate. Structural contract validation does not establish authoritative acceptance enforcement or completion of the whole Stage 1.
