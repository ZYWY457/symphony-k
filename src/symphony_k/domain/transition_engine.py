"""Pure authoritative lifecycle-transition mechanics for immutable snapshots.

M7A validates caller-supplied versions and canonical structural topology. M7B1
requires a separate exact-bound authority decision. M7B2 additionally requires
the decision actor's type to be canonically eligible for the exact lifecycle edge.
M7C requires the applicable canonical entity semantic guard before ordinary
additional guards, then returns a new snapshot and one DomainEvent.
Eligibility is not a scoped grant. This module performs no loading, persistence,
transaction, or external action.
"""

from collections.abc import Mapping
from dataclasses import dataclass, replace
from enum import Enum
from types import MappingProxyType
from typing import Final, Protocol, overload, runtime_checkable

from . import effect as effect_domain
from . import evaluation as evaluation_domain
from . import objective as objective_domain
from . import outcome as outcome_domain
from . import run as run_domain
from . import task as task_domain
from .actors import ActorIdentity, ActorType
from .effect import Effect, EffectState
from .effect_semantics import EffectSemanticGuard
from .errors import (
    ConcurrencyConflict,
    InvalidDomainValue,
    InvalidTransition,
    InvariantViolation,
    UnauthorizedTransition,
)
from .evaluation import Evaluation, EvaluationState
from .evaluation_semantics import EvaluationSemanticGuard
from .ids import (
    CausationId,
    CorrelationId,
    EffectId,
    EvaluationId,
    EventId,
    ObjectiveId,
    OutcomeId,
    RunId,
    TaskId,
)
from .objective import Objective, ObjectiveState
from .objective_semantics import ObjectiveSemanticGuard
from .outcome import Outcome, OutcomeState
from .outcome_semantics import OutcomeSemanticGuard
from .run import Run, RunState
from .run_semantics import RunSemanticGuard
from .task import Task, TaskState
from .task_semantics import TaskSemanticGuard
from .time import Timestamp
from .transitions import TransitionReason
from .version import EntityVersion

type LifecycleEntity = Objective | Task | Run | Outcome | Evaluation | Effect
type LifecycleState = (
    ObjectiveState | TaskState | RunState | OutcomeState | EvaluationState | EffectState
)
type LifecycleEntityId = (
    ObjectiveId | TaskId | RunId | OutcomeId | EvaluationId | EffectId
)


class DomainEntityType(Enum):
    """Closed identity of the six lifecycle-bearing core entity families."""

    OBJECTIVE = "OBJECTIVE"
    TASK = "TASK"
    RUN = "RUN"
    OUTCOME = "OUTCOME"
    EVALUATION = "EVALUATION"
    EFFECT = "EFFECT"


class TransitionAuthorityStatus(Enum):
    """Closed result of trusted authority evaluation for one exact attempt."""

    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"
    UNRESOLVED = "UNRESOLVED"


class DomainEventType(Enum):
    """Closed authoritative lifecycle-event family from the accepted design."""

    OBJECTIVE_CREATED = "ObjectiveCreated"
    OBJECTIVE_ACTIVATED = "ObjectiveActivated"
    OBJECTIVE_BLOCKED = "ObjectiveBlocked"
    OBJECTIVE_SATISFIED = "ObjectiveSatisfied"
    OBJECTIVE_FAILED = "ObjectiveFailed"
    OBJECTIVE_CANCELLED = "ObjectiveCancelled"
    OBJECTIVE_EXPIRED = "ObjectiveExpired"
    OBJECTIVE_ARCHIVED = "ObjectiveArchived"

    TASK_CREATED = "TaskCreated"
    TASK_READIED = "TaskReadied"
    TASK_STARTED = "TaskStarted"
    TASK_BLOCKED = "TaskBlocked"
    TASK_COMPLETED = "TaskCompleted"
    TASK_FAILED = "TaskFailed"
    TASK_CANCELLED = "TaskCancelled"

    RUN_CREATED = "RunCreated"
    RUN_STARTED = "RunStarted"
    RUN_WAITING_FOR_VERIFICATION = "RunWaitingForVerification"
    RUN_RETRYING = "RunRetrying"
    RUN_REASSIGNED = "RunReassigned"
    RUN_COMPLETED = "RunCompleted"
    RUN_FAILED = "RunFailed"
    RUN_ABORTED = "RunAborted"

    OUTCOME_PROPOSED = "OutcomeProposed"
    OUTCOME_VALIDATION_STARTED = "OutcomeValidationStarted"
    OUTCOME_ACCEPTED = "OutcomeAccepted"
    OUTCOME_REJECTED = "OutcomeRejected"
    OUTCOME_SUPERSEDED = "OutcomeSuperseded"
    OUTCOME_EXPIRED = "OutcomeExpired"

    EVALUATION_REQUESTED = "EvaluationRequested"
    EVALUATION_STARTED = "EvaluationStarted"
    EVALUATION_COMPLETED = "EvaluationCompleted"
    EVALUATION_CONFLICTED = "EvaluationConflicted"
    EVALUATION_ARBITRATED = "EvaluationArbitrated"
    EVALUATION_INVALIDATED = "EvaluationInvalidated"

    EFFECT_PLANNED = "EffectPlanned"
    EFFECT_SIMULATED = "EffectSimulated"
    EFFECT_PENDING_COMMIT = "EffectPendingCommit"
    EFFECT_COMMITTED = "EffectCommitted"
    EFFECT_ROLLED_BACK = "EffectRolledBack"
    EFFECT_COMPENSATION_STARTED = "EffectCompensationStarted"
    EFFECT_COMPENSATED = "EffectCompensated"
    EFFECT_QUARANTINED = "EffectQuarantined"


_EVENT_TYPE_BY_STATE: Final[Mapping[LifecycleState, DomainEventType]] = (
    MappingProxyType(
        {
            ObjectiveState.DRAFT: DomainEventType.OBJECTIVE_CREATED,
            ObjectiveState.ACTIVE: DomainEventType.OBJECTIVE_ACTIVATED,
            ObjectiveState.BLOCKED: DomainEventType.OBJECTIVE_BLOCKED,
            ObjectiveState.SATISFIED: DomainEventType.OBJECTIVE_SATISFIED,
            ObjectiveState.FAILED: DomainEventType.OBJECTIVE_FAILED,
            ObjectiveState.CANCELLED: DomainEventType.OBJECTIVE_CANCELLED,
            ObjectiveState.EXPIRED: DomainEventType.OBJECTIVE_EXPIRED,
            ObjectiveState.ARCHIVED: DomainEventType.OBJECTIVE_ARCHIVED,
            TaskState.DRAFT: DomainEventType.TASK_CREATED,
            TaskState.READY: DomainEventType.TASK_READIED,
            TaskState.IN_PROGRESS: DomainEventType.TASK_STARTED,
            TaskState.BLOCKED: DomainEventType.TASK_BLOCKED,
            TaskState.COMPLETED: DomainEventType.TASK_COMPLETED,
            TaskState.FAILED: DomainEventType.TASK_FAILED,
            TaskState.CANCELLED: DomainEventType.TASK_CANCELLED,
            RunState.PENDING: DomainEventType.RUN_CREATED,
            RunState.RUNNING: DomainEventType.RUN_STARTED,
            RunState.WAITING_FOR_VERIFICATION: (
                DomainEventType.RUN_WAITING_FOR_VERIFICATION
            ),
            RunState.RETRYING: DomainEventType.RUN_RETRYING,
            RunState.REASSIGNED: DomainEventType.RUN_REASSIGNED,
            RunState.COMPLETED: DomainEventType.RUN_COMPLETED,
            RunState.FAILED: DomainEventType.RUN_FAILED,
            RunState.ABORTED: DomainEventType.RUN_ABORTED,
            OutcomeState.PROPOSED: DomainEventType.OUTCOME_PROPOSED,
            OutcomeState.VALIDATING: DomainEventType.OUTCOME_VALIDATION_STARTED,
            OutcomeState.ACCEPTED: DomainEventType.OUTCOME_ACCEPTED,
            OutcomeState.REJECTED: DomainEventType.OUTCOME_REJECTED,
            OutcomeState.SUPERSEDED: DomainEventType.OUTCOME_SUPERSEDED,
            OutcomeState.EXPIRED: DomainEventType.OUTCOME_EXPIRED,
            EvaluationState.PENDING: DomainEventType.EVALUATION_REQUESTED,
            EvaluationState.RUNNING: DomainEventType.EVALUATION_STARTED,
            EvaluationState.COMPLETED: DomainEventType.EVALUATION_COMPLETED,
            EvaluationState.CONFLICTED: DomainEventType.EVALUATION_CONFLICTED,
            EvaluationState.ARBITRATED: DomainEventType.EVALUATION_ARBITRATED,
            EvaluationState.INVALID: DomainEventType.EVALUATION_INVALIDATED,
            EffectState.PLANNED: DomainEventType.EFFECT_PLANNED,
            EffectState.SIMULATED: DomainEventType.EFFECT_SIMULATED,
            EffectState.PENDING_COMMIT: DomainEventType.EFFECT_PENDING_COMMIT,
            EffectState.COMMITTED: DomainEventType.EFFECT_COMMITTED,
            EffectState.ROLLED_BACK: DomainEventType.EFFECT_ROLLED_BACK,
            EffectState.COMPENSATING: DomainEventType.EFFECT_COMPENSATION_STARTED,
            EffectState.COMPENSATED: DomainEventType.EFFECT_COMPENSATED,
            EffectState.QUARANTINED: DomainEventType.EFFECT_QUARANTINED,
        }
    )
)


def _is_lifecycle_state(value: object) -> bool:
    return isinstance(
        value,
        (
            ObjectiveState,
            TaskState,
            RunState,
            OutcomeState,
            EvaluationState,
            EffectState,
        ),
    )


def _entity_type_for_state(state: LifecycleState) -> DomainEntityType:
    if isinstance(state, ObjectiveState):
        return DomainEntityType.OBJECTIVE
    if isinstance(state, TaskState):
        return DomainEntityType.TASK
    if isinstance(state, RunState):
        return DomainEntityType.RUN
    if isinstance(state, OutcomeState):
        return DomainEntityType.OUTCOME
    if isinstance(state, EvaluationState):
        return DomainEntityType.EVALUATION
    return DomainEntityType.EFFECT


def _entity_type_for_id(identity: LifecycleEntityId) -> DomainEntityType:
    if isinstance(identity, ObjectiveId):
        return DomainEntityType.OBJECTIVE
    if isinstance(identity, TaskId):
        return DomainEntityType.TASK
    if isinstance(identity, RunId):
        return DomainEntityType.RUN
    if isinstance(identity, OutcomeId):
        return DomainEntityType.OUTCOME
    if isinstance(identity, EvaluationId):
        return DomainEntityType.EVALUATION
    return DomainEntityType.EFFECT


@dataclass(frozen=True, slots=True)
class TransitionAuthorityDecision:
    """Explicit authority result bound to one exact lifecycle transition attempt."""

    actor: ActorIdentity
    entity_type: DomainEntityType
    entity_id: LifecycleEntityId
    observed_entity_version: EntityVersion
    prior_state: LifecycleState
    target_state: LifecycleState
    decision: TransitionAuthorityStatus
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.actor, ActorIdentity):
            raise InvalidDomainValue("actor must be an ActorIdentity")
        if not isinstance(self.entity_type, DomainEntityType):
            raise InvalidDomainValue("entity_type must be a DomainEntityType")
        if not isinstance(
            self.entity_id,
            (ObjectiveId, TaskId, RunId, OutcomeId, EvaluationId, EffectId),
        ):
            raise InvalidDomainValue("entity_id must be a core entity ID")
        if _entity_type_for_id(self.entity_id) is not self.entity_type:
            raise InvalidDomainValue("entity_id must match entity_type")
        if not isinstance(self.observed_entity_version, EntityVersion):
            raise InvalidDomainValue("observed_entity_version must be an EntityVersion")
        if not _is_lifecycle_state(self.prior_state):
            raise InvalidDomainValue("prior_state must be a lifecycle state")
        if not _is_lifecycle_state(self.target_state):
            raise InvalidDomainValue("target_state must be a lifecycle state")
        if (
            _entity_type_for_state(self.prior_state) is not self.entity_type
            or _entity_type_for_state(self.target_state) is not self.entity_type
        ):
            raise InvalidDomainValue(
                "prior_state and target_state must match entity_type"
            )
        if self.prior_state is self.target_state:
            raise InvalidDomainValue(
                "Authority decision cannot describe a self-transition"
            )
        if not isinstance(self.decision, TransitionAuthorityStatus):
            raise InvalidDomainValue("decision must be a TransitionAuthorityStatus")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")


def _entity_details(
    entity: LifecycleEntity,
) -> tuple[DomainEntityType, LifecycleEntityId, LifecycleState]:
    if isinstance(entity, Objective):
        return DomainEntityType.OBJECTIVE, entity.objective_id, entity.state
    if isinstance(entity, Task):
        return DomainEntityType.TASK, entity.task_id, entity.state
    if isinstance(entity, Run):
        return DomainEntityType.RUN, entity.run_id, entity.state
    if isinstance(entity, Outcome):
        return DomainEntityType.OUTCOME, entity.outcome_id, entity.state
    if isinstance(entity, Evaluation):
        return DomainEntityType.EVALUATION, entity.evaluation_id, entity.state
    return DomainEntityType.EFFECT, entity.effect_id, entity.state


def _replace_entity_state(
    entity: LifecycleEntity,
    target: LifecycleState,
    version: EntityVersion,
) -> LifecycleEntity:
    """Create a same-family replacement, changing only state and version."""
    if isinstance(entity, Objective) and isinstance(target, ObjectiveState):
        return replace(entity, state=target, version=version)
    if isinstance(entity, Task) and isinstance(target, TaskState):
        return replace(entity, state=target, version=version)
    if isinstance(entity, Run) and isinstance(target, RunState):
        return replace(entity, state=target, version=version)
    if isinstance(entity, Outcome) and isinstance(target, OutcomeState):
        return replace(entity, state=target, version=version)
    if isinstance(entity, Evaluation) and isinstance(target, EvaluationState):
        return replace(entity, state=target, version=version)
    if isinstance(entity, Effect) and isinstance(target, EffectState):
        return replace(entity, state=target, version=version)
    raise InvalidTransition("Target state belongs to a different entity family")


def _project_outcome_supersession(
    source: Outcome,
    replacement_outcome_id: OutcomeId,
    version: EntityVersion,
) -> Outcome:
    """Create the only Outcome-specific relationship projection in M7C4C."""
    return replace(
        source,
        state=OutcomeState.SUPERSEDED,
        version=version,
        superseded_by_outcome_id=replacement_outcome_id,
    )


def _can_transition(
    entity_type: DomainEntityType,
    source: LifecycleState,
    target: LifecycleState,
) -> bool:
    """Delegate to the canonical entity topology; no edge set exists here."""
    if entity_type is DomainEntityType.OBJECTIVE:
        return (
            isinstance(source, ObjectiveState)
            and isinstance(target, ObjectiveState)
            and objective_domain.can_objective_transition(source, target)
        )
    if entity_type is DomainEntityType.TASK:
        return (
            isinstance(source, TaskState)
            and isinstance(target, TaskState)
            and task_domain.can_task_transition(source, target)
        )
    if entity_type is DomainEntityType.RUN:
        return (
            isinstance(source, RunState)
            and isinstance(target, RunState)
            and run_domain.can_run_transition(source, target)
        )
    if entity_type is DomainEntityType.OUTCOME:
        return (
            isinstance(source, OutcomeState)
            and isinstance(target, OutcomeState)
            and outcome_domain.can_outcome_transition(source, target)
        )
    if entity_type is DomainEntityType.EVALUATION:
        return (
            isinstance(source, EvaluationState)
            and isinstance(target, EvaluationState)
            and evaluation_domain.can_evaluation_transition(source, target)
        )
    return (
        isinstance(source, EffectState)
        and isinstance(target, EffectState)
        and effect_domain.can_effect_transition(source, target)
    )


def _is_creation_target(entity_type: DomainEntityType, target: LifecycleState) -> bool:
    if entity_type is DomainEntityType.OBJECTIVE:
        return target is objective_domain.OBJECTIVE_CREATION_STATE
    if entity_type is DomainEntityType.TASK:
        return target is task_domain.TASK_CREATION_STATE
    if entity_type is DomainEntityType.RUN:
        return target is run_domain.RUN_CREATION_STATE
    if entity_type is DomainEntityType.OUTCOME:
        return target is outcome_domain.OUTCOME_CREATION_STATE
    if entity_type is DomainEntityType.EVALUATION:
        return target is evaluation_domain.EVALUATION_CREATION_STATE
    return (
        isinstance(target, EffectState)
        and target in effect_domain.EFFECT_CREATION_STATES
    )


_OBJECTIVE_AUTHORITY: Final[frozenset[ActorType]] = frozenset(
    {
        ActorType.REQUESTER,
        ActorType.SCHEDULER,
        ActorType.POLICY_ENGINE,
        ActorType.HUMAN_OPERATOR,
    }
)
_TASK_AUTHORITY: Final[frozenset[ActorType]] = _OBJECTIVE_AUTHORITY
_RUN_AUTHORITY: Final[frozenset[ActorType]] = frozenset(
    {ActorType.SCHEDULER, ActorType.RUN_CONTROLLER}
)
_OUTCOME_AUTHORITY: Final[frozenset[ActorType]] = frozenset(
    {ActorType.SCHEDULER, ActorType.POLICY_ENGINE}
)
_EFFECT_AUTHORITY: Final[frozenset[ActorType]] = frozenset(
    {ActorType.EFFECT_CONTROLLER}
)

_UNIFORM_AUTHORITY_BY_ENTITY: Final[Mapping[DomainEntityType, frozenset[ActorType]]] = (
    MappingProxyType(
        {
            DomainEntityType.OBJECTIVE: _OBJECTIVE_AUTHORITY,
            DomainEntityType.TASK: _TASK_AUTHORITY,
            DomainEntityType.RUN: _RUN_AUTHORITY,
            DomainEntityType.OUTCOME: _OUTCOME_AUTHORITY,
            DomainEntityType.EFFECT: _EFFECT_AUTHORITY,
        }
    )
)

_EVALUATION_AUTHORITY_BY_EDGE: Final[
    Mapping[
        tuple[EvaluationState | None, EvaluationState],
        frozenset[ActorType],
    ]
] = MappingProxyType(
    {
        (None, EvaluationState.PENDING): frozenset(
            {ActorType.SCHEDULER, ActorType.EVALUATOR}
        ),
        (EvaluationState.PENDING, EvaluationState.RUNNING): frozenset(
            {ActorType.EVALUATOR}
        ),
        (EvaluationState.RUNNING, EvaluationState.COMPLETED): frozenset(
            {ActorType.EVALUATOR}
        ),
        (EvaluationState.RUNNING, EvaluationState.CONFLICTED): frozenset(
            {
                ActorType.EVALUATOR,
                ActorType.ARBITRATOR,
                ActorType.HUMAN_OPERATOR,
            }
        ),
        (EvaluationState.COMPLETED, EvaluationState.CONFLICTED): frozenset(
            {
                ActorType.EVALUATOR,
                ActorType.ARBITRATOR,
                ActorType.HUMAN_OPERATOR,
            }
        ),
        (EvaluationState.COMPLETED, EvaluationState.ARBITRATED): frozenset(
            {ActorType.ARBITRATOR, ActorType.HUMAN_OPERATOR}
        ),
        (EvaluationState.CONFLICTED, EvaluationState.ARBITRATED): frozenset(
            {ActorType.ARBITRATOR, ActorType.HUMAN_OPERATOR}
        ),
        **{
            (source, EvaluationState.INVALID): frozenset(
                {
                    ActorType.EVALUATOR,
                    ActorType.ARBITRATOR,
                    ActorType.HUMAN_OPERATOR,
                }
            )
            for source in (
                EvaluationState.PENDING,
                EvaluationState.RUNNING,
                EvaluationState.COMPLETED,
                EvaluationState.CONFLICTED,
            )
        },
    }
)


def is_actor_eligible_for_transition_authority(
    entity_type: DomainEntityType,
    prior_state: LifecycleState | None,
    target_state: LifecycleState,
    actor_type: ActorType,
) -> bool:
    """Return actor-type eligibility for one canonical edge, never a grant."""
    if not isinstance(entity_type, DomainEntityType) or not isinstance(
        actor_type, ActorType
    ):
        return False
    if not _is_lifecycle_state(target_state):
        return False
    if _entity_type_for_state(target_state) is not entity_type:
        return False

    if prior_state is None:
        if not _is_creation_target(entity_type, target_state):
            return False
    else:
        if not _is_lifecycle_state(prior_state):
            return False
        if _entity_type_for_state(prior_state) is not entity_type:
            return False
        if not _can_transition(entity_type, prior_state, target_state):
            return False

    if entity_type is DomainEntityType.EVALUATION:
        if not isinstance(target_state, EvaluationState):
            return False
        if prior_state is not None and not isinstance(prior_state, EvaluationState):
            return False
        return actor_type in _EVALUATION_AUTHORITY_BY_EDGE.get(
            (prior_state, target_state), frozenset()
        )

    return actor_type in _UNIFORM_AUTHORITY_BY_ENTITY[entity_type]


@dataclass(frozen=True, slots=True)
class DomainEventMetadata:
    """Immutable lifecycle meaning; None means pre-creation absence, not a state."""

    prior_state: LifecycleState | None
    new_state: LifecycleState
    annotations: frozenset[tuple[str, str]] = frozenset()

    def __post_init__(self) -> None:
        if self.prior_state is not None and not _is_lifecycle_state(self.prior_state):
            raise InvalidDomainValue("prior_state must be a lifecycle state or None")
        if not _is_lifecycle_state(self.new_state):
            raise InvalidDomainValue("new_state must be a lifecycle state")
        if self.prior_state is not None:
            if type(self.prior_state) is not type(self.new_state):
                raise InvalidDomainValue(
                    "prior_state and new_state must belong to the same entity family"
                )
            if self.prior_state is self.new_state:
                raise InvalidDomainValue(
                    "Lifecycle event metadata cannot self-transition"
                )
        if not isinstance(self.annotations, frozenset):
            raise InvalidDomainValue("annotations must be a frozenset")
        keys: list[str] = []
        for annotation in self.annotations:
            if (
                not isinstance(annotation, tuple)
                or len(annotation) != 2
                or not all(
                    isinstance(value, str) and value.strip() for value in annotation
                )
            ):
                raise InvalidDomainValue(
                    "Every annotation must contain two non-whitespace strings"
                )
            keys.append(annotation[0])
        if len(keys) != len(set(keys)):
            raise InvalidDomainValue("Annotation keys must be unique")


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """One immutable authoritative lifecycle event; persistence belongs to M8."""

    event_id: EventId
    event_type: DomainEventType
    entity_type: DomainEntityType
    entity_id: LifecycleEntityId
    entity_version: EntityVersion
    actor: ActorIdentity
    timestamp: Timestamp
    correlation_id: CorrelationId
    causation_id: CausationId | None
    reason: TransitionReason
    metadata: DomainEventMetadata

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, EventId):
            raise InvalidDomainValue("event_id must be an EventId")
        if not isinstance(self.event_type, DomainEventType):
            raise InvalidDomainValue("event_type must be a DomainEventType")
        if not isinstance(self.entity_type, DomainEntityType):
            raise InvalidDomainValue("entity_type must be a DomainEntityType")
        if not isinstance(
            self.entity_id,
            (ObjectiveId, TaskId, RunId, OutcomeId, EvaluationId, EffectId),
        ):
            raise InvalidDomainValue("entity_id must be a core entity ID")
        if _entity_type_for_id(self.entity_id) is not self.entity_type:
            raise InvalidDomainValue("entity_id must match entity_type")
        if not isinstance(self.entity_version, EntityVersion):
            raise InvalidDomainValue("entity_version must be an EntityVersion")
        if not isinstance(self.actor, ActorIdentity):
            raise InvalidDomainValue("actor must be an ActorIdentity")
        if not isinstance(self.timestamp, Timestamp):
            raise InvalidDomainValue("timestamp must be a Timestamp")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if self.causation_id is not None and not isinstance(
            self.causation_id, CausationId
        ):
            raise InvalidDomainValue("causation_id must be a CausationId or None")
        if not isinstance(self.reason, TransitionReason):
            raise InvalidDomainValue("reason must be a TransitionReason")
        if not isinstance(self.metadata, DomainEventMetadata):
            raise InvalidDomainValue("metadata must be DomainEventMetadata")
        if _entity_type_for_state(self.metadata.new_state) is not self.entity_type:
            raise InvalidDomainValue("metadata state must match entity_type")
        if _EVENT_TYPE_BY_STATE[self.metadata.new_state] is not self.event_type:
            raise InvalidDomainValue("event_type must match the new lifecycle state")
        if self.metadata.prior_state is None:
            if not _is_creation_target(self.entity_type, self.metadata.new_state):
                raise InvalidDomainValue(
                    "Absent prior state is valid only for a canonical creation target"
                )
        elif not _can_transition(
            self.entity_type, self.metadata.prior_state, self.metadata.new_state
        ):
            raise InvalidDomainValue(
                "metadata must describe a canonical lifecycle edge"
            )


@dataclass(frozen=True, slots=True)
class TransitionRequest[StateT_co: LifecycleState]:
    """Immutable caller request; actor classification alone grants no authority."""

    event_id: EventId
    target_state: StateT_co
    actor: ActorIdentity
    reason: TransitionReason
    expected_version: EntityVersion
    timestamp: Timestamp
    correlation_id: CorrelationId
    causation_id: CausationId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, EventId):
            raise InvalidDomainValue("event_id must be an EventId")
        if not _is_lifecycle_state(self.target_state):
            raise InvalidDomainValue("target_state must be a lifecycle state")
        if not isinstance(self.actor, ActorIdentity):
            raise InvalidDomainValue("actor must be an ActorIdentity")
        if not isinstance(self.reason, TransitionReason):
            raise InvalidDomainValue("reason must be a TransitionReason")
        if not isinstance(self.expected_version, EntityVersion):
            raise InvalidDomainValue("expected_version must be an EntityVersion")
        if not isinstance(self.timestamp, Timestamp):
            raise InvalidDomainValue("timestamp must be a Timestamp")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if self.causation_id is not None and not isinstance(
            self.causation_id, CausationId
        ):
            raise InvalidDomainValue("causation_id must be a CausationId or None")


@runtime_checkable
class TransitionGuard(Protocol):
    """Pure extension boundary for semantic and invariant guards only."""

    def validate(
        self,
        entity: LifecycleEntity,
        request: TransitionRequest[LifecycleState],
    ) -> None:
        """Return normally when satisfied or raise a typed DomainError."""
        ...


@dataclass(frozen=True, slots=True)
class TransitionContext:
    """Mandatory authority, entity-specific semantics, and extra guards."""

    guards: tuple[TransitionGuard, ...]
    authority_decision: TransitionAuthorityDecision | None = None
    objective_semantic_guard: ObjectiveSemanticGuard | None = None
    task_semantic_guard: TaskSemanticGuard | None = None
    run_semantic_guard: RunSemanticGuard | None = None
    outcome_semantic_guard: OutcomeSemanticGuard | None = None
    evaluation_semantic_guard: EvaluationSemanticGuard | None = None
    effect_semantic_guard: EffectSemanticGuard | None = None
    effect_compensation_start_event: DomainEvent | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.guards, tuple) or not self.guards:
            raise InvalidDomainValue("guards must be a nonempty tuple")
        if any(not isinstance(guard, TransitionGuard) for guard in self.guards):
            raise InvalidDomainValue("Every guard must implement TransitionGuard")
        if self.authority_decision is not None and not isinstance(
            self.authority_decision, TransitionAuthorityDecision
        ):
            raise InvalidDomainValue(
                "authority_decision must be a TransitionAuthorityDecision or None"
            )
        if self.objective_semantic_guard is not None and not isinstance(
            self.objective_semantic_guard, ObjectiveSemanticGuard
        ):
            raise InvalidDomainValue(
                "objective_semantic_guard must be an ObjectiveSemanticGuard or None"
            )
        if self.task_semantic_guard is not None and not isinstance(
            self.task_semantic_guard, TaskSemanticGuard
        ):
            raise InvalidDomainValue(
                "task_semantic_guard must be a TaskSemanticGuard or None"
            )
        if self.run_semantic_guard is not None and not isinstance(
            self.run_semantic_guard, RunSemanticGuard
        ):
            raise InvalidDomainValue(
                "run_semantic_guard must be a RunSemanticGuard or None"
            )
        if self.outcome_semantic_guard is not None and not isinstance(
            self.outcome_semantic_guard, OutcomeSemanticGuard
        ):
            raise InvalidDomainValue(
                "outcome_semantic_guard must be an OutcomeSemanticGuard or None"
            )
        if self.evaluation_semantic_guard is not None and not isinstance(
            self.evaluation_semantic_guard, EvaluationSemanticGuard
        ):
            raise InvalidDomainValue(
                "evaluation_semantic_guard must be an EvaluationSemanticGuard or None"
            )
        if self.effect_semantic_guard is not None and not isinstance(
            self.effect_semantic_guard, EffectSemanticGuard
        ):
            raise InvalidDomainValue(
                "effect_semantic_guard must be an EffectSemanticGuard or None"
            )
        if self.effect_compensation_start_event is not None and not isinstance(
            self.effect_compensation_start_event, DomainEvent
        ):
            raise InvalidDomainValue(
                "effect_compensation_start_event must be a DomainEvent or None"
            )


def _require_authorized_transition(
    entity_type: DomainEntityType,
    entity_id: LifecycleEntityId,
    source_state: LifecycleState,
    request: TransitionRequest[LifecycleState],
    decision: TransitionAuthorityDecision | None,
) -> None:
    """Reject unless one explicit AUTHORIZED decision matches the exact attempt."""
    if decision is None:
        raise UnauthorizedTransition("Transition authority decision is required")
    if decision.decision is not TransitionAuthorityStatus.AUTHORIZED:
        raise UnauthorizedTransition(
            f"Transition authority decision is {decision.decision.value}"
        )
    if not (
        decision.actor == request.actor
        and decision.entity_type is entity_type
        and decision.entity_id == entity_id
        and decision.observed_entity_version == request.expected_version
        and decision.prior_state is source_state
        and decision.target_state is request.target_state
        and decision.correlation_id == request.correlation_id
    ):
        raise UnauthorizedTransition(
            "Transition authority decision does not match the exact request snapshot"
        )

    if not is_actor_eligible_for_transition_authority(
        entity_type,
        source_state,
        request.target_state,
        decision.actor.actor_type,
    ):
        raise UnauthorizedTransition(
            f"{decision.actor.actor_type.value} is not eligible for direct "
            f"{entity_type.value} lifecycle authority on "
            f"{source_state.value} -> {request.target_state.value}"
        )


@dataclass(frozen=True, slots=True)
class TransitionResult[EntityT_co: LifecycleEntity]:
    """One new immutable snapshot paired with exactly one lifecycle event."""

    entity: EntityT_co
    event: DomainEvent

    def __post_init__(self) -> None:
        if not isinstance(
            self.entity, (Objective, Task, Run, Outcome, Evaluation, Effect)
        ):
            raise InvalidDomainValue("entity must be a lifecycle entity snapshot")
        if not isinstance(self.event, DomainEvent):
            raise InvalidDomainValue("event must be a DomainEvent")
        entity_type, entity_id, state = _entity_details(self.entity)
        if (
            self.event.entity_type is not entity_type
            or self.event.entity_id != entity_id
            or self.event.entity_version != self.entity.version
            or self.event.metadata.new_state is not state
        ):
            raise InvalidDomainValue("event must describe the returned entity snapshot")


@overload
def transition_entity(
    entity: Objective,
    request: TransitionRequest[ObjectiveState],
    context: TransitionContext,
) -> TransitionResult[Objective]: ...


@overload
def transition_entity(
    entity: Task,
    request: TransitionRequest[TaskState],
    context: TransitionContext,
) -> TransitionResult[Task]: ...


@overload
def transition_entity(
    entity: Run,
    request: TransitionRequest[RunState],
    context: TransitionContext,
) -> TransitionResult[Run]: ...


@overload
def transition_entity(
    entity: Outcome,
    request: TransitionRequest[OutcomeState],
    context: TransitionContext,
) -> TransitionResult[Outcome]: ...


@overload
def transition_entity(
    entity: Evaluation,
    request: TransitionRequest[EvaluationState],
    context: TransitionContext,
) -> TransitionResult[Evaluation]: ...


@overload
def transition_entity(
    entity: Effect,
    request: TransitionRequest[EffectState],
    context: TransitionContext,
) -> TransitionResult[Effect]: ...


def transition_entity(
    entity: LifecycleEntity,
    request: TransitionRequest[LifecycleState],
    context: TransitionContext,
) -> TransitionResult[LifecycleEntity]:
    """Apply foundation guards and return a replacement snapshot plus one event."""
    if not isinstance(entity, (Objective, Task, Run, Outcome, Evaluation, Effect)):
        raise InvalidDomainValue("entity must be a lifecycle entity snapshot")
    if not isinstance(request, TransitionRequest):
        raise InvalidDomainValue("request must be a TransitionRequest")
    if not isinstance(context, TransitionContext):
        raise InvalidDomainValue("context must be a TransitionContext")

    entity_type, entity_id, source_state = _entity_details(entity)
    if request.expected_version != entity.version:
        raise ConcurrencyConflict(
            f"Expected version {request.expected_version.value}, "
            f"but snapshot is version {entity.version.value}"
        )
    if _entity_type_for_state(request.target_state) is not entity_type:
        raise InvalidTransition("Target state belongs to a different entity family")
    if not _can_transition(entity_type, source_state, request.target_state):
        raise InvalidTransition(
            f"Unsupported {entity_type.value} transition "
            f"{source_state.value} -> {request.target_state.value}"
        )

    _require_authorized_transition(
        entity_type,
        entity_id,
        source_state,
        request,
        context.authority_decision,
    )

    if isinstance(entity, Objective):
        objective_guard = context.objective_semantic_guard
        if objective_guard is None:
            raise InvariantViolation("Canonical Objective semantic guard is required")
        if not isinstance(request.target_state, ObjectiveState):
            raise InvalidTransition("Target state belongs to a different entity family")
        objective_guard.validate(
            entity,
            request.target_state,
            request.timestamp,
            request.correlation_id,
        )
    elif isinstance(entity, Task):
        task_guard = context.task_semantic_guard
        if task_guard is None:
            raise InvariantViolation("Canonical Task semantic guard is required")
        if not isinstance(request.target_state, TaskState):
            raise InvalidTransition("Target state belongs to a different entity family")
        task_guard.validate(entity, request.target_state, request.correlation_id)
    elif isinstance(entity, Run):
        run_guard = context.run_semantic_guard
        if run_guard is None:
            raise InvariantViolation("Canonical Run semantic guard is required")
        if not isinstance(request.target_state, RunState):
            raise InvalidTransition("Target state belongs to a different entity family")
        run_guard.validate(entity, request.target_state, request.correlation_id)
    elif isinstance(entity, Outcome):
        outcome_guard = context.outcome_semantic_guard
        if outcome_guard is None:
            raise InvariantViolation("Canonical Outcome semantic guard is required")
        if not isinstance(request.target_state, OutcomeState):
            raise InvalidTransition("Target state belongs to a different entity family")
        outcome_guard.validate(
            entity,
            request.target_state,
            request.timestamp,
            request.correlation_id,
        )
    elif isinstance(entity, Evaluation):
        evaluation_guard = context.evaluation_semantic_guard
        if evaluation_guard is None:
            raise InvariantViolation("Canonical Evaluation semantic guard is required")
        if not isinstance(request.target_state, EvaluationState):
            raise InvalidTransition("Target state belongs to a different entity family")
        evaluation_guard.validate(
            entity,
            request.target_state,
            request.actor,
            request.correlation_id,
        )
    elif isinstance(entity, Effect):
        effect_guard = context.effect_semantic_guard
        scoped_effect_edge = (entity.state, request.target_state) in {
            (EffectState.PLANNED, EffectState.SIMULATED),
            (EffectState.PLANNED, EffectState.PENDING_COMMIT),
            (EffectState.SIMULATED, EffectState.PENDING_COMMIT),
            (EffectState.PLANNED, EffectState.COMMITTED),
            (EffectState.SIMULATED, EffectState.COMMITTED),
            (EffectState.PENDING_COMMIT, EffectState.COMMITTED),
            (EffectState.QUARANTINED, EffectState.COMMITTED),
            (EffectState.PLANNED, EffectState.QUARANTINED),
            (EffectState.SIMULATED, EffectState.QUARANTINED),
            (EffectState.PENDING_COMMIT, EffectState.QUARANTINED),
            (EffectState.COMMITTED, EffectState.ROLLED_BACK),
            (EffectState.COMMITTED, EffectState.COMPENSATING),
            (EffectState.COMMITTED, EffectState.QUARANTINED),
            (EffectState.COMPENSATING, EffectState.COMPENSATED),
            (EffectState.COMPENSATING, EffectState.QUARANTINED),
            (EffectState.QUARANTINED, EffectState.PENDING_COMMIT),
            (EffectState.QUARANTINED, EffectState.ROLLED_BACK),
            (EffectState.QUARANTINED, EffectState.COMPENSATING),
            (EffectState.QUARANTINED, EffectState.COMPENSATED),
        }
        if not scoped_effect_edge:
            raise InvariantViolation(
                "Effect canonical semantic guard denies this unimplemented edge"
            )
        if effect_guard is None:
            raise InvariantViolation("Canonical Effect semantic guard is required")
        if not isinstance(request.target_state, EffectState):
            raise InvalidTransition("Target state belongs to a different entity family")
        effect_guard.validate(
            entity,
            request.target_state,
            request.actor,
            request.correlation_id,
        )
        start_event = context.effect_compensation_start_event
        if (
            request.target_state
            in {
                EffectState.COMPENSATING,
                EffectState.COMPENSATED,
            }
            and entity.state is EffectState.QUARANTINED
            and effect_guard.requires_prior_compensation_start_event()
        ):
            if start_event is None:
                raise InvariantViolation(
                    "Quarantine compensation resume requires its start event"
                )
            if not (
                start_event.event_type is DomainEventType.EFFECT_COMPENSATION_STARTED
                and start_event.entity_type is DomainEntityType.EFFECT
                and start_event.entity_id == entity.effect_id
                and start_event.entity_version.value < entity.version.value
                and start_event.actor.actor_type is ActorType.EFFECT_CONTROLLER
                and start_event.correlation_id == request.correlation_id
                and start_event.metadata.prior_state is EffectState.COMMITTED
                and start_event.metadata.new_state is EffectState.COMPENSATING
                and start_event.metadata.annotations
                == effect_guard.compensation_start_annotations(start_event.event_id)
            ):
                raise InvariantViolation(
                    "Compensation start event does not bind quarantine plan lineage"
                )
            if request.target_state is EffectState.COMPENSATED and (
                effect_guard.validated_completion_verifier().actor_id
                == start_event.actor.actor_id
            ):
                raise InvariantViolation(
                    "Completion verifier must be separate from start controller"
                )
        elif request.target_state is EffectState.COMPENSATED:
            if start_event is None:
                raise InvariantViolation(
                    "Compensation completion requires its authoritative start event"
                )
            if not (
                start_event.event_type is DomainEventType.EFFECT_COMPENSATION_STARTED
                and start_event.entity_type is DomainEntityType.EFFECT
                and start_event.entity_id == entity.effect_id
                and start_event.entity_version == entity.version
                and start_event.actor.actor_type is ActorType.EFFECT_CONTROLLER
                and start_event.correlation_id == request.correlation_id
                and start_event.metadata.prior_state is EffectState.COMMITTED
                and start_event.metadata.new_state is EffectState.COMPENSATING
                and start_event.metadata.annotations
                == effect_guard.compensation_start_annotations(start_event.event_id)
            ):
                raise InvariantViolation(
                    "Compensation start event does not exact-bind the current plan "
                    "lineage"
                )
            if (
                effect_guard.validated_completion_verifier().actor_id
                == start_event.actor.actor_id
            ):
                raise InvariantViolation(
                    "Completion verifier must be separate from compensation-start "
                    "controller"
                )
        elif start_event is not None:
            raise InvariantViolation(
                "Compensation start event is valid only for completion semantics"
            )

    for guard in context.guards:
        guard.validate(entity, request)

    next_version = entity.version.next()
    updated: LifecycleEntity
    annotations: frozenset[tuple[str, str]] = frozenset()
    if isinstance(entity, Outcome) and request.target_state is OutcomeState.SUPERSEDED:
        outcome_guard = context.outcome_semantic_guard
        assert outcome_guard is not None
        replacement_outcome_id = outcome_guard.validated_replacement_outcome_id()
        updated = _project_outcome_supersession(
            entity, replacement_outcome_id, next_version
        )
        annotations = frozenset(
            {("replacement_outcome_id", str(replacement_outcome_id.value))}
        )
    elif (
        isinstance(entity, Evaluation)
        and request.target_state is EvaluationState.RUNNING
    ):
        evaluation_guard = context.evaluation_semantic_guard
        assert evaluation_guard is not None
        updated = replace(
            entity,
            state=EvaluationState.RUNNING,
            version=next_version,
            verifier=evaluation_guard.validated_start_verifier(),
        )
    elif (
        isinstance(entity, Evaluation)
        and request.target_state is EvaluationState.COMPLETED
    ):
        evaluation_guard = context.evaluation_semantic_guard
        assert evaluation_guard is not None
        updated = replace(
            entity,
            state=EvaluationState.COMPLETED,
            version=next_version,
            result=evaluation_guard.validated_completion_result(),
        )
    elif isinstance(entity, Evaluation) and request.target_state in (
        EvaluationState.CONFLICTED,
        EvaluationState.ARBITRATED,
    ):
        evaluation_guard = context.evaluation_semantic_guard
        assert evaluation_guard is not None
        updated = _replace_entity_state(entity, request.target_state, next_version)
        annotations = evaluation_guard.event_annotations()
    elif isinstance(entity, Effect) and request.target_state in {
        EffectState.ROLLED_BACK,
        EffectState.COMPENSATING,
        EffectState.COMPENSATED,
    }:
        effect_guard = context.effect_semantic_guard
        assert effect_guard is not None
        updated = _replace_entity_state(entity, request.target_state, next_version)
        if request.target_state is EffectState.COMPENSATING:
            annotations = effect_guard.remediation_event_annotations(
                start_event.event_id if start_event is not None else request.event_id
            )
        elif request.target_state is EffectState.COMPENSATED:
            start_event = context.effect_compensation_start_event
            assert start_event is not None
            annotations = effect_guard.remediation_event_annotations(
                start_event.event_id
            )
        else:
            annotations = effect_guard.remediation_event_annotations()
    else:
        updated = _replace_entity_state(entity, request.target_state, next_version)
    event = DomainEvent(
        event_id=request.event_id,
        event_type=_EVENT_TYPE_BY_STATE[request.target_state],
        entity_type=entity_type,
        entity_id=entity_id,
        entity_version=next_version,
        actor=request.actor,
        timestamp=request.timestamp,
        correlation_id=request.correlation_id,
        causation_id=request.causation_id,
        reason=request.reason,
        metadata=DomainEventMetadata(source_state, request.target_state, annotations),
    )
    return TransitionResult(updated, event)
