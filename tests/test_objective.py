"""Objective snapshot validation, without executing lifecycle transitions."""

from dataclasses import fields, replace
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CompletionPolicyRef,
    EntityVersion,
    InvalidDomainValue,
    Objective,
    ObjectiveId,
    ObjectiveState,
    TaskId,
    Timestamp,
    can_objective_transition,
)

IDENTIFIER = UUID("12345678-1234-4234-8234-123456789abc")


@pytest.fixture
def snapshot() -> Objective:
    return Objective(
        objective_id=ObjectiveId(IDENTIFIER),
        state=ObjectiveState.DRAFT,
        version=EntityVersion(17),
        goal="  Restore the payment path.\n",
        acceptance_criteria=("A test payment succeeds.", "  No duplicate charge.\n"),
        acceptance_authority=ActorIdentity(
            ActorId(IDENTIFIER), ActorType.HUMAN_OPERATOR
        ),
        completion_policy_ref=CompletionPolicyRef("payments/restoration", "revision-a"),
    )


def test_snapshot_preserves_required_definition_and_references(
    snapshot: Objective,
) -> None:
    assert snapshot.objective_id == ObjectiveId(IDENTIFIER)
    assert snapshot.state is ObjectiveState.DRAFT
    assert snapshot.version == EntityVersion(17)
    assert snapshot.goal == "  Restore the payment path.\n"
    assert snapshot.acceptance_criteria == (
        "A test payment succeeds.",
        "  No duplicate charge.\n",
    )
    assert snapshot.acceptance_authority == ActorIdentity(
        ActorId(IDENTIFIER), ActorType.HUMAN_OPERATOR
    )
    assert snapshot.completion_policy_ref == CompletionPolicyRef(
        "payments/restoration", "revision-a"
    )
    assert snapshot.valid_until is None


@pytest.mark.parametrize("state", list(ObjectiveState))
@pytest.mark.parametrize("version", [0, 1, 41])
def test_snapshot_representation_is_not_a_creation_transition(
    snapshot: Objective, state: ObjectiveState, version: int
) -> None:
    # replace constructs another snapshot, not a domain mutation/evolution API.
    represented = replace(snapshot, state=state, version=EntityVersion(version))
    assert represented.state is state
    assert represented.version.value == version
    assert snapshot.state is ObjectiveState.DRAFT
    assert snapshot.version.value == 17


def test_state_and_version_have_no_constructor_defaults() -> None:
    from dataclasses import MISSING

    definitions = {field.name: field for field in fields(Objective)}
    for name in ("state", "version"):
        assert definitions[name].default is MISSING
        assert definitions[name].default_factory is MISSING


@pytest.mark.parametrize("field", [field.name for field in fields(Objective)])
def test_all_snapshot_fields_are_immutable(snapshot: Objective, field: str) -> None:
    original = getattr(snapshot, field)
    with pytest.raises(AttributeError):
        setattr(snapshot, field, original)
    with pytest.raises(AttributeError):
        delattr(snapshot, field)
    assert getattr(snapshot, field) == original


def test_direct_state_assignment_and_nested_mutation_fail(snapshot: Objective) -> None:
    with pytest.raises(AttributeError):
        snapshot.state = ObjectiveState.ACTIVE  # type: ignore[misc]
    with pytest.raises(TypeError):
        snapshot.acceptance_criteria[0] = "changed"  # type: ignore[index]
    with pytest.raises(AttributeError):
        snapshot.completion_policy_ref.policy_version = "new"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        snapshot.acceptance_authority.actor_type = ActorType.SYSTEM  # type: ignore[misc]
    assert snapshot.state is ObjectiveState.DRAFT


@pytest.mark.parametrize("value", ["", " ", "\n\t", None, 1])
def test_invalid_goal_is_rejected(snapshot: Objective, value: object) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, goal=value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value",
    [(), ("",), ("valid", " \n"), (None,), (1,), ["valid"], {"valid"}, "valid", None],
)
def test_invalid_criteria_are_rejected(snapshot: Objective, value: object) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, acceptance_criteria=value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("objective_id", TaskId(IDENTIFIER)),
        ("objective_id", IDENTIFIER),
        ("objective_id", str(IDENTIFIER)),
        ("objective_id", None),
        ("state", "DRAFT"),
        ("state", "NONE"),
        ("state", None),
        ("state", ActorType.SYSTEM),
        ("version", 0),
        ("version", True),
        ("version", None),
        ("acceptance_authority", ActorId(IDENTIFIER)),
        ("acceptance_authority", ActorType.HUMAN_OPERATOR),
        ("acceptance_authority", "human"),
        ("acceptance_authority", None),
        ("completion_policy_ref", "policy@v1"),
        ("completion_policy_ref", True),
        ("completion_policy_ref", None),
        ("valid_until", datetime(2026, 9, 6, tzinfo=UTC)),
        ("valid_until", "2026-09-06T00:00:00+00:00"),
    ],
)
def test_typed_fields_reject_raw_or_wrong_values(
    snapshot: Objective, field: str, value: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, **{field: value})  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["policy_id", "policy_version"])
@pytest.mark.parametrize("value", ["", " ", "\t\n", None, 1, True])
def test_policy_reference_requires_two_meaningful_strings(
    field: str, value: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(CompletionPolicyRef("definition", "revision"), **{field: value})  # type: ignore[arg-type]


def test_policy_reference_is_opaque_and_immutable() -> None:
    reference = CompletionPolicyRef("  arbitrary definition URI\n", "not-semver")
    assert reference.policy_id == "  arbitrary definition URI\n"
    assert reference.policy_version == "not-semver"
    with pytest.raises(AttributeError):
        reference.policy_id = "replacement"  # type: ignore[misc]
    assert not hasattr(reference, "evaluate")
    assert not hasattr(reference, "policy_passed")


@pytest.mark.parametrize("category", list(ActorType))
def test_designation_does_not_check_or_grant_authority(
    snapshot: Objective, category: ActorType
) -> None:
    designation = ActorIdentity(ActorId(IDENTIFIER), category)
    represented = replace(snapshot, acceptance_authority=designation)
    assert represented.acceptance_authority == designation
    assert not hasattr(represented, "authorize")


def test_text_validation_does_not_claim_semantic_boundedness(
    snapshot: Objective,
) -> None:
    represented = replace(snapshot, goal="Always improve quality")
    assert represented.goal == "Always improve quality"


def test_horizon_retains_utc_without_automatically_expiring(
    snapshot: Objective,
) -> None:
    supplied = Timestamp(datetime(2000, 1, 1, 8, tzinfo=timezone(timedelta(hours=8))))
    represented = replace(snapshot, valid_until=supplied, state=ObjectiveState.ACTIVE)
    assert represented.valid_until is supplied
    assert represented.valid_until.value == datetime(2000, 1, 1, tzinfo=UTC)
    assert represented.valid_until.value.tzinfo is UTC
    assert represented.state is ObjectiveState.ACTIVE
    assert represented.version == snapshot.version


def test_topology_queries_do_not_execute_guards_or_mutate_snapshots(
    snapshot: Objective,
) -> None:
    represented = replace(
        snapshot,
        state=ObjectiveState.ACTIVE,
        acceptance_authority=ActorIdentity(ActorId(IDENTIFIER), ActorType.WORKER),
        completion_policy_ref=CompletionPolicyRef("not-resolved", "unknown-revision"),
    )
    assert can_objective_transition(represented.state, ObjectiveState.SATISFIED)
    assert can_objective_transition(represented.state, ObjectiveState.EXPIRED)
    assert represented.valid_until is None
    assert represented.state is ObjectiveState.ACTIVE
    assert represented.version == EntityVersion(17)
    assert represented.completion_policy_ref.policy_version == "unknown-revision"
    for name in (
        "create",
        "activate",
        "complete",
        "transition",
        "with_state",
        "events",
    ):
        assert not hasattr(represented, name)
