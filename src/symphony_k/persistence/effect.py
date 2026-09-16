"""Durable historical-provenance closure for accepted Effect transitions."""

from symphony_k.domain import ConcurrencyConflict, Effect, EffectState, EventId
from symphony_k.domain.effect_incident import EffectIncidentRecord
from symphony_k.domain.effect_observation import (
    EffectObservationRecord,
    EffectOccurrenceStatus,
)
from symphony_k.domain.effect_remediation import EffectCompensationPlanRecord
from symphony_k.domain.effect_semantics import (
    EffectCompensationCompletionSemantics,
    EffectCompensationStartSemantics,
    EffectConfirmedOccurrenceSemantics,
    EffectPendingCommitSemantics,
    EffectQuarantineCompensationCompletionSemantics,
    EffectQuarantineCompensationMode,
    EffectQuarantineCompensationStartSemantics,
    EffectQuarantineContext,
    EffectQuarantinePendingCommitSemantics,
    EffectQuarantineRollbackSemantics,
    EffectQuarantineSemantics,
    EffectReconciliationRecord,
    EffectRollbackSemantics,
    EffectSimulationSemantics,
)
from symphony_k.domain.transition_engine import (
    DomainEvent,
    TransitionContext,
    TransitionRequest,
)

from ._storage import Storage


def _event_for_current(storage: Storage, effect: Effect) -> DomainEvent:
    matches = tuple(
        event
        for event in storage.events.for_entity(effect.effect_id)
        if event.entity_version == effect.version
    )
    if len(matches) != 1:
        raise ConcurrencyConflict("Current Effect lifecycle event is not durable")
    return matches[0]


def _require_recorded_state(
    storage: Storage,
    effect: Effect,
    record: object,
    state: EffectState,
    *,
    event_id: EventId | None = None,
) -> DomainEvent:
    recorded_event_id = storage._require_existing_record(record)
    if event_id is not None and recorded_event_id != event_id:
        raise ConcurrencyConflict("Historical supporting-record lineage differs")
    event = storage.events.load(recorded_event_id)
    if (
        event.entity_id != effect.effect_id
        or event.metadata.new_state is not state
        or event.entity_version.value > effect.version.value
    ):
        raise ConcurrencyConflict(
            "Historical supporting record belongs to another path"
        )
    return event


def _require_original_commit(
    storage: Storage,
    effect: Effect,
    observation: EffectObservationRecord,
    *,
    event: DomainEvent | None = None,
) -> None:
    if observation.occurrence_status is not EffectOccurrenceStatus.CONFIRMED:
        raise ConcurrencyConflict("Historical commit observation is not confirmed")
    _require_recorded_state(
        storage,
        effect,
        observation,
        EffectState.COMMITTED,
        event_id=event.event_id if event is not None else None,
    )


def _require_context_references(
    storage: Storage,
    effect: Effect,
    context: EffectQuarantineContext,
    entry_event: DomainEvent,
) -> None:
    if context.prior_observation_id is not None:
        prior = storage._load_record(
            EffectObservationRecord, context.prior_observation_id
        )
        _require_recorded_state(
            storage,
            effect,
            prior,
            EffectState.QUARANTINED,
            event_id=entry_event.event_id,
        )
    if context.original_commit_observation_id is not None:
        original = storage._load_record(
            EffectObservationRecord, context.original_commit_observation_id
        )
        assert isinstance(original, EffectObservationRecord)
        _require_original_commit(storage, effect, original)
    if context.compensation_plan_id is not None:
        plan = storage._load_record(
            EffectCompensationPlanRecord, context.compensation_plan_id
        )
        _require_recorded_state(storage, effect, plan, EffectState.COMPENSATING)
    if context.incident_record_id is not None:
        incident = storage._load_record(
            EffectIncidentRecord, context.incident_record_id
        )
        _require_recorded_state(
            storage,
            effect,
            incident,
            EffectState.QUARANTINED,
            event_id=entry_event.event_id,
        )


def _require_quarantine_entry(
    storage: Storage,
    effect: Effect,
    context: EffectQuarantineContext,
) -> DomainEvent:
    entry_event = _event_for_current(storage, effect)
    if entry_event.metadata.new_state is not EffectState.QUARANTINED:
        raise ConcurrencyConflict("Current Effect was not durably quarantined")
    storage._require_existing_record(context, entry_event.event_id)
    _require_context_references(storage, effect, context, entry_event)
    return entry_event


def validate_effect_historical_provenance(
    storage: Storage,
    current_effect: Effect,
    transition_request: TransitionRequest[EffectState],
    transition_context: TransitionContext,
) -> None:
    """Require only facts whose accepted lifecycle role predates this operation."""
    guard = transition_context.effect_semantic_guard
    if guard is None:
        return
    semantics = guard.semantic_input

    # These inputs describe only the current attempt. In particular, the
    # SIMULATED -> PENDING_COMMIT simulation is S2 for the current snapshot.
    if isinstance(semantics, (EffectSimulationSemantics, EffectPendingCommitSemantics)):
        return

    if isinstance(semantics, EffectConfirmedOccurrenceSemantics):
        if current_effect.state is not EffectState.QUARANTINED:
            return
        if semantics.quarantine_context is not None:
            entry_event = _require_quarantine_entry(
                storage, current_effect, semantics.quarantine_context
            )
            if semantics.prior_observation is not None:
                storage._require_existing_record(
                    semantics.prior_observation, entry_event.event_id
                )
            if semantics.prior_incident_record is not None:
                storage._require_existing_record(
                    semantics.prior_incident_record, entry_event.event_id
                )
        return

    if isinstance(semantics, EffectQuarantineSemantics):
        current_event = _event_for_current(storage, current_effect)
        if current_effect.state is EffectState.COMMITTED:
            assert semantics.original_commit_observation is not None
            _require_original_commit(
                storage,
                current_effect,
                semantics.original_commit_observation,
                event=current_event,
            )
        elif current_effect.state is EffectState.COMPENSATING:
            assert semantics.original_commit_observation is not None
            assert semantics.compensation_plan is not None
            _require_original_commit(
                storage, current_effect, semantics.original_commit_observation
            )
            _require_recorded_state(
                storage,
                current_effect,
                semantics.compensation_plan,
                EffectState.COMPENSATING,
                event_id=current_event.event_id,
            )
        return

    if isinstance(semantics, EffectRollbackSemantics):
        _require_original_commit(
            storage,
            current_effect,
            semantics.original_commit_observation,
            event=_event_for_current(storage, current_effect),
        )
        return

    if isinstance(semantics, EffectCompensationStartSemantics):
        _require_original_commit(
            storage,
            current_effect,
            semantics.original_commit_observation,
            event=_event_for_current(storage, current_effect),
        )
        return

    if isinstance(semantics, EffectCompensationCompletionSemantics):
        start_event = transition_context.effect_compensation_start_event
        if start_event is None:
            return  # The accepted pure guard reports the missing event.
        _require_original_commit(
            storage, current_effect, semantics.original_commit_observation
        )
        resume = semantics.resume_provenance
        plan_event_id = (
            resume.prior_compensation_start_event_id
            if resume is not None
            else start_event.event_id
        )
        _require_recorded_state(
            storage,
            current_effect,
            semantics.compensation_plan,
            EffectState.COMPENSATING,
            event_id=plan_event_id,
        )
        if resume is not None:
            storage._load_record(EffectQuarantineContext, resume.quarantine_context_id)
            storage._load_record(EffectReconciliationRecord, resume.reconciliation_id)
            storage._require_operation_provenance(
                resume.prior_compensation_start_event_id,
                resume.prior_authorization,
            )
        return

    if isinstance(semantics, EffectQuarantinePendingCommitSemantics):
        entry_event = _require_quarantine_entry(
            storage, current_effect, semantics.quarantine_context
        )
        storage._require_existing_record(
            semantics.uncertain_observation, entry_event.event_id
        )
        return

    if isinstance(semantics, EffectQuarantineRollbackSemantics):
        _require_quarantine_entry(storage, current_effect, semantics.quarantine_context)
        _require_original_commit(
            storage,
            current_effect,
            semantics.rollback.original_commit_observation,
        )
        return

    if isinstance(semantics, EffectQuarantineCompensationStartSemantics):
        _require_quarantine_entry(storage, current_effect, semantics.quarantine_context)
        compensation = semantics.compensation
        _require_original_commit(
            storage, current_effect, compensation.original_commit_observation
        )
        if semantics.mode is EffectQuarantineCompensationMode.RESUME_EXISTING_PLAN:
            start_event = transition_context.effect_compensation_start_event
            if start_event is not None:
                _require_recorded_state(
                    storage,
                    current_effect,
                    compensation.compensation_plan,
                    EffectState.COMPENSATING,
                    event_id=start_event.event_id,
                )
        return

    if isinstance(semantics, EffectQuarantineCompensationCompletionSemantics):
        _require_quarantine_entry(storage, current_effect, semantics.quarantine_context)
        completion = semantics.completion
        _require_original_commit(
            storage, current_effect, completion.original_commit_observation
        )
        start_event = transition_context.effect_compensation_start_event
        if start_event is None:
            return
        _require_recorded_state(
            storage,
            current_effect,
            completion.compensation_plan,
            EffectState.COMPENSATING,
            event_id=start_event.event_id,
        )
        storage._require_operation_provenance(
            start_event.event_id, completion.authorization
        )
