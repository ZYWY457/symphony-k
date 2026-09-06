"""Run snapshot identity/provenance, without recovery or lifecycle execution."""

from dataclasses import MISSING, fields, replace
from uuid import UUID

import pytest

import symphony_k.domain as domain
from symphony_k.domain import (
    CompletionPolicyRef,
    EntityVersion,
    ExecutionProfileRef,
    InvalidDomainValue,
    ObjectiveId,
    Run,
    RunId,
    RunState,
    Task,
    TaskId,
    TaskState,
    can_run_transition,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")


@pytest.fixture
def snapshot() -> Run:
    return Run(
        run_id=RunId(VALUE),
        task_id=TaskId(VALUE),
        state=RunState.PENDING,
        version=EntityVersion(17),
        execution_profile_ref=ExecutionProfileRef(
            "unresolved-profile", "opaque-revision"
        ),
    )


def test_required_fields_and_absent_predecessor(snapshot: Run) -> None:
    assert snapshot.run_id == RunId(VALUE)
    assert snapshot.task_id == TaskId(VALUE)
    assert snapshot.state is RunState.PENDING
    assert snapshot.version == EntityVersion(17)
    assert snapshot.execution_profile_ref == ExecutionProfileRef(
        "unresolved-profile", "opaque-revision"
    )
    assert snapshot.predecessor_run_id is None
    assert {field.name for field in fields(Run)} == {
        "run_id",
        "task_id",
        "state",
        "version",
        "execution_profile_ref",
        "predecessor_run_id",
    }


def test_creation_and_initial_version_are_not_hidden_defaults() -> None:
    definitions = {field.name: field for field in fields(Run)}
    for name in ("run_id", "task_id", "state", "version", "execution_profile_ref"):
        assert definitions[name].default is MISSING
        assert definitions[name].default_factory is MISSING


@pytest.mark.parametrize("state", list(RunState))
@pytest.mark.parametrize("version", [0, 1, 41])
def test_snapshot_construction_does_not_execute_creation_or_guards(
    snapshot: Run, state: RunState, version: int
) -> None:
    represented = replace(snapshot, state=state, version=EntityVersion(version))
    assert represented.run_id == snapshot.run_id
    assert represented.state is state
    assert represented.version.value == version
    assert snapshot.state is RunState.PENDING and snapshot.version.value == 17


@pytest.mark.parametrize("field", [field.name for field in fields(Run)])
def test_snapshot_fields_are_immutable(snapshot: Run, field: str) -> None:
    original = getattr(snapshot, field)
    with pytest.raises(AttributeError):
        setattr(snapshot, field, original)
    with pytest.raises(AttributeError):
        delattr(snapshot, field)
    assert getattr(snapshot, field) == original


def test_state_and_nested_provenance_cannot_be_assigned(snapshot: Run) -> None:
    with pytest.raises(AttributeError):
        snapshot.state = RunState.COMPLETED  # type: ignore[misc]
    with pytest.raises(AttributeError):
        snapshot.run_id.value = OTHER  # type: ignore[misc]
    with pytest.raises(AttributeError):
        snapshot.execution_profile_ref.profile_id = "different"  # type: ignore[misc]
    assert snapshot.state is RunState.PENDING
    assert snapshot.run_id.value == VALUE


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("run_id", ObjectiveId(VALUE)),
        ("run_id", TaskId(VALUE)),
        ("run_id", VALUE),
        ("run_id", str(VALUE)),
        ("run_id", None),
        ("task_id", RunId(VALUE)),
        ("task_id", ObjectiveId(VALUE)),
        ("task_id", VALUE),
        ("task_id", str(VALUE)),
        ("task_id", None),
        ("task_id", (TaskId(VALUE), TaskId(OTHER))),
        ("state", "PENDING"),
        ("state", TaskState.READY),
        ("state", None),
        ("version", 0),
        ("version", True),
        ("version", None),
        ("execution_profile_ref", "profile@revision"),
        ("execution_profile_ref", True),
        ("execution_profile_ref", None),
        ("execution_profile_ref", CompletionPolicyRef("profile", "revision")),
        ("predecessor_run_id", ObjectiveId(OTHER)),
        ("predecessor_run_id", TaskId(OTHER)),
        ("predecessor_run_id", OTHER),
        ("predecessor_run_id", str(OTHER)),
    ],
)
def test_raw_or_wrong_typed_values_are_rejected(
    snapshot: Run, field: str, value: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, **{field: value})  # type: ignore[arg-type]


def test_task_and_run_objects_are_not_identity_references(snapshot: Run) -> None:
    task = Task(
        TaskId(VALUE),
        TaskState.CANCELLED,
        EntityVersion(3),
        "Work",
        ObjectiveId(VALUE),
        CompletionPolicyRef("policy", "revision"),
    )
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, task_id=task)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, predecessor_run_id=snapshot)  # type: ignore[arg-type]


def test_predecessor_is_optional_typed_provenance_without_lookup(snapshot: Run) -> None:
    represented = replace(snapshot, predecessor_run_id=RunId(OTHER))
    assert represented.predecessor_run_id == RunId(OTHER)
    assert represented.execution_profile_ref is snapshot.execution_profile_ref
    assert {represented: "found"}[replace(represented)] == "found"
    for identity in (snapshot.run_id, RunId(snapshot.run_id.value)):
        with pytest.raises(InvalidDomainValue):
            replace(snapshot, predecessor_run_id=identity)


def test_retry_can_describe_continuation_of_the_same_attempt(snapshot: Run) -> None:
    retrying = replace(snapshot, state=RunState.RETRYING)
    assert can_run_transition(retrying.state, RunState.RUNNING)
    # Two descriptive snapshots, not a domain transition/recovery helper.
    running = replace(retrying, state=RunState.RUNNING)
    assert running.run_id == retrying.run_id == snapshot.run_id
    assert running.task_id == retrying.task_id
    assert running.execution_profile_ref == retrying.execution_profile_ref
    assert running.version == retrying.version == EntityVersion(17)
    assert retrying.state is RunState.RETRYING


@pytest.mark.parametrize(
    "closed", [RunState.FAILED, RunState.ABORTED, RunState.REASSIGNED]
)
def test_a_distinct_attempt_uses_a_distinct_run_id(
    snapshot: Run, closed: RunState
) -> None:
    old = replace(snapshot, state=closed)
    new = Run(
        RunId(OTHER),
        old.task_id,
        RunState.PENDING,
        EntityVersion(5),
        ExecutionProfileRef("replacement-profile", "revision"),
        old.run_id,
    )
    assert new.run_id != old.run_id
    assert new.task_id == old.task_id
    assert new.predecessor_run_id == old.run_id
    assert old.state is closed and old.version.value == 17
    assert not can_run_transition(old.state, RunState.RUNNING)
    assert not hasattr(new, "attempt_id")


def test_structural_wait_and_completion_do_not_validate_or_propagate(
    snapshot: Run,
) -> None:
    task = Task(
        TaskId(VALUE),
        TaskState.CANCELLED,
        EntityVersion(3),
        "Work",
        ObjectiveId(VALUE),
        CompletionPolicyRef("unknown-policy", "revision"),
    )
    waiting = replace(
        snapshot, task_id=task.task_id, state=RunState.WAITING_FOR_VERIFICATION
    )
    assert can_run_transition(waiting.state, RunState.COMPLETED)
    assert can_run_transition(RunState.RUNNING, RunState.COMPLETED)
    completed = replace(waiting, state=RunState.COMPLETED)
    assert waiting.state is RunState.WAITING_FOR_VERIFICATION
    assert completed.version == waiting.version == EntityVersion(17)
    assert task.state is TaskState.CANCELLED and task.version.value == 3
    assert completed.execution_profile_ref is snapshot.execution_profile_ref
    assert not hasattr(domain, "Outcome")
    assert not hasattr(domain, "OutcomeState")
    assert not hasattr(domain, "AttemptId")
    for name in (
        "start",
        "retry",
        "complete",
        "fail",
        "abort",
        "reassign",
        "transition",
        "with_state",
        "resume",
        "rewind",
        "checkpoint",
        "events",
        "accepted",
        "successful_result",
        "outcome",
        "outcome_id",
        "successors",
        "authorize",
        "session_id",
        "container_id",
    ):
        assert not hasattr(completed, name)
