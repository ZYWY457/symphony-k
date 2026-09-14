"""M7D1 shared creation protocol: exact binding and deliberate default denial."""

from dataclasses import FrozenInstanceError, dataclass, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArtifactRef,
    CausationId,
    CommittedEffectObservationCreationRequest,
    CompletionPolicyRef,
    CorrelationId,
    CreationAuthorityDecision,
    CreationAuthorityDecisionId,
    CreationAuthorityStatus,
    CreationContext,
    CreationRequest,
    CreationRequestVariant,
    CreationResult,
    DomainEntityType,
    DomainEvent,
    DomainEventMetadata,
    DomainEventType,
    Effect,
    EffectExternalOperationRef,
    EffectId,
    EffectPayloadRef,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    Evaluation,
    EvaluationConfidence,
    EvaluationCreationSemanticInput,
    EvaluationCreationSpec,
    EvaluationId,
    EvaluationMethodRef,
    EvaluationPendingCreationRequest,
    EvaluationResult,
    EvaluationState,
    EvaluationTargetRef,
    EvaluationVerdict,
    EventId,
    EvidenceRef,
    ExecutionProfileRef,
    IdentifierAvailability,
    IdentifierAvailabilityId,
    IdentifierAvailabilityStatus,
    InvalidDomainValue,
    InvalidTransition,
    InvariantViolation,
    Objective,
    ObjectiveCreationSemanticInput,
    ObjectiveCreationSpec,
    ObjectiveDraftCreationRequest,
    ObjectiveId,
    ObjectiveState,
    ObservedEffectCreationSemanticInput,
    ObservedEffectCreationSpec,
    ObservedEffectOrigin,
    Outcome,
    OutcomeCreationSemanticInput,
    OutcomeCreationSpec,
    OutcomeId,
    OutcomeProposedCreationRequest,
    OutcomeState,
    PlannedEffectCreationRequest,
    PlannedEffectCreationSemanticInput,
    PlannedEffectCreationSpec,
    PlannedEffectOrigin,
    QuarantinedEffectObservationCreationRequest,
    Run,
    RunCreationSemanticInput,
    RunCreationSpec,
    RunId,
    RunPendingCreationRequest,
    RunState,
    Task,
    TaskCreationSemanticInput,
    TaskCreationSpec,
    TaskDraftCreationRequest,
    TaskId,
    TaskState,
    Timestamp,
    TransitionContext,
    TransitionReason,
    TransitionRequest,
    UnauthorizedTransition,
    create_entity,
    transition_entity,
)
from symphony_k.domain.transition_engine import LifecycleEntity, LifecycleState


def uid(value: int) -> UUID:
    return UUID(f"00000000-0000-4000-8000-{value:012x}")


VALUE = uid(1)
THIRD = uid(3)


def actor(value: UUID, actor_type: ActorType) -> ActorIdentity:
    return ActorIdentity(ActorId(value), actor_type)


def timestamp() -> Timestamp:
    return Timestamp(datetime(2026, 9, 13, tzinfo=UTC))


@dataclass(frozen=True, slots=True)
class CreationCase:
    name: str
    creation_request: CreationRequest
    entity: LifecycleEntity
    event_type: DomainEventType
    authority_actor_type: ActorType


def _objective_case() -> CreationCase:
    spec = ObjectiveCreationSpec(
        "Restore one payment path",
        ("A deterministic acceptance check passes",),
        actor(uid(1001), ActorType.HUMAN_OPERATOR),
        CompletionPolicyRef("objective-policy", "1"),
        timestamp(),
    )
    request = ObjectiveDraftCreationRequest(
        EventId(uid(101)),
        ObjectiveId(uid(102)),
        actor(uid(103), ActorType.REQUESTER),
        TransitionReason("Register bounded objective"),
        timestamp(),
        CorrelationId(uid(104)),
        CausationId(uid(105)),
        spec,
        ObjectiveCreationSemanticInput(CausationId(uid(106))),
    )
    return CreationCase(
        "objective",
        request,
        Objective(
            request.entity_id,
            ObjectiveState.DRAFT,
            EntityVersion(1),
            spec.goal,
            spec.acceptance_criteria,
            spec.acceptance_authority,
            spec.completion_policy_ref,
            spec.valid_until,
        ),
        DomainEventType.OBJECTIVE_CREATED,
        ActorType.SCHEDULER,
    )


def _task_case() -> CreationCase:
    spec = TaskCreationSpec(
        "Repair payment retry worker",
        ObjectiveId(uid(202)),
        CompletionPolicyRef("task-policy", "1"),
        frozenset({ObjectiveId(uid(203))}),
    )
    request = TaskDraftCreationRequest(
        EventId(uid(201)),
        TaskId(uid(204)),
        actor(uid(205), ActorType.REQUESTER),
        TransitionReason("Register bounded task"),
        timestamp(),
        CorrelationId(uid(206)),
        CausationId(uid(207)),
        spec,
        TaskCreationSemanticInput(CausationId(uid(208))),
    )
    return CreationCase(
        "task",
        request,
        Task(
            request.entity_id,
            TaskState.DRAFT,
            EntityVersion(1),
            spec.definition,
            spec.primary_objective_id,
            spec.completion_policy_ref,
            spec.contributes_to,
        ),
        DomainEventType.TASK_CREATED,
        ActorType.SCHEDULER,
    )


def _run_case() -> CreationCase:
    spec = RunCreationSpec(
        TaskId(uid(302)),
        ExecutionProfileRef("codex", "1"),
        RunId(uid(303)),
    )
    request = RunPendingCreationRequest(
        EventId(uid(301)),
        RunId(uid(304)),
        actor(uid(305), ActorType.SCHEDULER),
        TransitionReason("Register execution attempt"),
        timestamp(),
        CorrelationId(uid(306)),
        CausationId(uid(307)),
        spec,
        RunCreationSemanticInput(CausationId(uid(308))),
    )
    return CreationCase(
        "run",
        request,
        Run(
            request.entity_id,
            spec.task_id,
            RunState.PENDING,
            EntityVersion(1),
            spec.execution_profile_ref,
            spec.predecessor_run_id,
        ),
        DomainEventType.RUN_CREATED,
        ActorType.RUN_CONTROLLER,
    )


def _outcome_case() -> CreationCase:
    spec = OutcomeCreationSpec(
        RunId(uid(402)),
        actor(uid(403), ActorType.WORKER),
        frozenset({ArtifactRef("artifact:patch")}),
        frozenset({EvidenceRef("evidence:test-log")}),
        timestamp(),
        OutcomeId(uid(404)),
    )
    request = OutcomeProposedCreationRequest(
        EventId(uid(401)),
        OutcomeId(uid(405)),
        actor(uid(406), ActorType.WORKER),
        TransitionReason("Register candidate outcome"),
        timestamp(),
        CorrelationId(uid(407)),
        CausationId(uid(408)),
        spec,
        OutcomeCreationSemanticInput(CausationId(uid(409))),
    )
    return CreationCase(
        "outcome",
        request,
        Outcome(
            request.entity_id,
            spec.run_id,
            OutcomeState.PROPOSED,
            EntityVersion(1),
            spec.producer,
            spec.artifact_refs,
            spec.evidence_refs,
            spec.valid_until,
            spec.prior_outcome_id,
        ),
        DomainEventType.OUTCOME_PROPOSED,
        ActorType.POLICY_ENGINE,
    )


def _evaluation_case() -> CreationCase:
    spec = EvaluationCreationSpec(
        EvaluationTargetRef(RunId(uid(502)), EntityVersion(7)),
        EvaluationMethodRef("pytest", "1"),
        actor(uid(503), ActorType.EVALUATOR),
    )
    request = EvaluationPendingCreationRequest(
        EventId(uid(501)),
        EvaluationId(uid(504)),
        actor(uid(505), ActorType.SCHEDULER),
        TransitionReason("Register evaluation request"),
        timestamp(),
        CorrelationId(uid(506)),
        CausationId(uid(507)),
        spec,
        EvaluationCreationSemanticInput(CausationId(uid(508))),
    )
    return CreationCase(
        "evaluation",
        request,
        Evaluation(
            request.entity_id,
            EvaluationState.PENDING,
            EntityVersion(1),
            spec.target,
            spec.method,
            spec.verifier,
        ),
        DomainEventType.EVALUATION_REQUESTED,
        ActorType.EVALUATOR,
    )


def _planned_effect_case() -> CreationCase:
    spec = PlannedEffectCreationSpec(
        PlannedEffectOrigin(
            TaskId(uid(602)),
            actor(uid(603), ActorType.WORKER),
            RunId(uid(604)),
        ),
        EffectTargetRef("target:payment-service"),
        EffectPayloadRef("payload:planned-retry-config"),
    )
    request = PlannedEffectCreationRequest(
        EventId(uid(601)),
        EffectId(uid(605)),
        actor(uid(606), ActorType.WORKER),
        TransitionReason("Register planned effect"),
        timestamp(),
        CorrelationId(uid(607)),
        CausationId(uid(608)),
        spec,
        PlannedEffectCreationSemanticInput(CausationId(uid(609))),
    )
    return CreationCase(
        "planned_effect",
        request,
        Effect(
            request.entity_id,
            EffectState.PLANNED,
            EntityVersion(1),
            spec.origin,
            spec.target_ref,
            spec.payload_ref,
        ),
        DomainEventType.EFFECT_PLANNED,
        ActorType.EFFECT_CONTROLLER,
    )


def _committed_effect_case() -> CreationCase:
    spec = ObservedEffectCreationSpec(
        ObservedEffectOrigin(
            EffectExternalOperationRef("external:commit-1"),
            frozenset({EvidenceRef("receipt:commit-1")}),
            actor(uid(703), ActorType.EVALUATOR),
            timestamp(),
            TaskId(uid(704)),
            RunId(uid(705)),
        ),
        EffectTargetRef("target:remote-system"),
        EffectPayloadRef("payload:observed-change"),
    )
    request = CommittedEffectObservationCreationRequest(
        EventId(uid(701)),
        EffectId(uid(706)),
        actor(uid(707), ActorType.EVALUATOR),
        TransitionReason("Register confirmed external occurrence"),
        timestamp(),
        CorrelationId(uid(708)),
        CausationId(uid(709)),
        spec,
        ObservedEffectCreationSemanticInput(CausationId(uid(710))),
    )
    return CreationCase(
        "committed_effect",
        request,
        Effect(
            request.entity_id,
            EffectState.COMMITTED,
            EntityVersion(1),
            spec.origin,
            spec.target_ref,
            spec.payload_ref,
        ),
        DomainEventType.EFFECT_COMMITTED,
        ActorType.EFFECT_CONTROLLER,
    )


def _quarantined_effect_case() -> CreationCase:
    spec = ObservedEffectCreationSpec(
        ObservedEffectOrigin(
            EffectExternalOperationRef("external:suspected-1"),
            frozenset({EvidenceRef("receipt:suspected-1")}),
            actor(uid(803), ActorType.EVALUATOR),
            timestamp(),
            unlinked_reason="Attribution not yet known",
        ),
        EffectTargetRef("target:unknown-remote-system"),
        None,
    )
    request = QuarantinedEffectObservationCreationRequest(
        EventId(uid(801)),
        EffectId(uid(804)),
        actor(uid(805), ActorType.EVALUATOR),
        TransitionReason("Register suspected external occurrence"),
        timestamp(),
        CorrelationId(uid(806)),
        CausationId(uid(807)),
        spec,
        ObservedEffectCreationSemanticInput(CausationId(uid(808))),
    )
    return CreationCase(
        "quarantined_effect",
        request,
        Effect(
            request.entity_id,
            EffectState.QUARANTINED,
            EntityVersion(1),
            spec.origin,
            spec.target_ref,
            spec.payload_ref,
        ),
        DomainEventType.EFFECT_QUARANTINED,
        ActorType.EFFECT_CONTROLLER,
    )


def creation_cases() -> tuple[CreationCase, ...]:
    return (
        _objective_case(),
        _task_case(),
        _run_case(),
        _outcome_case(),
        _evaluation_case(),
        _planned_effect_case(),
        _committed_effect_case(),
        _quarantined_effect_case(),
    )


def case_ids() -> list[str]:
    return [case.name for case in creation_cases()]


def authority(
    case: CreationCase,
    *,
    decided_by: ActorIdentity | None = None,
    status: CreationAuthorityStatus = CreationAuthorityStatus.AUTHORIZED,
) -> CreationAuthorityDecision:
    return CreationAuthorityDecision(
        CreationAuthorityDecisionId(uid(9001)),
        case.creation_request.scope,
        decided_by or actor(uid(9002), case.authority_actor_type),
        status,
        (CausationId(uid(9003)),),
        timestamp(),
    )


def availability(
    case: CreationCase,
    *,
    status: IdentifierAvailabilityStatus = IdentifierAvailabilityStatus.AVAILABLE,
) -> IdentifierAvailability:
    request = case.creation_request
    return IdentifierAvailability(
        IdentifierAvailabilityId(uid(9101)),
        request.scope,
        request.entity_type,
        request.entity_id,
        status,
        actor(uid(9102), ActorType.SCHEDULER),
        timestamp(),
        request.correlation_id,
    )


def context(case: CreationCase) -> CreationContext:
    return CreationContext(
        authority(case),
        availability(case),
        actor(uid(9201), ActorType.SYSTEM),
    )


def creation_event(
    case: CreationCase,
    decision: CreationAuthorityDecision | None = None,
    *,
    metadata: DomainEventMetadata | None = None,
) -> DomainEvent:
    request = case.creation_request
    decision_actor = (decision or authority(case)).decided_by
    return DomainEvent(
        request.event_id,
        case.event_type,
        request.entity_type,
        request.entity_id,
        EntityVersion(1),
        decision_actor,
        request.timestamp,
        request.correlation_id,
        request.causation_id,
        request.reason,
        metadata or DomainEventMetadata(None, request.target_state),
    )


def result(case: CreationCase) -> CreationResult[LifecycleEntity]:
    decision = authority(case)
    return CreationResult(
        case.entity,
        creation_event(case, decision),
        case.creation_request,
        decision,
        availability(case),
    )


def test_exactly_eight_closed_creation_request_variants() -> None:
    assert len(CreationRequestVariant) == 8
    assert {member.value for member in CreationRequestVariant} == {
        "OBJECTIVE_DRAFT",
        "TASK_DRAFT",
        "RUN_PENDING",
        "OUTCOME_PROPOSED",
        "EVALUATION_PENDING",
        "EFFECT_PLANNED",
        "EFFECT_COMMITTED",
        "EFFECT_QUARANTINED",
    }
    assert len(creation_cases()) == 8


@pytest.mark.parametrize("case", creation_cases(), ids=case_ids())
def test_requests_and_normalized_scopes_have_no_source_or_version_inputs(
    case: CreationCase,
) -> None:
    request = case.creation_request
    scope = request.scope
    for field_name in (
        "source_state",
        "prior_state",
        "expected_version",
        "initial_version",
    ):
        assert not hasattr(request, field_name)
        assert not hasattr(scope, field_name)
    with pytest.raises(FrozenInstanceError):
        scope.entity_id = ObjectiveId(VALUE)  # type: ignore[misc]


@pytest.mark.parametrize("case", creation_cases(), ids=case_ids())
def test_all_request_variants_bind_family_id_target_spec_and_input(
    case: CreationCase,
) -> None:
    request = case.creation_request
    scope = request.scope
    expected_family_and_target = {
        ObjectiveDraftCreationRequest: (
            DomainEntityType.OBJECTIVE,
            ObjectiveState.DRAFT,
        ),
        TaskDraftCreationRequest: (DomainEntityType.TASK, TaskState.DRAFT),
        RunPendingCreationRequest: (DomainEntityType.RUN, RunState.PENDING),
        OutcomeProposedCreationRequest: (
            DomainEntityType.OUTCOME,
            OutcomeState.PROPOSED,
        ),
        EvaluationPendingCreationRequest: (
            DomainEntityType.EVALUATION,
            EvaluationState.PENDING,
        ),
        PlannedEffectCreationRequest: (
            DomainEntityType.EFFECT,
            EffectState.PLANNED,
        ),
        CommittedEffectObservationCreationRequest: (
            DomainEntityType.EFFECT,
            EffectState.COMMITTED,
        ),
        QuarantinedEffectObservationCreationRequest: (
            DomainEntityType.EFFECT,
            EffectState.QUARANTINED,
        ),
    }
    assert (request.entity_type, request.target_state) == expected_family_and_target[
        type(request)
    ]
    assert scope.variant is request.variant
    assert scope.entity_type is request.entity_type
    assert scope.entity_id == request.entity_id
    assert scope.target_state is request.target_state
    assert scope.entity_spec == request.entity_spec
    assert scope.semantic_input == request.semantic_input


def test_authority_rejects_a_decision_reused_for_a_relabelled_requester() -> None:
    original = _objective_case()
    request = original.creation_request
    assert isinstance(request, ObjectiveDraftCreationRequest)
    substituted_request = replace(
        request,
        requested_by=actor(uid(9991), ActorType.REQUESTER),
    )
    substituted = replace(original, creation_request=substituted_request)
    forged_context = CreationContext(
        authority(original),
        availability(substituted),
        actor(THIRD, ActorType.SYSTEM),
    )
    with pytest.raises(UnauthorizedTransition, match="exact-bind request scope"):
        create_entity(substituted.creation_request, forged_context)


def test_availability_rejects_a_observation_reused_for_changed_specification() -> None:
    original = _objective_case()
    request = original.creation_request
    assert isinstance(request, ObjectiveDraftCreationRequest)
    substituted_request = replace(
        request,
        entity_spec=replace(request.entity_spec, goal="Change the requested goal"),
    )
    substituted = replace(original, creation_request=substituted_request)
    forged_context = CreationContext(
        authority(substituted),
        availability(original),
        actor(THIRD, ActorType.SYSTEM),
    )
    with pytest.raises(InvariantViolation, match="exact-bind request scope"):
        create_entity(substituted.creation_request, forged_context)


@pytest.mark.parametrize(
    "status",
    [CreationAuthorityStatus.DENIED, CreationAuthorityStatus.UNRESOLVED],
)
def test_denied_and_unresolved_authority_fail_closed(
    status: CreationAuthorityStatus,
) -> None:
    case = _objective_case()
    with pytest.raises(UnauthorizedTransition, match=status.value):
        create_entity(
            case.creation_request,
            CreationContext(
                authority(case, status=status),
                availability(case),
                actor(THIRD, ActorType.SYSTEM),
            ),
        )


@pytest.mark.parametrize(
    "status",
    [
        IdentifierAvailabilityStatus.AVAILABLE,
        IdentifierAvailabilityStatus.DUPLICATE,
        IdentifierAvailabilityStatus.UNRESOLVED,
    ],
)
def test_all_identifier_availability_statuses_fail_closed_or_reject(
    status: IdentifierAvailabilityStatus,
) -> None:
    case = _objective_case()
    expected = (
        "not implemented"
        if status is IdentifierAvailabilityStatus.AVAILABLE
        else status.value
    )
    with pytest.raises(InvariantViolation, match=expected):
        create_entity(
            case.creation_request,
            CreationContext(
                authority(case),
                availability(case, status=status),
                actor(THIRD, ActorType.SYSTEM),
            ),
        )


def test_identifier_observation_must_not_be_requester_self_attestation() -> None:
    case = _objective_case()
    request = case.creation_request
    with pytest.raises(InvalidDomainValue, match="must differ from the requester"):
        replace(
            availability(case),
            observed_by=actor(request.requested_by.actor_id.value, ActorType.SCHEDULER),
        )


def test_identifier_observation_rejects_correlation_substitution() -> None:
    case = _objective_case()
    with pytest.raises(InvalidDomainValue, match="correlation_id must match"):
        replace(availability(case), correlation_id=CorrelationId(uid(9992)))


def test_identifier_availability_is_required() -> None:
    case = _objective_case()
    with pytest.raises(InvariantViolation, match="observation is required"):
        create_entity(
            case.creation_request,
            CreationContext(
                authority(case),
                None,
                actor(THIRD, ActorType.SYSTEM),
            ),
        )


def test_identifier_observation_rejects_entity_type_substitution() -> None:
    case = _objective_case()
    with pytest.raises(InvalidDomainValue, match="entity_type must match"):
        replace(
            availability(case),
            entity_type=_task_case().creation_request.entity_type,
        )


def test_identifier_observation_rejects_entity_id_substitution() -> None:
    case = _objective_case()
    with pytest.raises(InvalidDomainValue, match="entity_id must match"):
        replace(availability(case), entity_id=ObjectiveId(uid(9990)))


def test_raw_boolean_is_not_identifier_availability_evidence() -> None:
    case = _objective_case()
    with pytest.raises(
        InvalidDomainValue,
        match="identifier_availability must be an IdentifierAvailability",
    ):
        CreationContext(
            authority(case),
            True,  # type: ignore[arg-type]
            actor(THIRD, ActorType.SYSTEM),
        )


def test_system_has_no_implicit_superuser_creation_authority() -> None:
    case = _objective_case()
    with pytest.raises(UnauthorizedTransition, match="not eligible"):
        create_entity(
            case.creation_request,
            CreationContext(
                authority(case, decided_by=actor(uid(9002), ActorType.SYSTEM)),
                availability(case),
                actor(THIRD, ActorType.SYSTEM),
            ),
        )


def test_ineligible_actor_cannot_supply_creation_authority() -> None:
    case = _objective_case()
    with pytest.raises(UnauthorizedTransition, match="not eligible"):
        create_entity(
            case.creation_request,
            CreationContext(
                authority(case, decided_by=actor(uid(9010), ActorType.WORKER)),
                availability(case),
                actor(THIRD, ActorType.SYSTEM),
            ),
        )


def test_exact_same_eligible_principal_is_not_rejected_as_relabelled() -> None:
    case = _objective_case()
    with pytest.raises(InvariantViolation, match="not implemented"):
        create_entity(
            case.creation_request,
            CreationContext(
                authority(case, decided_by=case.creation_request.requested_by),
                availability(case),
                actor(THIRD, ActorType.SYSTEM),
            ),
        )


@pytest.mark.parametrize("case", creation_cases(), ids=case_ids())
def test_common_requester_principal_cannot_relabel_as_creation_authority(
    case: CreationCase,
) -> None:
    relabelled = actor(
        case.creation_request.requested_by.actor_id.value,
        case.authority_actor_type,
    )
    if relabelled.actor_type is case.creation_request.requested_by.actor_type:
        return
    with pytest.raises(UnauthorizedTransition, match="relabelling a principal"):
        create_entity(
            case.creation_request,
            CreationContext(
                authority(case, decided_by=relabelled),
                availability(case),
                actor(THIRD, ActorType.SYSTEM),
            ),
        )


def test_outcome_producer_cannot_relabel_worker_principal_as_authority() -> None:
    case = _outcome_case()
    request = case.creation_request
    assert isinstance(request.entity_spec, OutcomeCreationSpec)
    relabelled = actor(
        request.entity_spec.producer.actor_id.value,
        case.authority_actor_type,
    )
    with pytest.raises(UnauthorizedTransition, match="relabelling a principal"):
        create_entity(
            request,
            CreationContext(
                authority(case, decided_by=relabelled),
                availability(case),
                actor(THIRD, ActorType.SYSTEM),
            ),
        )


@pytest.mark.parametrize(
    "case",
    [_planned_effect_case(), _committed_effect_case(), _quarantined_effect_case()],
    ids=["planned", "committed", "quarantined"],
)
def test_effect_origin_principals_cannot_relabel_as_effect_controller(
    case: CreationCase,
) -> None:
    spec = case.creation_request.entity_spec
    if isinstance(spec, PlannedEffectCreationSpec):
        principal = spec.origin.proposed_by
    else:
        assert isinstance(spec, ObservedEffectCreationSpec)
        principal = spec.origin.observed_by
    relabelled = actor(principal.actor_id.value, ActorType.EFFECT_CONTROLLER)
    with pytest.raises(UnauthorizedTransition, match="relabelling a principal"):
        create_entity(
            case.creation_request,
            CreationContext(
                authority(case, decided_by=relabelled),
                availability(case),
                actor(THIRD, ActorType.SYSTEM),
            ),
        )


@pytest.mark.parametrize("case", creation_cases(), ids=case_ids())
def test_result_accepts_only_canonical_version_one_snapshot(
    case: CreationCase,
) -> None:
    creation_result = result(case)
    assert creation_result.entity.version == EntityVersion(1)
    assert creation_result.event.entity_version == EntityVersion(1)
    with pytest.raises(InvalidDomainValue, match="canonical version-1"):
        replace(
            creation_result,
            entity=replace(case.entity, version=EntityVersion(2)),
        )
    with pytest.raises(InvalidDomainValue, match="canonical version-1"):
        replace(
            creation_result,
            entity=replace(case.entity, version=EntityVersion(0)),
        )


@pytest.mark.parametrize("case", creation_cases(), ids=case_ids())
def test_result_rejects_entity_id_substitution(case: CreationCase) -> None:
    with pytest.raises(InvalidDomainValue, match="canonical version-1"):
        CreationResult(
            _with_substituted_id(case.entity),
            creation_event(case),
            case.creation_request,
            authority(case),
            availability(case),
        )


@pytest.mark.parametrize("case", creation_cases(), ids=case_ids())
def test_result_rejects_target_state_substitution(case: CreationCase) -> None:
    with pytest.raises(InvalidDomainValue, match="canonical version-1"):
        CreationResult(
            _with_substituted_state(case.entity),
            creation_event(case),
            case.creation_request,
            authority(case),
            availability(case),
        )


@pytest.mark.parametrize("case", creation_cases(), ids=case_ids())
def test_result_rejects_immutable_spec_substitution(case: CreationCase) -> None:
    with pytest.raises(InvalidDomainValue, match="exact-bind request.entity_spec"):
        CreationResult(
            _with_substituted_spec_content(case.entity),
            creation_event(case),
            case.creation_request,
            authority(case),
            availability(case),
        )


@pytest.mark.parametrize("case", creation_cases(), ids=case_ids())
def test_result_rejects_entity_family_substitution(case: CreationCase) -> None:
    substitute = (
        _task_case().entity
        if isinstance(case.entity, Objective)
        else _objective_case().entity
    )
    with pytest.raises(InvalidDomainValue, match="canonical version-1"):
        CreationResult(
            substitute,
            creation_event(case),
            case.creation_request,
            authority(case),
            availability(case),
        )


def test_result_rejects_fabricated_outcome_supersession_lineage() -> None:
    case = _outcome_case()
    assert isinstance(case.entity, Outcome)
    with pytest.raises(InvalidDomainValue, match="exact-bind request.entity_spec"):
        CreationResult(
            replace(case.entity, superseded_by_outcome_id=OutcomeId(uid(9993))),
            creation_event(case),
            case.creation_request,
            authority(case),
            availability(case),
        )


@pytest.mark.parametrize("case", creation_cases(), ids=case_ids())
def test_result_accepts_structurally_valid_nonempty_annotation(
    case: CreationCase,
) -> None:
    decision = authority(case)
    # Illustrative structure only; later entity slices own canonical keys/values.
    annotations = frozenset(
        {
            (
                "stable_ref",
                f"fixture:{decision.decision_ref.value}",
            )
        }
    )
    creation_result = CreationResult(
        case.entity,
        creation_event(
            case,
            decision,
            metadata=DomainEventMetadata(
                None,
                case.creation_request.target_state,
                annotations,
            ),
        ),
        case.creation_request,
        decision,
        availability(case),
    )
    assert creation_result.event.metadata.annotations == annotations


def test_result_rejects_event_id_substitution() -> None:
    creation_result = result(_objective_case())
    with pytest.raises(
        InvalidDomainValue, match="exactly describe the creation result"
    ):
        replace(
            creation_result,
            event=replace(creation_result.event, event_id=EventId(uid(9994))),
        )


def test_result_rejects_event_entity_id_substitution() -> None:
    creation_result = result(_objective_case())
    with pytest.raises(
        InvalidDomainValue, match="exactly describe the creation result"
    ):
        replace(
            creation_result,
            event=replace(
                creation_result.event,
                entity_id=ObjectiveId(uid(9995)),
            ),
        )


@pytest.mark.parametrize(
    "event_version",
    [EntityVersion(0), EntityVersion(2)],
    ids=["zero", "two"],
)
def test_result_rejects_event_entity_version_substitution(
    event_version: EntityVersion,
) -> None:
    creation_result = result(_objective_case())
    assert creation_result.entity.version == EntityVersion(1)
    assert creation_result.event.entity_version == EntityVersion(1)
    with pytest.raises(
        InvalidDomainValue, match="exactly describe the creation result"
    ):
        replace(
            creation_result,
            event=replace(
                creation_result.event,
                entity_version=event_version,
            ),
        )


def test_result_rejects_event_authority_actor_substitution() -> None:
    creation_result = result(_objective_case())
    with pytest.raises(
        InvalidDomainValue, match="exactly describe the creation result"
    ):
        replace(
            creation_result,
            event=replace(
                creation_result.event,
                actor=actor(uid(9996), ActorType.SCHEDULER),
            ),
        )


def test_result_rejects_event_timestamp_substitution() -> None:
    creation_result = result(_objective_case())
    substituted_timestamp = Timestamp(datetime(2026, 9, 14, tzinfo=UTC))
    with pytest.raises(
        InvalidDomainValue, match="exactly describe the creation result"
    ):
        replace(
            creation_result,
            event=replace(
                creation_result.event,
                timestamp=substituted_timestamp,
            ),
        )


def test_result_rejects_event_correlation_substitution() -> None:
    creation_result = result(_objective_case())
    with pytest.raises(
        InvalidDomainValue, match="exactly describe the creation result"
    ):
        replace(
            creation_result,
            event=replace(
                creation_result.event,
                correlation_id=CorrelationId(uid(9997)),
            ),
        )


def test_result_rejects_event_causation_substitution() -> None:
    creation_result = result(_objective_case())
    with pytest.raises(
        InvalidDomainValue, match="exactly describe the creation result"
    ):
        replace(
            creation_result,
            event=replace(
                creation_result.event,
                causation_id=CausationId(uid(9998)),
            ),
        )


def test_result_rejects_event_reason_substitution() -> None:
    creation_result = result(_objective_case())
    with pytest.raises(
        InvalidDomainValue, match="exactly describe the creation result"
    ):
        replace(
            creation_result,
            event=replace(
                creation_result.event,
                reason=TransitionReason("Substituted reason"),
            ),
        )


def test_domain_event_rejects_wrong_creation_event_type() -> None:
    with pytest.raises(InvalidDomainValue, match="event_type must match"):
        replace(
            creation_event(_objective_case()),
            event_type=DomainEventType.OBJECTIVE_ACTIVATED,
        )


def test_result_rejects_non_none_prior_state() -> None:
    case = _objective_case()
    with pytest.raises(InvalidDomainValue, match="canonical lifecycle edge"):
        replace(
            creation_event(case),
            metadata=DomainEventMetadata(
                ObjectiveState.ACTIVE,
                ObjectiveState.DRAFT,
            ),
        )


def test_domain_event_rejects_wrong_creation_new_state_when_prior_is_absent() -> None:
    with pytest.raises(InvalidDomainValue, match="canonical creation target"):
        replace(
            creation_event(_objective_case()),
            event_type=DomainEventType.OBJECTIVE_ACTIVATED,
            metadata=DomainEventMetadata(None, ObjectiveState.ACTIVE),
        )


def test_evaluation_pending_snapshot_rejects_result_injection() -> None:
    case = _evaluation_case()
    assert isinstance(case.entity, Evaluation)
    injected_result = EvaluationResult(
        EvaluationVerdict("PASS"),
        EvaluationConfidence("HIGH"),
        "Injected before verification",
    )
    with pytest.raises(InvalidDomainValue, match="cannot have a result"):
        replace(case.entity, result=injected_result)


def test_domain_event_metadata_rejects_malformed_annotation() -> None:
    with pytest.raises(InvalidDomainValue, match="two non-whitespace strings"):
        DomainEventMetadata(
            None,
            ObjectiveState.DRAFT,
            frozenset({("only-a-key",)}),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "annotation",
    [
        ("", "stable:value"),
        ("   ", "stable:value"),
        ("stable_key", ""),
        ("stable_key", "   "),
    ],
    ids=["empty-key", "blank-key", "empty-value", "blank-value"],
)
def test_domain_event_metadata_rejects_blank_annotation_key_or_value(
    annotation: tuple[str, str],
) -> None:
    with pytest.raises(InvalidDomainValue, match="two non-whitespace strings"):
        DomainEventMetadata(
            None,
            ObjectiveState.DRAFT,
            frozenset({annotation}),
        )


def test_domain_event_metadata_rejects_duplicate_annotation_keys() -> None:
    with pytest.raises(InvalidDomainValue, match="keys must be unique"):
        DomainEventMetadata(
            None,
            ObjectiveState.DRAFT,
            frozenset(
                {
                    ("stable_key", "stable:value-1"),
                    ("stable_key", "stable:value-2"),
                }
            ),
        )


@pytest.mark.parametrize("case", creation_cases(), ids=case_ids())
def test_shared_checks_fail_closed_before_entity_semantics_exist(
    case: CreationCase,
) -> None:
    with pytest.raises(InvariantViolation, match="not implemented"):
        create_entity(case.creation_request, context(case))


class _AllowTransitionGuard:
    def validate(
        self,
        entity: LifecycleEntity,
        request: TransitionRequest[LifecycleState],
    ) -> None:
        return None


def test_existing_transition_boundary_still_rejects_fabricated_creation_self_loop() -> (
    None
):
    case = _objective_case()
    assert isinstance(case.entity, Objective)
    transition_request = TransitionRequest(
        EventId(uid(9996)),
        ObjectiveState.DRAFT,
        actor(uid(9997), ActorType.SCHEDULER),
        TransitionReason("Attempt to fake creation through transition path"),
        EntityVersion(1),
        timestamp(),
        CorrelationId(uid(9998)),
        CausationId(uid(9999)),
    )
    with pytest.raises(InvalidTransition, match="Unsupported OBJECTIVE transition"):
        transition_entity(
            case.entity,
            transition_request,
            TransitionContext((_AllowTransitionGuard(),)),
        )


def _with_substituted_id(entity: LifecycleEntity) -> LifecycleEntity:
    if isinstance(entity, Objective):
        return replace(entity, objective_id=ObjectiveId(uid(9301)))
    if isinstance(entity, Task):
        return replace(entity, task_id=TaskId(uid(9302)))
    if isinstance(entity, Run):
        return replace(entity, run_id=RunId(uid(9303)))
    if isinstance(entity, Outcome):
        return replace(entity, outcome_id=OutcomeId(uid(9304)))
    if isinstance(entity, Evaluation):
        return replace(entity, evaluation_id=EvaluationId(uid(9305)))
    return replace(entity, effect_id=EffectId(uid(9306)))


def _with_substituted_state(entity: LifecycleEntity) -> LifecycleEntity:
    if isinstance(entity, Objective):
        return replace(entity, state=ObjectiveState.ACTIVE)
    if isinstance(entity, Task):
        return replace(entity, state=TaskState.READY)
    if isinstance(entity, Run):
        return replace(entity, state=RunState.RUNNING)
    if isinstance(entity, Outcome):
        return replace(entity, state=OutcomeState.VALIDATING)
    if isinstance(entity, Evaluation):
        return replace(entity, state=EvaluationState.RUNNING)
    if entity.state is EffectState.PLANNED:
        return replace(entity, state=EffectState.SIMULATED)
    return replace(entity, state=EffectState.PLANNED)


def _with_substituted_spec_content(entity: LifecycleEntity) -> LifecycleEntity:
    if isinstance(entity, Objective):
        return replace(entity, goal="Different authorized goal")
    if isinstance(entity, Task):
        return replace(entity, definition="Different task definition")
    if isinstance(entity, Run):
        return replace(
            entity,
            execution_profile_ref=ExecutionProfileRef("different", "1"),
        )
    if isinstance(entity, Outcome):
        return replace(entity, artifact_refs=frozenset({ArtifactRef("artifact:other")}))
    if isinstance(entity, Evaluation):
        return replace(entity, method=EvaluationMethodRef("different", "1"))
    return replace(entity, target_ref=EffectTargetRef("target:other"))
