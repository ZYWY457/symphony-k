"""Domain snapshots and structural topology; no authoritative transition execution."""

from .actors import ActorIdentity, ActorType
from .candidate_refs import ArtifactRef, EvidenceRef
from .completion import CompletionPolicyRef
from .errors import (
    CompletionPolicyNotSatisfied,
    ConcurrencyConflict,
    DomainError,
    EntityNotFound,
    ImmutableRecordViolation,
    InvalidDomainValue,
    InvalidRelationship,
    InvalidTransition,
    InvariantViolation,
    UnauthorizedTransition,
)
from .evaluation import (
    EVALUATION_CREATION_STATE,
    Evaluation,
    EvaluationState,
    can_evaluation_transition,
)
from .evaluation_arbitration import (
    ArbitrationDisposition,
    EvaluationArbitrationMemberDecision,
    EvaluationArbitrationPolicyRef,
    EvaluationArbitrationRecord,
    can_arbitrate_evaluation_conflict_set,
)
from .evaluation_conflict import (
    EvaluationConflictMemberRef,
    EvaluationConflictScopeRef,
    EvaluationConflictSetRecord,
    EvaluationConflictSetRef,
    can_extend_evaluation_conflict_set,
)
from .evaluation_invalidation import (
    EvaluationInvalidationRecord,
    can_invalidate_evaluation,
)
from .evaluation_result import (
    EvaluationConfidence,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationVerdict,
)
from .evaluation_target import EvaluationTargetRef
from .execution_profile import ExecutionProfileRef
from .ids import (
    ActorId,
    CorrelationId,
    EffectId,
    EvaluationArbitrationId,
    EvaluationConflictSetId,
    EvaluationId,
    EvaluationInvalidationId,
    ObjectiveId,
    OutcomeId,
    RunId,
    TaskId,
)
from .objective import (
    OBJECTIVE_CREATION_STATE,
    Objective,
    ObjectiveState,
    can_objective_transition,
)
from .outcome import (
    OUTCOME_CREATION_STATE,
    Outcome,
    OutcomeState,
    can_outcome_transition,
)
from .run import RUN_CREATION_STATE, Run, RunState, can_run_transition
from .task import TASK_CREATION_STATE, Task, TaskState, can_task_transition
from .time import Timestamp
from .transitions import TransitionReason
from .version import ConflictSetVersion, EntityVersion

__all__ = [
    "EVALUATION_CREATION_STATE",
    "OBJECTIVE_CREATION_STATE",
    "OUTCOME_CREATION_STATE",
    "RUN_CREATION_STATE",
    "TASK_CREATION_STATE",
    "ActorId",
    "ActorIdentity",
    "ActorType",
    "ArbitrationDisposition",
    "ArtifactRef",
    "CompletionPolicyNotSatisfied",
    "CompletionPolicyRef",
    "ConflictSetVersion",
    "ConcurrencyConflict",
    "CorrelationId",
    "DomainError",
    "EffectId",
    "EntityNotFound",
    "EntityVersion",
    "Evaluation",
    "EvaluationArbitrationId",
    "EvaluationArbitrationMemberDecision",
    "EvaluationArbitrationPolicyRef",
    "EvaluationArbitrationRecord",
    "EvaluationConfidence",
    "EvaluationConflictMemberRef",
    "EvaluationConflictScopeRef",
    "EvaluationConflictSetId",
    "EvaluationConflictSetRecord",
    "EvaluationConflictSetRef",
    "EvaluationId",
    "EvaluationInvalidationId",
    "EvaluationInvalidationRecord",
    "EvaluationMethodRef",
    "EvaluationResult",
    "EvaluationState",
    "EvaluationTargetRef",
    "EvaluationVerdict",
    "EvidenceRef",
    "ExecutionProfileRef",
    "ImmutableRecordViolation",
    "InvalidDomainValue",
    "InvalidRelationship",
    "InvalidTransition",
    "InvariantViolation",
    "Objective",
    "ObjectiveId",
    "ObjectiveState",
    "Outcome",
    "OutcomeId",
    "OutcomeState",
    "Run",
    "RunId",
    "RunState",
    "Task",
    "TaskId",
    "TaskState",
    "Timestamp",
    "TransitionReason",
    "UnauthorizedTransition",
    "can_arbitrate_evaluation_conflict_set",
    "can_extend_evaluation_conflict_set",
    "can_evaluation_transition",
    "can_invalidate_evaluation",
    "can_objective_transition",
    "can_outcome_transition",
    "can_run_transition",
    "can_task_transition",
]
