# Stage 1 M8 - Persistence and Atomicity

**Version:** 1
**Status:** M8 implementation candidate; independent Human Review required
**TaskSpec reference:** https://github.com/ZYWY457/symphony-k/issues/72
**TaskSpec access mode:** materialized-handoff
**TaskSpec precondition:** PASS
**Phase 0 parent:** `e59c61c54a27f3a4751fc5102c44ca0aa5379895`

## Plan and acceptance

1. M8A: database-neutral read repositories and atomic lifecycle port; ADR-0007;
   deterministic closed-schema JSON and full request fingerprints. Round-trip
   all eight creation variants, snapshots and events.
2. M8B: stdlib SQLite schema, read adapters, heads and immutable versions/events,
   operation ledger and structural foreign keys. Test memory and file storage.
3. M8C: authoritative create/transition transactions, currentness, CAS, replay,
   error translation, rollback injections and two-connection race proofs.

The accepted Evaluation conflict family requires complete atomic participant
updates and durable supporting history; a single-entity implementation alone
cannot establish M8 completion. Reuse existing semantic records and guards,
without changing authority, topology or effective-use meaning.

Each production phase requires focused and full pytest, Ruff, format, mypy,
locked sync and diff checks before its explicit-path local commit. No amendments,
squash or remote publication. Repository-local ignored `.uv-cache` is the
approved disposable-cache fallback; lock/dependency inputs remain unchanged.

## Boundaries

Six roots, 43 states, 99 edges. No domain import of persistence/SQLite; no Agent,
Docker, network dispatch, Effect execution, credentials, ORM, migration framework
or later-stage runtime. M7 remains Human Accepted; M8/M9 remain candidates and
Stage 1 remains incomplete.

## M8A validation

Focused codec suite: 23 passed, including eight full semantic requests,
eight snapshots and eight creation events. Full suite: 3168 passed. Locked
sync, Ruff, format (194 files), mypy (108 source files) and diff checks passed.
Initial new-test collection and codec typing errors were corrected before these
successful runs. No accepted domain source or dependency input changed.

## M8B validation

Focused SQLite suite: 12 passed; full suite: 3180 passed. Locked sync, Ruff,
format (196 files), mypy (110 source files) and diff checks passed. Tests cover
memory/file databases, reopening durable snapshots/events, three parent foreign
keys, and direct UPDATE/DELETE attacks on history, events and operation receipts.
The public repositories expose reads only. Adapter mutation helpers are internal;
the authorized service is implemented in M8C.

The first focused run completed its test bodies but pytest cleanup failed on the
default temporary directory's `pytest-current` link. It was not counted as a
passing run. Successful focused/full reruns used explicit disposable directories
under ignored `.uv-cache/` via `--basetemp`, without weakening any tests.
