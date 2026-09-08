"""Immutable Effect rollback and compensation provenance.

These supporting records preserve evidence about remedial facts without
authorizing, executing, or transitioning an Effect.  Rollback establishes
restoration of prior external state; compensation retains the original mutation
and identifies separate governed Effects used to address it.
"""

from dataclasses import dataclass

from .actors import ActorIdentity
from .candidate_refs import EvidenceRef
from .effect import Effect, EffectExternalOperationRef
from .errors import InvalidDomainValue
from .ids import (
    CorrelationId,
    EffectCompensationCompletionId,
    EffectCompensationPlanId,
    EffectId,
    EffectObservationId,
    EffectRollbackRecordId,
)
from .time import Timestamp
from .version import EntityVersion


def _require_evidence_refs(evidence_refs: frozenset[EvidenceRef]) -> None:
    if not isinstance(evidence_refs, frozenset) or not evidence_refs:
        raise InvalidDomainValue("evidence_refs must be a nonempty frozenset")
    if any(not isinstance(reference, EvidenceRef) for reference in evidence_refs):
        raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")


def _require_summary(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InvalidDomainValue(f"{field_name} must contain non-whitespace text")


@dataclass(frozen=True, slots=True)
class EffectRollbackRecord:
    """Independent evidence that an Effect's prior external state was restored."""

    rollback_record_id: EffectRollbackRecordId
    effect_id: EffectId
    observed_effect_version: EntityVersion
    original_commit_observation_id: EffectObservationId
    restoration_operation_ref: EffectExternalOperationRef
    restoration_summary: str
    evidence_refs: frozenset[EvidenceRef]
    verified_by: ActorIdentity
    recorded_by: ActorIdentity
    verified_at: Timestamp
    recorded_at: Timestamp
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.rollback_record_id, EffectRollbackRecordId):
            raise InvalidDomainValue(
                "rollback_record_id must be an EffectRollbackRecordId"
            )
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.observed_effect_version, EntityVersion):
            raise InvalidDomainValue("observed_effect_version must be an EntityVersion")
        if not isinstance(self.original_commit_observation_id, EffectObservationId):
            raise InvalidDomainValue(
                "original_commit_observation_id must be an EffectObservationId"
            )
        if not isinstance(self.restoration_operation_ref, EffectExternalOperationRef):
            raise InvalidDomainValue(
                "restoration_operation_ref must be an EffectExternalOperationRef"
            )
        _require_summary(self.restoration_summary, "restoration_summary")
        _require_evidence_refs(self.evidence_refs)
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


@dataclass(frozen=True, slots=True)
class EffectCompensationPlanRecord:
    """Supporting provenance linking an original Effect to governed compensations."""

    plan_id: EffectCompensationPlanId
    effect_id: EffectId
    observed_effect_version: EntityVersion
    original_commit_observation_id: EffectObservationId
    compensating_effect_ids: frozenset[EffectId]
    compensation_summary: str
    evidence_refs: frozenset[EvidenceRef]
    planned_by: ActorIdentity
    recorded_by: ActorIdentity
    planned_at: Timestamp
    recorded_at: Timestamp
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.plan_id, EffectCompensationPlanId):
            raise InvalidDomainValue("plan_id must be an EffectCompensationPlanId")
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.observed_effect_version, EntityVersion):
            raise InvalidDomainValue("observed_effect_version must be an EntityVersion")
        if not isinstance(self.original_commit_observation_id, EffectObservationId):
            raise InvalidDomainValue(
                "original_commit_observation_id must be an EffectObservationId"
            )
        if (
            not isinstance(self.compensating_effect_ids, frozenset)
            or not self.compensating_effect_ids
        ):
            raise InvalidDomainValue(
                "compensating_effect_ids must be a nonempty frozenset"
            )
        if any(
            not isinstance(effect_id, EffectId)
            for effect_id in self.compensating_effect_ids
        ):
            raise InvalidDomainValue("Every compensating effect ID must be an EffectId")
        if self.effect_id in self.compensating_effect_ids:
            raise InvalidDomainValue("An Effect must not compensate itself")
        _require_summary(self.compensation_summary, "compensation_summary")
        _require_evidence_refs(self.evidence_refs)
        if not isinstance(self.planned_by, ActorIdentity):
            raise InvalidDomainValue("planned_by must be an ActorIdentity")
        if not isinstance(self.recorded_by, ActorIdentity):
            raise InvalidDomainValue("recorded_by must be an ActorIdentity")
        if not isinstance(self.planned_at, Timestamp):
            raise InvalidDomainValue("planned_at must be a Timestamp")
        if not isinstance(self.recorded_at, Timestamp):
            raise InvalidDomainValue("recorded_at must be a Timestamp")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")


@dataclass(frozen=True, slots=True)
class EffectCompensationCompletionRecord:
    """Independent evidence that every action in a compensation plan completed."""

    completion_id: EffectCompensationCompletionId
    plan_id: EffectCompensationPlanId
    effect_id: EffectId
    observed_effect_version: EntityVersion
    original_commit_observation_id: EffectObservationId
    completion_summary: str
    residual_impact_summary: str
    evidence_refs: frozenset[EvidenceRef]
    verified_by: ActorIdentity
    recorded_by: ActorIdentity
    verified_at: Timestamp
    recorded_at: Timestamp
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.completion_id, EffectCompensationCompletionId):
            raise InvalidDomainValue(
                "completion_id must be an EffectCompensationCompletionId"
            )
        if not isinstance(self.plan_id, EffectCompensationPlanId):
            raise InvalidDomainValue("plan_id must be an EffectCompensationPlanId")
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.observed_effect_version, EntityVersion):
            raise InvalidDomainValue("observed_effect_version must be an EntityVersion")
        if not isinstance(self.original_commit_observation_id, EffectObservationId):
            raise InvalidDomainValue(
                "original_commit_observation_id must be an EffectObservationId"
            )
        _require_summary(self.completion_summary, "completion_summary")
        _require_summary(self.residual_impact_summary, "residual_impact_summary")
        _require_evidence_refs(self.evidence_refs)
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


def can_attach_effect_rollback_record(
    effect: Effect, record: EffectRollbackRecord
) -> bool:
    """Check exact snapshot compatibility without transition or observation lookup."""
    if not isinstance(effect, Effect):
        raise InvalidDomainValue("effect must be an Effect")
    if not isinstance(record, EffectRollbackRecord):
        raise InvalidDomainValue("record must be an EffectRollbackRecord")
    return (
        record.effect_id == effect.effect_id
        and record.observed_effect_version == effect.version
    )


def can_complete_effect_compensation_plan(
    plan: EffectCompensationPlanRecord,
    completion: EffectCompensationCompletionRecord,
) -> bool:
    """Check structural plan/completion compatibility without Effect lookup."""
    if not isinstance(plan, EffectCompensationPlanRecord):
        raise InvalidDomainValue("plan must be an EffectCompensationPlanRecord")
    if not isinstance(completion, EffectCompensationCompletionRecord):
        raise InvalidDomainValue(
            "completion must be an EffectCompensationCompletionRecord"
        )
    return (
        completion.plan_id == plan.plan_id
        and completion.effect_id == plan.effect_id
        and completion.correlation_id == plan.correlation_id
        and completion.observed_effect_version.value
        >= plan.observed_effect_version.value
    )
