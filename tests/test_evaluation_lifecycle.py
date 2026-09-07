"""An independent oracle for Evaluation's ten structural edges."""

from itertools import product

import pytest

from symphony_k.domain import (
    EVALUATION_CREATION_STATE,
    EvaluationState,
    InvalidDomainValue,
    OutcomeState,
    can_evaluation_transition,
)

EXPECTED_EDGES = {
    ("PENDING", "RUNNING"),
    ("RUNNING", "COMPLETED"),
    ("RUNNING", "CONFLICTED"),
    ("COMPLETED", "CONFLICTED"),
    ("COMPLETED", "ARBITRATED"),
    ("CONFLICTED", "ARBITRATED"),
    ("PENDING", "INVALID"),
    ("RUNNING", "INVALID"),
    ("COMPLETED", "INVALID"),
    ("CONFLICTED", "INVALID"),
}


def test_exact_state_inventory_and_creation() -> None:
    expected = {
        "PENDING",
        "RUNNING",
        "COMPLETED",
        "CONFLICTED",
        "ARBITRATED",
        "INVALID",
    }
    assert len(EvaluationState) == 6
    assert set(EvaluationState.__members__) == expected
    assert {state.value for state in EvaluationState} == expected
    assert EVALUATION_CREATION_STATE is EvaluationState.PENDING
    for invalid in ("NONE", "PASSED", "FAILED", "REJECTED", "OVERRIDDEN", "CANCELLED"):
        with pytest.raises(ValueError):
            EvaluationState(invalid)
    with pytest.raises(InvalidDomainValue):
        can_evaluation_transition(None, EvaluationState.PENDING)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("source", "target"), tuple(product(EvaluationState, repeat=2))
)
def test_all_thirty_six_state_pairs(
    source: EvaluationState, target: EvaluationState
) -> None:
    assert can_evaluation_transition(source, target) is (
        (source.value, target.value) in EXPECTED_EDGES
    )


def test_ten_edges_and_exactly_two_strict_sinks() -> None:
    actual = {
        (source.value, target.value)
        for source, target in product(EvaluationState, repeat=2)
        if can_evaluation_transition(source, target)
    }
    assert len(actual) == 10
    assert actual == EXPECTED_EDGES
    assert {
        source
        for source in EvaluationState
        if not any(
            can_evaluation_transition(source, target) for target in EvaluationState
        )
    } == {EvaluationState.ARBITRATED, EvaluationState.INVALID}


@pytest.mark.parametrize("state", list(EvaluationState))
def test_no_self_loops_or_terminal_reopening(state: EvaluationState) -> None:
    assert not can_evaluation_transition(state, state)
    assert not can_evaluation_transition(EvaluationState.ARBITRATED, state)
    assert not can_evaluation_transition(EvaluationState.INVALID, state)


@pytest.mark.parametrize(
    "invalid", ["RUNNING", "NONE", None, 0, OutcomeState.VALIDATING]
)
def test_queries_only_accept_evaluation_states(invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        can_evaluation_transition(invalid, EvaluationState.COMPLETED)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        can_evaluation_transition(EvaluationState.RUNNING, invalid)  # type: ignore[arg-type]
