"""Canonical typed semantic guards for selected Evaluation lifecycle edges."""

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Final

from .actors import ActorIdentity, ActorType
from .candidate_refs import EvidenceRef
from .errors import InvalidDomainValue, InvariantViolation
from .evaluation import Evaluation, EvaluationState
from .evaluation_invalidation import (
    EvaluationInvalidationRecord,
    can_invalidate_evaluation,
)
from .evaluation_result import EvaluationMethodRef, EvaluationResult
from .evaluation_target import EvaluationTargetRef
from .ids import CorrelationId, EvaluationId
from .version import EntityVersion


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InvalidDomainValue(f"{field} must contain non-whitespace text")


def _require_evidence(evidence_refs: frozenset[EvidenceRef]) -> None:
    if not isinstance(evidence_refs, frozenset) or not evidence_refs:
        raise InvalidDomainValue("evidence_refs must be a nonempty frozenset")
    if any(not isinstance(reference, EvidenceRef) for reference in evidence_refs):
        raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")


def _require_snapshot_scope(
    evaluation_id: EvaluationId,
    observed_entity_version: EntityVersion,
    correlation_id: CorrelationId,
) -> None:
    if not isinstance(evaluation_id, EvaluationId):
        raise InvalidDomainValue("evaluation_id must be an EvaluationId")
    if not isinstance(observed_entity_version, EntityVersion):
        raise InvalidDomainValue("observed_entity_version must be an EntityVersion")
    if not isinstance(correlation_id, CorrelationId):
        raise InvalidDomainValue("correlation_id must be a CorrelationId")


class EvaluationSemanticDecisionStatus(Enum):
    """Closed positive/negative status for evidence-backed semantic decisions."""

    PASSED = "PASSED"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class EvaluationSemanticDecisionRef:
    """Opaque immutable identity for one independently recorded semantic decision."""

    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, "value")


@dataclass(frozen=True, slots=True)
class EvaluationVerifierIndependenceDecision:
    """Evidence-backed independence decision for one exact Evaluation start."""

    decision_ref: EvaluationSemanticDecisionRef
    status: EvaluationSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    evaluation_id: EvaluationId
    observed_entity_version: EntityVersion
    target: EvaluationTargetRef
    method: EvaluationMethodRef
    assigned_verifier: ActorIdentity
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, EvaluationSemanticDecisionRef):
            raise InvalidDomainValue(
                "decision_ref must be an EvaluationSemanticDecisionRef"
            )
        if not isinstance(self.status, EvaluationSemanticDecisionStatus):
            raise InvalidDomainValue(
                "status must be an EvaluationSemanticDecisionStatus"
            )
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)
        _require_snapshot_scope(
            self.evaluation_id, self.observed_entity_version, self.correlation_id
        )
        if not isinstance(self.target, EvaluationTargetRef):
            raise InvalidDomainValue("target must be an EvaluationTargetRef")
        if not isinstance(self.method, EvaluationMethodRef):
            raise InvalidDomainValue("method must be an EvaluationMethodRef")
        if not isinstance(self.assigned_verifier, ActorIdentity):
            raise InvalidDomainValue("assigned_verifier must be an ActorIdentity")


@dataclass(frozen=True, slots=True)
class EvaluationInputReadinessDecision:
    """Evidence-backed anchored-input decision for one exact Evaluation start."""

    decision_ref: EvaluationSemanticDecisionRef
    status: EvaluationSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    evaluation_id: EvaluationId
    observed_entity_version: EntityVersion
    target: EvaluationTargetRef
    method: EvaluationMethodRef
    assigned_verifier: ActorIdentity
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, EvaluationSemanticDecisionRef):
            raise InvalidDomainValue(
                "decision_ref must be an EvaluationSemanticDecisionRef"
            )
        if not isinstance(self.status, EvaluationSemanticDecisionStatus):
            raise InvalidDomainValue(
                "status must be an EvaluationSemanticDecisionStatus"
            )
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)
        _require_snapshot_scope(
            self.evaluation_id, self.observed_entity_version, self.correlation_id
        )
        if not isinstance(self.target, EvaluationTargetRef):
            raise InvalidDomainValue("target must be an EvaluationTargetRef")
        if not isinstance(self.method, EvaluationMethodRef):
            raise InvalidDomainValue("method must be an EvaluationMethodRef")
        if not isinstance(self.assigned_verifier, ActorIdentity):
            raise InvalidDomainValue("assigned_verifier must be an ActorIdentity")


@dataclass(frozen=True, slots=True)
class EvaluationCompletionDecision:
    """Evidence-backed provenance for appending one exact original result."""

    decision_ref: EvaluationSemanticDecisionRef
    status: EvaluationSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    evaluation_id: EvaluationId
    observed_entity_version: EntityVersion
    target: EvaluationTargetRef
    method: EvaluationMethodRef
    verifier: ActorIdentity
    result: EvaluationResult
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, EvaluationSemanticDecisionRef):
            raise InvalidDomainValue(
                "decision_ref must be an EvaluationSemanticDecisionRef"
            )
        if not isinstance(self.status, EvaluationSemanticDecisionStatus):
            raise InvalidDomainValue(
                "status must be an EvaluationSemanticDecisionStatus"
            )
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)
        _require_snapshot_scope(
            self.evaluation_id, self.observed_entity_version, self.correlation_id
        )
        if not isinstance(self.target, EvaluationTargetRef):
            raise InvalidDomainValue("target must be an EvaluationTargetRef")
        if not isinstance(self.method, EvaluationMethodRef):
            raise InvalidDomainValue("method must be an EvaluationMethodRef")
        if not isinstance(self.verifier, ActorIdentity):
            raise InvalidDomainValue("verifier must be an ActorIdentity")
        if not isinstance(self.result, EvaluationResult):
            raise InvalidDomainValue("result must be an EvaluationResult")


@dataclass(frozen=True, slots=True)
class EvaluationConflictClearanceDecision:
    """Evidence-backed no-unresolved-conflict decision for an exact result."""

    decision_ref: EvaluationSemanticDecisionRef
    status: EvaluationSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    evaluation_id: EvaluationId
    observed_entity_version: EntityVersion
    target: EvaluationTargetRef
    method: EvaluationMethodRef
    verifier: ActorIdentity
    result: EvaluationResult
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, EvaluationSemanticDecisionRef):
            raise InvalidDomainValue(
                "decision_ref must be an EvaluationSemanticDecisionRef"
            )
        if not isinstance(self.status, EvaluationSemanticDecisionStatus):
            raise InvalidDomainValue(
                "status must be an EvaluationSemanticDecisionStatus"
            )
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)
        _require_snapshot_scope(
            self.evaluation_id, self.observed_entity_version, self.correlation_id
        )
        if not isinstance(self.target, EvaluationTargetRef):
            raise InvalidDomainValue("target must be an EvaluationTargetRef")
        if not isinstance(self.method, EvaluationMethodRef):
            raise InvalidDomainValue("method must be an EvaluationMethodRef")
        if not isinstance(self.verifier, ActorIdentity):
            raise InvalidDomainValue("verifier must be an ActorIdentity")
        if not isinstance(self.result, EvaluationResult):
            raise InvalidDomainValue("result must be an EvaluationResult")


@dataclass(frozen=True, slots=True)
class EvaluationStartSemantics:
    """Canonical input for PENDING -> RUNNING only."""

    assigned_verifier: ActorIdentity
    independence: EvaluationVerifierIndependenceDecision
    input_readiness: EvaluationInputReadinessDecision

    def __post_init__(self) -> None:
        if not isinstance(self.assigned_verifier, ActorIdentity):
            raise InvalidDomainValue("assigned_verifier must be an ActorIdentity")
        if not isinstance(self.independence, EvaluationVerifierIndependenceDecision):
            raise InvalidDomainValue(
                "independence must be an EvaluationVerifierIndependenceDecision"
            )
        if not isinstance(self.input_readiness, EvaluationInputReadinessDecision):
            raise InvalidDomainValue(
                "input_readiness must be an EvaluationInputReadinessDecision"
            )


@dataclass(frozen=True, slots=True)
class EvaluationCompletionSemantics:
    """Canonical input for RUNNING -> COMPLETED only."""

    intended_result: EvaluationResult
    completion: EvaluationCompletionDecision
    conflict_clearance: EvaluationConflictClearanceDecision

    def __post_init__(self) -> None:
        if not isinstance(self.intended_result, EvaluationResult):
            raise InvalidDomainValue("intended_result must be an EvaluationResult")
        if not isinstance(self.completion, EvaluationCompletionDecision):
            raise InvalidDomainValue(
                "completion must be an EvaluationCompletionDecision"
            )
        if not isinstance(self.conflict_clearance, EvaluationConflictClearanceDecision):
            raise InvalidDomainValue(
                "conflict_clearance must be an EvaluationConflictClearanceDecision"
            )


@dataclass(frozen=True, slots=True)
class EvaluationInvalidationSemantics:
    """Canonical input for the four existing Evaluation invalidation edges."""

    invalidation: EvaluationInvalidationRecord

    def __post_init__(self) -> None:
        if not isinstance(self.invalidation, EvaluationInvalidationRecord):
            raise InvalidDomainValue(
                "invalidation must be an EvaluationInvalidationRecord"
            )


type EvaluationSemanticInput = (
    EvaluationStartSemantics
    | EvaluationCompletionSemantics
    | EvaluationInvalidationSemantics
)

_INPUT_TYPE_BY_EDGE: Final[
    MappingProxyType[
        tuple[EvaluationState, EvaluationState], type[EvaluationSemanticInput]
    ]
] = MappingProxyType(
    {
        (EvaluationState.PENDING, EvaluationState.RUNNING): EvaluationStartSemantics,
        (
            EvaluationState.RUNNING,
            EvaluationState.COMPLETED,
        ): EvaluationCompletionSemantics,
        (
            EvaluationState.PENDING,
            EvaluationState.INVALID,
        ): EvaluationInvalidationSemantics,
        (
            EvaluationState.RUNNING,
            EvaluationState.INVALID,
        ): EvaluationInvalidationSemantics,
        (
            EvaluationState.COMPLETED,
            EvaluationState.INVALID,
        ): EvaluationInvalidationSemantics,
        (
            EvaluationState.CONFLICTED,
            EvaluationState.INVALID,
        ): EvaluationInvalidationSemantics,
    }
)

_CONTROL_OR_POLICY_ACTORS: Final[frozenset[ActorType]] = frozenset(
    {ActorType.SCHEDULER, ActorType.POLICY_ENGINE, ActorType.HUMAN_OPERATOR}
)
_CONFLICT_CLEARANCE_ACTORS: Final[frozenset[ActorType]] = frozenset(
    {ActorType.EVALUATOR, ActorType.ARBITRATOR, ActorType.HUMAN_OPERATOR}
)


@dataclass(frozen=True, slots=True)
class EvaluationSemanticGuard:
    """Canonical semantic guard for the six implemented Evaluation edges."""

    evaluation_id: EvaluationId
    observed_entity_version: EntityVersion
    prior_state: EvaluationState
    target_state: EvaluationState
    correlation_id: CorrelationId
    semantic_input: EvaluationSemanticInput

    def __post_init__(self) -> None:
        _require_snapshot_scope(
            self.evaluation_id, self.observed_entity_version, self.correlation_id
        )
        if not isinstance(self.prior_state, EvaluationState) or not isinstance(
            self.target_state, EvaluationState
        ):
            raise InvalidDomainValue(
                "prior_state and target_state must be EvaluationState"
            )
        expected = _INPUT_TYPE_BY_EDGE.get((self.prior_state, self.target_state))
        if expected is None:
            raise InvalidDomainValue(
                "Evaluation semantic guard does not support this lifecycle edge"
            )
        if not isinstance(self.semantic_input, expected):
            raise InvalidDomainValue(
                f"semantic_input must be {expected.__name__} for this edge"
            )

    def validate(
        self,
        evaluation: Evaluation,
        target_state: EvaluationState,
        principal: ActorIdentity,
        correlation_id: CorrelationId,
    ) -> None:
        """Validate exact binding and the accepted edge-specific semantics."""
        if not isinstance(evaluation, Evaluation):
            raise InvalidDomainValue("evaluation must be an Evaluation")
        if not isinstance(target_state, EvaluationState):
            raise InvalidDomainValue("target_state must be an EvaluationState")
        if not isinstance(principal, ActorIdentity):
            raise InvalidDomainValue("principal must be an ActorIdentity")
        if not isinstance(correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if not (
            self.evaluation_id == evaluation.evaluation_id
            and self.observed_entity_version == evaluation.version
            and self.prior_state is evaluation.state
            and self.target_state is target_state
            and self.correlation_id == correlation_id
        ):
            raise InvariantViolation(
                "Evaluation semantic guard does not match the exact request snapshot"
            )

        semantics = self.semantic_input
        if isinstance(semantics, EvaluationStartSemantics):
            self._validate_start(evaluation, principal, semantics)
        elif isinstance(semantics, EvaluationCompletionSemantics):
            self._validate_completion(evaluation, principal, semantics)
        else:
            self._validate_invalidation(evaluation, principal, semantics)

    def validated_start_verifier(self) -> ActorIdentity:
        """Return the one verifier recorded by an already validated start guard."""
        if not isinstance(self.semantic_input, EvaluationStartSemantics):
            raise InvariantViolation("Evaluation semantic input is not start semantics")
        return self.semantic_input.assigned_verifier

    def validated_completion_result(self) -> EvaluationResult:
        """Return the independently scoped result from a validated completion guard."""
        if not isinstance(self.semantic_input, EvaluationCompletionSemantics):
            raise InvariantViolation(
                "Evaluation semantic input is not completion semantics"
            )
        return self.semantic_input.intended_result

    def _validate_start(
        self,
        evaluation: Evaluation,
        principal: ActorIdentity,
        semantics: EvaluationStartSemantics,
    ) -> None:
        verifier = semantics.assigned_verifier
        if verifier.actor_type is not ActorType.EVALUATOR:
            raise InvariantViolation("Evaluation start verifier must be an EVALUATOR")
        if principal != verifier:
            raise InvariantViolation(
                "Evaluation start principal must exactly match the assigned verifier"
            )
        if evaluation.verifier is not None and evaluation.verifier != verifier:
            raise InvariantViolation("Evaluation start cannot replace a verifier")
        if evaluation.result is not None:
            raise InvariantViolation("Evaluation start cannot have an existing result")

        independence = semantics.independence
        input_readiness = semantics.input_readiness
        self._require_start_decision_bound(independence, evaluation, verifier)
        self._require_start_decision_bound(input_readiness, evaluation, verifier)
        if independence.status is not EvaluationSemanticDecisionStatus.PASSED:
            raise InvariantViolation("Verifier-independence decision is not passed")
        if input_readiness.status is not EvaluationSemanticDecisionStatus.PASSED:
            raise InvariantViolation("Input-readiness decision is not passed")
        if independence.decided_by.actor_type not in _CONTROL_OR_POLICY_ACTORS:
            raise InvariantViolation(
                "Verifier-independence decision lacks trusted provenance"
            )
        if input_readiness.decided_by.actor_type not in _CONTROL_OR_POLICY_ACTORS:
            raise InvariantViolation(
                "Input-readiness decision lacks trusted control or policy provenance"
            )

    def _validate_completion(
        self,
        evaluation: Evaluation,
        principal: ActorIdentity,
        semantics: EvaluationCompletionSemantics,
    ) -> None:
        if (
            evaluation.verifier is None
            or evaluation.verifier.actor_type is not ActorType.EVALUATOR
        ):
            raise InvariantViolation(
                "Evaluation completion requires an EVALUATOR verifier"
            )
        if principal != evaluation.verifier:
            raise InvariantViolation(
                "Evaluation completion principal does not match the verifier"
            )
        if evaluation.result is not None:
            raise InvariantViolation(
                "Evaluation completion cannot replace an existing result"
            )

        completion = semantics.completion
        clearance = semantics.conflict_clearance
        self._require_completion_decision_bound(completion, evaluation)
        self._require_completion_decision_bound(clearance, evaluation)
        if completion.status is not EvaluationSemanticDecisionStatus.PASSED:
            raise InvariantViolation("Evaluation completion decision is not passed")
        if clearance.status is not EvaluationSemanticDecisionStatus.PASSED:
            raise InvariantViolation(
                "Evaluation conflict-clearance decision is not passed"
            )
        if completion.decided_by != principal:
            raise InvariantViolation(
                "Evaluation completion decision must bind the authoritative principal"
            )
        if clearance.decided_by.actor_type not in _CONFLICT_CLEARANCE_ACTORS:
            raise InvariantViolation(
                "Evaluation conflict-clearance decision lacks trusted provenance"
            )
        if not (
            completion.result == semantics.intended_result
            and clearance.result == semantics.intended_result
        ):
            raise InvariantViolation(
                "Completion provenance does not match the intended result"
            )
        if not semantics.intended_result.evidence_refs:
            raise InvariantViolation("Evaluation completion result requires evidence")

    def _validate_invalidation(
        self,
        evaluation: Evaluation,
        principal: ActorIdentity,
        semantics: EvaluationInvalidationSemantics,
    ) -> None:
        invalidation = semantics.invalidation
        if not can_invalidate_evaluation(evaluation, invalidation):
            raise InvariantViolation(
                "Invalidation record does not match the exact source snapshot"
            )
        if invalidation.correlation_id != self.correlation_id:
            raise InvariantViolation(
                "Evaluation invalidation record does not match the exact correlation"
            )
        if invalidation.invalidated_by != principal:
            raise InvariantViolation(
                "Invalidation principal does not match the authoritative principal"
            )

    def _require_start_decision_bound(
        self,
        decision: EvaluationVerifierIndependenceDecision
        | EvaluationInputReadinessDecision,
        evaluation: Evaluation,
        verifier: ActorIdentity,
    ) -> None:
        if not (
            decision.evaluation_id == self.evaluation_id
            and decision.observed_entity_version == self.observed_entity_version
            and decision.target == evaluation.target
            and decision.method == evaluation.method
            and decision.assigned_verifier == verifier
            and decision.correlation_id == self.correlation_id
        ):
            raise InvariantViolation(
                "Evaluation start decision does not match the exact request snapshot"
            )

    def _require_completion_decision_bound(
        self,
        decision: EvaluationCompletionDecision | EvaluationConflictClearanceDecision,
        evaluation: Evaluation,
    ) -> None:
        if not (
            decision.evaluation_id == self.evaluation_id
            and decision.observed_entity_version == self.observed_entity_version
            and decision.target == evaluation.target
            and decision.method == evaluation.method
            and decision.verifier == evaluation.verifier
            and decision.correlation_id == self.correlation_id
        ):
            raise InvariantViolation(
                "Completion decision does not match the exact request snapshot"
            )
