"""Nominal UUID identities with explicit generation and parsing boundaries."""

from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4

from .errors import InvalidDomainValue


@dataclass(frozen=True, slots=True)
class _UuidId:
    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise InvalidDomainValue(
                "ID value must be a UUID; use from_string to parse"
            )

    @classmethod
    def new(cls) -> Self:
        """Explicitly create an identity using UUID4."""
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> Self:
        """Parse UUID text and retain the concrete domain identity type."""
        if not isinstance(value, str):
            raise InvalidDomainValue("Serialized ID must be a string")
        try:
            parsed = UUID(value)
        except ValueError as exc:
            raise InvalidDomainValue("Serialized ID must contain a valid UUID") from exc
        return cls(parsed)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ObjectiveId(_UuidId):
    """Identity of an Objective, distinct from all other ID kinds."""


@dataclass(frozen=True, slots=True)
class TaskId(_UuidId):
    """Identity of a Task."""


@dataclass(frozen=True, slots=True)
class RunId(_UuidId):
    """Identity of a Run."""


@dataclass(frozen=True, slots=True)
class OutcomeId(_UuidId):
    """Identity of an Outcome."""


@dataclass(frozen=True, slots=True)
class EvaluationId(_UuidId):
    """Identity of an Evaluation."""


@dataclass(frozen=True, slots=True)
class EffectId(_UuidId):
    """Identity of an Effect."""


@dataclass(frozen=True, slots=True)
class ActorId(_UuidId):
    """Identity of a principal, independent of its operating category."""
