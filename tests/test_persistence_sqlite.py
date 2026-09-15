"""Adapter structural tests; private seeding is not a production import API."""

import sqlite3
from pathlib import Path

import pytest

from symphony_k.domain import EntityNotFound, EventId, Objective, create_entity
from symphony_k.domain.transition_engine import TransitionResult
from symphony_k.persistence.sqlite import SQLiteStore
from tests.test_creation_integrated import creation_context
from tests.test_creation_objective_task import objective_request


def seed_objective(store: SQLiteStore) -> TransitionResult[Objective]:
    request = objective_request()
    result = create_entity(request, creation_context(request))
    durable = TransitionResult(result.entity, result.event)
    with store._transaction():
        store._append(durable, None)
        store._record_operation(request.event_id, "seed", request, ())
    return durable


@pytest.mark.parametrize("file_backed", [False, True])
def test_current_history_events_and_reopen(tmp_path: Path, file_backed: bool) -> None:
    path = str(tmp_path / "store.sqlite") if file_backed else ":memory:"
    store = SQLiteStore(path)
    result = seed_objective(store)
    assert store.objectives.load(result.entity.objective_id) == result.entity
    assert (
        store.load_version(result.event.entity_id, result.entity.version)
        == result.entity
    )
    assert store.events.load(result.event.event_id) == result.event
    assert store.events.for_entity(result.event.entity_id) == (result.event,)
    store.close()
    if file_backed:
        reopened = SQLiteStore(path)
        assert reopened.load(result.event.entity_id) == result.entity
        assert reopened.events.load(result.event.event_id) == result.event
        reopened.close()


@pytest.mark.parametrize("table", ["entity_versions", "events", "operations"])
@pytest.mark.parametrize("action", ["UPDATE", "DELETE"])
def test_raw_history_mutation_is_rejected(table: str, action: str) -> None:
    store = SQLiteStore()
    result = seed_objective(store)
    column = "snapshot" if table == "entity_versions" else "event_id"
    sql = (
        f"UPDATE {table} SET {column}={column}"
        if action == "UPDATE"
        else f"DELETE FROM {table}"
    )
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        store._connection.execute(sql)
    assert store.events.load(result.event.event_id) == result.event
    store.close()


@pytest.mark.parametrize(
    ("kind", "column"),
    [("TASK", "primary_objective_id"), ("RUN", "task_id"), ("OUTCOME", "run_id")],
)
def test_required_parent_foreign_keys(kind: str, column: str) -> None:
    store = SQLiteStore()
    assert store._connection.execute("PRAGMA foreign_keys").fetchone() == (1,)
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        store._connection.execute(
            f"INSERT INTO heads(kind,entity_id,version,{column}) VALUES (?,?,1,?)",
            (kind, "child", "missing"),
        )
    assert store._connection.execute("SELECT count(*) FROM heads").fetchone() == (0,)
    store.close()


def test_unknown_entity_and_event_are_typed() -> None:
    store = SQLiteStore()
    with pytest.raises(EntityNotFound):
        store.load(objective_request().entity_id)
    with pytest.raises(EntityNotFound):
        store.events.load(EventId.new())
    store.close()
