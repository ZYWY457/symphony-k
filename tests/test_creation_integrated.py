"""Integrated constitutional properties of all eight authoritative creation paths.

No known requester, producer, proposer or observer may acquire creation authority
merely by ActorType relabeling, including Evaluation target producing principals.
"""

from dataclasses import dataclass, fields, replace

import pytest

from symphony_k.domain import (
    ActorType,
    CausationId,
    CreationContext,
    CreationRequest,
    CreationRequestVariant,
    DomainEntityType,
    DomainEventMetadata,
    DomainEventType,
    EffectState,
    EntityVersion,
    EvaluationState,
    EventId,
    InvalidDomainValue,
    InvalidTransition,
    InvariantViolation,
    ObjectiveState,
    OutcomeState,
    RunState,
    TaskState,
    TransitionContext,
    TransitionReason,
    TransitionRequest,
    UnauthorizedTransition,
    can_effect_transition,
    can_evaluation_transition,
    can_objective_transition,
    can_outcome_transition,
    can_run_transition,
    can_task_transition,
    create_entity,
    transition_entity,
)
from tests.test_creation_objective_task import objective_request, task_request
from tests.test_creation_observed_effect import observed_request
from tests.test_creation_planned_effect import CONTROLLER, planned_request
from tests.test_creation_protocol import (
    _AllowTransitionGuard,
    _with_substituted_spec_content,
)
from tests.test_creation_run_outcome_evaluation import (
    SCHEDULER,
    actor,
    context,
    evaluation_request,
    independent_evaluation_request,
    outcome_request,
    run_request,
    uid,
)


def requests() -> tuple[CreationRequest, ...]:
    return (
        objective_request(),
        task_request(),
        run_request(),
        outcome_request(),
        evaluation_request(),
        planned_request(),
        observed_request(),
        observed_request(True),
    )


def creation_context(request: CreationRequest) -> CreationContext:
    return context(
        request,
        CONTROLLER if request.entity_type is DomainEntityType.EFFECT else SCHEDULER,
    )


CASES = requests()
EXPECTED_EVENTS = (
    DomainEventType.OBJECTIVE_CREATED,
    DomainEventType.TASK_CREATED,
    DomainEventType.RUN_CREATED,
    DomainEventType.OUTCOME_PROPOSED,
    DomainEventType.EVALUATION_REQUESTED,
    DomainEventType.EFFECT_PLANNED,
    DomainEventType.EFFECT_COMMITTED,
    DomainEventType.EFFECT_QUARANTINED,
)
ELIGIBLE = {
    DomainEntityType.OBJECTIVE: {
        ActorType.REQUESTER,
        ActorType.SCHEDULER,
        ActorType.POLICY_ENGINE,
        ActorType.HUMAN_OPERATOR,
    },
    DomainEntityType.TASK: {
        ActorType.REQUESTER,
        ActorType.SCHEDULER,
        ActorType.POLICY_ENGINE,
        ActorType.HUMAN_OPERATOR,
    },
    DomainEntityType.RUN: {ActorType.SCHEDULER, ActorType.RUN_CONTROLLER},
    DomainEntityType.OUTCOME: {ActorType.SCHEDULER, ActorType.POLICY_ENGINE},
    DomainEntityType.EVALUATION: {ActorType.SCHEDULER, ActorType.EVALUATOR},
    DomainEntityType.EFFECT: {ActorType.EFFECT_CONTROLLER},
}


def test_exactly_eight_successful_creation_variants() -> None:
    assert len(CASES) == len(CreationRequestVariant) == 8
    assert {item.variant for item in CASES} == set(CreationRequestVariant)
    for request, expected_event in zip(CASES, EXPECTED_EVENTS, strict=True):
        result = create_entity(request, creation_context(request))
        assert result.entity.state is request.target_state
        assert result.entity.version == result.event.entity_version == EntityVersion(1)
        assert result.event.event_type is expected_event
        assert result.event.metadata.prior_state is None
        assert result.event.metadata.new_state is request.target_state
        assert result.request == request


@pytest.mark.parametrize("creation_request", CASES)
@pytest.mark.parametrize("role", list(ActorType))
def test_exact_creation_authority_matrices(
    creation_request: CreationRequest, role: ActorType
) -> None:
    authority = CONTROLLER if role is ActorType.EFFECT_CONTROLLER else actor(700, role)
    ctx = context(creation_request, authority)
    if role in ELIGIBLE[creation_request.entity_type]:
        assert create_entity(creation_request, ctx).event.actor == authority
    else:
        with pytest.raises(UnauthorizedTransition):
            create_entity(creation_request, ctx)


@pytest.mark.parametrize("creation_request", CASES)
def test_requester_relabel_cannot_acquire_creation_authority(
    creation_request: CreationRequest,
) -> None:
    request = creation_request
    role = (
        ActorType.EFFECT_CONTROLLER
        if request.entity_type is DomainEntityType.EFFECT
        else ActorType.SCHEDULER
    )
    relabelled = replace(request.requested_by, actor_type=role)
    with pytest.raises(UnauthorizedTransition, match="relabelling a principal"):
        create_entity(request, context(request, relabelled))


@pytest.mark.parametrize("kind", ["run", "outcome", "effect", "evidence"])
def test_evaluation_target_producer_is_inside_creation_authority_boundary(
    kind: str,
) -> None:
    request = independent_evaluation_request(kind)
    scope = request.semantic_input.validation
    assert scope is not None
    producer = scope.producing_principals[0]
    assert producer.actor_type is ActorType.WORKER
    assert request.requested_by.actor_id != producer.actor_id
    # Control: both eligible roles retain exact-scoped independent authority.
    for role in (ActorType.EVALUATOR, ActorType.SCHEDULER):
        independent = actor(701, role)
        result = create_entity(request, context(request, independent))
        assert result.event.actor == independent
        assert result.entity.state is EvaluationState.PENDING
        assert result.entity.version == result.event.entity_version == EntityVersion(1)
        assert result.event.event_type is DomainEventType.EVALUATION_REQUESTED
        assert result.event.metadata.prior_state is None
        relabelled = replace(producer, actor_type=role)
        with pytest.raises(UnauthorizedTransition, match="relabelling a principal"):
            create_entity(request, context(request, relabelled))
        # A caller cannot inject the same forged authority into a valid result.
        forged = context(request, relabelled).authority_decision
        assert forged is not None
        with pytest.raises(UnauthorizedTransition, match="relabelling a principal"):
            replace(
                result,
                authority_decision=forged,
                event=replace(result.event, actor=relabelled),
            )


@pytest.mark.parametrize("index", range(8))
def test_authority_and_availability_cannot_cross_requests(index: int) -> None:
    request, other = CASES[index], CASES[(index + 1) % 8]
    ctx, other_ctx = creation_context(request), creation_context(other)
    with pytest.raises(UnauthorizedTransition):
        create_entity(
            request, replace(ctx, authority_decision=other_ctx.authority_decision)
        )
    with pytest.raises(InvariantViolation):
        create_entity(
            request,
            replace(ctx, identifier_availability=other_ctx.identifier_availability),
        )


@dataclass(frozen=True)
class MustNotRun:
    def validate(self, request: CreationRequest) -> None:
        raise AssertionError("Additional guard ran before failed canonical semantics")


@pytest.mark.parametrize("creation_request", CASES)
def test_semantic_request_replay_fails_before_additional_guards(
    creation_request: CreationRequest,
) -> None:
    changed = replace(creation_request, causation_id=CausationId(uid(999)))
    ctx = replace(creation_context(changed), guards=(MustNotRun(),))
    with pytest.raises(InvariantViolation):
        create_entity(changed, ctx)


@pytest.mark.parametrize("creation_request", CASES)
@pytest.mark.parametrize("version", [0, 2])
def test_every_result_rejects_noninitial_snapshot_and_event_versions(
    creation_request: CreationRequest, version: int
) -> None:
    result = create_entity(creation_request, creation_context(creation_request))
    with pytest.raises(InvalidDomainValue):
        replace(result, entity=replace(result.entity, version=EntityVersion(version)))  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        replace(
            result, event=replace(result.event, entity_version=EntityVersion(version))
        )


@pytest.mark.parametrize("creation_request", CASES)
def test_old_event_cannot_be_replayed_under_changed_request(
    creation_request: CreationRequest,
) -> None:
    result = create_entity(creation_request, creation_context(creation_request))
    changed = replace(
        creation_request, reason=TransitionReason("Different request content")
    )
    with pytest.raises(InvalidDomainValue):
        replace(result, request=changed)
    with pytest.raises(InvalidDomainValue):
        replace(result, event=replace(result.event, event_id=EventId(uid(999))))


@pytest.mark.parametrize("creation_request", CASES)
def test_creation_has_no_source_or_expected_version_and_cannot_use_transition(
    creation_request: CreationRequest,
) -> None:
    request = creation_request
    assert not {
        "state",
        "version",
        "prior_state",
        "source",
        "expected_version",
    }.intersection(field.name for field in fields(request))
    result = create_entity(request, creation_context(request))
    transition = TransitionRequest(
        request.event_id,
        request.target_state,
        result.event.actor,
        request.reason,
        EntityVersion(1),
        request.timestamp,
        request.correlation_id,
        request.causation_id,
    )
    with pytest.raises(InvalidTransition):
        transition_entity(
            result.entity,  # type: ignore[arg-type]
            transition,  # type: ignore[arg-type]
            TransitionContext((_AllowTransitionGuard(),)),
        )


@pytest.mark.parametrize("index", range(8))
def test_event_family_and_prior_state_cannot_be_fabricated(index: int) -> None:
    request = CASES[index]
    result = create_entity(request, creation_context(request))
    with pytest.raises(InvalidDomainValue):
        replace(
            result,
            event=replace(result.event, event_type=EXPECTED_EVENTS[(index + 1) % 8]),
        )
    with pytest.raises(InvalidDomainValue):
        replace(
            result,
            event=replace(
                result.event,
                metadata=DomainEventMetadata(
                    request.target_state, request.target_state
                ),
            ),
        )


@pytest.mark.parametrize("creation_request", CASES)
def test_annotations_are_repeatable_unique_and_reference_only(
    creation_request: CreationRequest,
) -> None:
    first = create_entity(creation_request, creation_context(creation_request))
    second = create_entity(creation_request, creation_context(creation_request))
    assert first == second
    annotations = first.event.metadata.annotations
    assert len(dict(annotations)) == len(annotations)
    assert all(
        isinstance(key, str) and isinstance(value, str) and key and value
        for key, value in annotations
    )
    assert not {
        "metadata",
        "body",
        "evidence_body",
        "verdict",
        "authorized",
        "dispatch",
    }.intersection(dict(annotations))
    evidence = sorted(
        (key, value)
        for key, value in annotations
        if key.startswith("semantic_evidence_ref.")
    )
    assert [value for _, value in evidence] == sorted({value for _, value in evidence})


def test_all_43_states_and_91_noncreation_edges_preserved() -> None:
    states = (
        ObjectiveState,
        TaskState,
        RunState,
        OutcomeState,
        EvaluationState,
        EffectState,
    )
    assert sum(len(family) for family in states) == 43
    assert all("NONE" not in family.__members__ for family in states)
    counts = (
        sum(
            can_objective_transition(a, b)
            for a in ObjectiveState
            for b in ObjectiveState
        ),
        sum(can_task_transition(a, b) for a in TaskState for b in TaskState),
        sum(can_run_transition(a, b) for a in RunState for b in RunState),
        sum(can_outcome_transition(a, b) for a in OutcomeState for b in OutcomeState),
        sum(
            can_evaluation_transition(a, b)
            for a in EvaluationState
            for b in EvaluationState
        ),
        sum(can_effect_transition(a, b) for a in EffectState for b in EffectState),
    )
    assert counts == (17, 16, 18, 11, 10, 19)
    assert sum(counts) + len(CASES) == 99


@pytest.mark.parametrize("creation_request", CASES)
def test_all_result_specs_are_exact_bound(creation_request: CreationRequest) -> None:
    result = create_entity(creation_request, creation_context(creation_request))
    with pytest.raises(InvalidDomainValue):
        replace(result, entity=_with_substituted_spec_content(result.entity))  # type: ignore[arg-type]


@pytest.mark.parametrize("index", range(8))
def test_semantic_input_cannot_cross_entity_families(index: int) -> None:
    request = CASES[index]
    # Observed variants share a semantic type; their occurrence/target checks must
    # reject the cross-variant replay even with refreshed common authority.
    other = CASES[(index + 1) % 8]
    with pytest.raises((InvalidDomainValue, InvariantViolation)):
        changed = replace(request, semantic_input=other.semantic_input)  # type: ignore[arg-type]
        create_entity(changed, creation_context(changed))
