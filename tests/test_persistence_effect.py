"""Observed occurrence deduplication and retained remediation records."""

from collections.abc import Callable
from dataclasses import fields, is_dataclass, replace
from typing import cast

import pytest

from symphony_k.domain import (
    ConcurrencyConflict,
    CreationRequest,
    Effect,
    EffectDeduplicationRef,
    EffectExternalOperationRef,
    EffectId,
    EffectState,
    EventId,
    create_entity,
)
from symphony_k.domain.effect_observation import EffectObservationRecord
from symphony_k.domain.effect_remediation import EffectCompensationCompletionRecord
from symphony_k.persistence.service import LifecycleService
from symphony_k.persistence.sqlite import SQLiteStore
from tests import test_effect_remediation_semantic_transitions as fixtures
from tests.persistence_fixtures import data_rows, seed_snapshot
from tests.test_creation_integrated import creation_context
from tests.test_creation_observed_effect import observed_request


def substitute(value: object, old: object, new: object) -> object:
    if type(value) is type(old) and value == old:
        return new
    if is_dataclass(value) and not isinstance(value, type):
        constructor = cast(Callable[..., object], type(value))
        return constructor(
            **{
                field.name: substitute(getattr(value, field.name), old, new)
                for field in fields(value)
            }
        )
    if isinstance(value, tuple):
        return tuple(substitute(item, old, new) for item in value)
    if isinstance(value, frozenset):
        return frozenset(substitute(item, old, new) for item in value)
    return value


@pytest.mark.parametrize("same", ["operation", "deduplication"])
def test_observed_occurrence_cannot_be_registered_under_another_effect(
    same: str,
) -> None:
    first = observed_request()
    changed = substitute(first, first.entity_id, EffectId.new())
    scope = first.semantic_input.registration
    assert scope is not None
    if same == "operation":
        changed = substitute(
            changed, scope.deduplication_ref, EffectDeduplicationRef("new dedup")
        )
    else:
        changed = substitute(
            changed,
            first.entity_spec.origin.external_operation_ref,
            EffectExternalOperationRef("new operation"),
        )
    second = replace(cast(CreationRequest, changed), event_id=EventId.new())
    # Both individually pass M7; only the durable M8 index rejects the duplicate.
    create_entity(second, creation_context(second))
    store = SQLiteStore()
    service = LifecycleService(store)
    service.create(first, creation_context(first))
    before = data_rows(store)
    with pytest.raises(ConcurrencyConflict):
        service.create(second, creation_context(second))
    assert data_rows(store) == before
    store.close()


def test_compensation_preserves_commit_event_and_original_observation() -> None:
    store = SQLiteStore()
    service = LifecycleService(store)
    committed = fixtures.effect(EffectState.COMMITTED)
    seed_snapshot(store, committed)
    original_events = store.events.for_entity(committed.effect_id)
    semantic = fixtures.start_semantics(committed)
    request = fixtures.request(committed, EffectState.COMPENSATING)
    started = service.transition(
        committed.effect_id, request, fixtures.context(committed, request, semantic)
    )
    assert isinstance(started.entity, Effect)
    plan = fixtures.compensation_plan(committed)
    completion = fixtures.completion_semantics(started.entity, plan)
    request = fixtures.request(
        started.entity,
        EffectState.COMPENSATED,
        controller=fixtures.COMPLETION_CONTROLLER,
        event_id=fixtures.OTHER,
    )
    finished = service.transition(
        committed.effect_id,
        request,
        fixtures.context(
            started.entity, request, completion, start_event=started.event
        ),
    )
    assert finished.entity.state is EffectState.COMPENSATED
    assert store.load_version(committed.effect_id, committed.version) == committed
    assert (
        store.events.for_entity(committed.effect_id)[: len(original_events)]
        == original_events
    )
    observations = store.supporting_records(EffectObservationRecord)
    assert observations == (fixtures.original_observation(committed),)
    records = store.supporting_records(EffectCompensationCompletionRecord)
    assert len(records) == 1 and records[0].residual_impact_summary
    store.close()
