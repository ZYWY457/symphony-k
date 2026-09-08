"""Independent oracle for Effect topology, not transition execution."""

from itertools import product

import pytest

import symphony_k.domain as domain
from symphony_k.domain import (
    EFFECT_CREATION_STATES,
    EffectState,
    InvalidDomainValue,
    OutcomeState,
    can_effect_transition,
)

EXPECTED_EDGES = {
    ("PLANNED", "SIMULATED"),
    ("PLANNED", "PENDING_COMMIT"),
    ("SIMULATED", "PENDING_COMMIT"),
    ("PLANNED", "COMMITTED"),
    ("SIMULATED", "COMMITTED"),
    ("PLANNED", "QUARANTINED"),
    ("SIMULATED", "QUARANTINED"),
    ("PENDING_COMMIT", "COMMITTED"),
    ("PENDING_COMMIT", "QUARANTINED"),
    ("COMMITTED", "ROLLED_BACK"),
    ("COMMITTED", "COMPENSATING"),
    ("COMMITTED", "QUARANTINED"),
    ("COMPENSATING", "COMPENSATED"),
    ("COMPENSATING", "QUARANTINED"),
    ("QUARANTINED", "PENDING_COMMIT"),
    ("QUARANTINED", "COMMITTED"),
    ("QUARANTINED", "ROLLED_BACK"),
    ("QUARANTINED", "COMPENSATING"),
    ("QUARANTINED", "COMPENSATED"),
}


def test_exact_state_inventory_and_three_creation_destinations() -> None:
    expected_states = {
        "PLANNED",
        "SIMULATED",
        "PENDING_COMMIT",
        "COMMITTED",
        "ROLLED_BACK",
        "COMPENSATING",
        "COMPENSATED",
        "QUARANTINED",
    }
    assert len(EffectState) == 8
    assert set(EffectState.__members__) == expected_states
    assert {state.value for state in EffectState} == expected_states
    assert EFFECT_CREATION_STATES == frozenset(
        {EffectState.PLANNED, EffectState.COMMITTED, EffectState.QUARANTINED}
    )
    assert len(EFFECT_CREATION_STATES) == 3
    assert not hasattr(domain, "EFFECT_CREATION_STATE")
    for invalid in ("NONE", "FAILED", "CANCELLED", "UNAUTHORIZED"):
        with pytest.raises(ValueError):
            EffectState(invalid)


@pytest.mark.parametrize(("source", "target"), tuple(product(EffectState, repeat=2)))
def test_all_sixty_four_state_pairs(source: EffectState, target: EffectState) -> None:
    assert can_effect_transition(source, target) is (
        (source.value, target.value) in EXPECTED_EDGES
    )


def test_exact_edge_counts_and_strict_sinks() -> None:
    actual = {
        (source.value, target.value)
        for source, target in product(EffectState, repeat=2)
        if can_effect_transition(source, target)
    }
    assert actual == EXPECTED_EDGES
    assert len(actual) == 19
    assert len(actual) + len(EFFECT_CREATION_STATES) == 22
    assert {
        source
        for source in EffectState
        if not any(can_effect_transition(source, target) for target in EffectState)
    } == {EffectState.ROLLED_BACK, EffectState.COMPENSATED}


@pytest.mark.parametrize("state", list(EffectState))
def test_self_loops_and_sink_exits_are_forbidden(state: EffectState) -> None:
    assert not can_effect_transition(state, state)
    assert not can_effect_transition(EffectState.ROLLED_BACK, state)
    assert not can_effect_transition(EffectState.COMPENSATED, state)


def test_commit_quarantine_rollback_and_compensation_remain_distinct() -> None:
    committed_exits = {
        target
        for target in EffectState
        if can_effect_transition(EffectState.COMMITTED, target)
    }
    assert committed_exits == {
        EffectState.ROLLED_BACK,
        EffectState.COMPENSATING,
        EffectState.QUARANTINED,
    }
    assert any(
        can_effect_transition(EffectState.QUARANTINED, target) for target in EffectState
    )
    assert not can_effect_transition(EffectState.COMMITTED, EffectState.COMPENSATED)
    assert not can_effect_transition(EffectState.COMPENSATED, EffectState.ROLLED_BACK)
    assert not can_effect_transition(EffectState.COMMITTED, EffectState.PLANNED)


@pytest.mark.parametrize("invalid", ["PLANNED", "NONE", None, 1, OutcomeState.PROPOSED])
def test_queries_require_effect_states(invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        can_effect_transition(invalid, EffectState.COMMITTED)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        can_effect_transition(EffectState.PLANNED, invalid)  # type: ignore[arg-type]
