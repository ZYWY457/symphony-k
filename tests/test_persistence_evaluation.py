"""Correlated Evaluation state/history commits preserve all participants."""

from dataclasses import replace

import pytest

from symphony_k.domain import (
    ConcurrencyConflict,
    EntityVersion,
    Evaluation,
    EvaluationArbitrationRecord,
    EvaluationArbitrationSemantics,
    EvaluationConflictParticipantObservation,
    EvaluationConflictSetRecord,
    EvaluationId,
    EvaluationInvalidationId,
    EvaluationInvalidationRecord,
    EvaluationInvalidationSemantics,
    EvaluationSemanticGuard,
    EvaluationState,
    EventId,
    ImmutableRecordViolation,
    InvariantViolation,
)
from symphony_k.persistence.service import LifecycleService, TransitionOperation
from symphony_k.persistence.sqlite import SQLiteStore
from tests import test_evaluation_conflict_arbitration_semantic_transitions as fixtures
from tests.persistence_fixtures import data_rows, seed_snapshot


def conflict_batch(store: SQLiteStore) -> tuple[TransitionOperation, ...]:
    left = fixtures.evaluation(EvaluationState.COMPLETED)
    right = replace(
        left,
        evaluation_id=EvaluationId(fixtures.OTHER),
        version=EntityVersion(4),
        target=fixtures.OTHER_TARGET,
    )
    seed_snapshot(store, left)
    seed_snapshot(store, right)
    semantic = fixtures.conflict_semantics(left)
    operations = []
    for current in (left, right):
        request = replace(
            fixtures.request(current, EvaluationState.CONFLICTED, fixtures.EVALUATOR),
            event_id=EventId.new(),
        )
        operations.append(
            (
                current.evaluation_id,
                request,
                fixtures.context(current, request, semantic),
            )
        )
    return tuple(operations)


def test_conflict_batch_is_atomic_and_original_content_survives_arbitration() -> None:
    store = SQLiteStore()
    service = LifecycleService(store)
    operations = conflict_batch(store)
    originals = tuple(store.load(operation[0]) for operation in operations)
    before = data_rows(store)
    with pytest.raises(InvariantViolation, match="all affected participants"):
        service.transition_batch(operations[:1])
    assert data_rows(store) == before
    results = service.transition_batch(operations)
    left, right = (result.entity for result in results)
    assert isinstance(left, Evaluation) and isinstance(right, Evaluation)
    records = store.supporting_records(EvaluationConflictSetRecord)
    assert len(records) == 1
    conflict = records[0]
    arbitration = replace(
        fixtures.arbitration(left, conflict=conflict),
        decisions=frozenset({fixtures.decision(left), fixtures.decision(right)}),
    )
    semantic = EvaluationArbitrationSemantics(
        arbitration, frozenset({conflict}), frozenset({arbitration}), frozenset()
    )
    batch = []
    for current in (left, right):
        request = replace(
            fixtures.request(current, EvaluationState.ARBITRATED, fixtures.ARBITRATOR),
            event_id=EventId.new(),
        )
        batch.append(
            (
                current.evaluation_id,
                request,
                fixtures.context(current, request, semantic),
            )
        )
    service.transition_batch(tuple(batch))
    for original in originals:
        assert isinstance(original, Evaluation)
        current = store.evaluations.load(original.evaluation_id)
        assert current.state is EvaluationState.ARBITRATED
        assert current.result == original.result
        assert (
            store.evaluations.load_version(original.evaluation_id, original.version)
            == original
        )
    assert store.supporting_records(EvaluationConflictSetRecord) == (conflict,)
    assert store.supporting_records(EvaluationArbitrationRecord) == (arbitration,)
    store.close()


def test_failed_second_member_rolls_back_first_member_and_supporting_history() -> None:
    store = SQLiteStore()
    operations = conflict_batch(store)
    before = data_rows(store)
    second_id = str(operations[1][1].event_id)
    store._connection.execute(
        "CREATE TRIGGER fail_second BEFORE INSERT ON events "
        f"WHEN NEW.event_id='{second_id}' "
        "BEGIN SELECT RAISE(ABORT, 'injected second member failure'); END"
    )
    with pytest.raises(ImmutableRecordViolation):
        LifecycleService(store).transition_batch(operations)
    assert data_rows(store) == before
    store.close()


def test_stale_member_rejects_entire_batch() -> None:
    store = SQLiteStore()
    operations = conflict_batch(store)
    LifecycleService(store).transition_batch(operations)
    changed = tuple(
        (identity, replace(request, event_id=EventId.new()), context)
        for identity, request, context in operations
    )
    before = data_rows(store)
    with pytest.raises(ConcurrencyConflict):
        LifecycleService(store).transition_batch(changed)
    assert data_rows(store) == before
    store.close()


def test_historical_supporting_identity_cannot_be_rewritten() -> None:
    store = SQLiteStore()
    operations = conflict_batch(store)
    LifecycleService(store).transition_batch(operations)
    record = store.supporting_records(EvaluationConflictSetRecord)[0]
    changed = replace(record, disagreement_summary="rewritten fact")
    with pytest.raises(ImmutableRecordViolation):
        with store._transaction():
            store._record_provenance(changed, operations[0][1].event_id)
    assert store.supporting_records(EvaluationConflictSetRecord) == (record,)
    store.close()


def test_conflict_membership_cannot_use_a_peer_changed_in_the_same_batch() -> None:
    store = SQLiteStore()
    left = fixtures.evaluation(EvaluationState.COMPLETED)
    right = replace(
        left,
        evaluation_id=EvaluationId(fixtures.OTHER),
        state=EvaluationState.CONFLICTED,
        version=EntityVersion(4),
    )
    seed_snapshot(store, left)
    seed_snapshot(store, right)
    observations = frozenset(
        EvaluationConflictParticipantObservation(
            item.evaluation_id, item.version, item.state, item.target
        )
        for item in (left, right)
    )
    semantic = fixtures.conflict_semantics(
        left, observations=observations, intended=frozenset({left.evaluation_id})
    )
    left_request = replace(
        fixtures.request(left, EvaluationState.CONFLICTED, fixtures.EVALUATOR),
        event_id=EventId.new(),
    )
    left_context = fixtures.context(left, left_request, semantic)
    right_request = replace(
        fixtures.request(right, EvaluationState.INVALID, fixtures.EVALUATOR),
        event_id=EventId.new(),
    )
    invalidation = EvaluationInvalidationRecord(
        EvaluationInvalidationId.new(),
        right.evaluation_id,
        right.version,
        "New independent invalidation",
        left.result.evidence_refs if left.result else frozenset(),
        fixtures.EVALUATOR,
        fixtures.NOW,
        fixtures.CORRELATION,
    )
    assert left_context.authority_decision is not None
    right_context = replace(
        left_context,
        authority_decision=replace(
            left_context.authority_decision,
            entity_id=right.evaluation_id,
            observed_entity_version=right.version,
            prior_state=right.state,
            target_state=EvaluationState.INVALID,
        ),
        evaluation_semantic_guard=EvaluationSemanticGuard(
            right.evaluation_id,
            right.version,
            right.state,
            EvaluationState.INVALID,
            fixtures.CORRELATION,
            EvaluationInvalidationSemantics(invalidation),
        ),
    )
    before = data_rows(store)
    with pytest.raises(InvariantViolation, match="already-conflicted member"):
        LifecycleService(store).transition_batch(
            (
                (left.evaluation_id, left_request, left_context),
                (right.evaluation_id, right_request, right_context),
            )
        )
    assert data_rows(store) == before
    store.close()
