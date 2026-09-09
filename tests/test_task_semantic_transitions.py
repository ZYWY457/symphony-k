"""M7C2 canonical Task semantic guards and M7 gate composition."""

from dataclasses import fields, replace
from datetime import UTC, datetime
from itertools import product
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CompletionPolicyNotSatisfied,
    CompletionPolicyRef,
    CorrelationId,
    EntityVersion,
    EventId,
    EvidenceRef,
    InvalidDomainValue,
    InvariantViolation,
    ObjectiveId,
    ObjectiveState,
    RunId,
    Task,
    TaskBlockerResolutionDecision,
    TaskBlockingSemantics,
    TaskBudgetValidityDecision,
    TaskCancellationSemantics,
    TaskCompletionAcceptanceDecision,
    TaskCompletionBlockerDecision,
    TaskCompletionBlockerStatus,
    TaskCompletionPolicyDecision,
    TaskCompletionSemantics,
    TaskCurrentBlockerDecision,
    TaskDefinitionGovernanceDecision,
    TaskDependencyReadinessDecision,
    TaskEvidenceIndependenceDecision,
    TaskExecutionAuthorizationEndedDecision,
    TaskExecutionOwnershipDecision,
    TaskExecutionOwnershipRef,
    TaskExecutionOwnershipStatus,
    TaskFailureEvidenceDecision,
    TaskFailureSemantics,
    TaskId,
    TaskPermissionValidityDecision,
    TaskPrimaryObjectiveStateDecision,
    TaskReadinessAfterBlockSemantics,
    TaskReadinessSemantics,
    TaskRecoveryDispositionDecision,
    TaskRequiredEffectsDecision,
    TaskResumeSemantics,
    TaskRiskDecision,
    TaskSemanticDecisionRef,
    TaskSemanticDecisionStatus,
    TaskSemanticGuard,
    TaskStartSemantics,
    TaskState,
    TaskTerminationDecision,
    Timestamp,
    TransitionAuthorityDecision,
    TransitionAuthorityStatus,
    TransitionContext,
    TransitionGuard,
    TransitionReason,
    TransitionRequest,
    can_task_transition,
    transition_entity,
)
from symphony_k.domain.transition_engine import (
    DomainEntityType,
    LifecycleEntity,
    LifecycleState,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
VERSION = EntityVersion(7)
CORRELATION = CorrelationId(VALUE)
POLICY = CompletionPolicyRef("task-completion", "v1")
LIFECYCLE_AUTHORITY = ActorIdentity(ActorId(VALUE), ActorType.SCHEDULER)
DECISION_AUTHORITY = ActorIdentity(ActorId(OTHER), ActorType.POLICY_ENGINE)


def task(
    state: TaskState,
    *,
    version: EntityVersion = VERSION,
    policy: CompletionPolicyRef = POLICY,
) -> Task:
    return Task(
        TaskId(VALUE),
        state,
        version,
        "Deliver one bounded Task result",
        ObjectiveId(VALUE),
        policy,
    )


def request(
    target: TaskState,
    *,
    correlation: CorrelationId = CORRELATION,
) -> TransitionRequest[TaskState]:
    return TransitionRequest(
        EventId(VALUE),
        target,
        LIFECYCLE_AUTHORITY,
        TransitionReason("Task semantic transition"),
        VERSION,
        Timestamp(datetime(2026, 9, 9, 12, tzinfo=UTC)),
        correlation,
    )


def evidence(name: str) -> frozenset[EvidenceRef]:
    return frozenset({EvidenceRef(name)})


def decision[DecisionT](
    decision_type: type[DecisionT],
    name: str,
    status: TaskSemanticDecisionStatus = TaskSemanticDecisionStatus.PASSED,
) -> DecisionT:
    return decision_type(  # type: ignore[call-arg]
        TaskSemanticDecisionRef(name),
        status,
        DECISION_AUTHORITY,
        evidence(name),
        TaskId(VALUE),
        VERSION,
        CORRELATION,
    )


def primary_objective(
    *,
    state: ObjectiveState = ObjectiveState.ACTIVE,
    objective_id: ObjectiveId | None = None,
    status: TaskSemanticDecisionStatus = TaskSemanticDecisionStatus.PASSED,
) -> TaskPrimaryObjectiveStateDecision:
    return TaskPrimaryObjectiveStateDecision(
        TaskSemanticDecisionRef("primary-objective"),
        status,
        DECISION_AUTHORITY,
        evidence("primary-objective"),
        TaskId(VALUE),
        VERSION,
        CORRELATION,
        ObjectiveId(VALUE) if objective_id is None else objective_id,
        state,
    )


def readiness(**statuses: TaskSemanticDecisionStatus) -> TaskReadinessSemantics:
    return TaskReadinessSemantics(
        decision(
            TaskDefinitionGovernanceDecision,
            "governance",
            statuses.get("governance", TaskSemanticDecisionStatus.PASSED),
        ),
        decision(
            TaskDependencyReadinessDecision,
            "dependencies",
            statuses.get("dependencies", TaskSemanticDecisionStatus.PASSED),
        ),
        decision(
            TaskBudgetValidityDecision,
            "budget",
            statuses.get("budget", TaskSemanticDecisionStatus.PASSED),
        ),
        decision(
            TaskPermissionValidityDecision,
            "permissions",
            statuses.get("permissions", TaskSemanticDecisionStatus.PASSED),
        ),
        primary_objective(),
    )


def ownership(
    status: TaskExecutionOwnershipStatus,
) -> TaskExecutionOwnershipDecision:
    linked_run = (
        RunId(VALUE)
        if status is TaskExecutionOwnershipStatus.ACTIVE_OWNERSHIP
        else None
    )
    return TaskExecutionOwnershipDecision(
        TaskSemanticDecisionRef("execution-ownership"),
        status,
        DECISION_AUTHORITY,
        evidence("execution-ownership"),
        TaskId(VALUE),
        VERSION,
        CORRELATION,
        linked_run,
    )


def completion(
    *,
    policy: CompletionPolicyRef = POLICY,
    completion_status: TaskSemanticDecisionStatus = TaskSemanticDecisionStatus.PASSED,
    independence: TaskSemanticDecisionStatus = TaskSemanticDecisionStatus.PASSED,
    acceptance: TaskSemanticDecisionStatus = TaskSemanticDecisionStatus.PASSED,
    effects: TaskSemanticDecisionStatus = TaskSemanticDecisionStatus.PASSED,
    risk: TaskSemanticDecisionStatus = TaskSemanticDecisionStatus.PASSED,
    blocker_status: TaskCompletionBlockerStatus = TaskCompletionBlockerStatus.CLEARED,
    waiver_policy: CompletionPolicyRef | None = None,
) -> TaskCompletionSemantics:
    return TaskCompletionSemantics(
        TaskCompletionPolicyDecision(
            TaskSemanticDecisionRef("completion"),
            completion_status,
            DECISION_AUTHORITY,
            evidence("completion"),
            TaskId(VALUE),
            VERSION,
            CORRELATION,
            policy,
        ),
        decision(TaskEvidenceIndependenceDecision, "independence", independence),
        decision(TaskCompletionAcceptanceDecision, "acceptance", acceptance),
        decision(TaskRequiredEffectsDecision, "effects", effects),
        decision(TaskRiskDecision, "risk", risk),
        TaskCompletionBlockerDecision(
            TaskSemanticDecisionRef("completion-blockers"),
            blocker_status,
            DECISION_AUTHORITY,
            evidence("completion-blockers"),
            TaskId(VALUE),
            VERSION,
            CORRELATION,
            waiver_policy,
        ),
    )


def semantic_input(source: TaskState, target: TaskState) -> object:
    if (source, target) == (TaskState.DRAFT, TaskState.READY):
        return readiness()
    if target is TaskState.BLOCKED:
        return TaskBlockingSemantics(decision(TaskCurrentBlockerDecision, "blocker"))
    if (source, target) == (TaskState.BLOCKED, TaskState.READY):
        return TaskReadinessAfterBlockSemantics(
            decision(TaskBlockerResolutionDecision, "blocker-resolution"),
            readiness(),
            ownership(TaskExecutionOwnershipStatus.NO_ACTIVE_OWNERSHIP),
        )
    if (source, target) == (TaskState.READY, TaskState.IN_PROGRESS):
        return TaskStartSemantics(
            readiness(), ownership(TaskExecutionOwnershipStatus.ACTIVE_OWNERSHIP)
        )
    if (source, target) == (TaskState.BLOCKED, TaskState.IN_PROGRESS):
        return TaskResumeSemantics(
            decision(TaskBlockerResolutionDecision, "blocker-resolution"),
            primary_objective(),
            ownership(TaskExecutionOwnershipStatus.ACTIVE_OWNERSHIP),
        )
    if target is TaskState.COMPLETED:
        return completion()
    if target is TaskState.FAILED:
        return TaskFailureSemantics(
            decision(TaskFailureEvidenceDecision, "failure-evidence"),
            decision(TaskRecoveryDispositionDecision, "recovery-disposition"),
        )
    return TaskCancellationSemantics(
        decision(TaskTerminationDecision, "termination"),
        decision(TaskExecutionAuthorizationEndedDecision, "execution-ended"),
    )


def canonical_guard(
    snapshot: Task,
    target: TaskState,
    semantic: object,
    *,
    correlation: CorrelationId = CORRELATION,
) -> TaskSemanticGuard:
    return TaskSemanticGuard(
        snapshot.task_id,
        snapshot.version,
        snapshot.state,
        target,
        correlation,
        semantic,  # type: ignore[arg-type]
    )


def authority(
    snapshot: Task, transition_request: TransitionRequest[TaskState]
) -> TransitionAuthorityDecision:
    return TransitionAuthorityDecision(
        transition_request.actor,
        DomainEntityType.TASK,
        snapshot.task_id,
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
    snapshot: Task,
    transition_request: TransitionRequest[TaskState],
    guard: TaskSemanticGuard,
    *,
    extra_guards: tuple[TransitionGuard, ...] = (PassingGuard(),),
) -> TransitionContext:
    return TransitionContext(
        extra_guards,
        authority(snapshot, transition_request),
        task_semantic_guard=guard,
    )


LEGAL_EDGES = tuple(
    (source, target)
    for source, target in product(TaskState, repeat=2)
    if can_task_transition(source, target)
)


@pytest.mark.parametrize(("source", "target"), LEGAL_EDGES)
def test_every_legal_task_edge_requires_and_accepts_canonical_semantics(
    source: TaskState, target: TaskState
) -> None:
    snapshot = task(source)
    transition_request = request(target)
    result = transition_entity(
        snapshot,
        transition_request,
        context(
            snapshot,
            transition_request,
            canonical_guard(snapshot, target, semantic_input(source, target)),
        ),
    )
    assert result.entity.state is target
    assert result.entity.version == VERSION.next()
    assert result.event.metadata.prior_state is source
    assert result.event.metadata.new_state is target
    assert (snapshot.state, snapshot.version) == (source, VERSION)


def test_task_semantic_guard_is_required_before_additional_generic_guards() -> None:
    snapshot = task(TaskState.DRAFT)
    transition_request = request(TaskState.READY)
    with pytest.raises(InvariantViolation, match="Canonical Task semantic guard"):
        transition_entity(
            snapshot,
            transition_request,
            TransitionContext(
                (PassingGuard(),), authority(snapshot, transition_request)
            ),
        )
    assert (snapshot.state, snapshot.version) == (TaskState.DRAFT, VERSION)


@pytest.mark.parametrize(
    "field", ["governance", "dependencies", "budget", "permissions"]
)
def test_readiness_requires_all_explicit_eligibility_decisions(field: str) -> None:
    snapshot = task(TaskState.DRAFT)
    transition_request = request(TaskState.READY)
    semantics = readiness(**{field: TaskSemanticDecisionStatus.UNRESOLVED})
    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, TaskState.READY, semantics),
            ),
        )
    assert (snapshot.state, snapshot.version) == (TaskState.DRAFT, VERSION)


@pytest.mark.parametrize(
    "state", [state for state in ObjectiveState if state is not ObjectiveState.ACTIVE]
)
def test_readiness_start_and_resume_reject_any_non_active_primary_objective(
    state: ObjectiveState,
) -> None:
    cases = (
        (
            TaskState.DRAFT,
            TaskState.READY,
            replace(readiness(), primary_objective=primary_objective(state=state)),
        ),
        (
            TaskState.READY,
            TaskState.IN_PROGRESS,
            TaskStartSemantics(
                replace(readiness(), primary_objective=primary_objective(state=state)),
                ownership(TaskExecutionOwnershipStatus.ACTIVE_OWNERSHIP),
            ),
        ),
        (
            TaskState.BLOCKED,
            TaskState.IN_PROGRESS,
            TaskResumeSemantics(
                decision(TaskBlockerResolutionDecision, "blocker-resolution"),
                primary_objective(state=state),
                ownership(TaskExecutionOwnershipStatus.ACTIVE_OWNERSHIP),
            ),
        ),
    )
    for source, target, semantics in cases:
        snapshot = task(source)
        transition_request = request(target)
        with pytest.raises(InvariantViolation, match="not ACTIVE"):
            transition_entity(
                snapshot,
                transition_request,
                context(
                    snapshot,
                    transition_request,
                    canonical_guard(snapshot, target, semantics),
                ),
            )
        assert (snapshot.state, snapshot.version) == (source, VERSION)


def test_primary_objective_evidence_must_identify_exact_task_primary_objective() -> (
    None
):
    snapshot = task(TaskState.DRAFT)
    transition_request = request(TaskState.READY)
    semantics = replace(
        readiness(),
        primary_objective=primary_objective(objective_id=ObjectiveId(OTHER)),
    )
    with pytest.raises(InvariantViolation, match="does not identify"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, TaskState.READY, semantics),
            ),
        )
    assert (snapshot.state, snapshot.version) == (TaskState.DRAFT, VERSION)


def test_blocked_to_ready_requires_explicit_no_active_ownership() -> None:
    snapshot = task(TaskState.BLOCKED)
    transition_request = request(TaskState.READY)
    for status in (
        TaskExecutionOwnershipStatus.ACTIVE_OWNERSHIP,
        TaskExecutionOwnershipStatus.UNRESOLVED,
    ):
        semantics = TaskReadinessAfterBlockSemantics(
            decision(TaskBlockerResolutionDecision, "blocker-resolution"),
            readiness(),
            ownership(status),
        )
        with pytest.raises(InvariantViolation, match="ownership"):
            transition_entity(
                snapshot,
                transition_request,
                context(
                    snapshot,
                    transition_request,
                    canonical_guard(snapshot, TaskState.READY, semantics),
                ),
            )
    assert (snapshot.state, snapshot.version) == (TaskState.BLOCKED, VERSION)


@pytest.mark.parametrize("source", [TaskState.READY, TaskState.BLOCKED])
def test_start_and_resume_require_explicit_active_execution_ownership(
    source: TaskState,
) -> None:
    target = TaskState.IN_PROGRESS
    if source is TaskState.READY:
        semantics: object = TaskStartSemantics(
            readiness(), ownership(TaskExecutionOwnershipStatus.UNRESOLVED)
        )
    else:
        semantics = TaskResumeSemantics(
            decision(TaskBlockerResolutionDecision, "blocker-resolution"),
            primary_objective(),
            ownership(TaskExecutionOwnershipStatus.UNRESOLVED),
        )
    snapshot = task(source)
    transition_request = request(target)
    with pytest.raises(InvariantViolation, match="active execution ownership"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, target, semantics),
            ),
        )
    assert (snapshot.state, snapshot.version) == (source, VERSION)


@pytest.mark.parametrize("source", [TaskState.IN_PROGRESS, TaskState.BLOCKED])
def test_completion_requires_current_policy_independent_evidence_and_all_checks(
    source: TaskState,
) -> None:
    snapshot = task(source)
    transition_request = request(TaskState.COMPLETED)
    invalid_inputs = (
        completion(policy=CompletionPolicyRef("task-completion", "stale")),
        completion(completion_status=TaskSemanticDecisionStatus.UNRESOLVED),
        completion(independence=TaskSemanticDecisionStatus.REJECTED),
        completion(acceptance=TaskSemanticDecisionStatus.UNRESOLVED),
        completion(effects=TaskSemanticDecisionStatus.REJECTED),
        completion(risk=TaskSemanticDecisionStatus.UNRESOLVED),
        completion(blocker_status=TaskCompletionBlockerStatus.BLOCKED),
        completion(
            blocker_status=TaskCompletionBlockerStatus.LAWFULLY_WAIVED,
            waiver_policy=CompletionPolicyRef("task-completion", "stale"),
        ),
    )
    for semantics in invalid_inputs:
        with pytest.raises((CompletionPolicyNotSatisfied, InvariantViolation)):
            transition_entity(
                snapshot,
                transition_request,
                context(
                    snapshot,
                    transition_request,
                    canonical_guard(snapshot, TaskState.COMPLETED, semantics),
                ),
            )
        assert (snapshot.state, snapshot.version) == (source, VERSION)


def test_completion_does_not_consume_run_outcome_percentage_or_child_inputs() -> None:
    snapshot = task(TaskState.IN_PROGRESS)
    transition_request = request(TaskState.COMPLETED)
    assert not (
        {"runs", "outcomes", "children", "percentage"}
        & {field.name for field in fields(Task)}
    )
    assert (
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, TaskState.COMPLETED, completion()),
            ),
        ).entity.state
        is TaskState.COMPLETED
    )


def test_failure_and_cancellation_require_recorded_semantic_decisions() -> None:
    failure_snapshot = task(TaskState.IN_PROGRESS)
    failure_request = request(TaskState.FAILED)
    failure = TaskFailureSemantics(
        decision(
            TaskFailureEvidenceDecision,
            "failure",
            TaskSemanticDecisionStatus.UNRESOLVED,
        ),
        decision(TaskRecoveryDispositionDecision, "recovery"),
    )
    with pytest.raises(InvariantViolation):
        transition_entity(
            failure_snapshot,
            failure_request,
            context(
                failure_snapshot,
                failure_request,
                canonical_guard(failure_snapshot, TaskState.FAILED, failure),
            ),
        )

    cancelled_snapshot = task(TaskState.IN_PROGRESS)
    cancelled_request = request(TaskState.CANCELLED)
    cancellation = TaskCancellationSemantics(
        decision(TaskTerminationDecision, "termination"),
        decision(
            TaskExecutionAuthorizationEndedDecision,
            "execution-ended",
            TaskSemanticDecisionStatus.UNRESOLVED,
        ),
    )
    with pytest.raises(InvariantViolation):
        transition_entity(
            cancelled_snapshot,
            cancelled_request,
            context(
                cancelled_snapshot,
                cancelled_request,
                canonical_guard(cancelled_snapshot, TaskState.CANCELLED, cancellation),
            ),
        )
    assert (failure_snapshot.state, failure_snapshot.version) == (
        TaskState.IN_PROGRESS,
        VERSION,
    )
    assert (cancelled_snapshot.state, cancelled_snapshot.version) == (
        TaskState.IN_PROGRESS,
        VERSION,
    )


@pytest.mark.parametrize(
    "replacement", [TaskId(OTHER), EntityVersion(6), CorrelationId(OTHER)]
)
def test_exact_guard_cannot_launder_cross_task_stale_or_cross_correlation_decisions(
    replacement: TaskId | EntityVersion | CorrelationId,
) -> None:
    snapshot = task(TaskState.DRAFT)
    transition_request = request(TaskState.READY)
    semantics = readiness()
    if isinstance(replacement, TaskId):
        semantics = replace(
            semantics, governance=replace(semantics.governance, task_id=replacement)
        )
    elif isinstance(replacement, EntityVersion):
        semantics = replace(
            semantics,
            budget=replace(semantics.budget, observed_entity_version=replacement),
        )
    else:
        semantics = replace(
            semantics,
            permissions=replace(semantics.permissions, correlation_id=replacement),
        )
    with pytest.raises(InvariantViolation, match="semantic decision does not match"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, TaskState.READY, semantics),
            ),
        )
    assert (snapshot.state, snapshot.version) == (TaskState.DRAFT, VERSION)


def test_authority_eligibility_semantics_and_generic_guards_are_distinct_gates() -> (
    None
):
    snapshot = task(TaskState.DRAFT)
    transition_request = request(TaskState.READY)
    guard = canonical_guard(snapshot, TaskState.READY, readiness())
    with pytest.raises(InvariantViolation, match="additional generic"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot, transition_request, guard, extra_guards=(RejectingGuard(),)
            ),
        )
    assert (snapshot.state, snapshot.version) == (TaskState.DRAFT, VERSION)


def test_active_ownership_requires_a_linked_run_or_control_record() -> None:
    with pytest.raises(InvalidDomainValue):
        TaskExecutionOwnershipDecision(
            TaskSemanticDecisionRef("missing-owner"),
            TaskExecutionOwnershipStatus.ACTIVE_OWNERSHIP,
            DECISION_AUTHORITY,
            evidence("missing-owner"),
            TaskId(VALUE),
            VERSION,
            CORRELATION,
        )
    assert (
        TaskExecutionOwnershipDecision(
            TaskSemanticDecisionRef("control-owner"),
            TaskExecutionOwnershipStatus.ACTIVE_OWNERSHIP,
            DECISION_AUTHORITY,
            evidence("control-owner"),
            TaskId(VALUE),
            VERSION,
            CORRELATION,
            execution_control_ref=TaskExecutionOwnershipRef("controller/record-1"),
        ).status
        is TaskExecutionOwnershipStatus.ACTIVE_OWNERSHIP
    )
