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
    InvalidDomainValue,
    InvalidRelationship,
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
        for table in ("entity_versions", "events", "operations"):
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
