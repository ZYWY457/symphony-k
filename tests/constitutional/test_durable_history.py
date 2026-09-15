"""Acceptance and remediation add history; failures cannot leave partial truth."""

import sqlite3
from dataclasses import replace
from pathlib import Path

import pytest

from symphony_k.domain import (
    ActorType,
    ConcurrencyConflict,
    Effect,
    EffectState,
    EntityVersion,
    Evaluation,
    EvaluationArbitrationRecord,
    EvaluationConflictSetRecord,
    EvaluationState,
    EventId,
    ImmutableRecordViolation,
    InvalidTransition,
    Objective,
    ObjectiveState,
)
from symphony_k.domain.effect_authorization import (
    EffectAuthorizationFindingRecord,
    EffectAuthorizationStatus,
)
from symphony_k.persistence.service import LifecycleService
from symphony_k.persistence.sqlite import SQLiteStore
from tests import test_effect_remediation_semantic_transitions as effect_fixtures
from tests import (
    test_evaluation_conflict_arbitration_semantic_transitions as eval_fixtures,
)
from tests.persistence_fixtures import data_rows, seed_snapshot
from tests.test_creation_integrated import creation_context
from tests.test_creation_objective_task import objective_request
from tests.test_creation_observed_effect import observed_request
from tests.test_persistence_evaluation import conflict_batch
from tests.test_persistence_service import objective_transition


def test_evaluation_original_record_survives_override_or_arbitration() -> None:
    store = SQLiteStore()
    original = eval_fixtures.evaluation(EvaluationState.COMPLETED)
    seed_snapshot(store, original)
    arbitration = eval_fixtures.arbitration(original)
    semantic = eval_fixtures.arbitration_semantics(original, record=arbitration)
    request = eval_fixtures.request(
        original, EvaluationState.ARBITRATED, eval_fixtures.ARBITRATOR
    )
    result = LifecycleService(store).transition(
        original.evaluation_id,
        request,
        eval_fixtures.context(original, request, semantic),
    )
    assert isinstance(result.entity, Evaluation)
    assert result.entity.result == original.result
    assert result.entity.state is EvaluationState.ARBITRATED
    assert store.load_version(original.evaluation_id, original.version) == original
    assert store.supporting_records(EvaluationArbitrationRecord) == (arbitration,)
    store.close()


def test_evaluation_conflict_history_is_not_rewritten() -> None:
    store = SQLiteStore()
    operations = conflict_batch(store)
    LifecycleService(store).transition_batch(operations)
    records = store.supporting_records(EvaluationConflictSetRecord)
    assert len(records) == 1
    assert all(
        store.load(item[0]).state is EvaluationState.CONFLICTED for item in operations
    )
    with pytest.raises(sqlite3.IntegrityError):
        store._connection.execute("DELETE FROM supporting_records")
    assert store.supporting_records(EvaluationConflictSetRecord) == records
    store.close()


def compensate(store: SQLiteStore) -> tuple[Effect, Effect]:
    committed = effect_fixtures.effect(EffectState.COMMITTED)
    seed_snapshot(store, committed)
    service = LifecycleService(store)
    start_request = effect_fixtures.request(committed, EffectState.COMPENSATING)
    start = service.transition(
        committed.effect_id,
        start_request,
        effect_fixtures.context(
            committed, start_request, effect_fixtures.start_semantics(committed)
        ),
    )
    assert isinstance(start.entity, Effect)
    plan = effect_fixtures.compensation_plan(committed)
    request = effect_fixtures.request(
        start.entity,
        EffectState.COMPENSATED,
        controller=effect_fixtures.COMPLETION_CONTROLLER,
        event_id=effect_fixtures.OTHER,
    )
    result = service.transition(
        committed.effect_id,
        request,
        effect_fixtures.context(
            start.entity,
            request,
            effect_fixtures.completion_semantics(start.entity, plan),
            start_event=start.event,
        ),
    )
    assert isinstance(result.entity, Effect)
    return committed, result.entity


def test_effect_compensation_preserves_commit_history() -> None:
    store = SQLiteStore()
    original, current = compensate(store)
    assert current.state is EffectState.COMPENSATED
    assert store.load_version(original.effect_id, original.version) == original
    assert [
        event.metadata.new_state
        for event in store.events.for_entity(original.effect_id)
    ] == [EffectState.COMMITTED, EffectState.COMPENSATING, EffectState.COMPENSATED]
    store.close()


def test_effect_rollback_is_distinct_from_compensation() -> None:
    rollback_store, compensation_store = SQLiteStore(), SQLiteStore()
    committed = effect_fixtures.effect(EffectState.COMMITTED)
    seed_snapshot(rollback_store, committed)
    request = effect_fixtures.request(committed, EffectState.ROLLED_BACK)
    rolled_back = LifecycleService(rollback_store).transition(
        committed.effect_id,
        request,
        effect_fixtures.context(
            committed, request, effect_fixtures.rollback_semantics(committed)
        ),
    )
    _, compensated = compensate(compensation_store)
    assert rolled_back.entity.state is EffectState.ROLLED_BACK
    assert compensated.state is EffectState.COMPENSATED
    for store in (rollback_store, compensation_store):
        assert store.load_version(committed.effect_id, committed.version) == committed
        store.close()


def test_confirmed_unauthorized_effect_remains_recordable() -> None:
    store = SQLiteStore()
    request = observed_request(status=EffectAuthorizationStatus.UNAUTHORIZED)
    result = LifecycleService(store).create(request, creation_context(request))
    assert result.entity.state is EffectState.COMMITTED
    findings = store.supporting_records(EffectAuthorizationFindingRecord)
    assert len(findings) == 1
    assert findings[0].status is EffectAuthorizationStatus.UNAUTHORIZED
    assert [
        event.metadata.new_state for event in store.events.for_entity(request.entity_id)
    ] == [EffectState.COMMITTED]
    store.close()


def test_human_governance_cannot_rewrite_historical_fact() -> None:
    store = SQLiteStore()
    creation = objective_request()
    service = LifecycleService(store)
    initial = service.create(creation, creation_context(creation))
    assert isinstance(initial.entity, Objective)
    request, context = objective_transition(initial.entity)
    human = replace(request.actor, actor_type=ActorType.HUMAN_OPERATOR)
    assert context.authority_decision is not None
    request = replace(request, actor=human)
    context = replace(
        context, authority_decision=replace(context.authority_decision, actor=human)
    )
    cancelled = service.transition(creation.entity_id, request, context)
    before = data_rows(store)
    forged = replace(
        request,
        event_id=EventId.new(),
        expected_version=cancelled.entity.version,
        target_state=ObjectiveState.DRAFT,
    )
    with pytest.raises(InvalidTransition):
        service.transition(creation.entity_id, forged, context)
    assert data_rows(store) == before
    assert store.load_version(creation.entity_id, EntityVersion(1)) == initial.entity
    assert store.events.load(initial.event.event_id) == initial.event
    store.close()


def test_stale_entity_version_is_rejected() -> None:
    store = SQLiteStore()
    creation = objective_request()
    service = LifecycleService(store)
    result = service.create(creation, creation_context(creation))
    assert isinstance(result.entity, Objective)
    request, context = objective_transition(result.entity)
    service.transition(creation.entity_id, request, context)
    before = data_rows(store)
    with pytest.raises(ConcurrencyConflict):
        service.transition(
            creation.entity_id, replace(request, event_id=EventId.new()), context
        )
    assert data_rows(store) == before
    store.close()


def test_concurrent_writers_cannot_silently_overwrite(tmp_path: Path) -> None:
    path = str(tmp_path / "constitutional.sqlite")
    a, b = SQLiteStore(path), SQLiteStore(path)
    assert a._connection is not b._connection
    creation = objective_request()
    LifecycleService(a).create(creation, creation_context(creation))
    original_a, original_b = (
        a.objectives.load(creation.entity_id),
        b.objectives.load(creation.entity_id),
    )
    assert original_a.version == original_b.version
    request_a, context_a = objective_transition(original_a)
    request_b, context_b = objective_transition(original_b)
    winner = LifecycleService(a).transition(creation.entity_id, request_a, context_a)
    with pytest.raises(ConcurrencyConflict):
        LifecycleService(b).transition(creation.entity_id, request_b, context_b)
    assert b.load(creation.entity_id) == winner.entity
    assert len(b.events.for_entity(creation.entity_id)) == 2
    a.close()
    b.close()


@pytest.mark.parametrize("table", ["events", "operations"])
def test_state_and_event_commit_atomically(table: str) -> None:
    store = SQLiteStore()
    creation = objective_request()
    before = data_rows(store)
    store._connection.execute(
        f"CREATE TRIGGER reject_write BEFORE INSERT ON {table} "
        "BEGIN SELECT RAISE(ABORT, 'constitutional failure probe'); END"
    )
    with pytest.raises(ImmutableRecordViolation):
        LifecycleService(store).create(creation, creation_context(creation))
    assert data_rows(store) == before
    store.close()


def test_event_history_is_append_only() -> None:
    store = SQLiteStore()
    request = objective_request()
    result = LifecycleService(store).create(request, creation_context(request))
    for sql in ("UPDATE events SET event=event", "DELETE FROM events"):
        with pytest.raises(sqlite3.IntegrityError):
            store._connection.execute(sql)
    assert store.events.load(result.event.event_id) == result.event
    store.close()


def test_creation_uniqueness_is_durable(tmp_path: Path) -> None:
    path = str(tmp_path / "uniqueness.sqlite")
    request = objective_request()
    store = SQLiteStore(path)
    LifecycleService(store).create(request, creation_context(request))
    store.close()
    store = SQLiteStore(path)
    changed = replace(request, event_id=EventId.new())
    with pytest.raises(ConcurrencyConflict):
        LifecycleService(store).create(changed, creation_context(changed))
    assert len(store.events.for_entity(request.entity_id)) == 1
    store.close()


def test_idempotent_replay_does_not_duplicate_history(tmp_path: Path) -> None:
    path = str(tmp_path / "replay.sqlite")
    request = objective_request()
    store = SQLiteStore(path)
    first = LifecycleService(store).create(request, creation_context(request))
    store.close()
    store = SQLiteStore(path)
    before = data_rows(store)
    assert LifecycleService(store).create(request, creation_context(request)) == first
    assert data_rows(store) == before
    store.close()
