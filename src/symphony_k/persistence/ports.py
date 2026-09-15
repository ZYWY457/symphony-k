"""Read-only repositories and the authoritative transactional lifecycle port."""

from typing import Protocol

from symphony_k.domain.creation import CreationContext, CreationRequest
from symphony_k.domain.effect import Effect
from symphony_k.domain.evaluation import Evaluation
from symphony_k.domain.ids import (
    EffectId,
    EvaluationId,
    EventId,
    ObjectiveId,
    OutcomeId,
    RunId,
    TaskId,
)
from symphony_k.domain.objective import Objective
from symphony_k.domain.outcome import Outcome
from symphony_k.domain.run import Run
from symphony_k.domain.task import Task
from symphony_k.domain.transition_engine import (
    DomainEvent,
    LifecycleEntity,
    LifecycleEntityId,
    LifecycleState,
    TransitionContext,
    TransitionRequest,
    TransitionResult,
)
from symphony_k.domain.version import EntityVersion


class Repository[IdT, EntityT](Protocol):
    """Missing current or historical identities raise EntityNotFound."""

    def load(self, entity_id: IdT) -> EntityT: ...

    def load_version(self, entity_id: IdT, version: EntityVersion) -> EntityT: ...


class ObjectiveRepository(Repository[ObjectiveId, Objective], Protocol): ...


class TaskRepository(Repository[TaskId, Task], Protocol): ...


class RunRepository(Repository[RunId, Run], Protocol): ...


class OutcomeRepository(Repository[OutcomeId, Outcome], Protocol): ...


class EvaluationRepository(Repository[EvaluationId, Evaluation], Protocol): ...


class EffectRepository(Repository[EffectId, Effect], Protocol): ...


class EventRepository(Protocol):
    def load(self, event_id: EventId) -> DomainEvent: ...

    def for_entity(self, entity_id: LifecycleEntityId) -> tuple[DomainEvent, ...]: ...


class UnitOfWork(Protocol):
    """One call commits a domain-approved snapshot, history, event and receipt.

    Failures roll back the entire operation. No public raw-write or commit hook
    permits callers to persist arbitrary snapshots. Replay returns the original
    entity version and event, including after subsequent head advancement.
    """

    def create(
        self, request: CreationRequest, context: CreationContext
    ) -> TransitionResult[LifecycleEntity]: ...

    def transition(
        self,
        entity_id: LifecycleEntityId,
        request: TransitionRequest[LifecycleState],
        context: TransitionContext,
    ) -> TransitionResult[LifecycleEntity]: ...

    def transition_batch(
        self,
        operations: tuple[
            tuple[
                LifecycleEntityId, TransitionRequest[LifecycleState], TransitionContext
            ],
            ...,
        ],
    ) -> tuple[TransitionResult[LifecycleEntity], ...]: ...
