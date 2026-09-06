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
from .execution_profile import ExecutionProfileRef
from .ids import ActorId, EffectId, EvaluationId, ObjectiveId, OutcomeId, RunId, TaskId
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
from .version import EntityVersion

__all__ = [
    "OBJECTIVE_CREATION_STATE",
    "OUTCOME_CREATION_STATE",
    "RUN_CREATION_STATE",
    "TASK_CREATION_STATE",
    "ActorId",
    "ActorIdentity",
    "ActorType",
    "ArtifactRef",
    "CompletionPolicyNotSatisfied",
    "CompletionPolicyRef",
    "ConcurrencyConflict",
    "DomainError",
    "EffectId",
    "EntityNotFound",
    "EntityVersion",
    "EvaluationId",
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
    "can_objective_transition",
    "can_outcome_transition",
    "can_run_transition",
    "can_task_transition",
]
