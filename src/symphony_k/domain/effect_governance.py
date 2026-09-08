"""Immutable historical findings about Effect compliance with exact policies.

Governance findings preserve policy-scoped evidence.  They do not evaluate a
policy, imply authorization, or alter Effect lifecycle.
"""

from dataclasses import dataclass
from enum import Enum

from .actors import ActorIdentity
from .candidate_refs import EvidenceRef
from .effect import Effect
from .errors import InvalidDomainValue
from .ids import CorrelationId, EffectGovernanceFindingId, EffectId
from .time import Timestamp
from .version import EntityVersion


class EffectGovernanceStatus(Enum):
    """Evidence-backed finding for one exact policy reference."""

    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class EffectGovernancePolicyRef:
    """Opaque identity of the exact governance policy and version assessed."""

    policy_id: str
    policy_version: str

    def __post_init__(self) -> None:
        if not isinstance(self.policy_id, str) or not self.policy_id.strip():
            raise InvalidDomainValue("policy_id must contain non-whitespace text")
        if not isinstance(self.policy_version, str) or not self.policy_version.strip():
            raise InvalidDomainValue("policy_version must contain non-whitespace text")


@dataclass(frozen=True, slots=True)
class EffectGovernanceFindingRecord:
    """One immutable finding about an Effect under one exact policy version."""

    finding_id: EffectGovernanceFindingId
    effect_id: EffectId
    observed_effect_version: EntityVersion
    policy_ref: EffectGovernancePolicyRef
    status: EffectGovernanceStatus
    finding_summary: str
    evidence_refs: frozenset[EvidenceRef]
    determined_by: ActorIdentity
    recorded_by: ActorIdentity
    determined_at: Timestamp
    recorded_at: Timestamp
    correlation_id: CorrelationId
    prior_finding_id: EffectGovernanceFindingId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.finding_id, EffectGovernanceFindingId):
            raise InvalidDomainValue("finding_id must be an EffectGovernanceFindingId")
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.observed_effect_version, EntityVersion):
            raise InvalidDomainValue("observed_effect_version must be an EntityVersion")
        if not isinstance(self.policy_ref, EffectGovernancePolicyRef):
            raise InvalidDomainValue("policy_ref must be an EffectGovernancePolicyRef")
        if not isinstance(self.status, EffectGovernanceStatus):
            raise InvalidDomainValue("status must be an EffectGovernanceStatus")
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
            self.prior_finding_id, EffectGovernanceFindingId
        ):
            raise InvalidDomainValue(
                "prior_finding_id must be an EffectGovernanceFindingId or None"
            )
        if self.prior_finding_id == self.finding_id:
            raise InvalidDomainValue("prior_finding_id must not self-reference")


def can_attach_effect_governance_finding(
    effect: Effect, finding: EffectGovernanceFindingRecord
) -> bool:
    """Check exact snapshot compatibility without policy evaluation or mutation."""
    if not isinstance(effect, Effect):
        raise InvalidDomainValue("effect must be an Effect")
    if not isinstance(finding, EffectGovernanceFindingRecord):
        raise InvalidDomainValue("finding must be an EffectGovernanceFindingRecord")
    return (
        finding.effect_id == effect.effect_id
        and finding.observed_effect_version == effect.version
    )


def can_follow_effect_governance_finding(
    previous: EffectGovernanceFindingRecord,
    current: EffectGovernanceFindingRecord,
) -> bool:
    """Check explicit same-policy lineage without resolving competing findings."""
    if not isinstance(previous, EffectGovernanceFindingRecord):
        raise InvalidDomainValue("previous must be an EffectGovernanceFindingRecord")
    if not isinstance(current, EffectGovernanceFindingRecord):
        raise InvalidDomainValue("current must be an EffectGovernanceFindingRecord")
    return (
        current.prior_finding_id == previous.finding_id
        and current.effect_id == previous.effect_id
        and current.policy_ref == previous.policy_ref
        and current.correlation_id == previous.correlation_id
        and current.observed_effect_version.value
        >= previous.observed_effect_version.value
    )
