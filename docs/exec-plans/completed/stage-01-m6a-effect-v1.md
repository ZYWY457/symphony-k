# Stage 1 M6A — Effect Core Model and Lifecycle Topology

**Version:** 1
**Status:** Implementation and required validation completed, 2026-09-08
**Scope:** [Implementation #6A / GitHub Issue #13](https://github.com/ZYWY457/symphony-k/issues/13), under the accepted Stage 1 Exec Plan, ADR-0005, and Effect state-machine design.

## Boundary Review

The accepted repository hierarchy and Issue are consistent. M6A is a bounded implementation of the existing sixth core entity and requires neither an ADR nor a dependency change.

In scope: immutable Effect snapshots, exactly eight Effect states, typed target/payload/external-operation references, immutable planned and observed creation provenance, three creation destinations, and the exact nineteen state-to-state structural edges.

Out of scope: occurrence, authorization, governance, incident, attribution, preparation, reconciliation, rollback, and compensation records or execution; authoritative transition guards; events; repositories; persistence; and all external mutation.

## Bounded Steps and Acceptance

1. Add the Effect value objects, origins, snapshot, and structural topology. Accept when malformed inputs are rejected, unknown observed attribution/payload remain representable, origin is immutable, and topology matches the accepted design exactly.
2. Export the M6A public API and add deterministic runtime/static tests. Accept when all 64 state pairs, all three creation destinations, provenance rules, type separation, strict sinks, and absence of mutation/execution APIs are covered.
3. Run every Issue validation command and inspect the complete explicitly staged diff. Accept when all gates pass without dependency/configuration changes or M6B+ behavior, then create exactly one local commit.

## Representation Decisions

`Effect` is a frozen, slotted snapshot with explicitly supplied `EffectId`, `EffectState`, `EntityVersion`, creation `origin`, `EffectTargetRef`, and optional `EffectPayloadRef`. It has no lifecycle mutation method. A planned origin requires a typed TaskId, optional RunId, ActorIdentity proposer, and a present payload reference. An observed origin requires external-operation identity, at least one immutable typed EvidenceRef, observer identity, Timestamp, and either known Task attribution or an explicit meaningful unlinked reason. A Run cannot be attributed without a Task. Actor identities remain provenance and confer no authority.

The three reference classes are distinct frozen runtime/static types containing preserved non-whitespace text. They select no URL, hash, storage, adapter, or authorization-token semantics and load no content. Unknown observed payload remains `None` rather than being fabricated.

Creation-origin objects and the Effect snapshot are immutable. Later associations cannot edit observed creation history through this API. `EFFECT_CREATION_STATES` is an immutable set containing exactly PLANNED, COMMITTED, and QUARANTINED; NONE is not an EffectState. The private topology contains exactly the accepted nineteen state pairs. Its public query performs only typed structural membership.

COMMITTED is documented solely as confirmed external occurrence regardless of authorization. QUARANTINED is documented as controlled reconciliation rather than occurrence, incident, or authorization truth. ROLLED_BACK and COMPENSATED are separate strict sinks; compensation requires the COMPENSATING path and never implies rollback or erasure of the original occurrence.

## Validation Evidence

Python 3.12.7 with the existing locked pytest 9.1.1, Ruff 0.16.6, and mypy 1.20.2. No dependency, lock-file, or tool-configuration change was made.

| Command | Final result |
| --- | --- |
| `uv --cache-dir .uv-cache sync --dev --locked` | Exit 0; resolved and checked 13 packages |
| `uv --cache-dir .uv-cache run pytest -p no:cacheprovider` | Exit 0; 1442 passed, no warnings |
| `uv --cache-dir .uv-cache run ruff check .` | Exit 0; all checks passed |
| `uv --cache-dir .uv-cache run ruff format --check .` | Exit 0; 87 files already formatted |
| `uv --cache-dir .uv-cache run mypy src tests` | Exit 0; no issues in 52 source files |
| `git diff --check` | Exit 0; only Git's existing LF-to-CRLF working-copy notices |

The repository-local ignored uv cache was required because the sandbox denied access to the default user cache. Pytest's cache provider was disabled in the final equivalent run because the sandbox also denied `.pytest_cache` writes; an earlier full run with the provider enabled passed all tests with only that cache-write warning. Neither adjustment changes dependency resolution or test semantics.

Tests independently enumerate all 64 state pairs and exactly nineteen accepted edges, plus the three creation destinations for 22 total topology edges including creation. They cover immutable and typed provenance, linked/unlinked observations, nonempty observation evidence, unknown observed payload, all ActorType values as non-authoritative provenance, and absence of mutation/execution/status/parent-propagation APIs. Static negative examples keep all Effect IDs/references distinct under strict mypy.

No external action occurred. No occurrence/governance/authorization/incident/reconciliation/remediation record, Transition Engine, event, repository, persistence, or M6B+ behavior was introduced. Repository and GitHub Issue #13 supplied sufficient cold-start context; no previous conversation history or other authority was required.
