from dataclasses import dataclass, fields, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CausationId,
    CompletionPolicyRef,
    CorrelationId,
    CreationAuthorityDecision,
    CreationAuthorityDecisionId,
    CreationAuthorityStatus,
    CreationContext,
    CreationRequest,
    CreationResult,
    CreationSemanticDecisionStatus,
    DomainEntityType,
    DomainEventType,
    EntityNotFound,
    EntityVersion,
    EventId,
    EvidenceRef,
    IdentifierAvailability,
    IdentifierAvailabilityId,
    IdentifierAvailabilityStatus,
    InvalidDomainValue,
    InvalidRelationship,
    InvariantViolation,
    Objective,
    ObjectiveAcceptanceBindingDecision,
    ObjectiveBoundedGoalDecision,
    ObjectiveCreationCompletionPolicyDecision,
    ObjectiveCreationDecisionRef,
    ObjectiveCreationSemanticInput,
    ObjectiveCreationSpec,
    ObjectiveDraftCreationRequest,
    ObjectiveId,
    ObjectiveState,
    Task,
    TaskBoundedDefinitionDecision,
    TaskCreationCompletionPolicyDecision,
    TaskCreationDecisionRef,
    TaskCreationSemanticInput,
    TaskCreationSpec,
    TaskDraftCreationRequest,
    TaskId,
    TaskObjectiveObservation,
    TaskObjectiveObservationRef,
    TaskObjectiveObservationStatus,
    TaskObjectiveRelationship,
    TaskState,
    Timestamp,
    TransitionReason,
    create_entity,
)


def uid(value: int) -> UUID:
    return UUID(int=value)


def actor(value: int, actor_type: ActorType) -> ActorIdentity:
    return ActorIdentity(ActorId(uid(value)), actor_type)


NOW = Timestamp(datetime(2026, 9, 14, tzinfo=UTC))
REQUESTER = actor(10, ActorType.REQUESTER)
SEMANTIC_DECIDER = actor(11, ActorType.POLICY_ENGINE)
RELATIONSHIP_OBSERVER = actor(12, ActorType.SCHEDULER)
AUTHORITY = actor(13, ActorType.SCHEDULER)
APPLYING_SERVICE = actor(14, ActorType.SYSTEM)
AVAILABILITY_OBSERVER = actor(15, ActorType.SCHEDULER)


def objective_request(
    *,
    bounded_status: CreationSemanticDecisionStatus = (
        CreationSemanticDecisionStatus.PASSED
    ),
    acceptance_status: CreationSemanticDecisionStatus = (
        CreationSemanticDecisionStatus.PASSED
    ),
    completion_status: CreationSemanticDecisionStatus = (
        CreationSemanticDecisionStatus.PASSED
    ),
) -> ObjectiveDraftCreationRequest:
    objective_id = ObjectiveId(uid(100))
    correlation_id = CorrelationId(uid(101))
    causation_id = CausationId(uid(102))
    spec = ObjectiveCreationSpec(
        "Restore one bounded payment path",
        ("A deterministic acceptance check passes",),
        actor(16, ActorType.HUMAN_OPERATOR),
        CompletionPolicyRef("objective-policy", "1"),
        NOW,
    )
    bounded = ObjectiveBoundedGoalDecision(
        ObjectiveCreationDecisionRef("decision:objective:bounded"),
        bounded_status,
        SEMANTIC_DECIDER,
        frozenset({EvidenceRef("evidence:bounded-goal")}),
        objective_id,
        spec.goal,
        causation_id,
        correlation_id,
    )
    acceptance = ObjectiveAcceptanceBindingDecision(
        ObjectiveCreationDecisionRef("decision:objective:acceptance"),
        acceptance_status,
        SEMANTIC_DECIDER,
        frozenset({EvidenceRef("evidence:acceptance-binding")}),
        objective_id,
        spec.goal,
        spec.acceptance_criteria,
        spec.acceptance_authority,
        causation_id,
        correlation_id,
    )
    completion = ObjectiveCreationCompletionPolicyDecision(
        ObjectiveCreationDecisionRef("decision:objective:completion"),
        completion_status,
        SEMANTIC_DECIDER,
        frozenset({EvidenceRef("evidence:completion-policy")}),
        objective_id,
        spec.completion_policy_ref,
        causation_id,
        correlation_id,
    )
    return ObjectiveDraftCreationRequest(
        EventId(uid(103)),
        objective_id,
        REQUESTER,
        TransitionReason("Register bounded Objective"),
        NOW,
        correlation_id,
        causation_id,
        spec,
        ObjectiveCreationSemanticInput(
            CausationId(uid(104)), bounded, acceptance, completion
        ),
    )


def task_request(
    *,
    definition_status: CreationSemanticDecisionStatus = (
        CreationSemanticDecisionStatus.PASSED
    ),
    completion_status: CreationSemanticDecisionStatus = (
        CreationSemanticDecisionStatus.PASSED
    ),
    primary_status: TaskObjectiveObservationStatus = (
        TaskObjectiveObservationStatus.CURRENT
    ),
    primary_state: ObjectiveState | None = ObjectiveState.DRAFT,
    contribution_status: TaskObjectiveObservationStatus = (
        TaskObjectiveObservationStatus.CURRENT
    ),
) -> TaskDraftCreationRequest:
    task_id = TaskId(uid(200))
    primary_id = ObjectiveId(uid(201))
    contribution_ids = frozenset({ObjectiveId(uid(203)), ObjectiveId(uid(202))})
    correlation_id = CorrelationId(uid(204))
    causation_id = CausationId(uid(205))
    spec = TaskCreationSpec(
        "Repair the bounded payment retry worker",
        primary_id,
        CompletionPolicyRef("task-policy", "1"),
        contribution_ids,
    )
    definition = TaskBoundedDefinitionDecision(
        TaskCreationDecisionRef("decision:task:definition"),
        definition_status,
        SEMANTIC_DECIDER,
        frozenset({EvidenceRef("evidence:task-definition")}),
        task_id,
        spec.definition,
        causation_id,
        correlation_id,
    )
    completion = TaskCreationCompletionPolicyDecision(
        TaskCreationDecisionRef("decision:task:completion"),
        completion_status,
        SEMANTIC_DECIDER,
        frozenset({EvidenceRef("evidence:task-policy")}),
        task_id,
        spec.completion_policy_ref,
        causation_id,
        correlation_id,
    )

    def observation(
        objective_id: ObjectiveId,
        relationship: TaskObjectiveRelationship,
        status: TaskObjectiveObservationStatus,
        version: int,
        state: ObjectiveState | None,
    ) -> TaskObjectiveObservation:
        has_snapshot = status in {
            TaskObjectiveObservationStatus.CURRENT,
            TaskObjectiveObservationStatus.STALE,
        }
        return TaskObjectiveObservation(
            TaskObjectiveObservationRef(f"observation:{objective_id}"),
            status,
            RELATIONSHIP_OBSERVER,
            NOW,
            frozenset({EvidenceRef(f"evidence:objective:{objective_id}")}),
            task_id,
            objective_id,
            relationship,
            causation_id,
            correlation_id,
            EntityVersion(version) if has_snapshot else None,
            state if has_snapshot else None,
        )

    observations = (
        observation(
            primary_id,
            TaskObjectiveRelationship.PRIMARY,
            primary_status,
            4,
            primary_state,
        ),
        *(
            observation(
                objective_id,
                TaskObjectiveRelationship.CONTRIBUTION,
                contribution_status,
                index + 7,
                ObjectiveState.ACTIVE,
            )
            for index, objective_id in enumerate(sorted(contribution_ids, key=str))
        ),
    )
    return TaskDraftCreationRequest(
        EventId(uid(206)),
        task_id,
        REQUESTER,
        TransitionReason("Register bounded Task"),
        NOW,
        correlation_id,
        causation_id,
        spec,
        TaskCreationSemanticInput(
            CausationId(uid(207)), definition, completion, observations
        ),
    )


def context(
    request: ObjectiveDraftCreationRequest | TaskDraftCreationRequest,
    *,
    decided_by: ActorIdentity = AUTHORITY,
) -> CreationContext:
    authority = CreationAuthorityDecision(
        CreationAuthorityDecisionId(uid(300)),
        request.scope,
        decided_by,
        CreationAuthorityStatus.AUTHORIZED,
        (CausationId(uid(301)), CausationId(uid(302))),
        NOW,
    )
    availability = IdentifierAvailability(
        IdentifierAvailabilityId(uid(303)),
        request.scope,
        request.entity_type,
        request.entity_id,
        IdentifierAvailabilityStatus.AVAILABLE,
        AVAILABILITY_OBSERVER,
        NOW,
        request.correlation_id,
    )
    return CreationContext(authority, availability, APPLYING_SERVICE)


def annotations(
    result: CreationResult[Objective] | CreationResult[Task],
) -> dict[str, str]:
    return dict(result.event.metadata.annotations)


def replace_task_observation(
    request: TaskDraftCreationRequest,
    index: int,
    **changes: object,
) -> TaskDraftCreationRequest:
    observations = request.semantic_input.objective_observations
    assert observations is not None
    updated = list(observations)
    updated[index] = replace(updated[index], **changes)  # type: ignore[arg-type]
    return replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            objective_observations=tuple(updated),
        ),
    )


def test_objective_creation_returns_exact_snapshot_event_and_annotations() -> None:
    request = objective_request()
    result = create_entity(request, context(request))

    assert result.entity == Objective(
        request.entity_id,
        ObjectiveState.DRAFT,
        EntityVersion(1),
        request.entity_spec.goal,
        request.entity_spec.acceptance_criteria,
        request.entity_spec.acceptance_authority,
        request.entity_spec.completion_policy_ref,
        request.entity_spec.valid_until,
    )
    assert result.event.event_type is DomainEventType.OBJECTIVE_CREATED
    assert result.event.entity_type is DomainEntityType.OBJECTIVE
    assert result.event.entity_id == request.entity_id
    assert result.event.entity_version == EntityVersion(1)
    assert result.event.actor == AUTHORITY
    assert result.event.timestamp == request.timestamp
    assert result.event.correlation_id == request.correlation_id
    assert result.event.causation_id == request.causation_id
    assert result.event.reason == request.reason
    assert result.event.metadata.prior_state is None
    assert result.event.metadata.new_state is ObjectiveState.DRAFT
    assert annotations(result) == {
        "requested_by.actor_id": str(REQUESTER.actor_id),
        "requested_by.actor_type": "REQUESTER",
        "applying_service.actor_id": str(APPLYING_SERVICE.actor_id),
        "applying_service.actor_type": "SYSTEM",
        "creation_authority_decision_ref": str(uid(300)),
        "identifier_availability_ref": str(uid(303)),
        "semantic_provenance_ref": str(uid(104)),
        "authority_policy_or_grant_ref.0000": str(uid(301)),
        "authority_policy_or_grant_ref.0001": str(uid(302)),
        "bounded_goal_decision_ref": "decision:objective:bounded",
        "acceptance_binding_decision_ref": "decision:objective:acceptance",
        "completion_policy_decision_ref": "decision:objective:completion",
        "semantic_evidence_ref.0000": "evidence:acceptance-binding",
        "semantic_evidence_ref.0001": "evidence:bounded-goal",
        "semantic_evidence_ref.0002": "evidence:completion-policy",
    }


@pytest.mark.parametrize(
    "actor_type",
    [
        ActorType.REQUESTER,
        ActorType.SCHEDULER,
        ActorType.POLICY_ENGINE,
        ActorType.HUMAN_OPERATOR,
    ],
)
def test_all_eligible_objective_creation_authorities_succeed(
    actor_type: ActorType,
) -> None:
    request = objective_request()
    decision_actor = actor(400 + list(ActorType).index(actor_type), actor_type)
    result = create_entity(request, context(request, decided_by=decision_actor))
    assert result.event.actor == decision_actor


def test_objective_valid_until_is_preserved_exactly() -> None:
    request = objective_request()
    result = create_entity(request, context(request))
    assert result.entity.valid_until is NOW


@pytest.mark.parametrize(
    "field,value",
    [
        ("objective_id", ObjectiveId(uid(900))),
        ("goal", "Substituted bounded goal"),
        ("request_causation_id", CausationId(uid(901))),
        ("correlation_id", CorrelationId(uid(902))),
    ],
)
def test_bounded_goal_each_exact_binding_rejects_substitution(
    field: str, value: object
) -> None:
    request = objective_request()
    bounded = request.semantic_input.bounded_goal
    assert bounded is not None
    substituted = replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            bounded_goal=replace(bounded, **{field: value}),  # type: ignore[arg-type]
        ),
    )
    with pytest.raises(InvariantViolation, match="Bounded-goal.*exact-bind"):
        create_entity(substituted, context(substituted))


@pytest.mark.parametrize(
    "field,value",
    [
        ("objective_id", ObjectiveId(uid(904))),
        ("goal", "Substituted acceptance goal"),
        ("acceptance_criteria", ("Substituted criterion",)),
        ("acceptance_authority", actor(903, ActorType.HUMAN_OPERATOR)),
        ("request_causation_id", CausationId(uid(905))),
        ("correlation_id", CorrelationId(uid(906))),
    ],
)
def test_acceptance_definition_each_exact_binding_rejects_substitution(
    field: str, value: object
) -> None:
    request = objective_request()
    acceptance = request.semantic_input.acceptance_binding
    assert acceptance is not None
    substituted = replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            acceptance_binding=replace(
                acceptance,
                **{field: value},  # type: ignore[arg-type]
            ),
        ),
    )
    with pytest.raises(InvariantViolation, match="Acceptance-binding.*exact-bind"):
        create_entity(substituted, context(substituted))


def test_acceptance_binding_rejects_malformed_goal() -> None:
    request = objective_request()
    acceptance = request.semantic_input.acceptance_binding
    assert acceptance is not None
    with pytest.raises(InvalidDomainValue, match="goal"):
        replace(acceptance, goal="   ")


def test_objective_completion_policy_substitution_is_rejected() -> None:
    request = objective_request()
    completion = request.semantic_input.completion_policy
    assert completion is not None
    substituted = replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            completion_policy=replace(
                completion,
                completion_policy_ref=CompletionPolicyRef("other-policy", "1"),
            ),
        ),
    )
    with pytest.raises(InvariantViolation, match="Completion-policy.*exact-bind"):
        create_entity(substituted, context(substituted))


def test_objective_semantic_decisions_cannot_replay_across_definitions() -> None:
    original = objective_request()
    new_goal = "A different bounded goal"
    bounded = original.semantic_input.bounded_goal
    assert bounded is not None
    replay_target = replace(
        original,
        entity_spec=replace(original.entity_spec, goal=new_goal),
        semantic_input=replace(
            original.semantic_input,
            bounded_goal=replace(bounded, goal=new_goal),
        ),
    )
    with pytest.raises(InvariantViolation, match="Acceptance-binding.*exact-bind"):
        create_entity(replay_target, context(replay_target))


def test_task_creation_accepts_current_draft_primary_and_exact_annotations() -> None:
    request = task_request(primary_state=ObjectiveState.DRAFT)
    result = create_entity(request, context(request))

    assert result.entity == Task(
        request.entity_id,
        TaskState.DRAFT,
        EntityVersion(1),
        request.entity_spec.definition,
        request.entity_spec.primary_objective_id,
        request.entity_spec.completion_policy_ref,
        request.entity_spec.contributes_to,
    )
    assert result.event.event_type is DomainEventType.TASK_CREATED
    assert result.event.entity_type is DomainEntityType.TASK
    assert result.event.entity_id == request.entity_id
    assert result.event.entity_version == EntityVersion(1)
    assert result.event.actor == AUTHORITY
    assert result.event.timestamp == request.timestamp
    assert result.event.correlation_id == request.correlation_id
    assert result.event.causation_id == request.causation_id
    assert result.event.reason == request.reason
    assert result.event.metadata.prior_state is None
    assert result.event.metadata.new_state is TaskState.DRAFT
    assert annotations(result) == {
        "requested_by.actor_id": str(REQUESTER.actor_id),
        "requested_by.actor_type": "REQUESTER",
        "applying_service.actor_id": str(APPLYING_SERVICE.actor_id),
        "applying_service.actor_type": "SYSTEM",
        "creation_authority_decision_ref": str(uid(300)),
        "identifier_availability_ref": str(uid(303)),
        "semantic_provenance_ref": str(uid(207)),
        "authority_policy_or_grant_ref.0000": str(uid(301)),
        "authority_policy_or_grant_ref.0001": str(uid(302)),
        "definition_decision_ref": "decision:task:definition",
        "completion_policy_decision_ref": "decision:task:completion",
        "primary_objective_observation_ref": (f"observation:{ObjectiveId(uid(201))}"),
        "primary_objective_observed_version": "4",
        "contribution_objective.0000.id": str(ObjectiveId(uid(202))),
        "contribution_objective.0000.observation_ref": (
            f"observation:{ObjectiveId(uid(202))}"
        ),
        "contribution_objective.0000.observed_version": "7",
        "contribution_objective.0001.id": str(ObjectiveId(uid(203))),
        "contribution_objective.0001.observation_ref": (
            f"observation:{ObjectiveId(uid(203))}"
        ),
        "contribution_objective.0001.observed_version": "8",
        "semantic_evidence_ref.0000": (f"evidence:objective:{ObjectiveId(uid(201))}"),
        "semantic_evidence_ref.0001": (f"evidence:objective:{ObjectiveId(uid(202))}"),
        "semantic_evidence_ref.0002": (f"evidence:objective:{ObjectiveId(uid(203))}"),
        "semantic_evidence_ref.0003": "evidence:task-definition",
        "semantic_evidence_ref.0004": "evidence:task-policy",
    }


def test_task_creation_accepts_current_active_primary_without_state_propagation() -> (
    None
):
    request = task_request(primary_state=ObjectiveState.ACTIVE)
    result = create_entity(request, context(request))
    assert result.entity.state is TaskState.DRAFT
    assert "observed_state" not in {field.name for field in fields(result.entity)}
    assert all("state" not in key for key in annotations(result))


@pytest.mark.parametrize(
    "actor_type",
    [
        ActorType.REQUESTER,
        ActorType.SCHEDULER,
        ActorType.POLICY_ENGINE,
        ActorType.HUMAN_OPERATOR,
    ],
)
def test_all_eligible_task_creation_authorities_succeed(actor_type: ActorType) -> None:
    request = task_request()
    decision_actor = actor(500 + list(ActorType).index(actor_type), actor_type)
    result = create_entity(request, context(request, decided_by=decision_actor))
    assert result.event.actor == decision_actor


def test_objective_relationship_observer_grants_no_task_authority() -> None:
    request = task_request()
    result = create_entity(request, context(request))
    assert result.event.actor == AUTHORITY
    assert result.event.actor != RELATIONSHIP_OBSERVER
    assert result.entity.state is TaskState.DRAFT


@pytest.mark.parametrize(
    "field,status",
    [
        ("bounded_goal", CreationSemanticDecisionStatus.REJECTED),
        ("bounded_goal", CreationSemanticDecisionStatus.UNRESOLVED),
        ("acceptance_binding", CreationSemanticDecisionStatus.REJECTED),
        ("acceptance_binding", CreationSemanticDecisionStatus.UNRESOLVED),
        ("completion_policy", CreationSemanticDecisionStatus.REJECTED),
        ("completion_policy", CreationSemanticDecisionStatus.UNRESOLVED),
    ],
)
def test_objective_rejected_and_unresolved_decisions_fail_closed(
    field: str, status: CreationSemanticDecisionStatus
) -> None:
    request = objective_request()
    decision = getattr(request.semantic_input, field)
    substituted = replace(
        request,
        semantic_input=replace(
            request.semantic_input, **{field: replace(decision, status=status)}
        ),
    )
    with pytest.raises(InvariantViolation, match=status.value):
        create_entity(substituted, context(substituted))


@pytest.mark.parametrize(
    "field", ["bounded_goal", "acceptance_binding", "completion_policy"]
)
def test_objective_semantic_scope_substitution_is_rejected(field: str) -> None:
    request = objective_request()
    decision = getattr(request.semantic_input, field)
    substituted = replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            **{field: replace(decision, request_causation_id=CausationId(uid(999)))},
        ),
    )
    with pytest.raises(InvariantViolation, match="exact-bind"):
        create_entity(substituted, context(substituted))


@pytest.mark.parametrize(
    "definition_status,completion_status",
    [
        (
            CreationSemanticDecisionStatus.REJECTED,
            CreationSemanticDecisionStatus.PASSED,
        ),
        (
            CreationSemanticDecisionStatus.UNRESOLVED,
            CreationSemanticDecisionStatus.PASSED,
        ),
        (
            CreationSemanticDecisionStatus.PASSED,
            CreationSemanticDecisionStatus.REJECTED,
        ),
        (
            CreationSemanticDecisionStatus.PASSED,
            CreationSemanticDecisionStatus.UNRESOLVED,
        ),
    ],
)
def test_task_rejected_and_unresolved_decisions_fail_closed(
    definition_status: CreationSemanticDecisionStatus,
    completion_status: CreationSemanticDecisionStatus,
) -> None:
    request = task_request(
        definition_status=definition_status, completion_status=completion_status
    )
    with pytest.raises(InvariantViolation, match="Creation semantic condition"):
        create_entity(request, context(request))


def test_task_relationship_observation_set_must_exactly_match_request() -> None:
    request = task_request()
    observations = request.semantic_input.objective_observations
    assert observations is not None
    substituted = replace(
        request,
        semantic_input=replace(
            request.semantic_input, objective_observations=observations[:-1]
        ),
    )
    with pytest.raises(InvalidRelationship, match="exactly equal"):
        create_entity(substituted, context(substituted))


def test_task_relationship_role_substitution_is_rejected() -> None:
    request = task_request()
    observations = request.semantic_input.objective_observations
    assert observations is not None
    substituted = replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            objective_observations=(
                replace(
                    observations[0],
                    relationship=TaskObjectiveRelationship.CONTRIBUTION,
                ),
                *observations[1:],
            ),
        ),
    )
    with pytest.raises(InvalidRelationship, match="exactly equal"):
        create_entity(substituted, context(substituted))


def test_missing_primary_objective_raises_entity_not_found() -> None:
    request = task_request(
        primary_status=TaskObjectiveObservationStatus.MISSING, primary_state=None
    )
    with pytest.raises(EntityNotFound, match="missing"):
        create_entity(request, context(request))


@pytest.mark.parametrize(
    "status,error_type",
    [
        (TaskObjectiveObservationStatus.MISSING, EntityNotFound),
        (TaskObjectiveObservationStatus.STALE, InvariantViolation),
        (TaskObjectiveObservationStatus.UNRESOLVED, InvariantViolation),
    ],
)
def test_each_noncurrent_primary_observation_fails_closed(
    status: TaskObjectiveObservationStatus,
    error_type: type[Exception],
) -> None:
    request = task_request()
    has_snapshot = status is TaskObjectiveObservationStatus.STALE
    substituted = replace_task_observation(
        request,
        0,
        status=status,
        observed_entity_version=EntityVersion(4) if has_snapshot else None,
        observed_state=ObjectiveState.DRAFT if has_snapshot else None,
    )
    with pytest.raises(
        error_type,
        match=status.value.lower()
        if status is TaskObjectiveObservationStatus.MISSING
        else status.value,
    ):
        create_entity(substituted, context(substituted))


@pytest.mark.parametrize(
    "status,error_type",
    [
        (TaskObjectiveObservationStatus.MISSING, EntityNotFound),
        (TaskObjectiveObservationStatus.STALE, InvariantViolation),
        (TaskObjectiveObservationStatus.UNRESOLVED, InvariantViolation),
    ],
)
def test_each_noncurrent_contribution_observation_fails_closed(
    status: TaskObjectiveObservationStatus,
    error_type: type[Exception],
) -> None:
    request = task_request()
    has_snapshot = status is TaskObjectiveObservationStatus.STALE
    substituted = replace_task_observation(
        request,
        1,
        status=status,
        observed_entity_version=EntityVersion(7) if has_snapshot else None,
        observed_state=ObjectiveState.ACTIVE if has_snapshot else None,
    )
    with pytest.raises(
        error_type,
        match=status.value.lower()
        if status is TaskObjectiveObservationStatus.MISSING
        else status.value,
    ):
        create_entity(substituted, context(substituted))


@pytest.mark.parametrize(
    "field,value",
    [
        ("task_id", TaskId(uid(910))),
        ("request_causation_id", CausationId(uid(911))),
        ("correlation_id", CorrelationId(uid(912))),
    ],
)
def test_task_observation_each_request_binding_rejects_substitution(
    field: str, value: object
) -> None:
    request = task_request()
    substituted = replace_task_observation(request, 0, **{field: value})
    with pytest.raises(InvalidRelationship, match="exact-bind"):
        create_entity(substituted, context(substituted))


def test_wrong_primary_objective_is_rejected() -> None:
    request = task_request()
    substituted = replace_task_observation(
        request,
        0,
        objective_id=ObjectiveId(uid(913)),
    )
    with pytest.raises(InvalidRelationship, match="exactly equal"):
        create_entity(substituted, context(substituted))


def test_extra_contribution_observation_is_rejected() -> None:
    request = task_request()
    observations = request.semantic_input.objective_observations
    assert observations is not None
    extra = replace(
        observations[1],
        observation_ref=TaskObjectiveObservationRef("observation:extra"),
        objective_id=ObjectiveId(uid(914)),
    )
    substituted = replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            objective_observations=(*observations, extra),
        ),
    )
    with pytest.raises(InvalidRelationship, match="exactly equal"):
        create_entity(substituted, context(substituted))


def test_duplicate_relationship_observation_is_rejected() -> None:
    request = task_request()
    observations = request.semantic_input.objective_observations
    assert observations is not None
    substituted = replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            objective_observations=(*observations, observations[1]),
        ),
    )
    with pytest.raises(InvalidRelationship, match="exactly equal"):
        create_entity(substituted, context(substituted))


def test_requester_actor_id_cannot_be_relabelled_as_relationship_observer() -> None:
    request = task_request()
    substituted = replace_task_observation(
        request,
        0,
        observed_by=ActorIdentity(REQUESTER.actor_id, ActorType.SCHEDULER),
    )
    with pytest.raises(InvariantViolation, match="relabel the requester"):
        create_entity(substituted, context(substituted))


def test_task_spec_rejects_primary_duplicated_as_contribution() -> None:
    with pytest.raises(InvalidDomainValue, match="cannot also be a contribution"):
        TaskCreationSpec(
            "Bounded definition",
            ObjectiveId(uid(915)),
            CompletionPolicyRef("task-policy", "1"),
            frozenset({ObjectiveId(uid(915))}),
        )


def test_task_observation_retains_typed_observed_at() -> None:
    request = task_request()
    observations = request.semantic_input.objective_observations
    assert observations is not None
    assert all(observation.observed_at is NOW for observation in observations)


def test_task_observation_rejects_malformed_observed_at() -> None:
    request = task_request()
    observations = request.semantic_input.objective_observations
    assert observations is not None
    with pytest.raises(InvalidDomainValue, match="observed_at must be a Timestamp"):
        replace(
            observations[0],
            observed_at="2026-09-14T00:00:00Z",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "status",
    [
        TaskObjectiveObservationStatus.MISSING,
        TaskObjectiveObservationStatus.UNRESOLVED,
    ],
)
def test_missing_and_unresolved_observations_cannot_fabricate_snapshot(
    status: TaskObjectiveObservationStatus,
) -> None:
    request = task_request()
    observations = request.semantic_input.objective_observations
    assert observations is not None
    with pytest.raises(InvalidDomainValue, match="cannot claim a snapshot"):
        replace(observations[0], status=status)


def test_current_observation_requires_version_and_state() -> None:
    request = task_request()
    observations = request.semantic_input.objective_observations
    assert observations is not None
    with pytest.raises(InvalidDomainValue, match="require Objective version and state"):
        replace(
            observations[0],
            observed_entity_version=None,
            observed_state=None,
        )


def test_stale_observation_retains_observed_snapshot() -> None:
    request = task_request()
    observations = request.semantic_input.objective_observations
    assert observations is not None
    stale = replace(observations[0], status=TaskObjectiveObservationStatus.STALE)
    assert stale.observed_entity_version == EntityVersion(4)
    assert stale.observed_state is ObjectiveState.DRAFT


def test_task_completion_policy_substitution_is_rejected() -> None:
    request = task_request()
    completion = request.semantic_input.completion_policy
    assert completion is not None
    substituted = replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            completion_policy=replace(
                completion,
                completion_policy_ref=CompletionPolicyRef("other-task-policy", "1"),
            ),
        ),
    )
    with pytest.raises(InvariantViolation, match="Completion-policy.*exact-bind"):
        create_entity(substituted, context(substituted))


def test_task_definition_wrong_task_id_is_rejected() -> None:
    request = task_request()
    definition = request.semantic_input.bounded_definition
    assert definition is not None
    substituted = replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            bounded_definition=replace(definition, task_id=TaskId(uid(916))),
        ),
    )
    with pytest.raises(InvariantViolation, match="Bounded-definition.*exact-bind"):
        create_entity(substituted, context(substituted))


@pytest.mark.parametrize(
    "decision_name,field,value",
    [
        ("bounded_definition", "request_causation_id", CausationId(uid(917))),
        ("bounded_definition", "correlation_id", CorrelationId(uid(918))),
        ("completion_policy", "task_id", TaskId(uid(919))),
        ("completion_policy", "request_causation_id", CausationId(uid(920))),
        ("completion_policy", "correlation_id", CorrelationId(uid(921))),
    ],
)
def test_task_semantic_decision_request_bindings_reject_substitution(
    decision_name: str, field: str, value: object
) -> None:
    request = task_request()
    decision = getattr(request.semantic_input, decision_name)
    assert decision is not None
    substituted = replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            **{decision_name: replace(decision, **{field: value})},
        ),
    )
    with pytest.raises(InvariantViolation, match="exact-bind"):
        create_entity(substituted, context(substituted))


def test_task_contribution_and_evidence_ordering_are_deterministic() -> None:
    request = task_request()
    semantics = request.semantic_input
    observations = semantics.objective_observations
    bounded = semantics.bounded_definition
    completion = semantics.completion_policy
    assert observations is not None
    assert bounded is not None
    assert completion is not None
    shared = EvidenceRef("evidence:shared")
    substituted_observations = tuple(
        replace(observation, evidence_refs=frozenset({shared}))
        for observation in reversed(observations)
    )
    substituted = replace(
        request,
        semantic_input=replace(
            semantics,
            bounded_definition=replace(
                bounded, evidence_refs=frozenset({shared, EvidenceRef("evidence:z")})
            ),
            completion_policy=replace(
                completion,
                evidence_refs=frozenset({shared, EvidenceRef("evidence:a")}),
            ),
            objective_observations=substituted_observations,
        ),
    )
    values = annotations(create_entity(substituted, context(substituted)))
    assert values["contribution_objective.0000.id"] == str(ObjectiveId(uid(202)))
    assert values["contribution_objective.0001.id"] == str(ObjectiveId(uid(203)))
    assert {
        key: value
        for key, value in values.items()
        if key.startswith("semantic_evidence_ref")
    } == {
        "semantic_evidence_ref.0000": "evidence:a",
        "semantic_evidence_ref.0001": "evidence:shared",
        "semantic_evidence_ref.0002": "evidence:z",
    }


@pytest.mark.parametrize(
    "status",
    [
        TaskObjectiveObservationStatus.STALE,
        TaskObjectiveObservationStatus.UNRESOLVED,
    ],
)
def test_stale_and_unresolved_contribution_objectives_fail_closed(
    status: TaskObjectiveObservationStatus,
) -> None:
    request = task_request(contribution_status=status)
    with pytest.raises(InvariantViolation, match=status.value):
        create_entity(request, context(request))


@dataclass(frozen=True, slots=True)
class RejectingGuard:
    def validate(self, request: CreationRequest) -> None:
        raise InvariantViolation("additional guard rejected creation")


@pytest.mark.parametrize("creation_request", [objective_request(), task_request()])
def test_additional_guard_failure_returns_no_creation_result(
    creation_request: ObjectiveDraftCreationRequest | TaskDraftCreationRequest,
) -> None:
    base = context(creation_request)
    guarded = replace(base, guards=(RejectingGuard(),))
    with pytest.raises(InvariantViolation, match="additional guard"):
        create_entity(creation_request, guarded)
