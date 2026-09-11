"""Canonical Outcome validation and disposition lifecycle inputs.

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
from .evaluation_effective_use import EvaluationEffectiveUseView
from .evaluation_result import EvaluationMethodRef, EvaluationVerdict
from .evaluation_target import EvaluationTargetRef
from .ids import CorrelationId, EvaluationId, OutcomeId, RunId, TaskId
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


class OutcomeDisposition(Enum):
    """Explicit Outcome-side interpretation, never an Evaluation verdict taxonomy."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class OutcomeDispositionPolicyRef:
    """Dedicated Outcome disposition-policy identity and version."""

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
class OutcomeValidationLineage:
    """Exact immutable link from a VALIDATING snapshot to validation start."""

    outcome_id: OutcomeId
    candidate_version: EntityVersion
    validating_version: EntityVersion
    correlation_id: CorrelationId
    artifact_refs: frozenset[ArtifactRef]
    evaluation_request_ref: OutcomeEvaluationRequestRef

    def __post_init__(self) -> None:
        _require_outcome_snapshot_scope(
            self.outcome_id, self.validating_version, self.correlation_id
        )
        if not isinstance(self.candidate_version, EntityVersion):
            raise InvalidDomainValue("candidate_version must be an EntityVersion")
        if self.validating_version != self.candidate_version.next():
            raise InvalidDomainValue(
                "validating_version must immediately follow candidate_version"
            )
        if not isinstance(self.artifact_refs, frozenset) or not self.artifact_refs:
            raise InvalidDomainValue("artifact_refs must be a nonempty frozenset")
        if any(
            not isinstance(reference, ArtifactRef) for reference in self.artifact_refs
        ):
            raise InvalidDomainValue("Every artifact reference must be an ArtifactRef")
        if not isinstance(self.evaluation_request_ref, OutcomeEvaluationRequestRef):
            raise InvalidDomainValue(
                "evaluation_request_ref must be an OutcomeEvaluationRequestRef"
            )


@dataclass(frozen=True, slots=True)
class OutcomeEvaluationEffectiveUseObservation:
    """Exact observed Evaluation snapshot plus its accepted effective-use view."""

    request_ref: OutcomeEvaluationRequestRef
    evaluation_id: EvaluationId
    observed_evaluation_version: EntityVersion
    observed_state: EvaluationState
    target: EvaluationTargetRef
    verifier: ActorIdentity | None
    effective_use: EvaluationEffectiveUseView
    correlation_id: CorrelationId
    effective_use_snapshot: "OutcomeEvaluationEffectiveUseSnapshot"

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
        if self.verifier is not None and not isinstance(self.verifier, ActorIdentity):
            raise InvalidDomainValue("verifier must be an ActorIdentity or None")
        if not isinstance(self.effective_use, EvaluationEffectiveUseView):
            raise InvalidDomainValue(
                "effective_use must be an EvaluationEffectiveUseView"
            )
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if not isinstance(
            self.effective_use_snapshot, OutcomeEvaluationEffectiveUseSnapshot
        ):
            raise InvalidDomainValue(
                "effective_use_snapshot must be an "
                "OutcomeEvaluationEffectiveUseSnapshot"
            )


@dataclass(frozen=True, slots=True)
class OutcomeEvaluationEffectiveUseSnapshot:
    """Immutable effective-use provenance for one exact Evaluation snapshot."""

    evaluation_id: EvaluationId
    observed_evaluation_version: EntityVersion
    observed_state: EvaluationState
    target: EvaluationTargetRef
    effective_use: EvaluationEffectiveUseView

    def __post_init__(self) -> None:
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
        if not isinstance(self.effective_use, EvaluationEffectiveUseView):
            raise InvalidDomainValue(
                "effective_use must be an EvaluationEffectiveUseView"
            )
        if self.effective_use.evaluation_id != self.evaluation_id:
            raise InvalidDomainValue(
                "effective_use must concern the exact observed Evaluation"
            )


@dataclass(frozen=True, slots=True)
class OutcomeDispositionPolicyDecision:
    """Explicit policy interpretation of one effective judgement for one candidate."""

    decision_ref: OutcomeSemanticDecisionRef
    status: OutcomeSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    validation_lineage: OutcomeValidationLineage
    evaluation_id: EvaluationId
    observed_evaluation_version: EntityVersion
    effective_judgement: EvaluationVerdict
    disposition: OutcomeDisposition
    policy_ref: OutcomeDispositionPolicyRef
    human_acceptance_required: bool

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
        if not isinstance(self.validation_lineage, OutcomeValidationLineage):
            raise InvalidDomainValue(
                "validation_lineage must be an OutcomeValidationLineage"
            )
        if not isinstance(self.evaluation_id, EvaluationId):
            raise InvalidDomainValue("evaluation_id must be an EvaluationId")
        if not isinstance(self.observed_evaluation_version, EntityVersion):
            raise InvalidDomainValue(
                "observed_evaluation_version must be an EntityVersion"
            )
        if not isinstance(self.effective_judgement, EvaluationVerdict):
            raise InvalidDomainValue("effective_judgement must be an EvaluationVerdict")
        if not isinstance(self.disposition, OutcomeDisposition):
            raise InvalidDomainValue("disposition must be an OutcomeDisposition")
        if not isinstance(self.policy_ref, OutcomeDispositionPolicyRef):
            raise InvalidDomainValue(
                "policy_ref must be an OutcomeDispositionPolicyRef"
            )
        if not isinstance(self.human_acceptance_required, bool):
            raise InvalidDomainValue("human_acceptance_required must be a bool")


@dataclass(frozen=True, slots=True)
class OutcomeHumanAcceptanceDecision:
    """Affirmative human input to authority C, never direct lifecycle authority."""

    decision_ref: OutcomeSemanticDecisionRef
    affirmative: bool
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    validation_lineage: OutcomeValidationLineage
    evaluation_id: EvaluationId
    observed_evaluation_version: EntityVersion
    effective_judgement: EvaluationVerdict
    disposition: OutcomeDisposition
    policy_ref: OutcomeDispositionPolicyRef
    policy_decision_ref: OutcomeSemanticDecisionRef

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, OutcomeSemanticDecisionRef):
            raise InvalidDomainValue(
                "decision_ref must be an OutcomeSemanticDecisionRef"
            )
        if not isinstance(self.affirmative, bool):
            raise InvalidDomainValue("affirmative must be a bool")
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)
        if not isinstance(self.validation_lineage, OutcomeValidationLineage):
            raise InvalidDomainValue(
                "validation_lineage must be an OutcomeValidationLineage"
            )
        if not isinstance(self.evaluation_id, EvaluationId):
            raise InvalidDomainValue("evaluation_id must be an EvaluationId")
        if not isinstance(self.observed_evaluation_version, EntityVersion):
            raise InvalidDomainValue(
                "observed_evaluation_version must be an EntityVersion"
            )
        if not isinstance(self.effective_judgement, EvaluationVerdict):
            raise InvalidDomainValue("effective_judgement must be an EvaluationVerdict")
        if not isinstance(self.disposition, OutcomeDisposition):
            raise InvalidDomainValue("disposition must be an OutcomeDisposition")
        if not isinstance(self.policy_ref, OutcomeDispositionPolicyRef):
            raise InvalidDomainValue(
                "policy_ref must be an OutcomeDispositionPolicyRef"
            )
        if not isinstance(self.policy_decision_ref, OutcomeSemanticDecisionRef):
            raise InvalidDomainValue(
                "policy_decision_ref must be an OutcomeSemanticDecisionRef"
            )


@dataclass(frozen=True, slots=True)
class OutcomeDispositionSemantics:
    """Complete explicit Outcome disposition inputs for one VALIDATING snapshot."""

    validation_lineage: OutcomeValidationLineage
    evaluation: OutcomeEvaluationEffectiveUseObservation
    policy_decision: OutcomeDispositionPolicyDecision
    human_acceptance: OutcomeHumanAcceptanceDecision | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.validation_lineage, OutcomeValidationLineage):
            raise InvalidDomainValue(
                "validation_lineage must be an OutcomeValidationLineage"
            )
        if not isinstance(self.evaluation, OutcomeEvaluationEffectiveUseObservation):
            raise InvalidDomainValue(
                "evaluation must be an OutcomeEvaluationEffectiveUseObservation"
            )
        if not isinstance(self.policy_decision, OutcomeDispositionPolicyDecision):
            raise InvalidDomainValue(
                "policy_decision must be an OutcomeDispositionPolicyDecision"
            )
        if self.human_acceptance is not None and not isinstance(
            self.human_acceptance, OutcomeHumanAcceptanceDecision
        ):
            raise InvalidDomainValue(
                "human_acceptance must be an OutcomeHumanAcceptanceDecision or None"
            )


@dataclass(frozen=True, slots=True)
class OutcomeReplacementObservation:
    """Exact immutable observation of an existing replacement Outcome."""

    outcome_id: OutcomeId
    observed_entity_version: EntityVersion
    observed_state: OutcomeState
    originating_run_id: RunId
    prior_outcome_id: OutcomeId | None
    superseded_by_outcome_id: OutcomeId | None
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        _require_outcome_snapshot_scope(
            self.outcome_id, self.observed_entity_version, self.correlation_id
        )
        if not isinstance(self.observed_state, OutcomeState):
            raise InvalidDomainValue("observed_state must be an OutcomeState")
        if not isinstance(self.originating_run_id, RunId):
            raise InvalidDomainValue("originating_run_id must be a RunId")
        for name, outcome_id in (
            ("prior_outcome_id", self.prior_outcome_id),
            ("superseded_by_outcome_id", self.superseded_by_outcome_id),
        ):
            if outcome_id is not None and not isinstance(outcome_id, OutcomeId):
                raise InvalidDomainValue(f"{name} must be an OutcomeId or None")


@dataclass(frozen=True, slots=True)
class OutcomeOriginatingRunObservation:
    """Exact Run-to-Task provenance for one observed Outcome snapshot."""

    outcome_id: OutcomeId
    observed_outcome_version: EntityVersion
    originating_run_id: RunId
    observed_run_version: EntityVersion
    task_id: TaskId

    def __post_init__(self) -> None:
        if not isinstance(self.outcome_id, OutcomeId):
            raise InvalidDomainValue("outcome_id must be an OutcomeId")
        if not isinstance(self.observed_outcome_version, EntityVersion):
            raise InvalidDomainValue(
                "observed_outcome_version must be an EntityVersion"
            )
        if not isinstance(self.originating_run_id, RunId):
            raise InvalidDomainValue("originating_run_id must be a RunId")
        if not isinstance(self.observed_run_version, EntityVersion):
            raise InvalidDomainValue("observed_run_version must be an EntityVersion")
        if not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId")


@dataclass(frozen=True, slots=True)
class OutcomeAcceptanceScopeRef:
    """Opaque identity/version for an Outcome acceptance scope."""

    scope_id: str
    scope_version: str

    def __post_init__(self) -> None:
        for value, field in (
            (self.scope_id, "scope_id"),
            (self.scope_version, "scope_version"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise InvalidDomainValue(f"{field} must contain non-whitespace text")


@dataclass(frozen=True, slots=True)
class OutcomeAcceptanceScopeCompatibilityDecision:
    """Policy decision that two exact Outcome snapshots share an acceptance scope."""

    decision_ref: OutcomeSemanticDecisionRef
    status: OutcomeSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    source_outcome_id: OutcomeId
    source_outcome_version: EntityVersion
    source_originating_run_id: RunId
    source_observed_run_version: EntityVersion
    replacement_outcome_id: OutcomeId
    replacement_outcome_version: EntityVersion
    replacement_originating_run_id: RunId
    replacement_observed_run_version: EntityVersion
    task_id: TaskId
    acceptance_scope: OutcomeAcceptanceScopeRef
    correlation_id: CorrelationId

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
        for value, expected, field in (
            (self.source_outcome_id, OutcomeId, "source_outcome_id"),
            (self.source_outcome_version, EntityVersion, "source_outcome_version"),
            (self.source_originating_run_id, RunId, "source_originating_run_id"),
            (
                self.source_observed_run_version,
                EntityVersion,
                "source_observed_run_version",
            ),
            (self.replacement_outcome_id, OutcomeId, "replacement_outcome_id"),
            (
                self.replacement_outcome_version,
                EntityVersion,
                "replacement_outcome_version",
            ),
            (
                self.replacement_originating_run_id,
                RunId,
                "replacement_originating_run_id",
            ),
            (
                self.replacement_observed_run_version,
                EntityVersion,
                "replacement_observed_run_version",
            ),
            (self.task_id, TaskId, "task_id"),
            (self.correlation_id, CorrelationId, "correlation_id"),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue(f"{field} has an invalid type")
        if not isinstance(self.acceptance_scope, OutcomeAcceptanceScopeRef):
            raise InvalidDomainValue(
                "acceptance_scope must be an OutcomeAcceptanceScopeRef"
            )


@dataclass(frozen=True, slots=True)
class OutcomePriorLineageObservation:
    """One immutable member of a complete observed prior-candidate chain."""

    outcome_id: OutcomeId
    observed_entity_version: EntityVersion
    prior_outcome_id: OutcomeId | None

    def __post_init__(self) -> None:
        if not isinstance(self.outcome_id, OutcomeId):
            raise InvalidDomainValue("outcome_id must be an OutcomeId")
        if not isinstance(self.observed_entity_version, EntityVersion):
            raise InvalidDomainValue("observed_entity_version must be an EntityVersion")
        if self.prior_outcome_id is not None and not isinstance(
            self.prior_outcome_id, OutcomeId
        ):
            raise InvalidDomainValue("prior_outcome_id must be an OutcomeId or None")


@dataclass(frozen=True, slots=True)
class OutcomeSupersessionSemantics:
    """Complete caller-supplied evidence bundle for one supersession attempt."""

    replacement: OutcomeReplacementObservation
    source_run: OutcomeOriginatingRunObservation
    replacement_run: OutcomeOriginatingRunObservation
    acceptance_scope: OutcomeAcceptanceScopeRef
    acceptance_scope_decision: OutcomeAcceptanceScopeCompatibilityDecision
    source_prior_lineage: tuple[OutcomePriorLineageObservation, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.replacement, OutcomeReplacementObservation):
            raise InvalidDomainValue(
                "replacement must be an OutcomeReplacementObservation"
            )
        if not isinstance(self.source_run, OutcomeOriginatingRunObservation):
            raise InvalidDomainValue(
                "source_run must be an OutcomeOriginatingRunObservation"
            )
        if not isinstance(self.replacement_run, OutcomeOriginatingRunObservation):
            raise InvalidDomainValue(
                "replacement_run must be an OutcomeOriginatingRunObservation"
            )
        if not isinstance(self.acceptance_scope, OutcomeAcceptanceScopeRef):
            raise InvalidDomainValue(
                "acceptance_scope must be an OutcomeAcceptanceScopeRef"
            )
        if not isinstance(
            self.acceptance_scope_decision, OutcomeAcceptanceScopeCompatibilityDecision
        ):
            raise InvalidDomainValue(
                "acceptance_scope_decision must be an "
                "OutcomeAcceptanceScopeCompatibilityDecision"
            )
        if (
            not isinstance(self.source_prior_lineage, tuple)
            or not self.source_prior_lineage
        ):
            raise InvalidDomainValue("source_prior_lineage must be a nonempty tuple")
        if any(
            not isinstance(member, OutcomePriorLineageObservation)
            for member in self.source_prior_lineage
        ):
            raise InvalidDomainValue(
                "Every source_prior_lineage member must be an "
                "OutcomePriorLineageObservation"
            )


@dataclass(frozen=True, slots=True)
class OutcomeSemanticGuard:
    """Canonical guard for implemented Outcome semantic edges through M7C4C."""

    outcome_id: OutcomeId
    observed_entity_version: EntityVersion
    prior_state: OutcomeState
    target_state: OutcomeState
    correlation_id: CorrelationId
    semantic_input: (
        OutcomeValidationStartSemantics
        | OutcomeDispositionSemantics
        | OutcomeSupersessionSemantics
    )

    def __post_init__(self) -> None:
        _require_outcome_snapshot_scope(
            self.outcome_id, self.observed_entity_version, self.correlation_id
        )
        edge = (self.prior_state, self.target_state)
        expected_input: (
            type[OutcomeValidationStartSemantics]
            | type[OutcomeDispositionSemantics]
            | type[OutcomeSupersessionSemantics]
        )
        if edge == (OutcomeState.PROPOSED, OutcomeState.VALIDATING):
            expected_input = OutcomeValidationStartSemantics
        elif edge in {
            (OutcomeState.VALIDATING, OutcomeState.ACCEPTED),
            (OutcomeState.VALIDATING, OutcomeState.REJECTED),
        }:
            expected_input = OutcomeDispositionSemantics
        elif edge in {
            (OutcomeState.PROPOSED, OutcomeState.SUPERSEDED),
            (OutcomeState.VALIDATING, OutcomeState.SUPERSEDED),
            (OutcomeState.ACCEPTED, OutcomeState.SUPERSEDED),
            (OutcomeState.REJECTED, OutcomeState.SUPERSEDED),
        }:
            expected_input = OutcomeSupersessionSemantics
        else:
            raise InvalidDomainValue(
                "Outcome semantic guard does not support this lifecycle edge"
            )
        if not isinstance(self.semantic_input, expected_input):
            raise InvalidDomainValue(
                f"semantic_input must be {expected_input.__name__} for this edge"
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
        if isinstance(semantics, OutcomeValidationStartSemantics):
            self._validate_artifact_scope(outcome, semantics.artifact_scope)
            self._validate_policy(semantics.validation_policy)
            self._validate_evaluation_request(outcome, semantics.evaluation_request)
            return
        if isinstance(semantics, OutcomeDispositionSemantics):
            self._validate_disposition(outcome, target_state, semantics)
            return
        self._validate_supersession(outcome, semantics)

    def validated_replacement_outcome_id(self) -> OutcomeId:
        """Return the replacement only for an already exact-bound supersession guard."""
        if not isinstance(self.semantic_input, OutcomeSupersessionSemantics):
            raise InvariantViolation(
                "Outcome semantic input is not supersession semantics"
            )
        return self.semantic_input.replacement.outcome_id

    def _validate_supersession(
        self,
        source: Outcome,
        semantics: OutcomeSupersessionSemantics,
    ) -> None:
        replacement = semantics.replacement
        if not (
            replacement.correlation_id == self.correlation_id
            and replacement.outcome_id != source.outcome_id
            and replacement.prior_outcome_id == source.outcome_id
            and replacement.superseded_by_outcome_id is None
            and replacement.observed_state
            not in {OutcomeState.SUPERSEDED, OutcomeState.EXPIRED}
        ):
            raise InvariantViolation(
                "Replacement Outcome is not a distinct current direct successor"
            )
        if source.superseded_by_outcome_id is not None:
            raise InvariantViolation("Source Outcome already has a replacement link")
        if (
            source.state is OutcomeState.ACCEPTED
            and replacement.observed_state is not OutcomeState.ACCEPTED
        ):
            raise InvariantViolation(
                "An ACCEPTED source requires an already-ACCEPTED replacement"
            )

        source_run = semantics.source_run
        replacement_run = semantics.replacement_run
        if not (
            source_run.outcome_id == source.outcome_id
            and source_run.observed_outcome_version == source.version
            and source_run.originating_run_id == source.run_id
            and replacement_run.outcome_id == replacement.outcome_id
            and replacement_run.observed_outcome_version
            == replacement.observed_entity_version
            and replacement_run.originating_run_id == replacement.originating_run_id
            and source_run.task_id == replacement_run.task_id
        ):
            raise InvariantViolation(
                "Originating Run observations do not prove same-Task provenance"
            )

        decision = semantics.acceptance_scope_decision
        if not (
            decision.status is OutcomeSemanticDecisionStatus.PASSED
            and decision.decided_by.actor_type is ActorType.POLICY_ENGINE
            and decision.source_outcome_id == source.outcome_id
            and decision.source_outcome_version == source.version
            and decision.source_originating_run_id == source_run.originating_run_id
            and decision.source_observed_run_version == source_run.observed_run_version
            and decision.replacement_outcome_id == replacement.outcome_id
            and decision.replacement_outcome_version
            == replacement.observed_entity_version
            and decision.replacement_originating_run_id
            == replacement_run.originating_run_id
            and decision.replacement_observed_run_version
            == replacement_run.observed_run_version
            and decision.task_id == source_run.task_id
            and decision.acceptance_scope == semantics.acceptance_scope
            and decision.correlation_id == self.correlation_id
        ):
            raise InvariantViolation(
                "Acceptance-scope compatibility decision is not exact and passed"
            )

        lineage = semantics.source_prior_lineage
        first = lineage[0]
        if not (
            first.outcome_id == source.outcome_id
            and first.observed_entity_version == source.version
            and first.prior_outcome_id == source.prior_outcome_id
        ):
            raise InvariantViolation("Prior lineage does not exact-bind the source")
        lineage_ids = tuple(member.outcome_id for member in lineage)
        if len(set(lineage_ids)) != len(lineage_ids):
            raise InvariantViolation(
                "Prior lineage contains duplicate or cyclic members"
            )
        if replacement.outcome_id in lineage_ids:
            raise InvariantViolation(
                "Replacement Outcome already occurs in source ancestry"
            )
        for member, prior in zip(lineage[:-1], lineage[1:], strict=True):
            if member.prior_outcome_id != prior.outcome_id:
                raise InvariantViolation("Prior lineage is discontinuous")
        if lineage[-1].prior_outcome_id is not None:
            raise InvariantViolation("Prior lineage is incomplete")

    def _validate_disposition(
        self,
        outcome: Outcome,
        target_state: OutcomeState,
        semantics: OutcomeDispositionSemantics,
    ) -> None:
        lineage = semantics.validation_lineage
        if not (
            lineage.outcome_id == outcome.outcome_id
            and lineage.validating_version == outcome.version
            and lineage.correlation_id == self.correlation_id
            and lineage.artifact_refs.issubset(outcome.artifact_refs)
        ):
            raise InvariantViolation(
                "Validation lineage does not match the exact VALIDATING snapshot"
            )

        observation = semantics.evaluation
        effective_use = observation.effective_use
        if not (
            observation.request_ref == lineage.evaluation_request_ref
            and observation.evaluation_id == observation.request_ref.evaluation_id
            and observation.evaluation_id == effective_use.evaluation_id
            and observation.observed_evaluation_version.value
            >= observation.request_ref.observed_evaluation_version.value
            and observation.target.reference == outcome.outcome_id
            and observation.target.version == lineage.candidate_version
            and observation.correlation_id == lineage.correlation_id
            and observation.evaluation_id
            == observation.effective_use_snapshot.evaluation_id
            and observation.observed_evaluation_version
            == observation.effective_use_snapshot.observed_evaluation_version
            and observation.observed_state
            is observation.effective_use_snapshot.observed_state
            and observation.target == observation.effective_use_snapshot.target
            and effective_use == observation.effective_use_snapshot.effective_use
        ):
            raise InvariantViolation(
                "Evaluation effective-use observation does not match validation lineage"
            )
        if observation.observed_state not in {
            EvaluationState.COMPLETED,
            EvaluationState.ARBITRATED,
        }:
            raise InvariantViolation(
                "Evaluation lifecycle state is not usable for Outcome disposition"
            )
        if (
            observation.verifier is None
            or observation.verifier.actor_type is not ActorType.EVALUATOR
        ):
            raise InvariantViolation(
                "Outcome disposition requires an independent EVALUATOR"
            )
        if observation.verifier.actor_id == outcome.producer.actor_id:
            raise InvariantViolation(
                "Outcome producer cannot be the independent validation authority"
            )
        if not effective_use.eligible_for_effective_use:
            raise InvariantViolation("Evaluation is ineligible for effective use")
        if effective_use.effective_judgement is None:
            raise InvariantViolation("Evaluation effective judgement is missing")
        if effective_use.unresolved_conflicts:
            raise InvariantViolation("Evaluation has unresolved applicable conflict")
        if effective_use.arbitration_ambiguous:
            raise InvariantViolation("Evaluation terminal arbitration is ambiguous")
        if effective_use.invalidation_ids:
            raise InvariantViolation("Evaluation is invalidated and unusable")
        if observation.observed_state is EvaluationState.COMPLETED:
            if not (
                effective_use.original_judgement == effective_use.effective_judgement
                and not effective_use.applicable_conflicts
                and not effective_use.unresolved_conflicts
                and not effective_use.supporting_arbitration_ids
                and effective_use.terminal_arbitration_id is None
                and not effective_use.arbitration_ambiguous
            ):
                raise InvariantViolation(
                    "COMPLETED Evaluation effective-use provenance is inconsistent"
                )
        else:
            if not (
                effective_use.supporting_arbitration_ids
                and effective_use.terminal_arbitration_id is not None
                and not effective_use.arbitration_ambiguous
                and not effective_use.unresolved_conflicts
            ):
                raise InvariantViolation(
                    "ARBITRATED Evaluation effective-use provenance is inconsistent"
                )

        disposition = (
            OutcomeDisposition.ACCEPTED
            if target_state is OutcomeState.ACCEPTED
            else OutcomeDisposition.REJECTED
        )
        policy = semantics.policy_decision
        if not (
            policy.status is OutcomeSemanticDecisionStatus.PASSED
            and policy.decided_by.actor_type is ActorType.POLICY_ENGINE
            and policy.decided_by.actor_id != outcome.producer.actor_id
            and policy.validation_lineage == lineage
            and policy.evaluation_id == observation.evaluation_id
            and policy.observed_evaluation_version
            == observation.observed_evaluation_version
            and policy.effective_judgement == effective_use.effective_judgement
            and policy.disposition is disposition
        ):
            raise InvariantViolation(
                "Outcome disposition-policy decision is not exact, current, and passed"
            )

        human = semantics.human_acceptance
        if disposition is OutcomeDisposition.REJECTED:
            if human is not None:
                raise InvariantViolation(
                    "Human acceptance cannot authorize an Outcome rejection"
                )
            return
        if policy.human_acceptance_required and human is None:
            raise InvariantViolation("Required human acceptance is missing")
        if human is None:
            return
        if not (
            human.affirmative
            and human.decided_by.actor_type is ActorType.HUMAN_OPERATOR
            and human.decided_by.actor_id != outcome.producer.actor_id
            and human.validation_lineage == lineage
            and human.evaluation_id == observation.evaluation_id
            and human.observed_evaluation_version
            == observation.observed_evaluation_version
            and human.effective_judgement == effective_use.effective_judgement
            and human.disposition is OutcomeDisposition.ACCEPTED
            and human.policy_ref == policy.policy_ref
            and human.policy_decision_ref == policy.decision_ref
        ):
            raise InvariantViolation(
                "Human acceptance is not affirmative and exact-bound"
            )

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
        if (
            observation.verifier is not None
            and observation.verifier.actor_id == outcome.producer.actor_id
        ):
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
