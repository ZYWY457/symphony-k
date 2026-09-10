"""M7C3B4 canonical Run ABORTED semantic guards."""

from dataclasses import fields, replace
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
    RunAbortedDecision,
    RunAbortSemantics,
    RunAbortStopBasis,
    RunAbortStopBasisDecision,
    RunId,
    RunOwnershipFencingDecision,
    RunSemanticDecisionRef,
    RunSemanticDecisionStatus,
    RunSemanticGuard,
    RunState,
    TaskId,
    Timestamp,
    TransitionAuthorityDecision,
    TransitionAuthorityStatus,
    TransitionContext,
    TransitionReason,
    TransitionRequest,
    can_run_transition,
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
CORRELATION = CorrelationId(VALUE)
PROFILE = ExecutionProfileRef("approved-profile", "v3")
RUN_ID = RunId(VALUE)
TASK_ID = TaskId(VALUE)
LIFECYCLE_AUTHORITY = ActorIdentity(ActorId(VALUE), ActorType.RUN_CONTROLLER)
DECISION_AUTHORITY = ActorIdentity(ActorId(OTHER), ActorType.RUN_CONTROLLER)


def run(state: RunState) -> Run:
    return Run(RUN_ID, TASK_ID, state, RUN_VERSION, PROFILE)


def evidence(name: str) -> frozenset[EvidenceRef]:
    return frozenset({EvidenceRef(name)})


def decision[DecisionT](
    decision_type: type[DecisionT],
    name: str,
    *extra: object,
    status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    actor: ActorIdentity = DECISION_AUTHORITY,
    evidence_refs: frozenset[EvidenceRef] | None = None,
) -> DecisionT:
    return decision_type(  # type: ignore[call-arg]
        RunSemanticDecisionRef(name),
        status,
        actor,
        evidence(name) if evidence_refs is None else evidence_refs,
        RUN_ID,
        RUN_VERSION,
        CORRELATION,
        *extra,
    )


def semantics(
    *,
    basis: RunAbortStopBasis = RunAbortStopBasis.SCHEDULER_CONTROL,
    basis_status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    fencing_status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    aborted_status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
) -> RunAbortSemantics:
    return RunAbortSemantics(
        decision(RunAbortStopBasisDecision, "stop-basis", basis, status=basis_status),
        decision(
            RunOwnershipFencingDecision,
            "ownership-fencing",
            status=fencing_status,
        ),
        decision(RunAbortedDecision, "aborted", status=aborted_status),
    )


def request(target: RunState = RunState.ABORTED) -> TransitionRequest[RunState]:
    return TransitionRequest(
        EventId(VALUE),
        target,
        LIFECYCLE_AUTHORITY,
        TransitionReason("Run abort closure semantic transition"),
        RUN_VERSION,
        Timestamp(datetime(2026, 9, 10, 12, tzinfo=UTC)),
        CORRELATION,
    )


def guard(snapshot: Run, semantic: RunAbortSemantics) -> RunSemanticGuard:
    return RunSemanticGuard(
        snapshot.run_id,
        snapshot.version,
        snapshot.state,
        RunState.ABORTED,
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
    semantic_guard: RunSemanticGuard,
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
    return TransitionContext(
        (PassingGuard(),), authority, run_semantic_guard=semantic_guard
    )


@pytest.mark.parametrize(
    "source",
    (
        RunState.PENDING,
        RunState.RUNNING,
        RunState.WAITING_FOR_VERIFICATION,
        RunState.RETRYING,
    ),
)
def test_every_aborted_edge_requires_canonical_semantics_and_preserves_run(
    source: RunState,
) -> None:
    snapshot = run(source)
    transition_request = request()
    result = transition_entity(
        snapshot,
        transition_request,
        context(snapshot, transition_request, guard(snapshot, semantics())),
    )
    assert result.entity.state is RunState.ABORTED
    assert result.entity.version == RUN_VERSION.next()
    assert result.entity.run_id == snapshot.run_id
    assert result.entity.task_id == snapshot.task_id
    assert result.entity.predecessor_run_id == snapshot.predecessor_run_id
    assert result.entity.execution_profile_ref == snapshot.execution_profile_ref
    assert (snapshot.state, snapshot.version) == (source, RUN_VERSION)


@pytest.mark.parametrize("basis", RunAbortStopBasis)
def test_every_canonical_abort_stop_basis_is_representable(
    basis: RunAbortStopBasis,
) -> None:
    assert semantics(basis=basis).stop_basis.basis is basis


@pytest.mark.parametrize("actor_type", ActorType)
def test_abort_selection_accepts_exactly_r_authorities(actor_type: ActorType) -> None:
    actor = ActorIdentity(ActorId(OTHER), actor_type)
    if actor_type in {ActorType.SCHEDULER, ActorType.RUN_CONTROLLER}:
        assert isinstance(
            decision(RunAbortedDecision, "aborted", actor=actor), RunAbortedDecision
        )
    else:
        with pytest.raises(InvalidDomainValue, match="SCHEDULER or RUN_CONTROLLER"):
            decision(RunAbortedDecision, "aborted", actor=actor)


def test_worker_evidence_can_support_an_independent_stop_basis() -> None:
    worker_evidence = frozenset({EvidenceRef("worker/requested-safety-stop")})
    stop_basis = decision(
        RunAbortStopBasisDecision,
        "stop-basis",
        RunAbortStopBasis.SAFETY,
        evidence_refs=worker_evidence,
    )
    assert stop_basis.evidence_refs == worker_evidence


def test_worker_cannot_authoritatively_select_abort_or_certify_fencing() -> None:
    worker = ActorIdentity(ActorId(OTHER), ActorType.WORKER)
    with pytest.raises(InvalidDomainValue, match="SCHEDULER or RUN_CONTROLLER"):
        decision(RunAbortedDecision, "aborted", actor=worker)

    snapshot = run(RunState.RUNNING)
    transition_request = request()
    base = semantics()
    semantic = replace(
        base, ownership_fencing=replace(base.ownership_fencing, decided_by=worker)
    )
    with pytest.raises(InvariantViolation, match="ended or fenced ownership"):
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, guard(snapshot, semantic)),
        )


@pytest.mark.parametrize(
    "field",
    ("run_id", "observed_entity_version", "correlation_id"),
)
def test_stale_cross_run_and_cross_correlation_decisions_cannot_be_laundered(
    field: str,
) -> None:
    snapshot = run(RunState.PENDING)
    transition_request = request()
    semantic = semantics()
    if field == "run_id":
        stop_basis = replace(semantic.stop_basis, run_id=RunId(OTHER))
    elif field == "observed_entity_version":
        stop_basis = replace(
            semantic.stop_basis,
            observed_entity_version=EntityVersion(8),
        )
    else:
        stop_basis = replace(
            semantic.stop_basis,
            correlation_id=CorrelationId(OTHER),
        )
    semantic = replace(semantic, stop_basis=stop_basis)
    with pytest.raises(InvariantViolation, match="exact request snapshot"):
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, guard(snapshot, semantic)),
        )


@pytest.mark.parametrize(
    "semantic",
    (
        lambda: semantics(basis_status=RunSemanticDecisionStatus.UNRESOLVED),
        lambda: semantics(fencing_status=RunSemanticDecisionStatus.REJECTED),
        lambda: semantics(aborted_status=RunSemanticDecisionStatus.UNRESOLVED),
    ),
)
def test_missing_or_unresolved_abort_conditions_reject(semantic: object) -> None:
    snapshot = run(RunState.RETRYING)
    transition_request = request()
    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, guard(snapshot, semantic())),  # type: ignore[operator]
        )
    assert (snapshot.state, snapshot.version) == (RunState.RETRYING, RUN_VERSION)


def test_abort_semantics_require_no_failure_or_recovery_closure() -> None:
    forbidden = {"failure", "classification", "recovery", "successor", "handoff"}
    assert not (forbidden & {field.name for field in fields(RunAbortSemantics)})


def test_abort_semantics_do_not_mutate_related_lifecycle_or_verdicts() -> None:
    forbidden = {
        "task",
        "objective",
        "outcome",
        "evaluation",
        "effect",
        "successor",
        "verification",
        "verdict",
    }
    assert not (forbidden & {field.name for field in fields(RunAbortSemantics)})


def test_run_lifecycle_topology_remains_the_existing_eighteen_edges() -> None:
    expected = {
        (RunState.PENDING, RunState.RUNNING),
        (RunState.RUNNING, RunState.WAITING_FOR_VERIFICATION),
        (RunState.RUNNING, RunState.RETRYING),
        (RunState.RETRYING, RunState.RUNNING),
        *(
            (source, RunState.REASSIGNED)
            for source in (
                RunState.PENDING,
                RunState.RUNNING,
                RunState.WAITING_FOR_VERIFICATION,
                RunState.RETRYING,
            )
        ),
        (RunState.RUNNING, RunState.COMPLETED),
        (RunState.WAITING_FOR_VERIFICATION, RunState.COMPLETED),
        *(
            (source, RunState.FAILED)
            for source in (
                RunState.PENDING,
                RunState.RUNNING,
                RunState.WAITING_FOR_VERIFICATION,
                RunState.RETRYING,
            )
        ),
        *(
            (source, RunState.ABORTED)
            for source in (
                RunState.PENDING,
                RunState.RUNNING,
                RunState.WAITING_FOR_VERIFICATION,
                RunState.RETRYING,
            )
        ),
    }
    actual = {
        (source, target)
        for source in RunState
        for target in RunState
        if can_run_transition(source, target)
    }
    assert actual == expected
