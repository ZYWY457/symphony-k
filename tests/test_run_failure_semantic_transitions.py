"""M7C3B3 canonical Run FAILED semantic guards."""

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
    RunFailedDecision,
    RunFailureClassification,
    RunFailureSemantics,
    RunId,
    RunNormalizedFailureClassificationDecision,
    RunOwnershipFencingDecision,
    RunRecoveryPathClosureDecision,
    RunRecoveryPathClosureReason,
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
) -> DecisionT:
    return decision_type(  # type: ignore[call-arg]
        RunSemanticDecisionRef(name),
        status,
        actor,
        evidence(name),
        RUN_ID,
        RUN_VERSION,
        CORRELATION,
        *extra,
    )


def semantics(
    *,
    classification: RunFailureClassification = RunFailureClassification.INFRA_FAILURE,
    classification_status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    closure_status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    fencing_status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    failed_status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
) -> RunFailureSemantics:
    return RunFailureSemantics(
        decision(
            RunNormalizedFailureClassificationDecision,
            "classification",
            classification,
            status=classification_status,
        ),
        decision(
            RunRecoveryPathClosureDecision,
            "recovery-closure",
            RunRecoveryPathClosureReason.RECOVERY_EXHAUSTED,
            status=closure_status,
        ),
        decision(
            RunOwnershipFencingDecision,
            "ownership-fencing",
            status=fencing_status,
        ),
        decision(RunFailedDecision, "failed", status=failed_status),
    )


def request(target: RunState = RunState.FAILED) -> TransitionRequest[RunState]:
    return TransitionRequest(
        EventId(VALUE),
        target,
        LIFECYCLE_AUTHORITY,
        TransitionReason("Run failure closure semantic transition"),
        RUN_VERSION,
        Timestamp(datetime(2026, 9, 10, 12, tzinfo=UTC)),
        CORRELATION,
    )


def guard(snapshot: Run, semantic: RunFailureSemantics) -> RunSemanticGuard:
    return RunSemanticGuard(
        snapshot.run_id,
        snapshot.version,
        snapshot.state,
        RunState.FAILED,
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
def test_every_failed_edge_requires_canonical_semantics_and_preserves_run(
    source: RunState,
) -> None:
    snapshot = run(source)
    transition_request = request()
    result = transition_entity(
        snapshot,
        transition_request,
        context(snapshot, transition_request, guard(snapshot, semantics())),
    )
    assert result.entity.state is RunState.FAILED
    assert result.entity.version == RUN_VERSION.next()
    assert result.entity.run_id == snapshot.run_id
    assert result.entity.task_id == snapshot.task_id
    assert result.entity.predecessor_run_id == snapshot.predecessor_run_id
    assert result.entity.execution_profile_ref == snapshot.execution_profile_ref
    assert (snapshot.state, snapshot.version) == (source, RUN_VERSION)


@pytest.mark.parametrize("classification", RunFailureClassification)
def test_every_accepted_failure_class_is_representable(
    classification: RunFailureClassification,
) -> None:
    assert (
        semantics(classification=classification).failure_classification.classification
        is classification
    )


def test_failure_taxonomy_is_provider_independent() -> None:
    names = {classification.name for classification in RunFailureClassification}
    assert {"WINDOWS", "LINUX", "CODEX", "HTTP", "EXCEPTION"}.isdisjoint(names)


def test_worker_evidence_can_support_independent_classification() -> None:
    worker_evidence = frozenset({EvidenceRef("worker/raw-provider-observation")})
    classification = RunNormalizedFailureClassificationDecision(
        RunSemanticDecisionRef("classification"),
        RunSemanticDecisionStatus.PASSED,
        DECISION_AUTHORITY,
        worker_evidence,
        RUN_ID,
        RUN_VERSION,
        CORRELATION,
        RunFailureClassification.WORKER_FAILURE,
    )
    assert classification.evidence_refs == worker_evidence


@pytest.mark.parametrize("actor_type", ActorType)
def test_failed_selection_accepts_exactly_r_authorities(actor_type: ActorType) -> None:
    actor = ActorIdentity(ActorId(OTHER), actor_type)
    if actor_type in {ActorType.SCHEDULER, ActorType.RUN_CONTROLLER}:
        assert isinstance(
            decision(RunFailedDecision, "failed", actor=actor), RunFailedDecision
        )
    else:
        with pytest.raises(InvalidDomainValue, match="SCHEDULER or RUN_CONTROLLER"):
            decision(RunFailedDecision, "failed", actor=actor)


@pytest.mark.parametrize("actor_type", ActorType)
def test_recovery_path_closure_accepts_exactly_r_authorities(
    actor_type: ActorType,
) -> None:
    actor = ActorIdentity(ActorId(OTHER), actor_type)
    if actor_type in {ActorType.SCHEDULER, ActorType.RUN_CONTROLLER}:
        assert isinstance(
            decision(
                RunRecoveryPathClosureDecision,
                "closure",
                RunRecoveryPathClosureReason.CONTINUATION_INVALID,
                actor=actor,
            ),
            RunRecoveryPathClosureDecision,
        )
    else:
        with pytest.raises(InvalidDomainValue, match="SCHEDULER or RUN_CONTROLLER"):
            decision(
                RunRecoveryPathClosureDecision,
                "closure",
                RunRecoveryPathClosureReason.CONTINUATION_INVALID,
                actor=actor,
            )


def test_worker_cannot_authoritatively_classify_or_fence_failure() -> None:
    worker = ActorIdentity(ActorId(OTHER), ActorType.WORKER)
    with pytest.raises(InvalidDomainValue, match="normalized failure classification"):
        decision(
            RunNormalizedFailureClassificationDecision,
            "classification",
            RunFailureClassification.EXECUTION_FAILURE,
            actor=worker,
        )
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
        classification = replace(semantic.failure_classification, run_id=RunId(OTHER))
    elif field == "observed_entity_version":
        classification = replace(
            semantic.failure_classification,
            observed_entity_version=EntityVersion(8),
        )
    else:
        classification = replace(
            semantic.failure_classification,
            correlation_id=CorrelationId(OTHER),
        )
    semantic = replace(
        semantic,
        failure_classification=classification,
    )
    with pytest.raises(InvariantViolation, match="exact request snapshot"):
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, guard(snapshot, semantic)),
        )


@pytest.mark.parametrize(
    "semantic",
    (
        lambda: semantics(classification_status=RunSemanticDecisionStatus.UNRESOLVED),
        lambda: semantics(closure_status=RunSemanticDecisionStatus.REJECTED),
        lambda: semantics(fencing_status=RunSemanticDecisionStatus.UNRESOLVED),
        lambda: semantics(failed_status=RunSemanticDecisionStatus.REJECTED),
    ),
)
def test_missing_or_unresolved_failure_conditions_reject(semantic: object) -> None:
    snapshot = run(RunState.RETRYING)
    transition_request = request()
    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, guard(snapshot, semantic())),  # type: ignore[operator]
        )
    assert (snapshot.state, snapshot.version) == (RunState.RETRYING, RUN_VERSION)


def test_transient_classification_does_not_imply_a_transition() -> None:
    snapshot = run(RunState.RUNNING)
    transition_request = request()
    with pytest.raises(InvariantViolation, match="recovery-path closure"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard(
                    snapshot,
                    semantics(
                        classification=RunFailureClassification.TRANSIENT,
                        closure_status=RunSemanticDecisionStatus.UNRESOLVED,
                    ),
                ),
            ),
        )


@pytest.mark.parametrize("reason", RunRecoveryPathClosureReason)
def test_every_accepted_recovery_path_closure_reason_is_representable(
    reason: RunRecoveryPathClosureReason,
) -> None:
    assert decision(RunRecoveryPathClosureDecision, "closure", reason).reason is reason


def test_failure_semantics_do_not_introduce_related_entity_or_successor_fields() -> (
    None
):
    forbidden = {
        "task",
        "objective",
        "outcome",
        "evaluation",
        "effect",
        "successor",
        "handoff",
    }
    assert not (forbidden & {field.name for field in fields(RunFailureSemantics)})


def test_aborted_edges_remain_without_canonical_semantics() -> None:
    snapshot = run(RunState.RUNNING)
    with pytest.raises(InvalidDomainValue, match="canonical normal Run lifecycle edge"):
        RunSemanticGuard(
            snapshot.run_id,
            snapshot.version,
            snapshot.state,
            RunState.ABORTED,
            CORRELATION,
            semantics(),
        )
