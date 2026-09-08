"""Effect identity and immutable planned/observed creation provenance."""

from dataclasses import MISSING, FrozenInstanceError, fields, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    Effect,
    EffectExternalOperationRef,
    EffectId,
    EffectPayloadRef,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    EvidenceRef,
    InvalidDomainValue,
    ObservedEffectOrigin,
    PlannedEffectOrigin,
    RunId,
    TaskId,
    Timestamp,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")


def actor(category: ActorType = ActorType.WORKER) -> ActorIdentity:
    return ActorIdentity(ActorId(VALUE), category)


def planned_origin(run_id: RunId | None = None) -> PlannedEffectOrigin:
    return PlannedEffectOrigin(TaskId(VALUE), actor(), run_id)


def observed_origin(
    *,
    task_id: TaskId | None = None,
    run_id: RunId | None = None,
    unlinked_reason: str | None = "Attribution not yet established",
) -> ObservedEffectOrigin:
    return ObservedEffectOrigin(
        EffectExternalOperationRef("provider operation 42"),
        frozenset({EvidenceRef("independent receipt 42")}),
        actor(ActorType.EVALUATOR),
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        task_id,
        run_id,
        unlinked_reason,
    )


@pytest.fixture
def planned_effect() -> Effect:
    return Effect(
        EffectId(VALUE),
        EffectState.PLANNED,
        EntityVersion(17),
        planned_origin(),
        EffectTargetRef("external target"),
        EffectPayloadRef("exact payload"),
    )


@pytest.mark.parametrize(
    "reference_type",
    [EffectTargetRef, EffectPayloadRef, EffectExternalOperationRef],
)
def test_effect_references_are_immutable_opaque_and_nonempty(
    reference_type: type[EffectTargetRef]
    | type[EffectPayloadRef]
    | type[EffectExternalOperationRef],
) -> None:
    text = "  supplied opaque identity\n"
    reference = reference_type(text)
    assert reference.value == text
    assert {field.name for field in fields(reference)} == {"value"}
    assert {reference: "found"}[reference_type(text)] == "found"
    with pytest.raises(FrozenInstanceError):
        reference.value = "changed"  # type: ignore[misc]
    for name in ("load", "read", "execute", "authorize", "url", "digest"):
        assert not hasattr(reference, name)


@pytest.mark.parametrize(
    "reference_type",
    [EffectTargetRef, EffectPayloadRef, EffectExternalOperationRef],
)
@pytest.mark.parametrize("invalid", ["", " ", "\t\n", None, 1, True])
def test_effect_references_reject_nonmeaningful_values(
    reference_type: type[EffectTargetRef]
    | type[EffectPayloadRef]
    | type[EffectExternalOperationRef],
    invalid: object,
) -> None:
    with pytest.raises(InvalidDomainValue):
        reference_type(invalid)  # type: ignore[arg-type]


def test_effect_reference_types_remain_distinct_at_runtime() -> None:
    target = EffectTargetRef("same")
    payload = EffectPayloadRef("same")
    operation = EffectExternalOperationRef("same")
    assert len({target, payload, operation}) == 3
    with pytest.raises(InvalidDomainValue):
        EffectTargetRef(payload)  # type: ignore[arg-type]


def test_planned_origin_requires_typed_task_and_preserves_optional_run() -> None:
    without_run = planned_origin()
    with_run = planned_origin(RunId(OTHER))
    assert without_run.task_id == TaskId(VALUE)
    assert without_run.run_id is None
    assert with_run.run_id == RunId(OTHER)
    assert with_run.proposed_by.actor_type is ActorType.WORKER
    assert {field.name for field in fields(with_run)} == {
        "task_id",
        "run_id",
        "proposed_by",
    }
    for category in ActorType:
        assert (
            replace(with_run, proposed_by=actor(category)).proposed_by.actor_type
            is category
        )


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("task_id", RunId(VALUE)),
        ("task_id", VALUE),
        ("task_id", str(VALUE)),
        ("task_id", None),
        ("run_id", TaskId(VALUE)),
        ("run_id", VALUE),
        ("proposed_by", ActorId(VALUE)),
        ("proposed_by", ActorType.WORKER),
        ("proposed_by", None),
    ],
)
def test_planned_origin_rejects_raw_or_wrong_typed_values(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(planned_origin(), **{field: invalid})  # type: ignore[arg-type]


def test_unlinked_observation_retains_unknown_attribution() -> None:
    origin = observed_origin()
    assert origin.task_id is None
    assert origin.run_id is None
    assert origin.unlinked_reason == "Attribution not yet established"
    assert origin.observation_evidence_refs == frozenset(
        {EvidenceRef("independent receipt 42")}
    )
    assert origin.external_operation_ref == EffectExternalOperationRef(
        "provider operation 42"
    )


def test_observed_origin_and_evidence_collection_are_immutable() -> None:
    origin = observed_origin()
    for field in fields(ObservedEffectOrigin):
        with pytest.raises(FrozenInstanceError):
            setattr(origin, field.name, getattr(origin, field.name))
    with pytest.raises(AttributeError):
        origin.observation_evidence_refs.add(EvidenceRef("later evidence"))  # type: ignore[attr-defined]


@pytest.mark.parametrize("category", list(ActorType))
def test_observer_category_is_provenance_not_recording_authority(
    category: ActorType,
) -> None:
    origin = replace(observed_origin(), observed_by=actor(category))
    assert origin.observed_by.actor_type is category
    assert not hasattr(origin, "recording_authority")


@pytest.mark.parametrize("run_id", [None, RunId(OTHER)])
def test_linked_observation_supports_task_and_optional_run(
    run_id: RunId | None,
) -> None:
    origin = observed_origin(task_id=TaskId(VALUE), run_id=run_id, unlinked_reason=None)
    assert origin.task_id == TaskId(VALUE)
    assert origin.run_id == run_id
    assert origin.unlinked_reason is None


@pytest.mark.parametrize("reason", [None, "", " ", "\t\n", 1])
def test_unlinked_observation_requires_meaningful_reason(reason: object) -> None:
    with pytest.raises(InvalidDomainValue):
        observed_origin(unlinked_reason=reason)  # type: ignore[arg-type]


def test_observation_attribution_rejects_run_without_task_or_linked_reason() -> None:
    with pytest.raises(InvalidDomainValue):
        observed_origin(run_id=RunId(OTHER))
    with pytest.raises(InvalidDomainValue):
        observed_origin(task_id=TaskId(VALUE), unlinked_reason="contradiction")


@pytest.mark.parametrize("evidence", [frozenset(), None, (), [], {EvidenceRef("x")}])
def test_observation_requires_nonempty_immutable_evidence(evidence: object) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(observed_origin(), observation_evidence_refs=evidence)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "evidence", [frozenset({"raw"}), frozenset({EffectPayloadRef("payload")})]
)
def test_observation_requires_typed_evidence(evidence: object) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(observed_origin(), observation_evidence_refs=evidence)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("external_operation_ref", EffectTargetRef("target")),
        ("external_operation_ref", "operation"),
        ("observed_by", ActorId(VALUE)),
        ("observed_by", ActorType.EVALUATOR),
        ("observed_at", datetime(2026, 9, 8, tzinfo=UTC)),
        ("task_id", RunId(VALUE)),
        ("run_id", TaskId(VALUE)),
    ],
)
def test_observed_origin_rejects_raw_or_wrong_typed_values(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(observed_origin(), **{field: invalid})  # type: ignore[arg-type]


def test_effect_snapshot_has_only_explicit_structural_fields(
    planned_effect: Effect,
) -> None:
    assert planned_effect.effect_id == EffectId(VALUE)
    assert planned_effect.state is EffectState.PLANNED
    assert planned_effect.version == EntityVersion(17)
    assert isinstance(planned_effect.origin, PlannedEffectOrigin)
    assert planned_effect.target_ref == EffectTargetRef("external target")
    assert planned_effect.payload_ref == EffectPayloadRef("exact payload")
    assert {field.name for field in fields(Effect)} == {
        "effect_id",
        "state",
        "version",
        "origin",
        "target_ref",
        "payload_ref",
    }
    for field in fields(Effect):
        assert field.default is MISSING
        assert field.default_factory is MISSING


@pytest.mark.parametrize("state", list(EffectState))
@pytest.mark.parametrize("version", [0, 1, 41])
def test_snapshots_represent_lifecycle_without_executing_it(
    planned_effect: Effect, state: EffectState, version: int
) -> None:
    represented = replace(planned_effect, state=state, version=EntityVersion(version))
    assert represented.state is state
    assert represented.version == EntityVersion(version)
    assert represented.origin is planned_effect.origin
    assert planned_effect.state is EffectState.PLANNED


@pytest.mark.parametrize("field", [field.name for field in fields(Effect)])
def test_all_effect_fields_are_immutable(planned_effect: Effect, field: str) -> None:
    original = getattr(planned_effect, field)
    with pytest.raises(FrozenInstanceError):
        setattr(planned_effect, field, original)
    with pytest.raises(FrozenInstanceError):
        delattr(planned_effect, field)


def test_creation_origin_and_nested_provenance_are_immutable(
    planned_effect: Effect,
) -> None:
    with pytest.raises(FrozenInstanceError):
        planned_effect.origin = observed_origin()  # type: ignore[misc]
    origin = planned_effect.origin
    assert isinstance(origin, PlannedEffectOrigin)
    with pytest.raises(FrozenInstanceError):
        origin.task_id = TaskId(OTHER)  # type: ignore[misc]
    assert origin.task_id == TaskId(VALUE)


def test_planned_effect_requires_payload_while_observed_payload_may_be_unknown(
    planned_effect: Effect,
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(planned_effect, payload_ref=None)
    observed = replace(
        planned_effect,
        state=EffectState.COMMITTED,
        origin=observed_origin(),
        payload_ref=None,
    )
    suspected = replace(observed, state=EffectState.QUARANTINED)
    assert observed.payload_ref is None
    assert suspected.payload_ref is None
    assert isinstance(observed.origin, ObservedEffectOrigin)


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("effect_id", TaskId(VALUE)),
        ("effect_id", VALUE),
        ("state", "PLANNED"),
        ("version", 1),
        ("origin", actor()),
        ("target_ref", EffectPayloadRef("payload")),
        ("payload_ref", EffectTargetRef("target")),
    ],
)
def test_effect_rejects_raw_or_wrong_typed_fields(
    planned_effect: Effect, field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(planned_effect, **{field: invalid})  # type: ignore[arg-type]


def test_provenance_implies_no_authority_or_external_action(
    planned_effect: Effect,
) -> None:
    origin = planned_effect.origin
    assert isinstance(origin, PlannedEffectOrigin)
    for category in ActorType:
        proposed = replace(
            planned_effect,
            origin=replace(origin, proposed_by=actor(category)),
        )
        assert proposed.state is EffectState.PLANNED
    observed = replace(
        planned_effect,
        state=EffectState.COMMITTED,
        origin=observed_origin(),
        payload_ref=None,
    )
    for value in (planned_effect, observed, planned_effect.origin, observed.origin):
        for name in (
            "commit",
            "rollback",
            "compensate",
            "transition",
            "with_state",
            "execute",
            "dispatch",
            "authorize",
            "relink_origin",
            "convert_to_planned",
            "convert_to_observed",
            "occurrence_status",
            "authorization_status",
            "incident_status",
            "task",
            "run",
            "events",
        ):
            assert not hasattr(value, name)
