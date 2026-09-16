"""Observed occurrence deduplication and retained remediation records."""

from collections.abc import Callable
from dataclasses import fields, is_dataclass, replace
from typing import cast

import pytest

from symphony_k.domain import (
    ActorType,
    ConcurrencyConflict,
    CreationRequest,
    DomainEvent,
    Effect,
    EffectCompensationCompletionSemantics,
    EffectCompensationPlanId,
    EffectDeduplicationRef,
    EffectExternalOperationRef,
    EffectId,
    EffectObservationId,
    EffectOccurrenceStatus,
    EffectQuarantineCompensationCompletionSemantics,
    EffectQuarantineContextId,
    EffectQuarantineReason,
    EffectSimulationRecord,
    EffectSimulationRecordId,
    EffectSimulationSemantics,
    EffectState,
    EventId,
    EvidenceRef,
    InvariantViolation,
    TransitionReason,
    create_entity,
)
from symphony_k.domain.effect_observation import EffectObservationRecord
from symphony_k.domain.effect_remediation import (
    EffectCompensationCompletionRecord,
    EffectCompensationPlanRecord,
)
from symphony_k.domain.effect_semantics import (
    EffectQuarantineSemantics,
    EffectRemediationAuthorizationSemantics,
)
from symphony_k.persistence.service import LifecycleService
from symphony_k.persistence.sqlite import SQLiteStore
from tests import test_creation_planned_effect as planned_fixtures
from tests import (
    test_effect_observation_quarantine_semantic_transitions as observation_fixtures,
)
from tests import test_effect_quarantine_exit_provenance as quarantine_fixtures
from tests import test_effect_remediation_semantic_transitions as fixtures
from tests import test_effect_semantic_transitions as preparation_fixtures
from tests.persistence_fixtures import data_rows, seed_snapshot
from tests.test_creation_integrated import creation_context
from tests.test_creation_observed_effect import observed_request
from tests.test_creation_run_outcome_evaluation import TASK


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


def committed_effect_history(
    store: SQLiteStore,
) -> tuple[LifecycleService, Effect, EffectObservationRecord]:
    """Build a real planned Effect and confirmed occurrence through the service."""
    creation = planned_fixtures.planned_request(with_run=False)
    seed_snapshot(store, TASK)
    service = LifecycleService(store)
    planned = service.create(creation, creation_context(creation)).entity
    assert isinstance(planned, Effect)
    semantics = observation_fixtures.confirmed_semantics(planned)
    request = replace(
        observation_fixtures.request(planned, EffectState.COMMITTED),
        event_id=EventId.new(),
    )
    committed = service.transition(
        planned.effect_id,
        request,
        observation_fixtures.context(planned, request, semantics),
    ).entity
    assert isinstance(committed, Effect)
    return service, committed, semantics.observation


def planned_effect_history(store: SQLiteStore) -> tuple[LifecycleService, Effect]:
    creation = planned_fixtures.planned_request(with_run=False)
    seed_snapshot(store, TASK)
    service = LifecycleService(store)
    planned = service.create(creation, creation_context(creation)).entity
    assert isinstance(planned, Effect)
    return service, planned


def quarantined_effect_history(
    store: SQLiteStore,
) -> tuple[LifecycleService, Effect, EffectQuarantineSemantics]:
    service, planned = planned_effect_history(store)
    uncertain = observation_fixtures.observation(
        planned,
        status=EffectOccurrenceStatus.UNCERTAIN,
    )
    semantics = EffectQuarantineSemantics(
        observation_fixtures.scope(planned, EffectState.QUARANTINED),
        observation_fixtures.quarantine_context(
            planned,
            reason=(EffectQuarantineReason.UNKNOWN_OR_SUSPECTED_OCCURRENCE),
            prior=uncertain.observation_id,
        ),
        observation=uncertain,
    )
    request = replace(
        observation_fixtures.request(planned, EffectState.QUARANTINED),
        event_id=EventId.new(),
    )
    quarantined = service.transition(
        planned.effect_id,
        request,
        observation_fixtures.context(planned, request, semantics),
    ).entity
    assert isinstance(quarantined, Effect)
    return service, quarantined, semantics


def compensating_quarantine_history(
    store: SQLiteStore,
) -> tuple[
    LifecycleService,
    Effect,
    EffectObservationRecord,
    EffectCompensationPlanRecord,
    EffectRemediationAuthorizationSemantics,
    DomainEvent,
    EffectQuarantineSemantics,
]:
    service, committed, original = committed_effect_history(store)
    start_semantics = replace(
        fixtures.start_semantics(committed),
        original_commit_observation=original,
    )
    start_request = replace(
        fixtures.request(committed, EffectState.COMPENSATING),
        event_id=EventId.new(),
    )
    started = service.transition(
        committed.effect_id,
        start_request,
        fixtures.context(committed, start_request, start_semantics),
    )
    assert isinstance(started.entity, Effect)
    context = observation_fixtures.quarantine_context(
        started.entity,
        reason=EffectQuarantineReason.COMPENSATION_OR_REMEDIATION_UNCERTAINTY,
        original=original.observation_id,
        plan=start_semantics.compensation_plan.plan_id,
    )
    semantics = EffectQuarantineSemantics(
        observation_fixtures.scope(started.entity, EffectState.QUARANTINED),
        context,
        original_commit_observation=original,
        compensation_plan=start_semantics.compensation_plan,
    )
    request = replace(
        observation_fixtures.request(started.entity, EffectState.QUARANTINED),
        event_id=EventId.new(),
    )
    quarantined = service.transition(
        committed.effect_id,
        request,
        observation_fixtures.context(started.entity, request, semantics),
    ).entity
    assert isinstance(quarantined, Effect)
    return (
        service,
        quarantined,
        original,
        start_semantics.compensation_plan,
        start_semantics.authorization,
        started.event,
        semantics,
    )


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
    service, committed, original = committed_effect_history(store)
    original_events = store.events.for_entity(committed.effect_id)
    semantic = replace(
        fixtures.start_semantics(committed),
        original_commit_observation=original,
    )
    request = fixtures.request(committed, EffectState.COMPENSATING)
    started = service.transition(
        committed.effect_id, request, fixtures.context(committed, request, semantic)
    )
    assert isinstance(started.entity, Effect)
    plan = semantic.compensation_plan
    completion = replace(
        fixtures.completion_semantics(
            started.entity,
            plan,
            authorized=fixtures.authorization(
                fixtures.authorization_scope(committed, plan=plan),
                recorded_by=fixtures.actor(
                    ActorType.EFFECT_CONTROLLER,
                    fixtures.COMPLETION_CONTROLLER,
                ),
            ),
        ),
        original_commit_observation=original,
    )
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
    assert observations == (original,)
    records = store.supporting_records(EffectCompensationCompletionRecord)
    assert len(records) == 1 and records[0].residual_impact_summary
    store.close()


def test_rollback_cannot_backfill_fabricated_original_commit_observation() -> None:
    store = SQLiteStore()
    service, committed, original = committed_effect_history(store)
    fabricated = replace(original, observation_id=EffectObservationId.new())
    rollback = fixtures.rollback_record(
        committed, original_id=fabricated.observation_id
    )
    authorization_scope = replace(
        fixtures.authorization_scope(committed),
        original_commit_observation_id=fabricated.observation_id,
    )
    semantics = fixtures.rollback_semantics(
        committed,
        original=fabricated,
        rollback=rollback,
        authorized=fixtures.authorization(authorization_scope),
    )
    request = replace(
        fixtures.request(committed, EffectState.ROLLED_BACK),
        event_id=EventId.new(),
    )
    before = data_rows(store)
    with pytest.raises(ConcurrencyConflict):
        service.transition(
            committed.effect_id,
            request,
            fixtures.context(committed, request, semantics),
        )
    assert data_rows(store) == before
    assert fabricated not in store.supporting_records(EffectObservationRecord)

    valid = fixtures.rollback_semantics(committed, original=original)
    request = replace(request, event_id=EventId.new())
    result = service.transition(
        committed.effect_id,
        request,
        fixtures.context(committed, request, valid),
    )
    assert result.entity.state is EffectState.ROLLED_BACK
    store.close()


def test_compensation_start_cannot_backfill_commit_observation() -> None:
    store = SQLiteStore()
    service, committed, original = committed_effect_history(store)
    fabricated = replace(original, observation_id=EffectObservationId.new())
    plan = replace(
        fixtures.compensation_plan(committed),
        original_commit_observation_id=fabricated.observation_id,
    )
    scope = replace(
        fixtures.authorization_scope(committed, plan=plan),
        original_commit_observation_id=fabricated.observation_id,
    )
    semantics = fixtures.start_semantics(
        committed,
        plan=plan,
        authorized=fixtures.authorization(scope),
    )
    semantics = replace(semantics, original_commit_observation=fabricated)
    request = replace(
        fixtures.request(committed, EffectState.COMPENSATING),
        event_id=EventId.new(),
    )
    before = data_rows(store)
    with pytest.raises(ConcurrencyConflict):
        service.transition(
            committed.effect_id,
            request,
            fixtures.context(committed, request, semantics),
        )
    assert data_rows(store) == before
    assert fabricated not in store.supporting_records(EffectObservationRecord)

    valid = replace(
        fixtures.start_semantics(committed),
        original_commit_observation=original,
    )
    request = replace(request, event_id=EventId.new())
    result = service.transition(
        committed.effect_id,
        request,
        fixtures.context(committed, request, valid),
    )
    assert result.entity.state is EffectState.COMPENSATING
    store.close()


def test_historical_record_requires_exact_durable_content() -> None:
    store = SQLiteStore()
    service, committed, original = committed_effect_history(store)
    substituted = replace(
        original,
        evidence_refs=frozenset({EvidenceRef("substituted occurrence evidence")}),
    )
    semantics = fixtures.rollback_semantics(committed, original=substituted)
    request = replace(
        fixtures.request(committed, EffectState.ROLLED_BACK),
        event_id=EventId.new(),
    )
    before = data_rows(store)
    with pytest.raises(ConcurrencyConflict):
        service.transition(
            committed.effect_id,
            request,
            fixtures.context(committed, request, semantics),
        )
    assert data_rows(store) == before
    store.close()


def test_compensation_completion_requires_durable_start_plan() -> None:
    store = SQLiteStore()
    service, committed, original = committed_effect_history(store)
    start_semantics = replace(
        fixtures.start_semantics(committed),
        original_commit_observation=original,
    )
    start_request = replace(
        fixtures.request(committed, EffectState.COMPENSATING),
        event_id=EventId.new(),
    )
    started = service.transition(
        committed.effect_id,
        start_request,
        fixtures.context(committed, start_request, start_semantics),
    )
    assert isinstance(started.entity, Effect)
    plan = start_semantics.compensation_plan
    fabricated_plan = replace(plan, plan_id=EffectCompensationPlanId.new())
    attack = replace(
        fixtures.completion_semantics(
            started.entity,
            fabricated_plan,
            authorized=fixtures.authorization(
                fixtures.authorization_scope(committed, plan=fabricated_plan),
                recorded_by=fixtures.actor(
                    ActorType.EFFECT_CONTROLLER,
                    fixtures.COMPLETION_CONTROLLER,
                ),
            ),
        ),
        original_commit_observation=original,
    )
    request = replace(
        fixtures.request(
            started.entity,
            EffectState.COMPENSATED,
            controller=fixtures.COMPLETION_CONTROLLER,
        ),
        event_id=EventId.new(),
    )
    before = data_rows(store)
    with pytest.raises(ConcurrencyConflict):
        service.transition(
            committed.effect_id,
            request,
            fixtures.context(
                started.entity, request, attack, start_event=started.event
            ),
        )
    assert data_rows(store) == before
    assert fabricated_plan not in store.supporting_records(type(fabricated_plan))

    valid = replace(
        fixtures.completion_semantics(
            started.entity,
            plan,
            authorized=fixtures.authorization(
                fixtures.authorization_scope(committed, plan=plan),
                recorded_by=fixtures.actor(
                    ActorType.EFFECT_CONTROLLER,
                    fixtures.COMPLETION_CONTROLLER,
                ),
            ),
        ),
        original_commit_observation=original,
    )
    forged_start = replace(
        started.event,
        reason=TransitionReason("substituted compensation-start event"),
    )
    event_attack_request = replace(request, event_id=EventId.new())
    with pytest.raises(ConcurrencyConflict):
        service.transition(
            committed.effect_id,
            event_attack_request,
            fixtures.context(
                started.entity,
                event_attack_request,
                valid,
                start_event=forged_start,
            ),
        )
    assert data_rows(store) == before
    request = replace(request, event_id=EventId.new())
    completed = service.transition(
        committed.effect_id,
        request,
        fixtures.context(started.entity, request, valid, start_event=started.event),
    )
    assert completed.entity.state is EffectState.COMPENSATED
    store.close()


def test_simulation_records_are_current_attempt_provenance() -> None:
    store = SQLiteStore()
    service, planned = planned_effect_history(store)
    s1 = preparation_fixtures.simulation(planned)
    request = replace(
        preparation_fixtures.request(planned, EffectState.SIMULATED),
        event_id=EventId.new(),
    )
    simulated = service.transition(
        planned.effect_id,
        request,
        preparation_fixtures.context(
            planned,
            request,
            EffectSimulationSemantics(s1),
        ),
    ).entity
    assert isinstance(simulated, Effect)

    request = replace(
        preparation_fixtures.request(simulated, EffectState.PENDING_COMMIT),
        event_id=EventId.new(),
    )
    reuse = preparation_fixtures.pending_semantics(simulated, simulation=s1)
    with pytest.raises(InvariantViolation):
        service.transition(
            simulated.effect_id,
            request,
            preparation_fixtures.context(simulated, request, reuse),
        )

    s2 = replace(
        preparation_fixtures.simulation(simulated),
        simulation_id=EffectSimulationRecordId.new(),
    )
    semantics = preparation_fixtures.pending_semantics(simulated, simulation=s2)
    request = replace(request, event_id=EventId.new())
    pending = service.transition(
        simulated.effect_id,
        request,
        preparation_fixtures.context(simulated, request, semantics),
    )
    assert pending.entity.state is EffectState.PENDING_COMMIT
    assert s1 != s2
    assert s1.operation_scope.observed_effect_version == planned.version
    assert s2.operation_scope.observed_effect_version == simulated.version
    assert set(store.supporting_records(EffectSimulationRecord)) == {s1, s2}
    store.close()


def test_quarantine_exit_cannot_substitute_context_or_uncertain_observation() -> None:
    store = SQLiteStore()
    service, quarantined, entry = quarantined_effect_history(store)
    assert entry.observation is not None
    valid = quarantine_fixtures.pending_exit_semantics(quarantined)
    disproved = replace(
        entry.observation,
        observation_id=EffectObservationId.new(),
        observed_effect_version=quarantined.version,
        occurrence_status=EffectOccurrenceStatus.DISPROVED,
        prior_observation_id=entry.observation.observation_id,
    )
    valid = replace(
        valid,
        quarantine_context=entry.quarantine_context,
        uncertain_observation=entry.observation,
        disproved_observation=disproved,
        reconciliation=replace(
            valid.reconciliation,
            quarantine_context_id=entry.quarantine_context.context_id,
        ),
    )
    fabricated_uncertain = replace(
        entry.observation, observation_id=EffectObservationId.new()
    )
    fabricated_context = replace(
        entry.quarantine_context,
        context_id=EffectQuarantineContextId.new(),
        prior_observation_id=fabricated_uncertain.observation_id,
    )
    attack = replace(
        valid,
        quarantine_context=fabricated_context,
        uncertain_observation=fabricated_uncertain,
        disproved_observation=replace(
            disproved,
            prior_observation_id=fabricated_uncertain.observation_id,
        ),
        reconciliation=replace(
            valid.reconciliation,
            quarantine_context_id=fabricated_context.context_id,
        ),
    )
    request = replace(
        quarantine_fixtures.transition_request(
            quarantined,
            EffectState.PENDING_COMMIT,
            quarantine_fixtures.CURRENT_CONTROLLER,
            quarantine_fixtures.ATTACK,
        ),
        event_id=EventId.new(),
    )
    before = data_rows(store)
    with pytest.raises(ConcurrencyConflict):
        service.transition(
            quarantined.effect_id,
            request,
            quarantine_fixtures.transition_context(quarantined, request, attack),
        )
    assert data_rows(store) == before
    assert fabricated_context not in store.supporting_records(type(fabricated_context))
    assert fabricated_uncertain not in store.supporting_records(EffectObservationRecord)

    request = replace(request, event_id=EventId.new())
    result = service.transition(
        quarantined.effect_id,
        request,
        quarantine_fixtures.transition_context(quarantined, request, valid),
    )
    assert result.entity.state is EffectState.PENDING_COMMIT
    store.close()


def test_direct_quarantine_completion_requires_historical_start_authorization() -> None:
    store = SQLiteStore()
    (
        service,
        quarantined,
        original,
        plan,
        historical_authorization,
        start_event,
        entry,
    ) = compensating_quarantine_history(store)
    completion = fixtures.completion_record(quarantined, plan)
    valid_completion = EffectCompensationCompletionSemantics(
        original,
        plan,
        completion,
        historical_authorization,
    )
    reconciliation = quarantine_fixtures.reconciliation_for(
        quarantined,
        entry.quarantine_context,
        quarantine_fixtures.CURRENT_CONTROLLER,
    )
    altered_authorization = replace(
        historical_authorization,
        policy_decision=replace(
            historical_authorization.policy_decision,
            evidence_refs=frozenset({EvidenceRef("substituted policy evidence")}),
        ),
    )
    attack = EffectQuarantineCompensationCompletionSemantics(
        entry.quarantine_context,
        reconciliation,
        replace(valid_completion, authorization=altered_authorization),
    )
    request = replace(
        quarantine_fixtures.transition_request(
            quarantined,
            EffectState.COMPENSATED,
            quarantine_fixtures.CURRENT_CONTROLLER,
            quarantine_fixtures.ATTACK,
        ),
        event_id=EventId.new(),
    )
    before = data_rows(store)
    with pytest.raises(ConcurrencyConflict):
        service.transition(
            quarantined.effect_id,
            request,
            quarantine_fixtures.transition_context(
                quarantined, request, attack, start_event
            ),
        )
    assert data_rows(store) == before

    valid = replace(attack, completion=valid_completion)
    request = replace(request, event_id=EventId.new())
    result = service.transition(
        quarantined.effect_id,
        request,
        quarantine_fixtures.transition_context(
            quarantined, request, valid, start_event
        ),
    )
    assert result.entity.state is EffectState.COMPENSATED
    store.close()
