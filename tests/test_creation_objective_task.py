from dataclasses import dataclass, replace
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
) -> CreationContext:
    authority = CreationAuthorityDecision(
        CreationAuthorityDecisionId(uid(300)),
        request.scope,
        AUTHORITY,
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
    assert result.event.entity_version == EntityVersion(1)
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
    assert result.event.entity_version == EntityVersion(1)
    assert result.event.metadata.prior_state is None
    assert result.event.metadata.new_state is TaskState.DRAFT
    values = annotations(result)
    assert values["primary_objective_observed_version"] == "4"
    assert values["primary_objective_observation_ref"].startswith("observation:")
    assert values["contribution_objective.0000.id"] == str(ObjectiveId(uid(202)))
    assert values["contribution_objective.0001.id"] == str(ObjectiveId(uid(203)))
    assert set(values) == {
        "requested_by.actor_id",
        "requested_by.actor_type",
        "applying_service.actor_id",
        "applying_service.actor_type",
        "creation_authority_decision_ref",
        "identifier_availability_ref",
        "semantic_provenance_ref",
        "authority_policy_or_grant_ref.0000",
        "authority_policy_or_grant_ref.0001",
        "definition_decision_ref",
        "completion_policy_decision_ref",
        "primary_objective_observation_ref",
        "primary_objective_observed_version",
        "contribution_objective.0000.id",
        "contribution_objective.0000.observation_ref",
        "contribution_objective.0000.observed_version",
        "contribution_objective.0001.id",
        "contribution_objective.0001.observation_ref",
        "contribution_objective.0001.observed_version",
        "semantic_evidence_ref.0000",
        "semantic_evidence_ref.0001",
        "semantic_evidence_ref.0002",
        "semantic_evidence_ref.0003",
        "semantic_evidence_ref.0004",
    }


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
