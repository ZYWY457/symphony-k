"""Immutable provenance for preparing, verifying, and authorizing an Effect.

These supporting records describe prospective pre-commit control facts for one
exact Effect snapshot. They do not mutate lifecycle state, execute an external
action, establish occurrence, or rewrite historical authorization/governance.
"""

from dataclasses import dataclass

from .actors import ActorIdentity
from .candidate_refs import EvidenceRef
from .effect import Effect
from .errors import InvalidDomainValue
from .ids import (
    CorrelationId,
    EffectExecutionAuthorizationId,
    EffectId,
    EffectPreparationRecordId,
    EffectVerificationRecordId,
)
from .time import Timestamp
from .version import EntityVersion


def _require_summary(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InvalidDomainValue(f"{field_name} must contain non-whitespace text")


def _require_evidence_refs(evidence_refs: frozenset[EvidenceRef]) -> None:
    if not isinstance(evidence_refs, frozenset) or not evidence_refs:
        raise InvalidDomainValue("evidence_refs must be a nonempty frozenset")
    if any(not isinstance(reference, EvidenceRef) for reference in evidence_refs):
        raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")


@dataclass(frozen=True, slots=True)
class EffectPreparationRecord:
    """Intentional preparation of one exact Effect snapshot for governed use."""

    preparation_id: EffectPreparationRecordId
    effect_id: EffectId
    observed_effect_version: EntityVersion
    preparation_summary: str
    prepared_by: ActorIdentity
    recorded_by: ActorIdentity
    prepared_at: Timestamp
    recorded_at: Timestamp
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.preparation_id, EffectPreparationRecordId):
            raise InvalidDomainValue(
                "preparation_id must be an EffectPreparationRecordId"
            )
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.observed_effect_version, EntityVersion):
            raise InvalidDomainValue("observed_effect_version must be an EntityVersion")
        _require_summary(self.preparation_summary, "preparation_summary")
        if not isinstance(self.prepared_by, ActorIdentity):
            raise InvalidDomainValue("prepared_by must be an ActorIdentity")
        if not isinstance(self.recorded_by, ActorIdentity):
            raise InvalidDomainValue("recorded_by must be an ActorIdentity")
        if not isinstance(self.prepared_at, Timestamp):
            raise InvalidDomainValue("prepared_at must be a Timestamp")
        if not isinstance(self.recorded_at, Timestamp):
            raise InvalidDomainValue("recorded_at must be a Timestamp")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")


@dataclass(frozen=True, slots=True)
class EffectVerificationRecord:
    """Successful independent verification of one prepared Effect snapshot."""

    verification_id: EffectVerificationRecordId
    preparation_id: EffectPreparationRecordId
    effect_id: EffectId
    observed_effect_version: EntityVersion
    verification_summary: str
    evidence_refs: frozenset[EvidenceRef]
    verified_by: ActorIdentity
    recorded_by: ActorIdentity
    verified_at: Timestamp
    recorded_at: Timestamp
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.verification_id, EffectVerificationRecordId):
            raise InvalidDomainValue(
                "verification_id must be an EffectVerificationRecordId"
            )
        if not isinstance(self.preparation_id, EffectPreparationRecordId):
            raise InvalidDomainValue(
                "preparation_id must be an EffectPreparationRecordId"
            )
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.observed_effect_version, EntityVersion):
            raise InvalidDomainValue("observed_effect_version must be an EntityVersion")
        _require_summary(self.verification_summary, "verification_summary")
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
class EffectExecutionAuthorizationRecord:
    """Prospective authorization decision for one exact prepared Effect snapshot."""

    authorization_id: EffectExecutionAuthorizationId
    preparation_id: EffectPreparationRecordId
    effect_id: EffectId
    authorized_effect_version: EntityVersion
    verification_ids: frozenset[EffectVerificationRecordId]
    authorization_summary: str
    evidence_refs: frozenset[EvidenceRef]
    authorized_by: ActorIdentity
    recorded_by: ActorIdentity
    authorized_at: Timestamp
    recorded_at: Timestamp
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.authorization_id, EffectExecutionAuthorizationId):
            raise InvalidDomainValue(
                "authorization_id must be an EffectExecutionAuthorizationId"
            )
        if not isinstance(self.preparation_id, EffectPreparationRecordId):
            raise InvalidDomainValue(
                "preparation_id must be an EffectPreparationRecordId"
            )
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.authorized_effect_version, EntityVersion):
            raise InvalidDomainValue(
                "authorized_effect_version must be an EntityVersion"
            )
        if (
            not isinstance(self.verification_ids, frozenset)
            or not self.verification_ids
        ):
            raise InvalidDomainValue("verification_ids must be a nonempty frozenset")
        if any(
            not isinstance(identity, EffectVerificationRecordId)
            for identity in self.verification_ids
        ):
            raise InvalidDomainValue(
                "Every verification ID must be an EffectVerificationRecordId"
            )
        _require_summary(self.authorization_summary, "authorization_summary")
        _require_evidence_refs(self.evidence_refs)
        if not isinstance(self.authorized_by, ActorIdentity):
            raise InvalidDomainValue("authorized_by must be an ActorIdentity")
        if not isinstance(self.recorded_by, ActorIdentity):
            raise InvalidDomainValue("recorded_by must be an ActorIdentity")
        if not isinstance(self.authorized_at, Timestamp):
            raise InvalidDomainValue("authorized_at must be a Timestamp")
        if not isinstance(self.recorded_at, Timestamp):
            raise InvalidDomainValue("recorded_at must be a Timestamp")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")


def can_attach_effect_preparation_record(
    effect: Effect, preparation: EffectPreparationRecord
) -> bool:
    """Check exact snapshot compatibility without state or authority semantics."""
    if not isinstance(effect, Effect):
        raise InvalidDomainValue("effect must be an Effect")
    if not isinstance(preparation, EffectPreparationRecord):
        raise InvalidDomainValue("preparation must be an EffectPreparationRecord")
    return (
        preparation.effect_id == effect.effect_id
        and preparation.observed_effect_version == effect.version
    )


def can_verify_effect_preparation(
    preparation: EffectPreparationRecord,
    verification: EffectVerificationRecord,
) -> bool:
    """Check explicit preparation/verification identity and snapshot compatibility."""
    if not isinstance(preparation, EffectPreparationRecord):
        raise InvalidDomainValue("preparation must be an EffectPreparationRecord")
    if not isinstance(verification, EffectVerificationRecord):
        raise InvalidDomainValue("verification must be an EffectVerificationRecord")
    return (
        verification.preparation_id == preparation.preparation_id
        and verification.effect_id == preparation.effect_id
        and verification.observed_effect_version == preparation.observed_effect_version
        and verification.correlation_id == preparation.correlation_id
    )


def can_authorize_effect_preparation(
    preparation: EffectPreparationRecord,
    authorization: EffectExecutionAuthorizationRecord,
) -> bool:
    """Check exact preparation/authorization compatibility without granting it."""
    if not isinstance(preparation, EffectPreparationRecord):
        raise InvalidDomainValue("preparation must be an EffectPreparationRecord")
    if not isinstance(authorization, EffectExecutionAuthorizationRecord):
        raise InvalidDomainValue(
            "authorization must be an EffectExecutionAuthorizationRecord"
        )
    return (
        authorization.preparation_id == preparation.preparation_id
        and authorization.effect_id == preparation.effect_id
        and authorization.authorized_effect_version
        == preparation.observed_effect_version
        and authorization.correlation_id == preparation.correlation_id
    )


def can_use_effect_verification_for_authorization(
    verification: EffectVerificationRecord,
    authorization: EffectExecutionAuthorizationRecord,
) -> bool:
    """Check explicitly referenced verification without inferred precedence."""
    if not isinstance(verification, EffectVerificationRecord):
        raise InvalidDomainValue("verification must be an EffectVerificationRecord")
    if not isinstance(authorization, EffectExecutionAuthorizationRecord):
        raise InvalidDomainValue(
            "authorization must be an EffectExecutionAuthorizationRecord"
        )
    return (
        verification.verification_id in authorization.verification_ids
        and verification.preparation_id == authorization.preparation_id
        and verification.effect_id == authorization.effect_id
        and verification.observed_effect_version
        == authorization.authorized_effect_version
        and verification.correlation_id == authorization.correlation_id
    )
