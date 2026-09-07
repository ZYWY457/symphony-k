"""Typed target alternatives preserve observed scope without repository lookups."""

from dataclasses import fields
from uuid import UUID

import pytest

from symphony_k.domain import (
    ArtifactRef,
    EffectId,
    EntityVersion,
    EvaluationTargetRef,
    EvidenceRef,
    ExecutionProfileRef,
    InvalidDomainValue,
    ObjectiveId,
    OutcomeId,
    Run,
    RunId,
    RunState,
    TaskId,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")


@pytest.mark.parametrize("identity", [RunId(VALUE), OutcomeId(VALUE), EffectId(VALUE)])
@pytest.mark.parametrize("version", [0, 1, 41])
def test_entity_targets_retain_concrete_identity_and_observed_version(
    identity: RunId | OutcomeId | EffectId, version: int
) -> None:
    target = EvaluationTargetRef(identity, EntityVersion(version))
    assert target.reference is identity
    assert target.version == EntityVersion(version)
    assert {target: "found"}[
        EvaluationTargetRef(identity, EntityVersion(version))
    ] == "found"
    assert {field.name for field in fields(target)} == {"reference", "version"}
    assert not hasattr(target, "kind")  # No label that could disagree with the ID.
    assert not hasattr(target, "lookup")


def test_target_kinds_do_not_collapse_for_the_same_uuid() -> None:
    assert (
        len(
            {
                EvaluationTargetRef(identity, EntityVersion(7))
                for identity in (RunId(VALUE), OutcomeId(VALUE), EffectId(VALUE))
            }
        )
        == 3
    )


def test_anchored_evidence_has_no_invented_entity_version() -> None:
    evidence = EvidenceRef("opaque anchor; content not loaded")
    target = EvaluationTargetRef(evidence)
    assert target.reference is evidence
    assert target.version is None
    assert target == EvaluationTargetRef(evidence, None)
    assert {target: "found"}[EvaluationTargetRef(evidence)] == "found"


@pytest.mark.parametrize("identity", [RunId(VALUE), OutcomeId(VALUE), EffectId(VALUE)])
def test_entity_targets_cannot_omit_the_observed_version(
    identity: RunId | OutcomeId | EffectId,
) -> None:
    with pytest.raises(InvalidDomainValue):
        EvaluationTargetRef(identity)  # type: ignore[call-overload]
    with pytest.raises(InvalidDomainValue):
        EvaluationTargetRef(identity, None)  # type: ignore[call-overload]


@pytest.mark.parametrize("invalid", [0, True, "revision", EntityVersion(1)])
def test_evidence_cannot_carry_an_entity_version(invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        EvaluationTargetRef(EvidenceRef("anchor"), invalid)  # type: ignore[call-overload]


@pytest.mark.parametrize("invalid", [0, True, "revision"])
def test_entity_version_must_be_typed(invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        EvaluationTargetRef(RunId(VALUE), invalid)  # type: ignore[call-overload]


@pytest.mark.parametrize(
    "invalid",
    [
        VALUE,
        str(VALUE),
        None,
        TaskId(VALUE),
        ObjectiveId(VALUE),
        ArtifactRef("anchor"),
        (RunId(VALUE), OutcomeId(VALUE)),
    ],
)
def test_invalid_identity_categories_and_raw_values_are_rejected(
    invalid: object,
) -> None:
    with pytest.raises(InvalidDomainValue):
        EvaluationTargetRef(invalid, EntityVersion(7))  # type: ignore[call-overload]


def test_target_objects_are_not_references() -> None:
    run = Run(
        RunId(VALUE),
        TaskId(VALUE),
        RunState.RUNNING,
        EntityVersion(3),
        ExecutionProfileRef("profile", "revision"),
    )
    with pytest.raises(InvalidDomainValue):
        EvaluationTargetRef(run, EntityVersion(3))  # type: ignore[call-overload]
    target = EvaluationTargetRef(run.run_id, EntityVersion(999))
    assert target.version == EntityVersion(999)  # No lookup/current-version comparison.
    assert run.version == EntityVersion(3)


def test_target_and_nested_identity_are_immutable() -> None:
    target = EvaluationTargetRef(RunId(VALUE), EntityVersion(7))
    with pytest.raises(AttributeError):
        target.reference = OutcomeId(VALUE)  # type: ignore[misc]
    with pytest.raises(AttributeError):
        target.version = EntityVersion(8)  # type: ignore[misc]
    with pytest.raises(AttributeError):
        delattr(target, "reference")
    assert target.reference == RunId(VALUE)
    assert target.version == EntityVersion(7)
