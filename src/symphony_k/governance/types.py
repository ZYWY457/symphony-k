"""Caller-controlled DTOs and exact references for the governance facade."""

from dataclasses import dataclass
from typing import overload

from symphony_k.domain import (
    ActorIdentity,
    ArtifactRef,
    CausationId,
    CorrelationId,
    DomainEvent,
    Effect,
    EffectId,
    EntityVersion,
    Evaluation,
    EvaluationId,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationState,
    EventId,
    EvidenceRef,
    ExecutionProfileRef,
    Objective,
    ObjectiveId,
    Outcome,
    OutcomeId,
    Run,
    RunId,
    Task,
    TaskId,
    Timestamp,
    TransitionReason,
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
    """Caller claims for one attempt; no field grants creation authority."""

    event_id: EventId
    run_id: RunId
    caller_identity_claim: ActorIdentity
    reason: TransitionReason
    timestamp: Timestamp
    correlation_id: CorrelationId
    causation_id: CausationId
    task: TaskRef
    primary_objective: ObjectiveRef
    execution_profile_ref: ExecutionProfileRef
    predecessor: RunRef | None = None


@dataclass(frozen=True, slots=True)
class OutcomeCandidateSubmission:
    """Caller-controlled Outcome proposal bound to an exact Run."""

    event_id: EventId
    outcome_id: OutcomeId
    caller_identity_claim: ActorIdentity
    reason: TransitionReason
    timestamp: Timestamp
    correlation_id: CorrelationId
    causation_id: CausationId
    run: RunRef
    producer_identity_claim: ActorIdentity
    artifact_refs: frozenset[ArtifactRef]
    evidence_refs: frozenset[EvidenceRef] = frozenset()
    valid_until: Timestamp | None = None
    prior_outcome: OutcomeRef | None = None


@dataclass(frozen=True, slots=True)
class EvaluationSubmission:
    """Evaluation/evidence claims; assignment and authority remain trusted."""

    event_id: EventId
    evaluation_id: EvaluationId
    caller_identity_claim: ActorIdentity
    reason: TransitionReason
    timestamp: Timestamp
    correlation_id: CorrelationId
    causation_id: CausationId
    target: EvaluationTargetReference
    method: EvaluationMethodRef
    artifact_refs: frozenset[ArtifactRef]
    evidence_refs: frozenset[EvidenceRef]
    producing_identity_claims: tuple[ActorIdentity, ...]


@dataclass(frozen=True, slots=True)
class EvaluationTransitionSubmission:
    """A caller request to start or complete an exact Evaluation."""

    evaluation: EvaluationRef
    target: EvaluationTargetReference
    target_state: EvaluationState
    event_id: EventId
    caller_identity_claim: ActorIdentity
    reason: TransitionReason
    timestamp: Timestamp
    correlation_id: CorrelationId
    causation_id: CausationId | None = None
    result_claim: EvaluationResult | None = None

    def __post_init__(self) -> None:
        if self.target_state not in {
            EvaluationState.RUNNING,
            EvaluationState.COMPLETED,
        }:
            raise InvalidRequestError(
                "Facade supports only Evaluation start and result submission"
            )
        if (
            self.target_state is EvaluationState.RUNNING
            and self.result_claim is not None
        ):
            raise InvalidRequestError("Evaluation start cannot carry a result claim")
        if self.target_state is EvaluationState.COMPLETED and self.result_claim is None:
            raise InvalidRequestError("Evaluation completion requires a result claim")
