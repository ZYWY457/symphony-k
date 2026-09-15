# ADR-0007: Stage 1 SQLite Persistence and Atomicity

## Status

Implementation decision authorized by GitHub Issue #72; implementation candidate
requires independent Human Review.

## Context

M7 validates supplied immutable domain inputs. M8 must establish durable
currentness, identity uniqueness, history and atomic state/event persistence.

## Decision

SQLite is the initial adapter, not the domain abstraction. Repository/UoW ports
remain database-neutral. Python stdlib `sqlite3` avoids unnecessary Stage 1
runtime dependencies. A future adapter may supersede SQLite without changing
domain semantics. No ORM, migration framework or external service is introduced.

Read repositories expose current and exact historical snapshots and events.
Only the lifecycle service may orchestrate authoritative writes. It invokes the
accepted domain engine within a write transaction; SQL enforces structural
constraints rather than lifecycle authority rules. Entity heads advance by
compare-and-swap; versions, events and operation receipts are append-only.
EventId identifies an operation and canonical request encoding identifies its
content. A replay returns its original historical result.

Creation checks identifier absence and supplied relationship currentness inside
the transaction. Foreign keys protect Task/Objective, Run/Task and Outcome/Run.
Deterministic JSON uses a closed type registry, explicit tags and canonical sets;
decoding never imports a payload-selected module or executes payload code.

## Consequences and required closure

SQLite serializes writers; optimistic expected-version checks still reject stale
clients. File-backed tests must exercise independent connections. A future
adapter must pass the same transaction, replay and immutable-history contracts.
Domain imports remain persistence-independent; persistence dispatches no Effects.

Evaluation conflict/arbitration operations must also obey ADR-0005: correlated
membership, all affected projections and per-member events form one atomic
boundary. The single-entity operation is not sufficient for that family.
Supporting provenance records remain records under the six roots, not additional
domain entities. Their authoritative history cannot be replaced with event
reference strings alone.
