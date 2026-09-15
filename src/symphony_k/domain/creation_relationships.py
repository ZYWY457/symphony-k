"""Immutable supplied relationship evidence; no repository currentness claim."""

from dataclasses import dataclass
from enum import Enum

from .actors import ActorIdentity, ActorType
from .candidate_refs import EvidenceRef
from .creation_semantics import _require_evidence, _require_text
from .effect import Effect
from .errors import EntityNotFound, InvalidDomainValue, InvariantViolation
from .ids import (
    CausationId,
    CorrelationId,
    EffectId,
    ObjectiveId,
    OutcomeId,
    RunId,
    TaskId,
)
from .objective import Objective
from .outcome import Outcome
from .run import Run
from .task import Task
from .time import Timestamp


@dataclass(frozen=True, slots=True)
class CreationProvenanceRef:
    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, "creation provenance reference")


@dataclass(frozen=True, slots=True)
class CreationRequestIdentity:
    requested_by: ActorIdentity
    causation_id: CausationId
    correlation_id: CorrelationId
    provenance_ref: CausationId

    def __post_init__(self) -> None:
        for value, expected in (
            (self.requested_by, ActorIdentity),
            (self.causation_id, CausationId),
            (self.correlation_id, CorrelationId),
            (self.provenance_ref, CausationId),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue("Invalid creation request identity")


class CreationObservationStatus(Enum):
    CURRENT = "CURRENT"
    MISSING = "MISSING"
    STALE = "STALE"
    UNRESOLVED = "UNRESOLVED"


type RelatedSnapshot = Objective | Task | Run | Outcome | Effect
type RelatedId = ObjectiveId | TaskId | RunId | OutcomeId | EffectId


def related_id(snapshot: RelatedSnapshot) -> RelatedId:
    if isinstance(snapshot, Objective):
        return snapshot.objective_id
    if isinstance(snapshot, Task):
        return snapshot.task_id
    if isinstance(snapshot, Run):
        return snapshot.run_id
    if isinstance(snapshot, Outcome):
        return snapshot.outcome_id
    return snapshot.effect_id


@dataclass(frozen=True, slots=True)
class CreationRelationshipObservation:
    observation_ref: CreationProvenanceRef
    request_identity: CreationRequestIdentity
    entity_id: RelatedId
    status: CreationObservationStatus
    snapshot: RelatedSnapshot | None
    observed_by: ActorIdentity
    observed_at: Timestamp
    evidence_refs: frozenset[EvidenceRef]

    def __post_init__(self) -> None:
        if not isinstance(self.observation_ref, CreationProvenanceRef):
            raise InvalidDomainValue("Invalid relationship observation reference")
        if not isinstance(self.request_identity, CreationRequestIdentity):
            raise InvalidDomainValue("Invalid observation request identity")
        if not isinstance(
            self.entity_id, (ObjectiveId, TaskId, RunId, OutcomeId, EffectId)
        ):
            raise InvalidDomainValue("Invalid related entity ID")
        if not isinstance(self.status, CreationObservationStatus):
            raise InvalidDomainValue("Invalid relationship status")
        if not isinstance(self.observed_by, ActorIdentity):
            raise InvalidDomainValue("Invalid relationship observer")
        if not isinstance(self.observed_at, Timestamp):
            raise InvalidDomainValue("Invalid relationship observation time")
        _require_evidence(self.evidence_refs)
        if self.status in {
            CreationObservationStatus.CURRENT,
            CreationObservationStatus.STALE,
        }:
            if not isinstance(self.snapshot, (Objective, Task, Run, Outcome, Effect)):
                raise InvalidDomainValue("Observed status requires a typed snapshot")
            if related_id(self.snapshot) != self.entity_id:
                raise InvalidDomainValue("Observation ID must match snapshot")
        elif self.snapshot is not None:
            raise InvalidDomainValue(
                "Missing/unresolved observation cannot fabricate snapshot"
            )


def require_independent(
    actor: ActorIdentity, principals: tuple[ActorIdentity, ...]
) -> None:
    if actor.actor_type in {ActorType.WORKER, ActorType.REQUESTER, ActorType.SYSTEM}:
        raise InvariantViolation(
            "Creation evidence requires an independent orchestration boundary"
        )
    if any(actor.actor_id == principal.actor_id for principal in principals):
        raise InvariantViolation(
            "Creation evidence cannot relabel a producing/requesting principal"
        )


def require_current(
    observation: CreationRelationshipObservation,
    identity: CreationRequestIdentity,
    entity_id: RelatedId,
    principals: tuple[ActorIdentity, ...],
) -> RelatedSnapshot:
    if observation.request_identity != identity or observation.entity_id != entity_id:
        raise InvariantViolation(
            "Relationship observation must exact-bind request and entity"
        )
    require_independent(observation.observed_by, principals)
    if observation.status is CreationObservationStatus.MISSING:
        raise EntityNotFound("Creation relationship entity is missing")
    if observation.status is not CreationObservationStatus.CURRENT:
        raise InvariantViolation("Creation relationship observation is not CURRENT")
    assert observation.snapshot is not None
    return observation.snapshot
