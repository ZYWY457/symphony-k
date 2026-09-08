"""Immutable historical findings about prior Effect authorization.

These records describe what evidence establishes about authorization that
already existed.  They neither grant permission nor alter Effect lifecycle.
"""

from dataclasses import dataclass
from enum import Enum

from .actors import ActorIdentity
from .candidate_refs import EvidenceRef
from .effect import Effect
from .errors import InvalidDomainValue
from .ids import CorrelationId, EffectAuthorizationFindingId, EffectId
from .time import Timestamp
from .version import EntityVersion


class EffectAuthorizationStatus(Enum):
    """Evidence-backed historical finding, not execution authorization."""

    AUTHORIZED = "AUTHORIZED"
    UNAUTHORIZED = "UNAUTHORIZED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class EffectAuthorizationFindingRecord:
    """One immutable finding about whether prior authorization existed."""

    finding_id: EffectAuthorizationFindingId
    effect_id: EffectId
    observed_effect_version: EntityVersion
    status: EffectAuthorizationStatus
    finding_summary: str
    evidence_refs: frozenset[EvidenceRef]
    determined_by: ActorIdentity
    recorded_by: ActorIdentity
    determined_at: Timestamp
    recorded_at: Timestamp
    correlation_id: CorrelationId
    prior_finding_id: EffectAuthorizationFindingId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.finding_id, EffectAuthorizationFindingId):
            raise InvalidDomainValue(
                "finding_id must be an EffectAuthorizationFindingId"
            )
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.observed_effect_version, EntityVersion):
            raise InvalidDomainValue("observed_effect_version must be an EntityVersion")
        if not isinstance(self.status, EffectAuthorizationStatus):
            raise InvalidDomainValue("status must be an EffectAuthorizationStatus")
        if (
            not isinstance(self.finding_summary, str)
            or not self.finding_summary.strip()
        ):
            raise InvalidDomainValue("finding_summary must contain non-whitespace text")
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
        if self.prior_finding_id is not None and not isinstance(
            self.prior_finding_id, EffectAuthorizationFindingId
        ):
            raise InvalidDomainValue(
                "prior_finding_id must be an EffectAuthorizationFindingId or None"
            )
        if self.prior_finding_id == self.finding_id:
            raise InvalidDomainValue("prior_finding_id must not self-reference")


def can_attach_effect_authorization_finding(
    effect: Effect, finding: EffectAuthorizationFindingRecord
) -> bool:
    """Check exact snapshot compatibility without authority or mutation semantics."""
    if not isinstance(effect, Effect):
        raise InvalidDomainValue("effect must be an Effect")
    if not isinstance(finding, EffectAuthorizationFindingRecord):
        raise InvalidDomainValue("finding must be an EffectAuthorizationFindingRecord")
    return (
        finding.effect_id == effect.effect_id
        and finding.observed_effect_version == effect.version
    )


def can_follow_effect_authorization_finding(
    previous: EffectAuthorizationFindingRecord,
    current: EffectAuthorizationFindingRecord,
) -> bool:
    """Check explicit lineage only; timestamps do not select finding precedence."""
    if not isinstance(previous, EffectAuthorizationFindingRecord):
        raise InvalidDomainValue("previous must be an EffectAuthorizationFindingRecord")
    if not isinstance(current, EffectAuthorizationFindingRecord):
        raise InvalidDomainValue("current must be an EffectAuthorizationFindingRecord")
    return (
        current.prior_finding_id == previous.finding_id
        and current.effect_id == previous.effect_id
        and current.correlation_id == previous.correlation_id
        and current.observed_effect_version.value
        >= previous.observed_effect_version.value
    )
