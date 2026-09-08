"""Identity construction, serialization and nominal value semantics."""

from collections.abc import Iterator
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    CorrelationId,
    EffectCompensationCompletionId,
    EffectCompensationPlanId,
    EffectExecutionAuthorizationId,
    EffectId,
    EffectIncidentId,
    EffectIncidentRecordId,
    EffectObservationId,
    EffectPreparationRecordId,
    EffectRollbackRecordId,
    EffectVerificationRecordId,
    EvaluationArbitrationId,
    EvaluationConflictSetId,
    EvaluationId,
    EvaluationInvalidationId,
    InvalidDomainValue,
    ObjectiveId,
    OutcomeId,
    RunId,
    TaskId,
    ids,
)

type IdClass = (
    type[ObjectiveId]
    | type[TaskId]
    | type[RunId]
    | type[OutcomeId]
    | type[EvaluationId]
    | type[EvaluationArbitrationId]
    | type[EvaluationConflictSetId]
    | type[EvaluationInvalidationId]
    | type[EffectId]
    | type[EffectPreparationRecordId]
    | type[EffectVerificationRecordId]
    | type[EffectExecutionAuthorizationId]
    | type[EffectRollbackRecordId]
    | type[EffectCompensationPlanId]
    | type[EffectCompensationCompletionId]
    | type[EffectObservationId]
    | type[EffectIncidentId]
    | type[EffectIncidentRecordId]
    | type[ActorId]
    | type[CorrelationId]
)

ID_CLASSES: tuple[IdClass, ...] = (
    ObjectiveId,
    TaskId,
    RunId,
    OutcomeId,
    EvaluationId,
    EvaluationArbitrationId,
    EvaluationConflictSetId,
    EvaluationInvalidationId,
    EffectId,
    EffectPreparationRecordId,
    EffectVerificationRecordId,
    EffectExecutionAuthorizationId,
    EffectRollbackRecordId,
    EffectCompensationPlanId,
    EffectCompensationCompletionId,
    EffectObservationId,
    EffectIncidentId,
    EffectIncidentRecordId,
    ActorId,
    CorrelationId,
)
UUID_TEXT = "12345678-1234-4234-8234-123456789abc"
VALUE = UUID(UUID_TEXT)
OTHER = UUID("87654321-4321-4321-8321-cba987654321")


@pytest.mark.parametrize("id_class", ID_CLASSES)
def test_generation_preserves_concrete_type(
    id_class: IdClass, monkeypatch: pytest.MonkeyPatch
) -> None:
    generated: Iterator[UUID] = iter((VALUE, OTHER))
    monkeypatch.setattr(ids, "uuid4", lambda: next(generated))
    first, second = id_class.new(), id_class.new()
    assert type(first) is id_class
    assert first.value == VALUE and first.value.version == 4
    assert second.value == OTHER and first != second


@pytest.mark.parametrize("id_class", ID_CLASSES)
def test_uuid_round_trip_and_hashing(id_class: IdClass) -> None:
    identity = id_class(VALUE)
    assert str(identity) == UUID_TEXT
    assert id_class.from_string(UUID_TEXT.upper()) == identity
    assert id_class.from_string(str(identity)) == identity
    assert {identity: "found"}[id_class.from_string(UUID_TEXT)] == "found"
    assert identity != id_class(OTHER)
    assert identity != VALUE
    assert identity != UUID_TEXT  # type: ignore[comparison-overlap]


def test_all_id_kinds_with_the_same_uuid_are_distinct() -> None:
    values = [id_class(VALUE) for id_class in ID_CLASSES]
    assert len(set(values)) == len(ID_CLASSES)
    for index, identity in enumerate(values):
        for other in values[index + 1 :]:
            assert identity != other


@pytest.mark.parametrize("id_class", ID_CLASSES)
def test_ids_are_immutable(id_class: IdClass) -> None:
    identity = id_class(VALUE)
    with pytest.raises(AttributeError):
        identity.value = OTHER  # type: ignore[misc]
    with pytest.raises(AttributeError):
        delattr(identity, "value")
    assert identity.value == VALUE


@pytest.mark.parametrize("id_class", ID_CLASSES)
@pytest.mark.parametrize("text", ["", " ", "not-a-uuid", "1234", "g" * 32])
def test_invalid_uuid_text_is_rejected(id_class: IdClass, text: str) -> None:
    with pytest.raises(InvalidDomainValue):
        id_class.from_string(text)


@pytest.mark.parametrize("id_class", ID_CLASSES)
def test_construction_requires_uuid_and_parsing_requires_text(
    id_class: IdClass,
) -> None:
    with pytest.raises(InvalidDomainValue):
        id_class(UUID_TEXT)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        id_class(None)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        id_class(TaskId(VALUE))  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        id_class.from_string(VALUE)  # type: ignore[arg-type]


def test_valid_uuid_versions_are_not_restricted_by_new_factory() -> None:
    for value in (UUID(int=0), UUID("12345678-1234-1234-8234-123456789abc")):
        assert ObjectiveId.from_string(str(value)).value == value
