"""Independent Run topology oracle; no authority or execution enforcement."""

from itertools import product

import pytest

from symphony_k.domain import (
    RUN_CREATION_STATE,
    InvalidDomainValue,
    ObjectiveState,
    RunState,
    TaskState,
    can_run_transition,
)

EXPECTED_EDGES = {
    ("PENDING", "RUNNING"),
    ("RUNNING", "WAITING_FOR_VERIFICATION"),
    ("RUNNING", "RETRYING"),
    ("RETRYING", "RUNNING"),
    ("PENDING", "REASSIGNED"),
    ("RUNNING", "REASSIGNED"),
    ("WAITING_FOR_VERIFICATION", "REASSIGNED"),
    ("RETRYING", "REASSIGNED"),
    ("RUNNING", "COMPLETED"),
    ("WAITING_FOR_VERIFICATION", "COMPLETED"),
    ("PENDING", "FAILED"),
    ("RUNNING", "FAILED"),
    ("WAITING_FOR_VERIFICATION", "FAILED"),
    ("RETRYING", "FAILED"),
    ("PENDING", "ABORTED"),
    ("RUNNING", "ABORTED"),
    ("WAITING_FOR_VERIFICATION", "ABORTED"),
    ("RETRYING", "ABORTED"),
}


def test_exact_run_state_inventory_and_creation_boundary() -> None:
    expected = {
        "PENDING",
        "RUNNING",
        "WAITING_FOR_VERIFICATION",
        "RETRYING",
        "REASSIGNED",
        "COMPLETED",
        "FAILED",
        "ABORTED",
    }
    assert len(RunState) == 8
    assert set(RunState.__members__) == expected
    assert {state.value for state in RunState} == expected
    assert RUN_CREATION_STATE is RunState.PENDING
    for invalid in ("NONE", "CANCELLED", "PAUSED", "REWINDING", "RESUMING"):
        with pytest.raises(ValueError):
            RunState(invalid)
    with pytest.raises(InvalidDomainValue):
        can_run_transition(None, RunState.PENDING)  # type: ignore[arg-type]


@pytest.mark.parametrize(("source", "target"), tuple(product(RunState, repeat=2)))
def test_all_sixty_four_pairs_match_the_contract(
    source: RunState, target: RunState
) -> None:
    assert can_run_transition(source, target) is (
        (source.value, target.value) in EXPECTED_EDGES
    )


def test_exactly_eighteen_edges_and_four_strict_sinks() -> None:
    actual = {
        (source.value, target.value)
        for source, target in product(RunState, repeat=2)
        if can_run_transition(source, target)
    }
    assert len(actual) == 18
    assert actual == EXPECTED_EDGES
    assert {
        source
        for source in RunState
        if not any(can_run_transition(source, target) for target in RunState)
    } == {RunState.REASSIGNED, RunState.COMPLETED, RunState.FAILED, RunState.ABORTED}


@pytest.mark.parametrize("target", list(RunState))
def test_terminal_runs_never_reopen_and_self_loops_are_forbidden(
    target: RunState,
) -> None:
    assert not can_run_transition(target, target)
    for terminal in (
        RunState.REASSIGNED,
        RunState.COMPLETED,
        RunState.FAILED,
        RunState.ABORTED,
    ):
        assert not can_run_transition(terminal, target)


def test_verification_wait_cannot_resume_execution_but_retry_can() -> None:
    assert not can_run_transition(RunState.WAITING_FOR_VERIFICATION, RunState.RUNNING)
    assert not can_run_transition(RunState.PENDING, RunState.COMPLETED)
    assert can_run_transition(RunState.RETRYING, RunState.RUNNING)


@pytest.mark.parametrize(
    "invalid", ["PENDING", "NONE", None, 1, TaskState.READY, ObjectiveState.ACTIVE]
)
def test_queries_reject_raw_and_other_entity_states(invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        can_run_transition(invalid, RunState.RUNNING)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        can_run_transition(RunState.PENDING, invalid)  # type: ignore[arg-type]
