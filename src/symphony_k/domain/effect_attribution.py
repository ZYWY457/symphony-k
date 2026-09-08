"""Immutable supporting facts about verified Effect Task/Run attribution.

Attribution records preserve later verified associations without changing an
Effect's immutable creation origin.  They grant no authority and select no
effective attribution.
"""

from dataclasses import dataclass

from .actors import ActorIdentity
from .candidate_refs import EvidenceRef
from .effect import Effect, ObservedEffectOrigin
from .errors import InvalidDomainValue
from .ids import CorrelationId, EffectAttributionId, EffectId, RunId, TaskId
from .time import Timestamp
from .version import EntityVersion


@dataclass(frozen=True, slots=True)
class EffectAttributionRecord:
    """One immutable, evidence-backed positive Task/Run association for an Effect."""

    attribution_id: EffectAttributionId
    effect_id: EffectId
    observed_effect_version: EntityVersion
    task_id: TaskId
    run_id: RunId | None
    evidence_refs: frozenset[EvidenceRef]
    attribution_summary: str
    verified_by: ActorIdentity
    recorded_by: ActorIdentity
    verified_at: Timestamp
    recorded_at: Timestamp
    correlation_id: CorrelationId
    prior_attribution_id: EffectAttributionId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.attribution_id, EffectAttributionId):
            raise InvalidDomainValue("attribution_id must be an EffectAttributionId")
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.observed_effect_version, EntityVersion):
            raise InvalidDomainValue("observed_effect_version must be an EntityVersion")
        if not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId")
        if self.run_id is not None and not isinstance(self.run_id, RunId):
            raise InvalidDomainValue("run_id must be a RunId or None")
        if not isinstance(self.evidence_refs, frozenset) or not self.evidence_refs:
            raise InvalidDomainValue("evidence_refs must be a nonempty frozenset")
        if any(
            not isinstance(reference, EvidenceRef) for reference in self.evidence_refs
        ):
            raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")
        if (
            not isinstance(self.attribution_summary, str)
            or not self.attribution_summary.strip()
        ):
            raise InvalidDomainValue(
                "attribution_summary must contain non-whitespace text"
            )
        if not isinstance(self.verified_by, ActorIdentity):
            raise InvalidDomainValue("verified_by must be an ActorIdentity")
        if not isinstance(self.recorded_by, ActorIdentity):
            raise InvalidDomainValue("recorded_by must be an ActorIdentity")
        if not isinstance(self.verified_at, Timestamp):
            raise InvalidDomainValue("verified_at must be a Timestamp")
        if not isinstance(self.recorded_at, Timestamp):
            raise InvalidDomainValue("recorded_at must be a Timestamp")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if self.prior_attribution_id is not None and not isinstance(
            self.prior_attribution_id, EffectAttributionId
        ):
            raise InvalidDomainValue(
                "prior_attribution_id must be an EffectAttributionId or None"
            )
        if self.prior_attribution_id == self.attribution_id:
            raise InvalidDomainValue("prior_attribution_id must not self-reference")


def can_attach_effect_attribution(
    effect: Effect, attribution: EffectAttributionRecord
) -> bool:
    """Check observation-origin attribution compatibility without mutation."""
    if not isinstance(effect, Effect):
        raise InvalidDomainValue("effect must be an Effect")
    if not isinstance(attribution, EffectAttributionRecord):
        raise InvalidDomainValue("attribution must be an EffectAttributionRecord")
    if not isinstance(effect.origin, ObservedEffectOrigin):
        return False
    if (
        attribution.effect_id != effect.effect_id
        or attribution.observed_effect_version != effect.version
    ):
        return False
    if (
        effect.origin.task_id is not None
        and attribution.task_id != effect.origin.task_id
    ):
        return False
    return effect.origin.run_id is None or attribution.run_id == effect.origin.run_id


def can_follow_effect_attribution(
    previous: EffectAttributionRecord, current: EffectAttributionRecord
) -> bool:
    """Check explicit attribution refinement without resolving competing records."""
    if not isinstance(previous, EffectAttributionRecord):
        raise InvalidDomainValue("previous must be an EffectAttributionRecord")
    if not isinstance(current, EffectAttributionRecord):
        raise InvalidDomainValue("current must be an EffectAttributionRecord")
    if (
        current.prior_attribution_id != previous.attribution_id
        or current.effect_id != previous.effect_id
        or current.correlation_id != previous.correlation_id
        or current.task_id != previous.task_id
        or current.observed_effect_version.value
        < previous.observed_effect_version.value
    ):
        return False
    return previous.run_id is None or current.run_id == previous.run_id
