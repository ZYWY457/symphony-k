"""Effect incident history remains immutable, explicit, and orthogonal."""

from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

import symphony_k.domain.effect_incident as incident_module
from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CorrelationId,
    Effect,
    EffectAttributionId,
    EffectAuthorizationFindingId,
    EffectExternalOperationRef,
    EffectGovernanceFindingId,
    EffectId,
    EffectIncidentId,
    EffectIncidentRecord,
    EffectIncidentRecordId,
    EffectIncidentStatus,
    EffectObservationId,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    EvidenceRef,
    InvalidDomainValue,
    ObservedEffectOrigin,
    Timestamp,
    can_attach_effect_incident_record,
    can_follow_effect_incident_record,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
THIRD = UUID("abcdefab-cdef-4def-8def-abcdefabcdef")
EFFECT_ID = EffectId(VALUE)
INCIDENT_ID = EffectIncidentId(OTHER)
RECORD_ID = EffectIncidentRecordId(THIRD)
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
            EffectExternalOperationRef("provider-operation"),
            frozenset({EvidenceRef("independent receipt")}),
            actor(ActorType.EFFECT_CONTROLLER),
            instant(),
            None,
            None,
            "Task attribution is unknown",
        ),
        EffectTargetRef("target"),
        None,
    )


def record(
    *,
    record_id: EffectIncidentRecordId = RECORD_ID,
    incident_id: EffectIncidentId = INCIDENT_ID,
    effect_id: EffectId = EFFECT_ID,
    version: EntityVersion = VERSION,
    status: EffectIncidentStatus = EffectIncidentStatus.OPEN,
    correlation: CorrelationId = CORRELATION,
    prior: EffectIncidentRecordId | None = None,
) -> EffectIncidentRecord:
    return EffectIncidentRecord(
        record_id,
        incident_id,
        effect_id,
        version,
        status,
        "Evidence supports this incident finding",
        frozenset({EvidenceRef("incident evidence")}),
        actor(ActorType.EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER),
        instant(),
        instant(9),
        correlation,
        prior,
    )


def test_incident_identities_are_nominal_and_distinct() -> None:
    assert (
        len(
            {
                EffectIncidentId(VALUE),
                EffectIncidentRecordId(VALUE),
                EffectId(VALUE),
                EffectObservationId(VALUE),
                EffectAttributionId(VALUE),
                EffectAuthorizationFindingId(VALUE),
                EffectGovernanceFindingId(VALUE),
                CorrelationId(VALUE),
            }
        )
        == 8
    )
    assert set(EffectIncidentStatus.__members__) == {"OPEN", "CLOSED"}


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("record_id", EffectIncidentId(VALUE)),
        ("record_id", VALUE),
        ("incident_id", EffectIncidentRecordId(VALUE)),
        ("incident_id", VALUE),
        ("effect_id", EffectIncidentId(VALUE)),
        ("effect_id", VALUE),
        ("observed_effect_version", 7),
        ("status", "OPEN"),
        ("incident_summary", " \t"),
        ("evidence_refs", frozenset()),
        ("evidence_refs", frozenset({"raw"})),
        ("determined_by", ActorId(VALUE)),
        ("recorded_by", ActorType.EFFECT_CONTROLLER),
        ("determined_at", datetime(2026, 9, 8, tzinfo=UTC)),
        ("recorded_at", datetime(2026, 9, 9, tzinfo=UTC)),
        ("correlation_id", EffectId(VALUE)),
        ("prior_record_id", EffectIncidentId(VALUE)),
    ],
)
def test_record_rejects_invalid_typed_or_empty_fields(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(record(), **{field: invalid})  # type: ignore[arg-type]


def test_record_is_frozen_and_only_rejects_direct_self_reference() -> None:
    value = record()
    for field in fields(value):
        with pytest.raises(FrozenInstanceError):
            setattr(value, field.name, getattr(value, field.name))
    with pytest.raises(AttributeError):
        value.evidence_refs.add(EvidenceRef("later"))  # type: ignore[attr-defined]
    with pytest.raises(InvalidDomainValue):
        record(prior=RECORD_ID)
    assert record(
        prior=EffectIncidentRecordId(VALUE)
    ).prior_record_id == EffectIncidentRecordId(VALUE)


@pytest.mark.parametrize("status", list(EffectIncidentStatus))
def test_first_record_may_truthfully_be_open_or_closed(
    status: EffectIncidentStatus,
) -> None:
    first = record(status=status)
    assert first.prior_record_id is None
    assert first.status is status


@pytest.mark.parametrize("state", list(EffectState))
def test_incident_history_attaches_to_every_effect_lifecycle_state(
    state: EffectState,
) -> None:
    snapshot = effect(state)
    value = record()
    assert can_attach_effect_incident_record(snapshot, value)
    assert snapshot.state is state


def test_attachment_requires_exact_effect_identity_and_version_without_mutation() -> (
    None
):
    snapshot = effect()
    assert not can_attach_effect_incident_record(
        snapshot, record(effect_id=EffectId(OTHER))
    )
    assert not can_attach_effect_incident_record(
        snapshot, record(version=EntityVersion(6))
    )
    assert not can_attach_effect_incident_record(
        snapshot, record(version=EntityVersion(8))
    )
    with pytest.raises(InvalidDomainValue):
        can_attach_effect_incident_record(snapshot, EFFECT_ID)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("previous_status", "current_status"),
    [
        (EffectIncidentStatus.OPEN, EffectIncidentStatus.OPEN),
        (EffectIncidentStatus.OPEN, EffectIncidentStatus.CLOSED),
        (EffectIncidentStatus.CLOSED, EffectIncidentStatus.CLOSED),
        (EffectIncidentStatus.CLOSED, EffectIncidentStatus.OPEN),
    ],
)
def test_lineage_allows_every_structurally_valid_status_combination(
    previous_status: EffectIncidentStatus, current_status: EffectIncidentStatus
) -> None:
    previous = record(status=previous_status)
    current = record(
        record_id=EffectIncidentRecordId(VALUE),
        status=current_status,
        prior=previous.record_id,
    )
    assert can_follow_effect_incident_record(previous, current)
    assert can_follow_effect_incident_record(
        previous, replace(current, observed_effect_version=EntityVersion(8))
    )


def test_lineage_requires_explicit_shared_context_without_timestamp_precedence() -> (
    None
):
    previous = record()
    current = record(record_id=EffectIncidentRecordId(VALUE), prior=previous.record_id)
    assert not can_follow_effect_incident_record(
        previous, replace(current, prior_record_id=EffectIncidentRecordId(OTHER))
    )
    assert not can_follow_effect_incident_record(
        previous, replace(current, incident_id=EffectIncidentId(VALUE))
    )
    assert not can_follow_effect_incident_record(
        previous, replace(current, effect_id=EffectId(OTHER))
    )
    assert not can_follow_effect_incident_record(
        previous, replace(current, correlation_id=CorrelationId(OTHER))
    )
    assert not can_follow_effect_incident_record(
        previous, replace(current, observed_effect_version=EntityVersion(6))
    )
    assert can_follow_effect_incident_record(
        previous, replace(current, determined_at=instant(7), recorded_at=instant(6))
    )
    with pytest.raises(InvalidDomainValue):
        can_follow_effect_incident_record(previous, previous.record_id)  # type: ignore[arg-type]


def test_incident_history_has_no_resolver_authority_or_cross_dimension_behavior() -> (
    None
):
    value = record(status=EffectIncidentStatus.CLOSED)
    for name in (
        "severity",
        "owner",
        "authorize",
        "execution_allowed",
        "rollback",
        "compensate",
        "current_incident_status",
        "latest_incident_record",
        "effective_incident_status",
    ):
        assert not hasattr(value, name)
        assert not hasattr(incident_module, name)
    assert effect(EffectState.COMMITTED).state is EffectState.COMMITTED
    assert effect(EffectState.QUARANTINED).state is EffectState.QUARANTINED
    assert effect(EffectState.ROLLED_BACK).state is EffectState.ROLLED_BACK
    assert effect(EffectState.COMPENSATED).state is EffectState.COMPENSATED
