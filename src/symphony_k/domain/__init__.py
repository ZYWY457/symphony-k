"""Shared Domain Kernel value types; no lifecycle or authorization behavior."""

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
from .time import Timestamp
from .transitions import TransitionReason
from .version import EntityVersion

__all__ = [
    "ActorId",
    "ActorIdentity",
    "ActorType",
    "CompletionPolicyNotSatisfied",
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
    "ObjectiveId",
    "OutcomeId",
    "RunId",
    "TaskId",
    "Timestamp",
    "TransitionReason",
    "UnauthorizedTransition",
]
