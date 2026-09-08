"""Immutable Effect provenance and structural lifecycle topology.

This module records intended or observed external-mutation identity. It contains
no authority checks, transition execution, reconciliation, or external action.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final

from .actors import ActorIdentity
from .candidate_refs import EvidenceRef
from .errors import InvalidDomainValue
from .ids import EffectId, RunId, TaskId
from .time import Timestamp
from .version import EntityVersion


class EffectState(Enum):
    """Effect lifecycle projections, separate from governance and occurrence facts."""

    PLANNED = "PLANNED"  # Governed intent exists; dispatch is not authorized by this.
    SIMULATED = "SIMULATED"  # Preparation only; no external mutation is implied.
    PENDING_COMMIT = "PENDING_COMMIT"  # Awaiting commit handling, not permission.
    COMMITTED = "COMMITTED"  # Confirmed occurrence, regardless of authorization.
    ROLLED_BACK = "ROLLED_BACK"  # Prior state restored; occurrence history remains.
    COMPENSATING = "COMPENSATING"  # Distinct compensating work is in progress.
    COMPENSATED = "COMPENSATED"  # Compensation completed; no rollback is implied.
    QUARANTINED = "QUARANTINED"  # Controlled reconciliation, not a factual verdict.


@dataclass(frozen=True, slots=True)
class EffectTargetRef:
    """Opaque identity of the external target or mutation scope."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Effect target reference must contain non-whitespace text"
            )


@dataclass(frozen=True, slots=True)
class EffectPayloadRef:
    """Opaque identity of an exact intended or observed mutation payload."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Effect payload reference must contain non-whitespace text"
            )


@dataclass(frozen=True, slots=True)
class EffectExternalOperationRef:
    """Opaque identity of the externally observed operation; never authorization."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Effect external-operation reference must contain non-whitespace text"
            )


@dataclass(frozen=True, slots=True)
class PlannedEffectOrigin:
    """Immutable creation provenance for governed intent, not execution authority."""

    task_id: TaskId
    proposed_by: ActorIdentity
    run_id: RunId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId")
        if not isinstance(self.proposed_by, ActorIdentity):
            raise InvalidDomainValue("proposed_by must be an ActorIdentity")
        if self.run_id is not None and not isinstance(self.run_id, RunId):
            raise InvalidDomainValue("run_id must be a RunId or None")


@dataclass(frozen=True, slots=True)
class ObservedEffectOrigin:
    """Immutable creation provenance for an independently evidenced observation."""

    external_operation_ref: EffectExternalOperationRef
    observation_evidence_refs: frozenset[EvidenceRef]
    observed_by: ActorIdentity
    observed_at: Timestamp
    task_id: TaskId | None = None
    run_id: RunId | None = None
    unlinked_reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.external_operation_ref, EffectExternalOperationRef):
            raise InvalidDomainValue(
                "external_operation_ref must be an EffectExternalOperationRef"
            )
        if (
            not isinstance(self.observation_evidence_refs, frozenset)
            or not self.observation_evidence_refs
        ):
            raise InvalidDomainValue(
                "observation_evidence_refs must be a nonempty frozenset"
            )
        if any(
            not isinstance(reference, EvidenceRef)
            for reference in self.observation_evidence_refs
        ):
            raise InvalidDomainValue(
                "Every observation evidence reference must be an EvidenceRef"
            )
        if not isinstance(self.observed_by, ActorIdentity):
            raise InvalidDomainValue("observed_by must be an ActorIdentity")
        if not isinstance(self.observed_at, Timestamp):
            raise InvalidDomainValue("observed_at must be a Timestamp")
        if self.task_id is not None and not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId or None")
        if self.run_id is not None and not isinstance(self.run_id, RunId):
            raise InvalidDomainValue("run_id must be a RunId or None")
        if self.task_id is None:
            if self.run_id is not None:
                raise InvalidDomainValue("run_id requires known Task attribution")
            if (
                not isinstance(self.unlinked_reason, str)
                or not self.unlinked_reason.strip()
            ):
                raise InvalidDomainValue(
                    "Unlinked observation requires a non-whitespace reason"
                )
        elif self.unlinked_reason is not None:
            raise InvalidDomainValue(
                "Linked observation must not contain an unlinked_reason"
            )


type EffectOrigin = PlannedEffectOrigin | ObservedEffectOrigin


@dataclass(frozen=True, slots=True)
class Effect:
    """Descriptive Effect snapshot; construction performs no external mutation."""

    effect_id: EffectId
    state: EffectState
    version: EntityVersion
    origin: EffectOrigin
    target_ref: EffectTargetRef
    payload_ref: EffectPayloadRef | None

    def __post_init__(self) -> None:
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.state, EffectState):
            raise InvalidDomainValue("state must be an EffectState")
        if not isinstance(self.version, EntityVersion):
            raise InvalidDomainValue("version must be an EntityVersion")
        if not isinstance(self.origin, (PlannedEffectOrigin, ObservedEffectOrigin)):
            raise InvalidDomainValue(
                "origin must be a PlannedEffectOrigin or ObservedEffectOrigin"
            )
        if not isinstance(self.target_ref, EffectTargetRef):
            raise InvalidDomainValue("target_ref must be an EffectTargetRef")
        if self.payload_ref is not None and not isinstance(
            self.payload_ref, EffectPayloadRef
        ):
            raise InvalidDomainValue("payload_ref must be an EffectPayloadRef or None")
        if isinstance(self.origin, PlannedEffectOrigin) and self.payload_ref is None:
            raise InvalidDomainValue("Planned Effect requires a payload_ref")


# NONE is absence, not an EffectState. Creation authority and guards belong to M7.
EFFECT_CREATION_STATES: Final[frozenset[EffectState]] = frozenset(
    {EffectState.PLANNED, EffectState.COMMITTED, EffectState.QUARANTINED}
)

_EFFECT_TRANSITIONS: Final[frozenset[tuple[EffectState, EffectState]]] = frozenset(
    {
        (EffectState.PLANNED, EffectState.SIMULATED),
        (EffectState.PLANNED, EffectState.PENDING_COMMIT),
        (EffectState.SIMULATED, EffectState.PENDING_COMMIT),
        (EffectState.PLANNED, EffectState.COMMITTED),
        (EffectState.SIMULATED, EffectState.COMMITTED),
        (EffectState.PLANNED, EffectState.QUARANTINED),
        (EffectState.SIMULATED, EffectState.QUARANTINED),
        (EffectState.PENDING_COMMIT, EffectState.COMMITTED),
        (EffectState.PENDING_COMMIT, EffectState.QUARANTINED),
        (EffectState.COMMITTED, EffectState.ROLLED_BACK),
        (EffectState.COMMITTED, EffectState.COMPENSATING),
        (EffectState.COMMITTED, EffectState.QUARANTINED),
        (EffectState.COMPENSATING, EffectState.COMPENSATED),
        (EffectState.COMPENSATING, EffectState.QUARANTINED),
        (EffectState.QUARANTINED, EffectState.PENDING_COMMIT),
        (EffectState.QUARANTINED, EffectState.COMMITTED),
        (EffectState.QUARANTINED, EffectState.ROLLED_BACK),
        (EffectState.QUARANTINED, EffectState.COMPENSATING),
        (EffectState.QUARANTINED, EffectState.COMPENSATED),
    }
)


def can_effect_transition(source: EffectState, target: EffectState) -> bool:
    """Return structural membership without guards, mutation, or external action."""
    if not isinstance(source, EffectState) or not isinstance(target, EffectState):
        raise InvalidDomainValue("source and target must be EffectState values")
    return (source, target) in _EFFECT_TRANSITIONS
