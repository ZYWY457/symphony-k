"""Effect occurrence observations are immutable supporting facts."""

from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

import symphony_k.domain.effect_observation as observation_module
from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CorrelationId,
    Effect,
    EffectDeduplicationRef,
    EffectExternalOperationRef,
    EffectId,
    EffectObservationId,
    EffectObservationRecord,
    EffectOccurrenceStatus,
    EffectPayloadRef,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    EvidenceRef,
    InvalidDomainValue,
    ObservedEffectOrigin,
    PlannedEffectOrigin,
    TaskId,
    Timestamp,
    can_attach_effect_observation,
    can_follow_effect_observation,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
THIRD = UUID("abcdefab-cdef-4def-8def-abcdefabcdef")
OBSERVATION_ID = EffectObservationId(VALUE)
EFFECT_ID = EffectId(VALUE)
VERSION = EntityVersion(7)
OPERATION = EffectExternalOperationRef("operation")
DEDUPLICATION = EffectDeduplicationRef("provider key")
TARGET = EffectTargetRef("target")
CORRELATION = CorrelationId(VALUE)


def actor(category: ActorType = ActorType.EVALUATOR) -> ActorIdentity:
    return ActorIdentity(ActorId(VALUE), category)


def instant(day: int = 8) -> Timestamp:
    return Timestamp(datetime(2026, 9, day, tzinfo=UTC))


def record(
    *,
    observation_id: EffectObservationId = OBSERVATION_ID,
    effect_id: EffectId = EFFECT_ID,
    version: EntityVersion = VERSION,
    operation: EffectExternalOperationRef = OPERATION,
    deduplication: EffectDeduplicationRef = DEDUPLICATION,
    status: EffectOccurrenceStatus = EffectOccurrenceStatus.UNCERTAIN,
    target: EffectTargetRef = TARGET,
    payload: EffectPayloadRef | None = None,
    correlation: CorrelationId = CORRELATION,
    prior: EffectObservationId | None = None,
) -> EffectObservationRecord:
    return EffectObservationRecord(
        observation_id,
        effect_id,
        version,
        operation,
        deduplication,
        status,
        target,
        payload,
        frozenset({EvidenceRef("independent receipt")}),
        actor(ActorType.EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER),
        instant(),
        None,
        instant(9),
        correlation,
        prior,
    )


@pytest.mark.parametrize("invalid", ["", " ", "\t\n", None, 1, True])
def test_deduplication_reference_is_immutable_opaque_and_nonempty(
    invalid: object,
) -> None:
    with pytest.raises(InvalidDomainValue):
        EffectDeduplicationRef(invalid)  # type: ignore[arg-type]
    reference = EffectDeduplicationRef(" supplied identity ")
    assert reference.value == " supplied identity "
    with pytest.raises(FrozenInstanceError):
        reference.value = "changed"  # type: ignore[misc]
    for name in ("lookup", "deduplicate", "lock", "execute", "authorize"):
        assert not hasattr(reference, name)


def test_observation_identity_is_distinct_from_effect_and_correlation() -> None:
    observation_id = EffectObservationId(VALUE)
    assert len({observation_id, EffectId(VALUE), CorrelationId(VALUE)}) == 3


def test_exact_occurrence_status_inventory_is_supporting_metadata() -> None:
    assert set(EffectOccurrenceStatus.__members__) == {
        "CONFIRMED",
        "UNCERTAIN",
        "DISPROVED",
    }
    assert {status.value for status in EffectOccurrenceStatus} == {
        "CONFIRMED",
        "UNCERTAIN",
        "DISPROVED",
    }
    assert EffectOccurrenceStatus.__name__ != EffectState.__name__


def test_record_is_immutable_and_retains_unknown_payload_and_occurrence_time() -> None:
    value = record()
    assert value.payload_ref is None
    assert value.occurrence_at is None
    assert value.observed_by != value.recorded_by
    assert value.evidence_refs == frozenset({EvidenceRef("independent receipt")})
    for field in fields(value):
        with pytest.raises(FrozenInstanceError):
            setattr(value, field.name, getattr(value, field.name))
    with pytest.raises(AttributeError):
        value.evidence_refs.add(EvidenceRef("later"))  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("observation_id", EffectId(VALUE)),
        ("effect_id", EffectObservationId(VALUE)),
        ("observed_effect_version", 7),
        ("external_operation_ref", EffectTargetRef("target")),
        ("deduplication_ref", "provider key"),
        ("occurrence_status", "CONFIRMED"),
        ("target_ref", EffectPayloadRef("payload")),
        ("payload_ref", EffectTargetRef("target")),
        ("evidence_refs", frozenset()),
        ("evidence_refs", frozenset({"raw"})),
        ("observed_by", ActorId(VALUE)),
        ("recorded_by", ActorType.EFFECT_CONTROLLER),
        ("observed_at", datetime(2026, 9, 8, tzinfo=UTC)),
        ("occurrence_at", datetime(2026, 9, 8, tzinfo=UTC)),
        ("recorded_at", datetime(2026, 9, 9, tzinfo=UTC)),
        ("correlation_id", EffectId(VALUE)),
        ("prior_observation_id", EffectId(OTHER)),
    ],
)
def test_record_rejects_raw_or_wrong_typed_fields(field: str, invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(record(), **{field: invalid})  # type: ignore[arg-type]


def test_record_rejects_direct_self_reference_but_allows_explicit_prior() -> None:
    with pytest.raises(InvalidDomainValue):
        record(prior=EffectObservationId(VALUE))
    value = record(
        observation_id=EffectObservationId(OTHER), prior=EffectObservationId(VALUE)
    )
    assert value.prior_observation_id == EffectObservationId(VALUE)


def planned_effect(*, state: EffectState = EffectState.PLANNED) -> Effect:
    return Effect(
        EffectId(VALUE),
        state,
        EntityVersion(7),
        PlannedEffectOrigin(TaskId(VALUE), actor(ActorType.WORKER)),
        EffectTargetRef("target"),
        EffectPayloadRef("payload"),
    )


def observed_effect() -> Effect:
    return Effect(
        EffectId(VALUE),
        EffectState.COMMITTED,
        EntityVersion(7),
        ObservedEffectOrigin(
            EffectExternalOperationRef("operation"),
            frozenset({EvidenceRef("creation evidence")}),
            actor(),
            instant(),
            None,
            None,
            "Attribution unknown",
        ),
        EffectTargetRef("target"),
        None,
    )


def test_effect_compatibility_checks_exact_effect_structure() -> None:
    effect = planned_effect()
    matching = record(payload=EffectPayloadRef("payload"))
    assert can_attach_effect_observation(effect, matching)
    assert not can_attach_effect_observation(
        effect, replace(matching, effect_id=EffectId(OTHER))
    )
    assert not can_attach_effect_observation(
        effect, replace(matching, observed_effect_version=EntityVersion(6))
    )
    assert not can_attach_effect_observation(
        effect, replace(matching, observed_effect_version=EntityVersion(8))
    )
    assert not can_attach_effect_observation(
        effect, replace(matching, target_ref=EffectTargetRef("other target"))
    )
    assert not can_attach_effect_observation(
        effect, replace(matching, payload_ref=EffectPayloadRef("other payload"))
    )
    assert can_attach_effect_observation(effect, replace(matching, payload_ref=None))


def test_observed_origin_operation_is_checked_without_authority() -> None:
    effect = observed_effect()
    confirmed = replace(record(), occurrence_status=EffectOccurrenceStatus.CONFIRMED)
    assert can_attach_effect_observation(effect, confirmed)
    assert not can_attach_effect_observation(
        effect,
        replace(confirmed, external_operation_ref=EffectExternalOperationRef("other")),
    )
    assert can_attach_effect_observation(
        effect, replace(confirmed, payload_ref=EffectPayloadRef("observed"))
    )
    for name in ("authorized", "policy_passed", "permission_granted", "transition"):
        assert not hasattr(confirmed, name)


def test_disproved_observation_is_valid_metadata_for_quarantined_effect() -> None:
    effect = planned_effect(state=EffectState.QUARANTINED)
    disproved = replace(record(), occurrence_status=EffectOccurrenceStatus.DISPROVED)
    assert can_attach_effect_observation(effect, disproved)
    assert effect.state is EffectState.QUARANTINED


def test_lineage_requires_explicit_link_and_matching_identity_provenance() -> None:
    previous = record(status=EffectOccurrenceStatus.UNCERTAIN)
    confirmed = record(
        observation_id=EffectObservationId(OTHER),
        status=EffectOccurrenceStatus.CONFIRMED,
        prior=previous.observation_id,
    )
    disproved = replace(confirmed, occurrence_status=EffectOccurrenceStatus.DISPROVED)
    assert can_follow_effect_observation(previous, confirmed)
    assert can_follow_effect_observation(previous, disproved)
    assert not can_follow_effect_observation(
        previous, replace(confirmed, prior_observation_id=EffectObservationId(THIRD))
    )
    assert not can_follow_effect_observation(
        previous, replace(confirmed, effect_id=EffectId(OTHER))
    )
    assert not can_follow_effect_observation(
        previous,
        replace(confirmed, external_operation_ref=EffectExternalOperationRef("other")),
    )
    assert not can_follow_effect_observation(
        previous,
        replace(confirmed, deduplication_ref=EffectDeduplicationRef("other key")),
    )
    assert not can_follow_effect_observation(
        previous, replace(confirmed, correlation_id=CorrelationId(OTHER))
    )
    assert not can_follow_effect_observation(
        previous, replace(confirmed, observed_effect_version=EntityVersion(6))
    )
    assert can_follow_effect_observation(
        previous, replace(confirmed, observed_effect_version=EntityVersion(8))
    )


def test_observation_helpers_are_pure_and_offer_no_latest_wins_resolver() -> None:
    previous = record()
    current = record(
        observation_id=EffectObservationId(OTHER), prior=previous.observation_id
    )
    assert not hasattr(observation_module, "current_occurrence_status")
    assert not hasattr(observation_module, "latest_observation")
    assert can_follow_effect_observation(previous, current)
    assert previous.occurrence_status is EffectOccurrenceStatus.UNCERTAIN
    assert current.occurrence_status is EffectOccurrenceStatus.UNCERTAIN
    with pytest.raises(InvalidDomainValue):
        can_attach_effect_observation(planned_effect(), previous.effect_id)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        can_follow_effect_observation(previous, previous.observation_id)  # type: ignore[arg-type]
