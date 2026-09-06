"""Independent oracle for the accepted Task structural lifecycle graph."""

from itertools import product

import pytest

from symphony_k.domain import (
    TASK_CREATION_STATE,
    InvalidDomainValue,
    ObjectiveState,
    TaskState,
    can_task_transition,
)

EXPECTED_EDGES = {
    ("DRAFT", "READY"),
    ("DRAFT", "BLOCKED"),
    ("READY", "BLOCKED"),
    ("IN_PROGRESS", "BLOCKED"),
    ("BLOCKED", "READY"),
    ("READY", "IN_PROGRESS"),
    ("BLOCKED", "IN_PROGRESS"),
    ("IN_PROGRESS", "COMPLETED"),
    ("BLOCKED", "COMPLETED"),
    ("READY", "FAILED"),
    ("IN_PROGRESS", "FAILED"),
    ("BLOCKED", "FAILED"),
    ("DRAFT", "CANCELLED"),
    ("READY", "CANCELLED"),
    ("IN_PROGRESS", "CANCELLED"),
    ("BLOCKED", "CANCELLED"),
}


def test_task_state_inventory_and_separate_creation_boundary() -> None:
    expected = {
        "DRAFT",
        "READY",
        "IN_PROGRESS",
        "BLOCKED",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
    }
    assert len(TaskState) == 7
    assert set(TaskState.__members__) == expected
    assert {state.value for state in TaskState} == expected
    assert TASK_CREATION_STATE is TaskState.DRAFT
    for invalid in ("NONE", "EXPIRED", "ARCHIVED", "RETRYING"):
        with pytest.raises(ValueError):
            TaskState(invalid)
    with pytest.raises(InvalidDomainValue):
        can_task_transition(None, TaskState.DRAFT)  # type: ignore[arg-type]


@pytest.mark.parametrize(("source", "target"), tuple(product(TaskState, repeat=2)))
def test_all_forty_nine_pairs_match_the_contract(
    source: TaskState, target: TaskState
) -> None:
    assert can_task_transition(source, target) is (
        (source.value, target.value) in EXPECTED_EDGES
    )


def test_exactly_sixteen_state_edges_and_three_strict_sinks() -> None:
    actual = {
        (source.value, target.value)
        for source, target in product(TaskState, repeat=2)
        if can_task_transition(source, target)
    }
    assert len(actual) == 16
    assert actual == EXPECTED_EDGES
    assert {
        source
        for source in TaskState
        if not any(can_task_transition(source, target) for target in TaskState)
    } == {TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED}


@pytest.mark.parametrize("target", list(TaskState))
def test_self_loops_and_exits_from_terminal_states_are_forbidden(
    target: TaskState,
) -> None:
    assert not can_task_transition(target, target)
    for terminal in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED):
        assert not can_task_transition(terminal, target)


@pytest.mark.parametrize(
    "invalid", ["DRAFT", "READY", "NONE", None, 0, ObjectiveState.DRAFT]
)
def test_query_rejects_raw_or_other_entity_states(invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        can_task_transition(invalid, TaskState.READY)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        can_task_transition(TaskState.DRAFT, invalid)  # type: ignore[arg-type]
