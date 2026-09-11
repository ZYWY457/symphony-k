"""Canonical pure semantic guards for the first three Effect preparation edges.

These types represent immutable supporting provenance for the exact Effect
attempt. They do not load records, run validators, authorize dispatch, create
observations, or cause an external action.
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
    EffectPayloadRef,
    EffectState,
    EffectTargetRef,
    PlannedEffectOrigin,
)
from .effect_execution import (
    EffectPreparationRecord,
    EffectVerificationRecord,
    can_attach_effect_preparation_record,
    can_verify_effect_preparation,
)
from .errors import InvalidDomainValue, InvariantViolation
from .ids import (
    CorrelationId,
    EffectId,
    EffectRemediationReadinessId,
    EffectSimulationBypassDecisionId,
    EffectSimulationRecordId,
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


type EffectSemanticInput = EffectSimulationSemantics | EffectPendingCommitSemantics


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
    """Canonical semantic guard for exactly three exact-bound Effect edges."""

    effect_id: EffectId
    observed_entity_version: EntityVersion
    prior_state: EffectState
    target_state: EffectState
    target_ref: EffectTargetRef
    payload_ref: EffectPayloadRef
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
        if not isinstance(self.payload_ref, EffectPayloadRef):
            raise InvalidDomainValue("payload_ref must be an EffectPayloadRef")
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
        if effect.payload_ref is None:
            raise InvariantViolation(
                "Canonical Effect preparation requires concrete payload"
            )
        if isinstance(self.semantic_input, EffectSimulationSemantics):
            self._validate_simulation(effect, controller, correlation_id)
            return
        self._validate_pending_commit(effect, controller, correlation_id)

    def _validate_simulation(
        self,
        effect: Effect,
        controller: ActorIdentity,
        correlation_id: CorrelationId,
    ) -> None:
        simulation = self.semantic_input.simulation
        assert isinstance(simulation, EffectSimulationRecord)
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
