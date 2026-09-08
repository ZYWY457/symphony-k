"""Immutable supporting history for explicit Effect incident findings.

Incident records are evidence-backed governance history. They do not change an
Effect lifecycle snapshot, infer any other Effect truth dimension, or authorize
execution, rollback, or compensation.
"""

from dataclasses import dataclass
from enum import Enum

from .actors import ActorIdentity
from .candidate_refs import EvidenceRef
from .effect import Effect
from .errors import InvalidDomainValue
from .ids import CorrelationId, EffectId, EffectIncidentId, EffectIncidentRecordId
from .time import Timestamp
from .version import EntityVersion


class EffectIncidentStatus(Enum):
    """Supporting incident-history status, separate from Effect lifecycle."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass(frozen=True, slots=True)
class EffectIncidentRecord:
    """One immutable, evidence-backed registration of an Effect incident."""

    record_id: EffectIncidentRecordId
    incident_id: EffectIncidentId
    effect_id: EffectId
    observed_effect_version: EntityVersion
    status: EffectIncidentStatus
    incident_summary: str
    evidence_refs: frozenset[EvidenceRef]
    determined_by: ActorIdentity
    recorded_by: ActorIdentity
    determined_at: Timestamp
    recorded_at: Timestamp
    correlation_id: CorrelationId
    prior_record_id: EffectIncidentRecordId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.record_id, EffectIncidentRecordId):
            raise InvalidDomainValue("record_id must be an EffectIncidentRecordId")
        if not isinstance(self.incident_id, EffectIncidentId):
            raise InvalidDomainValue("incident_id must be an EffectIncidentId")
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.observed_effect_version, EntityVersion):
            raise InvalidDomainValue("observed_effect_version must be an EntityVersion")
        if not isinstance(self.status, EffectIncidentStatus):
            raise InvalidDomainValue("status must be an EffectIncidentStatus")
        if (
            not isinstance(self.incident_summary, str)
            or not self.incident_summary.strip()
        ):
            raise InvalidDomainValue(
                "incident_summary must contain non-whitespace text"
            )
        if not isinstance(self.evidence_refs, frozenset) or not self.evidence_refs:
            raise InvalidDomainValue("evidence_refs must be a nonempty frozenset")
        if any(
            not isinstance(reference, EvidenceRef) for reference in self.evidence_refs
        ):
            raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")
        if not isinstance(self.determined_by, ActorIdentity):
            raise InvalidDomainValue("determined_by must be an ActorIdentity")
        if not isinstance(self.recorded_by, ActorIdentity):
            raise InvalidDomainValue("recorded_by must be an ActorIdentity")
        if not isinstance(self.determined_at, Timestamp):
            raise InvalidDomainValue("determined_at must be a Timestamp")
        if not isinstance(self.recorded_at, Timestamp):
            raise InvalidDomainValue("recorded_at must be a Timestamp")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if self.prior_record_id is not None and not isinstance(
            self.prior_record_id, EffectIncidentRecordId
        ):
            raise InvalidDomainValue(
                "prior_record_id must be an EffectIncidentRecordId or None"
            )
        if self.prior_record_id == self.record_id:
            raise InvalidDomainValue("prior_record_id must not self-reference")


def can_attach_effect_incident_record(
    effect: Effect, record: EffectIncidentRecord
) -> bool:
    """Check exact snapshot compatibility without lifecycle mutation or inference."""
    if not isinstance(effect, Effect):
        raise InvalidDomainValue("effect must be an Effect")
    if not isinstance(record, EffectIncidentRecord):
        raise InvalidDomainValue("record must be an EffectIncidentRecord")
    return (
        record.effect_id == effect.effect_id
        and record.observed_effect_version == effect.version
    )


def can_follow_effect_incident_record(
    previous: EffectIncidentRecord, current: EffectIncidentRecord
) -> bool:
    """Check explicit append-only lineage without resolving an effective status."""
    if not isinstance(previous, EffectIncidentRecord):
        raise InvalidDomainValue("previous must be an EffectIncidentRecord")
    if not isinstance(current, EffectIncidentRecord):
        raise InvalidDomainValue("current must be an EffectIncidentRecord")
    return (
        current.prior_record_id == previous.record_id
        and current.incident_id == previous.incident_id
        and current.effect_id == previous.effect_id
        and current.correlation_id == previous.correlation_id
        and current.observed_effect_version.value
        >= previous.observed_effect_version.value
    )
