# Stage 1 M5A — Evaluation Core and Lifecycle Contract

**Version:** 1
**Status:** Implementation and required validation completed, 2026-09-07
**Scope:** [Implementation #5A / GitHub Issue #8](https://github.com/ZYWY457/symphony-k/issues/8), under the accepted [Stage 1 Exec Plan](../active/stage-01-domain-kernel.md), [ADR-0005](../../adr/0005-core-state-machine-semantics.md), and [Evaluation design](../../design-docs/state-machines.md#7-evaluation).

## Boundary Review

No conflict with the accepted hierarchy was found. This implements existing Evaluation concepts and the specified result-presence contract; it does not amend authority, lifecycle or verification semantics. Initial working tree and index were clean. Only standard-library and existing primitives are needed.

In scope: immutable Evaluation snapshots, explicit versioned entity/evidence targets, verifier provenance, opaque method/verdict/confidence values, immutable result content, six states and ten structural state-to-state edges.

Out of scope: verdict taxonomy, numeric confidence scale/calibration, target lookup, verification execution, authority/independence checks, ConflictSet/membership/correlation, ArbitrationRecord/dispositions/effective judgment, invalidation history, physical deletion enforcement, Transition Engine, persistence, events and M5B/M5C behavior.

## Bounded Steps

1. Implement frozen target/content/snapshot representations and explicit public exports. Accept when target identity/version combinations and local result/state compatibility reject malformed data without verifying related records.
2. Test all 36 state pairs against an independent ten-edge oracle, immutable original content, four target categories, opaque judgments, and the exact result-presence matrix. Add static examples that reject malformed target versions and wrong reference/value types.
3. Run every required command, inspect the actual staged names and diff, create one local commit containing only the explicit whitelist, and verify committed files/content match the staged audit. No remote mutation is authorized.

## Representation Decisions

| Evaluation field | Type / meaning |
| --- | --- |
| evaluation_id | EvaluationId |
| state | EvaluationState, explicitly supplied |
| version | EntityVersion, explicitly supplied; no initial-value convention |
| target | EvaluationTargetRef |
| method | EvaluationMethodRef |
| verifier | ActorIdentity or None, default None; provenance, not authority |
| result | EvaluationResult or None, default None; original recorded content |

EvaluationTargetRef is a frozen two-field wrapper around a sum of existing reference types. Its `reference` is RunId, OutcomeId, EffectId or EvidenceRef; the concrete type discriminates the category, so there is no independent kind label that could disagree with an ID. `version` is required EntityVersion for entity IDs and must be None for anchored evidence. Constructor overloads express these two alternatives statically; runtime validation enforces the same relation. No artifact-scope collection is added because identity plus observed entity version (or the anchored EvidenceRef itself) meets this Issue's scope requirement. No reference proves current existence/content validity.

EvaluationMethodRef retains non-whitespace method_id/method_version strings. EvaluationVerdict and EvaluationConfidence are distinct frozen wrappers around a non-whitespace `value: str`, preserved exactly. Any supplied meaningful representation is opaque: no PASS/FAIL enum, range, units, ordering or global calibration is selected. Numerical calibration and confidence gates belong to later verification design.

EvaluationResult retains typed verdict/confidence, non-whitespace reasoning_summary, and a frozenset of EvidenceRef (default empty). Evidence order has no meaning here; set semantics remove duplicates. Only a frozenset with typed elements is accepted; references are neither loaded nor promoted to trusted evidence. The Issue specifies no minimum evidence count; sufficiency is deferred to verification guards. Original result, verifier, method and target references are immutable snapshot content. InvalidDomainValue is reused for malformed construction.

Result compatibility: PENDING/RUNNING require no result; COMPLETED requires a result; CONFLICTED/ARBITRATED/INVALID permit either. No result is invented, erased or rewritten by a lifecycle query. INVALID denotes unusable verification, not unfavorable verdict text. Verifier absence is representable without adding a new state-dependent constructor rule; assignment and independence are later authoritative transition guards. No actor category itself grants authority.

The private frozenset contains exactly ten typed edges and is queried only through can_evaluation_transition. EVALUATION_CREATION_STATE is PENDING; NONE is not a state. ARBITRATED and INVALID are strict sinks. ARBITRATED does not imply reversal and carries no disposition in M5A. Snapshot construction/copying is not authoritative history, and no mutation or delete API is supplied. Cross-version result preservation and physical no-delete enforcement will require later append-only records/repositories; M5A does not claim those are implemented.

## Required Validation

```text
uv sync --dev --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
git diff --check
```

## Explicit Local Commit Whitelist

- README.md
- docs/exec-plans/completed/stage-01-m5a-evaluation-v1.md
- src/symphony_k/domain/__init__.py
- src/symphony_k/domain/evaluation.py
- src/symphony_k/domain/evaluation_target.py
- src/symphony_k/domain/evaluation_result.py
- tests/test_evaluation.py
- tests/test_evaluation_targets.py
- tests/test_evaluation_result.py
- tests/test_evaluation_lifecycle.py
- tests/typing_examples.py

## Validation Evidence

Python 3.12.7, with existing locked pytest 9.1.1, Ruff 0.16.6 and mypy 1.20.2. No dependency, lock-file or quality-configuration changes.

| Required command | Final result |
| --- | --- |
| `uv sync --dev --locked` | Exit 0; resolved/checked 13 packages |
| `uv run pytest` | Exit 0; 980 passed, no warnings |
| `uv run ruff check .` | Exit 0; all checks passed |
| `uv run ruff format --check .` | Exit 0; 71 files already formatted |
| `uv run mypy src tests` | Exit 0; no issues in 41 source files |
| `git diff --check` | Exit 0; only existing Windows LF-to-CRLF notices |

Tests check all 36 state pairs against the independent ten-edge oracle, the exact six states/no aliases, PENDING-only creation and two strict sinks. They exercise all four target categories, entity-version requirements, evidence-without-version, wrong references/raw values, immutable target scope, opaque method/judgment/confidence values, immutable original result and nested evidence, unfavorable COMPLETED results, retained results/provenance after INVALID/CONFLICTED/ARBITRATED projection, and all twelve state/result-presence combinations. Static examples verify overloaded target constructor restrictions and distinguish EvidenceRef from ArtifactRef, verdict from confidence, and EvaluationState from other entity states. Existing M2–M4 tests pass unchanged.

Import sorting and formatting were applied only to the nine new/modified Python files. First-pass mypy diagnostics concerned deliberate invalid-input examples and test narrowing; they were corrected with precise test annotations/assertions, and affected checks reran successfully. No production types or strictness settings were weakened.

Prior domain implementations, accepted specifications, Constitution, dependency declarations and lock file are unchanged. No unresolved architectural question, new verdict taxonomy, confidence scale, target category, lifecycle edge or scope deviation was introduced. M5A is complete as a bounded implementation; M5, authority enforcement, append-only record workflows and physical repository deletion protection are not complete.

## Commit and Remote Gate

Stage only the eleven explicit paths above; never use git add . or git add -A. Inspect `git diff --cached --name-status`, review the staged diff and run `git diff --cached --check`. Assert that the staged file list equals the whitelist and all staged contents match validated working files. After the single local commit, verify committed paths and content against that staged audit and report the exact hash outside the commit itself.

No push, PR/Issue mutation, remote ref changes or release publication is authorized or performed. Remote repository access is limited to reading the Issue. Stop after the validated local commit; human publication remains separate.
