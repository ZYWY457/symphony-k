"""Domain values and Objective topology; no authoritative transition execution."""

from .actors import ActorIdentity, ActorType
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
from .ids import ActorId, EffectId, EvaluationId, ObjectiveId, OutcomeId, RunId, TaskId
from .objective import (
    OBJECTIVE_CREATION_STATE,
    CompletionPolicyRef,
    Objective,
    ObjectiveState,
    can_objective_transition,
)
from .time import Timestamp
from .transitions import TransitionReason
from .version import EntityVersion

__all__ = [
    "OBJECTIVE_CREATION_STATE",
    "ActorId",
    "ActorIdentity",
    "ActorType",
    "CompletionPolicyNotSatisfied",
    "CompletionPolicyRef",
    "ConcurrencyConflict",
    "DomainError",
    "EffectId",
    "EntityNotFound",
    "EntityVersion",
    "EvaluationId",
    "ImmutableRecordViolation",
    "InvalidDomainValue",
    "InvalidRelationship",
    "InvalidTransition",
    "InvariantViolation",
    "Objective",
    "ObjectiveId",
    "ObjectiveState",
    "OutcomeId",
    "RunId",
    "TaskId",
    "Timestamp",
    "TransitionReason",
    "UnauthorizedTransition",
    "can_objective_transition",
]
