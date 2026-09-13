"""Canonical pure semantic guards for accepted Effect lifecycle edges.

These types represent immutable supporting provenance for the exact Effect
attempt. They do not load records, run validators, grant lifecycle authority,
dispatch, remediate, create observations, or cause an external action.
"""

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Final

from .actors import ActorIdentity, ActorType
from .candidate_refs import EvidenceRef
from .effect import (
    Effect,
    EffectDeduplicationRef,
    EffectExternalOperationRef,
    EffectPayloadRef,
    EffectState,
    EffectTargetRef,
    ObservedEffectOrigin,
    PlannedEffectOrigin,
)
from .effect_authorization import (
    EffectAuthorizationFindingRecord,
    can_attach_effect_authorization_finding,
)
from .effect_execution import (
    EffectPreparationRecord,
    EffectVerificationRecord,
    can_attach_effect_preparation_record,
    can_verify_effect_preparation,
)
from .effect_governance import (
    EffectGovernanceFindingRecord,
    can_attach_effect_governance_finding,
)
from .effect_incident import (
    EffectIncidentRecord,
    can_attach_effect_incident_record,
)
from .effect_observation import (
    EffectObservationRecord,
    EffectOccurrenceStatus,
    can_attach_effect_observation,
    can_follow_effect_observation,
)
from .effect_remediation import (
    EffectCompensationCompletionRecord,
    EffectCompensationPlanRecord,
    EffectRollbackRecord,
    can_attach_effect_rollback_record,
    can_complete_effect_compensation_plan,
)
from .errors import InvalidDomainValue, InvariantViolation
from .ids import (
    CorrelationId,
    EffectCompensationPlanId,
    EffectId,
    EffectIncidentRecordId,
    EffectObservationId,
    EffectQuarantineContextId,
    EffectRemediationReadinessId,
    EffectSimulationBypassDecisionId,
    EffectSimulationRecordId,
    EventId,
)
from .time import Timestamp
from .version import EntityVersion


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InvalidDomainValue(f"{field_name} must contain non-whitespace text")


def _require_evidence(evidence_refs: frozenset[EvidenceRef]) -> None:
    if not isinstance(evidence_refs, frozenset) or not evidence_refs:
        raise InvalidDomainValue("evidence_refs must be a nonempty frozenset")
    if any(not isinstance(reference, EvidenceRef) for reference in evidence_refs):
        raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")


@dataclass(frozen=True, slots=True)
class EffectOperationScope:
    """Canonical intended operation scope; it never defines lifecycle authority."""

    effect_id: EffectId
    observed_effect_version: EntityVersion
    target_ref: EffectTargetRef
    payload_ref: EffectPayloadRef
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.observed_effect_version, EntityVersion):
            raise InvalidDomainValue("observed_effect_version must be an EntityVersion")
        if not isinstance(self.target_ref, EffectTargetRef):
            raise InvalidDomainValue("target_ref must be an EffectTargetRef")
        if not isinstance(self.payload_ref, EffectPayloadRef):
            raise InvalidDomainValue("payload_ref must be an EffectPayloadRef")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")


@dataclass(frozen=True, slots=True)
class EffectObservationScope:
    """Immutable canonical scope for one observation-only lifecycle attempt."""

    effect_id: EffectId
    observed_effect_version: EntityVersion
    source_state: EffectState
    target_state: EffectState
    target_ref: EffectTargetRef
    external_operation_ref: EffectExternalOperationRef
    deduplication_ref: EffectDeduplicationRef
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.observed_effect_version, EntityVersion):
            raise InvalidDomainValue("observed_effect_version must be an EntityVersion")
        if not isinstance(self.source_state, EffectState) or not isinstance(
            self.target_state, EffectState
        ):
            raise InvalidDomainValue(
                "source_state and target_state must be EffectState"
            )
        if not isinstance(self.target_ref, EffectTargetRef):
            raise InvalidDomainValue("target_ref must be an EffectTargetRef")
        if not isinstance(self.external_operation_ref, EffectExternalOperationRef):
            raise InvalidDomainValue(
                "external_operation_ref must be an EffectExternalOperationRef"
            )
        if not isinstance(self.deduplication_ref, EffectDeduplicationRef):
            raise InvalidDomainValue(
                "deduplication_ref must be an EffectDeduplicationRef"
            )
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")


class EffectQuarantineReason(Enum):
    """Closed reconciliation categories; none is occurrence or authority truth."""

    UNKNOWN_OR_SUSPECTED_OCCURRENCE = "UNKNOWN_OR_SUSPECTED_OCCURRENCE"
    POST_COMMIT_PROBLEM = "POST_COMMIT_PROBLEM"
    COMPENSATION_OR_REMEDIATION_UNCERTAINTY = "COMPENSATION_OR_REMEDIATION_UNCERTAINTY"


@dataclass(frozen=True, slots=True)
class EffectQuarantineContext:
    """Immutable evidence-backed context for an exact quarantine attempt."""

    context_id: EffectQuarantineContextId
    observation_scope: EffectObservationScope
    reason: EffectQuarantineReason
    context_summary: str
    evidence_refs: frozenset[EvidenceRef]
    recorded_by: ActorIdentity
    recorded_at: Timestamp
    prior_observation_id: EffectObservationId | None = None
    original_commit_observation_id: EffectObservationId | None = None
    incident_record_id: EffectIncidentRecordId | None = None
    compensation_plan_id: EffectCompensationPlanId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, EffectQuarantineContextId):
            raise InvalidDomainValue("context_id must be an EffectQuarantineContextId")
        if not isinstance(self.observation_scope, EffectObservationScope):
            raise InvalidDomainValue(
                "observation_scope must be an EffectObservationScope"
            )
        if self.observation_scope.target_state is not EffectState.QUARANTINED:
            raise InvalidDomainValue("Quarantine context must target QUARANTINED")
        if not isinstance(self.reason, EffectQuarantineReason):
            raise InvalidDomainValue("reason must be an EffectQuarantineReason")
        _require_text(self.context_summary, "context_summary")
        _require_evidence(self.evidence_refs)
        if not isinstance(self.recorded_by, ActorIdentity):
            raise InvalidDomainValue("recorded_by must be an ActorIdentity")
        if not isinstance(self.recorded_at, Timestamp):
            raise InvalidDomainValue("recorded_at must be a Timestamp")
        if self.prior_observation_id is not None and not isinstance(
            self.prior_observation_id, EffectObservationId
        ):
            raise InvalidDomainValue(
                "prior_observation_id must be an EffectObservationId or None"
            )
        if self.original_commit_observation_id is not None and not isinstance(
            self.original_commit_observation_id, EffectObservationId
        ):
            raise InvalidDomainValue(
                "original_commit_observation_id must be an EffectObservationId or None"
            )
        if self.incident_record_id is not None and not isinstance(
            self.incident_record_id, EffectIncidentRecordId
        ):
            raise InvalidDomainValue(
                "incident_record_id must be an EffectIncidentRecordId or None"
            )
        if self.compensation_plan_id is not None and not isinstance(
            self.compensation_plan_id, EffectCompensationPlanId
        ):
            raise InvalidDomainValue(
                "compensation_plan_id must be an EffectCompensationPlanId or None"
            )


@dataclass(frozen=True, slots=True)
class EffectSimulationScopeRef:
    """Opaque scoped identity of one dry-run or preparation method."""

    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, "Effect simulation scope reference")


@dataclass(frozen=True, slots=True)
class EffectSimulationRecord:
    """Non-occurring dry-run provenance for one exact intended Effect operation."""

    simulation_id: EffectSimulationRecordId
    operation_scope: EffectOperationScope
    simulation_scope: EffectSimulationScopeRef
    simulation_summary: str
    evidence_refs: frozenset[EvidenceRef]
    simulated_by: ActorIdentity
    recorded_by: ActorIdentity
    simulated_at: Timestamp
    recorded_at: Timestamp

    def __post_init__(self) -> None:
        if not isinstance(self.simulation_id, EffectSimulationRecordId):
            raise InvalidDomainValue(
                "simulation_id must be an EffectSimulationRecordId"
            )
        if not isinstance(self.operation_scope, EffectOperationScope):
            raise InvalidDomainValue("operation_scope must be an EffectOperationScope")
        if not isinstance(self.simulation_scope, EffectSimulationScopeRef):
            raise InvalidDomainValue(
                "simulation_scope must be an EffectSimulationScopeRef"
            )
        _require_text(self.simulation_summary, "simulation_summary")
        _require_evidence(self.evidence_refs)
        if not isinstance(self.simulated_by, ActorIdentity):
            raise InvalidDomainValue("simulated_by must be an ActorIdentity")
        if not isinstance(self.recorded_by, ActorIdentity):
            raise InvalidDomainValue("recorded_by must be an ActorIdentity")
        if not isinstance(self.simulated_at, Timestamp):
            raise InvalidDomainValue("simulated_at must be a Timestamp")
        if not isinstance(self.recorded_at, Timestamp):
            raise InvalidDomainValue("recorded_at must be a Timestamp")


class EffectRemediationReadinessStatus(Enum):
    """Bounded pre-commit remediation facts; none asserts remediation occurred."""

    ROLLBACK_PREPARED = "ROLLBACK_PREPARED"
    COMPENSATION_PREPARED = "COMPENSATION_PREPARED"
    UNAVAILABLE_OR_IMPRACTICAL = "UNAVAILABLE_OR_IMPRACTICAL"


@dataclass(frozen=True, slots=True)
class EffectRemediationReadinessRecord:
    """Immutable pre-commit readiness fact, separate from post-commit remedies."""

    readiness_id: EffectRemediationReadinessId
    operation_scope: EffectOperationScope
    status: EffectRemediationReadinessStatus
    readiness_summary: str
    evidence_refs: frozenset[EvidenceRef]
    prepared_by: ActorIdentity
    recorded_by: ActorIdentity
    prepared_at: Timestamp
    recorded_at: Timestamp

    def __post_init__(self) -> None:
        if not isinstance(self.readiness_id, EffectRemediationReadinessId):
            raise InvalidDomainValue(
                "readiness_id must be an EffectRemediationReadinessId"
            )
        if not isinstance(self.operation_scope, EffectOperationScope):
            raise InvalidDomainValue("operation_scope must be an EffectOperationScope")
        if not isinstance(self.status, EffectRemediationReadinessStatus):
            raise InvalidDomainValue(
                "status must be an EffectRemediationReadinessStatus"
            )
        _require_text(self.readiness_summary, "readiness_summary")
        _require_evidence(self.evidence_refs)
        if not isinstance(self.prepared_by, ActorIdentity):
            raise InvalidDomainValue("prepared_by must be an ActorIdentity")
        if not isinstance(self.recorded_by, ActorIdentity):
            raise InvalidDomainValue("recorded_by must be an ActorIdentity")
        if not isinstance(self.prepared_at, Timestamp):
            raise InvalidDomainValue("prepared_at must be a Timestamp")
        if not isinstance(self.recorded_at, Timestamp):
            raise InvalidDomainValue("recorded_at must be a Timestamp")


class EffectRemediationKind(Enum):
    """Closed remedy kinds; rollback and compensation are never interchangeable."""

    ROLLBACK = "ROLLBACK"
    COMPENSATION = "COMPENSATION"


class EffectRemediationAuthorizationStatus(Enum):
    """Result of an already-made remediation authorization decision."""

    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class EffectRemediationAuthorizationRef:
    """Opaque durable identity of a remediation authorization decision."""

    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, "Effect remediation authorization reference")


@dataclass(frozen=True, slots=True)
class EffectRemediationAuthorizationScope:
    """Exact restoration operation or compensation plan authorized for one Effect."""

    effect_id: EffectId
    authorized_effect_version: EntityVersion
    original_commit_observation_id: EffectObservationId
    remediation_kind: EffectRemediationKind
    correlation_id: CorrelationId
    restoration_operation_ref: EffectExternalOperationRef | None = None
    compensation_plan_id: EffectCompensationPlanId | None = None
    compensating_effect_ids: frozenset[EffectId] = frozenset()

    def __post_init__(self) -> None:
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.authorized_effect_version, EntityVersion):
            raise InvalidDomainValue(
                "authorized_effect_version must be an EntityVersion"
            )
        if not isinstance(self.original_commit_observation_id, EffectObservationId):
            raise InvalidDomainValue(
                "original_commit_observation_id must be an EffectObservationId"
            )
        if not isinstance(self.remediation_kind, EffectRemediationKind):
            raise InvalidDomainValue(
                "remediation_kind must be an EffectRemediationKind"
            )
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if not isinstance(self.compensating_effect_ids, frozenset) or any(
            not isinstance(effect_id, EffectId)
            for effect_id in self.compensating_effect_ids
        ):
            raise InvalidDomainValue(
                "compensating_effect_ids must be a frozenset of EffectId values"
            )
        if self.remediation_kind is EffectRemediationKind.ROLLBACK:
            if not isinstance(
                self.restoration_operation_ref, EffectExternalOperationRef
            ):
                raise InvalidDomainValue(
                    "Rollback authorization requires a restoration operation"
                )
            if self.compensation_plan_id is not None or self.compensating_effect_ids:
                raise InvalidDomainValue(
                    "Rollback authorization must not contain compensation scope"
                )
            return
        if self.restoration_operation_ref is not None:
            raise InvalidDomainValue(
                "Compensation authorization must not contain restoration scope"
            )
        if not isinstance(self.compensation_plan_id, EffectCompensationPlanId):
            raise InvalidDomainValue(
                "Compensation authorization requires a compensation plan identity"
            )
        if not self.compensating_effect_ids:
            raise InvalidDomainValue(
                "Compensation authorization requires linked compensating Effects"
            )
        if self.effect_id in self.compensating_effect_ids:
            raise InvalidDomainValue(
                "An Effect must not authorize itself as compensation"
            )


@dataclass(frozen=True, slots=True)
class EffectRemediationAuthorizationDecision:
    """Policy authorization for an exact remedy, never M7 lifecycle authority."""

    decision_ref: EffectRemediationAuthorizationRef
    scope: EffectRemediationAuthorizationScope
    status: EffectRemediationAuthorizationStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    human_authorization_required: bool

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, EffectRemediationAuthorizationRef):
            raise InvalidDomainValue(
                "decision_ref must be an EffectRemediationAuthorizationRef"
            )
        if not isinstance(self.scope, EffectRemediationAuthorizationScope):
            raise InvalidDomainValue(
                "scope must be an EffectRemediationAuthorizationScope"
            )
        if not isinstance(self.status, EffectRemediationAuthorizationStatus):
            raise InvalidDomainValue(
                "status must be an EffectRemediationAuthorizationStatus"
            )
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)
        if not isinstance(self.human_authorization_required, bool):
            raise InvalidDomainValue("human_authorization_required must be a bool")


@dataclass(frozen=True, slots=True)
class EffectRemediationHumanAuthorization:
    """Affirmative human authorization exact-bound to one remediation decision."""

    authorization_ref: EffectRemediationAuthorizationRef
    scope: EffectRemediationAuthorizationScope
    policy_decision_ref: EffectRemediationAuthorizationRef
    affirmative: bool
    authorized_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]

    def __post_init__(self) -> None:
        if not isinstance(self.authorization_ref, EffectRemediationAuthorizationRef):
            raise InvalidDomainValue(
                "authorization_ref must be an EffectRemediationAuthorizationRef"
            )
        if not isinstance(self.scope, EffectRemediationAuthorizationScope):
            raise InvalidDomainValue(
                "scope must be an EffectRemediationAuthorizationScope"
            )
        if not isinstance(self.policy_decision_ref, EffectRemediationAuthorizationRef):
            raise InvalidDomainValue(
                "policy_decision_ref must be an EffectRemediationAuthorizationRef"
            )
        if not isinstance(self.affirmative, bool):
            raise InvalidDomainValue("affirmative must be a bool")
        if not isinstance(self.authorized_by, ActorIdentity):
            raise InvalidDomainValue("authorized_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)


@dataclass(frozen=True, slots=True)
class EffectRemediationAuthorizationSemantics:
    """Complete authorization input for an exact remedy operation or plan."""

    policy_decision: EffectRemediationAuthorizationDecision
    human_authorization: EffectRemediationHumanAuthorization | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.policy_decision, EffectRemediationAuthorizationDecision):
            raise InvalidDomainValue(
                "policy_decision must be an EffectRemediationAuthorizationDecision"
            )
        if self.human_authorization is not None and not isinstance(
            self.human_authorization, EffectRemediationHumanAuthorization
        ):
            raise InvalidDomainValue(
                "human_authorization must be an "
                "EffectRemediationHumanAuthorization or None"
            )


class EffectSimulationBypassStatus(Enum):
    """Closed decision outcome; only accepted bypasses permit the direct edge."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


class EffectSimulationBypassBasis(Enum):
    """Positive accepted basis for bypassing a simulation; absence never suffices."""

    IMPRACTICAL = "IMPRACTICAL"
    INAPPLICABLE = "INAPPLICABLE"
    OTHER_ACCEPTED_GUARD = "OTHER_ACCEPTED_GUARD"


@dataclass(frozen=True, slots=True)
class EffectSimulationBypassDecision:
    """Immutable scoped decision to bypass simulation, not lifecycle authority."""

    decision_id: EffectSimulationBypassDecisionId
    operation_scope: EffectOperationScope
    status: EffectSimulationBypassStatus
    basis: EffectSimulationBypassBasis
    justification: str
    evidence_refs: frozenset[EvidenceRef]
    decided_by: ActorIdentity
    recorded_by: ActorIdentity
    decided_at: Timestamp
    recorded_at: Timestamp

    def __post_init__(self) -> None:
        if not isinstance(self.decision_id, EffectSimulationBypassDecisionId):
            raise InvalidDomainValue(
                "decision_id must be an EffectSimulationBypassDecisionId"
            )
        if not isinstance(self.operation_scope, EffectOperationScope):
            raise InvalidDomainValue("operation_scope must be an EffectOperationScope")
        if not isinstance(self.status, EffectSimulationBypassStatus):
            raise InvalidDomainValue("status must be an EffectSimulationBypassStatus")
        if not isinstance(self.basis, EffectSimulationBypassBasis):
            raise InvalidDomainValue("basis must be an EffectSimulationBypassBasis")
        _require_text(self.justification, "justification")
        _require_evidence(self.evidence_refs)
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        if not isinstance(self.recorded_by, ActorIdentity):
            raise InvalidDomainValue("recorded_by must be an ActorIdentity")
        if not isinstance(self.decided_at, Timestamp):
            raise InvalidDomainValue("decided_at must be a Timestamp")
        if not isinstance(self.recorded_at, Timestamp):
            raise InvalidDomainValue("recorded_at must be a Timestamp")


@dataclass(frozen=True, slots=True)
class EffectSimulationSemantics:
    """Required immutable simulation provenance for `PLANNED -> SIMULATED`."""

    simulation: EffectSimulationRecord

    def __post_init__(self) -> None:
        if not isinstance(self.simulation, EffectSimulationRecord):
            raise InvalidDomainValue("simulation must be an EffectSimulationRecord")


@dataclass(frozen=True, slots=True)
class EffectPendingCommitSemantics:
    """Required pre-commit provenance; this does not authorize dispatch."""

    operation_scope: EffectOperationScope
    preparation: EffectPreparationRecord
    verification: EffectVerificationRecord
    remediation_readiness: EffectRemediationReadinessRecord
    deduplication_ref: EffectDeduplicationRef
    simulation: EffectSimulationRecord | None = None
    simulation_bypass: EffectSimulationBypassDecision | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.operation_scope, EffectOperationScope):
            raise InvalidDomainValue("operation_scope must be an EffectOperationScope")
        if not isinstance(self.preparation, EffectPreparationRecord):
            raise InvalidDomainValue("preparation must be an EffectPreparationRecord")
        if not isinstance(self.verification, EffectVerificationRecord):
            raise InvalidDomainValue("verification must be an EffectVerificationRecord")
        if not isinstance(self.remediation_readiness, EffectRemediationReadinessRecord):
            raise InvalidDomainValue(
                "remediation_readiness must be an EffectRemediationReadinessRecord"
            )
        if not isinstance(self.deduplication_ref, EffectDeduplicationRef):
            raise InvalidDomainValue(
                "deduplication_ref must be an EffectDeduplicationRef"
            )
        if self.simulation is not None and not isinstance(
            self.simulation, EffectSimulationRecord
        ):
            raise InvalidDomainValue(
                "simulation must be an EffectSimulationRecord or None"
            )
        if self.simulation_bypass is not None and not isinstance(
            self.simulation_bypass, EffectSimulationBypassDecision
        ):
            raise InvalidDomainValue(
                "simulation_bypass must be an EffectSimulationBypassDecision or None"
            )


@dataclass(frozen=True, slots=True)
class EffectConfirmedOccurrenceSemantics:
    """Exact observation provenance for a factual, non-dispatch COMMITTED edge."""

    observation_scope: EffectObservationScope
    observation: EffectObservationRecord
    authorization_finding: EffectAuthorizationFindingRecord
    governance_finding: EffectGovernanceFindingRecord | None = None
    quarantine_context: EffectQuarantineContext | None = None
    prior_observation: EffectObservationRecord | None = None
    prior_incident_record: EffectIncidentRecord | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.observation_scope, EffectObservationScope):
            raise InvalidDomainValue(
                "observation_scope must be an EffectObservationScope"
            )
        if not isinstance(self.observation, EffectObservationRecord):
            raise InvalidDomainValue("observation must be an EffectObservationRecord")
        if not isinstance(self.authorization_finding, EffectAuthorizationFindingRecord):
            raise InvalidDomainValue(
                "authorization_finding must be an EffectAuthorizationFindingRecord"
            )
        if self.governance_finding is not None and not isinstance(
            self.governance_finding, EffectGovernanceFindingRecord
        ):
            raise InvalidDomainValue(
                "governance_finding must be an EffectGovernanceFindingRecord or None"
            )
        if self.quarantine_context is not None and not isinstance(
            self.quarantine_context, EffectQuarantineContext
        ):
            raise InvalidDomainValue(
                "quarantine_context must be an EffectQuarantineContext or None"
            )
        if self.prior_observation is not None and not isinstance(
            self.prior_observation, EffectObservationRecord
        ):
            raise InvalidDomainValue(
                "prior_observation must be an EffectObservationRecord or None"
            )
        if self.prior_incident_record is not None and not isinstance(
            self.prior_incident_record, EffectIncidentRecord
        ):
            raise InvalidDomainValue(
                "prior_incident_record must be an EffectIncidentRecord or None"
            )


@dataclass(frozen=True, slots=True)
class EffectQuarantineSemantics:
    """Exact observation or remediation provenance for a QUARANTINED edge."""

    observation_scope: EffectObservationScope
    quarantine_context: EffectQuarantineContext
    observation: EffectObservationRecord | None = None
    original_commit_observation: EffectObservationRecord | None = None
    incident_record: EffectIncidentRecord | None = None
    compensation_plan: EffectCompensationPlanRecord | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.observation_scope, EffectObservationScope):
            raise InvalidDomainValue(
                "observation_scope must be an EffectObservationScope"
            )
        if not isinstance(self.quarantine_context, EffectQuarantineContext):
            raise InvalidDomainValue(
                "quarantine_context must be an EffectQuarantineContext"
            )
        if self.observation is not None and not isinstance(
            self.observation, EffectObservationRecord
        ):
            raise InvalidDomainValue(
                "observation must be an EffectObservationRecord or None"
            )
        if self.original_commit_observation is not None and not isinstance(
            self.original_commit_observation, EffectObservationRecord
        ):
            raise InvalidDomainValue(
                "original_commit_observation must be an EffectObservationRecord or None"
            )
        if self.incident_record is not None and not isinstance(
            self.incident_record, EffectIncidentRecord
        ):
            raise InvalidDomainValue(
                "incident_record must be an EffectIncidentRecord or None"
            )
        if self.compensation_plan is not None and not isinstance(
            self.compensation_plan, EffectCompensationPlanRecord
        ):
            raise InvalidDomainValue(
                "compensation_plan must be an EffectCompensationPlanRecord or None"
            )


@dataclass(frozen=True, slots=True)
class EffectRollbackSemantics:
    """Restoration evidence and exact authorization for a true rollback."""

    original_commit_observation: EffectObservationRecord
    rollback_record: EffectRollbackRecord
    authorization: EffectRemediationAuthorizationSemantics

    def __post_init__(self) -> None:
        if not isinstance(self.original_commit_observation, EffectObservationRecord):
            raise InvalidDomainValue(
                "original_commit_observation must be an EffectObservationRecord"
            )
        if not isinstance(self.rollback_record, EffectRollbackRecord):
            raise InvalidDomainValue("rollback_record must be an EffectRollbackRecord")
        if not isinstance(self.authorization, EffectRemediationAuthorizationSemantics):
            raise InvalidDomainValue(
                "authorization must be an EffectRemediationAuthorizationSemantics"
            )


@dataclass(frozen=True, slots=True)
class EffectCompensationStartSemantics:
    """Exact authorized plan for entering the COMPENSATING disposition."""

    original_commit_observation: EffectObservationRecord
    compensation_plan: EffectCompensationPlanRecord
    authorization: EffectRemediationAuthorizationSemantics

    def __post_init__(self) -> None:
        if not isinstance(self.original_commit_observation, EffectObservationRecord):
            raise InvalidDomainValue(
                "original_commit_observation must be an EffectObservationRecord"
            )
        if not isinstance(self.compensation_plan, EffectCompensationPlanRecord):
            raise InvalidDomainValue(
                "compensation_plan must be an EffectCompensationPlanRecord"
            )
        if not isinstance(self.authorization, EffectRemediationAuthorizationSemantics):
            raise InvalidDomainValue(
                "authorization must be an EffectRemediationAuthorizationSemantics"
            )


@dataclass(frozen=True, slots=True)
class EffectCompensationCompletionSemantics:
    """Independent completion evidence for the exact started compensation plan."""

    original_commit_observation: EffectObservationRecord
    compensation_plan: EffectCompensationPlanRecord
    completion_record: EffectCompensationCompletionRecord
    authorization: EffectRemediationAuthorizationSemantics

    def __post_init__(self) -> None:
        if not isinstance(self.original_commit_observation, EffectObservationRecord):
            raise InvalidDomainValue(
                "original_commit_observation must be an EffectObservationRecord"
            )
        if not isinstance(self.compensation_plan, EffectCompensationPlanRecord):
            raise InvalidDomainValue(
                "compensation_plan must be an EffectCompensationPlanRecord"
            )
        if not isinstance(self.completion_record, EffectCompensationCompletionRecord):
            raise InvalidDomainValue(
                "completion_record must be an EffectCompensationCompletionRecord"
            )
        if not isinstance(self.authorization, EffectRemediationAuthorizationSemantics):
            raise InvalidDomainValue(
                "authorization must be an EffectRemediationAuthorizationSemantics"
            )


type EffectSemanticInput = (
    EffectSimulationSemantics
    | EffectPendingCommitSemantics
    | EffectConfirmedOccurrenceSemantics
    | EffectQuarantineSemantics
    | EffectRollbackSemantics
    | EffectCompensationStartSemantics
    | EffectCompensationCompletionSemantics
)


_INPUT_TYPE_BY_EDGE: Final[
    MappingProxyType[tuple[EffectState, EffectState], type[EffectSemanticInput]]
] = MappingProxyType(
    {
        (EffectState.PLANNED, EffectState.SIMULATED): EffectSimulationSemantics,
        (EffectState.PLANNED, EffectState.PENDING_COMMIT): EffectPendingCommitSemantics,
        (
            EffectState.SIMULATED,
            EffectState.PENDING_COMMIT,
        ): EffectPendingCommitSemantics,
        (
            EffectState.PLANNED,
            EffectState.COMMITTED,
        ): EffectConfirmedOccurrenceSemantics,
        (
            EffectState.SIMULATED,
            EffectState.COMMITTED,
        ): EffectConfirmedOccurrenceSemantics,
        (
            EffectState.PENDING_COMMIT,
            EffectState.COMMITTED,
        ): EffectConfirmedOccurrenceSemantics,
        (
            EffectState.QUARANTINED,
            EffectState.COMMITTED,
        ): EffectConfirmedOccurrenceSemantics,
        (EffectState.PLANNED, EffectState.QUARANTINED): EffectQuarantineSemantics,
        (EffectState.SIMULATED, EffectState.QUARANTINED): EffectQuarantineSemantics,
        (
            EffectState.PENDING_COMMIT,
            EffectState.QUARANTINED,
        ): EffectQuarantineSemantics,
        (EffectState.COMMITTED, EffectState.QUARANTINED): EffectQuarantineSemantics,
        (
            EffectState.COMPENSATING,
            EffectState.QUARANTINED,
        ): EffectQuarantineSemantics,
        (EffectState.COMMITTED, EffectState.ROLLED_BACK): EffectRollbackSemantics,
        (
            EffectState.COMMITTED,
            EffectState.COMPENSATING,
        ): EffectCompensationStartSemantics,
        (
            EffectState.COMPENSATING,
            EffectState.COMPENSATED,
        ): EffectCompensationCompletionSemantics,
    }
)


def _scope_matches_effect(
    scope: EffectOperationScope, effect: Effect, correlation_id: CorrelationId
) -> bool:
    return (
        scope.effect_id == effect.effect_id
        and scope.observed_effect_version == effect.version
        and scope.target_ref == effect.target_ref
        and scope.payload_ref == effect.payload_ref
        and scope.correlation_id == correlation_id
    )


@dataclass(frozen=True, slots=True)
class EffectSemanticGuard:
    """Canonical semantic guard for accepted exact-bound Effect edges only."""

    effect_id: EffectId
    observed_entity_version: EntityVersion
    prior_state: EffectState
    target_state: EffectState
    target_ref: EffectTargetRef
    payload_ref: EffectPayloadRef | None
    correlation_id: CorrelationId
    semantic_input: EffectSemanticInput

    def __post_init__(self) -> None:
        if not isinstance(self.effect_id, EffectId):
            raise InvalidDomainValue("effect_id must be an EffectId")
        if not isinstance(self.observed_entity_version, EntityVersion):
            raise InvalidDomainValue("observed_entity_version must be an EntityVersion")
        if not isinstance(self.prior_state, EffectState) or not isinstance(
            self.target_state, EffectState
        ):
            raise InvalidDomainValue("prior_state and target_state must be EffectState")
        if not isinstance(self.target_ref, EffectTargetRef):
            raise InvalidDomainValue("target_ref must be an EffectTargetRef")
        if self.payload_ref is not None and not isinstance(
            self.payload_ref, EffectPayloadRef
        ):
            raise InvalidDomainValue("payload_ref must be an EffectPayloadRef or None")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        expected = _INPUT_TYPE_BY_EDGE.get((self.prior_state, self.target_state))
        if expected is None or not isinstance(self.semantic_input, expected):
            raise InvalidDomainValue(
                "semantic_input must match a canonical Effect lifecycle edge"
            )

    def validate(
        self,
        effect: Effect,
        target_state: EffectState,
        controller: ActorIdentity,
        correlation_id: CorrelationId,
    ) -> None:
        """Validate only pure exact-bound semantics for the accepted scoped edges."""
        if not isinstance(effect, Effect):
            raise InvalidDomainValue("effect must be an Effect")
        if not isinstance(target_state, EffectState):
            raise InvalidDomainValue("target_state must be an EffectState")
        if not isinstance(controller, ActorIdentity):
            raise InvalidDomainValue("controller must be an ActorIdentity")
        if not isinstance(correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if not (
            self.effect_id == effect.effect_id
            and self.observed_entity_version == effect.version
            and self.prior_state is effect.state
            and self.target_state is target_state
            and self.target_ref == effect.target_ref
            and self.payload_ref == effect.payload_ref
            and self.correlation_id == correlation_id
        ):
            raise InvariantViolation(
                "Effect semantic guard does not match the exact request snapshot"
            )
        if isinstance(self.semantic_input, EffectSimulationSemantics):
            if effect.payload_ref is None:
                raise InvariantViolation(
                    "Canonical Effect preparation requires concrete payload"
                )
            self._validate_simulation(effect, controller, correlation_id)
            return
        if isinstance(self.semantic_input, EffectPendingCommitSemantics):
            if effect.payload_ref is None:
                raise InvariantViolation(
                    "Canonical Effect preparation requires concrete payload"
                )
            self._validate_pending_commit(effect, controller, correlation_id)
            return
        if isinstance(self.semantic_input, EffectConfirmedOccurrenceSemantics):
            self._validate_confirmed_occurrence(effect, controller, correlation_id)
            return
        if isinstance(self.semantic_input, EffectRollbackSemantics):
            self._validate_rollback(effect, controller, correlation_id)
            return
        if isinstance(self.semantic_input, EffectCompensationStartSemantics):
            self._validate_compensation_start(effect, controller, correlation_id)
            return
        if isinstance(self.semantic_input, EffectCompensationCompletionSemantics):
            self._validate_compensation_completion(effect, controller, correlation_id)
            return
        self._validate_quarantine(effect, controller, correlation_id)

    def _validate_simulation(
        self,
        effect: Effect,
        controller: ActorIdentity,
        correlation_id: CorrelationId,
    ) -> None:
        semantics = self.semantic_input
        assert isinstance(semantics, EffectSimulationSemantics)
        simulation = semantics.simulation
        if not _scope_matches_effect(
            simulation.operation_scope, effect, correlation_id
        ):
            raise InvariantViolation(
                "Simulation provenance does not match exact Effect intent"
            )
        if simulation.simulated_by.actor_id == controller.actor_id:
            raise InvariantViolation(
                "Simulation preparer must be separate from Effect controller"
            )

    def _validate_pending_commit(
        self, effect: Effect, controller: ActorIdentity, correlation_id: CorrelationId
    ) -> None:
        semantics = self.semantic_input
        assert isinstance(semantics, EffectPendingCommitSemantics)
        if not _scope_matches_effect(semantics.operation_scope, effect, correlation_id):
            raise InvariantViolation(
                "Operation scope does not match exact Effect intent"
            )
        if not can_attach_effect_preparation_record(effect, semantics.preparation):
            raise InvariantViolation(
                "Preparation does not match the exact Effect snapshot"
            )
        if semantics.preparation.correlation_id != correlation_id:
            raise InvariantViolation(
                "Preparation does not match transition correlation"
            )
        if not can_verify_effect_preparation(
            semantics.preparation, semantics.verification
        ):
            raise InvariantViolation("Verification does not match the preparation")
        if semantics.verification.verified_by.actor_type is not ActorType.EVALUATOR:
            raise InvariantViolation("Independent verification requires an EVALUATOR")
        if (
            isinstance(effect.origin, PlannedEffectOrigin)
            and semantics.verification.verified_by.actor_id
            == effect.origin.proposed_by.actor_id
        ):
            raise InvariantViolation(
                "Verifier must be distinct from the planned Effect producing principal"
            )
        separated_ids = {
            semantics.preparation.prepared_by.actor_id,
            semantics.verification.verified_by.actor_id,
            controller.actor_id,
        }
        if len(separated_ids) != 3:
            raise InvariantViolation(
                "Preparer, verifier, and Effect controller must be distinct principals"
            )
        if not _scope_matches_effect(
            semantics.remediation_readiness.operation_scope, effect, correlation_id
        ):
            raise InvariantViolation(
                "Remediation readiness does not match exact Effect intent"
            )
        if effect.state is EffectState.SIMULATED:
            simulation = semantics.simulation
            if simulation is None:
                raise InvariantViolation(
                    "SIMULATED Effect requires simulation provenance"
                )
            if not _scope_matches_effect(
                simulation.operation_scope, effect, correlation_id
            ):
                raise InvariantViolation(
                    "Simulation provenance does not match exact Effect intent"
                )
            if simulation.simulated_by.actor_id == controller.actor_id:
                raise InvariantViolation(
                    "Simulation preparer must be separate from Effect controller"
                )
            if semantics.simulation_bypass is not None:
                raise InvariantViolation(
                    "SIMULATED Effect must not carry bypass provenance"
                )
        else:
            bypass = semantics.simulation_bypass
            if bypass is None:
                raise InvariantViolation(
                    "PLANNED Effect requires explicit simulation bypass"
                )
            if bypass.status is not EffectSimulationBypassStatus.ACCEPTED:
                raise InvariantViolation("Simulation bypass is not accepted")
            if not _scope_matches_effect(
                bypass.operation_scope, effect, correlation_id
            ):
                raise InvariantViolation(
                    "Simulation bypass does not match exact Effect intent"
                )
            if bypass.decided_by.actor_type is ActorType.WORKER:
                raise InvariantViolation("Worker cannot decide simulation bypass")
            if bypass.decided_by.actor_id in separated_ids:
                raise InvariantViolation(
                    "Bypass decision maker must be separate from preparer, verifier, "
                    "and Effect controller"
                )

    def _validate_original_commit_observation(
        self,
        effect: Effect,
        observation: EffectObservationRecord,
        expected_observation_id: EffectObservationId,
    ) -> None:
        if not (
            observation.observation_id == expected_observation_id
            and observation.effect_id == effect.effect_id
            and observation.occurrence_status is EffectOccurrenceStatus.CONFIRMED
            and observation.occurrence_at is not None
            and observation.target_ref == effect.target_ref
            and (
                effect.payload_ref is None
                or observation.payload_ref is None
                or observation.payload_ref == effect.payload_ref
            )
            and observation.observed_effect_version.value <= effect.version.value
        ):
            raise InvariantViolation(
                "Original commit observation is not compatible historical provenance"
            )
        if (
            isinstance(effect.origin, ObservedEffectOrigin)
            and observation.external_operation_ref
            != effect.origin.external_operation_ref
        ):
            raise InvariantViolation(
                "Original commit observation does not match observed Effect origin"
            )
        if observation.observed_by.actor_type is ActorType.WORKER:
            raise InvariantViolation(
                "Worker-only observation cannot establish original commit"
            )

    def _validate_remediation_authorization(
        self,
        authorization: EffectRemediationAuthorizationSemantics,
        expected_scope: EffectRemediationAuthorizationScope,
        controller: ActorIdentity,
    ) -> None:
        policy = authorization.policy_decision
        if not (
            policy.status is EffectRemediationAuthorizationStatus.AUTHORIZED
            and policy.decided_by.actor_type is ActorType.POLICY_ENGINE
            and policy.scope == expected_scope
            and policy.decided_by.actor_id != controller.actor_id
        ):
            raise InvariantViolation(
                "Remediation policy authorization is not exact, authorized, and "
                "independent"
            )
        human = authorization.human_authorization
        if policy.human_authorization_required and human is None:
            raise InvariantViolation(
                "Required human remediation authorization is missing"
            )
        if human is None:
            return
        if not (
            human.affirmative
            and human.authorized_by.actor_type is ActorType.HUMAN_OPERATOR
            and human.scope == expected_scope
            and human.policy_decision_ref == policy.decision_ref
            and human.authorized_by.actor_id != controller.actor_id
            and human.authorized_by.actor_id != policy.decided_by.actor_id
        ):
            raise InvariantViolation(
                "Human remediation authorization is not affirmative, exact, and "
                "independent"
            )

    def _require_independent_remediation_verifier(
        self,
        verifier: ActorIdentity,
        effect: Effect,
        controller: ActorIdentity,
        authorization: EffectRemediationAuthorizationSemantics,
        *additional_principals: ActorIdentity,
    ) -> None:
        policy = authorization.policy_decision
        human = authorization.human_authorization
        excluded_actor_ids = {
            controller.actor_id,
            policy.decided_by.actor_id,
            *(principal.actor_id for principal in additional_principals),
        }
        if human is not None:
            excluded_actor_ids.add(human.authorized_by.actor_id)
        if isinstance(effect.origin, PlannedEffectOrigin):
            excluded_actor_ids.add(effect.origin.proposed_by.actor_id)
        if (
            verifier.actor_type is not ActorType.EVALUATOR
            or verifier.actor_id in excluded_actor_ids
        ):
            raise InvariantViolation(
                "Remediation verification requires an independent EVALUATOR principal"
            )

    def _validate_rollback(
        self,
        effect: Effect,
        controller: ActorIdentity,
        correlation_id: CorrelationId,
    ) -> None:
        semantics = self.semantic_input
        assert isinstance(semantics, EffectRollbackSemantics)
        rollback = semantics.rollback_record
        if not (
            can_attach_effect_rollback_record(effect, rollback)
            and rollback.correlation_id == correlation_id
            and rollback.recorded_by.actor_id == controller.actor_id
        ):
            raise InvariantViolation(
                "Rollback record does not match the exact Effect restoration attempt"
            )
        self._validate_original_commit_observation(
            effect,
            semantics.original_commit_observation,
            rollback.original_commit_observation_id,
        )
        expected_scope = EffectRemediationAuthorizationScope(
            effect_id=effect.effect_id,
            authorized_effect_version=effect.version,
            original_commit_observation_id=rollback.original_commit_observation_id,
            remediation_kind=EffectRemediationKind.ROLLBACK,
            correlation_id=correlation_id,
            restoration_operation_ref=rollback.restoration_operation_ref,
        )
        self._validate_remediation_authorization(
            semantics.authorization, expected_scope, controller
        )
        self._require_independent_remediation_verifier(
            rollback.verified_by, effect, controller, semantics.authorization
        )

    def _validate_compensation_plan(
        self,
        effect: Effect,
        plan: EffectCompensationPlanRecord,
        original_commit_observation: EffectObservationRecord,
        correlation_id: CorrelationId,
    ) -> EffectRemediationAuthorizationScope:
        if not (
            plan.effect_id == effect.effect_id
            and plan.correlation_id == correlation_id
            and plan.original_commit_observation_id
            == original_commit_observation.observation_id
        ):
            raise InvariantViolation(
                "Compensation plan does not match the exact Effect and correlation"
            )
        self._validate_original_commit_observation(
            effect,
            original_commit_observation,
            plan.original_commit_observation_id,
        )
        return EffectRemediationAuthorizationScope(
            effect_id=effect.effect_id,
            authorized_effect_version=plan.observed_effect_version,
            original_commit_observation_id=plan.original_commit_observation_id,
            remediation_kind=EffectRemediationKind.COMPENSATION,
            correlation_id=correlation_id,
            compensation_plan_id=plan.plan_id,
            compensating_effect_ids=plan.compensating_effect_ids,
        )

    def _validate_compensation_start(
        self,
        effect: Effect,
        controller: ActorIdentity,
        correlation_id: CorrelationId,
    ) -> None:
        semantics = self.semantic_input
        assert isinstance(semantics, EffectCompensationStartSemantics)
        plan = semantics.compensation_plan
        if not (
            plan.observed_effect_version == effect.version
            and plan.recorded_by.actor_id == controller.actor_id
        ):
            raise InvariantViolation(
                "Compensation plan does not match the exact COMMITTED snapshot"
            )
        expected_scope = self._validate_compensation_plan(
            effect, plan, semantics.original_commit_observation, correlation_id
        )
        self._validate_remediation_authorization(
            semantics.authorization, expected_scope, controller
        )
        authorization_principals = {
            semantics.authorization.policy_decision.decided_by.actor_id,
            controller.actor_id,
        }
        human = semantics.authorization.human_authorization
        if human is not None:
            authorization_principals.add(human.authorized_by.actor_id)
        if plan.planned_by.actor_id in authorization_principals:
            raise InvariantViolation(
                "Compensation planner must be separate from authorizers and controller"
            )

    def _validate_compensation_completion(
        self,
        effect: Effect,
        controller: ActorIdentity,
        correlation_id: CorrelationId,
    ) -> None:
        semantics = self.semantic_input
        assert isinstance(semantics, EffectCompensationCompletionSemantics)
        plan = semantics.compensation_plan
        completion = semantics.completion_record
        if plan.observed_effect_version.next() != effect.version:
            raise InvariantViolation(
                "Compensation plan does not establish the current COMPENSATING version"
            )
        expected_scope = self._validate_compensation_plan(
            effect, plan, semantics.original_commit_observation, correlation_id
        )
        self._validate_remediation_authorization(
            semantics.authorization, expected_scope, controller
        )
        if not (
            can_complete_effect_compensation_plan(plan, completion)
            and completion.observed_effect_version == effect.version
            and completion.original_commit_observation_id
            == semantics.original_commit_observation.observation_id
            and completion.correlation_id == correlation_id
            and completion.recorded_by.actor_id == controller.actor_id
        ):
            raise InvariantViolation(
                "Compensation completion does not exact-bind the current plan attempt"
            )
        self._require_independent_remediation_verifier(
            completion.verified_by,
            effect,
            controller,
            semantics.authorization,
            plan.planned_by,
        )

    @staticmethod
    def _compensating_effect_ids_annotation(
        plan: EffectCompensationPlanRecord,
    ) -> str:
        return ",".join(
            sorted(str(effect_id.value) for effect_id in plan.compensating_effect_ids)
        )

    def compensation_start_annotations(
        self, start_event_id: EventId
    ) -> frozenset[tuple[str, str]]:
        """Return exact stable lineage shared by start and completion events."""
        if not isinstance(start_event_id, EventId):
            raise InvalidDomainValue("start_event_id must be an EventId")
        semantics = self.semantic_input
        if isinstance(semantics, EffectCompensationStartSemantics):
            plan = semantics.compensation_plan
            authorization = semantics.authorization
        elif isinstance(semantics, EffectCompensationCompletionSemantics):
            plan = semantics.compensation_plan
            authorization = semantics.authorization
        else:
            raise InvalidDomainValue(
                "Compensation start annotations require compensation semantics"
            )
        return frozenset(
            {
                ("compensation_start_event_id", str(start_event_id.value)),
                ("compensation_plan_id", str(plan.plan_id.value)),
                (
                    "compensating_effect_ids",
                    self._compensating_effect_ids_annotation(plan),
                ),
                (
                    "original_commit_observation_id",
                    str(plan.original_commit_observation_id.value),
                ),
                (
                    "remediation_authorization_ref",
                    authorization.policy_decision.decision_ref.value,
                ),
            }
        )

    def remediation_event_annotations(
        self, compensation_start_event_id: EventId | None = None
    ) -> frozenset[tuple[str, str]]:
        """Return narrow remediation provenance for the lifecycle event."""
        semantics = self.semantic_input
        if isinstance(semantics, EffectRollbackSemantics):
            return frozenset(
                {
                    (
                        "rollback_record_id",
                        str(semantics.rollback_record.rollback_record_id.value),
                    ),
                    (
                        "original_commit_observation_id",
                        str(semantics.original_commit_observation.observation_id.value),
                    ),
                    (
                        "remediation_authorization_ref",
                        semantics.authorization.policy_decision.decision_ref.value,
                    ),
                }
            )
        if compensation_start_event_id is None:
            raise InvalidDomainValue(
                "Compensation event annotations require start event identity"
            )
        annotations = self.compensation_start_annotations(compensation_start_event_id)
        if isinstance(semantics, EffectCompensationStartSemantics):
            return annotations
        if isinstance(semantics, EffectCompensationCompletionSemantics):
            return annotations | frozenset(
                {
                    (
                        "compensation_completion_id",
                        str(semantics.completion_record.completion_id.value),
                    )
                }
            )
        raise InvalidDomainValue(
            "Remediation annotations require rollback or compensation semantics"
        )

    def validated_completion_verifier(self) -> ActorIdentity:
        """Expose the already-validated completion verifier for lineage checks."""
        semantics = self.semantic_input
        if not isinstance(semantics, EffectCompensationCompletionSemantics):
            raise InvalidDomainValue(
                "Completion verifier requires compensation-completion semantics"
            )
        return semantics.completion_record.verified_by

    def _validate_observation_scope(
        self,
        effect: Effect,
        target_state: EffectState,
        scope: EffectObservationScope,
        correlation_id: CorrelationId,
    ) -> None:
        if not (
            scope.effect_id == effect.effect_id
            and scope.observed_effect_version == effect.version
            and scope.source_state is effect.state
            and scope.target_state is target_state
            and scope.target_ref == effect.target_ref
            and scope.correlation_id == correlation_id
        ):
            raise InvariantViolation(
                "Observation scope does not match the exact Effect transition snapshot"
            )

    def _validate_observation(
        self,
        effect: Effect,
        controller: ActorIdentity,
        scope: EffectObservationScope,
        observation: EffectObservationRecord,
    ) -> None:
        if not can_attach_effect_observation(effect, observation):
            raise InvariantViolation(
                "Observation does not match the exact Effect snapshot"
            )
        if not (
            observation.external_operation_ref == scope.external_operation_ref
            and observation.deduplication_ref == scope.deduplication_ref
            and observation.correlation_id == scope.correlation_id
        ):
            raise InvariantViolation(
                "Observation does not match external-operation, deduplication, or "
                "correlation scope"
            )
        if observation.recorded_by.actor_id != controller.actor_id:
            raise InvariantViolation(
                "Observation must be recorded by the authoritative Effect controller"
            )

    def _validate_confirmed_occurrence(
        self, effect: Effect, controller: ActorIdentity, correlation_id: CorrelationId
    ) -> None:
        semantics = self.semantic_input
        assert isinstance(semantics, EffectConfirmedOccurrenceSemantics)
        self._validate_observation_scope(
            effect, EffectState.COMMITTED, semantics.observation_scope, correlation_id
        )
        self._validate_observation(
            effect, controller, semantics.observation_scope, semantics.observation
        )
        observation = semantics.observation
        if observation.occurrence_status is not EffectOccurrenceStatus.CONFIRMED:
            raise InvariantViolation(
                "COMMITTED requires a CONFIRMED occurrence observation"
            )
        if observation.occurrence_at is None:
            raise InvariantViolation("Confirmed occurrence requires occurrence_at")
        if observation.observed_by.actor_type is ActorType.WORKER:
            raise InvariantViolation(
                "Worker-only observation cannot confirm occurrence"
            )
        if (
            isinstance(effect.origin, PlannedEffectOrigin)
            and observation.observed_by.actor_id == effect.origin.proposed_by.actor_id
        ):
            raise InvariantViolation(
                "Planned Effect producing principal cannot independently confirm "
                "occurrence"
            )
        if (
            not can_attach_effect_authorization_finding(
                effect, semantics.authorization_finding
            )
            or semantics.authorization_finding.correlation_id != correlation_id
        ):
            raise InvariantViolation(
                "Authorization finding does not match the exact observation context"
            )
        if semantics.governance_finding is not None and (
            not can_attach_effect_governance_finding(
                effect, semantics.governance_finding
            )
            or semantics.governance_finding.correlation_id != correlation_id
        ):
            raise InvariantViolation(
                "Governance finding does not match the exact observation context"
            )
        if effect.state is not EffectState.QUARANTINED:
            if semantics.quarantine_context is not None:
                raise InvariantViolation(
                    "Only QUARANTINED reconciliation may carry quarantine context"
                )
            return
        context = semantics.quarantine_context
        if context is None:
            if isinstance(effect.origin, ObservedEffectOrigin):
                return
            raise InvariantViolation(
                "QUARANTINED reconciliation requires quarantine context"
            )
        self._validate_reconciliation_context(
            effect, semantics.observation_scope, context, semantics
        )

    def _validate_reconciliation_context(
        self,
        effect: Effect,
        scope: EffectObservationScope,
        context: EffectQuarantineContext,
        semantics: EffectConfirmedOccurrenceSemantics,
    ) -> None:
        context_scope = context.observation_scope
        if not (
            context_scope.effect_id == effect.effect_id
            and context_scope.target_ref == scope.target_ref
            and context_scope.external_operation_ref == scope.external_operation_ref
            and context_scope.deduplication_ref == scope.deduplication_ref
            and context_scope.correlation_id == scope.correlation_id
            and context_scope.observed_effect_version.value < effect.version.value
            and context_scope.source_state is not EffectState.QUARANTINED
        ):
            raise InvariantViolation(
                "Quarantine context does not preserve compatible historical entry "
                "provenance"
            )
        if context.reason is EffectQuarantineReason.UNKNOWN_OR_SUSPECTED_OCCURRENCE:
            prior = semantics.prior_observation
            if (
                prior is None
                or context.prior_observation_id != prior.observation_id
                or prior.occurrence_status is not EffectOccurrenceStatus.UNCERTAIN
                or context_scope.source_state
                not in {
                    EffectState.PLANNED,
                    EffectState.SIMULATED,
                    EffectState.PENDING_COMMIT,
                }
                or context_scope.observed_effect_version
                != prior.observed_effect_version
                or not self._is_compatible_historical_observation(effect, scope, prior)
                or not can_follow_effect_observation(prior, semantics.observation)
            ):
                raise InvariantViolation(
                    "Uncertain quarantine reconciliation requires compatible prior "
                    "observation"
                )
        elif (
            context.original_commit_observation_id is None
            or (
                context.reason is EffectQuarantineReason.POST_COMMIT_PROBLEM
                and context_scope.source_state is not EffectState.COMMITTED
            )
            or (
                context.reason
                is EffectQuarantineReason.COMPENSATION_OR_REMEDIATION_UNCERTAINTY
                and context_scope.source_state is not EffectState.COMPENSATING
            )
        ):
            raise InvariantViolation(
                "Post-commit reconciliation requires original commit observation "
                "context"
            )
        if semantics.prior_incident_record is not None and (
            context.incident_record_id != semantics.prior_incident_record.record_id
            or not can_attach_effect_incident_record(
                effect, semantics.prior_incident_record
            )
            or semantics.prior_incident_record.correlation_id != scope.correlation_id
        ):
            raise InvariantViolation(
                "Prior incident record does not match quarantine reconciliation context"
            )

    def _is_compatible_historical_observation(
        self,
        effect: Effect,
        scope: EffectObservationScope,
        observation: EffectObservationRecord,
    ) -> bool:
        """Bind immutable historical evidence without requiring current version."""
        return (
            observation.effect_id == effect.effect_id
            and observation.target_ref == effect.target_ref
            and (
                effect.payload_ref is None
                or observation.payload_ref is None
                or observation.payload_ref == effect.payload_ref
            )
            and observation.external_operation_ref == scope.external_operation_ref
            and observation.deduplication_ref == scope.deduplication_ref
            and observation.correlation_id == scope.correlation_id
            and observation.observed_effect_version.value <= effect.version.value
        )

    def _validate_quarantine(
        self, effect: Effect, controller: ActorIdentity, correlation_id: CorrelationId
    ) -> None:
        semantics = self.semantic_input
        assert isinstance(semantics, EffectQuarantineSemantics)
        self._validate_observation_scope(
            effect, EffectState.QUARANTINED, semantics.observation_scope, correlation_id
        )
        context = semantics.quarantine_context
        if context.observation_scope != semantics.observation_scope:
            raise InvariantViolation(
                "Quarantine context does not match exact transition observation scope"
            )
        if context.recorded_by.actor_id != controller.actor_id:
            raise InvariantViolation(
                "Quarantine context must be recorded by the authoritative Effect "
                "controller"
            )
        if effect.state in {
            EffectState.PLANNED,
            EffectState.SIMULATED,
            EffectState.PENDING_COMMIT,
        }:
            self._validate_pre_commit_quarantine(effect, controller, semantics)
            return
        self._validate_post_commit_quarantine(effect, semantics)

    def _validate_pre_commit_quarantine(
        self,
        effect: Effect,
        controller: ActorIdentity,
        semantics: EffectQuarantineSemantics,
    ) -> None:
        observation = semantics.observation
        context = semantics.quarantine_context
        if observation is None:
            raise InvariantViolation(
                "Pre-commit quarantine requires uncertainty observation"
            )
        self._validate_observation(
            effect, controller, semantics.observation_scope, observation
        )
        if observation.occurrence_status is not EffectOccurrenceStatus.UNCERTAIN:
            raise InvariantViolation(
                "Pre-commit quarantine requires UNCERTAIN occurrence"
            )
        if observation.occurrence_at is not None:
            raise InvariantViolation(
                "Uncertain occurrence must not invent occurrence_at"
            )
        if context.reason is not EffectQuarantineReason.UNKNOWN_OR_SUSPECTED_OCCURRENCE:
            raise InvariantViolation(
                "Pre-commit quarantine requires unknown or suspected occurrence context"
            )
        if context.prior_observation_id != observation.observation_id:
            raise InvariantViolation(
                "Pre-commit quarantine context must retain uncertainty observation "
                "identity"
            )
        self._validate_optional_incident(effect, semantics, context)
        if (
            semantics.original_commit_observation is not None
            or semantics.compensation_plan is not None
        ):
            raise InvariantViolation(
                "Pre-commit quarantine must not fabricate commit or compensation "
                "context"
            )

    def _validate_post_commit_quarantine(
        self, effect: Effect, semantics: EffectQuarantineSemantics
    ) -> None:
        context = semantics.quarantine_context
        original = semantics.original_commit_observation
        if (
            original is None
            or original.occurrence_status is not EffectOccurrenceStatus.CONFIRMED
        ):
            raise InvariantViolation(
                "Post-commit quarantine requires confirmed original commit observation"
            )
        if original.occurrence_at is None:
            raise InvariantViolation(
                "Original commit observation requires occurrence_at"
            )
        if not (
            self._is_compatible_historical_observation(
                effect, semantics.observation_scope, original
            )
            and context.original_commit_observation_id == original.observation_id
        ):
            raise InvariantViolation(
                "Original commit observation does not match quarantine context"
            )
        self._validate_optional_incident(effect, semantics, context)
        if effect.state is EffectState.COMMITTED:
            if context.reason is not EffectQuarantineReason.POST_COMMIT_PROBLEM:
                raise InvariantViolation(
                    "COMMITTED quarantine requires post-commit problem context"
                )
            if semantics.compensation_plan is not None:
                raise InvariantViolation(
                    "COMMITTED quarantine must not claim compensation context"
                )
            return
        if (
            context.reason
            is not EffectQuarantineReason.COMPENSATION_OR_REMEDIATION_UNCERTAINTY
        ):
            raise InvariantViolation(
                "COMPENSATING quarantine requires compensation uncertainty context"
            )
        plan = semantics.compensation_plan
        if (
            plan is None
            or context.compensation_plan_id != plan.plan_id
            or plan.effect_id != effect.effect_id
            or plan.original_commit_observation_id != original.observation_id
        ):
            raise InvariantViolation(
                "COMPENSATING quarantine requires matching compensation plan context"
            )
        if semantics.observation is not None:
            raise InvariantViolation(
                "Post-commit quarantine does not replace known occurrence with "
                "observation"
            )

    def _validate_optional_incident(
        self,
        effect: Effect,
        semantics: EffectQuarantineSemantics,
        context: EffectQuarantineContext,
    ) -> None:
        record = semantics.incident_record
        if record is None:
            if context.incident_record_id is not None:
                raise InvariantViolation(
                    "Quarantine context incident identity requires supplied incident "
                    "record"
                )
            return
        if (
            context.incident_record_id != record.record_id
            or not can_attach_effect_incident_record(effect, record)
            or record.correlation_id != semantics.observation_scope.correlation_id
        ):
            raise InvariantViolation(
                "Incident record does not match exact quarantine context"
            )
