"""Static-only API contracts checked by `mypy src tests`.

Targeted ignores are negative assertions: strict mypy rejects an unused ignore
if these invalid argument combinations ever become type-compatible.
"""

from typing import TYPE_CHECKING, assert_type
from uuid import UUID

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArtifactRef,
    CompletionPolicyRef,
    EffectId,
    EntityVersion,
    Evaluation,
    EvaluationConfidence,
    EvaluationId,
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
    can_evaluation_transition,
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
    assert_type(EffectId.new(), EffectId)
    assert_type(ActorId.new(), ActorId)
    assert_type(ObjectiveId.from_string(str(value)), ObjectiveId)
    assert_type(requires_objective(ObjectiveId(value)), ObjectiveId)

    requires_objective(TaskId(value))  # type: ignore[arg-type]
    requires_objective(RunId(value))  # type: ignore[arg-type]
    requires_objective(OutcomeId(value))  # type: ignore[arg-type]
    requires_objective(EvaluationId(value))  # type: ignore[arg-type]
    requires_objective(EffectId(value))  # type: ignore[arg-type]
    requires_objective(ActorId(value))  # type: ignore[arg-type]
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
