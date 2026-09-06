"""Task snapshot and passive Objective relationship contracts."""

from dataclasses import MISSING, fields, replace
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
    Task,
    TaskId,
    TaskState,
    can_task_transition,
)

PRIMARY = ObjectiveId(UUID("12345678-1234-4234-8234-123456789abc"))
SECONDARY = ObjectiveId(UUID("87654321-4321-4321-8321-cba987654321"))
ANOTHER = ObjectiveId(UUID(int=0))


@pytest.fixture
def snapshot() -> Task:
    # IDs need no Objective objects or repository to be represented.
    return Task(
        task_id=TaskId(PRIMARY.value),
        state=TaskState.DRAFT,
        version=EntityVersion(17),
        definition="  Restore the payment endpoint.\n",
        primary_objective_id=PRIMARY,
        completion_policy_ref=CompletionPolicyRef("payment-task", "revision-a"),
    )


def test_required_typed_fields_and_empty_contributions(snapshot: Task) -> None:
    assert snapshot.task_id == TaskId(PRIMARY.value)
    assert snapshot.state is TaskState.DRAFT
    assert snapshot.version == EntityVersion(17)
    assert snapshot.definition == "  Restore the payment endpoint.\n"
    assert snapshot.primary_objective_id == PRIMARY
    assert snapshot.contributes_to == frozenset()
    assert snapshot.completion_policy_ref == CompletionPolicyRef(
        "payment-task", "revision-a"
    )


def test_state_version_and_primary_ownership_have_no_defaults() -> None:
    definitions = {field.name: field for field in fields(Task)}
    for name in ("state", "version", "primary_objective_id"):
        assert definitions[name].default is MISSING
        assert definitions[name].default_factory is MISSING


@pytest.mark.parametrize("state", list(TaskState))
@pytest.mark.parametrize("version", [0, 1, 41])
def test_snapshots_do_not_execute_creation_or_assign_versions(
    snapshot: Task, state: TaskState, version: int
) -> None:
    represented = replace(snapshot, state=state, version=EntityVersion(version))
    assert represented.state is state
    assert represented.version == EntityVersion(version)
    assert represented.primary_objective_id == PRIMARY
    assert snapshot.state is TaskState.DRAFT
    assert snapshot.version.value == 17


@pytest.mark.parametrize("field", [field.name for field in fields(Task)])
def test_all_snapshot_fields_are_immutable(snapshot: Task, field: str) -> None:
    original = getattr(snapshot, field)
    with pytest.raises(AttributeError):
        setattr(snapshot, field, original)
    with pytest.raises(AttributeError):
        delattr(snapshot, field)
    assert getattr(snapshot, field) == original


def test_state_ownership_and_nested_policy_cannot_be_assigned(snapshot: Task) -> None:
    with pytest.raises(AttributeError):
        snapshot.state = TaskState.READY  # type: ignore[misc]
    with pytest.raises(AttributeError):
        snapshot.primary_objective_id = SECONDARY  # type: ignore[misc]
    with pytest.raises(AttributeError):
        snapshot.completion_policy_ref.policy_version = "changed"  # type: ignore[misc]
    assert snapshot.state is TaskState.DRAFT
    assert snapshot.primary_objective_id == PRIMARY


@pytest.mark.parametrize("value", ["", " ", "\t\n", None, 0, True])
def test_definition_requires_meaningful_text(snapshot: Task, value: object) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, definition=value)  # type: ignore[arg-type]


def test_definition_does_not_perform_semantic_planning(snapshot: Task) -> None:
    assert (
        replace(snapshot, definition="Always improve quality").definition
        == "Always improve quality"
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("task_id", PRIMARY),
        ("task_id", PRIMARY.value),
        ("task_id", str(PRIMARY)),
        ("task_id", None),
        ("state", "DRAFT"),
        ("state", None),
        ("state", ObjectiveState.DRAFT),
        ("version", 0),
        ("version", True),
        ("version", None),
        ("primary_objective_id", None),
        ("primary_objective_id", PRIMARY.value),
        ("primary_objective_id", str(PRIMARY)),
        ("primary_objective_id", TaskId(PRIMARY.value)),
        ("primary_objective_id", (PRIMARY, SECONDARY)),
        ("primary_objective_id", frozenset({PRIMARY, SECONDARY})),
        ("completion_policy_ref", "policy@revision"),
        ("completion_policy_ref", True),
        ("completion_policy_ref", None),
    ],
)
def test_malformed_typed_fields_are_rejected(
    snapshot: Task, field: str, value: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, **{field: value})  # type: ignore[arg-type]


def test_contributions_are_immutable_unique_and_unordered(snapshot: Task) -> None:
    links = frozenset((SECONDARY, ANOTHER, ObjectiveId(SECONDARY.value)))
    represented = replace(snapshot, contributes_to=links)
    assert isinstance(represented.contributes_to, frozenset)
    assert len(represented.contributes_to) == 2
    assert represented.contributes_to == frozenset((ANOTHER, SECONDARY))
    assert represented.primary_objective_id not in represented.contributes_to
    assert {represented: "found"}[replace(represented)] == "found"
    with pytest.raises(AttributeError):
        represented.contributes_to.add(PRIMARY)  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        represented.contributes_to |= frozenset({PRIMARY})  # type: ignore[misc]
    assert represented.contributes_to == links


@pytest.mark.parametrize(
    "links",
    [
        frozenset({PRIMARY}),
        frozenset({ObjectiveId(PRIMARY.value), SECONDARY}),
    ],
)
def test_primary_cannot_also_be_a_secondary(
    snapshot: Task, links: frozenset[ObjectiveId]
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, contributes_to=links)


@pytest.mark.parametrize(
    "links",
    [
        None,
        "reference",
        (),
        [SECONDARY],
        {SECONDARY},
        frozenset({SECONDARY.value}),
        frozenset({str(SECONDARY)}),
        frozenset({TaskId(SECONDARY.value)}),
        frozenset({ActorId(SECONDARY.value)}),
        frozenset({SECONDARY, None}),
    ],
)
def test_invalid_secondary_collections_or_elements_are_rejected(
    snapshot: Task, links: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, contributes_to=links)  # type: ignore[arg-type]


def test_objective_objects_cannot_be_relationship_values(snapshot: Task) -> None:
    objective = Objective(
        objective_id=PRIMARY,
        state=ObjectiveState.CANCELLED,
        version=EntityVersion(23),
        goal="Restore payment processing",
        acceptance_criteria=("Payment succeeds",),
        acceptance_authority=ActorIdentity(
            ActorId(PRIMARY.value), ActorType.HUMAN_OPERATOR
        ),
        completion_policy_ref=snapshot.completion_policy_ref,
    )
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, primary_objective_id=objective)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, contributes_to=frozenset({objective}))  # type: ignore[arg-type]


def test_relationships_and_queries_never_read_or_propagate_objective_state(
    snapshot: Task,
) -> None:
    primary = Objective(
        objective_id=PRIMARY,
        state=ObjectiveState.CANCELLED,
        version=EntityVersion(23),
        goal="Restore payment processing",
        acceptance_criteria=("Payment succeeds",),
        acceptance_authority=ActorIdentity(ActorId(PRIMARY.value), ActorType.WORKER),
        completion_policy_ref=CompletionPolicyRef("unresolved-policy", "unknown"),
    )
    secondary = replace(primary, objective_id=SECONDARY, state=ObjectiveState.BLOCKED)
    represented = replace(
        snapshot,
        state=TaskState.BLOCKED,
        contributes_to=frozenset({secondary.objective_id}),
        completion_policy_ref=primary.completion_policy_ref,
    )
    assert can_task_transition(represented.state, TaskState.READY)
    assert can_task_transition(represented.state, TaskState.COMPLETED)
    # Merely representing a completed Task also cannot perform propagation.
    completed_snapshot = replace(represented, state=TaskState.COMPLETED)
    assert completed_snapshot.primary_objective_id == primary.objective_id
    assert represented.state is TaskState.BLOCKED
    assert represented.version == EntityVersion(17)
    assert primary.state is ObjectiveState.CANCELLED and primary.version.value == 23
    assert secondary.state is ObjectiveState.BLOCKED and secondary.version.value == 23
    assert represented.completion_policy_ref is primary.completion_policy_ref
    for name in (
        "ready",
        "start",
        "complete",
        "cancel",
        "transition",
        "with_state",
        "propagate_state",
        "complete_primary_objective",
        "update_contributed_objectives",
        "events",
        "dependencies",
        "run_id",
        "evaluate_policy",
    ):
        assert not hasattr(represented, name)
