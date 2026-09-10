"""M7C3B2 canonical Run reassignment semantic guards."""

from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CorrelationId,
    EntityVersion,
    EventId,
    EvidenceRef,
    ExecutionProfileRef,
    InvalidDomainValue,
    InvariantViolation,
    Run,
    RunAcceptedHumanHandoffDecision,
    RunExecutionRouteUnsuitabilityDecision,
    RunHumanHandoffRef,
    RunId,
    RunOwnershipFencingDecision,
    RunReassignDecision,
    RunReassignmentSemantics,
    RunSemanticDecisionRef,
    RunSemanticDecisionStatus,
    RunSemanticGuard,
    RunState,
    RunSuccessorRunObservation,
    RunTransferExclusivityDecision,
    TaskId,
    Timestamp,
    TransitionAuthorityDecision,
    TransitionAuthorityStatus,
    TransitionContext,
    TransitionReason,
    TransitionRequest,
    transition_entity,
)
from symphony_k.domain.transition_engine import (
    DomainEntityType,
    LifecycleEntity,
    LifecycleState,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
RUN_VERSION = EntityVersion(7)
SUCCESSOR_VERSION = EntityVersion(3)
CORRELATION = CorrelationId(VALUE)
PROFILE = ExecutionProfileRef("approved-profile", "v3")
CURRENT_RUN_ID = RunId(VALUE)
SUCCESSOR_RUN_ID = RunId(OTHER)
CURRENT_TASK_ID = TaskId(VALUE)
LIFECYCLE_AUTHORITY = ActorIdentity(ActorId(VALUE), ActorType.RUN_CONTROLLER)
RECOVERY_AUTHORITY = ActorIdentity(ActorId(OTHER), ActorType.RUN_CONTROLLER)
DECISION_AUTHORITY = ActorIdentity(ActorId(OTHER), ActorType.POLICY_ENGINE)


def run(state: RunState) -> Run:
    return Run(CURRENT_RUN_ID, CURRENT_TASK_ID, state, RUN_VERSION, PROFILE)


def evidence(name: str) -> frozenset[EvidenceRef]:
    return frozenset({EvidenceRef(name)})


def decision[DecisionT](
    decision_type: type[DecisionT],
    name: str,
    *,
    status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    actor: ActorIdentity = DECISION_AUTHORITY,
) -> DecisionT:
    return decision_type(  # type: ignore[call-arg]
        RunSemanticDecisionRef(name),
        status,
        actor,
        evidence(name),
        CURRENT_RUN_ID,
        RUN_VERSION,
        CORRELATION,
    )


def successor_observation(
    *,
    successor_id: RunId = SUCCESSOR_RUN_ID,
    task_id: TaskId = CURRENT_TASK_ID,
    predecessor_id: RunId = CURRENT_RUN_ID,
    state: RunState = RunState.PENDING,
    status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    actor: ActorIdentity = RECOVERY_AUTHORITY,
) -> RunSuccessorRunObservation:
    return RunSuccessorRunObservation(
        RunSemanticDecisionRef("successor-run"),
        status,
        actor,
        evidence("successor-run"),
        CURRENT_RUN_ID,
        RUN_VERSION,
        CORRELATION,
        successor_id,
        SUCCESSOR_VERSION,
        task_id,
        predecessor_id,
        state,
    )


def human_handoff(
    *,
    handoff_ref: RunHumanHandoffRef | None = None,
    status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    actor: ActorIdentity = RECOVERY_AUTHORITY,
) -> RunAcceptedHumanHandoffDecision:
    if handoff_ref is None:
        handoff_ref = RunHumanHandoffRef("handoff/record-1")
    return RunAcceptedHumanHandoffDecision(
        RunSemanticDecisionRef("human-handoff"),
        status,
        actor,
        evidence("human-handoff"),
        CURRENT_RUN_ID,
        RUN_VERSION,
        CORRELATION,
        handoff_ref,
    )


def transfer_exclusivity(
    *,
    successor: RunSuccessorRunObservation | None = None,
    handoff: RunAcceptedHumanHandoffDecision | None = None,
    status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    actor: ActorIdentity = DECISION_AUTHORITY,
) -> RunTransferExclusivityDecision:
    if successor is None and handoff is None:
        successor = successor_observation()
    return RunTransferExclusivityDecision(
        RunSemanticDecisionRef("transfer-exclusivity"),
        status,
        actor,
        evidence("transfer-exclusivity"),
        CURRENT_RUN_ID,
        RUN_VERSION,
        CORRELATION,
        successor.successor_run_id if successor is not None else None,
        successor.observed_successor_version if successor is not None else None,
        handoff.handoff_ref if handoff is not None else None,
    )


def semantics(
    *,
    reassign: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    reassign_actor: ActorIdentity = RECOVERY_AUTHORITY,
    fencing: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    fencing_actor: ActorIdentity = DECISION_AUTHORITY,
    unsuitable: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    unsuitable_actor: ActorIdentity = DECISION_AUTHORITY,
    successor: RunSuccessorRunObservation | None = None,
    handoff: RunAcceptedHumanHandoffDecision | None = None,
    exclusivity: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    exclusivity_actor: ActorIdentity = DECISION_AUTHORITY,
) -> RunReassignmentSemantics:
    selected_successor = (
        successor_observation() if successor is None and handoff is None else successor
    )
    return RunReassignmentSemantics(
        decision(
            RunReassignDecision, "reassign", status=reassign, actor=reassign_actor
        ),
        decision(
            RunOwnershipFencingDecision,
            "ownership-fencing",
            status=fencing,
            actor=fencing_actor,
        ),
        decision(
            RunExecutionRouteUnsuitabilityDecision,
            "route-unsuitability",
            status=unsuitable,
            actor=unsuitable_actor,
        ),
        selected_successor,
        handoff,
        transfer_exclusivity(
            successor=selected_successor,
            handoff=handoff,
            status=exclusivity,
            actor=exclusivity_actor,
        ),
    )


def request(target: RunState) -> TransitionRequest[RunState]:
    return TransitionRequest(
        EventId(VALUE),
        target,
        LIFECYCLE_AUTHORITY,
        TransitionReason("Run reassignment semantic transition"),
        RUN_VERSION,
        Timestamp(datetime(2026, 9, 10, 12, tzinfo=UTC)),
        CORRELATION,
    )


def guard(snapshot: Run, semantic: RunReassignmentSemantics) -> RunSemanticGuard:
    return RunSemanticGuard(
        snapshot.run_id,
        snapshot.version,
        snapshot.state,
        RunState.REASSIGNED,
        CORRELATION,
        semantic,
    )


class PassingGuard:
    def validate(
        self,
        entity: LifecycleEntity,
        transition_request: TransitionRequest[LifecycleState],
    ) -> None:
        assert entity.version == transition_request.expected_version


def context(
    snapshot: Run,
    transition_request: TransitionRequest[RunState],
    guard: RunSemanticGuard,
) -> TransitionContext:
    authority = TransitionAuthorityDecision(
        transition_request.actor,
        DomainEntityType.RUN,
        snapshot.run_id,
        snapshot.version,
        snapshot.state,
        transition_request.target_state,
        TransitionAuthorityStatus.AUTHORIZED,
        transition_request.correlation_id,
    )
    return TransitionContext((PassingGuard(),), authority, run_semantic_guard=guard)


@pytest.mark.parametrize(
    "source",
    (
        RunState.PENDING,
        RunState.RUNNING,
        RunState.WAITING_FOR_VERIFICATION,
        RunState.RETRYING,
    ),
)
def test_every_reassignment_edge_requires_canonical_semantics_and_preserves_old_run(
    source: RunState,
) -> None:
    snapshot = run(source)
    transition_request = request(RunState.REASSIGNED)
    result = transition_entity(
        snapshot,
        transition_request,
        context(snapshot, transition_request, guard(snapshot, semantics())),
    )
    assert result.entity.state is RunState.REASSIGNED
    assert result.entity.version == RUN_VERSION.next()
    assert result.entity.run_id == snapshot.run_id
    assert result.entity.task_id == snapshot.task_id
    assert result.entity.execution_profile_ref == snapshot.execution_profile_ref
    assert result.entity.predecessor_run_id == snapshot.predecessor_run_id
    assert (snapshot.state, snapshot.version) == (source, RUN_VERSION)


def test_accepted_human_handoff_is_an_alternative_durable_transfer_target() -> None:
    snapshot = run(RunState.RUNNING)
    transition_request = request(RunState.REASSIGNED)
    semantic = semantics(successor=None, handoff=human_handoff())
    assert (
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, guard(snapshot, semantic)),
        ).entity.state
        is RunState.REASSIGNED
    )


def test_successor_exclusivity_binds_the_exact_successor_snapshot() -> None:
    successor = successor_observation()
    exclusivity = transfer_exclusivity(successor=successor)
    assert exclusivity.successor_run_id == successor.successor_run_id
    assert (
        exclusivity.observed_successor_version == successor.observed_successor_version
    )
    assert exclusivity.human_handoff_ref is None


def test_handoff_exclusivity_binds_the_exact_accepted_handoff() -> None:
    handoff = human_handoff()
    exclusivity = transfer_exclusivity(handoff=handoff)
    assert exclusivity.successor_run_id is None
    assert exclusivity.observed_successor_version is None
    assert exclusivity.human_handoff_ref == handoff.handoff_ref


@pytest.mark.parametrize(
    "replacement",
    (
        lambda semantic: transfer_exclusivity(
            successor=successor_observation(successor_id=RunId(VALUE))
        ),
        lambda semantic: transfer_exclusivity(
            successor=replace(
                semantic.successor_run,
                observed_successor_version=EntityVersion(4),
            )
        ),
        lambda semantic: transfer_exclusivity(handoff=human_handoff()),
    ),
)
def test_successor_exclusivity_cannot_be_reused_for_a_different_target(
    replacement: object,
) -> None:
    snapshot = run(RunState.RUNNING)
    transition_request = request(RunState.REASSIGNED)
    semantic = semantics()
    semantic = replace(
        semantic,
        transfer_exclusivity=replacement(semantic),  # type: ignore[operator]
    )
    with pytest.raises(InvariantViolation, match="selected successor Run snapshot"):
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, guard(snapshot, semantic)),
        )


@pytest.mark.parametrize(
    "replacement",
    (
        lambda: transfer_exclusivity(
            handoff=human_handoff(handoff_ref=RunHumanHandoffRef("handoff/record-2"))
        ),
        lambda: transfer_exclusivity(successor=successor_observation()),
    ),
)
def test_handoff_exclusivity_cannot_be_reused_for_a_different_target(
    replacement: object,
) -> None:
    snapshot = run(RunState.RUNNING)
    transition_request = request(RunState.REASSIGNED)
    semantic = semantics(successor=None, handoff=human_handoff())
    semantic = replace(
        semantic,
        transfer_exclusivity=replacement(),  # type: ignore[operator]
    )
    with pytest.raises(InvariantViolation, match="accepted human handoff"):
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, guard(snapshot, semantic)),
        )


@pytest.mark.parametrize(
    ("successor_id", "successor_version", "handoff_ref"),
    (
        (None, None, None),
        (SUCCESSOR_RUN_ID, SUCCESSOR_VERSION, RunHumanHandoffRef("handoff/record-1")),
        (SUCCESSOR_RUN_ID, None, None),
        ("not-a-run-id", SUCCESSOR_VERSION, None),
        (SUCCESSOR_RUN_ID, "not-a-version", None),
        (None, None, "not-a-handoff-ref"),
    ),
)
def test_exclusivity_rejects_ambiguous_incomplete_and_untyped_targets(
    successor_id: object,
    successor_version: object,
    handoff_ref: object,
) -> None:
    with pytest.raises(InvalidDomainValue):
        RunTransferExclusivityDecision(
            RunSemanticDecisionRef("transfer-exclusivity"),
            RunSemanticDecisionStatus.PASSED,
            DECISION_AUTHORITY,
            evidence("transfer-exclusivity"),
            CURRENT_RUN_ID,
            RUN_VERSION,
            CORRELATION,
            successor_id,  # type: ignore[arg-type]
            successor_version,  # type: ignore[arg-type]
            handoff_ref,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("actor_type", ActorType)
def test_reassign_decision_accepts_exactly_canonical_recovery_authorities(
    actor_type: ActorType,
) -> None:
    actor = ActorIdentity(ActorId(OTHER), actor_type)
    if actor_type in {ActorType.SCHEDULER, ActorType.RUN_CONTROLLER}:
        assert isinstance(
            decision(RunReassignDecision, "reassign", actor=actor), RunReassignDecision
        )
    else:
        with pytest.raises(InvalidDomainValue, match="SCHEDULER or RUN_CONTROLLER"):
            decision(RunReassignDecision, "reassign", actor=actor)


@pytest.mark.parametrize(
    "field", ("ownership_fencing", "route_unsuitability", "transfer_exclusivity")
)
def test_worker_cannot_authoritatively_establish_reassignment_safety(
    field: str,
) -> None:
    snapshot = run(RunState.RUNNING)
    transition_request = request(RunState.REASSIGNED)
    worker = ActorIdentity(ActorId(OTHER), ActorType.WORKER)
    semantic = semantics()
    semantic = replace(
        semantic, **{field: replace(getattr(semantic, field), decided_by=worker)}
    )
    with pytest.raises(
        InvariantViolation, match="Worker cannot authoritatively establish"
    ):
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, guard(snapshot, semantic)),
        )


@pytest.mark.parametrize(
    "semantic",
    (
        pytest.param(lambda: semantics(reassign=RunSemanticDecisionStatus.UNRESOLVED)),
        pytest.param(lambda: semantics(fencing=RunSemanticDecisionStatus.REJECTED)),
        pytest.param(
            lambda: semantics(unsuitable=RunSemanticDecisionStatus.UNRESOLVED)
        ),
        pytest.param(lambda: semantics(exclusivity=RunSemanticDecisionStatus.REJECTED)),
        pytest.param(
            lambda: semantics(
                successor=successor_observation(
                    status=RunSemanticDecisionStatus.REJECTED
                )
            )
        ),
        pytest.param(
            lambda: semantics(
                successor=None,
                handoff=human_handoff(status=RunSemanticDecisionStatus.UNRESOLVED),
            )
        ),
    ),
)
def test_missing_or_unresolved_reassignment_conditions_reject(semantic: object) -> None:
    snapshot = run(RunState.RETRYING)
    transition_request = request(RunState.REASSIGNED)
    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, guard(snapshot, semantic())),  # type: ignore[operator]
        )
    assert (snapshot.state, snapshot.version) == (RunState.RETRYING, RUN_VERSION)


def test_reassignment_requires_exactly_one_transfer_target() -> None:
    base = semantics()
    with pytest.raises(InvalidDomainValue, match="exactly one"):
        replace(base, successor_run=None)
    with pytest.raises(InvalidDomainValue, match="exactly one"):
        replace(base, human_handoff=human_handoff())


@pytest.mark.parametrize(
    "successor",
    (
        lambda: successor_observation(successor_id=RunId(VALUE)),
        lambda: successor_observation(task_id=TaskId(OTHER)),
        lambda: successor_observation(predecessor_id=RunId(OTHER)),
        lambda: successor_observation(state=RunState.RUNNING),
    ),
)
def test_successor_target_must_be_a_distinct_pending_same_task_child(
    successor: object,
) -> None:
    snapshot = run(RunState.RUNNING)
    transition_request = request(RunState.REASSIGNED)
    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard(snapshot, semantics(successor=successor())),  # type: ignore[operator]
            ),
        )


def test_successor_observation_retains_own_version_without_mutation() -> None:
    snapshot = run(RunState.RUNNING)
    successor = successor_observation()
    transition_request = request(RunState.REASSIGNED)
    transition_entity(
        snapshot,
        transition_request,
        context(
            snapshot,
            transition_request,
            guard(snapshot, semantics(successor=successor)),
        ),
    )
    assert successor.observed_successor_version == SUCCESSOR_VERSION
    assert successor.observed_successor_state is RunState.PENDING


@pytest.mark.parametrize(
    "field", ("run_id", "observed_entity_version", "correlation_id")
)
def test_stale_cross_run_and_cross_correlation_decisions_cannot_be_laundered(
    field: str,
) -> None:
    snapshot = run(RunState.PENDING)
    transition_request = request(RunState.REASSIGNED)
    semantic = semantics()
    if field == "run_id":
        fencing = replace(semantic.ownership_fencing, run_id=RunId(OTHER))
    elif field == "observed_entity_version":
        fencing = replace(
            semantic.ownership_fencing,
            observed_entity_version=EntityVersion(8),
        )
    else:
        fencing = replace(
            semantic.ownership_fencing,
            correlation_id=CorrelationId(OTHER),
        )
    semantic = replace(semantic, ownership_fencing=fencing)
    with pytest.raises(InvariantViolation, match="exact request snapshot"):
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, guard(snapshot, semantic)),
        )


def test_failed_and_aborted_edges_remain_without_canonical_semantics() -> None:
    snapshot = run(RunState.RUNNING)
    for target in (RunState.FAILED, RunState.ABORTED):
        with pytest.raises(
            InvalidDomainValue, match="canonical normal Run lifecycle edge"
        ):
            RunSemanticGuard(
                snapshot.run_id,
                snapshot.version,
                snapshot.state,
                target,
                CORRELATION,
                semantics(),
            )
