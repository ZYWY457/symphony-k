"""Canonical Outcome validation-start inputs for lifecycle transitions.

These immutable records consume already-made decisions and observations. They do
not evaluate policy, load artifacts or Evaluations, create validation work, or
mutate any lifecycle entity.
"""

from dataclasses import dataclass
from enum import Enum

from .actors import ActorIdentity, ActorType
from .candidate_refs import ArtifactRef, EvidenceRef
from .errors import InvalidDomainValue, InvariantViolation
from .evaluation import EvaluationState
from .evaluation_result import EvaluationMethodRef
from .evaluation_target import EvaluationTargetRef
from .ids import CorrelationId, EvaluationId, OutcomeId
from .outcome import Outcome, OutcomeState
from .version import EntityVersion


class OutcomeSemanticDecisionStatus(Enum):
    """Closed result vocabulary for an already-made Outcome semantic decision."""

    PASSED = "PASSED"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class OutcomeSemanticDecisionRef:
    """Opaque durable decision identity; it does not evaluate a decision."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Outcome semantic decision reference must contain non-whitespace text"
            )


@dataclass(frozen=True, slots=True)
class OutcomeValidationPolicyRef:
    """Opaque validation-policy identity/version, distinct from completion policy."""

    policy_id: str
    policy_version: str

    def __post_init__(self) -> None:
        for value, field in (
            (self.policy_id, "policy_id"),
            (self.policy_version, "policy_version"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise InvalidDomainValue(f"{field} must contain non-whitespace text")


@dataclass(frozen=True, slots=True)
class OutcomeEvaluationRequestRef:
    """Immutable provenance for one exact durable Evaluation request snapshot."""

    value: str
    evaluation_id: EvaluationId
    observed_evaluation_version: EntityVersion

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Outcome Evaluation request reference must contain non-whitespace text"
            )
        if not isinstance(self.evaluation_id, EvaluationId):
            raise InvalidDomainValue("evaluation_id must be an EvaluationId")
        if not isinstance(self.observed_evaluation_version, EntityVersion):
            raise InvalidDomainValue(
                "observed_evaluation_version must be an EntityVersion"
            )


def _require_outcome_snapshot_scope(
    outcome_id: OutcomeId,
    observed_entity_version: EntityVersion,
    correlation_id: CorrelationId,
) -> None:
    if not isinstance(outcome_id, OutcomeId):
        raise InvalidDomainValue("outcome_id must be an OutcomeId")
    if not isinstance(observed_entity_version, EntityVersion):
        raise InvalidDomainValue("observed_entity_version must be an EntityVersion")
    if not isinstance(correlation_id, CorrelationId):
        raise InvalidDomainValue("correlation_id must be a CorrelationId")


def _require_evidence(evidence_refs: frozenset[EvidenceRef]) -> None:
    if not isinstance(evidence_refs, frozenset) or not evidence_refs:
        raise InvalidDomainValue("Semantic decisions require evidence references")
    if any(not isinstance(reference, EvidenceRef) for reference in evidence_refs):
        raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")


@dataclass(frozen=True, slots=True)
class OutcomeValidationArtifactScope:
    """Explicit candidate artifact scope bound to one Outcome snapshot."""

    outcome_id: OutcomeId
    observed_entity_version: EntityVersion
    correlation_id: CorrelationId
    artifact_refs: frozenset[ArtifactRef]

    def __post_init__(self) -> None:
        _require_outcome_snapshot_scope(
            self.outcome_id, self.observed_entity_version, self.correlation_id
        )
        if not isinstance(self.artifact_refs, frozenset) or not self.artifact_refs:
            raise InvalidDomainValue("artifact_refs must be a nonempty frozenset")
        if any(
            not isinstance(reference, ArtifactRef) for reference in self.artifact_refs
        ):
            raise InvalidDomainValue("Every artifact reference must be an ArtifactRef")


@dataclass(frozen=True, slots=True)
class OutcomeValidationPolicyDecision:
    """Evidence-backed applicability decision for one exact validation attempt."""

    decision_ref: OutcomeSemanticDecisionRef
    status: OutcomeSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    outcome_id: OutcomeId
    observed_entity_version: EntityVersion
    correlation_id: CorrelationId
    validation_policy_ref: OutcomeValidationPolicyRef

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, OutcomeSemanticDecisionRef):
            raise InvalidDomainValue(
                "decision_ref must be an OutcomeSemanticDecisionRef"
            )
        if not isinstance(self.status, OutcomeSemanticDecisionStatus):
            raise InvalidDomainValue("status must be an OutcomeSemanticDecisionStatus")
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)
        _require_outcome_snapshot_scope(
            self.outcome_id, self.observed_entity_version, self.correlation_id
        )
        if not isinstance(self.validation_policy_ref, OutcomeValidationPolicyRef):
            raise InvalidDomainValue(
                "validation_policy_ref must be an OutcomeValidationPolicyRef"
            )


@dataclass(frozen=True, slots=True)
class OutcomeEvaluationRequestObservation:
    """Immutable observation of a durable Evaluation request for this Outcome."""

    request_ref: OutcomeEvaluationRequestRef
    evaluation_id: EvaluationId
    observed_evaluation_version: EntityVersion
    observed_state: EvaluationState
    target: EvaluationTargetRef
    method: EvaluationMethodRef
    requested_by: ActorIdentity
    verifier: ActorIdentity | None
    outcome_id: OutcomeId
    observed_outcome_version: EntityVersion
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.request_ref, OutcomeEvaluationRequestRef):
            raise InvalidDomainValue(
                "request_ref must be an OutcomeEvaluationRequestRef"
            )
        if not isinstance(self.evaluation_id, EvaluationId):
            raise InvalidDomainValue("evaluation_id must be an EvaluationId")
        if not isinstance(self.observed_evaluation_version, EntityVersion):
            raise InvalidDomainValue(
                "observed_evaluation_version must be an EntityVersion"
            )
        if not isinstance(self.observed_state, EvaluationState):
            raise InvalidDomainValue("observed_state must be an EvaluationState")
        if not isinstance(self.target, EvaluationTargetRef):
            raise InvalidDomainValue("target must be an EvaluationTargetRef")
        if not isinstance(self.method, EvaluationMethodRef):
            raise InvalidDomainValue("method must be an EvaluationMethodRef")
        if not isinstance(self.requested_by, ActorIdentity):
            raise InvalidDomainValue("requested_by must be an ActorIdentity")
        if self.verifier is not None and not isinstance(self.verifier, ActorIdentity):
            raise InvalidDomainValue("verifier must be an ActorIdentity or None")
        _require_outcome_snapshot_scope(
            self.outcome_id, self.observed_outcome_version, self.correlation_id
        )


@dataclass(frozen=True, slots=True)
class OutcomeValidationStartSemantics:
    """The complete independent-validation start bundle for one candidate."""

    artifact_scope: OutcomeValidationArtifactScope
    validation_policy: OutcomeValidationPolicyDecision
    evaluation_request: OutcomeEvaluationRequestObservation

    def __post_init__(self) -> None:
        if not isinstance(self.artifact_scope, OutcomeValidationArtifactScope):
            raise InvalidDomainValue(
                "artifact_scope must be an OutcomeValidationArtifactScope"
            )
        if not isinstance(self.validation_policy, OutcomeValidationPolicyDecision):
            raise InvalidDomainValue(
                "validation_policy must be an OutcomeValidationPolicyDecision"
            )
        if not isinstance(self.evaluation_request, OutcomeEvaluationRequestObservation):
            raise InvalidDomainValue(
                "evaluation_request must be an OutcomeEvaluationRequestObservation"
            )


@dataclass(frozen=True, slots=True)
class OutcomeSemanticGuard:
    """Canonical guard for the exact `PROPOSED -> VALIDATING` transition."""

    outcome_id: OutcomeId
    observed_entity_version: EntityVersion
    prior_state: OutcomeState
    target_state: OutcomeState
    correlation_id: CorrelationId
    semantic_input: OutcomeValidationStartSemantics

    def __post_init__(self) -> None:
        _require_outcome_snapshot_scope(
            self.outcome_id, self.observed_entity_version, self.correlation_id
        )
        if (
            self.prior_state is not OutcomeState.PROPOSED
            or self.target_state is not OutcomeState.VALIDATING
        ):
            raise InvalidDomainValue(
                "Outcome semantic guard supports only PROPOSED -> VALIDATING"
            )
        if not isinstance(self.semantic_input, OutcomeValidationStartSemantics):
            raise InvalidDomainValue(
                "semantic_input must be OutcomeValidationStartSemantics"
            )

    def validate(
        self,
        outcome: Outcome,
        target_state: OutcomeState,
        correlation_id: CorrelationId,
    ) -> None:
        """Validate the binding and start validation without a verdict."""
        if not isinstance(outcome, Outcome):
            raise InvalidDomainValue("outcome must be an Outcome")
        if not isinstance(target_state, OutcomeState):
            raise InvalidDomainValue("target_state must be an OutcomeState")
        if not isinstance(correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if not (
            self.outcome_id == outcome.outcome_id
            and self.observed_entity_version == outcome.version
            and self.prior_state is outcome.state
            and self.target_state is target_state
            and self.correlation_id == correlation_id
        ):
            raise InvariantViolation(
                "Outcome semantic guard does not match the exact request snapshot"
            )

        semantics = self.semantic_input
        self._validate_artifact_scope(outcome, semantics.artifact_scope)
        self._validate_policy(semantics.validation_policy)
        self._validate_evaluation_request(outcome, semantics.evaluation_request)

    def _validate_artifact_scope(
        self,
        outcome: Outcome,
        artifact_scope: OutcomeValidationArtifactScope,
    ) -> None:
        self._require_bound(
            artifact_scope.outcome_id,
            artifact_scope.observed_entity_version,
            artifact_scope.correlation_id,
        )
        if not artifact_scope.artifact_refs.issubset(outcome.artifact_refs):
            raise InvariantViolation(
                "Validation artifact scope contains an artifact absent from Outcome"
            )

    def _validate_policy(self, policy: OutcomeValidationPolicyDecision) -> None:
        self._require_bound(
            policy.outcome_id,
            policy.observed_entity_version,
            policy.correlation_id,
        )
        if policy.status is not OutcomeSemanticDecisionStatus.PASSED:
            raise InvariantViolation("Validation-policy applicability is not satisfied")
        if policy.decided_by.actor_type is ActorType.WORKER:
            raise InvariantViolation(
                "Worker cannot establish validation-policy applicability"
            )

    def _validate_evaluation_request(
        self,
        outcome: Outcome,
        observation: OutcomeEvaluationRequestObservation,
    ) -> None:
        self._require_bound(
            observation.outcome_id,
            observation.observed_outcome_version,
            observation.correlation_id,
        )
        if observation.observed_state is not EvaluationState.PENDING:
            raise InvariantViolation("Evaluation request is not in PENDING state")
        if not (
            observation.request_ref.evaluation_id == observation.evaluation_id
            and observation.request_ref.observed_evaluation_version
            == observation.observed_evaluation_version
        ):
            raise InvariantViolation(
                "Evaluation request provenance does not match the exact snapshot"
            )
        if not (
            observation.target.reference == outcome.outcome_id
            and observation.target.version == outcome.version
        ):
            raise InvariantViolation(
                "Evaluation request does not target the exact Outcome snapshot"
            )
        if observation.requested_by.actor_type is ActorType.WORKER:
            raise InvariantViolation(
                "Worker request cannot establish independent validation"
            )
        if observation.verifier == outcome.producer:
            raise InvariantViolation(
                "Outcome producer cannot be the assigned independent verifier"
            )

    def _require_bound(
        self,
        outcome_id: OutcomeId,
        observed_entity_version: EntityVersion,
        correlation_id: CorrelationId,
    ) -> None:
        if not (
            outcome_id == self.outcome_id
            and observed_entity_version == self.observed_entity_version
            and correlation_id == self.correlation_id
        ):
            raise InvariantViolation(
                "Outcome semantic input does not match the exact request snapshot"
            )
