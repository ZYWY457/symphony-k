"""Closed Objective topology, not transition execution or authorization."""

from itertools import product

import pytest

from symphony_k.domain import (
    OBJECTIVE_CREATION_STATE,
    ActorType,
    InvalidDomainValue,
    ObjectiveState,
    can_objective_transition,
)

# Independent contract oracle transcribed from the accepted Objective table.
EXPECTED_EDGES = {
    ("DRAFT", "ACTIVE"),
    ("ACTIVE", "BLOCKED"),
    ("BLOCKED", "ACTIVE"),
    ("ACTIVE", "SATISFIED"),
    ("BLOCKED", "SATISFIED"),
    ("ACTIVE", "FAILED"),
    ("BLOCKED", "FAILED"),
    ("DRAFT", "CANCELLED"),
    ("ACTIVE", "CANCELLED"),
    ("BLOCKED", "CANCELLED"),
    ("DRAFT", "EXPIRED"),
    ("ACTIVE", "EXPIRED"),
    ("BLOCKED", "EXPIRED"),
    ("SATISFIED", "ARCHIVED"),
    ("FAILED", "ARCHIVED"),
    ("CANCELLED", "ARCHIVED"),
    ("EXPIRED", "ARCHIVED"),
}


def test_exact_state_inventory_and_draft_only_creation_contract() -> None:
    expected = {
        "DRAFT",
        "ACTIVE",
        "BLOCKED",
        "SATISFIED",
        "FAILED",
        "CANCELLED",
        "EXPIRED",
        "ARCHIVED",
    }
    assert len(ObjectiveState) == 8
    assert set(ObjectiveState.__members__) == expected  # Includes aliases, if added.
    assert {state.value for state in ObjectiveState} == expected
    assert OBJECTIVE_CREATION_STATE is ObjectiveState.DRAFT
    assert "NONE" not in ObjectiveState.__members__
    with pytest.raises(ValueError):
        ObjectiveState("NONE")
    with pytest.raises(InvalidDomainValue):
        can_objective_transition(None, ObjectiveState.DRAFT)  # type: ignore[arg-type]


@pytest.mark.parametrize(("source", "target"), tuple(product(ObjectiveState, repeat=2)))
def test_every_state_pair_matches_the_closed_contract(
    source: ObjectiveState, target: ObjectiveState
) -> None:
    assert can_objective_transition(source, target) is (
        (source.value, target.value) in EXPECTED_EDGES
    )


def test_exactly_seventeen_state_edges() -> None:
    actual = {
        (source.value, target.value)
        for source, target in product(ObjectiveState, repeat=2)
        if can_objective_transition(source, target)
    }
    assert len(actual) == 17
    assert actual == EXPECTED_EDGES


@pytest.mark.parametrize("state", list(ObjectiveState))
def test_archived_is_a_sink_and_self_loops_are_forbidden(state: ObjectiveState) -> None:
    assert not can_objective_transition(ObjectiveState.ARCHIVED, state)
    assert not can_objective_transition(state, state)


@pytest.mark.parametrize("name", ["SATISFIED", "FAILED", "CANCELLED", "EXPIRED"])
def test_closed_objectives_have_only_the_archival_exit(name: str) -> None:
    source = ObjectiveState(name)
    exits = {
        target for target in ObjectiveState if can_objective_transition(source, target)
    }
    assert exits == {ObjectiveState.ARCHIVED}


@pytest.mark.parametrize(
    "invalid", ["ACTIVE", "DRAFT", "NONE", None, 1, ActorType.SYSTEM]
)
def test_queries_require_typed_states(invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        can_objective_transition(invalid, ObjectiveState.ACTIVE)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        can_objective_transition(ObjectiveState.ACTIVE, invalid)  # type: ignore[arg-type]
