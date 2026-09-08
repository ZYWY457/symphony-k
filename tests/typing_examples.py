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
    CompletionPolicyRef,
    ConflictSetVersion,
    CorrelationId,
    EffectId,
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
    EvaluationId,
    EvaluationInvalidationId,
    EvaluationInvalidationRecord,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationState,
    EvaluationTargetRef,
    EvaluationVerdict,
    EvidenceRef,
    ExecutionProfileRef,
    Objective,
    ObjectiveId,
    ObjectiveState,
    Outcome,
    OutcomeId,
    OutcomeState,
    Run,
    RunId,
    RunState,
    Task,
    TaskId,
    TaskState,
    Timestamp,
    can_arbitrate_evaluation_conflict_set,
    can_evaluation_transition,
    can_extend_evaluation_conflict_set,
    can_invalidate_evaluation,
    can_objective_transition,
    can_outcome_transition,
    can_run_transition,
    can_task_transition,
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
