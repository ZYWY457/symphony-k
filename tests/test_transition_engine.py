"""M7 transition mechanics, authority gates, and event contracts."""

from dataclasses import MISSING, FrozenInstanceError, dataclass, fields, replace
from datetime import UTC, datetime
from types import ModuleType
from typing import cast
from uuid import UUID

import pytest

import symphony_k.domain.effect as effect_module
import symphony_k.domain.evaluation as evaluation_module
import symphony_k.domain.objective as objective_module
import symphony_k.domain.outcome as outcome_module
import symphony_k.domain.run as run_module
import symphony_k.domain.task as task_module
import symphony_k.domain.transition_engine as engine_module
from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArtifactRef,
    CausationId,
    CompletionPolicyRef,
    ConcurrencyConflict,
    CorrelationId,
    DomainEntityType,
    DomainEvent,
    DomainEventMetadata,
    DomainEventType,
    Effect,
    EffectAuthorizationFindingRecord,
    EffectExecutionAuthorizationRecord,
    EffectGovernanceFindingRecord,
    EffectId,
    EffectOperationScope,
    EffectPayloadRef,
    EffectSemanticGuard,
    EffectSimulationRecord,
    EffectSimulationRecordId,
    EffectSimulationScopeRef,
    EffectSimulationSemantics,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    Evaluation,
    EvaluationId,
    EvaluationInputReadinessDecision,
    EvaluationMethodRef,
    EvaluationSemanticDecisionRef,
    EvaluationSemanticDecisionStatus,
    EvaluationSemanticGuard,
    EvaluationStartSemantics,
    EvaluationState,
    EvaluationTargetRef,
    EvaluationVerifierIndependenceDecision,
    EventId,
    EvidenceRef,
    ExecutionProfileRef,
    InvalidDomainValue,
    InvalidTransition,
    InvariantViolation,
    Objective,
    ObjectiveActivationSemantics,
    ObjectiveBudgetValidityDecision,
    ObjectiveGovernanceApprovalDecision,
    ObjectiveId,
    ObjectivePermissionValidityDecision,
    ObjectiveSemanticDecisionRef,
    ObjectiveSemanticDecisionStatus,
    ObjectiveSemanticGuard,
    ObjectiveState,
    ObjectiveTimeHorizonValidityDecision,
    Outcome,
    OutcomeEvaluationRequestObservation,
    OutcomeEvaluationRequestRef,
    OutcomeId,
    OutcomeSemanticDecisionRef,
    OutcomeSemanticDecisionStatus,
    OutcomeSemanticGuard,
    OutcomeState,
    OutcomeValidationArtifactScope,
    OutcomeValidationPolicyDecision,
    OutcomeValidationPolicyRef,
    OutcomeValidationStartSemantics,
    PlannedEffectOrigin,
    Run,
    RunBudgetValidityDecision,
    RunExecutionBoundaryDecision,
    RunExecutionOwnershipDecision,
    RunExecutionOwnershipRef,
    RunExecutionProfileApprovalDecision,
    RunGrantValidityDecision,
    RunId,
    RunPrimaryObjectiveStateObservation,
    RunSemanticDecisionRef,
    RunSemanticDecisionStatus,
    RunSemanticGuard,
    RunStartSemantics,
    RunState,
    RunTaskStateObservation,
    RunTrustedStartConfirmationDecision,
    Task,
    TaskBudgetValidityDecision,
    TaskDefinitionGovernanceDecision,
    TaskDependencyReadinessDecision,
    TaskId,
    TaskPermissionValidityDecision,
    TaskPrimaryObjectiveStateDecision,
    TaskReadinessSemantics,
    TaskSemanticDecisionRef,
    TaskSemanticDecisionStatus,
    TaskSemanticGuard,
    TaskState,
    Timestamp,
    TransitionAuthorityDecision,
    TransitionAuthorityStatus,
    TransitionContext,
    TransitionReason,
    TransitionRequest,
    TransitionResult,
    UnauthorizedTransition,
    is_actor_eligible_for_transition_authority,
    transition_entity,
)
from symphony_k.domain.transition_engine import LifecycleEntity, LifecycleState

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
VERSION = EntityVersion(17)
EVENT_ID = EventId(VALUE)
CORRELATION_ID = CorrelationId(VALUE)
CAUSATION_ID = CausationId(OTHER)


def actor(category: ActorType = ActorType.SYSTEM) -> ActorIdentity:
    return ActorIdentity(ActorId(VALUE), category)


def instant() -> Timestamp:
    return Timestamp(datetime(2026, 9, 8, tzinfo=UTC))


@dataclass(frozen=True, slots=True)
class PassingSemanticGuard:
    """Test-only semantic guard; passing it grants no authority."""

    def validate(
        self,
        entity: LifecycleEntity,
        request: TransitionRequest[LifecycleState],
    ) -> None:
        assert entity.version == request.expected_version


@dataclass(frozen=True, slots=True)
class RejectingSemanticGuard:
    def validate(
        self,
        entity: LifecycleEntity,
        request: TransitionRequest[LifecycleState],
    ) -> None:
        raise InvariantViolation(
            f"Semantic prerequisites reject {type(entity).__name__}"
        )


PASSING_GUARD = PassingSemanticGuard()
MISSING_AUTHORITY_CONTEXT = TransitionContext((PASSING_GUARD,))


def transition_request[StateT: LifecycleState](
    target: StateT,
    *,
    expected_version: EntityVersion = VERSION,
    causation_id: CausationId | None = CAUSATION_ID,
    authority_actor: ActorIdentity | None = None,
) -> TransitionRequest[StateT]:
    if authority_actor is None:
        if isinstance(target, EvaluationState):
            authority_actor = actor(ActorType.EVALUATOR)
        elif isinstance(target, EffectState):
            authority_actor = actor(ActorType.EFFECT_CONTROLLER)
        else:
            authority_actor = actor(ActorType.SCHEDULER)
    return TransitionRequest(
        EVENT_ID,
        target,
        authority_actor,
        TransitionReason("Foundation transition requested"),
        expected_version,
        instant(),
        CORRELATION_ID,
        causation_id,
    )


def authorized_context(
    entity: LifecycleEntity,
    request: TransitionRequest[LifecycleState],
    *,
    guards: tuple[engine_module.TransitionGuard, ...] = (PASSING_GUARD,),
) -> TransitionContext:
    objective_guard = None
    if isinstance(entity, Objective):
        assert isinstance(request.target_state, ObjectiveState)
        objective_guard = activation_guard(entity, request.target_state)
    task_guard = None
    if isinstance(entity, Task):
        assert isinstance(request.target_state, TaskState)
        task_guard = readiness_guard(entity, request.target_state)
    run_guard = None
    if isinstance(entity, Run):
        assert isinstance(request.target_state, RunState)
        if (entity.state, request.target_state) == (
            RunState.PENDING,
            RunState.RUNNING,
        ):
            run_guard = run_start_guard(entity, request.target_state)
    outcome_guard = None
    if isinstance(entity, Outcome):
        assert isinstance(request.target_state, OutcomeState)
        if (entity.state, request.target_state) == (
            OutcomeState.PROPOSED,
            OutcomeState.VALIDATING,
        ):
            outcome_guard = outcome_validation_start_guard(entity, request.target_state)
    evaluation_guard = None
    if isinstance(entity, Evaluation):
        assert isinstance(request.target_state, EvaluationState)
        if (entity.state, request.target_state) == (
            EvaluationState.PENDING,
            EvaluationState.RUNNING,
        ):
            verifier = request.actor
            evaluation_guard = EvaluationSemanticGuard(
                entity.evaluation_id,
                entity.version,
                entity.state,
                request.target_state,
                request.correlation_id,
                EvaluationStartSemantics(
                    verifier,
                    EvaluationVerifierIndependenceDecision(
                        EvaluationSemanticDecisionRef("independence"),
                        EvaluationSemanticDecisionStatus.PASSED,
                        actor(ActorType.POLICY_ENGINE),
                        frozenset({EvidenceRef("independence")}),
                        entity.evaluation_id,
                        entity.version,
                        entity.target,
                        entity.method,
                        verifier,
                        request.correlation_id,
                    ),
                    EvaluationInputReadinessDecision(
                        EvaluationSemanticDecisionRef("input-readiness"),
                        EvaluationSemanticDecisionStatus.PASSED,
                        actor(ActorType.SCHEDULER),
                        frozenset({EvidenceRef("input-readiness")}),
                        entity.evaluation_id,
                        entity.version,
                        entity.target,
                        entity.method,
                        verifier,
                        request.correlation_id,
                    ),
                ),
            )
    return TransitionContext(
        guards,
        authority_decision(entity, request),
        objective_guard,
        task_guard,
        run_guard,
        outcome_guard,
        evaluation_guard,
        effect_guard(entity, request) if isinstance(entity, Effect) else None,
    )


def effect_guard(
    entity: Effect, request: TransitionRequest[LifecycleState]
) -> EffectSemanticGuard | None:
    if (entity.state, request.target_state) != (
        EffectState.PLANNED,
        EffectState.SIMULATED,
    ):
        return None
    assert isinstance(request.target_state, EffectState)
    assert entity.payload_ref is not None
    scope = EffectOperationScope(
        entity.effect_id,
        entity.version,
        entity.target_ref,
        entity.payload_ref,
        request.correlation_id,
    )
    return EffectSemanticGuard(
        entity.effect_id,
        entity.version,
        entity.state,
        request.target_state,
        entity.target_ref,
        entity.payload_ref,
        request.correlation_id,
        EffectSimulationSemantics(
            EffectSimulationRecord(
                EffectSimulationRecordId(VALUE),
                scope,
                EffectSimulationScopeRef("deterministic dry run"),
                "Prepared a dry-run representation without external mutation",
                frozenset({EvidenceRef("dry-run-evidence")}),
                ActorIdentity(ActorId(OTHER), ActorType.WORKER),
                actor(ActorType.SCHEDULER),
                instant(),
                instant(),
            )
        ),
    )


def activation_guard(
    entity: Objective, target: ObjectiveState
) -> ObjectiveSemanticGuard:
    def decision[
        DecisionT: (
            ObjectiveGovernanceApprovalDecision
            | ObjectiveBudgetValidityDecision
            | ObjectivePermissionValidityDecision
            | ObjectiveTimeHorizonValidityDecision
        )
    ](decision_type: type[DecisionT], name: str) -> DecisionT:
        return cast(
            DecisionT,
            decision_type(
                ObjectiveSemanticDecisionRef(name),
                ObjectiveSemanticDecisionStatus.PASSED,
                actor(ActorType.POLICY_ENGINE),
                frozenset({EvidenceRef(name)}),
                entity.objective_id,
                entity.version,
                CORRELATION_ID,
            ),
        )

    return ObjectiveSemanticGuard(
        entity.objective_id,
        entity.version,
        entity.state,
        target,
        CORRELATION_ID,
        ObjectiveActivationSemantics(
            decision(ObjectiveGovernanceApprovalDecision, "governance"),
            decision(ObjectiveBudgetValidityDecision, "budget"),
            decision(ObjectivePermissionValidityDecision, "permission"),
            decision(ObjectiveTimeHorizonValidityDecision, "time"),
        ),
    )


def readiness_guard(entity: Task, target: TaskState) -> TaskSemanticGuard:
    def decision[
        DecisionT: (
            TaskDefinitionGovernanceDecision
            | TaskDependencyReadinessDecision
            | TaskBudgetValidityDecision
            | TaskPermissionValidityDecision
        )
    ](decision_type: type[DecisionT], name: str) -> DecisionT:
        return cast(
            DecisionT,
            decision_type(
                TaskSemanticDecisionRef(name),
                TaskSemanticDecisionStatus.PASSED,
                actor(ActorType.POLICY_ENGINE),
                frozenset({EvidenceRef(name)}),
                entity.task_id,
                entity.version,
                CORRELATION_ID,
            ),
        )

    return TaskSemanticGuard(
        entity.task_id,
        entity.version,
        entity.state,
        target,
        CORRELATION_ID,
        TaskReadinessSemantics(
            decision(TaskDefinitionGovernanceDecision, "governance"),
            decision(TaskDependencyReadinessDecision, "dependencies"),
            decision(TaskBudgetValidityDecision, "budget"),
            decision(TaskPermissionValidityDecision, "permission"),
            TaskPrimaryObjectiveStateDecision(
                TaskSemanticDecisionRef("primary-objective"),
                TaskSemanticDecisionStatus.PASSED,
                actor(ActorType.POLICY_ENGINE),
                frozenset({EvidenceRef("primary-objective")}),
                entity.task_id,
                entity.version,
                CORRELATION_ID,
                entity.primary_objective_id,
                EntityVersion(11),
                ObjectiveState.ACTIVE,
            ),
        ),
    )


def run_start_guard(entity: Run, target: RunState) -> RunSemanticGuard:
    def decision[
        DecisionT: (
            RunExecutionBoundaryDecision
            | RunGrantValidityDecision
            | RunBudgetValidityDecision
            | RunTrustedStartConfirmationDecision
        )
    ](decision_type: type[DecisionT], name: str) -> DecisionT:
        return cast(
            DecisionT,
            decision_type(
                RunSemanticDecisionRef(name),
                RunSemanticDecisionStatus.PASSED,
                actor(ActorType.POLICY_ENGINE),
                frozenset({EvidenceRef(name)}),
                entity.run_id,
                entity.version,
                CORRELATION_ID,
            ),
        )

    return RunSemanticGuard(
        entity.run_id,
        entity.version,
        entity.state,
        target,
        CORRELATION_ID,
        RunStartSemantics(
            RunTaskStateObservation(
                RunSemanticDecisionRef("task"),
                RunSemanticDecisionStatus.PASSED,
                actor(ActorType.POLICY_ENGINE),
                frozenset({EvidenceRef("task")}),
                entity.run_id,
                entity.version,
                CORRELATION_ID,
                entity.task_id,
                EntityVersion(11),
                TaskState.IN_PROGRESS,
            ),
            RunPrimaryObjectiveStateObservation(
                RunSemanticDecisionRef("primary-objective"),
                RunSemanticDecisionStatus.PASSED,
                actor(ActorType.POLICY_ENGINE),
                frozenset({EvidenceRef("primary-objective")}),
                entity.run_id,
                entity.version,
                CORRELATION_ID,
                entity.task_id,
                EntityVersion(11),
                ObjectiveId(VALUE),
                EntityVersion(13),
                ObjectiveState.ACTIVE,
            ),
            RunExecutionOwnershipDecision(
                RunSemanticDecisionRef("ownership"),
                RunSemanticDecisionStatus.PASSED,
                actor(ActorType.POLICY_ENGINE),
                frozenset({EvidenceRef("ownership")}),
                entity.run_id,
                entity.version,
                CORRELATION_ID,
                entity.task_id,
                EntityVersion(11),
                RunExecutionOwnershipRef("ownership/record-1"),
                entity.run_id,
            ),
            RunExecutionProfileApprovalDecision(
                RunSemanticDecisionRef("profile"),
                RunSemanticDecisionStatus.PASSED,
                actor(ActorType.POLICY_ENGINE),
                frozenset({EvidenceRef("profile")}),
                entity.run_id,
                entity.version,
                CORRELATION_ID,
                entity.execution_profile_ref,
            ),
            decision(RunExecutionBoundaryDecision, "boundary"),
            decision(RunGrantValidityDecision, "grants"),
            decision(RunBudgetValidityDecision, "budget"),
            decision(RunTrustedStartConfirmationDecision, "start"),
        ),
    )


def outcome_validation_start_guard(
    entity: Outcome, target: OutcomeState
) -> OutcomeSemanticGuard:
    return OutcomeSemanticGuard(
        entity.outcome_id,
        entity.version,
        entity.state,
        target,
        CORRELATION_ID,
        OutcomeValidationStartSemantics(
            OutcomeValidationArtifactScope(
                entity.outcome_id,
                entity.version,
                CORRELATION_ID,
                entity.artifact_refs,
            ),
            OutcomeValidationPolicyDecision(
                OutcomeSemanticDecisionRef("validation-policy"),
                OutcomeSemanticDecisionStatus.PASSED,
                actor(ActorType.POLICY_ENGINE),
                frozenset({EvidenceRef("validation-policy")}),
                entity.outcome_id,
                entity.version,
                CORRELATION_ID,
                OutcomeValidationPolicyRef("validation", "v1"),
            ),
            OutcomeEvaluationRequestObservation(
                OutcomeEvaluationRequestRef(
                    "evaluation-request", EvaluationId(VALUE), EntityVersion(5)
                ),
                EvaluationId(VALUE),
                EntityVersion(5),
                EvaluationState.PENDING,
                EvaluationTargetRef(entity.outcome_id, entity.version),
                EvaluationMethodRef("method", "v1"),
                actor(ActorType.SCHEDULER),
                None,
                entity.outcome_id,
                entity.version,
                CORRELATION_ID,
            ),
        ),
    )


def authority_decision(
    entity: LifecycleEntity,
    request: TransitionRequest[LifecycleState],
    *,
    status: TransitionAuthorityStatus = TransitionAuthorityStatus.AUTHORIZED,
) -> TransitionAuthorityDecision:
    entity_type, entity_id, source_state = engine_module._entity_details(entity)
    return TransitionAuthorityDecision(
        request.actor,
        entity_type,
        entity_id,
        entity.version,
        source_state,
        request.target_state,
        status,
        request.correlation_id,
    )


def objective() -> Objective:
    return Objective(
        ObjectiveId(VALUE),
        ObjectiveState.DRAFT,
        VERSION,
        "Deliver the bounded objective",
        ("The result is independently verifiable",),
        actor(ActorType.HUMAN_OPERATOR),
        CompletionPolicyRef("objective-completion", "v1"),
    )


def task() -> Task:
    return Task(
        TaskId(VALUE),
        TaskState.DRAFT,
        VERSION,
        "Perform one bounded unit of work",
        ObjectiveId(VALUE),
        CompletionPolicyRef("task-completion", "v1"),
    )


def run() -> Run:
    return Run(
        RunId(VALUE),
        TaskId(VALUE),
        RunState.PENDING,
        VERSION,
        ExecutionProfileRef("profile", "v1"),
    )


def outcome() -> Outcome:
    return Outcome(
        OutcomeId(VALUE),
        RunId(VALUE),
        OutcomeState.PROPOSED,
        VERSION,
        actor(ActorType.WORKER),
        frozenset({ArtifactRef("candidate")}),
    )


def evaluation() -> Evaluation:
    return Evaluation(
        EvaluationId(VALUE),
        EvaluationState.PENDING,
        VERSION,
        EvaluationTargetRef(OutcomeId(VALUE), EntityVersion(3)),
        EvaluationMethodRef("method", "v1"),
    )


def effect() -> Effect:
    return Effect(
        EffectId(VALUE),
        EffectState.PLANNED,
        VERSION,
        PlannedEffectOrigin(TaskId(VALUE), actor(ActorType.WORKER)),
        EffectTargetRef("target"),
        EffectPayloadRef("payload"),
    )


SUCCESS_CASES: tuple[tuple[LifecycleEntity, LifecycleState, DomainEventType], ...] = (
    (objective(), ObjectiveState.ACTIVE, DomainEventType.OBJECTIVE_ACTIVATED),
    (task(), TaskState.READY, DomainEventType.TASK_READIED),
    (run(), RunState.RUNNING, DomainEventType.RUN_STARTED),
    (
        outcome(),
        OutcomeState.VALIDATING,
        DomainEventType.OUTCOME_VALIDATION_STARTED,
    ),
    (
        evaluation(),
        EvaluationState.RUNNING,
        DomainEventType.EVALUATION_STARTED,
    ),
    (effect(), EffectState.SIMULATED, DomainEventType.EFFECT_SIMULATED),
)

CANONICAL_HELPER_CASES: tuple[
    tuple[ModuleType, str, LifecycleEntity, LifecycleState], ...
] = (
    (
        objective_module,
        "can_objective_transition",
        objective(),
        ObjectiveState.ACTIVE,
    ),
    (task_module, "can_task_transition", task(), TaskState.READY),
    (run_module, "can_run_transition", run(), RunState.RUNNING),
    (
        outcome_module,
        "can_outcome_transition",
        outcome(),
        OutcomeState.VALIDATING,
    ),
    (
        evaluation_module,
        "can_evaluation_transition",
        evaluation(),
        EvaluationState.RUNNING,
    ),
    (effect_module, "can_effect_transition", effect(), EffectState.SIMULATED),
)


@pytest.mark.parametrize(("snapshot", "target", "event_type"), SUCCESS_CASES)
def test_success_returns_new_snapshot_and_exactly_one_matching_event(
    snapshot: LifecycleEntity,
    target: LifecycleState,
    event_type: DomainEventType,
) -> None:
    before = tuple(getattr(snapshot, field.name) for field in fields(snapshot))
    request = transition_request(target)
    result = transition_entity(
        snapshot,  # type: ignore[arg-type]
        request,  # type: ignore[arg-type]
        authorized_context(snapshot, request),
    )
    assert isinstance(result, TransitionResult)
    assert tuple(field.name for field in fields(result)) == ("entity", "event")
    assert result.entity is not snapshot
    assert result.entity.state is target
    assert result.entity.version == EntityVersion(18)
    assert snapshot.version == VERSION
    assert tuple(getattr(snapshot, field.name) for field in fields(snapshot)) == before
    changed_fields = {"state", "version"}
    if (
        isinstance(snapshot, Evaluation)
        and isinstance(target, EvaluationState)
        and target is EvaluationState.RUNNING
    ):
        changed_fields.add("verifier")
        assert isinstance(result.entity, Evaluation)
        assert result.entity.verifier == request.actor
    for field in fields(snapshot):
        if field.name not in changed_fields:
            assert getattr(result.entity, field.name) == getattr(snapshot, field.name)
    assert result.event.event_id == EVENT_ID
    assert result.event.event_type is event_type
    assert result.event.entity_version == result.entity.version
    assert result.event.actor == request.actor
    assert result.event.timestamp == instant()
    assert result.event.correlation_id == CORRELATION_ID
    assert result.event.causation_id == CAUSATION_ID
    assert result.event.reason == TransitionReason("Foundation transition requested")
    assert result.event.metadata.prior_state is snapshot.state
    assert result.event.metadata.new_state is target


def objective_event() -> DomainEvent:
    snapshot = objective()
    request = transition_request(ObjectiveState.ACTIVE)
    return transition_entity(
        snapshot, request, authorized_context(snapshot, request)
    ).event


def test_domain_event_and_metadata_are_frozen_and_typed() -> None:
    event = objective_event()
    metadata = DomainEventMetadata(
        ObjectiveState.DRAFT,
        ObjectiveState.ACTIVE,
        frozenset({("policy", "deferred-to-M7B")}),
    )
    annotated = replace(event, metadata=metadata)
    assert annotated.entity_type is DomainEntityType.OBJECTIVE
    assert annotated.entity_id == ObjectiveId(VALUE)
    assert annotated.metadata.annotations == frozenset({("policy", "deferred-to-M7B")})
    with pytest.raises(FrozenInstanceError):
        event.entity_version = EntityVersion(99)  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        metadata.new_state = ObjectiveState.BLOCKED  # type: ignore[misc]
    with pytest.raises(AttributeError):
        metadata.annotations.add(("extra", "value"))  # type: ignore[attr-defined]


def test_event_and_entity_type_inventories_are_closed_and_complete() -> None:
    assert len(DomainEntityType) == 6
    assert len(DomainEventType) == 43
    assert len(DomainEntityType.__members__) == 6
    assert len(DomainEventType.__members__) == 43


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("event_id", CorrelationId(VALUE)),
        ("event_type", "ObjectiveActivated"),
        ("entity_type", "OBJECTIVE"),
        ("entity_id", TaskId(VALUE)),
        ("entity_version", 18),
        ("actor", ActorId(VALUE)),
        ("timestamp", datetime(2026, 9, 8, tzinfo=UTC)),
        ("correlation_id", EventId(VALUE)),
        ("causation_id", EventId(VALUE)),
        ("reason", "reason"),
        ("metadata", (ObjectiveState.DRAFT, ObjectiveState.ACTIVE)),
    ],
)
def test_domain_event_rejects_raw_or_wrong_typed_provenance(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(objective_event(), **{field: invalid})  # type: ignore[arg-type]


def test_domain_event_rejects_inconsistent_lifecycle_meaning() -> None:
    event = objective_event()
    with pytest.raises(InvalidDomainValue):
        replace(event, event_type=DomainEventType.OBJECTIVE_BLOCKED)
    with pytest.raises(InvalidDomainValue):
        replace(
            event,
            metadata=DomainEventMetadata(ObjectiveState.DRAFT, ObjectiveState.ARCHIVED),
        )
    with pytest.raises(InvalidDomainValue):
        DomainEventMetadata(ObjectiveState.DRAFT, TaskState.READY)
    with pytest.raises(InvalidDomainValue):
        DomainEventMetadata(ObjectiveState.DRAFT, ObjectiveState.DRAFT)


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("event_id", CorrelationId(VALUE)),
        ("target_state", "ACTIVE"),
        ("actor", ActorId(VALUE)),
        ("reason", "reason"),
        ("expected_version", 17),
        ("timestamp", datetime(2026, 9, 8, tzinfo=UTC)),
        ("correlation_id", EventId(VALUE)),
        ("causation_id", EventId(VALUE)),
    ],
)
def test_transition_request_rejects_raw_or_wrong_typed_values(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(
            transition_request(ObjectiveState.ACTIVE),
            **{field: invalid},  # type: ignore[arg-type]
        )


def test_request_context_and_result_are_immutable_supporting_records() -> None:
    request = transition_request(ObjectiveState.ACTIVE)
    snapshot = objective()
    context = authorized_context(snapshot, request)
    result = transition_entity(snapshot, request, context)
    with pytest.raises(FrozenInstanceError):
        request.expected_version = EntityVersion(99)  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        context.guards = ()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.entity = objective()  # type: ignore[misc]
    with pytest.raises(InvalidDomainValue):
        replace(
            result,
            event=replace(result.event, entity_version=EntityVersion(99)),
        )


def test_creation_uses_absence_not_a_none_lifecycle_state() -> None:
    creation = DomainEvent(
        EventId(VALUE),
        DomainEventType.OBJECTIVE_CREATED,
        DomainEntityType.OBJECTIVE,
        ObjectiveId(VALUE),
        EntityVersion(0),
        actor(),
        instant(),
        CORRELATION_ID,
        None,
        TransitionReason("Objective registered"),
        DomainEventMetadata(None, ObjectiveState.DRAFT),
    )
    assert creation.metadata.prior_state is None
    for state_type in (
        ObjectiveState,
        TaskState,
        RunState,
        OutcomeState,
        EvaluationState,
        EffectState,
    ):
        assert "NONE" not in state_type.__members__
    with pytest.raises(InvalidDomainValue):
        replace(
            creation,
            event_type=DomainEventType.OBJECTIVE_ACTIVATED,
            metadata=DomainEventMetadata(None, ObjectiveState.ACTIVE),
        )


@pytest.mark.parametrize("expected", [EntityVersion(16), EntityVersion(18)])
def test_nonmatching_expected_version_rejects_without_mutation(
    expected: EntityVersion,
) -> None:
    snapshot = objective()
    before = (snapshot.state, snapshot.version)
    with pytest.raises(ConcurrencyConflict):
        transition_entity(
            snapshot,
            transition_request(ObjectiveState.ACTIVE, expected_version=expected),
            MISSING_AUTHORITY_CONTEXT,
        )
    assert (snapshot.state, snapshot.version) == before


@pytest.mark.parametrize("target", [ObjectiveState.DRAFT, ObjectiveState.ARCHIVED])
def test_same_state_and_unsupported_edges_reject_without_result(
    target: ObjectiveState,
) -> None:
    snapshot = objective()
    with pytest.raises(InvalidTransition):
        transition_entity(
            snapshot, transition_request(target), MISSING_AUTHORITY_CONTEXT
        )
    assert snapshot.state is ObjectiveState.DRAFT
    assert snapshot.version == VERSION


def test_cross_entity_state_rejects_as_invalid_transition() -> None:
    snapshot = objective()
    with pytest.raises(InvalidTransition):
        transition_entity(
            snapshot,
            transition_request(TaskState.READY),  # type: ignore[arg-type]
            MISSING_AUTHORITY_CONTEXT,
        )
    assert snapshot.state is ObjectiveState.DRAFT


def test_authority_success_does_not_bypass_rejecting_semantic_guard() -> None:
    snapshot = run()
    request = transition_request(RunState.RUNNING)
    rejecting_context = authorized_context(
        snapshot,
        request,
        guards=(RejectingSemanticGuard(),),
    )
    with pytest.raises(InvariantViolation):
        transition_entity(snapshot, request, rejecting_context)
    assert snapshot.state is RunState.PENDING
    assert snapshot.version == VERSION


@pytest.mark.parametrize(
    ("snapshot", "target", "ineligible_actor"),
    [
        (run(), RunState.RUNNING, ActorType.WORKER),
        (run(), RunState.ABORTED, ActorType.HUMAN_OPERATOR),
        (outcome(), OutcomeState.VALIDATING, ActorType.EVALUATOR),
        (effect(), EffectState.PENDING_COMMIT, ActorType.HUMAN_OPERATOR),
        (objective(), ObjectiveState.ACTIVE, ActorType.SYSTEM),
    ],
)
def test_ineligible_actor_with_exact_authorized_decision_is_rejected(
    snapshot: LifecycleEntity,
    target: LifecycleState,
    ineligible_actor: ActorType,
) -> None:
    request = transition_request(target, authority_actor=actor(ineligible_actor))
    before = (snapshot.state, snapshot.version)
    with pytest.raises(UnauthorizedTransition, match="not eligible"):
        transition_entity(
            snapshot,  # type: ignore[arg-type]
            request,  # type: ignore[arg-type]
            authorized_context(snapshot, request),
        )
    assert (snapshot.state, snapshot.version) == before


def test_context_requires_explicit_typed_guards_and_has_no_permissive_default() -> None:
    with pytest.raises(InvalidDomainValue):
        TransitionContext(())
    with pytest.raises(InvalidDomainValue):
        TransitionContext((object(),))  # type: ignore[arg-type]
    definitions = {field.name: field for field in fields(TransitionContext)}
    assert definitions["guards"].default is MISSING
    assert definitions["authority_decision"].default is None
    assert definitions["objective_semantic_guard"].default is None
    assert definitions["task_semantic_guard"].default is None
    assert definitions["run_semantic_guard"].default is None
    assert definitions["outcome_semantic_guard"].default is None
    with pytest.raises(InvalidDomainValue):
        TransitionContext((PASSING_GUARD,), object())  # type: ignore[arg-type]


def test_authority_decision_is_frozen_typed_and_has_minimal_status_inventory() -> None:
    snapshot = objective()
    request = transition_request(ObjectiveState.ACTIVE)
    decision = authority_decision(snapshot, request)
    assert tuple(TransitionAuthorityStatus) == (
        TransitionAuthorityStatus.AUTHORIZED,
        TransitionAuthorityStatus.DENIED,
        TransitionAuthorityStatus.UNRESOLVED,
    )
    assert tuple(field.name for field in fields(decision)) == (
        "actor",
        "entity_type",
        "entity_id",
        "observed_entity_version",
        "prior_state",
        "target_state",
        "decision",
        "correlation_id",
    )
    with pytest.raises(FrozenInstanceError):
        decision.decision = TransitionAuthorityStatus.DENIED  # type: ignore[misc]
    for field_name, invalid in (
        ("actor", ActorId(VALUE)),
        ("entity_type", "OBJECTIVE"),
        ("entity_id", TaskId(VALUE)),
        ("observed_entity_version", 17),
        ("prior_state", "DRAFT"),
        ("target_state", "ACTIVE"),
        ("decision", "AUTHORIZED"),
        ("correlation_id", EventId(VALUE)),
    ):
        with pytest.raises(InvalidDomainValue):
            replace(decision, **{field_name: invalid})  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "status",
    [TransitionAuthorityStatus.DENIED, TransitionAuthorityStatus.UNRESOLVED],
)
def test_non_authorized_decisions_reject_without_partial_transition(
    status: TransitionAuthorityStatus,
) -> None:
    snapshot = objective()
    request = transition_request(ObjectiveState.ACTIVE)
    context = TransitionContext(
        (PASSING_GUARD,), authority_decision(snapshot, request, status=status)
    )
    before = (snapshot.state, snapshot.version)
    with pytest.raises(UnauthorizedTransition):
        transition_entity(snapshot, request, context)
    assert (snapshot.state, snapshot.version) == before


def test_missing_authority_rejects_before_a_passing_semantic_guard() -> None:
    calls: list[str] = []

    @dataclass(frozen=True, slots=True)
    class RecordingSemanticGuard:
        def validate(
            self,
            entity: LifecycleEntity,
            request: TransitionRequest[LifecycleState],
        ) -> None:
            calls.append(f"{type(entity).__name__}:{request.target_state.value}")

    snapshot = objective()
    request = transition_request(ObjectiveState.ACTIVE)
    before = (snapshot.state, snapshot.version)
    with pytest.raises(UnauthorizedTransition):
        transition_entity(
            snapshot, request, TransitionContext((RecordingSemanticGuard(),))
        )
    assert calls == []
    assert (snapshot.state, snapshot.version) == before


def test_exact_authority_reaches_semantic_guards_and_preserves_actor_provenance() -> (
    None
):
    calls: list[ActorIdentity] = []

    @dataclass(frozen=True, slots=True)
    class RecordingSemanticGuard:
        def validate(
            self,
            entity: LifecycleEntity,
            request: TransitionRequest[LifecycleState],
        ) -> None:
            calls.append(request.actor)

    snapshot = objective()
    request = transition_request(ObjectiveState.ACTIVE)
    decision = authority_decision(snapshot, request)
    result = transition_entity(
        snapshot,
        request,
        TransitionContext(
            (RecordingSemanticGuard(),),
            decision,
            activation_guard(snapshot, ObjectiveState.ACTIVE),
        ),
    )
    assert calls == [request.actor]
    assert request.actor == decision.actor == result.event.actor
    assert result.event.entity_version == result.entity.version


def test_every_incompatible_authority_binding_rejects_without_mutation() -> None:
    snapshot = objective()
    request = transition_request(ObjectiveState.ACTIVE)
    exact = authority_decision(snapshot, request)
    incompatible = (
        replace(exact, actor=ActorIdentity(ActorId(OTHER), ActorType.SYSTEM)),
        replace(
            exact,
            entity_type=DomainEntityType.TASK,
            entity_id=TaskId(VALUE),
            prior_state=TaskState.DRAFT,
            target_state=TaskState.READY,
        ),
        replace(exact, entity_id=ObjectiveId(OTHER)),
        replace(exact, observed_entity_version=EntityVersion(16)),
        replace(exact, observed_entity_version=EntityVersion(18)),
        replace(exact, prior_state=ObjectiveState.BLOCKED),
        replace(exact, target_state=ObjectiveState.BLOCKED),
        replace(exact, correlation_id=CorrelationId(OTHER)),
    )
    before = (snapshot.state, snapshot.version)
    for candidate in incompatible:
        with pytest.raises(UnauthorizedTransition):
            transition_entity(
                snapshot, request, TransitionContext((PASSING_GUARD,), candidate)
            )
        assert (snapshot.state, snapshot.version) == before


@pytest.mark.parametrize(
    "actor_type",
    [ActorType.SYSTEM, ActorType.HUMAN_OPERATOR, ActorType.WORKER],
)
def test_actor_categories_receive_no_implicit_superuser_authority(
    actor_type: ActorType,
) -> None:
    snapshot = objective()
    request = replace(
        transition_request(ObjectiveState.ACTIVE), actor=actor(actor_type)
    )
    with pytest.raises(UnauthorizedTransition):
        transition_entity(snapshot, request, MISSING_AUTHORITY_CONTEXT)


def test_transition_authority_is_distinct_from_m6_effect_records() -> None:
    authority_type = TransitionAuthorityDecision
    assert (
        len(
            {
                authority_type,
                EffectExecutionAuthorizationRecord,
                EffectAuthorizationFindingRecord,
                EffectGovernanceFindingRecord,
            }
        )
        == 4
    )
    authority_fields = {field.name for field in fields(authority_type)}
    assert "prior_state" in authority_fields
    assert "target_state" in authority_fields
    assert "authorization_id" not in authority_fields
    assert "finding_id" not in authority_fields


def test_engine_delegates_to_the_canonical_topology_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[ObjectiveState, ObjectiveState]] = []
    canonical = objective_module.can_objective_transition

    def recording_helper(source: ObjectiveState, target: ObjectiveState) -> bool:
        calls.append((source, target))
        return canonical(source, target)

    monkeypatch.setattr(
        objective_module,
        "can_objective_transition",
        recording_helper,
    )
    snapshot = objective()
    request = transition_request(ObjectiveState.ACTIVE)
    transition_entity(snapshot, request, authorized_context(snapshot, request))
    assert calls
    assert set(calls) == {(ObjectiveState.DRAFT, ObjectiveState.ACTIVE)}


@pytest.mark.parametrize(
    ("topology_module", "helper_name", "snapshot", "target"),
    CANONICAL_HELPER_CASES,
)
def test_every_entity_family_depends_on_its_canonical_topology_helper(
    monkeypatch: pytest.MonkeyPatch,
    topology_module: ModuleType,
    helper_name: str,
    snapshot: LifecycleEntity,
    target: LifecycleState,
) -> None:
    monkeypatch.setattr(
        topology_module,
        helper_name,
        lambda source, target: False,
    )
    with pytest.raises(InvalidTransition):
        transition_entity(
            snapshot,  # type: ignore[arg-type]
            transition_request(target),  # type: ignore[arg-type]
            MISSING_AUTHORITY_CONTEXT,
        )
    assert not any(name.endswith("_TRANSITIONS") for name in vars(engine_module))


def test_existing_snapshot_invariant_rejection_is_typed_and_has_no_partial_result() -> (
    None
):
    snapshot = replace(evaluation(), state=EvaluationState.RUNNING)
    request = transition_request(EvaluationState.COMPLETED)
    with pytest.raises(InvariantViolation, match="Canonical Evaluation semantic guard"):
        transition_entity(
            snapshot,
            request,
            authorized_context(snapshot, request),
        )
    assert snapshot.state is EvaluationState.RUNNING
    assert snapshot.result is None
    assert snapshot.version == VERSION


def test_transition_authority_has_no_m7c_or_m8_runtime_boundaries() -> None:
    for name in (
        "Repository",
        "UnitOfWork",
        "Transaction",
        "Persistence",
        "Outbox",
        "MessageBus",
        "CompletionPolicyEvaluator",
        "PolicyEngine",
        "PermissionEngine",
        "AllowAllAuthority",
        "EffectExecutor",
        "execute_effect",
        "resolve_evaluation",
        "failover",
    ):
        assert not hasattr(engine_module, name)
    snapshot = effect()
    request = transition_request(EffectState.SIMULATED)
    result = transition_entity(snapshot, request, authorized_context(snapshot, request))
    assert result.entity.state is EffectState.SIMULATED
    assert effect().state is EffectState.PLANNED


def test_public_eligibility_query_does_not_replace_m7b1_authority() -> None:
    assert is_actor_eligible_for_transition_authority(
        DomainEntityType.RUN,
        RunState.PENDING,
        RunState.RUNNING,
        ActorType.SCHEDULER,
    )
    snapshot = run()
    request = transition_request(RunState.RUNNING)
    with pytest.raises(UnauthorizedTransition, match="decision is required"):
        transition_entity(snapshot, request, MISSING_AUTHORITY_CONTEXT)
