"""Typed semantic evidence for Objective and Task authoritative creation.

These records are pure, immutable inputs.  They retain exact request bindings
and stable evidence references, but they do not load repositories or turn an
observation into an M8 authoritative fact.
"""

from dataclasses import dataclass
from enum import Enum

from .actors import ActorIdentity, ActorType
from .candidate_refs import EvidenceRef
from .completion import CompletionPolicyRef
from .errors import InvalidDomainValue
from .ids import CausationId, CorrelationId, ObjectiveId, TaskId
from .objective import ObjectiveState
from .time import Timestamp
from .version import EntityVersion


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InvalidDomainValue(f"{field} must contain non-whitespace text")


def _require_evidence(value: frozenset[EvidenceRef]) -> None:
    if (
        not isinstance(value, frozenset)
        or not value
        or any(not isinstance(item, EvidenceRef) for item in value)
    ):
        raise InvalidDomainValue("evidence_refs must be a nonempty EvidenceRef set")


@dataclass(frozen=True, slots=True)
class _StableRef:
    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, "reference")


@dataclass(frozen=True, slots=True)
class ObjectiveCreationDecisionRef(_StableRef):
    """Stable identity of one Objective creation semantic decision."""


@dataclass(frozen=True, slots=True)
class TaskCreationDecisionRef(_StableRef):
    """Stable identity of one Task creation semantic decision."""


@dataclass(frozen=True, slots=True)
class TaskObjectiveObservationRef(_StableRef):
    """Stable identity of one Task-to-Objective relationship observation."""


class CreationSemanticDecisionStatus(Enum):
    PASSED = "PASSED"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


class TaskObjectiveObservationStatus(Enum):
    CURRENT = "CURRENT"
    MISSING = "MISSING"
    STALE = "STALE"
    UNRESOLVED = "UNRESOLVED"


class TaskObjectiveRelationship(Enum):
    PRIMARY = "PRIMARY"
    CONTRIBUTION = "CONTRIBUTION"


def _require_common_decision_fields(
    status: CreationSemanticDecisionStatus,
    decided_by: ActorIdentity,
    evidence_refs: frozenset[EvidenceRef],
    causation_id: CausationId,
    correlation_id: CorrelationId,
) -> None:
    if not isinstance(status, CreationSemanticDecisionStatus):
        raise InvalidDomainValue("status must be a CreationSemanticDecisionStatus")
    if not isinstance(decided_by, ActorIdentity):
        raise InvalidDomainValue("decided_by must be an ActorIdentity")
    if decided_by.actor_type in {ActorType.REQUESTER, ActorType.WORKER}:
        raise InvalidDomainValue("creation semantics require an independent decider")
    _require_evidence(evidence_refs)
    if not isinstance(causation_id, CausationId):
        raise InvalidDomainValue("request_causation_id must be a CausationId")
    if not isinstance(correlation_id, CorrelationId):
        raise InvalidDomainValue("correlation_id must be a CorrelationId")


@dataclass(frozen=True, slots=True)
class ObjectiveBoundedGoalDecision:
    decision_ref: ObjectiveCreationDecisionRef
    status: CreationSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    objective_id: ObjectiveId
    goal: str
    request_causation_id: CausationId
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, ObjectiveCreationDecisionRef):
            raise InvalidDomainValue("decision_ref has the wrong Objective type")
        _require_common_decision_fields(
            self.status,
            self.decided_by,
            self.evidence_refs,
            self.request_causation_id,
            self.correlation_id,
        )
        if not isinstance(self.objective_id, ObjectiveId):
            raise InvalidDomainValue("objective_id must be an ObjectiveId")
        _require_text(self.goal, "goal")


@dataclass(frozen=True, slots=True)
class ObjectiveAcceptanceBindingDecision:
    decision_ref: ObjectiveCreationDecisionRef
    status: CreationSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    objective_id: ObjectiveId
    goal: str
    acceptance_criteria: tuple[str, ...]
    acceptance_authority: ActorIdentity
    request_causation_id: CausationId
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, ObjectiveCreationDecisionRef):
            raise InvalidDomainValue("decision_ref has the wrong Objective type")
        _require_common_decision_fields(
            self.status,
            self.decided_by,
            self.evidence_refs,
            self.request_causation_id,
            self.correlation_id,
        )
        if not isinstance(self.objective_id, ObjectiveId):
            raise InvalidDomainValue("objective_id must be an ObjectiveId")
        _require_text(self.goal, "goal")
        if (
            not isinstance(self.acceptance_criteria, tuple)
            or not self.acceptance_criteria
            or any(
                not isinstance(item, str) or not item.strip()
                for item in self.acceptance_criteria
            )
        ):
            raise InvalidDomainValue(
                "acceptance_criteria must be a nonempty text tuple"
            )
        if not isinstance(self.acceptance_authority, ActorIdentity):
            raise InvalidDomainValue("acceptance_authority must be an ActorIdentity")


@dataclass(frozen=True, slots=True)
class ObjectiveCreationCompletionPolicyDecision:
    decision_ref: ObjectiveCreationDecisionRef
    status: CreationSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    objective_id: ObjectiveId
    completion_policy_ref: CompletionPolicyRef
    request_causation_id: CausationId
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, ObjectiveCreationDecisionRef):
            raise InvalidDomainValue("decision_ref has the wrong Objective type")
        _require_common_decision_fields(
            self.status,
            self.decided_by,
            self.evidence_refs,
            self.request_causation_id,
            self.correlation_id,
        )
        if not isinstance(self.objective_id, ObjectiveId):
            raise InvalidDomainValue("objective_id must be an ObjectiveId")
        if not isinstance(self.completion_policy_ref, CompletionPolicyRef):
            raise InvalidDomainValue(
                "completion_policy_ref must be a CompletionPolicyRef"
            )


@dataclass(frozen=True, slots=True)
class TaskBoundedDefinitionDecision:
    decision_ref: TaskCreationDecisionRef
    status: CreationSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    task_id: TaskId
    definition: str
    request_causation_id: CausationId
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, TaskCreationDecisionRef):
            raise InvalidDomainValue("decision_ref has the wrong Task type")
        _require_common_decision_fields(
            self.status,
            self.decided_by,
            self.evidence_refs,
            self.request_causation_id,
            self.correlation_id,
        )
        if not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId")
        _require_text(self.definition, "definition")


@dataclass(frozen=True, slots=True)
class TaskCreationCompletionPolicyDecision:
    decision_ref: TaskCreationDecisionRef
    status: CreationSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    task_id: TaskId
    completion_policy_ref: CompletionPolicyRef
    request_causation_id: CausationId
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, TaskCreationDecisionRef):
            raise InvalidDomainValue("decision_ref has the wrong Task type")
        _require_common_decision_fields(
            self.status,
            self.decided_by,
            self.evidence_refs,
            self.request_causation_id,
            self.correlation_id,
        )
        if not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId")
        if not isinstance(self.completion_policy_ref, CompletionPolicyRef):
            raise InvalidDomainValue(
                "completion_policy_ref must be a CompletionPolicyRef"
            )


@dataclass(frozen=True, slots=True)
class TaskObjectiveObservation:
    observation_ref: TaskObjectiveObservationRef
    status: TaskObjectiveObservationStatus
    observed_by: ActorIdentity
    observed_at: Timestamp
    evidence_refs: frozenset[EvidenceRef]
    task_id: TaskId
    objective_id: ObjectiveId
    relationship: TaskObjectiveRelationship
    request_causation_id: CausationId
    correlation_id: CorrelationId
    observed_entity_version: EntityVersion | None = None
    observed_state: ObjectiveState | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.observation_ref, TaskObjectiveObservationRef):
            raise InvalidDomainValue("observation_ref has the wrong relationship type")
        if not isinstance(self.status, TaskObjectiveObservationStatus):
            raise InvalidDomainValue("status must be a TaskObjectiveObservationStatus")
        if not isinstance(self.observed_by, ActorIdentity):
            raise InvalidDomainValue("observed_by must be an ActorIdentity")
        if self.observed_by.actor_type in {ActorType.REQUESTER, ActorType.WORKER}:
            raise InvalidDomainValue("relationship must be observed independently")
        if not isinstance(self.observed_at, Timestamp):
            raise InvalidDomainValue("observed_at must be a Timestamp")
        _require_evidence(self.evidence_refs)
        if not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId")
        if not isinstance(self.objective_id, ObjectiveId):
            raise InvalidDomainValue("objective_id must be an ObjectiveId")
        if not isinstance(self.relationship, TaskObjectiveRelationship):
            raise InvalidDomainValue("relationship has the wrong type")
        if not isinstance(self.request_causation_id, CausationId):
            raise InvalidDomainValue("request_causation_id must be a CausationId")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        has_snapshot = (
            self.observed_entity_version is not None or self.observed_state is not None
        )
        if self.status in {
            TaskObjectiveObservationStatus.CURRENT,
            TaskObjectiveObservationStatus.STALE,
        }:
            if not isinstance(
                self.observed_entity_version, EntityVersion
            ) or not isinstance(self.observed_state, ObjectiveState):
                raise InvalidDomainValue(
                    "CURRENT and STALE observations require Objective version and state"
                )
        elif has_snapshot:
            raise InvalidDomainValue(
                "MISSING and UNRESOLVED observations cannot claim a snapshot"
            )
