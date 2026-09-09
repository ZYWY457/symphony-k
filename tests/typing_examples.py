"""Static-only API contracts checked by `mypy src tests`.

Targeted ignores are negative assertions: strict mypy rejects an unused ignore
if these invalid argument combinations ever become type-compatible.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, assert_type
from uuid import UUID

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArbitrationDisposition,
    ArtifactRef,
    CausationId,
    CompletionPolicyRef,
    ConflictSetVersion,
    CorrelationId,
    DomainEntityType,
    DomainEvent,
    DomainEventMetadata,
    DomainEventType,
    Effect,
    EffectAttributionId,
    EffectAuthorizationFindingId,
    EffectCompensationCompletionId,
    EffectCompensationCompletionRecord,
    EffectCompensationPlanId,
    EffectCompensationPlanRecord,
    EffectDeduplicationRef,
    EffectExecutionAuthorizationId,
    EffectExecutionAuthorizationRecord,
    EffectExternalOperationRef,
    EffectGovernanceFindingId,
    EffectId,
    EffectIncidentId,
    EffectIncidentRecord,
    EffectIncidentRecordId,
    EffectIncidentStatus,
    EffectObservationId,
    EffectObservationRecord,
    EffectOccurrenceStatus,
    EffectPayloadRef,
    EffectPreparationRecord,
    EffectPreparationRecordId,
    EffectRollbackRecord,
    EffectRollbackRecordId,
    EffectState,
    EffectTargetRef,
    EffectVerificationRecord,
    EffectVerificationRecordId,
    EntityVersion,
    Evaluation,
    EvaluationArbitrationId,
    EvaluationArbitrationMemberDecision,
    EvaluationArbitrationPolicyRef,
    EvaluationArbitrationRecord,
    EvaluationConfidence,
    EvaluationConflictMemberRef,
    EvaluationConflictScopeRef,
    EvaluationConflictSetId,
    EvaluationConflictSetRecord,
    EvaluationConflictSetRef,
    EvaluationEffectiveUseView,
    EvaluationId,
    EvaluationInvalidationId,
    EvaluationInvalidationRecord,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationState,
    EvaluationTargetRef,
    EvaluationVerdict,
    EventId,
    EvidenceRef,
    ExecutionProfileRef,
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
    ObservedEffectOrigin,
    Outcome,
    OutcomeId,
    OutcomeState,
    PlannedEffectOrigin,
    Run,
    RunId,
    RunState,
    Task,
    TaskId,
    TaskState,
    Timestamp,
    TransitionAuthorityDecision,
    TransitionAuthorityStatus,
    TransitionContext,
    TransitionReason,
    TransitionRequest,
    TransitionResult,
    can_arbitrate_evaluation_conflict_set,
    can_attach_effect_incident_record,
    can_attach_effect_observation,
    can_attach_effect_preparation_record,
    can_attach_effect_rollback_record,
    can_authorize_effect_preparation,
    can_complete_effect_compensation_plan,
    can_effect_transition,
    can_evaluation_transition,
    can_extend_evaluation_conflict_set,
    can_follow_effect_incident_record,
    can_follow_effect_observation,
    can_invalidate_evaluation,
    can_objective_transition,
    can_outcome_transition,
    can_run_transition,
    can_task_transition,
    can_use_effect_verification_for_authorization,
    can_verify_effect_preparation,
    derive_evaluation_effective_use,
    is_actor_eligible_for_transition_authority,
    transition_entity,
)

if TYPE_CHECKING:
    value = UUID("12345678-1234-4234-8234-123456789abc")

    def requires_objective(identity: ObjectiveId) -> ObjectiveId:
        return identity

    assert_type(ObjectiveId.new(), ObjectiveId)
    assert_type(TaskId.new(), TaskId)
    assert_type(RunId.new(), RunId)
    assert_type(OutcomeId.new(), OutcomeId)
    assert_type(EvaluationId.new(), EvaluationId)
    assert_type(EvaluationArbitrationId.new(), EvaluationArbitrationId)
    assert_type(EvaluationConflictSetId.new(), EvaluationConflictSetId)
    assert_type(EvaluationInvalidationId.new(), EvaluationInvalidationId)
    assert_type(EffectId.new(), EffectId)
    assert_type(EffectObservationId.new(), EffectObservationId)
    assert_type(EventId.new(), EventId)
    assert_type(CausationId.new(), CausationId)
    assert_type(ActorId.new(), ActorId)
    assert_type(CorrelationId.new(), CorrelationId)
    assert_type(ObjectiveId.from_string(str(value)), ObjectiveId)
    assert_type(requires_objective(ObjectiveId(value)), ObjectiveId)

    requires_objective(TaskId(value))  # type: ignore[arg-type]
    requires_objective(RunId(value))  # type: ignore[arg-type]
    requires_objective(OutcomeId(value))  # type: ignore[arg-type]
    requires_objective(EvaluationId(value))  # type: ignore[arg-type]
    requires_objective(EvaluationArbitrationId(value))  # type: ignore[arg-type]
    requires_objective(EvaluationConflictSetId(value))  # type: ignore[arg-type]
    requires_objective(EvaluationInvalidationId(value))  # type: ignore[arg-type]
    requires_objective(EffectId(value))  # type: ignore[arg-type]
    requires_objective(EffectObservationId(value))  # type: ignore[arg-type]
    requires_objective(ActorId(value))  # type: ignore[arg-type]
    requires_objective(CorrelationId(value))  # type: ignore[arg-type]
    requires_objective(value)  # type: ignore[arg-type]
    requires_objective(str(value))  # type: ignore[arg-type]
    ActorIdentity(TaskId(value), ActorType.WORKER)  # type: ignore[arg-type]
    ActorIdentity(ActorId(value), "SYSTEM")  # type: ignore[arg-type]

    policy = CompletionPolicyRef("definition", "revision")
    designation = ActorIdentity(ActorId(value), ActorType.HUMAN_OPERATOR)
    assert_type(
        Objective(
            ObjectiveId(value),
            ObjectiveState.DRAFT,
            EntityVersion(7),
            "Bounded result",
            ("Criterion",),
            designation,
            policy,
        ),
        Objective,
    )
    Objective(
        TaskId(value),  # type: ignore[arg-type]
        ObjectiveState.DRAFT,
        EntityVersion(7),
        "Result",
        ("Criterion",),
        designation,
        policy,
    )
    can_objective_transition("DRAFT", ObjectiveState.ACTIVE)  # type: ignore[arg-type]
    CompletionPolicyRef("definition", EntityVersion(1))  # type: ignore[arg-type]

    assert_type(
        Task(
            TaskId(value),
            TaskState.DRAFT,
            EntityVersion(7),
            "Bounded work",
            ObjectiveId(value),
            policy,
        ),
        Task,
    )
    Task(
        TaskId(value),
        TaskState.DRAFT,
        EntityVersion(7),
        "Work",
        TaskId(value),  # type: ignore[arg-type]
        policy,
    )
    Task(
        TaskId(value),
        TaskState.DRAFT,
        EntityVersion(7),
        "Work",
        ObjectiveId(value),
        policy,
        frozenset({TaskId(value)}),  # type: ignore[arg-type]
    )
    can_task_transition(ObjectiveState.DRAFT, TaskState.READY)  # type: ignore[arg-type]
    can_task_transition("DRAFT", TaskState.READY)  # type: ignore[arg-type]

    profile = ExecutionProfileRef("profile", "revision")
    run = Run(RunId(value), TaskId(value), RunState.PENDING, EntityVersion(7), profile)
    assert_type(run, Run)
    assert_type(run.task_id, TaskId)
    assert_type(run.predecessor_run_id, RunId | None)

    def requires_run_id(identity: RunId) -> RunId:
        return identity

    requires_run_id(ObjectiveId(value))  # type: ignore[arg-type]
    requires_run_id(TaskId(value))  # type: ignore[arg-type]
    requires_run_id(value)  # type: ignore[arg-type]
    requires_run_id(str(value))  # type: ignore[arg-type]
    Run(
        TaskId(value),  # type: ignore[arg-type]
        TaskId(value),
        RunState.PENDING,
        EntityVersion(7),
        profile,
    )
    task_snapshot = Task(
        TaskId(value),
        TaskState.DRAFT,
        EntityVersion(7),
        "Work",
        ObjectiveId(value),
        policy,
    )
    Run(
        RunId(value),
        task_snapshot,  # type: ignore[arg-type]
        RunState.PENDING,
        EntityVersion(7),
        profile,
    )
    Run(
        RunId(value),
        TaskId(value),
        RunState.PENDING,
        EntityVersion(7),
        profile,
        TaskId(value),  # type: ignore[arg-type]
    )
    can_run_transition(TaskState.READY, RunState.RUNNING)  # type: ignore[arg-type]
    can_run_transition("PENDING", RunState.RUNNING)  # type: ignore[arg-type]

    artifacts = frozenset({ArtifactRef("candidate")})
    candidate = Outcome(
        OutcomeId(value),
        RunId(value),
        OutcomeState.PROPOSED,
        EntityVersion(7),
        designation,
        artifacts,
    )
    assert_type(candidate.outcome_id, OutcomeId)
    assert_type(candidate.run_id, RunId)
    assert_type(candidate.producer, ActorIdentity)
    assert_type(candidate.artifact_refs, frozenset[ArtifactRef])
    assert_type(candidate.evidence_refs, frozenset[EvidenceRef])

    def requires_artifact(reference: ArtifactRef) -> ArtifactRef:
        return reference

    def requires_evidence(reference: EvidenceRef) -> EvidenceRef:
        return reference

    requires_artifact(EvidenceRef("same"))  # type: ignore[arg-type]
    requires_evidence(ArtifactRef("same"))  # type: ignore[arg-type]
    Outcome(
        RunId(value),  # type: ignore[arg-type]
        RunId(value),
        OutcomeState.PROPOSED,
        EntityVersion(7),
        designation,
        artifacts,
    )
    Outcome(
        OutcomeId(value),
        run,  # type: ignore[arg-type]
        OutcomeState.PROPOSED,
        EntityVersion(7),
        designation,
        artifacts,
    )
    Outcome(
        OutcomeId(value),
        RunId(value),
        OutcomeState.PROPOSED,
        EntityVersion(7),
        ActorId(value),  # type: ignore[arg-type]
        artifacts,
    )
    can_outcome_transition(RunState.COMPLETED, OutcomeState.ACCEPTED)  # type: ignore[arg-type]
    can_outcome_transition("PROPOSED", OutcomeState.ACCEPTED)  # type: ignore[arg-type]

    entity_target = EvaluationTargetRef(RunId(value), EntityVersion(7))
    outcome_target = EvaluationTargetRef(OutcomeId(value), EntityVersion(7))
    effect_target = EvaluationTargetRef(EffectId(value), EntityVersion(7))
    evidence_target = EvaluationTargetRef(EvidenceRef("anchor"))
    assert_type(entity_target, EvaluationTargetRef)
    if isinstance(entity_target.reference, RunId):
        assert_type(entity_target.reference, RunId)
    if isinstance(outcome_target.reference, OutcomeId):
        assert_type(outcome_target.reference, OutcomeId)
    if isinstance(effect_target.reference, EffectId):
        assert_type(effect_target.reference, EffectId)
    if isinstance(evidence_target.reference, EvidenceRef):
        assert_type(evidence_target.reference, EvidenceRef)
    EvaluationTargetRef(RunId(value))  # type: ignore[call-overload]
    EvaluationTargetRef(EvidenceRef("anchor"), EntityVersion(7))  # type: ignore[call-overload]
    EvaluationTargetRef(TaskId(value), EntityVersion(7))  # type: ignore[call-overload]
    EvaluationTargetRef(ArtifactRef("anchor"))  # type: ignore[call-overload]
    EvaluationTargetRef(value, EntityVersion(7))  # type: ignore[call-overload]

    judgment = EvaluationVerdict("Supplied judgment")
    confidence = EvaluationConfidence("Supplied confidence representation")
    original_result = EvaluationResult(
        judgment, confidence, "Reasoning", frozenset({EvidenceRef("evidence")})
    )
    evaluation = Evaluation(
        EvaluationId(value),
        EvaluationState.COMPLETED,
        EntityVersion(7),
        entity_target,
        EvaluationMethodRef("method", "revision"),
        designation,
        original_result,
    )
    assert_type(evaluation.target, EvaluationTargetRef)
    assert_type(evaluation.result, EvaluationResult | None)
    EvaluationResult(confidence, confidence, "Reasoning")  # type: ignore[arg-type]
    EvaluationResult(judgment, judgment, "Reasoning")  # type: ignore[arg-type]
    artifact_only = frozenset({ArtifactRef("evidence")})
    EvaluationResult(
        judgment,
        confidence,
        "Reasoning",
        artifact_only,  # type: ignore[arg-type]
    )
    can_evaluation_transition(OutcomeState.VALIDATING, EvaluationState.COMPLETED)  # type: ignore[arg-type]

    def requires_conflict_set_id(
        identity: EvaluationConflictSetId,
    ) -> EvaluationConflictSetId:
        return identity

    def requires_correlation_id(identity: CorrelationId) -> CorrelationId:
        return identity

    def requires_conflict_version(version: ConflictSetVersion) -> ConflictSetVersion:
        return version

    conflict_set_id = EvaluationConflictSetId(value)
    correlation_id = CorrelationId(value)
    conflict_version = ConflictSetVersion(17)
    assert_type(requires_conflict_set_id(conflict_set_id), EvaluationConflictSetId)
    assert_type(requires_correlation_id(correlation_id), CorrelationId)
    assert_type(requires_conflict_version(conflict_version), ConflictSetVersion)
    requires_conflict_set_id(EvaluationId(value))  # type: ignore[arg-type]
    requires_conflict_set_id(CorrelationId(value))  # type: ignore[arg-type]
    requires_correlation_id(EvaluationConflictSetId(value))  # type: ignore[arg-type]
    requires_correlation_id(EvaluationId(value))  # type: ignore[arg-type]
    requires_conflict_version(EntityVersion(17))  # type: ignore[arg-type]

    conflict_member = EvaluationConflictMemberRef(EvaluationId(value), EntityVersion(7))
    conflict_scope = EvaluationConflictScopeRef("acceptance scope")
    conflict_ref = EvaluationConflictSetRef(conflict_set_id, conflict_version)
    assert_type(conflict_member.evaluation_id, EvaluationId)
    assert_type(conflict_member.observed_version, EntityVersion)
    assert_type(conflict_ref.version, ConflictSetVersion)
    EvaluationConflictMemberRef(
        EvaluationConflictSetId(value),  # type: ignore[arg-type]
        EntityVersion(7),
    )
    EvaluationConflictMemberRef(
        EvaluationId(value),
        ConflictSetVersion(7),  # type: ignore[arg-type]
    )
    EvaluationConflictSetRef(
        CorrelationId(value),  # type: ignore[arg-type]
        conflict_version,
    )
    EvaluationConflictSetRef(
        conflict_set_id,
        EntityVersion(17),  # type: ignore[arg-type]
    )

    conflict_record = EvaluationConflictSetRecord(
        conflict_set_id,
        conflict_version,
        None,
        frozenset({conflict_member}),
        conflict_scope,
        "Material disagreement",
        frozenset({EvidenceRef("opposing evidence")}),
        designation,
        Timestamp(datetime(2026, 9, 7, tzinfo=UTC)),
        correlation_id,
    )
    assert_type(conflict_record.members, frozenset[EvaluationConflictMemberRef])
    assert_type(
        can_extend_evaluation_conflict_set(conflict_record, conflict_record), bool
    )
    EvaluationConflictSetRecord(
        EvaluationId(value),  # type: ignore[arg-type]
        conflict_version,
        None,
        frozenset({conflict_member}),
        conflict_scope,
        "Material disagreement",
        frozenset({EvidenceRef("opposing evidence")}),
        designation,
        Timestamp(datetime(2026, 9, 7, tzinfo=UTC)),
        correlation_id,
    )

    def requires_arbitration_id(
        identity: EvaluationArbitrationId,
    ) -> EvaluationArbitrationId:
        return identity

    arbitration_id = EvaluationArbitrationId(value)
    assert_type(requires_arbitration_id(arbitration_id), EvaluationArbitrationId)
    requires_arbitration_id(EvaluationId(value))  # type: ignore[arg-type]
    requires_arbitration_id(EvaluationConflictSetId(value))  # type: ignore[arg-type]
    requires_arbitration_id(CorrelationId(value))  # type: ignore[arg-type]

    arbitration_decision = EvaluationArbitrationMemberDecision(
        EvaluationId(value),
        EntityVersion(7),
        ArbitrationDisposition.UPHELD,
        judgment,
        judgment,
    )
    arbitration_record = EvaluationArbitrationRecord(
        arbitration_id,
        conflict_ref,
        frozenset({arbitration_decision}),
        "Rationale",
        frozenset({EvidenceRef("arbitration evidence")}),
        EvaluationArbitrationPolicyRef("policy", "revision"),
        designation,
        Timestamp(datetime(2026, 9, 7, tzinfo=UTC)),
        correlation_id,
    )
    assert_type(arbitration_decision.observed_version, EntityVersion)
    assert_type(
        arbitration_record.decisions, frozenset[EvaluationArbitrationMemberDecision]
    )
    assert_type(
        can_arbitrate_evaluation_conflict_set(conflict_record, arbitration_record),
        bool,
    )
    EvaluationArbitrationMemberDecision(
        EvaluationConflictSetId(value),  # type: ignore[arg-type]
        EntityVersion(7),
        ArbitrationDisposition.UPHELD,
        judgment,
        judgment,
    )
    EvaluationArbitrationMemberDecision(
        EvaluationId(value),
        ConflictSetVersion(7),  # type: ignore[arg-type]
        ArbitrationDisposition.UPHELD,
        judgment,
        judgment,
    )
    EvaluationArbitrationRecord(
        EvaluationId(value),  # type: ignore[arg-type]
        conflict_ref,
        frozenset({arbitration_decision}),
        "Rationale",
        frozenset({EvidenceRef("arbitration evidence")}),
        EvaluationArbitrationPolicyRef("policy", "revision"),
        designation,
        Timestamp(datetime(2026, 9, 7, tzinfo=UTC)),
        correlation_id,
    )

    def requires_invalidation_id(
        identity: EvaluationInvalidationId,
    ) -> EvaluationInvalidationId:
        return identity

    invalidation_id = EvaluationInvalidationId(value)
    assert_type(requires_invalidation_id(invalidation_id), EvaluationInvalidationId)
    requires_invalidation_id(EvaluationId(value))  # type: ignore[arg-type]
    requires_invalidation_id(EvaluationArbitrationId(value))  # type: ignore[arg-type]
    requires_invalidation_id(EvaluationConflictSetId(value))  # type: ignore[arg-type]
    requires_invalidation_id(CorrelationId(value))  # type: ignore[arg-type]

    invalidation_record = EvaluationInvalidationRecord(
        invalidation_id,
        EvaluationId(value),
        EntityVersion(7),
        "Established verifier failure",
        frozenset({EvidenceRef("invalidation evidence")}),
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        correlation_id,
    )
    assert_type(invalidation_record.observed_version, EntityVersion)
    assert_type(invalidation_record.evidence_refs, frozenset[EvidenceRef])
    assert_type(can_invalidate_evaluation(evaluation, invalidation_record), bool)
    EvaluationInvalidationRecord(
        EvaluationId(value),  # type: ignore[arg-type]
        EvaluationId(value),
        EntityVersion(7),
        "Established verifier failure",
        frozenset({EvidenceRef("invalidation evidence")}),
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        correlation_id,
    )

    def requires_rollback_record_id(
        identity: EffectRollbackRecordId,
    ) -> EffectRollbackRecordId:
        return identity

    def requires_compensation_plan_id(
        identity: EffectCompensationPlanId,
    ) -> EffectCompensationPlanId:
        return identity

    def requires_compensation_completion_id(
        identity: EffectCompensationCompletionId,
    ) -> EffectCompensationCompletionId:
        return identity

    rollback_record_id = EffectRollbackRecordId(value)
    compensation_plan_id = EffectCompensationPlanId(value)
    compensation_completion_id = EffectCompensationCompletionId(value)
    assert_type(requires_rollback_record_id(rollback_record_id), EffectRollbackRecordId)
    assert_type(
        requires_compensation_plan_id(compensation_plan_id), EffectCompensationPlanId
    )
    assert_type(
        requires_compensation_completion_id(compensation_completion_id),
        EffectCompensationCompletionId,
    )
    requires_rollback_record_id(EffectId(value))  # type: ignore[arg-type]
    requires_compensation_plan_id(EffectObservationId(value))  # type: ignore[arg-type]
    requires_compensation_completion_id(CorrelationId(value))  # type: ignore[arg-type]

    rollback_record = EffectRollbackRecord(
        rollback_record_id,
        EffectId(value),
        EntityVersion(7),
        EffectObservationId(value),
        EffectExternalOperationRef("restoration operation"),
        "Independent evidence established restoration",
        frozenset({EvidenceRef("restoration evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    compensation_plan = EffectCompensationPlanRecord(
        compensation_plan_id,
        EffectId(value),
        EntityVersion(7),
        EffectObservationId(value),
        frozenset({EffectId(UUID("87654321-4321-4321-8321-cba987654321"))}),
        "Separate governed Effect corrects the mutation",
        frozenset({EvidenceRef("plan evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    compensation_completion = EffectCompensationCompletionRecord(
        compensation_completion_id,
        compensation_plan_id,
        EffectId(value),
        EntityVersion(7),
        EffectObservationId(value),
        "Independent evidence supports completion",
        "Original mutation remains historical fact",
        frozenset({EvidenceRef("completion evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    assert_type(rollback_record.rollback_record_id, EffectRollbackRecordId)
    assert_type(compensation_plan.plan_id, EffectCompensationPlanId)
    assert_type(compensation_completion.completion_id, EffectCompensationCompletionId)
    remediation_effect = Effect(
        EffectId(value),
        EffectState.COMMITTED,
        EntityVersion(7),
        ObservedEffectOrigin(
            EffectExternalOperationRef("original operation"),
            frozenset({EvidenceRef("original observation evidence")}),
            designation,
            Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
            None,
            None,
            "Attribution unknown",
        ),
        EffectTargetRef("target"),
        None,
    )
    assert_type(
        can_attach_effect_rollback_record(remediation_effect, rollback_record), bool
    )
    assert_type(
        can_complete_effect_compensation_plan(
            compensation_plan, compensation_completion
        ),
        bool,
    )
    EffectRollbackRecord(
        EffectId(value),  # type: ignore[arg-type]
        EffectId(value),
        EntityVersion(7),
        EffectObservationId(value),
        EffectExternalOperationRef("restoration operation"),
        "Independent evidence established restoration",
        frozenset({EvidenceRef("restoration evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    EffectCompensationPlanRecord(
        compensation_plan_id,
        EffectId(value),
        EntityVersion(7),
        EffectId(value),  # type: ignore[arg-type]
        frozenset({EffectId(UUID("87654321-4321-4321-8321-cba987654321"))}),
        "Separate governed Effect corrects the mutation",
        frozenset({EvidenceRef("plan evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    EffectCompensationCompletionRecord(
        compensation_completion_id,
        EffectId(value),  # type: ignore[arg-type]
        EffectId(value),
        EntityVersion(7),
        EffectObservationId(value),
        "Independent evidence supports completion",
        "Original mutation remains historical fact",
        frozenset({EvidenceRef("completion evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    can_attach_effect_rollback_record(
        remediation_effect,
        compensation_plan,  # type: ignore[arg-type]
    )
    can_complete_effect_compensation_plan(
        compensation_plan,
        rollback_record,  # type: ignore[arg-type]
    )

    effect_target_ref = EffectTargetRef("target")
    effect_payload_ref = EffectPayloadRef("payload")
    external_operation_ref = EffectExternalOperationRef("operation")
    planned_effect_origin = PlannedEffectOrigin(
        TaskId(value), designation, RunId(value)
    )
    observed_effect_origin = ObservedEffectOrigin(
        external_operation_ref,
        frozenset({EvidenceRef("observation")}),
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        None,
        None,
        "Attribution unknown",
    )
    planned_effect = Effect(
        EffectId(value),
        EffectState.PLANNED,
        EntityVersion(7),
        planned_effect_origin,
        effect_target_ref,
        effect_payload_ref,
    )
    observed_effect = Effect(
        EffectId(value),
        EffectState.COMMITTED,
        EntityVersion(7),
        observed_effect_origin,
        effect_target_ref,
        None,
    )
    assert_type(planned_effect, Effect)
    assert_type(observed_effect.origin, PlannedEffectOrigin | ObservedEffectOrigin)
    assert_type(observed_effect.payload_ref, EffectPayloadRef | None)
    observation = EffectObservationRecord(
        EffectObservationId(value),
        EffectId(value),
        EntityVersion(7),
        external_operation_ref,
        EffectDeduplicationRef("provider key"),
        EffectOccurrenceStatus.CONFIRMED,
        effect_target_ref,
        None,
        frozenset({EvidenceRef("observation evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        None,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        CorrelationId(value),
    )
    assert_type(observation.observation_id, EffectObservationId)
    assert_type(observation.deduplication_ref, EffectDeduplicationRef)
    assert_type(
        can_attach_effect_observation(observed_effect, observation),
        bool,
    )
    assert_type(can_follow_effect_observation(observation, observation), bool)
    EffectObservationRecord(
        EffectId(value),  # type: ignore[arg-type]
        EffectId(value),
        EntityVersion(7),
        external_operation_ref,
        EffectDeduplicationRef("provider key"),
        EffectOccurrenceStatus.CONFIRMED,
        effect_target_ref,
        None,
        frozenset({EvidenceRef("observation evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        None,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        CorrelationId(value),
    )
    EffectObservationRecord(
        EffectObservationId(value),
        EffectId(value),
        EntityVersion(7),
        external_operation_ref,
        EffectDeduplicationRef("provider key"),
        EffectOccurrenceStatus.CONFIRMED,
        effect_target_ref,
        None,
        frozenset({EvidenceRef("observation evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        None,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        EffectId(value),  # type: ignore[arg-type]
    )
    can_attach_effect_observation(
        observed_effect,
        observed_effect,  # type: ignore[arg-type]
    )
    EffectTargetRef(effect_payload_ref)  # type: ignore[arg-type]
    EffectPayloadRef(effect_target_ref)  # type: ignore[arg-type]
    EffectExternalOperationRef(effect_target_ref)  # type: ignore[arg-type]
    EffectTargetRef(EvidenceRef("evidence"))  # type: ignore[arg-type]
    EffectPayloadRef(EvidenceRef("evidence"))  # type: ignore[arg-type]
    EffectExternalOperationRef(EvidenceRef("evidence"))  # type: ignore[arg-type]
    EvidenceRef(effect_target_ref)  # type: ignore[arg-type]
    PlannedEffectOrigin(RunId(value), designation)  # type: ignore[arg-type]
    PlannedEffectOrigin(TaskId(value), ActorId(value))  # type: ignore[arg-type]
    ObservedEffectOrigin(
        effect_target_ref,  # type: ignore[arg-type]
        frozenset({EvidenceRef("observation")}),
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        None,
        None,
        "Attribution unknown",
    )
    Effect(
        TaskId(value),  # type: ignore[arg-type]
        EffectState.PLANNED,
        EntityVersion(7),
        planned_effect_origin,
        effect_target_ref,
        effect_payload_ref,
    )
    Effect(
        EffectId(value),
        EffectState.PLANNED,
        EntityVersion(7),
        planned_effect_origin,
        effect_payload_ref,  # type: ignore[arg-type]
        effect_payload_ref,
    )
    can_effect_transition(OutcomeState.PROPOSED, EffectState.COMMITTED)  # type: ignore[arg-type]

    effective_view = derive_evaluation_effective_use(
        evaluation,
        applicable_conflict_sets=frozenset({conflict_record}),
        arbitration_records=frozenset({arbitration_record}),
        invalidation_records=frozenset({invalidation_record}),
    )
    assert_type(effective_view, EvaluationEffectiveUseView)
    assert_type(effective_view.effective_judgement, EvaluationVerdict | None)
    assert_type(
        effective_view.applicable_conflicts, frozenset[EvaluationConflictSetRef]
    )
    derive_evaluation_effective_use(
        evaluation,
        applicable_conflict_sets=frozenset({arbitration_record}),  # type: ignore[arg-type]
        arbitration_records=frozenset({arbitration_record}),
        invalidation_records=frozenset({invalidation_record}),
    )
    EvaluationInvalidationRecord(
        invalidation_id,
        EvaluationInvalidationId(value),  # type: ignore[arg-type]
        EntityVersion(7),
        "Established verifier failure",
        frozenset({EvidenceRef("invalidation evidence")}),
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        correlation_id,
    )

    def requires_event_id(identity: EventId) -> EventId:
        return identity

    def requires_causation_id(identity: CausationId) -> CausationId:
        return identity

    event_id = EventId(value)
    causation_id = CausationId(value)
    assert_type(requires_event_id(event_id), EventId)
    assert_type(requires_causation_id(causation_id), CausationId)
    requires_event_id(CorrelationId(value))  # type: ignore[arg-type]
    requires_event_id(CausationId(value))  # type: ignore[arg-type]
    requires_event_id(ObjectiveId(value))  # type: ignore[arg-type]
    requires_causation_id(EventId(value))  # type: ignore[arg-type]
    requires_causation_id(CorrelationId(value))  # type: ignore[arg-type]

    class StaticTransitionGuard:
        def validate(self, entity: object, request: object) -> None:
            pass

    transition_objective = Objective(
        ObjectiveId(value),
        ObjectiveState.DRAFT,
        EntityVersion(7),
        "Bounded goal",
        ("Criterion",),
        designation,
        policy,
    )
    objective_transition_request = TransitionRequest(
        event_id,
        ObjectiveState.ACTIVE,
        designation,
        TransitionReason("Activate objective"),
        EntityVersion(7),
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        correlation_id,
        causation_id,
    )
    transition_authority = TransitionAuthorityDecision(
        designation,
        DomainEntityType.OBJECTIVE,
        ObjectiveId(value),
        EntityVersion(7),
        ObjectiveState.DRAFT,
        ObjectiveState.ACTIVE,
        TransitionAuthorityStatus.AUTHORIZED,
        correlation_id,
    )
    semantic_decision_ref = ObjectiveSemanticDecisionRef("decision")
    semantic_status = ObjectiveSemanticDecisionStatus.PASSED
    semantic_evidence = frozenset({EvidenceRef("semantic evidence")})
    objective_semantic_guard = ObjectiveSemanticGuard(
        ObjectiveId(value),
        EntityVersion(7),
        ObjectiveState.DRAFT,
        ObjectiveState.ACTIVE,
        correlation_id,
        ObjectiveActivationSemantics(
            ObjectiveGovernanceApprovalDecision(
                semantic_decision_ref,
                semantic_status,
                designation,
                semantic_evidence,
                ObjectiveId(value),
                EntityVersion(7),
                correlation_id,
            ),
            ObjectiveBudgetValidityDecision(
                semantic_decision_ref,
                semantic_status,
                designation,
                semantic_evidence,
                ObjectiveId(value),
                EntityVersion(7),
                correlation_id,
            ),
            ObjectivePermissionValidityDecision(
                semantic_decision_ref,
                semantic_status,
                designation,
                semantic_evidence,
                ObjectiveId(value),
                EntityVersion(7),
                correlation_id,
            ),
            ObjectiveTimeHorizonValidityDecision(
                semantic_decision_ref,
                semantic_status,
                designation,
                semantic_evidence,
                ObjectiveId(value),
                EntityVersion(7),
                correlation_id,
            ),
        ),
    )
    transition_context = TransitionContext(
        (StaticTransitionGuard(),), transition_authority, objective_semantic_guard
    )
    objective_transition_result = transition_entity(
        transition_objective,
        objective_transition_request,
        transition_context,
    )
    assert_type(objective_transition_request, TransitionRequest[ObjectiveState])
    assert_type(objective_transition_result, TransitionResult[Objective])
    assert_type(objective_transition_result.entity, Objective)
    assert_type(objective_transition_result.event, DomainEvent)
    assert_type(objective_transition_result.event.event_id, EventId)
    assert_type(
        objective_transition_result.event.entity_id,
        ObjectiveId | TaskId | RunId | OutcomeId | EvaluationId | EffectId,
    )
    assert_type(objective_transition_result.event.metadata, DomainEventMetadata)
    assert_type(objective_transition_result.event.entity_type, DomainEntityType)
    assert_type(objective_transition_result.event.event_type, DomainEventType)
    assert_type(transition_authority.actor, ActorIdentity)
    assert_type(
        transition_authority.entity_id,
        ObjectiveId | TaskId | RunId | OutcomeId | EvaluationId | EffectId,
    )
    assert_type(transition_authority.observed_entity_version, EntityVersion)
    assert_type(transition_authority.correlation_id, CorrelationId)
    assert_type(transition_authority.decision, TransitionAuthorityStatus)
    assert_type(objective_semantic_guard.objective_id, ObjectiveId)
    assert_type(objective_semantic_guard.observed_entity_version, EntityVersion)
    assert_type(objective_semantic_guard.prior_state, ObjectiveState)
    assert_type(objective_semantic_guard.target_state, ObjectiveState)
    assert_type(objective_semantic_guard.correlation_id, CorrelationId)
    assert_type(semantic_decision_ref, ObjectiveSemanticDecisionRef)
    ObjectiveSemanticGuard(
        TaskId(value),  # type: ignore[arg-type]
        EntityVersion(7),
        ObjectiveState.DRAFT,
        ObjectiveState.ACTIVE,
        correlation_id,
        objective_semantic_guard.semantic_input,
    )
    ObjectiveBudgetValidityDecision(
        EvidenceRef("not a decision"),  # type: ignore[arg-type]
        semantic_status,
        designation,
        semantic_evidence,
        ObjectiveId(value),
        EntityVersion(7),
        correlation_id,
    )
    assert_type(
        is_actor_eligible_for_transition_authority(
            DomainEntityType.OBJECTIVE,
            ObjectiveState.DRAFT,
            ObjectiveState.ACTIVE,
            ActorType.HUMAN_OPERATOR,
        ),
        bool,
    )
    TransitionAuthorityDecision(
        designation,
        DomainEntityType.EFFECT,
        EffectExecutionAuthorizationId(value),  # type: ignore[arg-type]
        EntityVersion(7),
        EffectState.PLANNED,
        EffectState.SIMULATED,
        TransitionAuthorityStatus.AUTHORIZED,
        correlation_id,
    )
    task_transition_request = TransitionRequest(
        event_id,
        TaskState.READY,
        designation,
        TransitionReason("Ready task"),
        EntityVersion(7),
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        correlation_id,
    )
    transition_entity(
        transition_objective,
        task_transition_request,  # type: ignore[arg-type]
        transition_context,
    )
    TransitionRequest(
        CorrelationId(value),  # type: ignore[arg-type]
        ObjectiveState.ACTIVE,
        designation,
        TransitionReason("Activate objective"),
        EntityVersion(7),
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        correlation_id,
    )

    def requires_preparation_id(
        identity: EffectPreparationRecordId,
    ) -> EffectPreparationRecordId:
        return identity

    def requires_verification_id(
        identity: EffectVerificationRecordId,
    ) -> EffectVerificationRecordId:
        return identity

    def requires_execution_authorization_id(
        identity: EffectExecutionAuthorizationId,
    ) -> EffectExecutionAuthorizationId:
        return identity

    preparation_id = EffectPreparationRecordId(value)
    verification_id = EffectVerificationRecordId(value)
    execution_authorization_id = EffectExecutionAuthorizationId(value)
    assert_type(requires_preparation_id(preparation_id), EffectPreparationRecordId)
    assert_type(requires_verification_id(verification_id), EffectVerificationRecordId)
    assert_type(
        requires_execution_authorization_id(execution_authorization_id),
        EffectExecutionAuthorizationId,
    )
    requires_preparation_id(EffectId(value))  # type: ignore[arg-type]
    requires_preparation_id(EffectObservationId(value))  # type: ignore[arg-type]
    requires_preparation_id(CorrelationId(value))  # type: ignore[arg-type]
    requires_verification_id(preparation_id)  # type: ignore[arg-type]
    requires_verification_id(EffectAuthorizationFindingId(value))  # type: ignore[arg-type]
    requires_execution_authorization_id(verification_id)  # type: ignore[arg-type]
    requires_execution_authorization_id(EffectAuthorizationFindingId(value))  # type: ignore[arg-type]

    prepared_effect = Effect(
        EffectId(value),
        EffectState.SIMULATED,
        EntityVersion(7),
        PlannedEffectOrigin(TaskId(value), designation),
        EffectTargetRef("target"),
        EffectPayloadRef("payload"),
    )
    preparation_record = EffectPreparationRecord(
        preparation_id,
        EffectId(value),
        EntityVersion(7),
        "Prepared exact payload",
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    verification_record = EffectVerificationRecord(
        verification_id,
        preparation_id,
        EffectId(value),
        EntityVersion(7),
        "Verified exact prepared payload",
        frozenset({EvidenceRef("verification evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    execution_authorization_record = EffectExecutionAuthorizationRecord(
        execution_authorization_id,
        preparation_id,
        EffectId(value),
        EntityVersion(7),
        frozenset({verification_id}),
        "Authorized exact prepared and verified payload",
        frozenset({EvidenceRef("authorization evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    assert_type(preparation_record.preparation_id, EffectPreparationRecordId)
    assert_type(verification_record.verification_id, EffectVerificationRecordId)
    assert_type(
        execution_authorization_record.authorization_id,
        EffectExecutionAuthorizationId,
    )
    assert_type(
        execution_authorization_record.verification_ids,
        frozenset[EffectVerificationRecordId],
    )
    assert_type(
        can_attach_effect_preparation_record(prepared_effect, preparation_record), bool
    )
    assert_type(
        can_verify_effect_preparation(preparation_record, verification_record), bool
    )
    assert_type(
        can_authorize_effect_preparation(
            preparation_record, execution_authorization_record
        ),
        bool,
    )
    assert_type(
        can_use_effect_verification_for_authorization(
            verification_record, execution_authorization_record
        ),
        bool,
    )
    EffectPreparationRecord(
        EffectId(value),  # type: ignore[arg-type]
        EffectId(value),
        EntityVersion(7),
        "Prepared exact payload",
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    EffectVerificationRecord(
        EffectAuthorizationFindingId(value),  # type: ignore[arg-type]
        preparation_id,
        EffectId(value),
        EntityVersion(7),
        "Verified exact prepared payload",
        frozenset({EvidenceRef("verification evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    EffectExecutionAuthorizationRecord(
        EffectAuthorizationFindingId(value),  # type: ignore[arg-type]
        preparation_id,
        EffectId(value),
        EntityVersion(7),
        frozenset({verification_id}),
        "Authorized exact prepared and verified payload",
        frozenset({EvidenceRef("authorization evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    can_attach_effect_preparation_record(
        prepared_effect,
        verification_record,  # type: ignore[arg-type]
    )
    can_verify_effect_preparation(
        preparation_record,
        execution_authorization_record,  # type: ignore[arg-type]
    )
    can_authorize_effect_preparation(
        preparation_record,
        verification_record,  # type: ignore[arg-type]
    )
    can_use_effect_verification_for_authorization(
        verification_record,
        EffectAuthorizationFindingId(value),  # type: ignore[arg-type]
    )

    def requires_incident_id(identity: EffectIncidentId) -> EffectIncidentId:
        return identity

    def requires_incident_record_id(
        identity: EffectIncidentRecordId,
    ) -> EffectIncidentRecordId:
        return identity

    incident_id = EffectIncidentId(value)
    incident_record_id = EffectIncidentRecordId(value)
    assert_type(requires_incident_id(incident_id), EffectIncidentId)
    assert_type(requires_incident_record_id(incident_record_id), EffectIncidentRecordId)
    requires_incident_id(EffectId(value))  # type: ignore[arg-type]
    requires_incident_id(EffectObservationId(value))  # type: ignore[arg-type]
    requires_incident_id(EffectAttributionId(value))  # type: ignore[arg-type]
    requires_incident_id(EffectAuthorizationFindingId(value))  # type: ignore[arg-type]
    requires_incident_id(EffectGovernanceFindingId(value))  # type: ignore[arg-type]
    requires_incident_id(CorrelationId(value))  # type: ignore[arg-type]
    requires_incident_id(value)  # type: ignore[arg-type]
    requires_incident_record_id(incident_id)  # type: ignore[arg-type]
    requires_incident_record_id(EffectId(value))  # type: ignore[arg-type]

    incident_record = EffectIncidentRecord(
        incident_record_id,
        incident_id,
        EffectId(value),
        EntityVersion(7),
        EffectIncidentStatus.CLOSED,
        "Historical closure finding",
        frozenset({EvidenceRef("incident evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    assert_type(incident_record.record_id, EffectIncidentRecordId)
    assert_type(incident_record.incident_id, EffectIncidentId)
    assert_type(
        can_attach_effect_incident_record(observed_effect, incident_record), bool
    )
    assert_type(
        can_follow_effect_incident_record(incident_record, incident_record), bool
    )
    EffectIncidentRecord(
        incident_id,  # type: ignore[arg-type]
        incident_id,
        EffectId(value),
        EntityVersion(7),
        EffectIncidentStatus.OPEN,
        "Finding",
        frozenset({EvidenceRef("incident evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    EffectIncidentRecord(
        incident_record_id,
        incident_record_id,  # type: ignore[arg-type]
        EffectId(value),
        EntityVersion(7),
        EffectIncidentStatus.OPEN,
        "Finding",
        frozenset({EvidenceRef("incident evidence")}),
        designation,
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        Timestamp(datetime(2026, 9, 9, tzinfo=UTC)),
        correlation_id,
    )
    EvaluationInvalidationRecord(
        invalidation_id,
        EvaluationId(value),
        ConflictSetVersion(7),  # type: ignore[arg-type]
        "Established verifier failure",
        frozenset({EvidenceRef("invalidation evidence")}),
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        correlation_id,
    )
    EvaluationInvalidationRecord(
        invalidation_id,
        EvaluationId(value),
        EntityVersion(7),
        "Established verifier failure",
        frozenset({ArtifactRef("not evidence")}),  # type: ignore[arg-type]
        designation,
        Timestamp(datetime(2026, 9, 8, tzinfo=UTC)),
        correlation_id,
    )
