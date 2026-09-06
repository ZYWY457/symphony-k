"""Independent oracle for Outcome topology, not acceptance enforcement."""

from itertools import product

import pytest

from symphony_k.domain import (
    OUTCOME_CREATION_STATE,
    InvalidDomainValue,
    OutcomeState,
    RunState,
    can_outcome_transition,
)

EXPECTED_EDGES = {
    ("PROPOSED", "VALIDATING"),
    ("VALIDATING", "ACCEPTED"),
    ("VALIDATING", "REJECTED"),
    ("PROPOSED", "SUPERSEDED"),
    ("VALIDATING", "SUPERSEDED"),
    ("ACCEPTED", "SUPERSEDED"),
    ("REJECTED", "SUPERSEDED"),
    ("PROPOSED", "EXPIRED"),
    ("VALIDATING", "EXPIRED"),
    ("ACCEPTED", "EXPIRED"),
    ("REJECTED", "EXPIRED"),
}


def test_exact_inventory_and_untrusted_creation_destination() -> None:
    expected = {
        "PROPOSED",
        "VALIDATING",
        "ACCEPTED",
        "REJECTED",
        "SUPERSEDED",
        "EXPIRED",
    }
    assert len(OutcomeState) == 6
    assert set(OutcomeState.__members__) == expected
    assert {state.value for state in OutcomeState} == expected
    assert OUTCOME_CREATION_STATE is OutcomeState.PROPOSED
    for invalid in ("NONE", "CONFLICTED", "INVALID", "COMPLETED", "FAILED"):
        with pytest.raises(ValueError):
            OutcomeState(invalid)
    with pytest.raises(InvalidDomainValue):
        can_outcome_transition(None, OutcomeState.PROPOSED)  # type: ignore[arg-type]


@pytest.mark.parametrize(("source", "target"), tuple(product(OutcomeState, repeat=2)))
def test_all_thirty_six_state_pairs(source: OutcomeState, target: OutcomeState) -> None:
    assert can_outcome_transition(source, target) is (
        (source.value, target.value) in EXPECTED_EDGES
    )


def test_exactly_eleven_edges_and_two_strict_sinks() -> None:
    actual = {
        (source.value, target.value)
        for source, target in product(OutcomeState, repeat=2)
        if can_outcome_transition(source, target)
    }
    assert actual == EXPECTED_EDGES
    assert len(actual) == 11
    assert {
        source
        for source in OutcomeState
        if not any(can_outcome_transition(source, target) for target in OutcomeState)
    } == {OutcomeState.SUPERSEDED, OutcomeState.EXPIRED}


@pytest.mark.parametrize("state", list(OutcomeState))
def test_self_loops_and_exits_from_strict_sinks_are_forbidden(
    state: OutcomeState,
) -> None:
    assert not can_outcome_transition(state, state)
    assert not can_outcome_transition(OutcomeState.SUPERSEDED, state)
    assert not can_outcome_transition(OutcomeState.EXPIRED, state)


@pytest.mark.parametrize("state", [OutcomeState.ACCEPTED, OutcomeState.REJECTED])
def test_judgments_only_exit_to_supersession_or_expiry(state: OutcomeState) -> None:
    assert {
        target for target in OutcomeState if can_outcome_transition(state, target)
    } == {OutcomeState.SUPERSEDED, OutcomeState.EXPIRED}


def test_no_direct_acceptance_or_judgment_toggle() -> None:
    assert not can_outcome_transition(OutcomeState.PROPOSED, OutcomeState.ACCEPTED)
    assert not can_outcome_transition(OutcomeState.ACCEPTED, OutcomeState.REJECTED)
    assert not can_outcome_transition(OutcomeState.REJECTED, OutcomeState.ACCEPTED)


@pytest.mark.parametrize("invalid", ["PROPOSED", "NONE", None, 1, RunState.COMPLETED])
def test_queries_require_outcome_states(invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        can_outcome_transition(invalid, OutcomeState.ACCEPTED)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        can_outcome_transition(OutcomeState.VALIDATING, invalid)  # type: ignore[arg-type]
