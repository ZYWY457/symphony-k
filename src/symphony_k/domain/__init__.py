"""Domain snapshots and structural topology; no authoritative transition execution."""

from .actors import ActorIdentity, ActorType
from .candidate_refs import ArtifactRef, EvidenceRef
from .completion import CompletionPolicyRef
from .effect import (
    EFFECT_CREATION_STATES,
    Effect,
    EffectExternalOperationRef,
    EffectOrigin,
    EffectPayloadRef,
    EffectState,
    EffectTargetRef,
    ObservedEffectOrigin,
    PlannedEffectOrigin,
    can_effect_transition,
)
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
from .evaluation_effective_use import (
    EvaluationEffectiveUseView,
    derive_evaluation_effective_use,
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
    "EFFECT_CREATION_STATES",
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
    "Effect",
    "EffectExternalOperationRef",
    "EffectOrigin",
    "EffectPayloadRef",
    "EffectState",
    "EffectTargetRef",
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
    "EvaluationEffectiveUseView",
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
    "ObservedEffectOrigin",
    "PlannedEffectOrigin",
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
    "can_effect_transition",
    "can_invalidate_evaluation",
    "derive_evaluation_effective_use",
    "can_objective_transition",
    "can_outcome_transition",
    "can_run_transition",
    "can_task_transition",
]
