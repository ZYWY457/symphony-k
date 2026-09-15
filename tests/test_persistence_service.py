"""Real atomic writes, immutable replay and independent SQLite connection races."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from threading import Barrier

import pytest

from symphony_k.domain import (
    ConcurrencyConflict,
    CreationRequest,
    EntityNotFound,
    EntityVersion,
    EventId,
    ImmutableRecordViolation,
    InvalidRelationship,
    InvariantViolation,
    Objective,
    ObjectiveArchivalDecision,
    ObjectiveArchivalSemantics,
    ObjectiveCancellationSemantics,
    ObjectiveState,
    ObjectiveTerminationDecision,
    TransitionContext,
    TransitionReason,
    TransitionRequest,
    transition_entity,
)
from symphony_k.domain.transition_engine import LifecycleEntity
from symphony_k.persistence.service import LifecycleService
from symphony_k.persistence.sqlite import SQLiteStore
from tests import test_objective_semantic_transitions as objective_fixtures
from tests.persistence_fixtures import advance_fixture, data_rows, seed_related
from tests.test_creation_integrated import CASES, creation_context
from tests.test_creation_objective_task import objective_request
from tests.test_creation_observed_effect import observed_request
from tests.test_creation_run_outcome_evaluation import outcome_request, run_request


def objective_transition(
    snapshot: Objective, target: ObjectiveState = ObjectiveState.CANCELLED
) -> tuple[TransitionRequest[ObjectiveState], TransitionContext]:
    request = replace(
        objective_fixtures.request(target),
        event_id=EventId.new(),
        expected_version=snapshot.version,
    )
    semantic: ObjectiveArchivalSemantics | ObjectiveCancellationSemantics
    if target is ObjectiveState.ARCHIVED:
        decision = replace(
            objective_fixtures.decision(ObjectiveArchivalDecision, "archive"),
            objective_id=snapshot.objective_id,
            observed_entity_version=snapshot.version,
        )
        semantic = ObjectiveArchivalSemantics(decision)
    else:
        termination = replace(
            objective_fixtures.decision(ObjectiveTerminationDecision, "cancel"),
            objective_id=snapshot.objective_id,
            observed_entity_version=snapshot.version,
        )
        semantic = ObjectiveCancellationSemantics(termination)
    return request, objective_fixtures.context(
        snapshot,
        request,
        objective_fixtures.canonical_guard(snapshot, target, semantic),
    )


@pytest.mark.parametrize("creation_request", CASES)
@pytest.mark.parametrize("file_backed", [False, True])
def test_all_six_entities_create_reload_and_replay(
    creation_request: CreationRequest, file_backed: bool, tmp_path: Path
) -> None:
    path = str(tmp_path / "create.sqlite") if file_backed else ":memory:"
    store = SQLiteStore(path)
    seed_related(store, creation_request)
    service = LifecycleService(store)
    result = service.create(creation_request, creation_context(creation_request))
    assert store.load(creation_request.entity_id) == result.entity
    assert result.entity.version == EntityVersion(1)
    assert store.events.for_entity(creation_request.entity_id) == (result.event,)
    before = data_rows(store)
    assert (
        service.create(creation_request, creation_context(creation_request)) == result
    )
    assert data_rows(store) == before
    store.close()
    if file_backed:
        store = SQLiteStore(path)
        assert store.load(creation_request.entity_id) == result.entity
        assert store.events.load(result.event.event_id) == result.event
        store.close()


def test_transition_history_and_replay_after_head_advances() -> None:
    store = SQLiteStore()
    service = LifecycleService(store)
    creation = objective_request()
    first = service.create(creation, creation_context(creation))
    assert isinstance(first.entity, Objective)
    request, context = objective_transition(first.entity)
    second = service.transition(creation.entity_id, request, context)
    assert isinstance(second.entity, Objective)
    third_request, third_context = objective_transition(
        second.entity, ObjectiveState.ARCHIVED
    )
    third = service.transition(creation.entity_id, third_request, third_context)
    before = data_rows(store)
    assert service.transition(creation.entity_id, request, context) == second
    assert service.create(creation, creation_context(creation)) == first
    assert store.load(creation.entity_id) == third.entity
    assert [
        item.entity_version.value
        for item in store.events.for_entity(creation.entity_id)
    ] == [1, 2, 3]
    assert data_rows(store) == before
    changed = replace(request, reason=TransitionReason("conflicting replay"))
    with pytest.raises(ConcurrencyConflict):
        service.transition(creation.entity_id, changed, context)
    assert data_rows(store) == before
    store.close()


def test_two_connections_reject_a_stale_writer(tmp_path: Path) -> None:
    path = str(tmp_path / "concurrent.sqlite")
    a, b = SQLiteStore(path), SQLiteStore(path)
    assert a._connection is not b._connection
    creation = objective_request()
    LifecycleService(a).create(creation, creation_context(creation))
    left, right = (
        a.objectives.load(creation.entity_id),
        b.objectives.load(creation.entity_id),
    )
    assert left.version == right.version == EntityVersion(1)
    request_a, context_a = objective_transition(left)
    request_b, context_b = objective_transition(right)
    winner = LifecycleService(a).transition(creation.entity_id, request_a, context_a)
    before = data_rows(a)
    with pytest.raises(ConcurrencyConflict):
        LifecycleService(b).transition(creation.entity_id, request_b, context_b)
    assert a.load(creation.entity_id) == winner.entity
    assert data_rows(b) == before
    with pytest.raises(EntityNotFound):
        b.events.load(request_b.event_id)
    a.close()
    b.close()


def test_simultaneous_duplicate_creation_has_exactly_one_winner(tmp_path: Path) -> None:
    path = str(tmp_path / "duplicate.sqlite")
    SQLiteStore(path).close()
    barrier = Barrier(2)
    base = objective_request()

    def writer() -> str:
        store = SQLiteStore(path)
        request = replace(base, event_id=EventId.new())
        with pytest.raises(EntityNotFound):
            store.load(request.entity_id)
        barrier.wait(timeout=10)
        try:
            LifecycleService(store).create(request, creation_context(request))
            return "created"
        except ConcurrencyConflict:
            return "conflict"
        finally:
            store.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(writer) for _ in range(2)]
        assert sorted(future.result(timeout=15) for future in futures) == [
            "conflict",
            "created",
        ]
    store = SQLiteStore(path)
    assert len(store.events.for_entity(base.entity_id)) == 1
    assert store.load(base.entity_id).version == EntityVersion(1)
    store.close()


@pytest.mark.parametrize(
    "creation_request",
    CASES[1:]
    + (
        run_request(True),
        outcome_request(True),
        observed_request(linked=True),
        observed_request(True, True),
    ),
)
def test_every_supplied_related_snapshot_is_checked(
    creation_request: CreationRequest,
) -> None:
    probe = SQLiteStore()
    identities = seed_related(probe, creation_request)
    probe.close()
    for identity in identities:
        store = SQLiteStore()
        seed_related(store, creation_request)
        advance_fixture(store, identity)
        before = data_rows(store)
        with pytest.raises(ConcurrencyConflict):
            LifecycleService(store).create(
                creation_request, creation_context(creation_request)
            )
        assert data_rows(store) == before
        store.close()


@pytest.mark.parametrize("table", ["entity_versions", "events", "operations"])
@pytest.mark.parametrize("creation", [False, True])
def test_injected_failure_rolls_back_every_write(table: str, creation: bool) -> None:
    store = SQLiteStore()
    service = LifecycleService(store)
    request = objective_request()
    source: LifecycleEntity | None = None
    if not creation:
        source = service.create(request, creation_context(request)).entity
    before = data_rows(store)
    store._connection.execute(
        f"CREATE TRIGGER fail_insert BEFORE INSERT ON {table} "
        "BEGIN SELECT RAISE(ABORT, 'injected failure'); END"
    )
    with pytest.raises(ImmutableRecordViolation):
        if creation:
            service.create(request, creation_context(request))
        else:
            assert isinstance(source, Objective)
            transition, context = objective_transition(source)
            service.transition(request.entity_id, transition, context)
    assert data_rows(store) == before
    store.close()


def test_foreign_key_failure_rolls_back_pending_history_and_head() -> None:
    store = SQLiteStore()
    request = objective_request()
    before = data_rows(store)
    store._connection.execute(
        "CREATE TRIGGER fail_fk BEFORE INSERT ON events BEGIN "
        "INSERT INTO heads(kind,entity_id,version,task_id) "
        "VALUES ('RUN','injected',1,'missing'); END"
    )
    with pytest.raises(InvalidRelationship):
        LifecycleService(store).create(request, creation_context(request))
    assert data_rows(store) == before
    store.close()


def test_domain_rejection_has_no_database_mutation() -> None:
    store = SQLiteStore()
    creation = objective_request()
    source = LifecycleService(store).create(creation, creation_context(creation)).entity
    assert isinstance(source, Objective)
    request, context = objective_transition(source)
    before = data_rows(store)
    context = replace(context, guards=(objective_fixtures.RejectingGuard(),))
    with pytest.raises(InvariantViolation):
        LifecycleService(store).transition(creation.entity_id, request, context)
    assert data_rows(store) == before
    store.close()


@pytest.mark.parametrize("table", ["events", "operations"])
def test_failure_occurs_after_intermediate_writes_are_visible(table: str) -> None:
    store = SQLiteStore()
    service = LifecycleService(store)
    creation = objective_request()
    first = service.create(creation, creation_context(creation))
    assert isinstance(first.entity, Objective)
    request, context = objective_transition(first.entity)
    observed: list[tuple[int, int]] = []

    def observe_pending() -> int:
        head = store.load(creation.entity_id)
        events = store.events.for_entity(creation.entity_id)
        observed.append((head.version.value, len(events)))
        return 0

    store._connection.create_function("observe_pending", 0, observe_pending)
    store._connection.execute(
        f"CREATE TRIGGER fail_after_probe BEFORE INSERT ON {table} "
        "BEGIN SELECT observe_pending(); "
        "SELECT RAISE(ABORT, 'injected after observation'); END"
    )
    before = data_rows(store)
    with pytest.raises(ImmutableRecordViolation):
        service.transition(creation.entity_id, request, context)
    assert observed == [(2, 1 if table == "events" else 2)]
    assert data_rows(store) == before
    store.close()


def test_creation_conflicting_event_identity_and_duplicate_entity_are_typed() -> None:
    store = SQLiteStore()
    service = LifecycleService(store)
    request = objective_request()
    service.create(request, creation_context(request))
    before = data_rows(store)
    for changed in (
        replace(request, reason=TransitionReason("changed request")),
        replace(request, event_id=EventId.new()),
    ):
        with pytest.raises(ConcurrencyConflict):
            service.create(changed, creation_context(changed))
        assert data_rows(store) == before
    store.close()


def test_compare_and_swap_zero_rows_rolls_back_the_appended_version() -> None:
    store = SQLiteStore()
    creation = objective_request()
    first = LifecycleService(store).create(creation, creation_context(creation))
    assert isinstance(first.entity, Objective)
    request, context = objective_transition(first.entity)
    result = transition_entity(first.entity, request, context)
    before = data_rows(store)
    with pytest.raises(ConcurrencyConflict, match="head no longer matches"):
        with store._transaction():
            store._append(result, EntityVersion(0))
    assert data_rows(store) == before
    store.close()
