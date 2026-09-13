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
class EvaluationConflictSetId(_UuidId):
    """Stable identity of one logical Evaluation conflict across versions."""


@dataclass(frozen=True, slots=True)
class EvaluationArbitrationId(_UuidId):
    """Identity of one immutable Evaluation arbitration decision record."""


@dataclass(frozen=True, slots=True)
class EvaluationInvalidationId(_UuidId):
    """Identity of one immutable Evaluation invalidation record."""


@dataclass(frozen=True, slots=True)
class EffectId(_UuidId):
    """Identity of an Effect."""


@dataclass(frozen=True, slots=True)
class EffectObservationId(_UuidId):
    """Identity of one immutable supporting Effect observation record."""


@dataclass(frozen=True, slots=True)
class EffectPreparationRecordId(_UuidId):
    """Identity of one immutable Effect preparation record."""


@dataclass(frozen=True, slots=True)
class EffectVerificationRecordId(_UuidId):
    """Identity of one immutable successful Effect verification record."""


@dataclass(frozen=True, slots=True)
class EffectExecutionAuthorizationId(_UuidId):
    """Identity of one immutable prospective execution-authorization decision."""


@dataclass(frozen=True, slots=True)
class EffectSimulationRecordId(_UuidId):
    """Identity of one immutable dry-run provenance record."""


@dataclass(frozen=True, slots=True)
class EffectRemediationReadinessId(_UuidId):
    """Identity of one immutable pre-commit remediation-readiness record."""


@dataclass(frozen=True, slots=True)
class EffectSimulationBypassDecisionId(_UuidId):
    """Identity of one immutable decision to bypass an Effect simulation."""


@dataclass(frozen=True, slots=True)
class EffectAttributionId(_UuidId):
    """Identity of one immutable supporting Effect attribution record."""


@dataclass(frozen=True, slots=True)
class EffectAuthorizationFindingId(_UuidId):
    """Identity of one immutable Effect authorization finding record."""


@dataclass(frozen=True, slots=True)
class EffectGovernanceFindingId(_UuidId):
    """Identity of one immutable Effect governance finding record."""


@dataclass(frozen=True, slots=True)
class EffectIncidentId(_UuidId):
    """Stable identity of one conceptual Effect incident."""


@dataclass(frozen=True, slots=True)
class EffectIncidentRecordId(_UuidId):
    """Identity of one immutable historical Effect incident record."""


@dataclass(frozen=True, slots=True)
class EffectQuarantineContextId(_UuidId):
    """Identity of one immutable Effect quarantine-context record."""


@dataclass(frozen=True, slots=True)
class EffectReconciliationRecordId(_UuidId):
    """Identity of one immutable quarantine-reconciliation conclusion."""


@dataclass(frozen=True, slots=True)
class EffectRollbackRecordId(_UuidId):
    """Identity of one immutable supporting Effect rollback record."""


@dataclass(frozen=True, slots=True)
class EffectCompensationPlanId(_UuidId):
    """Identity of one immutable supporting Effect compensation plan."""


@dataclass(frozen=True, slots=True)
class EffectCompensationCompletionId(_UuidId):
    """Identity of one immutable Effect compensation completion record."""


@dataclass(frozen=True, slots=True)
class EventId(_UuidId):
    """Identity of one immutable authoritative domain event."""


@dataclass(frozen=True, slots=True)
class CausationId(_UuidId):
    """Identity of the request or record that caused a domain event."""


@dataclass(frozen=True, slots=True)
class ActorId(_UuidId):
    """Identity of a principal, independent of its operating category."""


@dataclass(frozen=True, slots=True)
class CorrelationId(_UuidId):
    """Cross-record correlation identity that grants no lifecycle authority."""
