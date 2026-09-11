"""Canonical typed semantic guards for selected Evaluation lifecycle edges."""

from dataclasses import dataclass, replace
from enum import Enum
from types import MappingProxyType
from typing import Final

from .actors import ActorIdentity, ActorType
from .candidate_refs import EvidenceRef
from .errors import InvalidDomainValue, InvariantViolation
from .evaluation import Evaluation, EvaluationState
from .evaluation_arbitration import (
    EvaluationArbitrationRecord,
    can_arbitrate_evaluation_conflict_set,
)
from .evaluation_conflict import (
    EvaluationConflictMemberRef,
    EvaluationConflictScopeRef,
    EvaluationConflictSetRecord,
    EvaluationConflictSetRef,
    can_extend_evaluation_conflict_set,
)
from .evaluation_effective_use import derive_evaluation_effective_use
from .evaluation_invalidation import (
    EvaluationInvalidationRecord,
    can_invalidate_evaluation,
)
from .evaluation_result import EvaluationMethodRef, EvaluationResult
from .evaluation_target import EvaluationTargetRef
from .ids import CorrelationId, EvaluationArbitrationId, EvaluationId
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


@dataclass(frozen=True, slots=True)
class EvaluationConflictParticipantObservation:
    """One complete, caller-supplied participant snapshot for a conflict batch."""

    evaluation_id: EvaluationId
    observed_version: EntityVersion
    observed_state: EvaluationState
    target: EvaluationTargetRef

    def __post_init__(self) -> None:
        if not isinstance(self.evaluation_id, EvaluationId):
            raise InvalidDomainValue("evaluation_id must be an EvaluationId")
        if not isinstance(self.observed_version, EntityVersion):
            raise InvalidDomainValue("observed_version must be an EntityVersion")
        if not isinstance(self.observed_state, EvaluationState):
            raise InvalidDomainValue("observed_state must be an EvaluationState")
        if not isinstance(self.target, EvaluationTargetRef):
            raise InvalidDomainValue("target must be an EvaluationTargetRef")


@dataclass(frozen=True, slots=True)
class EvaluationConflictScopeMaterialityProvenance:
    """Independent evidence that exact members share the recorded affected scope."""

    conflict_set_ref: EvaluationConflictSetRef
    members: frozenset[EvaluationConflictMemberRef]
    affected_scope: EvaluationConflictScopeRef
    correlation_id: CorrelationId
    evidence_refs: frozenset[EvidenceRef]

    def __post_init__(self) -> None:
        if not isinstance(self.conflict_set_ref, EvaluationConflictSetRef):
            raise InvalidDomainValue(
                "conflict_set_ref must be an EvaluationConflictSetRef"
            )
        if not isinstance(self.members, frozenset) or not self.members:
            raise InvalidDomainValue("members must be a nonempty frozenset")
        if any(
            not isinstance(member, EvaluationConflictMemberRef)
            for member in self.members
        ):
            raise InvalidDomainValue(
                "Every member must be an EvaluationConflictMemberRef"
            )
        if len({member.evaluation_id for member in self.members}) != len(self.members):
            raise InvalidDomainValue(
                "Scope provenance members must have unique EvaluationIds"
            )
        if not isinstance(self.affected_scope, EvaluationConflictScopeRef):
            raise InvalidDomainValue(
                "affected_scope must be an EvaluationConflictScopeRef"
            )
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        _require_evidence(self.evidence_refs)


@dataclass(frozen=True, slots=True)
class EvaluationConflictSemantics:
    """Canonical full-batch input for RUNNING/COMPLETED -> CONFLICTED only."""

    conflict_set: EvaluationConflictSetRecord
    participant_observations: frozenset[EvaluationConflictParticipantObservation]
    scope_materiality: EvaluationConflictScopeMaterialityProvenance
    intended_conflicted_evaluation_ids: frozenset[EvaluationId]
    previous_conflict_set: EvaluationConflictSetRecord | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.conflict_set, EvaluationConflictSetRecord):
            raise InvalidDomainValue(
                "conflict_set must be an EvaluationConflictSetRecord"
            )
        if not isinstance(self.participant_observations, frozenset):
            raise InvalidDomainValue("participant_observations must be a frozenset")
        if any(
            not isinstance(item, EvaluationConflictParticipantObservation)
            for item in self.participant_observations
        ):
            raise InvalidDomainValue("Every participant observation must be typed")
        if len({item.evaluation_id for item in self.participant_observations}) != len(
            self.participant_observations
        ):
            raise InvalidDomainValue(
                "Participant observations must have unique EvaluationIds"
            )
        if not isinstance(
            self.scope_materiality, EvaluationConflictScopeMaterialityProvenance
        ):
            raise InvalidDomainValue("scope_materiality must be typed provenance")
        if not isinstance(self.intended_conflicted_evaluation_ids, frozenset) or any(
            not isinstance(item, EvaluationId)
            for item in self.intended_conflicted_evaluation_ids
        ):
            raise InvalidDomainValue(
                "intended_conflicted_evaluation_ids must be EvaluationIds"
            )
        if self.previous_conflict_set is not None and not isinstance(
            self.previous_conflict_set, EvaluationConflictSetRecord
        ):
            raise InvalidDomainValue(
                "previous_conflict_set must be an EvaluationConflictSetRecord or None"
            )


@dataclass(frozen=True, slots=True)
class EvaluationArbitrationSemantics:
    """Canonical caller-supplied history slice for an arbitration transition."""

    arbitration: EvaluationArbitrationRecord
    applicable_conflict_sets: frozenset[EvaluationConflictSetRecord]
    arbitration_history: frozenset[EvaluationArbitrationRecord]
    invalidation_history: frozenset[EvaluationInvalidationRecord]

    def __post_init__(self) -> None:
        if not isinstance(self.arbitration, EvaluationArbitrationRecord):
            raise InvalidDomainValue(
                "arbitration must be an EvaluationArbitrationRecord"
            )
        for value, item_type, name in (
            (
                self.applicable_conflict_sets,
                EvaluationConflictSetRecord,
                "applicable_conflict_sets",
            ),
            (
                self.arbitration_history,
                EvaluationArbitrationRecord,
                "arbitration_history",
            ),
            (
                self.invalidation_history,
                EvaluationInvalidationRecord,
                "invalidation_history",
            ),
        ):
            if not isinstance(value, frozenset) or any(
                not isinstance(item, item_type) for item in value
            ):
                raise InvalidDomainValue(
                    f"{name} must be a frozenset of {item_type.__name__}"
                )


type EvaluationSemanticInput = (
    EvaluationStartSemantics
    | EvaluationCompletionSemantics
    | EvaluationInvalidationSemantics
    | EvaluationConflictSemantics
    | EvaluationArbitrationSemantics
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
        (
            EvaluationState.RUNNING,
            EvaluationState.CONFLICTED,
        ): EvaluationConflictSemantics,
        (
            EvaluationState.COMPLETED,
            EvaluationState.CONFLICTED,
        ): EvaluationConflictSemantics,
        (
            EvaluationState.COMPLETED,
            EvaluationState.ARBITRATED,
        ): EvaluationArbitrationSemantics,
        (
            EvaluationState.CONFLICTED,
            EvaluationState.ARBITRATED,
        ): EvaluationArbitrationSemantics,
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
    """Canonical semantic guard for all ten non-creation Evaluation edges."""

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
        elif isinstance(semantics, EvaluationInvalidationSemantics):
            self._validate_invalidation(evaluation, principal, semantics)
        elif isinstance(semantics, EvaluationConflictSemantics):
            self._validate_conflict(evaluation, principal, semantics)
        else:
            self._validate_arbitration(evaluation, principal, semantics)

    def event_annotations(self) -> frozenset[tuple[str, str]]:
        """Return only stable supporting-record references for a validated edge."""
        semantics = self.semantic_input
        if isinstance(semantics, EvaluationConflictSemantics):
            return frozenset(
                {
                    (
                        "conflict_set_id",
                        str(semantics.conflict_set.conflict_set_id.value),
                    ),
                    ("conflict_set_version", str(semantics.conflict_set.version.value)),
                }
            )
        if isinstance(semantics, EvaluationArbitrationSemantics):
            return frozenset(
                {("arbitration_id", str(semantics.arbitration.arbitration_id.value))}
            )
        return frozenset()

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

    def _validate_conflict(
        self,
        evaluation: Evaluation,
        principal: ActorIdentity,
        semantics: EvaluationConflictSemantics,
    ) -> None:
        conflict = semantics.conflict_set
        if (
            conflict.correlation_id != self.correlation_id
            or conflict.recorded_by != principal
        ):
            raise InvariantViolation(
                "Conflict record does not bind correlation and principal"
            )
        subject_ref = EvaluationConflictMemberRef(
            evaluation.evaluation_id, evaluation.version
        )
        if subject_ref not in conflict.members:
            raise InvariantViolation(
                "Conflict set must contain the exact subject snapshot"
            )
        observations = {
            item.evaluation_id: item for item in semantics.participant_observations
        }
        members = {
            item.evaluation_id: item.observed_version for item in conflict.members
        }
        if set(observations) != set(members) or any(
            observations[item_id].observed_version != version
            for item_id, version in members.items()
        ):
            raise InvariantViolation(
                "Conflict participant observations must exactly match members"
            )
        subject_observation = observations.get(evaluation.evaluation_id)
        if subject_observation is None or not (
            subject_observation.observed_version == evaluation.version
            and subject_observation.observed_state is evaluation.state
            and subject_observation.target == evaluation.target
        ):
            raise InvariantViolation(
                "Conflict subject observation does not match the exact snapshot"
            )
        scope = semantics.scope_materiality
        if not (
            scope.conflict_set_ref
            == EvaluationConflictSetRef(conflict.conflict_set_id, conflict.version)
            and scope.members == conflict.members
            and scope.affected_scope == conflict.affected_scope
            and scope.correlation_id == conflict.correlation_id
        ):
            raise InvariantViolation(
                "Conflict scope/materiality provenance is not exact-bound"
            )
        expected_projection_ids = frozenset(
            item.evaluation_id
            for item in semantics.participant_observations
            if item.observed_state
            in (EvaluationState.RUNNING, EvaluationState.COMPLETED)
        )
        if semantics.intended_conflicted_evaluation_ids != expected_projection_ids:
            raise InvariantViolation(
                "Conflict projections must cover exactly new eligible participants"
            )
        if evaluation.evaluation_id not in expected_projection_ids:
            raise InvariantViolation(
                "Subject conflict transition must be a newly affected participant"
            )
        if conflict.previous_version is None:
            if semantics.previous_conflict_set is not None:
                raise InvariantViolation(
                    "Initial conflict set cannot supply prior provenance"
                )
        elif (
            semantics.previous_conflict_set is None
            or not can_extend_evaluation_conflict_set(
                semantics.previous_conflict_set, conflict
            )
        ):
            raise InvariantViolation(
                "Conflict-set extension is not append-only compatible"
            )

    def _validate_arbitration(
        self,
        evaluation: Evaluation,
        principal: ActorIdentity,
        semantics: EvaluationArbitrationSemantics,
    ) -> None:
        arbitration = semantics.arbitration
        if (
            arbitration.correlation_id != self.correlation_id
            or arbitration.decided_by != principal
        ):
            raise InvariantViolation(
                "Arbitration record does not bind correlation and principal"
            )
        subject_decisions = [
            decision
            for decision in arbitration.decisions
            if decision.evaluation_id == evaluation.evaluation_id
        ]
        if (
            len(subject_decisions) != 1
            or subject_decisions[0].observed_version != evaluation.version
        ):
            raise InvariantViolation(
                "Arbitration must contain one exact subject decision"
            )
        history_by_id: dict[EvaluationArbitrationId, EvaluationArbitrationRecord] = {}
        for record in semantics.arbitration_history:
            if record.arbitration_id in history_by_id:
                raise InvariantViolation(
                    "Arbitration history contains a repeated identity"
                )
            history_by_id[record.arbitration_id] = record
        if history_by_id.get(arbitration.arbitration_id) != arbitration:
            raise InvariantViolation(
                "Intended arbitration must be present in supplied history"
            )
        if evaluation.state is EvaluationState.COMPLETED:
            if (
                arbitration.conflict_set_ref is not None
                or semantics.applicable_conflict_sets
            ):
                raise InvariantViolation(
                    "Direct arbitration cannot fabricate a conflict set"
                )
        else:
            if arbitration.conflict_set_ref is None:
                raise InvariantViolation(
                    "Conflicted Evaluation requires conflict-linked arbitration"
                )
            matching = [
                conflict
                for conflict in semantics.applicable_conflict_sets
                if EvaluationConflictSetRef(conflict.conflict_set_id, conflict.version)
                == arbitration.conflict_set_ref
            ]
            if len(matching) != 1 or not can_arbitrate_evaluation_conflict_set(
                matching[0], arbitration
            ):
                raise InvariantViolation(
                    "Arbitration does not resolve its exact conflict-set version"
                )
        hypothetical = replace(evaluation, state=EvaluationState.ARBITRATED)
        view = derive_evaluation_effective_use(
            hypothetical,
            applicable_conflict_sets=semantics.applicable_conflict_sets,
            arbitration_records=semantics.arbitration_history,
            invalidation_records=semantics.invalidation_history,
        )
        if (
            view.arbitration_ambiguous
            or view.terminal_arbitration_id != arbitration.arbitration_id
            or not view.eligible_for_effective_use
        ):
            raise InvariantViolation(
                "Arbitration must be the terminal effective decision with no "
                "unresolved history"
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
