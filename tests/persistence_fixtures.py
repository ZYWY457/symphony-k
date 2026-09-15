"""Trusted historical fixtures for adapter integration; no public import API."""

from dataclasses import replace

from symphony_k.domain import (
    CreationRequest,
    DomainEntityType,
    DomainEvent,
    DomainEventMetadata,
    Effect,
    EntityNotFound,
    Evaluation,
    EventId,
    Objective,
    Outcome,
    Run,
    Task,
    create_entity,
)
from symphony_k.domain.creation_relationships import CreationRelationshipObservation
from symphony_k.domain.creation_semantics import TaskObjectiveObservation
from symphony_k.domain.transition_engine import (
    _EVENT_TYPE_BY_STATE,
    LifecycleEntity,
    LifecycleEntityId,
    TransitionResult,
    _can_transition,
    _is_creation_target,
    _replace_entity_state,
)
from symphony_k.persistence._records import walk
from symphony_k.persistence.sqlite import SQLiteStore, entity_key, snapshot_id
from tests.test_creation_integrated import CASES, creation_context


def seed_snapshot(store: SQLiteStore, entity: LifecycleEntity) -> None:
    """Install one trusted historical boundary, with its structurally legal event."""
    identity = snapshot_id(entity)
    try:
        store.load(identity)
    except EntityNotFound:
        pass
    else:
        return
    if isinstance(entity, Task):
        parent = create_entity(CASES[0], creation_context(CASES[0])).entity
        assert isinstance(parent, Objective)
        seed_snapshot(store, replace(parent, objective_id=entity.primary_objective_id))
    if isinstance(entity, Run):
        parent = create_entity(CASES[1], creation_context(CASES[1])).entity
        assert isinstance(parent, Task)
        seed_snapshot(store, replace(parent, task_id=entity.task_id))
    if isinstance(entity, Outcome):
        parent = create_entity(CASES[2], creation_context(CASES[2])).entity
        assert isinstance(parent, Run)
        seed_snapshot(store, replace(parent, run_id=entity.run_id))
    if isinstance(entity, Effect) and entity.origin.task_id:
        parent = create_entity(CASES[1], creation_context(CASES[1])).entity
        assert isinstance(parent, Task)
        seed_snapshot(store, replace(parent, task_id=entity.origin.task_id))
        if entity.origin.run_id:
            run = create_entity(CASES[2], creation_context(CASES[2])).entity
            assert isinstance(run, Run)
            seed_snapshot(
                store,
                replace(
                    run, run_id=entity.origin.run_id, task_id=entity.origin.task_id
                ),
            )
    template = create_entity(CASES[0], creation_context(CASES[0])).event
    kind = DomainEntityType(entity_key(identity)[0])
    prior = (
        None
        if _is_creation_target(kind, entity.state)
        else next(
            state
            for state in type(entity.state)
            if _can_transition(kind, state, entity.state)
        )
    )
    event = DomainEvent(
        EventId.new(),
        _EVENT_TYPE_BY_STATE[entity.state],
        kind,
        identity,
        entity.version,
        template.actor,
        template.timestamp,
        template.correlation_id,
        template.causation_id,
        template.reason,
        DomainEventMetadata(prior, entity.state),
    )
    with store._transaction():
        store._append(TransitionResult(entity, event), None)


def seed_related(
    store: SQLiteStore, request: CreationRequest
) -> tuple[LifecycleEntityId, ...]:
    snapshots: dict[LifecycleEntityId, LifecycleEntity] = {}
    for item in walk(request.semantic_input):
        if (
            isinstance(item, CreationRelationshipObservation)
            and item.snapshot is not None
        ):
            snapshots[snapshot_id(item.snapshot)] = item.snapshot
        elif (
            isinstance(item, TaskObjectiveObservation) and item.observed_entity_version
        ):
            template = create_entity(CASES[0], creation_context(CASES[0])).entity
            assert isinstance(template, Objective) and item.observed_state is not None
            snapshots[item.objective_id] = replace(
                template,
                objective_id=item.objective_id,
                version=item.observed_entity_version,
                state=item.observed_state,
            )
    order = {Objective: 0, Task: 1, Run: 2, Outcome: 3, Evaluation: 4, Effect: 5}
    for snapshot in sorted(snapshots.values(), key=lambda item: order[type(item)]):
        seed_snapshot(store, snapshot)
    return tuple(snapshots)


def advance_fixture(store: SQLiteStore, identity: LifecycleEntityId) -> None:
    """Simulate another independently trusted writer advancing a related head."""
    current = store.load(identity)
    kind = DomainEntityType(entity_key(identity)[0])
    target = next(
        state
        for state in type(current.state)
        if _can_transition(kind, current.state, state)
    )
    updated = _replace_entity_state(current, target, current.version.next())
    template = store.events.for_entity(identity)[-1]
    event = replace(
        template,
        event_id=EventId.new(),
        event_type=_EVENT_TYPE_BY_STATE[target],
        entity_version=updated.version,
        metadata=DomainEventMetadata(current.state, target),
    )
    with store._transaction():
        store._append(TransitionResult(updated, event), current.version)


def data_rows(store: SQLiteStore) -> tuple[tuple[tuple[object, ...], ...], ...]:
    return tuple(
        tuple(
            store._connection.execute(f"SELECT * FROM {table} ORDER BY 1,2").fetchall()
        )
        for table in (
            "heads",
            "entity_versions",
            "events",
            "operations",
            "supporting_records",
            "observed_occurrences",
        )
    )
