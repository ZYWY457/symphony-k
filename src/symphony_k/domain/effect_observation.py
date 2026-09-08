"""Immutable supporting facts about independently observed Effect occurrence.

Observation records describe externally anchored reality and provenance only. They
neither alter an Effect lifecycle snapshot nor authorize or dispatch an action.
"""

from dataclasses import dataclass
from enum import Enum

from .actors import ActorIdentity
from .candidate_refs import EvidenceRef
from .effect import (
    Effect,
    EffectDeduplicationRef,
    EffectExternalOperationRef,
    EffectPayloadRef,
    EffectTargetRef,
    ObservedEffectOrigin,
)
from .errors import InvalidDomainValue
from .ids import CorrelationId, EffectId, EffectObservationId
from .time import Timestamp
from .version import EntityVersion


class EffectOccurrenceStatus(Enum):
    """Supporting occurrence finding, deliberately separate from EffectState."""

    CONFIRMED = "CONFIRMED"
    UNCERTAIN = "UNCERTAIN"
    DISPROVED = "DISPROVED"


@dataclass(frozen=True, slots=True)
class EffectObservationRecord:
    """One immutable observation of an Effect's possible external occurrence."""

    observation_id: EffectObservationId
    effect_id: EffectId
    observed_effect_version: EntityVersion
    external_operation_ref: EffectExternalOperationRef
    deduplication_ref: EffectDeduplicationRef
    occurrence_status: EffectOccurrenceStatus
    target_ref: EffectTargetRef
    payload_ref: EffectPayloadRef | None
    evidence_refs: frozenset[EvidenceRef]
    observed_by: ActorIdentity
    recorded_by: ActorIdentity
    observed_at: Timestamp
    occurrence_at: Timestamp | None
    recorded_at: Timestamp
    correlation_id: CorrelationId
    prior_observation_id: EffectObservationId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.observation_id, EffectObservationId):
            raise InvalidDomainValue("observation_id must be an EffectObservationId")
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.observed_effect_version, EntityVersion):
            raise InvalidDomainValue("observed_effect_version must be an EntityVersion")
        if not isinstance(self.external_operation_ref, EffectExternalOperationRef):
            raise InvalidDomainValue(
                "external_operation_ref must be an EffectExternalOperationRef"
            )
        if not isinstance(self.deduplication_ref, EffectDeduplicationRef):
            raise InvalidDomainValue(
                "deduplication_ref must be an EffectDeduplicationRef"
            )
        if not isinstance(self.occurrence_status, EffectOccurrenceStatus):
            raise InvalidDomainValue(
                "occurrence_status must be an EffectOccurrenceStatus"
            )
        if not isinstance(self.target_ref, EffectTargetRef):
            raise InvalidDomainValue("target_ref must be an EffectTargetRef")
        if self.payload_ref is not None and not isinstance(
            self.payload_ref, EffectPayloadRef
        ):
            raise InvalidDomainValue("payload_ref must be an EffectPayloadRef or None")
        if not isinstance(self.evidence_refs, frozenset) or not self.evidence_refs:
            raise InvalidDomainValue("evidence_refs must be a nonempty frozenset")
        if any(
            not isinstance(reference, EvidenceRef) for reference in self.evidence_refs
        ):
            raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")
        if not isinstance(self.observed_by, ActorIdentity):
            raise InvalidDomainValue("observed_by must be an ActorIdentity")
        if not isinstance(self.recorded_by, ActorIdentity):
            raise InvalidDomainValue("recorded_by must be an ActorIdentity")
        if not isinstance(self.observed_at, Timestamp):
            raise InvalidDomainValue("observed_at must be a Timestamp")
        if self.occurrence_at is not None and not isinstance(
            self.occurrence_at, Timestamp
        ):
            raise InvalidDomainValue("occurrence_at must be a Timestamp or None")
        if not isinstance(self.recorded_at, Timestamp):
            raise InvalidDomainValue("recorded_at must be a Timestamp")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if self.prior_observation_id is not None and not isinstance(
            self.prior_observation_id, EffectObservationId
        ):
            raise InvalidDomainValue(
                "prior_observation_id must be an EffectObservationId or None"
            )
        if self.prior_observation_id == self.observation_id:
            raise InvalidDomainValue("prior_observation_id must not self-reference")


def can_attach_effect_observation(
    effect: Effect, observation: EffectObservationRecord
) -> bool:
    """Check exact structural compatibility without mutation or authority semantics."""
    if not isinstance(effect, Effect):
        raise InvalidDomainValue("effect must be an Effect")
    if not isinstance(observation, EffectObservationRecord):
        raise InvalidDomainValue("observation must be an EffectObservationRecord")
    if (
        observation.effect_id != effect.effect_id
        or observation.observed_effect_version != effect.version
        or observation.target_ref != effect.target_ref
    ):
        return False
    if (
        isinstance(effect.origin, ObservedEffectOrigin)
        and observation.external_operation_ref != effect.origin.external_operation_ref
    ):
        return False
    return (
        effect.payload_ref is None
        or observation.payload_ref is None
        or effect.payload_ref == observation.payload_ref
    )


def can_follow_effect_observation(
    previous: EffectObservationRecord, current: EffectObservationRecord
) -> bool:
    """Check explicit lineage compatibility without selecting any effective status."""
    if not isinstance(previous, EffectObservationRecord):
        raise InvalidDomainValue("previous must be an EffectObservationRecord")
    if not isinstance(current, EffectObservationRecord):
        raise InvalidDomainValue("current must be an EffectObservationRecord")
    return (
        current.prior_observation_id == previous.observation_id
        and current.effect_id == previous.effect_id
        and current.external_operation_ref == previous.external_operation_ref
        and current.deduplication_ref == previous.deduplication_ref
        and current.correlation_id == previous.correlation_id
        and current.observed_effect_version.value
        >= previous.observed_effect_version.value
    )
