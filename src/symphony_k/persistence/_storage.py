"""Internal adapter port. Applications use UnitOfWork and read repositories."""

from contextlib import AbstractContextManager
from typing import Protocol

from symphony_k.domain import EntityVersion, EventId
from symphony_k.domain.transition_engine import (
    LifecycleEntity,
    LifecycleEntityId,
    TransitionResult,
)

from .ports import EventRepository


class Storage(Protocol):
    @property
    def events(self) -> EventRepository: ...

    def load(self, entity_id: LifecycleEntityId) -> LifecycleEntity: ...

    def _transaction(self) -> AbstractContextManager[None]: ...

    def _append(
        self, result: TransitionResult[LifecycleEntity], expected: EntityVersion | None
    ) -> None: ...

    def _record_operation(
        self, event_id: EventId, digest: str, request: object, provenance: object
    ) -> None: ...

    def _replay(
        self, event_id: EventId, digest: str
    ) -> TransitionResult[LifecycleEntity] | None: ...

    def _reserve_occurrence(
        self, operation: str, deduplication: str, entity_id: str
    ) -> None: ...

    def _records(self, record_type: type) -> tuple[object, ...]: ...

    def _record_provenance(self, value: object, event_id: EventId) -> None: ...
