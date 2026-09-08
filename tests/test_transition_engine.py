"""M7A transition mechanics and authoritative event contracts."""

from dataclasses import MISSING, FrozenInstanceError, dataclass, fields, replace
from datetime import UTC, datetime
from types import ModuleType
from uuid import UUID

import pytest

import symphony_k.domain.effect as effect_module
import symphony_k.domain.evaluation as evaluation_module
import symphony_k.domain.objective as objective_module
import symphony_k.domain.outcome as outcome_module
import symphony_k.domain.run as run_module
import symphony_k.domain.task as task_module
import symphony_k.domain.transition_engine as engine_module
from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArtifactRef,
    CausationId,
    CompletionPolicyRef,
    ConcurrencyConflict,
    CorrelationId,
    DomainEntityType,
    DomainEvent,
    DomainEventMetadata,
    DomainEventType,
    Effect,
    EffectId,
    EffectPayloadRef,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    Evaluation,
    EvaluationId,
    EvaluationMethodRef,
    EvaluationState,
    EvaluationTargetRef,
    EventId,
    ExecutionProfileRef,
    InvalidDomainValue,
    InvalidTransition,
    Objective,
    ObjectiveId,
    ObjectiveState,
    Outcome,
    OutcomeId,
    OutcomeState,
    PlannedEffectOrigin,
    Run,
    RunId,
    RunState,
    Task,
    TaskId,
    TaskState,
    Timestamp,
    TransitionContext,
    TransitionReason,
    TransitionRequest,
    TransitionResult,
    UnauthorizedTransition,
    transition_entity,
)
from symphony_k.domain.transition_engine import LifecycleEntity, LifecycleState

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
VERSION = EntityVersion(17)
EVENT_ID = EventId(VALUE)
CORRELATION_ID = CorrelationId(VALUE)
CAUSATION_ID = CausationId(OTHER)


def actor(category: ActorType = ActorType.SYSTEM) -> ActorIdentity:
    return ActorIdentity(ActorId(VALUE), category)


def instant() -> Timestamp:
    return Timestamp(datetime(2026, 9, 8, tzinfo=UTC))


@dataclass(frozen=True, slots=True)
class AllowingFoundationGuard:
    """Test-only guard showing the required M7B+ extension contract."""

    def validate(
        self,
        entity: LifecycleEntity,
        request: TransitionRequest[LifecycleState],
    ) -> None:
        assert entity.version == request.expected_version


@dataclass(frozen=True, slots=True)
class RejectingAuthorityGuard:
    def validate(
        self,
        entity: LifecycleEntity,
        request: TransitionRequest[LifecycleState],
    ) -> None:
        raise UnauthorizedTransition(
            f"{request.actor.actor_type.value} lacks authority for "
            f"{type(entity).__name__}"
        )


ALLOW_CONTEXT = TransitionContext((AllowingFoundationGuard(),))


def transition_request[StateT: LifecycleState](
    target: StateT,
    *,
    expected_version: EntityVersion = VERSION,
    causation_id: CausationId | None = CAUSATION_ID,
) -> TransitionRequest[StateT]:
    return TransitionRequest(
        EVENT_ID,
        target,
        actor(),
        TransitionReason("Foundation transition requested"),
        expected_version,
        instant(),
        CORRELATION_ID,
        causation_id,
    )


def objective() -> Objective:
    return Objective(
        ObjectiveId(VALUE),
        ObjectiveState.DRAFT,
        VERSION,
        "Deliver the bounded objective",
        ("The result is independently verifiable",),
        actor(ActorType.HUMAN_OPERATOR),
        CompletionPolicyRef("objective-completion", "v1"),
    )


def task() -> Task:
    return Task(
        TaskId(VALUE),
        TaskState.DRAFT,
        VERSION,
        "Perform one bounded unit of work",
        ObjectiveId(VALUE),
        CompletionPolicyRef("task-completion", "v1"),
    )


def run() -> Run:
    return Run(
        RunId(VALUE),
        TaskId(VALUE),
        RunState.PENDING,
        VERSION,
        ExecutionProfileRef("profile", "v1"),
    )


def outcome() -> Outcome:
    return Outcome(
        OutcomeId(VALUE),
        RunId(VALUE),
        OutcomeState.PROPOSED,
        VERSION,
        actor(ActorType.WORKER),
        frozenset({ArtifactRef("candidate")}),
    )


def evaluation() -> Evaluation:
    return Evaluation(
        EvaluationId(VALUE),
        EvaluationState.PENDING,
        VERSION,
        EvaluationTargetRef(OutcomeId(VALUE), EntityVersion(3)),
        EvaluationMethodRef("method", "v1"),
    )


def effect() -> Effect:
    return Effect(
        EffectId(VALUE),
        EffectState.PLANNED,
        VERSION,
        PlannedEffectOrigin(TaskId(VALUE), actor(ActorType.WORKER)),
        EffectTargetRef("target"),
        EffectPayloadRef("payload"),
    )


SUCCESS_CASES: tuple[tuple[LifecycleEntity, LifecycleState, DomainEventType], ...] = (
    (objective(), ObjectiveState.ACTIVE, DomainEventType.OBJECTIVE_ACTIVATED),
    (task(), TaskState.READY, DomainEventType.TASK_READIED),
    (run(), RunState.RUNNING, DomainEventType.RUN_STARTED),
    (
        outcome(),
        OutcomeState.VALIDATING,
        DomainEventType.OUTCOME_VALIDATION_STARTED,
    ),
    (
        evaluation(),
        EvaluationState.RUNNING,
        DomainEventType.EVALUATION_STARTED,
    ),
    (effect(), EffectState.SIMULATED, DomainEventType.EFFECT_SIMULATED),
)

CANONICAL_HELPER_CASES: tuple[
    tuple[ModuleType, str, LifecycleEntity, LifecycleState], ...
] = (
    (
        objective_module,
        "can_objective_transition",
        objective(),
        ObjectiveState.ACTIVE,
    ),
    (task_module, "can_task_transition", task(), TaskState.READY),
    (run_module, "can_run_transition", run(), RunState.RUNNING),
    (
        outcome_module,
        "can_outcome_transition",
        outcome(),
        OutcomeState.VALIDATING,
    ),
    (
        evaluation_module,
        "can_evaluation_transition",
        evaluation(),
        EvaluationState.RUNNING,
    ),
    (effect_module, "can_effect_transition", effect(), EffectState.SIMULATED),
)


@pytest.mark.parametrize(("snapshot", "target", "event_type"), SUCCESS_CASES)
def test_success_returns_new_snapshot_and_exactly_one_matching_event(
    snapshot: LifecycleEntity,
    target: LifecycleState,
    event_type: DomainEventType,
) -> None:
    before = tuple(getattr(snapshot, field.name) for field in fields(snapshot))
    result = transition_entity(
        snapshot,  # type: ignore[arg-type]
        transition_request(target),  # type: ignore[arg-type]
        ALLOW_CONTEXT,
    )
    assert isinstance(result, TransitionResult)
    assert tuple(field.name for field in fields(result)) == ("entity", "event")
    assert result.entity is not snapshot
    assert result.entity.state is target
    assert result.entity.version == EntityVersion(18)
    assert snapshot.version == VERSION
    assert tuple(getattr(snapshot, field.name) for field in fields(snapshot)) == before
    for field in fields(snapshot):
        if field.name not in {"state", "version"}:
            assert getattr(result.entity, field.name) == getattr(snapshot, field.name)
    assert result.event.event_id == EVENT_ID
    assert result.event.event_type is event_type
    assert result.event.entity_version == result.entity.version
    assert result.event.actor == actor()
    assert result.event.timestamp == instant()
    assert result.event.correlation_id == CORRELATION_ID
    assert result.event.causation_id == CAUSATION_ID
    assert result.event.reason == TransitionReason("Foundation transition requested")
    assert result.event.metadata.prior_state is snapshot.state
    assert result.event.metadata.new_state is target


def objective_event() -> DomainEvent:
    return transition_entity(
        objective(), transition_request(ObjectiveState.ACTIVE), ALLOW_CONTEXT
    ).event


def test_domain_event_and_metadata_are_frozen_and_typed() -> None:
    event = objective_event()
    metadata = DomainEventMetadata(
        ObjectiveState.DRAFT,
        ObjectiveState.ACTIVE,
        frozenset({("policy", "deferred-to-M7B")}),
    )
    annotated = replace(event, metadata=metadata)
    assert annotated.entity_type is DomainEntityType.OBJECTIVE
    assert annotated.entity_id == ObjectiveId(VALUE)
    assert annotated.metadata.annotations == frozenset({("policy", "deferred-to-M7B")})
    with pytest.raises(FrozenInstanceError):
        event.entity_version = EntityVersion(99)  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        metadata.new_state = ObjectiveState.BLOCKED  # type: ignore[misc]
    with pytest.raises(AttributeError):
        metadata.annotations.add(("extra", "value"))  # type: ignore[attr-defined]


def test_event_and_entity_type_inventories_are_closed_and_complete() -> None:
    assert len(DomainEntityType) == 6
    assert len(DomainEventType) == 43
    assert len(DomainEntityType.__members__) == 6
    assert len(DomainEventType.__members__) == 43


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("event_id", CorrelationId(VALUE)),
        ("event_type", "ObjectiveActivated"),
        ("entity_type", "OBJECTIVE"),
        ("entity_id", TaskId(VALUE)),
        ("entity_version", 18),
        ("actor", ActorId(VALUE)),
        ("timestamp", datetime(2026, 9, 8, tzinfo=UTC)),
        ("correlation_id", EventId(VALUE)),
        ("causation_id", EventId(VALUE)),
        ("reason", "reason"),
        ("metadata", (ObjectiveState.DRAFT, ObjectiveState.ACTIVE)),
    ],
)
def test_domain_event_rejects_raw_or_wrong_typed_provenance(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(objective_event(), **{field: invalid})  # type: ignore[arg-type]


def test_domain_event_rejects_inconsistent_lifecycle_meaning() -> None:
    event = objective_event()
    with pytest.raises(InvalidDomainValue):
        replace(event, event_type=DomainEventType.OBJECTIVE_BLOCKED)
    with pytest.raises(InvalidDomainValue):
        replace(
            event,
            metadata=DomainEventMetadata(ObjectiveState.DRAFT, ObjectiveState.ARCHIVED),
        )
    with pytest.raises(InvalidDomainValue):
        DomainEventMetadata(ObjectiveState.DRAFT, TaskState.READY)
    with pytest.raises(InvalidDomainValue):
        DomainEventMetadata(ObjectiveState.DRAFT, ObjectiveState.DRAFT)


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("event_id", CorrelationId(VALUE)),
        ("target_state", "ACTIVE"),
        ("actor", ActorId(VALUE)),
        ("reason", "reason"),
        ("expected_version", 17),
        ("timestamp", datetime(2026, 9, 8, tzinfo=UTC)),
        ("correlation_id", EventId(VALUE)),
        ("causation_id", EventId(VALUE)),
    ],
)
def test_transition_request_rejects_raw_or_wrong_typed_values(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(
            transition_request(ObjectiveState.ACTIVE),
            **{field: invalid},  # type: ignore[arg-type]
        )


def test_request_context_and_result_are_immutable_supporting_records() -> None:
    request = transition_request(ObjectiveState.ACTIVE)
    result = transition_entity(objective(), request, ALLOW_CONTEXT)
    with pytest.raises(FrozenInstanceError):
        request.expected_version = EntityVersion(99)  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        ALLOW_CONTEXT.guards = ()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.entity = objective()  # type: ignore[misc]
    with pytest.raises(InvalidDomainValue):
        replace(
            result,
            event=replace(result.event, entity_version=EntityVersion(99)),
        )


def test_creation_uses_absence_not_a_none_lifecycle_state() -> None:
    creation = DomainEvent(
        EventId(VALUE),
        DomainEventType.OBJECTIVE_CREATED,
        DomainEntityType.OBJECTIVE,
        ObjectiveId(VALUE),
        EntityVersion(0),
        actor(),
        instant(),
        CORRELATION_ID,
        None,
        TransitionReason("Objective registered"),
        DomainEventMetadata(None, ObjectiveState.DRAFT),
    )
    assert creation.metadata.prior_state is None
    for state_type in (
        ObjectiveState,
        TaskState,
        RunState,
        OutcomeState,
        EvaluationState,
        EffectState,
    ):
        assert "NONE" not in state_type.__members__
    with pytest.raises(InvalidDomainValue):
        replace(
            creation,
            event_type=DomainEventType.OBJECTIVE_ACTIVATED,
            metadata=DomainEventMetadata(None, ObjectiveState.ACTIVE),
        )


@pytest.mark.parametrize("expected", [EntityVersion(16), EntityVersion(18)])
def test_nonmatching_expected_version_rejects_without_mutation(
    expected: EntityVersion,
) -> None:
    snapshot = objective()
    before = (snapshot.state, snapshot.version)
    with pytest.raises(ConcurrencyConflict):
        transition_entity(
            snapshot,
            transition_request(ObjectiveState.ACTIVE, expected_version=expected),
            ALLOW_CONTEXT,
        )
    assert (snapshot.state, snapshot.version) == before


@pytest.mark.parametrize("target", [ObjectiveState.DRAFT, ObjectiveState.ARCHIVED])
def test_same_state_and_unsupported_edges_reject_without_result(
    target: ObjectiveState,
) -> None:
    snapshot = objective()
    with pytest.raises(InvalidTransition):
        transition_entity(snapshot, transition_request(target), ALLOW_CONTEXT)
    assert snapshot.state is ObjectiveState.DRAFT
    assert snapshot.version == VERSION


def test_cross_entity_state_rejects_as_invalid_transition() -> None:
    snapshot = objective()
    with pytest.raises(InvalidTransition):
        transition_entity(
            snapshot,
            transition_request(TaskState.READY),  # type: ignore[arg-type]
            ALLOW_CONTEXT,
        )
    assert snapshot.state is ObjectiveState.DRAFT


def test_guard_rejection_produces_no_snapshot_or_event() -> None:
    snapshot = run()
    rejecting_context = TransitionContext((RejectingAuthorityGuard(),))
    with pytest.raises(UnauthorizedTransition):
        transition_entity(
            snapshot,
            transition_request(RunState.RUNNING),
            rejecting_context,
        )
    assert snapshot.state is RunState.PENDING
    assert snapshot.version == VERSION


def test_context_requires_explicit_typed_guards_and_has_no_permissive_default() -> None:
    with pytest.raises(InvalidDomainValue):
        TransitionContext(())
    with pytest.raises(InvalidDomainValue):
        TransitionContext((object(),))  # type: ignore[arg-type]
    definitions = {field.name: field for field in fields(TransitionContext)}
    assert definitions["guards"].default is MISSING


def test_engine_delegates_to_the_canonical_topology_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[ObjectiveState, ObjectiveState]] = []
    canonical = objective_module.can_objective_transition

    def recording_helper(source: ObjectiveState, target: ObjectiveState) -> bool:
        calls.append((source, target))
        return canonical(source, target)

    monkeypatch.setattr(
        objective_module,
        "can_objective_transition",
        recording_helper,
    )
    transition_entity(
        objective(), transition_request(ObjectiveState.ACTIVE), ALLOW_CONTEXT
    )
    assert calls
    assert set(calls) == {(ObjectiveState.DRAFT, ObjectiveState.ACTIVE)}


@pytest.mark.parametrize(
    ("topology_module", "helper_name", "snapshot", "target"),
    CANONICAL_HELPER_CASES,
)
def test_every_entity_family_depends_on_its_canonical_topology_helper(
    monkeypatch: pytest.MonkeyPatch,
    topology_module: ModuleType,
    helper_name: str,
    snapshot: LifecycleEntity,
    target: LifecycleState,
) -> None:
    monkeypatch.setattr(
        topology_module,
        helper_name,
        lambda source, target: False,
    )
    with pytest.raises(InvalidTransition):
        transition_entity(
            snapshot,  # type: ignore[arg-type]
            transition_request(target),  # type: ignore[arg-type]
            ALLOW_CONTEXT,
        )
    assert not any(name.endswith("_TRANSITIONS") for name in vars(engine_module))


def test_existing_snapshot_invariant_rejection_is_typed_and_has_no_partial_result() -> (
    None
):
    snapshot = replace(evaluation(), state=EvaluationState.RUNNING)
    with pytest.raises(InvalidDomainValue):
        transition_entity(
            snapshot,
            transition_request(EvaluationState.COMPLETED),
            ALLOW_CONTEXT,
        )
    assert snapshot.state is EvaluationState.RUNNING
    assert snapshot.result is None
    assert snapshot.version == VERSION


def test_transition_foundation_has_no_m7b_or_m8_runtime_boundaries() -> None:
    for name in (
        "Repository",
        "UnitOfWork",
        "Transaction",
        "Persistence",
        "Outbox",
        "MessageBus",
        "CompletionPolicyEvaluator",
        "PolicyEngine",
        "PermissionEngine",
        "EffectExecutor",
        "execute_effect",
        "resolve_evaluation",
        "failover",
    ):
        assert not hasattr(engine_module, name)
    result = transition_entity(
        effect(), transition_request(EffectState.SIMULATED), ALLOW_CONTEXT
    )
    assert result.entity.state is EffectState.SIMULATED
    assert effect().state is EffectState.PLANNED
