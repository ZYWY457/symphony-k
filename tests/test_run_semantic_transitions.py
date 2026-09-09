"""M7C3A canonical normal Run semantic guards and M7 gate composition."""

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
    ObjectiveId,
    ObjectiveState,
    OutcomeId,
    Run,
    RunArtifactUsagePersistenceDecision,
    RunBudgetValidityDecision,
    RunCandidateOutcomeObservation,
    RunDirectCompletionSemantics,
    RunExecutionBoundaryDecision,
    RunExecutionOwnershipDecision,
    RunExecutionOwnershipRef,
    RunExecutionProfileApprovalDecision,
    RunExecutionStoppedDecision,
    RunGrantValidityDecision,
    RunId,
    RunIndependentNormalTerminationDecision,
    RunNoVerificationWaitRequirementDecision,
    RunPrimaryObjectiveStateObservation,
    RunSemanticDecisionRef,
    RunSemanticDecisionStatus,
    RunSemanticGuard,
    RunStartSemantics,
    RunState,
    RunTaskStateObservation,
    RunTrustedStartConfirmationDecision,
    RunVerificationEvidenceRetentionDecision,
    RunVerificationRequestDecision,
    RunVerificationResolutionDecision,
    RunVerificationResolutionStatus,
    RunVerificationWaitSemantics,
    RunVerifiedCompletionSemantics,
    TaskId,
    TaskState,
    Timestamp,
    TransitionAuthorityDecision,
    TransitionAuthorityStatus,
    TransitionContext,
    TransitionGuard,
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
TASK_VERSION = EntityVersion(11)
OBJECTIVE_VERSION = EntityVersion(13)
OUTCOME_VERSION = EntityVersion(17)
CORRELATION = CorrelationId(VALUE)
PROFILE = ExecutionProfileRef("approved-profile", "v3")
LIFECYCLE_AUTHORITY = ActorIdentity(ActorId(VALUE), ActorType.RUN_CONTROLLER)
DECISION_AUTHORITY = ActorIdentity(ActorId(OTHER), ActorType.POLICY_ENGINE)


def run(state: RunState, *, version: EntityVersion = RUN_VERSION) -> Run:
    return Run(RunId(VALUE), TaskId(VALUE), state, version, PROFILE)


def request(
    target: RunState,
    *,
    correlation: CorrelationId = CORRELATION,
) -> TransitionRequest[RunState]:
    return TransitionRequest(
        EventId(VALUE),
        target,
        LIFECYCLE_AUTHORITY,
        TransitionReason("Run normal semantic transition"),
        RUN_VERSION,
        Timestamp(datetime(2026, 9, 9, 12, tzinfo=UTC)),
        correlation,
    )


def evidence(name: str) -> frozenset[EvidenceRef]:
    return frozenset({EvidenceRef(name)})


def decision[DecisionT](
    decision_type: type[DecisionT],
    name: str,
    status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    *,
    actor: ActorIdentity = DECISION_AUTHORITY,
) -> DecisionT:
    return decision_type(  # type: ignore[call-arg]
        RunSemanticDecisionRef(name),
        status,
        actor,
        evidence(name),
        RunId(VALUE),
        RUN_VERSION,
        CORRELATION,
    )


def task_observation(
    *,
    task_id: TaskId | None = None,
    task_version: EntityVersion = TASK_VERSION,
    state: TaskState = TaskState.IN_PROGRESS,
    status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
) -> RunTaskStateObservation:
    return RunTaskStateObservation(
        RunSemanticDecisionRef("task-observation"),
        status,
        DECISION_AUTHORITY,
        evidence("task-observation"),
        RunId(VALUE),
        RUN_VERSION,
        CORRELATION,
        TaskId(VALUE) if task_id is None else task_id,
        task_version,
        state,
    )


def primary_objective(
    *,
    task_id: TaskId | None = None,
    task_version: EntityVersion = TASK_VERSION,
    objective_id: ObjectiveId | None = None,
    objective_version: EntityVersion = OBJECTIVE_VERSION,
    state: ObjectiveState = ObjectiveState.ACTIVE,
    status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
) -> RunPrimaryObjectiveStateObservation:
    return RunPrimaryObjectiveStateObservation(
        RunSemanticDecisionRef("primary-objective"),
        status,
        DECISION_AUTHORITY,
        evidence("primary-objective"),
        RunId(VALUE),
        RUN_VERSION,
        CORRELATION,
        TaskId(VALUE) if task_id is None else task_id,
        task_version,
        ObjectiveId(VALUE) if objective_id is None else objective_id,
        objective_version,
        state,
    )


def ownership(
    *,
    task_id: TaskId | None = None,
    task_version: EntityVersion = TASK_VERSION,
    owner_run_id: RunId | None = None,
    status: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
) -> RunExecutionOwnershipDecision:
    return RunExecutionOwnershipDecision(
        RunSemanticDecisionRef("execution-ownership"),
        status,
        DECISION_AUTHORITY,
        evidence("execution-ownership"),
        RunId(VALUE),
        RUN_VERSION,
        CORRELATION,
        TaskId(VALUE) if task_id is None else task_id,
        task_version,
        RunExecutionOwnershipRef("ownership/record-1"),
        RunId(VALUE) if owner_run_id is None else owner_run_id,
    )


def start_semantics(
    *,
    task: RunTaskStateObservation | None = None,
    objective: RunPrimaryObjectiveStateObservation | None = None,
    owner: RunExecutionOwnershipDecision | None = None,
    profile: ExecutionProfileRef = PROFILE,
    statuses: dict[str, RunSemanticDecisionStatus] | None = None,
    start_actor: ActorIdentity = DECISION_AUTHORITY,
) -> RunStartSemantics:
    statuses = {} if statuses is None else statuses
    return RunStartSemantics(
        task_observation() if task is None else task,
        primary_objective() if objective is None else objective,
        ownership() if owner is None else owner,
        RunExecutionProfileApprovalDecision(
            RunSemanticDecisionRef("profile"),
            statuses.get("profile", RunSemanticDecisionStatus.PASSED),
            DECISION_AUTHORITY,
            evidence("profile"),
            RunId(VALUE),
            RUN_VERSION,
            CORRELATION,
            profile,
        ),
        decision(
            RunExecutionBoundaryDecision,
            "boundary",
            statuses.get("boundary", RunSemanticDecisionStatus.PASSED),
        ),
        decision(
            RunGrantValidityDecision,
            "grants",
            statuses.get("grants", RunSemanticDecisionStatus.PASSED),
        ),
        decision(
            RunBudgetValidityDecision,
            "budget",
            statuses.get("budget", RunSemanticDecisionStatus.PASSED),
        ),
        decision(
            RunTrustedStartConfirmationDecision,
            "start-confirmation",
            statuses.get("start_confirmation", RunSemanticDecisionStatus.PASSED),
            actor=start_actor,
        ),
    )


def verification_wait_semantics(
    *,
    stopped: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    candidate: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    originating_run_id: RunId | None = None,
    requested: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
) -> RunVerificationWaitSemantics:
    return RunVerificationWaitSemantics(
        decision(RunExecutionStoppedDecision, "execution-stopped", stopped),
        RunCandidateOutcomeObservation(
            RunSemanticDecisionRef("candidate-outcome"),
            candidate,
            DECISION_AUTHORITY,
            evidence("candidate-outcome"),
            RunId(VALUE),
            RUN_VERSION,
            CORRELATION,
            OutcomeId(VALUE),
            OUTCOME_VERSION,
            RunId(VALUE) if originating_run_id is None else originating_run_id,
        ),
        decision(RunVerificationRequestDecision, "verification-request", requested),
    )


def direct_completion_semantics(
    *,
    termination: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    persistence: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    no_wait: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    termination_actor: ActorIdentity = DECISION_AUTHORITY,
) -> RunDirectCompletionSemantics:
    return RunDirectCompletionSemantics(
        decision(
            RunIndependentNormalTerminationDecision,
            "normal-termination",
            termination,
            actor=termination_actor,
        ),
        decision(RunArtifactUsagePersistenceDecision, "persistence", persistence),
        decision(RunNoVerificationWaitRequirementDecision, "no-wait", no_wait),
    )


def verified_completion_semantics(
    *,
    resolution: RunVerificationResolutionStatus = (
        RunVerificationResolutionStatus.RESOLVED_FAVORABLE
    ),
    retention: RunSemanticDecisionStatus = RunSemanticDecisionStatus.PASSED,
    resolution_actor: ActorIdentity = DECISION_AUTHORITY,
) -> RunVerifiedCompletionSemantics:
    return RunVerifiedCompletionSemantics(
        RunVerificationResolutionDecision(
            RunSemanticDecisionRef("verification-resolution"),
            resolution,
            resolution_actor,
            evidence("verification-resolution"),
            RunId(VALUE),
            RUN_VERSION,
            CORRELATION,
        ),
        decision(RunVerificationEvidenceRetentionDecision, "retention", retention),
    )


def canonical_guard(
    snapshot: Run, target: RunState, semantic: object
) -> RunSemanticGuard:
    return RunSemanticGuard(
        snapshot.run_id,
        snapshot.version,
        snapshot.state,
        target,
        CORRELATION,
        semantic,  # type: ignore[arg-type]
    )


def authority(
    snapshot: Run, transition_request: TransitionRequest[RunState]
) -> TransitionAuthorityDecision:
    return TransitionAuthorityDecision(
        transition_request.actor,
        DomainEntityType.RUN,
        snapshot.run_id,
        snapshot.version,
        snapshot.state,
        transition_request.target_state,
        TransitionAuthorityStatus.AUTHORIZED,
        transition_request.correlation_id,
    )


class PassingGuard:
    def validate(
        self,
        entity: LifecycleEntity,
        transition_request: TransitionRequest[LifecycleState],
    ) -> None:
        assert entity.version == transition_request.expected_version


class RejectingGuard:
    def validate(
        self,
        entity: LifecycleEntity,
        transition_request: TransitionRequest[LifecycleState],
    ) -> None:
        raise InvariantViolation("additional generic guard rejected")


def context(
    snapshot: Run,
    transition_request: TransitionRequest[RunState],
    guard: RunSemanticGuard,
    *,
    extra_guards: tuple[TransitionGuard, ...] = (PassingGuard(),),
) -> TransitionContext:
    return TransitionContext(
        extra_guards,
        authority(snapshot, transition_request),
        run_semantic_guard=guard,
    )


@pytest.mark.parametrize(
    ("source", "target", "semantic"),
    (
        (RunState.PENDING, RunState.RUNNING, start_semantics()),
        (
            RunState.RUNNING,
            RunState.WAITING_FOR_VERIFICATION,
            verification_wait_semantics(),
        ),
        (RunState.RUNNING, RunState.COMPLETED, direct_completion_semantics()),
        (
            RunState.WAITING_FOR_VERIFICATION,
            RunState.COMPLETED,
            verified_completion_semantics(),
        ),
    ),
)
def test_every_normal_run_edge_requires_and_accepts_canonical_semantics(
    source: RunState, target: RunState, semantic: object
) -> None:
    snapshot = run(source)
    transition_request = request(target)
    result = transition_entity(
        snapshot,
        transition_request,
        context(
            snapshot, transition_request, canonical_guard(snapshot, target, semantic)
        ),
    )
    assert result.entity.state is target
    assert result.entity.version == RUN_VERSION.next()
    assert result.event.metadata.prior_state is source
    assert result.event.metadata.new_state is target
    assert (snapshot.state, snapshot.version) == (source, RUN_VERSION)


@pytest.mark.parametrize(
    "target",
    (RunState.RETRYING, RunState.REASSIGNED, RunState.FAILED, RunState.ABORTED),
)
def test_recovery_reassign_failure_and_abort_cannot_receive_placeholder_semantics(
    target: RunState,
) -> None:
    with pytest.raises(InvalidDomainValue, match="normal Run lifecycle edge"):
        canonical_guard(run(RunState.RUNNING), target, direct_completion_semantics())


def test_start_requires_every_exact_normal_execution_input() -> None:
    snapshot = run(RunState.PENDING)
    transition_request = request(RunState.RUNNING)
    invalid_semantics = (
        start_semantics(task=task_observation(state=TaskState.BLOCKED)),
        start_semantics(objective=primary_objective(state=ObjectiveState.BLOCKED)),
        start_semantics(owner=ownership(owner_run_id=RunId(OTHER))),
        start_semantics(profile=ExecutionProfileRef("other-profile", "v3")),
        start_semantics(statuses={"boundary": RunSemanticDecisionStatus.UNRESOLVED}),
        start_semantics(statuses={"grants": RunSemanticDecisionStatus.REJECTED}),
        start_semantics(statuses={"budget": RunSemanticDecisionStatus.UNRESOLVED}),
        start_semantics(start_actor=ActorIdentity(ActorId(OTHER), ActorType.WORKER)),
    )
    for semantic in invalid_semantics:
        with pytest.raises(InvariantViolation):
            transition_entity(
                snapshot,
                transition_request,
                context(
                    snapshot,
                    transition_request,
                    canonical_guard(snapshot, RunState.RUNNING, semantic),
                ),
            )
        assert (snapshot.state, snapshot.version) == (RunState.PENDING, RUN_VERSION)


def test_start_cross_entity_observations_keep_their_own_versions() -> None:
    semantics = start_semantics()
    assert semantics.task.observed_entity_version == RUN_VERSION
    assert semantics.task.observed_task_version == TASK_VERSION
    assert semantics.primary_objective.observed_task_version == TASK_VERSION
    assert semantics.primary_objective.observed_objective_version == OBJECTIVE_VERSION
    assert semantics.task.observed_task_version != RUN_VERSION
    assert semantics.primary_objective.observed_objective_version != RUN_VERSION


def test_start_rejects_incoherent_cross_entity_task_versions() -> None:
    snapshot = run(RunState.PENDING)
    transition_request = request(RunState.RUNNING)
    semantic = start_semantics(
        objective=primary_objective(task_version=EntityVersion(12))
    )
    with pytest.raises(InvariantViolation, match="observed Task snapshot"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, RunState.RUNNING, semantic),
            ),
        )
    assert (snapshot.state, snapshot.version) == (RunState.PENDING, RUN_VERSION)


def test_wait_requires_stopped_execution_candidate_and_request() -> None:
    snapshot = run(RunState.RUNNING)
    transition_request = request(RunState.WAITING_FOR_VERIFICATION)
    invalid_semantics = (
        verification_wait_semantics(stopped=RunSemanticDecisionStatus.UNRESOLVED),
        verification_wait_semantics(candidate=RunSemanticDecisionStatus.REJECTED),
        verification_wait_semantics(originating_run_id=RunId(OTHER)),
        verification_wait_semantics(requested=RunSemanticDecisionStatus.UNRESOLVED),
    )
    for semantic in invalid_semantics:
        with pytest.raises(InvariantViolation):
            transition_entity(
                snapshot,
                transition_request,
                context(
                    snapshot,
                    transition_request,
                    canonical_guard(
                        snapshot, RunState.WAITING_FOR_VERIFICATION, semantic
                    ),
                ),
            )
        assert (snapshot.state, snapshot.version) == (RunState.RUNNING, RUN_VERSION)


def test_wait_candidate_outcome_keeps_its_own_identity_and_version() -> None:
    candidate = verification_wait_semantics().candidate_outcome
    assert candidate.outcome_id == OutcomeId(VALUE)
    assert candidate.observed_outcome_version == OUTCOME_VERSION
    assert candidate.observed_outcome_version != candidate.observed_entity_version
    with pytest.raises(InvalidDomainValue):
        replace(candidate, observed_outcome_version=17)  # type: ignore[arg-type]


def test_direct_completion_requires_termination_persistence_and_no_wait() -> None:
    snapshot = run(RunState.RUNNING)
    transition_request = request(RunState.COMPLETED)
    invalid_semantics = (
        direct_completion_semantics(termination=RunSemanticDecisionStatus.UNRESOLVED),
        direct_completion_semantics(persistence=RunSemanticDecisionStatus.REJECTED),
        direct_completion_semantics(no_wait=RunSemanticDecisionStatus.UNRESOLVED),
        direct_completion_semantics(
            termination_actor=ActorIdentity(ActorId(OTHER), ActorType.WORKER)
        ),
    )
    for semantic in invalid_semantics:
        with pytest.raises(InvariantViolation):
            transition_entity(
                snapshot,
                transition_request,
                context(
                    snapshot,
                    transition_request,
                    canonical_guard(snapshot, RunState.COMPLETED, semantic),
                ),
            )
        assert (snapshot.state, snapshot.version) == (RunState.RUNNING, RUN_VERSION)


def test_verified_completion_allows_unfavorable_verdict_with_evidence() -> None:
    snapshot = run(RunState.WAITING_FOR_VERIFICATION)
    transition_request = request(RunState.COMPLETED)
    unfavorable = verified_completion_semantics(
        resolution=RunVerificationResolutionStatus.RESOLVED_UNFAVORABLE
    )
    assert (
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, RunState.COMPLETED, unfavorable),
            ),
        ).entity.state
        is RunState.COMPLETED
    )
    for semantic in (
        verified_completion_semantics(
            resolution=RunVerificationResolutionStatus.UNRESOLVED
        ),
        verified_completion_semantics(retention=RunSemanticDecisionStatus.REJECTED),
        verified_completion_semantics(
            resolution_actor=ActorIdentity(ActorId(OTHER), ActorType.WORKER)
        ),
    ):
        with pytest.raises(InvariantViolation):
            transition_entity(
                snapshot,
                transition_request,
                context(
                    snapshot,
                    transition_request,
                    canonical_guard(snapshot, RunState.COMPLETED, semantic),
                ),
            )


@pytest.mark.parametrize(
    "replacement",
    (RunId(OTHER), EntityVersion(6), CorrelationId(OTHER)),
)
def test_every_consumed_decision_is_exact_bound_to_run_snapshot_and_correlation(
    replacement: RunId | EntityVersion | CorrelationId,
) -> None:
    snapshot = run(RunState.PENDING)
    transition_request = request(RunState.RUNNING)
    semantic = start_semantics()
    if isinstance(replacement, RunId):
        semantic = replace(
            semantic, boundary=replace(semantic.boundary, run_id=replacement)
        )
    elif isinstance(replacement, EntityVersion):
        semantic = replace(
            semantic,
            budget=replace(semantic.budget, observed_entity_version=replacement),
        )
    else:
        semantic = replace(
            semantic, grants=replace(semantic.grants, correlation_id=replacement)
        )
    with pytest.raises(InvariantViolation, match="semantic decision does not match"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, RunState.RUNNING, semantic),
            ),
        )
    assert (snapshot.state, snapshot.version) == (RunState.PENDING, RUN_VERSION)


def test_authority_semantics_and_generic_guards_remain_distinct_gates() -> None:
    snapshot = run(RunState.PENDING)
    transition_request = request(RunState.RUNNING)
    guard = canonical_guard(snapshot, RunState.RUNNING, start_semantics())
    with pytest.raises(InvariantViolation, match="Canonical Run semantic guard"):
        transition_entity(
            snapshot,
            transition_request,
            TransitionContext(
                (PassingGuard(),), authority(snapshot, transition_request)
            ),
        )
    with pytest.raises(InvariantViolation, match="additional generic"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard,
                extra_guards=(RejectingGuard(),),
            ),
        )
    assert (snapshot.state, snapshot.version) == (RunState.PENDING, RUN_VERSION)


def test_run_completion_has_no_outcome_task_or_objective_propagation() -> None:
    assert not (
        {"task", "objective", "outcome", "acceptance", "completion_policy"}
        & {field.name for field in fields(RunDirectCompletionSemantics)}
    )
    assert not (
        {"task", "objective", "outcome", "acceptance", "completion_policy"}
        & {field.name for field in fields(RunVerifiedCompletionSemantics)}
    )
    assert can_run_transition(RunState.RUNNING, RunState.COMPLETED)


def test_semantic_inputs_are_frozen_typed_evidence_backed_and_do_not_add_runtime() -> (
    None
):
    semantic = start_semantics()
    guard = canonical_guard(run(RunState.PENDING), RunState.RUNNING, semantic)
    with pytest.raises(AttributeError):
        semantic.boundary.evidence_refs.add(EvidenceRef("later"))  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        guard.observed_entity_version = EntityVersion(8)  # type: ignore[misc]
    import symphony_k.domain.run_semantics as semantics_module

    forbidden = {
        "Repository",
        "Persistence",
        "PolicyEngine",
        "Runtime",
        "Checkpoint",
        "OutcomeSemanticGuard",
        "EvaluationSemanticGuard",
        "Failover",
    }
    assert forbidden.isdisjoint(vars(semantics_module))
