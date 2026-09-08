"""Effect rollback and compensation provenance remains immutable and separate."""

from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

import symphony_k.domain.effect_remediation as remediation_module
from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CorrelationId,
    Effect,
    EffectCompensationCompletionId,
    EffectCompensationCompletionRecord,
    EffectCompensationPlanId,
    EffectCompensationPlanRecord,
    EffectExternalOperationRef,
    EffectId,
    EffectIncidentId,
    EffectObservationId,
    EffectRollbackRecord,
    EffectRollbackRecordId,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    EvidenceRef,
    InvalidDomainValue,
    ObservedEffectOrigin,
    Timestamp,
    can_attach_effect_rollback_record,
    can_complete_effect_compensation_plan,
    can_effect_transition,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
THIRD = UUID("abcdefab-cdef-4def-8def-abcdefabcdef")
EFFECT_ID = EffectId(VALUE)
COMPENSATING_EFFECT_ID = EffectId(OTHER)
OBSERVATION_ID = EffectObservationId(THIRD)
ROLLBACK_ID = EffectRollbackRecordId(OTHER)
PLAN_ID = EffectCompensationPlanId(OTHER)
COMPLETION_ID = EffectCompensationCompletionId(THIRD)
VERSION = EntityVersion(7)
CORRELATION = CorrelationId(VALUE)


def actor(category: ActorType) -> ActorIdentity:
    return ActorIdentity(ActorId(VALUE), category)


def instant(day: int = 8) -> Timestamp:
    return Timestamp(datetime(2026, 9, day, tzinfo=UTC))


def effect(state: EffectState = EffectState.COMMITTED) -> Effect:
    return Effect(
        EFFECT_ID,
        state,
        VERSION,
        ObservedEffectOrigin(
            EffectExternalOperationRef("original-operation"),
            frozenset({EvidenceRef("original occurrence receipt")}),
            actor(ActorType.EFFECT_CONTROLLER),
            instant(),
            None,
            None,
            "Task attribution is unknown",
        ),
        EffectTargetRef("target"),
        None,
    )


def rollback(
    *,
    record_id: EffectRollbackRecordId = ROLLBACK_ID,
    effect_id: EffectId = EFFECT_ID,
    version: EntityVersion = VERSION,
    observation_id: EffectObservationId = OBSERVATION_ID,
) -> EffectRollbackRecord:
    return EffectRollbackRecord(
        record_id,
        effect_id,
        version,
        observation_id,
        EffectExternalOperationRef("restoration-operation"),
        "Independent verification established prior state restoration",
        frozenset({EvidenceRef("restoration receipt")}),
        actor(ActorType.EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER),
        instant(),
        instant(9),
        CORRELATION,
    )


def plan(
    *,
    plan_id: EffectCompensationPlanId = PLAN_ID,
    effect_id: EffectId = EFFECT_ID,
    version: EntityVersion = VERSION,
    observation_id: EffectObservationId = OBSERVATION_ID,
    compensating_ids: frozenset[EffectId] = frozenset({COMPENSATING_EFFECT_ID}),
    correlation: CorrelationId = CORRELATION,
) -> EffectCompensationPlanRecord:
    return EffectCompensationPlanRecord(
        plan_id,
        effect_id,
        version,
        observation_id,
        compensating_ids,
        "Governed correction Effect addresses the original mutation",
        frozenset({EvidenceRef("compensation plan evidence")}),
        actor(ActorType.EFFECT_CONTROLLER),
        actor(ActorType.EFFECT_CONTROLLER),
        instant(),
        instant(9),
        correlation,
    )


def completion(
    *,
    completion_id: EffectCompensationCompletionId = COMPLETION_ID,
    plan_id: EffectCompensationPlanId = PLAN_ID,
    effect_id: EffectId = EFFECT_ID,
    version: EntityVersion = VERSION,
    observation_id: EffectObservationId = OBSERVATION_ID,
    correlation: CorrelationId = CORRELATION,
) -> EffectCompensationCompletionRecord:
    return EffectCompensationCompletionRecord(
        completion_id,
        plan_id,
        effect_id,
        version,
        observation_id,
        "Independent evidence establishes all planned compensations completed",
        "Original external mutation remains historical fact",
        frozenset({EvidenceRef("compensation completion evidence")}),
        actor(ActorType.EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER),
        instant(),
        instant(9),
        correlation,
    )


def test_remediation_identities_are_nominal_and_distinct() -> None:
    assert (
        len(
            {
                EffectRollbackRecordId(VALUE),
                EffectCompensationPlanId(VALUE),
                EffectCompensationCompletionId(VALUE),
                EffectId(VALUE),
                EffectObservationId(VALUE),
                EffectIncidentId(VALUE),
                CorrelationId(VALUE),
            }
        )
        == 7
    )


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("rollback_record_id", EffectId(VALUE)),
        ("effect_id", EffectObservationId(VALUE)),
        ("observed_effect_version", 7),
        ("original_commit_observation_id", EffectId(VALUE)),
        ("restoration_operation_ref", EffectTargetRef("target")),
        ("restoration_summary", " \t"),
        ("evidence_refs", frozenset()),
        ("evidence_refs", frozenset({"raw"})),
        ("verified_by", ActorId(VALUE)),
        ("recorded_by", ActorType.EFFECT_CONTROLLER),
        ("verified_at", datetime(2026, 9, 8, tzinfo=UTC)),
        ("recorded_at", datetime(2026, 9, 9, tzinfo=UTC)),
        ("correlation_id", EffectId(VALUE)),
    ],
)
def test_rollback_record_rejects_invalid_or_missing_provenance(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(rollback(), **{field: invalid})  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("plan_id", EffectId(VALUE)),
        ("effect_id", EffectObservationId(VALUE)),
        ("observed_effect_version", 7),
        ("original_commit_observation_id", EffectId(VALUE)),
        ("compensating_effect_ids", frozenset()),
        ("compensating_effect_ids", frozenset({EffectObservationId(VALUE)})),
        ("compensation_summary", " \t"),
        ("evidence_refs", frozenset()),
        ("planned_by", ActorId(VALUE)),
        ("recorded_by", ActorType.EFFECT_CONTROLLER),
        ("planned_at", datetime(2026, 9, 8, tzinfo=UTC)),
        ("recorded_at", datetime(2026, 9, 9, tzinfo=UTC)),
        ("correlation_id", EffectId(VALUE)),
    ],
)
def test_compensation_plan_rejects_invalid_or_missing_provenance(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(plan(), **{field: invalid})  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("completion_id", EffectId(VALUE)),
        ("plan_id", EffectId(VALUE)),
        ("effect_id", EffectObservationId(VALUE)),
        ("observed_effect_version", 7),
        ("original_commit_observation_id", EffectId(VALUE)),
        ("completion_summary", " \t"),
        ("residual_impact_summary", " \t"),
        ("evidence_refs", frozenset()),
        ("verified_by", ActorId(VALUE)),
        ("recorded_by", ActorType.EFFECT_CONTROLLER),
        ("verified_at", datetime(2026, 9, 8, tzinfo=UTC)),
        ("recorded_at", datetime(2026, 9, 9, tzinfo=UTC)),
        ("correlation_id", EffectId(VALUE)),
    ],
)
def test_compensation_completion_rejects_invalid_or_missing_provenance(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(completion(), **{field: invalid})  # type: ignore[arg-type]


@pytest.mark.parametrize("record", [rollback(), plan(), completion()])
def test_remediation_records_are_frozen(
    record: (
        EffectRollbackRecord
        | EffectCompensationPlanRecord
        | EffectCompensationCompletionRecord
    ),
) -> None:
    for field in fields(record):
        with pytest.raises(FrozenInstanceError):
            setattr(record, field.name, getattr(record, field.name))


def test_rollback_attachment_requires_exact_effect_identity_and_version() -> None:
    snapshot = effect()
    assert can_attach_effect_rollback_record(snapshot, rollback())
    assert not can_attach_effect_rollback_record(
        snapshot, rollback(effect_id=EffectId(OTHER))
    )
    assert not can_attach_effect_rollback_record(
        snapshot, rollback(version=EntityVersion(6))
    )
    assert not can_attach_effect_rollback_record(
        snapshot, rollback(version=EntityVersion(8))
    )
    with pytest.raises(InvalidDomainValue):
        can_attach_effect_rollback_record(snapshot, EFFECT_ID)  # type: ignore[arg-type]


def test_compensation_uses_separate_effects_and_plan_proves_nothing_else() -> None:
    with pytest.raises(InvalidDomainValue):
        plan(compensating_ids=frozenset({EFFECT_ID}))
    value = plan()
    assert value.compensating_effect_ids == frozenset({COMPENSATING_EFFECT_ID})
    for name in (
        "authorize",
        "execute",
        "commit",
        "occurred",
        "execution_allowed",
        "compensated",
    ):
        assert not hasattr(value, name)
        assert not hasattr(remediation_module, name)


def test_completion_compatibility_checks_required_structural_context() -> None:
    value = plan()
    assert can_complete_effect_compensation_plan(value, completion())
    assert can_complete_effect_compensation_plan(
        value, completion(version=EntityVersion(8))
    )
    assert not can_complete_effect_compensation_plan(
        value, completion(plan_id=EffectCompensationPlanId(VALUE))
    )
    assert not can_complete_effect_compensation_plan(
        value, completion(effect_id=EffectId(OTHER))
    )
    assert not can_complete_effect_compensation_plan(
        value, completion(correlation=CorrelationId(OTHER))
    )
    assert not can_complete_effect_compensation_plan(
        value, completion(version=EntityVersion(6))
    )
    assert can_complete_effect_compensation_plan(
        value,
        replace(completion(), verified_at=instant(7), recorded_at=instant(6)),
    )
    with pytest.raises(InvalidDomainValue):
        can_complete_effect_compensation_plan(value, PLAN_ID)  # type: ignore[arg-type]


def test_records_preserve_original_commit_provenance_without_lifecycle_mutation() -> (
    None
):
    original = effect(EffectState.COMMITTED)
    rollback_record = rollback()
    compensation_plan = plan()
    compensation_completion = completion()
    assert rollback_record.original_commit_observation_id == OBSERVATION_ID
    assert compensation_plan.original_commit_observation_id == OBSERVATION_ID
    assert compensation_completion.original_commit_observation_id == OBSERVATION_ID
    assert compensation_completion.residual_impact_summary.strip()
    assert original.state is EffectState.COMMITTED
    assert not can_effect_transition(EffectState.COMMITTED, EffectState.COMPENSATED)
    for name in ("rollback", "compensate", "reconcile", "transition", "execute"):
        assert not hasattr(rollback_record, name)
        assert not hasattr(compensation_completion, name)
        assert not hasattr(remediation_module, name)
