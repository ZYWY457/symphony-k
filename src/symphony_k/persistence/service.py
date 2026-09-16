"""Authoritative atomic lifecycle operations over a database-neutral adapter port."""

from collections.abc import Callable
from dataclasses import fields
from typing import cast

from symphony_k.domain import (
    ConcurrencyConflict,
    CreationContext,
    CreationRequest,
    Effect,
    EffectState,
    EntityNotFound,
    InvariantViolation,
    create_entity,
    transition_entity,
)
from symphony_k.domain.creation import ObservedEffectCreationSemanticInput
from symphony_k.domain.creation_relationships import (
    CreationObservationStatus,
    CreationRelationshipObservation,
)
from symphony_k.domain.creation_semantics import (
    TaskObjectiveObservation,
    TaskObjectiveObservationStatus,
)
from symphony_k.domain.transition_engine import (
    LifecycleEntity,
    LifecycleEntityId,
    LifecycleState,
    TransitionContext,
    TransitionRequest,
    TransitionResult,
)

from ._records import walk
from ._storage import Storage
from .codec import fingerprint
from .effect import validate_effect_historical_provenance
from .evaluation import validate_evaluation_batch

type TransitionOperation = tuple[
    LifecycleEntityId, TransitionRequest[LifecycleState], TransitionContext
]

_transition = cast(
    Callable[
        [LifecycleEntity, TransitionRequest[LifecycleState], TransitionContext],
        TransitionResult[LifecycleEntity],
    ],
    transition_entity,
)


def transition_provenance(context: TransitionContext) -> tuple[tuple[str, object], ...]:
    """Persist authority and immutable semantic inputs, never executable guards."""
    return tuple(
        (field.name, getattr(context, field.name))
        for field in fields(context)
        if field.name != "guards"
    )


class LifecycleService:
    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    def create(
        self, request: CreationRequest, context: CreationContext
    ) -> TransitionResult[LifecycleEntity]:
        digest = fingerprint(request)
        with self._storage._transaction():
            replay = self._storage._replay(request.event_id, digest)
            if replay is not None:
                return replay
            created = create_entity(request, context)
            try:
                self._storage.load(request.entity_id)
            except EntityNotFound:
                pass
            else:
                raise ConcurrencyConflict("Creation identity is already durable")
            self._require_creation_currentness(request)
            semantic = request.semantic_input
            if isinstance(semantic, ObservedEffectCreationSemanticInput):
                registration = semantic.registration
                assert registration is not None
                self._storage._reserve_occurrence(
                    registration.spec.origin.external_operation_ref.value,
                    registration.deduplication_ref.value,
                    str(request.entity_id),
                )
            result = TransitionResult(created.entity, created.event)
            self._storage._append(result, None)
            provenance = (context.authority_decision, context.identifier_availability)
            self._storage._record_provenance(request, request.event_id)
            self._storage._record_operation(
                request.event_id, digest, request, provenance
            )
            return result

    def transition(
        self,
        entity_id: LifecycleEntityId,
        request: TransitionRequest[LifecycleState],
        context: TransitionContext,
    ) -> TransitionResult[LifecycleEntity]:
        return self.transition_batch(((entity_id, request, context),))[0]

    def transition_batch(
        self, operations: tuple[TransitionOperation, ...]
    ) -> tuple[TransitionResult[LifecycleEntity], ...]:
        """Validate all participants against one view, then commit all or none."""
        if not operations or len({item[0] for item in operations}) != len(operations):
            raise InvariantViolation("Batch requires distinct entity identities")
        if len({item[1].event_id for item in operations}) != len(operations):
            raise InvariantViolation("Batch requires distinct event identities")
        digests = tuple(
            fingerprint((entity_id, request)) for entity_id, request, _ in operations
        )
        with self._storage._transaction():
            replays = tuple(
                self._storage._replay(request.event_id, digest)
                for (_, request, _), digest in zip(operations, digests, strict=True)
            )
            if all(result is not None for result in replays):
                return cast(tuple[TransitionResult[LifecycleEntity], ...], replays)
            if any(result is not None for result in replays):
                raise ConcurrencyConflict(
                    "Cannot mix prior operations and new batch writes"
                )
            sources = tuple(self._storage.load(item[0]) for item in operations)
            results = []
            for source, (_, request, context) in zip(sources, operations, strict=True):
                if source.version != request.expected_version:
                    raise ConcurrencyConflict(
                        "Stored version differs from expected version"
                    )
                if isinstance(source, Effect):
                    validate_effect_historical_provenance(
                        self._storage,
                        source,
                        cast(TransitionRequest[EffectState], request),
                        context,
                    )
                for event in (
                    context.effect_compensation_start_event,
                    context.effect_prior_compensation_start_event,
                ):
                    if (
                        event is not None
                        and self._storage.events.load(event.event_id) != event
                    ):
                        raise ConcurrencyConflict(
                            "Historical event differs from durable event"
                        )
                results.append(_transition(source, request, context))
            validate_evaluation_batch(self._storage, operations, sources)
            for result, (_, request, context), digest in zip(
                results, operations, digests, strict=True
            ):
                self._storage._append(result, request.expected_version)
                provenance = transition_provenance(context)
                self._storage._record_provenance(provenance, request.event_id)
                self._storage._record_operation(
                    request.event_id,
                    digest,
                    (result.event.entity_id, request),
                    provenance,
                )
            return tuple(results)

    def _require_creation_currentness(self, request: CreationRequest) -> None:
        for item in walk(request.semantic_input):
            if isinstance(item, CreationRelationshipObservation):
                if item.status is not CreationObservationStatus.CURRENT:
                    continue  # The canonical domain guard owns status rejection.
                try:
                    stored = self._storage.load(item.entity_id)
                except EntityNotFound as exc:
                    raise ConcurrencyConflict(
                        "Observed related entity is no longer current"
                    ) from exc
                if stored != item.snapshot:
                    raise ConcurrencyConflict(
                        "Related snapshot differs from durable head"
                    )
            elif isinstance(item, TaskObjectiveObservation):
                if item.status is not TaskObjectiveObservationStatus.CURRENT:
                    continue
                try:
                    stored = self._storage.load(item.objective_id)
                except EntityNotFound as exc:
                    raise ConcurrencyConflict(
                        "Observed Objective is no longer current"
                    ) from exc
                if (
                    stored.version != item.observed_entity_version
                    or stored.state != item.observed_state
                ):
                    raise ConcurrencyConflict(
                        "Objective observation differs from durable head"
                    )
