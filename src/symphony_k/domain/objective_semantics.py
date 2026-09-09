"""Canonical Objective-only semantic inputs for lifecycle transitions.

These immutable records consume decisions already made outside the domain kernel.
They do not evaluate policy, load evidence, inspect children, persist records, or
read a clock.
"""

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Final

from .actors import ActorIdentity
from .candidate_refs import EvidenceRef
from .completion import CompletionPolicyRef
from .errors import (
    CompletionPolicyNotSatisfied,
    InvalidDomainValue,
    InvariantViolation,
)
from .ids import CorrelationId, ObjectiveId
from .objective import Objective, ObjectiveState
from .time import Timestamp
from .version import EntityVersion


class ObjectiveSemanticDecisionStatus(Enum):
    """Closed result vocabulary for an already-made semantic decision."""

    PASSED = "PASSED"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


class ObjectiveCompletionBlockerStatus(Enum):
    """Explicit completion-blocker disposition; absence is not resolution."""

    CLEARED = "CLEARED"
    LAWFULLY_WAIVED = "LAWFULLY_WAIVED"
    BLOCKED = "BLOCKED"
    UNRESOLVED = "UNRESOLVED"


class ObjectiveExtensionCoverageStatus(Enum):
    """Result of reviewing recorded validity extensions for the exact snapshot."""

    NO_COVERING_EXTENSION = "NO_COVERING_EXTENSION"
    COVERED = "COVERED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class ObjectiveSemanticDecisionRef:
    """Opaque identity of a semantic decision; it does not evaluate that decision."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Objective semantic decision reference must contain non-whitespace text"
            )


def _require_evidence(evidence_refs: frozenset[EvidenceRef]) -> None:
    if not isinstance(evidence_refs, frozenset) or not evidence_refs:
        raise InvalidDomainValue("Semantic decisions require evidence references")
    if any(not isinstance(reference, EvidenceRef) for reference in evidence_refs):
        raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")


@dataclass(frozen=True, slots=True)
class _EvidenceBackedObjectiveDecision:
    decision_ref: ObjectiveSemanticDecisionRef
    status: ObjectiveSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, ObjectiveSemanticDecisionRef):
            raise InvalidDomainValue(
                "decision_ref must be an ObjectiveSemanticDecisionRef"
            )
        if not isinstance(self.status, ObjectiveSemanticDecisionStatus):
            raise InvalidDomainValue(
                "status must be an ObjectiveSemanticDecisionStatus"
            )
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)


@dataclass(frozen=True, slots=True)
class ObjectiveGovernanceApprovalDecision(_EvidenceBackedObjectiveDecision):
    pass


@dataclass(frozen=True, slots=True)
class ObjectiveBudgetValidityDecision(_EvidenceBackedObjectiveDecision):
    pass


@dataclass(frozen=True, slots=True)
class ObjectivePermissionValidityDecision(_EvidenceBackedObjectiveDecision):
    pass


@dataclass(frozen=True, slots=True)
class ObjectiveTimeHorizonValidityDecision(_EvidenceBackedObjectiveDecision):
    pass


@dataclass(frozen=True, slots=True)
class ObjectiveValidityDecision(_EvidenceBackedObjectiveDecision):
    pass


@dataclass(frozen=True, slots=True)
class ObjectiveCurrentBlockerDecision(_EvidenceBackedObjectiveDecision):
    pass


@dataclass(frozen=True, slots=True)
class ObjectiveBlockerResolutionDecision(_EvidenceBackedObjectiveDecision):
    pass


@dataclass(frozen=True, slots=True)
class ObjectiveEvidenceIndependenceDecision(_EvidenceBackedObjectiveDecision):
    pass


@dataclass(frozen=True, slots=True)
class ObjectiveInabilityDecision(_EvidenceBackedObjectiveDecision):
    pass


@dataclass(frozen=True, slots=True)
class ObjectiveTerminationDecision(_EvidenceBackedObjectiveDecision):
    pass


@dataclass(frozen=True, slots=True)
class ObjectiveArchivalDecision(_EvidenceBackedObjectiveDecision):
    pass


@dataclass(frozen=True, slots=True)
class ObjectiveCompletionPolicyDecision(_EvidenceBackedObjectiveDecision):
    completion_policy_ref: CompletionPolicyRef

    def __post_init__(self) -> None:
        super(ObjectiveCompletionPolicyDecision, self).__post_init__()
        if not isinstance(self.completion_policy_ref, CompletionPolicyRef):
            raise InvalidDomainValue(
                "completion_policy_ref must be a CompletionPolicyRef"
            )


@dataclass(frozen=True, slots=True)
class ObjectiveAcceptanceDecision(_EvidenceBackedObjectiveDecision):
    accepting_authority: ActorIdentity

    def __post_init__(self) -> None:
        super(ObjectiveAcceptanceDecision, self).__post_init__()
        if not isinstance(self.accepting_authority, ActorIdentity):
            raise InvalidDomainValue("accepting_authority must be an ActorIdentity")
        if self.accepting_authority != self.decided_by:
            raise InvalidDomainValue(
                "accepting_authority must be the principal who made the decision"
            )


@dataclass(frozen=True, slots=True)
class ObjectiveCompletionBlockerDecision:
    decision_ref: ObjectiveSemanticDecisionRef
    status: ObjectiveCompletionBlockerStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    waiver_policy_ref: CompletionPolicyRef | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, ObjectiveSemanticDecisionRef):
            raise InvalidDomainValue(
                "decision_ref must be an ObjectiveSemanticDecisionRef"
            )
        if not isinstance(self.status, ObjectiveCompletionBlockerStatus):
            raise InvalidDomainValue(
                "status must be an ObjectiveCompletionBlockerStatus"
            )
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)
        if self.status is ObjectiveCompletionBlockerStatus.LAWFULLY_WAIVED:
            if not isinstance(self.waiver_policy_ref, CompletionPolicyRef):
                raise InvalidDomainValue(
                    "A lawful completion-blocker waiver requires its policy reference"
                )
        elif self.waiver_policy_ref is not None:
            raise InvalidDomainValue(
                "waiver_policy_ref is valid only for a lawful waiver"
            )


@dataclass(frozen=True, slots=True)
class ObjectiveExtensionCoverageDecision:
    decision_ref: ObjectiveSemanticDecisionRef
    status: ObjectiveExtensionCoverageStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, ObjectiveSemanticDecisionRef):
            raise InvalidDomainValue(
                "decision_ref must be an ObjectiveSemanticDecisionRef"
            )
        if not isinstance(self.status, ObjectiveExtensionCoverageStatus):
            raise InvalidDomainValue(
                "status must be an ObjectiveExtensionCoverageStatus"
            )
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)


@dataclass(frozen=True, slots=True)
class ObjectiveActivationSemantics:
    governance: ObjectiveGovernanceApprovalDecision
    budget: ObjectiveBudgetValidityDecision
    permissions: ObjectivePermissionValidityDecision
    time_horizon: ObjectiveTimeHorizonValidityDecision

    def __post_init__(self) -> None:
        expected = (
            (self.governance, ObjectiveGovernanceApprovalDecision, "governance"),
            (self.budget, ObjectiveBudgetValidityDecision, "budget"),
            (self.permissions, ObjectivePermissionValidityDecision, "permissions"),
            (
                self.time_horizon,
                ObjectiveTimeHorizonValidityDecision,
                "time_horizon",
            ),
        )
        for value, decision_type, name in expected:
            if not isinstance(value, decision_type):
                raise InvalidDomainValue(f"{name} has the wrong decision type")


@dataclass(frozen=True, slots=True)
class ObjectiveBlockingSemantics:
    blocker: ObjectiveCurrentBlockerDecision
    objective_validity: ObjectiveValidityDecision

    def __post_init__(self) -> None:
        if not isinstance(self.blocker, ObjectiveCurrentBlockerDecision):
            raise InvalidDomainValue(
                "blocker must be an ObjectiveCurrentBlockerDecision"
            )
        if not isinstance(self.objective_validity, ObjectiveValidityDecision):
            raise InvalidDomainValue(
                "objective_validity must be an ObjectiveValidityDecision"
            )


@dataclass(frozen=True, slots=True)
class ObjectiveReactivationSemantics:
    blocker_resolution: ObjectiveBlockerResolutionDecision
    activation: ObjectiveActivationSemantics

    def __post_init__(self) -> None:
        if not isinstance(self.blocker_resolution, ObjectiveBlockerResolutionDecision):
            raise InvalidDomainValue(
                "blocker_resolution must be an ObjectiveBlockerResolutionDecision"
            )
        if not isinstance(self.activation, ObjectiveActivationSemantics):
            raise InvalidDomainValue("activation must be ObjectiveActivationSemantics")


@dataclass(frozen=True, slots=True)
class ObjectiveSatisfactionSemantics:
    completion_policy: ObjectiveCompletionPolicyDecision
    evidence_independence: ObjectiveEvidenceIndependenceDecision
    acceptance: ObjectiveAcceptanceDecision
    completion_blockers: ObjectiveCompletionBlockerDecision

    def __post_init__(self) -> None:
        expected = (
            (
                self.completion_policy,
                ObjectiveCompletionPolicyDecision,
                "completion_policy",
            ),
            (
                self.evidence_independence,
                ObjectiveEvidenceIndependenceDecision,
                "evidence_independence",
            ),
            (self.acceptance, ObjectiveAcceptanceDecision, "acceptance"),
            (
                self.completion_blockers,
                ObjectiveCompletionBlockerDecision,
                "completion_blockers",
            ),
        )
        for value, decision_type, name in expected:
            if not isinstance(value, decision_type):
                raise InvalidDomainValue(f"{name} has the wrong decision type")


@dataclass(frozen=True, slots=True)
class ObjectiveFailureSemantics:
    inability: ObjectiveInabilityDecision

    def __post_init__(self) -> None:
        if not isinstance(self.inability, ObjectiveInabilityDecision):
            raise InvalidDomainValue("inability must be an ObjectiveInabilityDecision")


@dataclass(frozen=True, slots=True)
class ObjectiveCancellationSemantics:
    termination: ObjectiveTerminationDecision

    def __post_init__(self) -> None:
        if not isinstance(self.termination, ObjectiveTerminationDecision):
            raise InvalidDomainValue(
                "termination must be an ObjectiveTerminationDecision"
            )


@dataclass(frozen=True, slots=True)
class ObjectiveExpirySemantics:
    extension_coverage: ObjectiveExtensionCoverageDecision

    def __post_init__(self) -> None:
        if not isinstance(self.extension_coverage, ObjectiveExtensionCoverageDecision):
            raise InvalidDomainValue(
                "extension_coverage must be an ObjectiveExtensionCoverageDecision"
            )


@dataclass(frozen=True, slots=True)
class ObjectiveArchivalSemantics:
    archival: ObjectiveArchivalDecision

    def __post_init__(self) -> None:
        if not isinstance(self.archival, ObjectiveArchivalDecision):
            raise InvalidDomainValue("archival must be an ObjectiveArchivalDecision")


type ObjectiveSemanticInput = (
    ObjectiveActivationSemantics
    | ObjectiveBlockingSemantics
    | ObjectiveReactivationSemantics
    | ObjectiveSatisfactionSemantics
    | ObjectiveFailureSemantics
    | ObjectiveCancellationSemantics
    | ObjectiveExpirySemantics
    | ObjectiveArchivalSemantics
)


_INPUT_TYPE_BY_EDGE: Final[
    MappingProxyType[
        tuple[ObjectiveState, ObjectiveState], type[ObjectiveSemanticInput]
    ]
] = MappingProxyType(
    {
        (ObjectiveState.DRAFT, ObjectiveState.ACTIVE): ObjectiveActivationSemantics,
        (ObjectiveState.ACTIVE, ObjectiveState.BLOCKED): ObjectiveBlockingSemantics,
        (ObjectiveState.BLOCKED, ObjectiveState.ACTIVE): ObjectiveReactivationSemantics,
        (
            ObjectiveState.ACTIVE,
            ObjectiveState.SATISFIED,
        ): ObjectiveSatisfactionSemantics,
        (
            ObjectiveState.BLOCKED,
            ObjectiveState.SATISFIED,
        ): ObjectiveSatisfactionSemantics,
        (ObjectiveState.ACTIVE, ObjectiveState.FAILED): ObjectiveFailureSemantics,
        (ObjectiveState.BLOCKED, ObjectiveState.FAILED): ObjectiveFailureSemantics,
        (
            ObjectiveState.DRAFT,
            ObjectiveState.CANCELLED,
        ): ObjectiveCancellationSemantics,
        (
            ObjectiveState.ACTIVE,
            ObjectiveState.CANCELLED,
        ): ObjectiveCancellationSemantics,
        (
            ObjectiveState.BLOCKED,
            ObjectiveState.CANCELLED,
        ): ObjectiveCancellationSemantics,
        (ObjectiveState.DRAFT, ObjectiveState.EXPIRED): ObjectiveExpirySemantics,
        (ObjectiveState.ACTIVE, ObjectiveState.EXPIRED): ObjectiveExpirySemantics,
        (ObjectiveState.BLOCKED, ObjectiveState.EXPIRED): ObjectiveExpirySemantics,
        (ObjectiveState.SATISFIED, ObjectiveState.ARCHIVED): ObjectiveArchivalSemantics,
        (ObjectiveState.FAILED, ObjectiveState.ARCHIVED): ObjectiveArchivalSemantics,
        (ObjectiveState.CANCELLED, ObjectiveState.ARCHIVED): ObjectiveArchivalSemantics,
        (ObjectiveState.EXPIRED, ObjectiveState.ARCHIVED): ObjectiveArchivalSemantics,
    }
)


def _require_passed(decision: _EvidenceBackedObjectiveDecision, condition: str) -> None:
    if decision.status is not ObjectiveSemanticDecisionStatus.PASSED:
        raise InvariantViolation(
            f"Objective semantic condition is not satisfied: {condition}"
        )


@dataclass(frozen=True, slots=True)
class ObjectiveSemanticGuard:
    """Canonical guard for one exact Objective snapshot transition attempt."""

    objective_id: ObjectiveId
    observed_entity_version: EntityVersion
    prior_state: ObjectiveState
    target_state: ObjectiveState
    correlation_id: CorrelationId
    semantic_input: ObjectiveSemanticInput

    def __post_init__(self) -> None:
        if not isinstance(self.objective_id, ObjectiveId):
            raise InvalidDomainValue("objective_id must be an ObjectiveId")
        if not isinstance(self.observed_entity_version, EntityVersion):
            raise InvalidDomainValue("observed_entity_version must be an EntityVersion")
        if not isinstance(self.prior_state, ObjectiveState) or not isinstance(
            self.target_state, ObjectiveState
        ):
            raise InvalidDomainValue(
                "prior_state and target_state must be ObjectiveState"
            )
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        expected = _INPUT_TYPE_BY_EDGE.get((self.prior_state, self.target_state))
        if expected is None or not isinstance(self.semantic_input, expected):
            raise InvalidDomainValue(
                "semantic_input must match a canonical Objective lifecycle edge"
            )

    def validate(
        self,
        objective: Objective,
        target_state: ObjectiveState,
        request_timestamp: Timestamp,
        correlation_id: CorrelationId,
    ) -> None:
        """Validate exact binding and the accepted edge-specific semantics."""
        if not isinstance(objective, Objective):
            raise InvalidDomainValue("objective must be an Objective")
        if not isinstance(target_state, ObjectiveState):
            raise InvalidDomainValue("target_state must be an ObjectiveState")
        if not isinstance(request_timestamp, Timestamp):
            raise InvalidDomainValue("request_timestamp must be a Timestamp")
        if not isinstance(correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if not (
            self.objective_id == objective.objective_id
            and self.observed_entity_version == objective.version
            and self.prior_state is objective.state
            and self.target_state is target_state
            and self.correlation_id == correlation_id
        ):
            raise InvariantViolation(
                "Objective semantic guard does not match the exact request snapshot"
            )

        semantics = self.semantic_input
        if isinstance(semantics, ObjectiveActivationSemantics):
            self._validate_activation(objective, request_timestamp, semantics)
        elif isinstance(semantics, ObjectiveBlockingSemantics):
            _require_passed(semantics.blocker, "explicit current blocker")
            _require_passed(semantics.objective_validity, "Objective remains valid")
            self._require_unexpired(objective, request_timestamp)
        elif isinstance(semantics, ObjectiveReactivationSemantics):
            _require_passed(
                semantics.blocker_resolution, "all blocking conditions resolved"
            )
            self._validate_activation(
                objective, request_timestamp, semantics.activation
            )
        elif isinstance(semantics, ObjectiveSatisfactionSemantics):
            self._validate_satisfaction(objective, semantics)
        elif isinstance(semantics, ObjectiveFailureSemantics):
            _require_passed(
                semantics.inability,
                "goal cannot be achieved under accepted constraints",
            )
        elif isinstance(semantics, ObjectiveCancellationSemantics):
            _require_passed(semantics.termination, "explicit termination decision")
        elif isinstance(semantics, ObjectiveExpirySemantics):
            self._validate_expiry(objective, request_timestamp, semantics)
        else:
            _require_passed(semantics.archival, "explicit archival decision")

    @staticmethod
    def _require_unexpired(objective: Objective, request_timestamp: Timestamp) -> None:
        if (
            objective.valid_until is not None
            and request_timestamp.value >= objective.valid_until.value
        ):
            raise InvariantViolation("Objective validity horizon has elapsed")

    def _validate_activation(
        self,
        objective: Objective,
        request_timestamp: Timestamp,
        semantics: ObjectiveActivationSemantics,
    ) -> None:
        _require_passed(semantics.governance, "definition and governance approval")
        _require_passed(semantics.budget, "applicable budget validity")
        _require_passed(semantics.permissions, "applicable permission validity")
        _require_passed(semantics.time_horizon, "applicable time-horizon validity")
        self._require_unexpired(objective, request_timestamp)

    @staticmethod
    def _validate_satisfaction(
        objective: Objective, semantics: ObjectiveSatisfactionSemantics
    ) -> None:
        if semantics.completion_policy.completion_policy_ref != (
            objective.completion_policy_ref
        ):
            raise CompletionPolicyNotSatisfied(
                "Completion decision does not use the current CompletionPolicyRef"
            )
        if (
            semantics.completion_policy.status
            is not ObjectiveSemanticDecisionStatus.PASSED
        ):
            raise CompletionPolicyNotSatisfied(
                "Current Objective completion policy is not satisfied"
            )
        _require_passed(
            semantics.evidence_independence, "independent completion evidence"
        )
        _require_passed(semantics.acceptance, "explicit designated acceptance")
        if not (
            semantics.acceptance.decided_by == objective.acceptance_authority
            and semantics.acceptance.accepting_authority
            == objective.acceptance_authority
        ):
            raise InvariantViolation(
                "Acceptance decision is not from the designated acceptance authority"
            )
        blockers = semantics.completion_blockers
        if blockers.status is ObjectiveCompletionBlockerStatus.CLEARED:
            return
        if blockers.status is ObjectiveCompletionBlockerStatus.LAWFULLY_WAIVED:
            if blockers.waiver_policy_ref != objective.completion_policy_ref:
                raise CompletionPolicyNotSatisfied(
                    "Completion-blocker waiver is not scoped to the current policy"
                )
            return
        raise CompletionPolicyNotSatisfied(
            "Completion blockers are not resolved or lawfully waived"
        )

    @staticmethod
    def _validate_expiry(
        objective: Objective,
        request_timestamp: Timestamp,
        semantics: ObjectiveExpirySemantics,
    ) -> None:
        if objective.valid_until is None:
            raise InvariantViolation("Objective has no validity horizon")
        if request_timestamp.value < objective.valid_until.value:
            raise InvariantViolation("Objective validity horizon has not elapsed")
        if (
            semantics.extension_coverage.status
            is not ObjectiveExtensionCoverageStatus.NO_COVERING_EXTENSION
        ):
            raise InvariantViolation(
                "A covering extension exists or extension coverage is unresolved"
            )
