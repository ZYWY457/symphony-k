"""Initial SQLite adapter. Public repositories read; lifecycle writes are internal."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from typing import cast

from symphony_k.domain import (
    ConcurrencyConflict,
    Effect,
    EffectId,
    EntityNotFound,
    EntityVersion,
    Evaluation,
    EvaluationId,
    EventId,
    ImmutableRecordViolation,
    InvalidDomainValue,
    InvalidRelationship,
    InvariantViolation,
    Objective,
    ObjectiveId,
    Outcome,
    OutcomeId,
    Run,
    RunId,
    Task,
    TaskId,
)
from symphony_k.domain.transition_engine import (
    DomainEvent,
    LifecycleEntity,
    LifecycleEntityId,
    TransitionResult,
)

from ._records import record_key, walk
from .codec import decode, encode
from .ports import (
    EffectRepository,
    EvaluationRepository,
    ObjectiveRepository,
    OutcomeRepository,
    RunRepository,
    TaskRepository,
)

_FAMILIES: dict[type, tuple[str, type[LifecycleEntity], str]] = {
    ObjectiveId: ("OBJECTIVE", Objective, "objective_id"),
    TaskId: ("TASK", Task, "task_id"),
    RunId: ("RUN", Run, "run_id"),
    OutcomeId: ("OUTCOME", Outcome, "outcome_id"),
    EvaluationId: ("EVALUATION", Evaluation, "evaluation_id"),
    EffectId: ("EFFECT", Effect, "effect_id"),
}


def entity_key(entity_id: LifecycleEntityId) -> tuple[str, str]:
    family = _FAMILIES.get(type(entity_id))
    if family is None:
        raise InvalidDomainValue("Expected a typed lifecycle entity ID")
    return family[0], str(entity_id.value)


def snapshot_id(entity: LifecycleEntity) -> LifecycleEntityId:
    for id_type, (_, entity_type, field) in _FAMILIES.items():
        if type(entity) is entity_type:
            value = getattr(entity, field)
            if type(value) is id_type:
                return cast(LifecycleEntityId, value)
    raise InvalidDomainValue("Expected a lifecycle snapshot")


_SCHEMA = """
CREATE TABLE IF NOT EXISTS heads (
    kind TEXT NOT NULL CHECK(kind IN
        ('OBJECTIVE','TASK','RUN','OUTCOME','EVALUATION','EFFECT')),
    entity_id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK(version >= 1),
    objective_kind TEXT NOT NULL DEFAULT 'OBJECTIVE' CHECK(objective_kind='OBJECTIVE'),
    primary_objective_id TEXT,
    task_kind TEXT NOT NULL DEFAULT 'TASK' CHECK(task_kind='TASK'),
    task_id TEXT,
    run_kind TEXT NOT NULL DEFAULT 'RUN' CHECK(run_kind='RUN'),
    run_id TEXT,
    PRIMARY KEY(kind,entity_id),
    CHECK(kind != 'TASK' OR primary_objective_id IS NOT NULL),
    CHECK(kind != 'RUN' OR task_id IS NOT NULL),
    CHECK(kind != 'OUTCOME' OR run_id IS NOT NULL),
    FOREIGN KEY(objective_kind,primary_objective_id) REFERENCES heads(kind,entity_id),
    FOREIGN KEY(task_kind,task_id) REFERENCES heads(kind,entity_id),
    FOREIGN KEY(run_kind,run_id) REFERENCES heads(kind,entity_id),
    FOREIGN KEY(kind,entity_id,version)
        REFERENCES entity_versions(kind,entity_id,version)
        DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS entity_versions (
    kind TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK(version >= 1),
    snapshot TEXT NOT NULL,
    event_id TEXT NOT NULL UNIQUE,
    PRIMARY KEY(kind,entity_id,version),
    FOREIGN KEY(kind,entity_id) REFERENCES heads(kind,entity_id)
        DEFERRABLE INITIALLY DEFERRED,
    FOREIGN KEY(event_id) REFERENCES events(event_id) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY NOT NULL,
    kind TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    event TEXT NOT NULL,
    UNIQUE(kind,entity_id,version),
    FOREIGN KEY(kind,entity_id,version)
        REFERENCES entity_versions(kind,entity_id,version)
        DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS operations (
    event_id TEXT PRIMARY KEY NOT NULL REFERENCES events(event_id),
    fingerprint TEXT NOT NULL,
    request TEXT NOT NULL,
    provenance TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS supporting_records (
    record_type TEXT NOT NULL,
    record_id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK(version >= 1),
    record TEXT NOT NULL,
    event_id TEXT NOT NULL REFERENCES events(event_id),
    PRIMARY KEY(record_type,record_id,version)
);
CREATE TABLE IF NOT EXISTS observed_occurrences (
    external_operation TEXT NOT NULL UNIQUE,
    deduplication TEXT NOT NULL UNIQUE,
    entity_id TEXT PRIMARY KEY NOT NULL,
    kind TEXT NOT NULL DEFAULT 'EFFECT' CHECK(kind='EFFECT'),
    FOREIGN KEY(kind,entity_id) REFERENCES heads(kind,entity_id)
        DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS evidence_records (
    evidence_ref TEXT PRIMARY KEY NOT NULL,
    record_fingerprint TEXT NOT NULL,
    record TEXT NOT NULL,
    UNIQUE(evidence_ref,record_fingerprint)
);
CREATE TABLE IF NOT EXISTS evidence_operations (
    operation_key TEXT PRIMARY KEY NOT NULL,
    operation_fingerprint TEXT NOT NULL,
    evidence_ref TEXT NOT NULL,
    record_fingerprint TEXT NOT NULL,
    claim TEXT NOT NULL,
    FOREIGN KEY(evidence_ref,record_fingerprint)
        REFERENCES evidence_records(evidence_ref,record_fingerprint)
);
CREATE TABLE IF NOT EXISTS evidence_trust_findings (
    finding_id TEXT PRIMARY KEY NOT NULL,
    evidence_ref TEXT NOT NULL,
    record_fingerprint TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN
        ('VERIFIED','ADVERSE','UNRESOLVED','INCOMPLETE')),
    supersedes_finding_id TEXT UNIQUE,
    record TEXT NOT NULL,
    FOREIGN KEY(evidence_ref,record_fingerprint)
        REFERENCES evidence_records(evidence_ref,record_fingerprint),
    FOREIGN KEY(supersedes_finding_id)
        REFERENCES evidence_trust_findings(finding_id)
);
CREATE TRIGGER IF NOT EXISTS heads_identity BEFORE UPDATE ON heads
WHEN NEW.kind != OLD.kind OR NEW.entity_id != OLD.entity_id
BEGIN SELECT RAISE(ABORT, 'immutable identity'); END;
CREATE TRIGGER IF NOT EXISTS heads_no_delete BEFORE DELETE ON heads
BEGIN SELECT RAISE(ABORT, 'immutable identity'); END;
"""


class SQLiteRepository[IdT: LifecycleEntityId, EntityT: LifecycleEntity]:
    def __init__(
        self,
        connection: sqlite3.Connection,
        id_type: type[IdT],
        entity_type: type[EntityT],
    ) -> None:
        self._connection = connection
        self._id_type = id_type
        self._entity_type = entity_type

    def load(self, entity_id: IdT) -> EntityT:
        if type(entity_id) is not self._id_type:
            raise InvalidDomainValue("Repository ID belongs to another entity family")
        row = self._connection.execute(
            "SELECT v.snapshot FROM heads h JOIN entity_versions v "
            "ON (v.kind,v.entity_id,v.version)=(h.kind,h.entity_id,h.version) "
            "WHERE h.kind=? AND h.entity_id=?",
            entity_key(entity_id),
        ).fetchone()
        return self._decode_row(row)

    def load_version(self, entity_id: IdT, version: EntityVersion) -> EntityT:
        if type(entity_id) is not self._id_type or not isinstance(
            version, EntityVersion
        ):
            raise InvalidDomainValue("Expected the repository's ID and EntityVersion")
        row = self._connection.execute(
            "SELECT snapshot FROM entity_versions "
            "WHERE kind=? AND entity_id=? AND version=?",
            (*entity_key(entity_id), version.value),
        ).fetchone()
        return self._decode_row(row)

    def _decode_row(self, row: tuple[str] | None) -> EntityT:
        if row is None:
            raise EntityNotFound("Entity snapshot is not recorded")
        value = decode(row[0])
        if not isinstance(value, self._entity_type):
            raise ValueError("Stored snapshot family mismatch")
        return value


class SQLiteEventRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def load(self, event_id: EventId) -> DomainEvent:
        if not isinstance(event_id, EventId):
            raise InvalidDomainValue("Expected EventId")
        row = self._connection.execute(
            "SELECT event FROM events WHERE event_id=?", (str(event_id),)
        ).fetchone()
        if row is None:
            raise EntityNotFound("Event is not recorded")
        return self._decode(row[0])

    def for_entity(self, entity_id: LifecycleEntityId) -> tuple[DomainEvent, ...]:
        rows = self._connection.execute(
            "SELECT event FROM events WHERE kind=? AND entity_id=? ORDER BY version",
            entity_key(entity_id),
        ).fetchall()
        return tuple(self._decode(row[0]) for row in rows)

    @staticmethod
    def _decode(text: str) -> DomainEvent:
        value = decode(text)
        if not isinstance(value, DomainEvent):
            raise ValueError("Stored value is not a DomainEvent")
        return value


class SQLiteStore:
    """Own one connection. Internal transaction access is reserved for the service."""

    def __init__(self, database: str = ":memory:") -> None:
        self._connection = sqlite3.connect(database, isolation_level=None, timeout=5)
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.executescript(_SCHEMA)
        for table in (
            "entity_versions",
            "events",
            "operations",
            "supporting_records",
            "observed_occurrences",
            "evidence_records",
            "evidence_operations",
            "evidence_trust_findings",
        ):
            for action in ("UPDATE", "DELETE"):
                self._connection.execute(
                    f"CREATE TRIGGER IF NOT EXISTS {table}_no_{action.lower()} "
                    f"BEFORE {action} ON {table} "
                    "BEGIN SELECT RAISE(ABORT, 'append-only history'); END"
                )
        self.objectives: ObjectiveRepository = SQLiteRepository(
            self._connection, ObjectiveId, Objective
        )
        self.tasks: TaskRepository = SQLiteRepository(self._connection, TaskId, Task)
        self.runs: RunRepository = SQLiteRepository(self._connection, RunId, Run)
        self.outcomes: OutcomeRepository = SQLiteRepository(
            self._connection, OutcomeId, Outcome
        )
        self.evaluations: EvaluationRepository = SQLiteRepository(
            self._connection, EvaluationId, Evaluation
        )
        self.effects: EffectRepository = SQLiteRepository(
            self._connection, EffectId, Effect
        )
        self.events = SQLiteEventRepository(self._connection)

    def close(self) -> None:
        self._connection.close()

    def load(self, entity_id: LifecycleEntityId) -> LifecycleEntity:
        family = _FAMILIES.get(type(entity_id))
        if family is None:
            raise InvalidDomainValue("Expected a lifecycle entity ID")
        return SQLiteRepository(self._connection, type(entity_id), family[1]).load(
            entity_id
        )

    def load_version(
        self, entity_id: LifecycleEntityId, version: EntityVersion
    ) -> LifecycleEntity:
        family = _FAMILIES.get(type(entity_id))
        if family is None:
            raise InvalidDomainValue("Expected a lifecycle entity ID")
        return SQLiteRepository(
            self._connection, type(entity_id), family[1]
        ).load_version(entity_id, version)

    @contextmanager
    def _transaction(self) -> Iterator[None]:
        if self._connection.in_transaction:
            raise RuntimeError("Nested authoritative transactions are forbidden")
        try:
            self._connection.execute("BEGIN IMMEDIATE")
            yield
            self._connection.execute("COMMIT")
        except BaseException as exc:
            if self._connection.in_transaction:
                self._connection.execute("ROLLBACK")
            if isinstance(exc, sqlite3.IntegrityError):
                if exc.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_FOREIGNKEY:
                    raise InvalidRelationship(
                        "Required durable relationship is absent"
                    ) from exc
                if exc.sqlite_errorcode in (
                    sqlite3.SQLITE_CONSTRAINT_PRIMARYKEY,
                    sqlite3.SQLITE_CONSTRAINT_UNIQUE,
                ):
                    raise ConcurrencyConflict(
                        "Durable identity already exists"
                    ) from exc
                if exc.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_TRIGGER:
                    raise ImmutableRecordViolation(
                        "Append-only record rejected mutation"
                    ) from exc
                if exc.sqlite_errorcode in (
                    sqlite3.SQLITE_CONSTRAINT_CHECK,
                    sqlite3.SQLITE_CONSTRAINT_NOTNULL,
                ):
                    raise InvariantViolation(
                        "Persistence structure rejected the operation"
                    ) from exc
            if isinstance(exc, sqlite3.OperationalError) and exc.sqlite_errorcode in (
                sqlite3.SQLITE_BUSY,
                sqlite3.SQLITE_LOCKED,
            ):
                raise ConcurrencyConflict(
                    "Concurrent writer holds the transaction"
                ) from exc
            raise

    def _append(
        self, result: TransitionResult[LifecycleEntity], expected: EntityVersion | None
    ) -> None:
        entity, event = result.entity, result.event
        key = entity_key(snapshot_id(entity))
        self._connection.execute(
            "INSERT INTO entity_versions VALUES (?,?,?,?,?)",
            (*key, entity.version.value, encode(entity), str(event.event_id)),
        )
        if expected is None:
            objective = (
                str(entity.primary_objective_id) if isinstance(entity, Task) else None
            )
            task = str(entity.task_id) if isinstance(entity, Run) else None
            run = str(entity.run_id) if isinstance(entity, Outcome) else None
            if isinstance(entity, Effect):
                task = str(entity.origin.task_id) if entity.origin.task_id else None
                run = str(entity.origin.run_id) if entity.origin.run_id else None
            self._connection.execute(
                "INSERT INTO heads(kind,entity_id,version,"
                "primary_objective_id,task_id,run_id) VALUES (?,?,?,?,?,?)",
                (*key, entity.version.value, objective, task, run),
            )
        else:
            cursor = self._connection.execute(
                "UPDATE heads SET version=? WHERE kind=? AND entity_id=? AND version=?",
                (entity.version.value, *key, expected.value),
            )
            if cursor.rowcount != 1:
                raise ConcurrencyConflict(
                    "Stored head no longer matches expected version"
                )
        self._connection.execute(
            "INSERT INTO events VALUES (?,?,?,?,?,?)",
            (
                str(event.event_id),
                *key,
                event.entity_version.value,
                event.event_type.value,
                encode(event),
            ),
        )

    def _record_operation(
        self, event_id: EventId, digest: str, request: object, provenance: object
    ) -> None:
        self._connection.execute(
            "INSERT INTO operations VALUES (?,?,?,?)",
            (str(event_id), digest, encode(request), encode(provenance)),
        )

    def _replay(
        self, event_id: EventId, digest: str
    ) -> TransitionResult[LifecycleEntity] | None:
        row = self._connection.execute(
            "SELECT fingerprint FROM operations WHERE event_id=?", (str(event_id),)
        ).fetchone()
        if row is None:
            return None
        if row[0] != digest:
            raise ConcurrencyConflict("EventId was already used for another request")
        event = self.events.load(event_id)
        return TransitionResult(
            self.load_version(event.entity_id, event.entity_version), event
        )

    def _reserve_occurrence(
        self, operation: str, deduplication: str, entity_id: str
    ) -> None:
        self._connection.execute(
            "INSERT INTO observed_occurrences"
            "(external_operation,deduplication,entity_id) VALUES (?,?,?)",
            (operation, deduplication, entity_id),
        )

    def _records(self, record_type: type) -> tuple[object, ...]:
        return tuple(
            decode(row[0])
            for row in self._connection.execute(
                "SELECT record FROM supporting_records "
                "WHERE record_type=? ORDER BY record_id,version",
                (record_type.__name__,),
            ).fetchall()
        )

    def _load_record(
        self, record_type: type, record_id: object, version: int = 1
    ) -> object:
        row = self._connection.execute(
            "SELECT record FROM supporting_records "
            "WHERE record_type=? AND record_id=? AND version=?",
            (record_type.__name__, str(record_id), version),
        ).fetchone()
        if row is None:
            raise ConcurrencyConflict("Required historical record is not durable")
        value = decode(row[0])
        if type(value) is not record_type or record_key(value) != (
            record_type.__name__,
            str(record_id),
            version,
        ):
            raise ConcurrencyConflict("Historical record type or identity differs")
        return value

    def _require_existing_record(
        self, value: object, event_id: EventId | None = None
    ) -> EventId:
        key = record_key(value)
        if key is None:
            raise InvariantViolation("Historical value is not a supporting record")
        row = self._connection.execute(
            "SELECT record,event_id FROM supporting_records "
            "WHERE record_type=? AND record_id=? AND version=?",
            key,
        ).fetchone()
        if row is None:
            raise ConcurrencyConflict("Required historical record is not durable")
        stored = decode(row[0])
        if type(stored) is not type(value) or record_key(stored) != key:
            raise ConcurrencyConflict("Historical record type or identity differs")
        if row[0] != encode(value):
            raise ConcurrencyConflict("Historical record content differs")
        recorded_event_id = EventId.from_string(row[1])
        if event_id is not None and recorded_event_id != event_id:
            raise ConcurrencyConflict("Historical record lineage differs")
        return recorded_event_id

    def _require_operation_provenance(self, event_id: EventId, value: object) -> None:
        row = self._connection.execute(
            "SELECT provenance FROM operations WHERE event_id=?", (str(event_id),)
        ).fetchone()
        if row is None:
            raise ConcurrencyConflict("Historical operation provenance is absent")
        provenance = decode(row[0])
        if not any(
            type(item) is type(value) and item == value for item in walk(provenance)
        ):
            raise ConcurrencyConflict("Historical operation provenance differs")

    def supporting_records[RecordT](
        self, record_type: type[RecordT]
    ) -> tuple[RecordT, ...]:
        values = self._records(record_type)
        if any(type(value) is not record_type for value in values):
            raise ValueError("Stored supporting record type mismatch")
        return cast(tuple[RecordT, ...], values)

    def _record_provenance(self, value: object, event_id: EventId) -> None:
        for item in walk(value):
            key = record_key(item)
            if key is None:
                continue
            encoded = encode(item)
            row = self._connection.execute(
                "SELECT record FROM supporting_records "
                "WHERE record_type=? AND record_id=? AND version=?",
                key,
            ).fetchone()
            if row is not None:
                if row[0] != encoded:
                    raise ImmutableRecordViolation(
                        "Supporting record identity cannot be rewritten"
                    )
                continue
            self._connection.execute(
                "INSERT INTO supporting_records VALUES (?,?,?,?,?)",
                (*key, encoded, str(event_id)),
            )

    @contextmanager
    def _evidence_read_snapshot(self) -> Iterator[None]:
        """Defer the read snapshot until the first SELECT; acquire no writer lock.

        The service owns chain/trust semantics and keeps every read inside this
        scope. Never borrow an existing transaction or commit caller-owned work.
        """
        if self._connection.in_transaction:
            raise ConcurrencyConflict("Evidence snapshot requires an idle connection")
        try:
            self._connection.execute("BEGIN")
            yield
        except sqlite3.OperationalError as exc:
            raise ConcurrencyConflict("Evidence snapshot could not be read") from exc
        finally:
            if self._connection.in_transaction:
                self._connection.execute("ROLLBACK")

    def _evidence_load_exact(self, evidence_ref: str, record_fingerprint: str) -> str:
        row = self._connection.execute(
            "SELECT record_fingerprint,record FROM evidence_records "
            "WHERE evidence_ref=?",
            (evidence_ref,),
        ).fetchone()
        if row is None:
            raise EntityNotFound("Evidence record is not recorded")
        if row[0] != record_fingerprint:
            raise ConcurrencyConflict("Evidence record fingerprint differs")
        return cast(str, row[1])

    def _evidence_load_identity(self, evidence_ref: str) -> tuple[str, str]:
        row = self._connection.execute(
            "SELECT record_fingerprint,record FROM evidence_records "
            "WHERE evidence_ref=?",
            (evidence_ref,),
        ).fetchone()
        if row is None:
            raise EntityNotFound("Evidence record is not recorded")
        return cast(tuple[str, str], row)

    def _evidence_findings(
        self, evidence_ref: str, record_fingerprint: str
    ) -> tuple[str, ...]:
        self._evidence_load_exact(evidence_ref, record_fingerprint)
        rows = self._connection.execute(
            "SELECT record FROM evidence_trust_findings "
            "WHERE evidence_ref=? AND record_fingerprint=? ORDER BY rowid",
            (evidence_ref, record_fingerprint),
        ).fetchall()
        return tuple(cast(str, row[0]) for row in rows)

    def _evidence_register(
        self,
        evidence_ref: str,
        record_fingerprint: str,
        record: str,
        operation_key: str,
        operation_fingerprint: str,
        claim: str,
        linked_records: tuple[tuple[str, str], ...],
    ) -> str:
        with self._transaction():
            operation = self._connection.execute(
                "SELECT operation_fingerprint,evidence_ref,record_fingerprint "
                "FROM evidence_operations WHERE operation_key=?",
                (operation_key,),
            ).fetchone()
            if operation is not None:
                if operation[0] != operation_fingerprint:
                    raise ConcurrencyConflict(
                        "Evidence operation key was already used differently"
                    )
                replay = self._evidence_load_exact(operation[1], operation[2])
                if replay != record:
                    raise ConcurrencyConflict("Evidence replay semantic record differs")
                return replay

            existing = self._connection.execute(
                "SELECT record_fingerprint,record FROM evidence_records "
                "WHERE evidence_ref=?",
                (evidence_ref,),
            ).fetchone()
            if existing is not None:
                if existing[0] != record_fingerprint or existing[1] != record:
                    raise ConcurrencyConflict(
                        "Evidence identity is bound to another immutable record"
                    )
            else:
                for linked_ref, linked_fingerprint in linked_records:
                    self._evidence_load_exact(linked_ref, linked_fingerprint)
                self._connection.execute(
                    "INSERT INTO evidence_records VALUES (?,?,?)",
                    (evidence_ref, record_fingerprint, record),
                )
            self._connection.execute(
                "INSERT INTO evidence_operations VALUES (?,?,?,?,?)",
                (
                    operation_key,
                    operation_fingerprint,
                    evidence_ref,
                    record_fingerprint,
                    claim,
                ),
            )
            return record

    def _evidence_append_finding(
        self,
        finding_id: str,
        evidence_ref: str,
        record_fingerprint: str,
        status: str,
        supersedes_finding_id: str | None,
        record: str,
    ) -> None:
        with self._transaction():
            self._evidence_load_exact(evidence_ref, record_fingerprint)
            if supersedes_finding_id is not None:
                row = self._connection.execute(
                    "SELECT evidence_ref,record_fingerprint "
                    "FROM evidence_trust_findings WHERE finding_id=?",
                    (supersedes_finding_id,),
                ).fetchone()
                if row is None:
                    raise InvalidRelationship(
                        "Superseded evidence finding is not recorded"
                    )
                if row != (
                    evidence_ref,
                    record_fingerprint,
                ):
                    raise InvalidRelationship(
                        "Finding supersession crosses evidence records"
                    )
            self._connection.execute(
                "INSERT INTO evidence_trust_findings VALUES (?,?,?,?,?,?)",
                (
                    finding_id,
                    evidence_ref,
                    record_fingerprint,
                    status,
                    supersedes_finding_id,
                    record,
                ),
            )
