"""M7B2 canonical actor-type eligibility matrix conformance tests."""

from collections.abc import Callable
from typing import cast

import pytest

from symphony_k.domain import (
    EFFECT_CREATION_STATES,
    EVALUATION_CREATION_STATE,
    OBJECTIVE_CREATION_STATE,
    OUTCOME_CREATION_STATE,
    RUN_CREATION_STATE,
    TASK_CREATION_STATE,
    ActorType,
    DomainEntityType,
    EffectState,
    EvaluationState,
    ObjectiveState,
    OutcomeState,
    RunState,
    TaskState,
    can_effect_transition,
    can_evaluation_transition,
    can_objective_transition,
    can_outcome_transition,
    can_run_transition,
    can_task_transition,
    is_actor_eligible_for_transition_authority,
)
from symphony_k.domain.transition_engine import LifecycleState

type Edge = tuple[DomainEntityType, LifecycleState | None, LifecycleState]
type TopologyHelper = Callable[[LifecycleState, LifecycleState], bool]

OBJECTIVE_AUTHORITY = frozenset(
    {
        ActorType.REQUESTER,
        ActorType.SCHEDULER,
        ActorType.POLICY_ENGINE,
        ActorType.HUMAN_OPERATOR,
    }
)
TASK_AUTHORITY = OBJECTIVE_AUTHORITY
RUN_AUTHORITY = frozenset({ActorType.SCHEDULER, ActorType.RUN_CONTROLLER})
OUTCOME_AUTHORITY = frozenset({ActorType.SCHEDULER, ActorType.POLICY_ENGINE})
EFFECT_AUTHORITY = frozenset({ActorType.EFFECT_CONTROLLER})
EVALUATION_DECISION_AUTHORITY = frozenset(
    {ActorType.EVALUATOR, ActorType.ARBITRATOR, ActorType.HUMAN_OPERATOR}
)


def _family_edges[StateT: LifecycleState](
    entity_type: DomainEntityType,
    states: type[StateT],
    creation_targets: frozenset[StateT],
    helper: Callable[[StateT, StateT], bool],
) -> tuple[Edge, ...]:
    edges: list[Edge] = [(entity_type, None, target) for target in creation_targets]
    edges.extend(
        (entity_type, source, target)
        for source in states
        for target in states
        if helper(cast(StateT, source), cast(StateT, target))
    )
    return tuple(edges)


LEGAL_EDGES = (
    *_family_edges(
        DomainEntityType.OBJECTIVE,
        ObjectiveState,
        frozenset({OBJECTIVE_CREATION_STATE}),
        can_objective_transition,
    ),
    *_family_edges(
        DomainEntityType.TASK,
        TaskState,
        frozenset({TASK_CREATION_STATE}),
        can_task_transition,
    ),
    *_family_edges(
        DomainEntityType.RUN,
        RunState,
        frozenset({RUN_CREATION_STATE}),
        can_run_transition,
    ),
    *_family_edges(
        DomainEntityType.OUTCOME,
        OutcomeState,
        frozenset({OUTCOME_CREATION_STATE}),
        can_outcome_transition,
    ),
    *_family_edges(
        DomainEntityType.EVALUATION,
        EvaluationState,
        frozenset({EVALUATION_CREATION_STATE}),
        can_evaluation_transition,
    ),
    *_family_edges(
        DomainEntityType.EFFECT,
        EffectState,
        EFFECT_CREATION_STATES,
        can_effect_transition,
    ),
)


def _accepted_authority_for_edge(edge: Edge) -> frozenset[ActorType]:
    entity_type, source, target = edge
    if entity_type is DomainEntityType.OBJECTIVE:
        return OBJECTIVE_AUTHORITY
    if entity_type is DomainEntityType.TASK:
        return TASK_AUTHORITY
    if entity_type is DomainEntityType.RUN:
        return RUN_AUTHORITY
    if entity_type is DomainEntityType.OUTCOME:
        return OUTCOME_AUTHORITY
    if entity_type is DomainEntityType.EFFECT:
        return EFFECT_AUTHORITY

    assert isinstance(target, EvaluationState)
    if source is None:
        return frozenset({ActorType.SCHEDULER, ActorType.EVALUATOR})
    assert isinstance(source, EvaluationState)
    if (source, target) in {
        (EvaluationState.PENDING, EvaluationState.RUNNING),
        (EvaluationState.RUNNING, EvaluationState.COMPLETED),
    }:
        return frozenset({ActorType.EVALUATOR})
    if target is EvaluationState.CONFLICTED:
        return EVALUATION_DECISION_AUTHORITY
    if target is EvaluationState.ARBITRATED:
        return frozenset({ActorType.ARBITRATOR, ActorType.HUMAN_OPERATOR})
    assert target is EvaluationState.INVALID
    return EVALUATION_DECISION_AUTHORITY


@pytest.mark.parametrize("edge", LEGAL_EDGES)
def test_every_accepted_edge_has_exact_actor_type_eligibility(edge: Edge) -> None:
    entity_type, source, target = edge
    actual = frozenset(
        actor_type
        for actor_type in ActorType
        if is_actor_eligible_for_transition_authority(
            entity_type, source, target, actor_type
        )
    )
    assert actual == _accepted_authority_for_edge(edge)


def test_matrix_covers_accepted_43_states_and_99_edges_without_topology_drift() -> None:
    assert len(LEGAL_EDGES) == 99
    assert len(set(LEGAL_EDGES)) == 99
    assert (
        sum(
            len(states)
            for states in (
                ObjectiveState,
                TaskState,
                RunState,
                OutcomeState,
                EvaluationState,
                EffectState,
            )
        )
        == 43
    )


@pytest.mark.parametrize(
    ("entity_type", "states", "creation_targets", "helper"),
    [
        (
            DomainEntityType.OBJECTIVE,
            ObjectiveState,
            frozenset({OBJECTIVE_CREATION_STATE}),
            can_objective_transition,
        ),
        (
            DomainEntityType.TASK,
            TaskState,
            frozenset({TASK_CREATION_STATE}),
            can_task_transition,
        ),
        (
            DomainEntityType.RUN,
            RunState,
            frozenset({RUN_CREATION_STATE}),
            can_run_transition,
        ),
        (
            DomainEntityType.OUTCOME,
            OutcomeState,
            frozenset({OUTCOME_CREATION_STATE}),
            can_outcome_transition,
        ),
        (
            DomainEntityType.EVALUATION,
            EvaluationState,
            frozenset({EVALUATION_CREATION_STATE}),
            can_evaluation_transition,
        ),
        (
            DomainEntityType.EFFECT,
            EffectState,
            EFFECT_CREATION_STATES,
            can_effect_transition,
        ),
    ],
)
def test_illegal_edges_receive_no_actor_eligibility(
    entity_type: DomainEntityType,
    states: type[LifecycleState],
    creation_targets: frozenset[LifecycleState],
    helper: TopologyHelper,
) -> None:
    for target in states:
        if target not in creation_targets:
            assert not any(
                is_actor_eligible_for_transition_authority(
                    entity_type, None, target, actor_type
                )
                for actor_type in ActorType
            )
        for source in states:
            if not helper(source, target):
                assert not any(
                    is_actor_eligible_for_transition_authority(
                        entity_type, source, target, actor_type
                    )
                    for actor_type in ActorType
                )


@pytest.mark.parametrize("actor_type", [ActorType.WORKER, ActorType.SYSTEM])
def test_worker_and_system_have_no_direct_lifecycle_authority(
    actor_type: ActorType,
) -> None:
    assert not any(
        is_actor_eligible_for_transition_authority(*edge, actor_type)
        for edge in LEGAL_EDGES
    )


def test_human_operator_is_scoped_rather_than_universal() -> None:
    eligible_families = {
        entity_type
        for entity_type, source, target in LEGAL_EDGES
        if is_actor_eligible_for_transition_authority(
            entity_type, source, target, ActorType.HUMAN_OPERATOR
        )
    }
    assert eligible_families == {
        DomainEntityType.OBJECTIVE,
        DomainEntityType.TASK,
        DomainEntityType.EVALUATION,
    }


def test_cross_family_and_raw_values_are_never_eligible() -> None:
    assert not is_actor_eligible_for_transition_authority(
        DomainEntityType.RUN,
        ObjectiveState.DRAFT,
        RunState.RUNNING,
        ActorType.SCHEDULER,
    )
    assert not is_actor_eligible_for_transition_authority(
        DomainEntityType.RUN,
        RunState.PENDING,
        ObjectiveState.ACTIVE,
        ActorType.SCHEDULER,
    )
    assert not is_actor_eligible_for_transition_authority(
        "RUN",  # type: ignore[arg-type]
        RunState.PENDING,
        RunState.RUNNING,
        ActorType.SCHEDULER,
    )
    assert not is_actor_eligible_for_transition_authority(
        DomainEntityType.RUN,
        RunState.PENDING,
        RunState.RUNNING,
        "SCHEDULER",  # type: ignore[arg-type]
    )
