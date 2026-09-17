"""Typed public references and submissions for the governance facade."""

from dataclasses import dataclass
from typing import overload

from symphony_k.domain import (
    CreationContext,
    DomainEvent,
    Effect,
    EffectId,
    EntityVersion,
    Evaluation,
    EvaluationId,
    EvaluationPendingCreationRequest,
    EvaluationState,
    Objective,
    ObjectiveId,
    Outcome,
    OutcomeId,
    OutcomeProposedCreationRequest,
    Run,
    RunId,
    RunPendingCreationRequest,
    Task,
    TaskId,
    TransitionContext,
    TransitionRequest,
)

from .errors import InvalidRequestError


def _require_reference(value: object, identity_type: type, label: str) -> None:
    identity = getattr(value, label, None)
    version = getattr(value, "version", None)
    if not isinstance(identity, identity_type) or not isinstance(
        version, EntityVersion
    ):
        raise InvalidRequestError(
            f"{type(value).__name__} is not a valid exact reference"
        )


@dataclass(frozen=True, slots=True)
class ObjectiveRef:
    objective_id: ObjectiveId
    version: EntityVersion

    def __post_init__(self) -> None:
        _require_reference(self, ObjectiveId, "objective_id")


@dataclass(frozen=True, slots=True)
class TaskRef:
    task_id: TaskId
    version: EntityVersion

    def __post_init__(self) -> None:
        _require_reference(self, TaskId, "task_id")


@dataclass(frozen=True, slots=True)
class RunRef:
    run_id: RunId
    version: EntityVersion

    def __post_init__(self) -> None:
        _require_reference(self, RunId, "run_id")


@dataclass(frozen=True, slots=True)
class OutcomeRef:
    outcome_id: OutcomeId
    version: EntityVersion

    def __post_init__(self) -> None:
        _require_reference(self, OutcomeId, "outcome_id")


@dataclass(frozen=True, slots=True)
class EvaluationRef:
    evaluation_id: EvaluationId
    version: EntityVersion

    def __post_init__(self) -> None:
        _require_reference(self, EvaluationId, "evaluation_id")


@dataclass(frozen=True, slots=True)
class EffectRef:
    effect_id: EffectId
    version: EntityVersion

    def __post_init__(self) -> None:
        _require_reference(self, EffectId, "effect_id")


type EntityReference = (
    ObjectiveRef | TaskRef | RunRef | OutcomeRef | EvaluationRef | EffectRef
)
type EvaluationTargetReference = RunRef | OutcomeRef | EffectRef
type GovernanceEntity = Objective | Task | Run | Outcome | Evaluation | Effect


@overload
def reference_of(entity: Objective) -> ObjectiveRef: ...


@overload
def reference_of(entity: Task) -> TaskRef: ...


@overload
def reference_of(entity: Run) -> RunRef: ...


@overload
def reference_of(entity: Outcome) -> OutcomeRef: ...


@overload
def reference_of(entity: Evaluation) -> EvaluationRef: ...


@overload
def reference_of(entity: Effect) -> EffectRef: ...


def reference_of(entity: GovernanceEntity) -> EntityReference:
    """Return the exact typed identity/version reference for a snapshot."""
    if isinstance(entity, Objective):
        return ObjectiveRef(entity.objective_id, entity.version)
    if isinstance(entity, Task):
        return TaskRef(entity.task_id, entity.version)
    if isinstance(entity, Run):
        return RunRef(entity.run_id, entity.version)
    if isinstance(entity, Outcome):
        return OutcomeRef(entity.outcome_id, entity.version)
    if isinstance(entity, Evaluation):
        return EvaluationRef(entity.evaluation_id, entity.version)
    return EffectRef(entity.effect_id, entity.version)


@dataclass(frozen=True, slots=True)
class AuthoritativeSnapshot[EntityT: GovernanceEntity, RefT: EntityReference]:
    """Caller-safe domain snapshot paired with its exact public reference."""

    reference: RefT
    entity: EntityT


@dataclass(frozen=True, slots=True)
class MutationResult[EntityT: GovernanceEntity, RefT: EntityReference]:
    """A persisted facade mutation and its authoritative lifecycle event."""

    snapshot: AuthoritativeSnapshot[EntityT, RefT]
    event: DomainEvent


@dataclass(frozen=True, slots=True)
class RunCandidateSubmission:
    """A legal Stage 1 Run registration with exact parent observations."""

    request: RunPendingCreationRequest
    context: CreationContext
    task: TaskRef
    primary_objective: ObjectiveRef

    def __post_init__(self) -> None:
        if not isinstance(self.request, RunPendingCreationRequest):
            raise InvalidRequestError(
                "Run submission requires RunPendingCreationRequest"
            )
        if not isinstance(self.context, CreationContext):
            raise InvalidRequestError("Run submission requires CreationContext")
        if not isinstance(self.task, TaskRef) or not isinstance(
            self.primary_objective, ObjectiveRef
        ):
            raise InvalidRequestError("Run submission requires exact parent references")


@dataclass(frozen=True, slots=True)
class OutcomeCandidateSubmission:
    """An untrusted Outcome proposal bound to one exact originating Run."""

    request: OutcomeProposedCreationRequest
    context: CreationContext
    run: RunRef

    def __post_init__(self) -> None:
        if not isinstance(self.request, OutcomeProposedCreationRequest):
            raise InvalidRequestError(
                "Outcome submission requires OutcomeProposedCreationRequest"
            )
        if not isinstance(self.context, CreationContext):
            raise InvalidRequestError("Outcome submission requires CreationContext")
        if not isinstance(self.run, RunRef):
            raise InvalidRequestError("Outcome submission requires an exact RunRef")


@dataclass(frozen=True, slots=True)
class EvaluationSubmission:
    """An Evaluation request bound to one exact Run, Outcome, or Effect."""

    request: EvaluationPendingCreationRequest
    context: CreationContext
    target: EvaluationTargetReference

    def __post_init__(self) -> None:
        if not isinstance(self.request, EvaluationPendingCreationRequest):
            raise InvalidRequestError(
                "Evaluation submission requires EvaluationPendingCreationRequest"
            )
        if not isinstance(self.context, CreationContext):
            raise InvalidRequestError("Evaluation submission requires CreationContext")
        if not isinstance(self.target, (RunRef, OutcomeRef, EffectRef)):
            raise InvalidRequestError(
                "Evaluation submission requires an exact versioned target"
            )


@dataclass(frozen=True, slots=True)
class EvaluationTransitionSubmission:
    """A narrow legal Evaluation start/result operation; never candidate authority."""

    evaluation: EvaluationRef
    target: EvaluationTargetReference
    request: TransitionRequest[EvaluationState]
    context: TransitionContext

    def __post_init__(self) -> None:
        if not isinstance(self.evaluation, EvaluationRef):
            raise InvalidRequestError("Evaluation transition requires EvaluationRef")
        if not isinstance(self.target, (RunRef, OutcomeRef, EffectRef)):
            raise InvalidRequestError("Evaluation transition requires exact target")
        if not isinstance(self.request, TransitionRequest):
            raise InvalidRequestError(
                "Evaluation transition requires TransitionRequest"
            )
        if self.request.target_state not in {
            EvaluationState.RUNNING,
            EvaluationState.COMPLETED,
        }:
            raise InvalidRequestError(
                "Facade supports only Evaluation start and result submission"
            )
        if not isinstance(self.context, TransitionContext):
            raise InvalidRequestError(
                "Evaluation transition requires TransitionContext"
            )
