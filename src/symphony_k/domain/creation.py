"""Authoritative lifecycle creation protocol.

M7D1 defines the shared request, authority, availability, and result records.
M7D2 and M7D3 add Objective, Task, Run, Outcome and Evaluation creation.
Planned Effect creation records intent; observed Effect variants remain closed.
There is no repository,
transaction, executor, or
call to the transition engine's existing-snapshot operation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final, Protocol, overload, runtime_checkable

from .actors import ActorIdentity, ActorType
from .candidate_refs import ArtifactRef, EvidenceRef
from .completion import CompletionPolicyRef
from .creation_effect_semantics import (
    PlannedEffectIntentDecision,
    PlannedEffectIntentScope,
    planned_effect_annotations,
    validate_planned_effect_creation,
)
from .creation_run_outcome_evaluation import (
    EvaluationRequestDecision,
    EvaluationRequestScope,
    OutcomeProposalDecision,
    OutcomeProposalScope,
    RunRegistrationDecision,
    RunRegistrationScope,
    creation_scope_annotations,
    validate_evaluation_creation,
    validate_outcome_creation,
    validate_run_creation,
)
from .creation_semantics import (
    CreationSemanticDecisionStatus,
    ObjectiveAcceptanceBindingDecision,
    ObjectiveBoundedGoalDecision,
    ObjectiveCreationCompletionPolicyDecision,
    TaskBoundedDefinitionDecision,
    TaskCreationCompletionPolicyDecision,
    TaskObjectiveObservation,
    TaskObjectiveObservationStatus,
    TaskObjectiveRelationship,
)
from .effect import (
    Effect,
    EffectPayloadRef,
    EffectState,
    EffectTargetRef,
    ObservedEffectOrigin,
    PlannedEffectOrigin,
)
from .errors import (
    EntityNotFound,
    InvalidDomainValue,
    InvalidRelationship,
    InvariantViolation,
    UnauthorizedTransition,
)
from .evaluation import Evaluation, EvaluationState
from .evaluation_result import EvaluationMethodRef
from .evaluation_target import EvaluationTargetRef
from .execution_profile import ExecutionProfileRef
from .ids import (
    CausationId,
    CorrelationId,
    CreationAuthorityDecisionId,
    EffectId,
    EvaluationId,
    EventId,
    IdentifierAvailabilityId,
    ObjectiveId,
    OutcomeId,
    RunId,
    TaskId,
)
from .objective import Objective, ObjectiveState
from .outcome import Outcome, OutcomeState
from .run import Run, RunState
from .task import Task, TaskState
from .time import Timestamp
from .transition_engine import (
    DomainEntityType,
    DomainEvent,
    DomainEventMetadata,
    DomainEventType,
    LifecycleEntity,
    LifecycleEntityId,
    LifecycleState,
    is_actor_eligible_for_transition_authority,
)
from .transitions import TransitionReason
from .version import EntityVersion

INITIAL_CREATION_VERSION: Final[EntityVersion] = EntityVersion(1)

type CreationEntitySpec = (
    ObjectiveCreationSpec
    | TaskCreationSpec
    | RunCreationSpec
    | OutcomeCreationSpec
    | EvaluationCreationSpec
    | PlannedEffectCreationSpec
    | ObservedEffectCreationSpec
)


@dataclass(frozen=True, slots=True)
class ObjectiveCreationSpec:
    """Snapshot fields for an Objective creation request, excluding state/version."""

    goal: str
    acceptance_criteria: tuple[str, ...]
    acceptance_authority: ActorIdentity
    completion_policy_ref: CompletionPolicyRef
    valid_until: Timestamp | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.goal, str) or not self.goal.strip():
            raise InvalidDomainValue("goal must contain non-whitespace text")
        if (
            not isinstance(self.acceptance_criteria, tuple)
            or not self.acceptance_criteria
        ):
            raise InvalidDomainValue("acceptance_criteria must be a nonempty tuple")
        if any(
            not isinstance(value, str) or not value.strip()
            for value in self.acceptance_criteria
        ):
            raise InvalidDomainValue(
                "Every acceptance criterion must be non-whitespace text"
            )
        if not isinstance(self.acceptance_authority, ActorIdentity):
            raise InvalidDomainValue("acceptance_authority must be an ActorIdentity")
        if not isinstance(self.completion_policy_ref, CompletionPolicyRef):
            raise InvalidDomainValue(
                "completion_policy_ref must be a CompletionPolicyRef"
            )
        if self.valid_until is not None and not isinstance(self.valid_until, Timestamp):
            raise InvalidDomainValue("valid_until must be a Timestamp or None")


@dataclass(frozen=True, slots=True)
class TaskCreationSpec:
    """Snapshot fields for a Task creation request, excluding state/version."""

    definition: str
    primary_objective_id: ObjectiveId
    completion_policy_ref: CompletionPolicyRef
    contributes_to: frozenset[ObjectiveId] = frozenset()

    def __post_init__(self) -> None:
        if not isinstance(self.definition, str) or not self.definition.strip():
            raise InvalidDomainValue("definition must contain non-whitespace text")
        if not isinstance(self.primary_objective_id, ObjectiveId):
            raise InvalidDomainValue("primary_objective_id must be an ObjectiveId")
        if not isinstance(self.completion_policy_ref, CompletionPolicyRef):
            raise InvalidDomainValue(
                "completion_policy_ref must be a CompletionPolicyRef"
            )
        if not isinstance(self.contributes_to, frozenset) or any(
            not isinstance(value, ObjectiveId) for value in self.contributes_to
        ):
            raise InvalidDomainValue(
                "contributes_to must be a frozenset of ObjectiveId"
            )
        if self.primary_objective_id in self.contributes_to:
            raise InvalidDomainValue("Primary Objective cannot also be a contribution")


@dataclass(frozen=True, slots=True)
class RunCreationSpec:
    """Snapshot fields for a Run creation request, excluding state/version."""

    task_id: TaskId
    execution_profile_ref: ExecutionProfileRef
    predecessor_run_id: RunId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId")
        if not isinstance(self.execution_profile_ref, ExecutionProfileRef):
            raise InvalidDomainValue(
                "execution_profile_ref must be an ExecutionProfileRef"
            )
        if self.predecessor_run_id is not None and not isinstance(
            self.predecessor_run_id, RunId
        ):
            raise InvalidDomainValue("predecessor_run_id must be a RunId or None")


@dataclass(frozen=True, slots=True)
class OutcomeCreationSpec:
    """Snapshot fields for an Outcome creation request, excluding state/version."""

    run_id: RunId
    producer: ActorIdentity
    artifact_refs: frozenset[ArtifactRef]
    evidence_refs: frozenset[EvidenceRef] = frozenset()
    valid_until: Timestamp | None = None
    prior_outcome_id: OutcomeId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.run_id, RunId):
            raise InvalidDomainValue("run_id must be a RunId")
        if not isinstance(self.producer, ActorIdentity):
            raise InvalidDomainValue("producer must be an ActorIdentity")
        if not isinstance(self.artifact_refs, frozenset) or not self.artifact_refs:
            raise InvalidDomainValue("artifact_refs must be a nonempty frozenset")
        if any(not isinstance(value, ArtifactRef) for value in self.artifact_refs):
            raise InvalidDomainValue("Every artifact reference must be an ArtifactRef")
        if not isinstance(self.evidence_refs, frozenset) or any(
            not isinstance(value, EvidenceRef) for value in self.evidence_refs
        ):
            raise InvalidDomainValue("evidence_refs must be a frozenset of EvidenceRef")
        if self.valid_until is not None and not isinstance(self.valid_until, Timestamp):
            raise InvalidDomainValue("valid_until must be a Timestamp or None")
        if self.prior_outcome_id is not None and not isinstance(
            self.prior_outcome_id, OutcomeId
        ):
            raise InvalidDomainValue("prior_outcome_id must be an OutcomeId or None")


@dataclass(frozen=True, slots=True)
class EvaluationCreationSpec:
    """Snapshot fields for an Evaluation creation request, excluding state/version."""

    target: EvaluationTargetRef
    method: EvaluationMethodRef
    verifier: ActorIdentity | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.target, EvaluationTargetRef):
            raise InvalidDomainValue("target must be an EvaluationTargetRef")
        if not isinstance(self.method, EvaluationMethodRef):
            raise InvalidDomainValue("method must be an EvaluationMethodRef")
        if self.verifier is not None and not isinstance(self.verifier, ActorIdentity):
            raise InvalidDomainValue("verifier must be an ActorIdentity or None")


@dataclass(frozen=True, slots=True)
class PlannedEffectCreationSpec:
    """Snapshot fields for planned Effect creation, excluding state/version."""

    origin: PlannedEffectOrigin
    target_ref: EffectTargetRef
    payload_ref: EffectPayloadRef

    def __post_init__(self) -> None:
        if not isinstance(self.origin, PlannedEffectOrigin):
            raise InvalidDomainValue("origin must be a PlannedEffectOrigin")
        if not isinstance(self.target_ref, EffectTargetRef):
            raise InvalidDomainValue("target_ref must be an EffectTargetRef")
        if not isinstance(self.payload_ref, EffectPayloadRef):
            raise InvalidDomainValue("payload_ref must be an EffectPayloadRef")


@dataclass(frozen=True, slots=True)
class ObservedEffectCreationSpec:
    """Snapshot fields for observed Effect creation, excluding state/version."""

    origin: ObservedEffectOrigin
    target_ref: EffectTargetRef
    payload_ref: EffectPayloadRef | None

    def __post_init__(self) -> None:
        if not isinstance(self.origin, ObservedEffectOrigin):
            raise InvalidDomainValue("origin must be an ObservedEffectOrigin")
        if not isinstance(self.target_ref, EffectTargetRef):
            raise InvalidDomainValue("target_ref must be an EffectTargetRef")
        if self.payload_ref is not None and not isinstance(
            self.payload_ref, EffectPayloadRef
        ):
            raise InvalidDomainValue("payload_ref must be an EffectPayloadRef or None")


@dataclass(frozen=True, slots=True)
class _CreationSemanticInput:
    """Typed semantic/provenance handle; M7D2--M7D5 add executable semantics."""

    provenance_ref: CausationId

    def __post_init__(self) -> None:
        if not isinstance(self.provenance_ref, CausationId):
            raise InvalidDomainValue("provenance_ref must be a CausationId")


@dataclass(frozen=True, slots=True)
class ObjectiveCreationSemanticInput(_CreationSemanticInput):
    """Exact semantic decisions required for Objective creation."""

    bounded_goal: ObjectiveBoundedGoalDecision | None = None
    acceptance_binding: ObjectiveAcceptanceBindingDecision | None = None
    completion_policy: ObjectiveCreationCompletionPolicyDecision | None = None

    def __post_init__(self) -> None:
        _CreationSemanticInput.__post_init__(self)
        for value, expected, name in (
            (self.bounded_goal, ObjectiveBoundedGoalDecision, "bounded_goal"),
            (
                self.acceptance_binding,
                ObjectiveAcceptanceBindingDecision,
                "acceptance_binding",
            ),
            (
                self.completion_policy,
                ObjectiveCreationCompletionPolicyDecision,
                "completion_policy",
            ),
        ):
            if value is not None and not isinstance(value, expected):
                raise InvalidDomainValue(f"{name} has the wrong decision type")


@dataclass(frozen=True, slots=True)
class TaskCreationSemanticInput(_CreationSemanticInput):
    """Exact decisions and Objective observations required for Task creation."""

    bounded_definition: TaskBoundedDefinitionDecision | None = None
    completion_policy: TaskCreationCompletionPolicyDecision | None = None
    objective_observations: tuple[TaskObjectiveObservation, ...] | None = None

    def __post_init__(self) -> None:
        _CreationSemanticInput.__post_init__(self)
        if self.bounded_definition is not None and not isinstance(
            self.bounded_definition, TaskBoundedDefinitionDecision
        ):
            raise InvalidDomainValue("bounded_definition has the wrong decision type")
        if self.completion_policy is not None and not isinstance(
            self.completion_policy, TaskCreationCompletionPolicyDecision
        ):
            raise InvalidDomainValue("completion_policy has the wrong decision type")
        if self.objective_observations is not None and (
            not isinstance(self.objective_observations, tuple)
            or any(
                not isinstance(value, TaskObjectiveObservation)
                for value in self.objective_observations
            )
        ):
            raise InvalidDomainValue(
                "objective_observations must be a tuple of TaskObjectiveObservation"
            )


@dataclass(frozen=True, slots=True)
class RunCreationSemanticInput(_CreationSemanticInput):
    """Exact independently evidenced attempt registration."""

    registration: RunRegistrationScope | None = None
    decision: RunRegistrationDecision | None = None

    def __post_init__(self) -> None:
        _CreationSemanticInput.__post_init__(self)
        if self.registration is not None and not isinstance(
            self.registration, RunRegistrationScope
        ):
            raise InvalidDomainValue("Invalid Run registration scope")
        if self.decision is not None and not isinstance(
            self.decision, RunRegistrationDecision
        ):
            raise InvalidDomainValue("Invalid Run registration decision")


@dataclass(frozen=True, slots=True)
class OutcomeCreationSemanticInput(_CreationSemanticInput):
    """Exact independently evidenced candidate proposal; never acceptance."""

    proposal: OutcomeProposalScope | None = None
    decision: OutcomeProposalDecision | None = None

    def __post_init__(self) -> None:
        _CreationSemanticInput.__post_init__(self)
        if self.proposal is not None and not isinstance(
            self.proposal, OutcomeProposalScope
        ):
            raise InvalidDomainValue("Invalid Outcome proposal scope")
        if self.decision is not None and not isinstance(
            self.decision, OutcomeProposalDecision
        ):
            raise InvalidDomainValue("Invalid Outcome proposal decision")


@dataclass(frozen=True, slots=True)
class EvaluationCreationSemanticInput(_CreationSemanticInput):
    """Exact independently evidenced validation request; never a verdict."""

    validation: EvaluationRequestScope | None = None
    decision: EvaluationRequestDecision | None = None

    def __post_init__(self) -> None:
        _CreationSemanticInput.__post_init__(self)
        if self.validation is not None and not isinstance(
            self.validation, EvaluationRequestScope
        ):
            raise InvalidDomainValue("Invalid Evaluation request scope")
        if self.decision is not None and not isinstance(
            self.decision, EvaluationRequestDecision
        ):
            raise InvalidDomainValue("Invalid Evaluation request decision")


@dataclass(frozen=True, slots=True)
class PlannedEffectCreationSemanticInput(_CreationSemanticInput):
    """Exact governed intent evidence, never execution authorization."""

    intent: PlannedEffectIntentScope | None = None
    decision: PlannedEffectIntentDecision | None = None

    def __post_init__(self) -> None:
        _CreationSemanticInput.__post_init__(self)
        if self.intent is not None and not isinstance(
            self.intent, PlannedEffectIntentScope
        ):
            raise InvalidDomainValue("Invalid planned Effect intent")
        if self.decision is not None and not isinstance(
            self.decision, PlannedEffectIntentDecision
        ):
            raise InvalidDomainValue("Invalid planned Effect intent decision")


@dataclass(frozen=True, slots=True)
class ObservedEffectCreationSemanticInput(_CreationSemanticInput):
    """Reserved typed input for M7D5 observed Effect creation semantics."""


type CreationSemanticInput = (
    ObjectiveCreationSemanticInput
    | TaskCreationSemanticInput
    | RunCreationSemanticInput
    | OutcomeCreationSemanticInput
    | EvaluationCreationSemanticInput
    | PlannedEffectCreationSemanticInput
    | ObservedEffectCreationSemanticInput
)


class CreationRequestVariant(Enum):
    """Exactly the eight accepted absent-to-state creation request variants."""

    OBJECTIVE_DRAFT = "OBJECTIVE_DRAFT"
    TASK_DRAFT = "TASK_DRAFT"
    RUN_PENDING = "RUN_PENDING"
    OUTCOME_PROPOSED = "OUTCOME_PROPOSED"
    EVALUATION_PENDING = "EVALUATION_PENDING"
    EFFECT_PLANNED = "EFFECT_PLANNED"
    EFFECT_COMMITTED = "EFFECT_COMMITTED"
    EFFECT_QUARANTINED = "EFFECT_QUARANTINED"


@dataclass(frozen=True, slots=True)
class CreationRequestScope:
    """Immutable full-value authority/freshness scope, never a source snapshot."""

    variant: CreationRequestVariant
    entity_type: DomainEntityType
    entity_id: LifecycleEntityId
    target_state: LifecycleState
    requested_by: ActorIdentity
    causation_id: CausationId
    correlation_id: CorrelationId
    entity_spec: CreationEntitySpec
    semantic_input: CreationSemanticInput

    def __post_init__(self) -> None:
        _validate_scope_components(
            self.variant,
            self.entity_type,
            self.entity_id,
            self.target_state,
            self.requested_by,
            self.causation_id,
            self.correlation_id,
            self.entity_spec,
            self.semantic_input,
        )


@dataclass(frozen=True, slots=True)
class _CreationRequest:
    """Common immutable fields shared by the closed public request variants."""

    event_id: EventId
    entity_id: LifecycleEntityId
    requested_by: ActorIdentity
    reason: TransitionReason
    timestamp: Timestamp
    correlation_id: CorrelationId
    causation_id: CausationId
    entity_spec: CreationEntitySpec
    semantic_input: CreationSemanticInput

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, EventId):
            raise InvalidDomainValue("event_id must be an EventId")
        _validate_scope_components(
            self.variant,
            self.entity_type,
            self.entity_id,
            self.target_state,
            self.requested_by,
            self.causation_id,
            self.correlation_id,
            self.entity_spec,
            self.semantic_input,
        )
        if not isinstance(self.reason, TransitionReason):
            raise InvalidDomainValue("reason must be a TransitionReason")
        if not isinstance(self.timestamp, Timestamp):
            raise InvalidDomainValue("timestamp must be a Timestamp")

    @property
    def variant(self) -> "CreationRequestVariant":
        raise NotImplementedError("Creation requests must use a closed variant")

    @property
    def entity_type(self) -> DomainEntityType:
        raise NotImplementedError("Creation requests must use a closed variant")

    @property
    def target_state(self) -> LifecycleState:
        raise NotImplementedError("Creation requests must use a closed variant")

    @property
    def scope(self) -> CreationRequestScope:
        return CreationRequestScope(
            self.variant,
            self.entity_type,
            self.entity_id,
            self.target_state,
            self.requested_by,
            self.causation_id,
            self.correlation_id,
            self.entity_spec,
            self.semantic_input,
        )


@dataclass(frozen=True, slots=True)
class ObjectiveDraftCreationRequest(_CreationRequest):
    entity_id: ObjectiveId
    entity_spec: ObjectiveCreationSpec
    semantic_input: ObjectiveCreationSemanticInput

    @property
    def variant(self) -> CreationRequestVariant:
        return CreationRequestVariant.OBJECTIVE_DRAFT

    @property
    def entity_type(self) -> DomainEntityType:
        return DomainEntityType.OBJECTIVE

    @property
    def target_state(self) -> ObjectiveState:
        return ObjectiveState.DRAFT


@dataclass(frozen=True, slots=True)
class TaskDraftCreationRequest(_CreationRequest):
    entity_id: TaskId
    entity_spec: TaskCreationSpec
    semantic_input: TaskCreationSemanticInput

    @property
    def variant(self) -> CreationRequestVariant:
        return CreationRequestVariant.TASK_DRAFT

    @property
    def entity_type(self) -> DomainEntityType:
        return DomainEntityType.TASK

    @property
    def target_state(self) -> TaskState:
        return TaskState.DRAFT


@dataclass(frozen=True, slots=True)
class RunPendingCreationRequest(_CreationRequest):
    entity_id: RunId
    entity_spec: RunCreationSpec
    semantic_input: RunCreationSemanticInput

    @property
    def variant(self) -> CreationRequestVariant:
        return CreationRequestVariant.RUN_PENDING

    @property
    def entity_type(self) -> DomainEntityType:
        return DomainEntityType.RUN

    @property
    def target_state(self) -> RunState:
        return RunState.PENDING


@dataclass(frozen=True, slots=True)
class OutcomeProposedCreationRequest(_CreationRequest):
    entity_id: OutcomeId
    entity_spec: OutcomeCreationSpec
    semantic_input: OutcomeCreationSemanticInput

    @property
    def variant(self) -> CreationRequestVariant:
        return CreationRequestVariant.OUTCOME_PROPOSED

    @property
    def entity_type(self) -> DomainEntityType:
        return DomainEntityType.OUTCOME

    @property
    def target_state(self) -> OutcomeState:
        return OutcomeState.PROPOSED


@dataclass(frozen=True, slots=True)
class EvaluationPendingCreationRequest(_CreationRequest):
    entity_id: EvaluationId
    entity_spec: EvaluationCreationSpec
    semantic_input: EvaluationCreationSemanticInput

    @property
    def variant(self) -> CreationRequestVariant:
        return CreationRequestVariant.EVALUATION_PENDING

    @property
    def entity_type(self) -> DomainEntityType:
        return DomainEntityType.EVALUATION

    @property
    def target_state(self) -> EvaluationState:
        return EvaluationState.PENDING


@dataclass(frozen=True, slots=True)
class PlannedEffectCreationRequest(_CreationRequest):
    entity_id: EffectId
    entity_spec: PlannedEffectCreationSpec
    semantic_input: PlannedEffectCreationSemanticInput

    @property
    def variant(self) -> CreationRequestVariant:
        return CreationRequestVariant.EFFECT_PLANNED

    @property
    def entity_type(self) -> DomainEntityType:
        return DomainEntityType.EFFECT

    @property
    def target_state(self) -> EffectState:
        return EffectState.PLANNED


@dataclass(frozen=True, slots=True)
class CommittedEffectObservationCreationRequest(_CreationRequest):
    entity_id: EffectId
    entity_spec: ObservedEffectCreationSpec
    semantic_input: ObservedEffectCreationSemanticInput

    @property
    def variant(self) -> CreationRequestVariant:
        return CreationRequestVariant.EFFECT_COMMITTED

    @property
    def entity_type(self) -> DomainEntityType:
        return DomainEntityType.EFFECT

    @property
    def target_state(self) -> EffectState:
        return EffectState.COMMITTED


@dataclass(frozen=True, slots=True)
class QuarantinedEffectObservationCreationRequest(_CreationRequest):
    entity_id: EffectId
    entity_spec: ObservedEffectCreationSpec
    semantic_input: ObservedEffectCreationSemanticInput

    @property
    def variant(self) -> CreationRequestVariant:
        return CreationRequestVariant.EFFECT_QUARANTINED

    @property
    def entity_type(self) -> DomainEntityType:
        return DomainEntityType.EFFECT

    @property
    def target_state(self) -> EffectState:
        return EffectState.QUARANTINED


type CreationRequest = (
    ObjectiveDraftCreationRequest
    | TaskDraftCreationRequest
    | RunPendingCreationRequest
    | OutcomeProposedCreationRequest
    | EvaluationPendingCreationRequest
    | PlannedEffectCreationRequest
    | CommittedEffectObservationCreationRequest
    | QuarantinedEffectObservationCreationRequest
)

_CREATION_REQUEST_TYPES = (
    ObjectiveDraftCreationRequest,
    TaskDraftCreationRequest,
    RunPendingCreationRequest,
    OutcomeProposedCreationRequest,
    EvaluationPendingCreationRequest,
    PlannedEffectCreationRequest,
    CommittedEffectObservationCreationRequest,
    QuarantinedEffectObservationCreationRequest,
)


def _validate_scope_components(
    variant: CreationRequestVariant,
    entity_type: DomainEntityType,
    entity_id: LifecycleEntityId,
    target_state: LifecycleState,
    requested_by: ActorIdentity,
    causation_id: CausationId,
    correlation_id: CorrelationId,
    entity_spec: CreationEntitySpec,
    semantic_input: CreationSemanticInput,
) -> None:
    """Validate the closed variant-to-family/spec/input mapping."""
    expected = {
        CreationRequestVariant.OBJECTIVE_DRAFT: (
            DomainEntityType.OBJECTIVE,
            ObjectiveId,
            ObjectiveState.DRAFT,
            ObjectiveCreationSpec,
            ObjectiveCreationSemanticInput,
        ),
        CreationRequestVariant.TASK_DRAFT: (
            DomainEntityType.TASK,
            TaskId,
            TaskState.DRAFT,
            TaskCreationSpec,
            TaskCreationSemanticInput,
        ),
        CreationRequestVariant.RUN_PENDING: (
            DomainEntityType.RUN,
            RunId,
            RunState.PENDING,
            RunCreationSpec,
            RunCreationSemanticInput,
        ),
        CreationRequestVariant.OUTCOME_PROPOSED: (
            DomainEntityType.OUTCOME,
            OutcomeId,
            OutcomeState.PROPOSED,
            OutcomeCreationSpec,
            OutcomeCreationSemanticInput,
        ),
        CreationRequestVariant.EVALUATION_PENDING: (
            DomainEntityType.EVALUATION,
            EvaluationId,
            EvaluationState.PENDING,
            EvaluationCreationSpec,
            EvaluationCreationSemanticInput,
        ),
        CreationRequestVariant.EFFECT_PLANNED: (
            DomainEntityType.EFFECT,
            EffectId,
            EffectState.PLANNED,
            PlannedEffectCreationSpec,
            PlannedEffectCreationSemanticInput,
        ),
        CreationRequestVariant.EFFECT_COMMITTED: (
            DomainEntityType.EFFECT,
            EffectId,
            EffectState.COMMITTED,
            ObservedEffectCreationSpec,
            ObservedEffectCreationSemanticInput,
        ),
        CreationRequestVariant.EFFECT_QUARANTINED: (
            DomainEntityType.EFFECT,
            EffectId,
            EffectState.QUARANTINED,
            ObservedEffectCreationSpec,
            ObservedEffectCreationSemanticInput,
        ),
    }.get(variant)
    if expected is None:
        raise InvalidDomainValue("variant must be a CreationRequestVariant")
    expected_entity_type, id_type, expected_target, spec_type, input_type = expected
    if entity_type is not expected_entity_type:
        raise InvalidDomainValue("entity_type must match the creation request variant")
    if not isinstance(entity_id, id_type):
        raise InvalidDomainValue("entity_id must match the creation request variant")
    if target_state is not expected_target:
        raise InvalidDomainValue("target_state must match the creation request variant")
    if not isinstance(requested_by, ActorIdentity):
        raise InvalidDomainValue("requested_by must be an ActorIdentity")
    if not isinstance(causation_id, CausationId):
        raise InvalidDomainValue("causation_id must be a CausationId")
    if not isinstance(correlation_id, CorrelationId):
        raise InvalidDomainValue("correlation_id must be a CorrelationId")
    if not isinstance(entity_spec, spec_type):
        raise InvalidDomainValue("entity_spec must match the creation request variant")
    if not isinstance(semantic_input, input_type):
        raise InvalidDomainValue(
            "semantic_input must match the creation request variant"
        )


class CreationAuthorityStatus(Enum):
    """Closed trusted authority outcome for an exact creation request scope."""

    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class CreationAuthorityDecision:
    """Independent authority decision; it has no source state or version."""

    decision_ref: CreationAuthorityDecisionId
    request_scope: CreationRequestScope
    decided_by: ActorIdentity
    decision_status: CreationAuthorityStatus
    policy_or_grant_refs: tuple[CausationId, ...]
    decided_at: Timestamp

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, CreationAuthorityDecisionId):
            raise InvalidDomainValue(
                "decision_ref must be a CreationAuthorityDecisionId"
            )
        if not isinstance(self.request_scope, CreationRequestScope):
            raise InvalidDomainValue("request_scope must be a CreationRequestScope")
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        if not isinstance(self.decision_status, CreationAuthorityStatus):
            raise InvalidDomainValue(
                "decision_status must be a CreationAuthorityStatus"
            )
        if not isinstance(self.policy_or_grant_refs, tuple) or any(
            not isinstance(value, CausationId) for value in self.policy_or_grant_refs
        ):
            raise InvalidDomainValue(
                "policy_or_grant_refs must be a tuple of CausationId"
            )
        if len(set(self.policy_or_grant_refs)) != len(self.policy_or_grant_refs):
            raise InvalidDomainValue("policy_or_grant_refs must not contain duplicates")
        if not isinstance(self.decided_at, Timestamp):
            raise InvalidDomainValue("decided_at must be a Timestamp")


class IdentifierAvailabilityStatus(Enum):
    """Pre-M8 trusted availability observation, never a uniqueness guarantee."""

    AVAILABLE = "AVAILABLE"
    DUPLICATE = "DUPLICATE"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class IdentifierAvailability:
    """Exact-scope identifier observation supplied by an orchestration boundary."""

    observation_ref: IdentifierAvailabilityId
    request_scope: CreationRequestScope
    entity_type: DomainEntityType
    entity_id: LifecycleEntityId
    status: IdentifierAvailabilityStatus
    observed_by: ActorIdentity
    observed_at: Timestamp
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.observation_ref, IdentifierAvailabilityId):
            raise InvalidDomainValue(
                "observation_ref must be an IdentifierAvailabilityId"
            )
        if not isinstance(self.request_scope, CreationRequestScope):
            raise InvalidDomainValue("request_scope must be a CreationRequestScope")
        if self.entity_type is not self.request_scope.entity_type:
            raise InvalidDomainValue("entity_type must match request_scope")
        if self.entity_id != self.request_scope.entity_id:
            raise InvalidDomainValue("entity_id must match request_scope")
        if not isinstance(self.status, IdentifierAvailabilityStatus):
            raise InvalidDomainValue("status must be an IdentifierAvailabilityStatus")
        if not isinstance(self.observed_by, ActorIdentity):
            raise InvalidDomainValue("observed_by must be an ActorIdentity")
        if self.observed_by.actor_type in {ActorType.REQUESTER, ActorType.WORKER}:
            raise InvalidDomainValue(
                "identifier availability must be observed by an orchestration boundary"
            )
        if self.observed_by.actor_id == self.request_scope.requested_by.actor_id:
            raise InvalidDomainValue(
                "identifier availability observer must differ from the requester"
            )
        if not isinstance(self.observed_at, Timestamp):
            raise InvalidDomainValue("observed_at must be a Timestamp")
        if self.correlation_id != self.request_scope.correlation_id:
            raise InvalidDomainValue("correlation_id must match request_scope")


@runtime_checkable
class CreationGuard(Protocol):
    """Pure additional guard boundary; it never supplies entity semantics."""

    def validate(self, request: CreationRequest) -> None:
        """Return normally or raise a typed domain rejection."""
        ...


@dataclass(frozen=True, slots=True)
class CreationContext:
    """Trusted creation inputs; missing entity semantic validation is denial."""

    authority_decision: CreationAuthorityDecision | None
    identifier_availability: IdentifierAvailability | None
    applying_service: ActorIdentity
    guards: tuple[CreationGuard, ...] = ()

    def __post_init__(self) -> None:
        if self.authority_decision is not None and not isinstance(
            self.authority_decision, CreationAuthorityDecision
        ):
            raise InvalidDomainValue(
                "authority_decision must be a CreationAuthorityDecision or None"
            )
        if self.identifier_availability is not None and not isinstance(
            self.identifier_availability, IdentifierAvailability
        ):
            raise InvalidDomainValue(
                "identifier_availability must be an IdentifierAvailability or None"
            )
        if not isinstance(self.applying_service, ActorIdentity):
            raise InvalidDomainValue("applying_service must be an ActorIdentity")
        if not isinstance(self.guards, tuple) or any(
            not isinstance(value, CreationGuard) for value in self.guards
        ):
            raise InvalidDomainValue("guards must be a tuple of CreationGuard")


@dataclass(frozen=True, slots=True)
class CreationResult[EntityT_co: LifecycleEntity]:
    """One version-1 snapshot and one matching event, if semantics authorize it.

    M7D1 relies on ``DomainEventMetadata`` for immutable annotation structure.
    M7D2--M7D5 own the exact annotation vocabulary and semantic values for each
    successful creation edge.
    """

    entity: EntityT_co
    event: DomainEvent
    request: CreationRequest
    authority_decision: CreationAuthorityDecision
    identifier_availability: IdentifierAvailability

    def __post_init__(self) -> None:
        if not isinstance(
            self.entity, (Objective, Task, Run, Outcome, Evaluation, Effect)
        ):
            raise InvalidDomainValue("entity must be a lifecycle entity snapshot")
        if not isinstance(self.event, DomainEvent):
            raise InvalidDomainValue("event must be a DomainEvent")
        if type(self.request) not in _CREATION_REQUEST_TYPES:
            raise InvalidDomainValue(
                "request must be one of the eight creation request variants"
            )
        if not isinstance(self.authority_decision, CreationAuthorityDecision):
            raise InvalidDomainValue(
                "authority_decision must be a CreationAuthorityDecision"
            )
        if not isinstance(self.identifier_availability, IdentifierAvailability):
            raise InvalidDomainValue(
                "identifier_availability must be an IdentifierAvailability"
            )
        _require_exact_authority(self.request, self.authority_decision)
        _require_exact_availability(self.request, self.identifier_availability)
        entity_type, entity_id, state, version = _entity_details(self.entity)
        if (
            entity_type is not self.request.entity_type
            or entity_id != self.request.entity_id
            or state is not self.request.target_state
            or version != INITIAL_CREATION_VERSION
        ):
            raise InvalidDomainValue(
                "entity must be the request's canonical version-1 snapshot"
            )
        _require_entity_matches_request_spec(self.request, self.entity)
        if not (
            self.event.event_id == self.request.event_id
            and self.event.entity_type is entity_type
            and self.event.entity_id == entity_id
            and self.event.entity_version == INITIAL_CREATION_VERSION
            and self.event.actor == self.authority_decision.decided_by
            and self.event.timestamp == self.request.timestamp
            and self.event.correlation_id == self.request.correlation_id
            and self.event.causation_id == self.request.causation_id
            and self.event.reason == self.request.reason
            and self.event.metadata.prior_state is None
            and self.event.metadata.new_state is state
        ):
            raise InvalidDomainValue("event must exactly describe the creation result")


def _entity_details(
    entity: LifecycleEntity,
) -> tuple[DomainEntityType, LifecycleEntityId, LifecycleState, EntityVersion]:
    if isinstance(entity, Objective):
        return (
            DomainEntityType.OBJECTIVE,
            entity.objective_id,
            entity.state,
            entity.version,
        )
    if isinstance(entity, Task):
        return DomainEntityType.TASK, entity.task_id, entity.state, entity.version
    if isinstance(entity, Run):
        return DomainEntityType.RUN, entity.run_id, entity.state, entity.version
    if isinstance(entity, Outcome):
        return DomainEntityType.OUTCOME, entity.outcome_id, entity.state, entity.version
    if isinstance(entity, Evaluation):
        return (
            DomainEntityType.EVALUATION,
            entity.evaluation_id,
            entity.state,
            entity.version,
        )
    return DomainEntityType.EFFECT, entity.effect_id, entity.state, entity.version


def _require_entity_matches_request_spec(
    request: CreationRequest, entity: LifecycleEntity
) -> None:
    """Bind successful immutable content to the authorized request spec."""
    spec = request.entity_spec
    exact_match = False
    if isinstance(entity, Objective) and isinstance(spec, ObjectiveCreationSpec):
        exact_match = (
            entity.goal == spec.goal
            and entity.acceptance_criteria == spec.acceptance_criteria
            and entity.acceptance_authority == spec.acceptance_authority
            and entity.completion_policy_ref == spec.completion_policy_ref
            and entity.valid_until == spec.valid_until
        )
    elif isinstance(entity, Task) and isinstance(spec, TaskCreationSpec):
        exact_match = (
            entity.definition == spec.definition
            and entity.primary_objective_id == spec.primary_objective_id
            and entity.completion_policy_ref == spec.completion_policy_ref
            and entity.contributes_to == spec.contributes_to
        )
    elif isinstance(entity, Run) and isinstance(spec, RunCreationSpec):
        exact_match = (
            entity.task_id == spec.task_id
            and entity.execution_profile_ref == spec.execution_profile_ref
            and entity.predecessor_run_id == spec.predecessor_run_id
        )
    elif isinstance(entity, Outcome) and isinstance(spec, OutcomeCreationSpec):
        exact_match = (
            entity.run_id == spec.run_id
            and entity.producer == spec.producer
            and entity.artifact_refs == spec.artifact_refs
            and entity.evidence_refs == spec.evidence_refs
            and entity.valid_until == spec.valid_until
            and entity.prior_outcome_id == spec.prior_outcome_id
            and entity.superseded_by_outcome_id is None
        )
    elif isinstance(entity, Evaluation) and isinstance(spec, EvaluationCreationSpec):
        exact_match = (
            entity.target == spec.target
            and entity.method == spec.method
            and entity.verifier == spec.verifier
            and entity.result is None
        )
    elif isinstance(entity, Effect) and isinstance(spec, PlannedEffectCreationSpec):
        exact_match = (
            entity.origin == spec.origin
            and entity.target_ref == spec.target_ref
            and entity.payload_ref == spec.payload_ref
        )
    elif isinstance(entity, Effect) and isinstance(spec, ObservedEffectCreationSpec):
        exact_match = (
            entity.origin == spec.origin
            and entity.target_ref == spec.target_ref
            and entity.payload_ref == spec.payload_ref
        )
    if not exact_match:
        raise InvalidDomainValue(
            "entity immutable content must exact-bind request.entity_spec"
        )


def _creation_principals_requiring_no_relabel(
    request: CreationRequest,
) -> tuple[ActorIdentity, ...]:
    spec = request.entity_spec
    principals = (request.requested_by,)
    if isinstance(spec, OutcomeCreationSpec):
        return principals + (spec.producer,)
    if isinstance(spec, PlannedEffectCreationSpec):
        return principals + (spec.origin.proposed_by,)
    if isinstance(spec, ObservedEffectCreationSpec):
        return principals + (spec.origin.observed_by,)
    return principals


def _require_no_creation_authority_relabel(
    request: CreationRequest, authority_actor: ActorIdentity
) -> None:
    for principal in _creation_principals_requiring_no_relabel(request):
        if (
            authority_actor.actor_id == principal.actor_id
            and authority_actor.actor_type is not principal.actor_type
        ):
            raise UnauthorizedTransition(
                "Creation authority cannot be acquired by relabelling a principal"
            )


def _require_exact_authority(
    request: CreationRequest, decision: CreationAuthorityDecision | None
) -> None:
    if decision is None:
        raise UnauthorizedTransition("Creation authority decision is required")
    if decision.decision_status is not CreationAuthorityStatus.AUTHORIZED:
        raise UnauthorizedTransition(
            f"Creation authority decision is {decision.decision_status.value}"
        )
    if decision.request_scope != request.scope:
        raise UnauthorizedTransition(
            "Creation authority decision must exact-bind request scope"
        )
    _require_no_creation_authority_relabel(request, decision.decided_by)
    if not is_actor_eligible_for_transition_authority(
        request.entity_type,
        None,
        request.target_state,
        decision.decided_by.actor_type,
    ):
        raise UnauthorizedTransition(
            f"{decision.decided_by.actor_type.value} is not eligible for direct "
            f"{request.entity_type.value} creation authority"
        )


def _require_exact_availability(
    request: CreationRequest, availability: IdentifierAvailability | None
) -> None:
    if availability is None:
        raise InvariantViolation("Identifier availability observation is required")
    if availability.request_scope != request.scope:
        raise InvariantViolation(
            "Identifier availability must exact-bind request scope"
        )
    if availability.status is not IdentifierAvailabilityStatus.AVAILABLE:
        raise InvariantViolation(
            f"Identifier availability is {availability.status.value}, not AVAILABLE"
        )


def _require_shared_context(request: CreationRequest, context: CreationContext) -> None:
    _require_exact_authority(request, context.authority_decision)
    _require_exact_availability(request, context.identifier_availability)


def _require_additional_guards(
    request: CreationRequest, context: CreationContext
) -> None:
    for guard in context.guards:
        guard.validate(request)


def _require_passed(status: CreationSemanticDecisionStatus, condition: str) -> None:
    if status is not CreationSemanticDecisionStatus.PASSED:
        raise InvariantViolation(
            "Creation semantic condition is not satisfied: "
            f"{condition} ({status.value})"
        )


def _require_independent_semantic_actor(
    request: CreationRequest, actor: ActorIdentity
) -> None:
    if actor.actor_id == request.requested_by.actor_id:
        raise InvariantViolation(
            "Creation semantic evidence must not relabel the requester principal"
        )


def _validate_objective_creation_semantics(
    request: ObjectiveDraftCreationRequest,
) -> tuple[
    ObjectiveBoundedGoalDecision,
    ObjectiveAcceptanceBindingDecision,
    ObjectiveCreationCompletionPolicyDecision,
]:
    semantics = request.semantic_input
    bounded = semantics.bounded_goal
    acceptance = semantics.acceptance_binding
    completion = semantics.completion_policy
    if bounded is None or acceptance is None or completion is None:
        raise InvariantViolation(
            "Canonical entity-specific creation semantics are not implemented"
        )
    spec = request.entity_spec
    if not (
        bounded.objective_id == request.entity_id
        and bounded.goal == spec.goal
        and bounded.request_causation_id == request.causation_id
        and bounded.correlation_id == request.correlation_id
    ):
        raise InvariantViolation(
            "Bounded-goal decision must exact-bind the Objective request"
        )
    if not (
        acceptance.objective_id == request.entity_id
        and acceptance.goal == spec.goal
        and acceptance.acceptance_criteria == spec.acceptance_criteria
        and acceptance.acceptance_authority == spec.acceptance_authority
        and acceptance.request_causation_id == request.causation_id
        and acceptance.correlation_id == request.correlation_id
    ):
        raise InvariantViolation(
            "Acceptance-binding decision must exact-bind the Objective request"
        )
    if not (
        completion.objective_id == request.entity_id
        and completion.completion_policy_ref == spec.completion_policy_ref
        and completion.request_causation_id == request.causation_id
        and completion.correlation_id == request.correlation_id
    ):
        raise InvariantViolation(
            "Completion-policy decision must exact-bind the Objective request"
        )
    for decision in (bounded, acceptance, completion):
        _require_independent_semantic_actor(request, decision.decided_by)
    _require_passed(bounded.status, "bounded Objective goal")
    _require_passed(
        acceptance.status,
        "acceptance criteria and designated authority binding",
    )
    _require_passed(completion.status, "Objective completion-policy applicability")
    return bounded, acceptance, completion


def _validate_task_creation_semantics(
    request: TaskDraftCreationRequest,
) -> tuple[
    TaskBoundedDefinitionDecision,
    TaskCreationCompletionPolicyDecision,
    tuple[TaskObjectiveObservation, ...],
]:
    semantics = request.semantic_input
    bounded = semantics.bounded_definition
    completion = semantics.completion_policy
    observations = semantics.objective_observations
    if bounded is None or completion is None or observations is None:
        raise InvariantViolation(
            "Canonical entity-specific creation semantics are not implemented"
        )
    spec = request.entity_spec
    if not (
        bounded.task_id == request.entity_id
        and bounded.definition == spec.definition
        and bounded.request_causation_id == request.causation_id
        and bounded.correlation_id == request.correlation_id
    ):
        raise InvariantViolation(
            "Bounded-definition decision must exact-bind the Task request"
        )
    if not (
        completion.task_id == request.entity_id
        and completion.completion_policy_ref == spec.completion_policy_ref
        and completion.request_causation_id == request.causation_id
        and completion.correlation_id == request.correlation_id
    ):
        raise InvariantViolation(
            "Completion-policy decision must exact-bind the Task request"
        )
    for decision in (bounded, completion):
        _require_independent_semantic_actor(request, decision.decided_by)
    _require_passed(bounded.status, "bounded Task definition")
    _require_passed(completion.status, "Task completion-policy applicability")

    expected = {
        (TaskObjectiveRelationship.PRIMARY, spec.primary_objective_id),
        *(
            (TaskObjectiveRelationship.CONTRIBUTION, objective_id)
            for objective_id in spec.contributes_to
        ),
    }
    actual = {(value.relationship, value.objective_id) for value in observations}
    if len(actual) != len(observations) or actual != expected:
        raise InvalidRelationship(
            "Task Objective observations must exactly equal request relationships"
        )
    for observation in observations:
        if not (
            observation.task_id == request.entity_id
            and observation.request_causation_id == request.causation_id
            and observation.correlation_id == request.correlation_id
        ):
            raise InvalidRelationship(
                "Task Objective observation must exact-bind the Task request"
            )
        _require_independent_semantic_actor(request, observation.observed_by)
        if observation.status is TaskObjectiveObservationStatus.MISSING:
            raise EntityNotFound(
                f"Related Objective {observation.objective_id} is missing"
            )
        if observation.status is not TaskObjectiveObservationStatus.CURRENT:
            raise InvariantViolation(
                f"Task Objective observation is not CURRENT: {observation.status.value}"
            )
    return bounded, completion, observations


def _common_creation_annotations(
    request: CreationRequest, context: CreationContext
) -> list[tuple[str, str]]:
    decision = context.authority_decision
    availability = context.identifier_availability
    assert decision is not None
    assert availability is not None
    annotations = [
        ("requested_by.actor_id", str(request.requested_by.actor_id)),
        ("requested_by.actor_type", request.requested_by.actor_type.value),
        ("applying_service.actor_id", str(context.applying_service.actor_id)),
        ("applying_service.actor_type", context.applying_service.actor_type.value),
        ("creation_authority_decision_ref", str(decision.decision_ref)),
        ("identifier_availability_ref", str(availability.observation_ref)),
        ("semantic_provenance_ref", str(request.semantic_input.provenance_ref)),
    ]
    annotations.extend(
        (f"authority_policy_or_grant_ref.{index:04d}", str(reference))
        for index, reference in enumerate(decision.policy_or_grant_refs)
    )
    return annotations


def _semantic_evidence_annotations(
    evidence_refs: frozenset[EvidenceRef],
) -> list[tuple[str, str]]:
    return [
        (f"semantic_evidence_ref.{index:04d}", reference.value)
        for index, reference in enumerate(
            sorted(evidence_refs, key=lambda item: item.value)
        )
    ]


def _objective_creation_annotations(
    request: ObjectiveDraftCreationRequest,
    context: CreationContext,
    bounded: ObjectiveBoundedGoalDecision,
    acceptance: ObjectiveAcceptanceBindingDecision,
    completion: ObjectiveCreationCompletionPolicyDecision,
) -> frozenset[tuple[str, str]]:
    annotations = _common_creation_annotations(request, context)
    annotations.extend(
        (
            ("bounded_goal_decision_ref", bounded.decision_ref.value),
            ("acceptance_binding_decision_ref", acceptance.decision_ref.value),
            ("completion_policy_decision_ref", completion.decision_ref.value),
        )
    )
    evidence = (
        bounded.evidence_refs | acceptance.evidence_refs | completion.evidence_refs
    )
    annotations.extend(_semantic_evidence_annotations(evidence))
    return frozenset(annotations)


def _task_creation_annotations(
    request: TaskDraftCreationRequest,
    context: CreationContext,
    bounded: TaskBoundedDefinitionDecision,
    completion: TaskCreationCompletionPolicyDecision,
    observations: tuple[TaskObjectiveObservation, ...],
) -> frozenset[tuple[str, str]]:
    annotations = _common_creation_annotations(request, context)
    annotations.extend(
        (
            ("definition_decision_ref", bounded.decision_ref.value),
            ("completion_policy_decision_ref", completion.decision_ref.value),
        )
    )
    primary = next(
        value
        for value in observations
        if value.relationship is TaskObjectiveRelationship.PRIMARY
    )
    assert primary.observed_entity_version is not None
    annotations.extend(
        (
            ("primary_objective_observation_ref", primary.observation_ref.value),
            (
                "primary_objective_observed_version",
                str(primary.observed_entity_version.value),
            ),
        )
    )
    contributions = sorted(
        (
            value
            for value in observations
            if value.relationship is TaskObjectiveRelationship.CONTRIBUTION
        ),
        key=lambda value: str(value.objective_id),
    )
    for index, observation in enumerate(contributions):
        assert observation.observed_entity_version is not None
        prefix = f"contribution_objective.{index:04d}"
        annotations.extend(
            (
                (f"{prefix}.id", str(observation.objective_id)),
                (f"{prefix}.observation_ref", observation.observation_ref.value),
                (
                    f"{prefix}.observed_version",
                    str(observation.observed_entity_version.value),
                ),
            )
        )
    evidence = bounded.evidence_refs | completion.evidence_refs
    for observation in observations:
        evidence |= observation.evidence_refs
    annotations.extend(_semantic_evidence_annotations(evidence))
    return frozenset(annotations)


def _creation_event(
    request: CreationRequest,
    decision: CreationAuthorityDecision,
    annotations: frozenset[tuple[str, str]],
) -> DomainEvent:
    event_type = {
        CreationRequestVariant.OBJECTIVE_DRAFT: DomainEventType.OBJECTIVE_CREATED,
        CreationRequestVariant.TASK_DRAFT: DomainEventType.TASK_CREATED,
        CreationRequestVariant.RUN_PENDING: DomainEventType.RUN_CREATED,
        CreationRequestVariant.OUTCOME_PROPOSED: DomainEventType.OUTCOME_PROPOSED,
        CreationRequestVariant.EVALUATION_PENDING: DomainEventType.EVALUATION_REQUESTED,
        CreationRequestVariant.EFFECT_PLANNED: DomainEventType.EFFECT_PLANNED,
    }[request.variant]
    return DomainEvent(
        request.event_id,
        event_type,
        request.entity_type,
        request.entity_id,
        INITIAL_CREATION_VERSION,
        decision.decided_by,
        request.timestamp,
        request.correlation_id,
        request.causation_id,
        request.reason,
        DomainEventMetadata(None, request.target_state, annotations),
    )


def _create_objective(
    request: ObjectiveDraftCreationRequest, context: CreationContext
) -> CreationResult[Objective]:
    bounded, acceptance, completion = _validate_objective_creation_semantics(request)
    _require_additional_guards(request, context)
    spec = request.entity_spec
    entity = Objective(
        request.entity_id,
        ObjectiveState.DRAFT,
        INITIAL_CREATION_VERSION,
        spec.goal,
        spec.acceptance_criteria,
        spec.acceptance_authority,
        spec.completion_policy_ref,
        spec.valid_until,
    )
    decision = context.authority_decision
    availability = context.identifier_availability
    assert decision is not None
    assert availability is not None
    event = _creation_event(
        request,
        decision,
        _objective_creation_annotations(
            request, context, bounded, acceptance, completion
        ),
    )
    return CreationResult(entity, event, request, decision, availability)


def _create_task(
    request: TaskDraftCreationRequest, context: CreationContext
) -> CreationResult[Task]:
    bounded, completion, observations = _validate_task_creation_semantics(request)
    _require_additional_guards(request, context)
    spec = request.entity_spec
    entity = Task(
        request.entity_id,
        TaskState.DRAFT,
        INITIAL_CREATION_VERSION,
        spec.definition,
        spec.primary_objective_id,
        spec.completion_policy_ref,
        spec.contributes_to,
    )
    decision = context.authority_decision
    availability = context.identifier_availability
    assert decision is not None
    assert availability is not None
    event = _creation_event(
        request,
        decision,
        _task_creation_annotations(request, context, bounded, completion, observations),
    )
    return CreationResult(entity, event, request, decision, availability)


@overload
def create_entity(
    request: ObjectiveDraftCreationRequest, context: CreationContext
) -> CreationResult[Objective]: ...


@overload
def create_entity(
    request: TaskDraftCreationRequest, context: CreationContext
) -> CreationResult[Task]: ...


@overload
def create_entity(
    request: RunPendingCreationRequest, context: CreationContext
) -> CreationResult[Run]: ...


@overload
def create_entity(
    request: OutcomeProposedCreationRequest, context: CreationContext
) -> CreationResult[Outcome]: ...


@overload
def create_entity(
    request: EvaluationPendingCreationRequest, context: CreationContext
) -> CreationResult[Evaluation]: ...


@overload
def create_entity(
    request: PlannedEffectCreationRequest, context: CreationContext
) -> CreationResult[Effect]: ...


@overload
def create_entity(
    request: CommittedEffectObservationCreationRequest, context: CreationContext
) -> CreationResult[Effect]: ...


@overload
def create_entity(
    request: QuarantinedEffectObservationCreationRequest, context: CreationContext
) -> CreationResult[Effect]: ...


def create_entity(
    request: CreationRequest, context: CreationContext
) -> CreationResult[LifecycleEntity]:
    """Create M7D2/M7D3 entities and planned Effects; deny observed Effects.

    This dedicated boundary intentionally accepts neither a source snapshot nor an
    expected version, and never delegates to ``transition_entity``.
    """
    if type(request) not in _CREATION_REQUEST_TYPES:
        raise InvalidDomainValue(
            "request must be one of the eight creation request variants"
        )
    if not isinstance(context, CreationContext):
        raise InvalidDomainValue("context must be a CreationContext")
    _require_shared_context(request, context)
    if isinstance(request, ObjectiveDraftCreationRequest):
        return _create_objective(request, context)
    if isinstance(request, TaskDraftCreationRequest):
        return _create_task(request, context)
    if isinstance(request, PlannedEffectCreationRequest):
        scope = validate_planned_effect_creation(request)
        _require_additional_guards(request, context)
        entity = Effect(
            request.entity_id,
            EffectState.PLANNED,
            INITIAL_CREATION_VERSION,
            request.entity_spec.origin,
            request.entity_spec.target_ref,
            request.entity_spec.payload_ref,
        )
        decision = context.authority_decision
        availability = context.identifier_availability
        semantic_decision = request.semantic_input.decision
        assert (
            decision is not None
            and availability is not None
            and semantic_decision is not None
        )
        annotations = frozenset(
            _common_creation_annotations(request, context)
        ) | planned_effect_annotations(scope, semantic_decision)
        return CreationResult(
            entity,
            _creation_event(request, decision, annotations),
            request,
            decision,
            availability,
        )
    if isinstance(
        request,
        (
            RunPendingCreationRequest,
            OutcomeProposedCreationRequest,
            EvaluationPendingCreationRequest,
        ),
    ):
        return _create_run_outcome_evaluation(request, context)
    _require_additional_guards(request, context)
    raise InvariantViolation(
        "Canonical entity-specific creation semantics are not implemented"
    )


def _create_run_outcome_evaluation(
    request: RunPendingCreationRequest
    | OutcomeProposedCreationRequest
    | EvaluationPendingCreationRequest,
    context: CreationContext,
) -> CreationResult[Run | Outcome | Evaluation]:
    scope: RunRegistrationScope | OutcomeProposalScope | EvaluationRequestScope
    entity: Run | Outcome | Evaluation
    if isinstance(request, RunPendingCreationRequest):
        scope = validate_run_creation(request)
        _require_additional_guards(request, context)
        entity = Run(
            request.entity_id,
            request.entity_spec.task_id,
            RunState.PENDING,
            INITIAL_CREATION_VERSION,
            request.entity_spec.execution_profile_ref,
            request.entity_spec.predecessor_run_id,
        )
    elif isinstance(request, OutcomeProposedCreationRequest):
        scope = validate_outcome_creation(request)
        _require_additional_guards(request, context)
        entity = Outcome(
            request.entity_id,
            request.entity_spec.run_id,
            OutcomeState.PROPOSED,
            INITIAL_CREATION_VERSION,
            request.entity_spec.producer,
            request.entity_spec.artifact_refs,
            request.entity_spec.evidence_refs,
            request.entity_spec.valid_until,
            request.entity_spec.prior_outcome_id,
        )
    else:
        scope = validate_evaluation_creation(request)
        _require_additional_guards(request, context)
        entity = Evaluation(
            request.entity_id,
            EvaluationState.PENDING,
            INITIAL_CREATION_VERSION,
            request.entity_spec.target,
            request.entity_spec.method,
            request.entity_spec.verifier,
        )
    semantic_decision = request.semantic_input.decision
    authority = context.authority_decision
    availability = context.identifier_availability
    assert (
        semantic_decision is not None
        and authority is not None
        and availability is not None
    )
    annotations = frozenset(
        _common_creation_annotations(request, context)
    ) | creation_scope_annotations(scope, semantic_decision)
    return CreationResult(
        entity,
        _creation_event(request, authority, annotations),
        request,
        authority,
        availability,
    )
