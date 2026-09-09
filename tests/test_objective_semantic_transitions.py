"""M7C1 canonical Objective semantic guards and M7 gate composition."""

from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime, timedelta
from itertools import product
from uuid import UUID

import pytest

import symphony_k.domain.objective_semantics as semantics_module
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
    Objective,
    ObjectiveAcceptanceDecision,
    ObjectiveActivationSemantics,
    ObjectiveArchivalDecision,
    ObjectiveArchivalSemantics,
    ObjectiveBlockerResolutionDecision,
    ObjectiveBlockingSemantics,
    ObjectiveBudgetValidityDecision,
    ObjectiveCancellationSemantics,
    ObjectiveCompletionBlockerDecision,
    ObjectiveCompletionBlockerStatus,
    ObjectiveCompletionPolicyDecision,
    ObjectiveCurrentBlockerDecision,
    ObjectiveEvidenceIndependenceDecision,
    ObjectiveExpirySemantics,
    ObjectiveExtensionCoverageDecision,
    ObjectiveExtensionCoverageStatus,
    ObjectiveFailureSemantics,
    ObjectiveGovernanceApprovalDecision,
    ObjectiveId,
    ObjectiveInabilityDecision,
    ObjectivePermissionValidityDecision,
    ObjectiveReactivationSemantics,
    ObjectiveSatisfactionSemantics,
    ObjectiveSemanticDecisionRef,
    ObjectiveSemanticDecisionStatus,
    ObjectiveSemanticGuard,
    ObjectiveState,
    ObjectiveTerminationDecision,
    ObjectiveTimeHorizonValidityDecision,
    ObjectiveValidityDecision,
    Timestamp,
    TransitionAuthorityDecision,
    TransitionAuthorityStatus,
    TransitionContext,
    TransitionGuard,
    TransitionReason,
    TransitionRequest,
    UnauthorizedTransition,
    can_objective_transition,
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
NOW = Timestamp(datetime(2026, 9, 9, 12, tzinfo=UTC))
POLICY = CompletionPolicyRef("objective-completion", "v1")
ACCEPTANCE_AUTHORITY = ActorIdentity(ActorId(OTHER), ActorType.HUMAN_OPERATOR)
LIFECYCLE_AUTHORITY = ActorIdentity(ActorId(VALUE), ActorType.SCHEDULER)


def objective(
    state: ObjectiveState,
    *,
    version: EntityVersion = VERSION,
    valid_until: Timestamp | None = None,
    policy: CompletionPolicyRef = POLICY,
) -> Objective:
    return Objective(
        ObjectiveId(VALUE),
        state,
        version,
        "Deliver one bounded result",
        ("Independent evidence supports acceptance",),
        ACCEPTANCE_AUTHORITY,
        policy,
        valid_until,
    )


def request(
    target: ObjectiveState,
    *,
    actor: ActorIdentity = LIFECYCLE_AUTHORITY,
    timestamp: Timestamp = NOW,
    correlation: CorrelationId = CORRELATION,
) -> TransitionRequest[ObjectiveState]:
    return TransitionRequest(
        EventId(VALUE),
        target,
        actor,
        TransitionReason("Objective semantic transition"),
        VERSION,
        timestamp,
        correlation,
    )


def evidence(name: str) -> frozenset[EvidenceRef]:
    return frozenset({EvidenceRef(name)})


def decision[DecisionT](
    decision_type: type[DecisionT],
    name: str,
    status: ObjectiveSemanticDecisionStatus = ObjectiveSemanticDecisionStatus.PASSED,
) -> DecisionT:
    return decision_type(  # type: ignore[call-arg]
        ObjectiveSemanticDecisionRef(name),
        status,
        ActorIdentity(ActorId(VALUE), ActorType.POLICY_ENGINE),
        evidence(name),
        ObjectiveId(VALUE),
        VERSION,
        CORRELATION,
    )


def activation(
    *,
    governance: ObjectiveSemanticDecisionStatus = (
        ObjectiveSemanticDecisionStatus.PASSED
    ),
    budget: ObjectiveSemanticDecisionStatus = ObjectiveSemanticDecisionStatus.PASSED,
    permissions: ObjectiveSemanticDecisionStatus = (
        ObjectiveSemanticDecisionStatus.PASSED
    ),
    time_horizon: ObjectiveSemanticDecisionStatus = (
        ObjectiveSemanticDecisionStatus.PASSED
    ),
) -> ObjectiveActivationSemantics:
    return ObjectiveActivationSemantics(
        decision(ObjectiveGovernanceApprovalDecision, "governance", governance),
        decision(ObjectiveBudgetValidityDecision, "budget", budget),
        decision(ObjectivePermissionValidityDecision, "permissions", permissions),
        decision(ObjectiveTimeHorizonValidityDecision, "time", time_horizon),
    )


def satisfaction(
    *,
    policy: CompletionPolicyRef = POLICY,
    completion: ObjectiveSemanticDecisionStatus = (
        ObjectiveSemanticDecisionStatus.PASSED
    ),
    independence: ObjectiveSemanticDecisionStatus = (
        ObjectiveSemanticDecisionStatus.PASSED
    ),
    acceptance: ObjectiveSemanticDecisionStatus = (
        ObjectiveSemanticDecisionStatus.PASSED
    ),
    accepting_authority: ActorIdentity = ACCEPTANCE_AUTHORITY,
    blocker_status: ObjectiveCompletionBlockerStatus = (
        ObjectiveCompletionBlockerStatus.CLEARED
    ),
    waiver_policy: CompletionPolicyRef | None = None,
) -> ObjectiveSatisfactionSemantics:
    return ObjectiveSatisfactionSemantics(
        ObjectiveCompletionPolicyDecision(
            ObjectiveSemanticDecisionRef("completion"),
            completion,
            ActorIdentity(ActorId(VALUE), ActorType.POLICY_ENGINE),
            evidence("completion"),
            ObjectiveId(VALUE),
            VERSION,
            CORRELATION,
            policy,
        ),
        decision(ObjectiveEvidenceIndependenceDecision, "independence", independence),
        ObjectiveAcceptanceDecision(
            ObjectiveSemanticDecisionRef("acceptance"),
            acceptance,
            accepting_authority,
            evidence("acceptance"),
            ObjectiveId(VALUE),
            VERSION,
            CORRELATION,
            accepting_authority,
        ),
        ObjectiveCompletionBlockerDecision(
            ObjectiveSemanticDecisionRef("completion-blockers"),
            blocker_status,
            ActorIdentity(ActorId(VALUE), ActorType.POLICY_ENGINE),
            evidence("completion-blockers"),
            ObjectiveId(VALUE),
            VERSION,
            CORRELATION,
            waiver_policy,
        ),
    )


def semantic_input(
    source: ObjectiveState, target: ObjectiveState
) -> tuple[Objective, object]:
    if (source, target) == (ObjectiveState.DRAFT, ObjectiveState.ACTIVE):
        return objective(
            source, valid_until=Timestamp(NOW.value + timedelta(days=1))
        ), activation()
    if (source, target) == (ObjectiveState.ACTIVE, ObjectiveState.BLOCKED):
        return (
            objective(source, valid_until=Timestamp(NOW.value + timedelta(days=1))),
            ObjectiveBlockingSemantics(
                decision(ObjectiveCurrentBlockerDecision, "blocker"),
                decision(ObjectiveValidityDecision, "validity"),
            ),
        )
    if (source, target) == (ObjectiveState.BLOCKED, ObjectiveState.ACTIVE):
        return (
            objective(source, valid_until=Timestamp(NOW.value + timedelta(days=1))),
            ObjectiveReactivationSemantics(
                decision(ObjectiveBlockerResolutionDecision, "blocker-resolution"),
                activation(),
            ),
        )
    if target is ObjectiveState.SATISFIED:
        return objective(source), satisfaction()
    if target is ObjectiveState.FAILED:
        return objective(source), ObjectiveFailureSemantics(
            decision(ObjectiveInabilityDecision, "inability")
        )
    if target is ObjectiveState.CANCELLED:
        return objective(source), ObjectiveCancellationSemantics(
            decision(ObjectiveTerminationDecision, "termination")
        )
    if target is ObjectiveState.EXPIRED:
        return (
            objective(source, valid_until=Timestamp(NOW.value - timedelta(seconds=1))),
            ObjectiveExpirySemantics(
                ObjectiveExtensionCoverageDecision(
                    ObjectiveSemanticDecisionRef("extension-review"),
                    ObjectiveExtensionCoverageStatus.NO_COVERING_EXTENSION,
                    ActorIdentity(ActorId(VALUE), ActorType.POLICY_ENGINE),
                    evidence("extension-review"),
                    ObjectiveId(VALUE),
                    VERSION,
                    CORRELATION,
                )
            ),
        )
    return objective(source), ObjectiveArchivalSemantics(
        decision(ObjectiveArchivalDecision, "archival")
    )


def canonical_guard(
    snapshot: Objective,
    target: ObjectiveState,
    semantic: object,
    *,
    correlation: CorrelationId = CORRELATION,
) -> ObjectiveSemanticGuard:
    return ObjectiveSemanticGuard(
        snapshot.objective_id,
        snapshot.version,
        snapshot.state,
        target,
        correlation,
        semantic,  # type: ignore[arg-type]
    )


def authority(
    snapshot: Objective,
    transition_request: TransitionRequest[ObjectiveState],
    *,
    status: TransitionAuthorityStatus = TransitionAuthorityStatus.AUTHORIZED,
) -> TransitionAuthorityDecision:
    return TransitionAuthorityDecision(
        transition_request.actor,
        DomainEntityType.OBJECTIVE,
        snapshot.objective_id,
        snapshot.version,
        snapshot.state,
        transition_request.target_state,
        status,
        transition_request.correlation_id,
    )


def context(
    snapshot: Objective,
    transition_request: TransitionRequest[ObjectiveState],
    guard: ObjectiveSemanticGuard,
    *,
    extra_guards: tuple[TransitionGuard, ...] | None = None,
) -> TransitionContext:
    if extra_guards is None:
        extra_guards = (PassingGuard(),)
    return TransitionContext(
        extra_guards,
        authority(snapshot, transition_request),
        guard,
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


LEGAL_EDGES = tuple(
    (source, target)
    for source, target in product(ObjectiveState, repeat=2)
    if can_objective_transition(source, target)
)


@pytest.mark.parametrize(("source", "target"), LEGAL_EDGES)
def test_every_legal_objective_edge_requires_and_accepts_canonical_semantics(
    source: ObjectiveState, target: ObjectiveState
) -> None:
    snapshot, semantic = semantic_input(source, target)
    transition_request = request(target)
    result = transition_entity(
        snapshot,
        transition_request,
        context(
            snapshot, transition_request, canonical_guard(snapshot, target, semantic)
        ),
    )
    assert result.entity.state is target
    assert result.entity.version == VERSION.next()
    assert result.event.metadata.prior_state is source
    assert result.event.metadata.new_state is target
    assert snapshot.state is source
    assert snapshot.version == VERSION


@pytest.mark.parametrize(
    "field",
    ["governance", "budget", "permissions", "time_horizon"],
)
def test_activation_rejects_each_missing_or_invalid_eligibility_decision(
    field: str,
) -> None:
    statuses = {field: ObjectiveSemanticDecisionStatus.UNRESOLVED}
    semantic = activation(**statuses)
    snapshot = objective(ObjectiveState.DRAFT)
    transition_request = request(ObjectiveState.ACTIVE)
    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, ObjectiveState.ACTIVE, semantic),
            ),
        )
    assert (snapshot.state, snapshot.version) == (ObjectiveState.DRAFT, VERSION)


def test_activation_and_blocking_reject_an_elapsed_objective_horizon() -> None:
    for source, target, semantic in (
        (ObjectiveState.DRAFT, ObjectiveState.ACTIVE, activation()),
        (
            ObjectiveState.ACTIVE,
            ObjectiveState.BLOCKED,
            ObjectiveBlockingSemantics(
                decision(ObjectiveCurrentBlockerDecision, "blocker"),
                decision(ObjectiveValidityDecision, "validity"),
            ),
        ),
    ):
        snapshot = objective(source, valid_until=NOW)
        transition_request = request(target)
        with pytest.raises(InvariantViolation, match="horizon has elapsed"):
            transition_entity(
                snapshot,
                transition_request,
                context(
                    snapshot,
                    transition_request,
                    canonical_guard(snapshot, target, semantic),
                ),
            )


def test_blocking_requires_explicit_blocker_and_does_not_inspect_children() -> None:
    snapshot = objective(ObjectiveState.ACTIVE)
    semantic = ObjectiveBlockingSemantics(
        decision(
            ObjectiveCurrentBlockerDecision,
            "blocker",
            ObjectiveSemanticDecisionStatus.UNRESOLVED,
        ),
        decision(ObjectiveValidityDecision, "validity"),
    )
    transition_request = request(ObjectiveState.BLOCKED)
    with pytest.raises(InvariantViolation, match="current blocker"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, ObjectiveState.BLOCKED, semantic),
            ),
        )
    assert not (
        {"tasks", "runs", "outcomes", "children"}
        & {field.name for field in fields(Objective)}
    )


def test_reactivation_requires_explicit_resolution_and_refreshed_eligibility() -> None:
    snapshot = objective(ObjectiveState.BLOCKED)
    transition_request = request(ObjectiveState.ACTIVE)
    for semantic in (
        ObjectiveReactivationSemantics(
            decision(
                ObjectiveBlockerResolutionDecision,
                "resolution",
                ObjectiveSemanticDecisionStatus.UNRESOLVED,
            ),
            activation(),
        ),
        ObjectiveReactivationSemantics(
            decision(ObjectiveBlockerResolutionDecision, "resolution"),
            activation(budget=ObjectiveSemanticDecisionStatus.REJECTED),
        ),
    ):
        with pytest.raises(InvariantViolation):
            transition_entity(
                snapshot,
                transition_request,
                context(
                    snapshot,
                    transition_request,
                    canonical_guard(snapshot, ObjectiveState.ACTIVE, semantic),
                ),
            )


@pytest.mark.parametrize("source", [ObjectiveState.ACTIVE, ObjectiveState.BLOCKED])
def test_satisfaction_requires_exact_policy_independence_and_designated_acceptance(
    source: ObjectiveState,
) -> None:
    snapshot = objective(source)
    transition_request = request(ObjectiveState.SATISFIED)
    invalid_inputs = (
        satisfaction(policy=CompletionPolicyRef("objective-completion", "stale")),
        satisfaction(completion=ObjectiveSemanticDecisionStatus.UNRESOLVED),
        satisfaction(independence=ObjectiveSemanticDecisionStatus.REJECTED),
        satisfaction(acceptance=ObjectiveSemanticDecisionStatus.UNRESOLVED),
        satisfaction(
            accepting_authority=ActorIdentity(ActorId(VALUE), ActorType.HUMAN_OPERATOR)
        ),
        satisfaction(blocker_status=ObjectiveCompletionBlockerStatus.BLOCKED),
        satisfaction(
            blocker_status=ObjectiveCompletionBlockerStatus.LAWFULLY_WAIVED,
            waiver_policy=CompletionPolicyRef("objective-completion", "stale"),
        ),
    )
    for semantic in invalid_inputs:
        with pytest.raises((CompletionPolicyNotSatisfied, InvariantViolation)):
            transition_entity(
                snapshot,
                transition_request,
                context(
                    snapshot,
                    transition_request,
                    canonical_guard(snapshot, ObjectiveState.SATISFIED, semantic),
                ),
            )
        assert (snapshot.state, snapshot.version) == (source, VERSION)


def test_lifecycle_authority_and_designated_acceptance_are_distinct_facts() -> None:
    snapshot = objective(ObjectiveState.ACTIVE)
    transition_request = request(ObjectiveState.SATISFIED)
    result = transition_entity(
        snapshot,
        transition_request,
        context(
            snapshot,
            transition_request,
            canonical_guard(snapshot, ObjectiveState.SATISFIED, satisfaction()),
        ),
    )
    assert result.event.actor == LIFECYCLE_AUTHORITY
    assert ACCEPTANCE_AUTHORITY != LIFECYCLE_AUTHORITY


def test_lawful_completion_blocker_waiver_requires_exact_current_policy() -> None:
    snapshot = objective(ObjectiveState.ACTIVE)
    transition_request = request(ObjectiveState.SATISFIED)
    semantic = satisfaction(
        blocker_status=ObjectiveCompletionBlockerStatus.LAWFULLY_WAIVED,
        waiver_policy=POLICY,
    )
    assert (
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, ObjectiveState.SATISFIED, semantic),
            ),
        ).entity.state
        is ObjectiveState.SATISFIED
    )


def test_failure_requires_evidence_backed_inability_not_child_failure() -> None:
    snapshot = objective(ObjectiveState.ACTIVE)
    transition_request = request(ObjectiveState.FAILED)
    semantic = ObjectiveFailureSemantics(
        decision(
            ObjectiveInabilityDecision,
            "single-run-failure-is-insufficient",
            ObjectiveSemanticDecisionStatus.UNRESOLVED,
        )
    )
    with pytest.raises(InvariantViolation, match="cannot be achieved"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, ObjectiveState.FAILED, semantic),
            ),
        )


def test_cancellation_requires_explicit_termination_provenance() -> None:
    snapshot = objective(ObjectiveState.DRAFT)
    transition_request = request(ObjectiveState.CANCELLED)
    semantic = ObjectiveCancellationSemantics(
        decision(
            ObjectiveTerminationDecision,
            "termination",
            ObjectiveSemanticDecisionStatus.UNRESOLVED,
        )
    )
    with pytest.raises(InvariantViolation, match="termination"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, ObjectiveState.CANCELLED, semantic),
            ),
        )


def test_expiry_uses_request_timestamp_at_boundary_and_never_system_clock() -> None:
    snapshot = objective(ObjectiveState.ACTIVE, valid_until=NOW)
    semantic = ObjectiveExpirySemantics(
        ObjectiveExtensionCoverageDecision(
            ObjectiveSemanticDecisionRef("extension-review"),
            ObjectiveExtensionCoverageStatus.NO_COVERING_EXTENSION,
            ActorIdentity(ActorId(VALUE), ActorType.POLICY_ENGINE),
            evidence("extension-review"),
            ObjectiveId(VALUE),
            VERSION,
            CORRELATION,
        )
    )
    at_boundary = request(ObjectiveState.EXPIRED, timestamp=NOW)
    assert (
        transition_entity(
            snapshot,
            at_boundary,
            context(
                snapshot,
                at_boundary,
                canonical_guard(snapshot, ObjectiveState.EXPIRED, semantic),
            ),
        ).entity.state
        is ObjectiveState.EXPIRED
    )
    before = request(
        ObjectiveState.EXPIRED,
        timestamp=Timestamp(NOW.value - timedelta(microseconds=1)),
    )
    with pytest.raises(InvariantViolation, match="has not elapsed"):
        transition_entity(
            snapshot,
            before,
            context(
                snapshot,
                before,
                canonical_guard(snapshot, ObjectiveState.EXPIRED, semantic),
            ),
        )
    assert "datetime" not in vars(semantics_module)


def test_expiry_rejects_no_horizon_covering_extension_and_unresolved_review() -> None:
    for snapshot, status in (
        (
            objective(ObjectiveState.DRAFT),
            ObjectiveExtensionCoverageStatus.NO_COVERING_EXTENSION,
        ),
        (
            objective(ObjectiveState.DRAFT, valid_until=NOW),
            ObjectiveExtensionCoverageStatus.COVERED,
        ),
        (
            objective(ObjectiveState.DRAFT, valid_until=NOW),
            ObjectiveExtensionCoverageStatus.UNRESOLVED,
        ),
    ):
        transition_request = request(ObjectiveState.EXPIRED)
        semantic = ObjectiveExpirySemantics(
            ObjectiveExtensionCoverageDecision(
                ObjectiveSemanticDecisionRef("extension-review"),
                status,
                ActorIdentity(ActorId(VALUE), ActorType.POLICY_ENGINE),
                evidence("extension-review"),
                ObjectiveId(VALUE),
                VERSION,
                CORRELATION,
            )
        )
        with pytest.raises(InvariantViolation):
            transition_entity(
                snapshot,
                transition_request,
                context(
                    snapshot,
                    transition_request,
                    canonical_guard(snapshot, ObjectiveState.EXPIRED, semantic),
                ),
            )


def test_archival_requires_explicit_decision_and_preserves_snapshot_data() -> None:
    snapshot = objective(ObjectiveState.SATISFIED)
    transition_request = request(ObjectiveState.ARCHIVED)
    semantic = ObjectiveArchivalSemantics(
        decision(
            ObjectiveArchivalDecision,
            "archival",
            ObjectiveSemanticDecisionStatus.UNRESOLVED,
        )
    )
    with pytest.raises(InvariantViolation, match="archival"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, ObjectiveState.ARCHIVED, semantic),
            ),
        )
    assert snapshot.acceptance_criteria
    assert snapshot.completion_policy_ref == POLICY


def test_exact_objective_snapshot_and_correlation_binding_is_mandatory() -> None:
    snapshot = objective(ObjectiveState.DRAFT)
    transition_request = request(ObjectiveState.ACTIVE)
    exact = canonical_guard(snapshot, ObjectiveState.ACTIVE, activation())
    incompatible = (
        replace(exact, objective_id=ObjectiveId(OTHER)),
        replace(exact, observed_entity_version=EntityVersion(6)),
        replace(exact, correlation_id=CorrelationId(OTHER)),
        canonical_guard(
            objective(ObjectiveState.BLOCKED),
            ObjectiveState.ACTIVE,
            ObjectiveReactivationSemantics(
                decision(ObjectiveBlockerResolutionDecision, "resolution"),
                activation(),
            ),
        ),
        canonical_guard(
            objective(ObjectiveState.ACTIVE),
            ObjectiveState.BLOCKED,
            ObjectiveBlockingSemantics(
                decision(ObjectiveCurrentBlockerDecision, "blocker"),
                decision(ObjectiveValidityDecision, "validity"),
            ),
        ),
    )
    for guard in incompatible:
        with pytest.raises(InvariantViolation, match="exact request snapshot"):
            transition_entity(
                snapshot,
                transition_request,
                context(snapshot, transition_request, guard),
            )
        assert (snapshot.state, snapshot.version) == (ObjectiveState.DRAFT, VERSION)


def _assert_reused_semantic_decision_is_rejected(
    semantic: ObjectiveActivationSemantics,
) -> None:
    snapshot = objective(ObjectiveState.DRAFT)
    transition_request = request(ObjectiveState.ACTIVE)
    with pytest.raises(
        InvariantViolation, match="semantic decision does not match the exact request"
    ):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                canonical_guard(snapshot, ObjectiveState.ACTIVE, semantic),
            ),
        )
    assert (snapshot.state, snapshot.version) == (ObjectiveState.DRAFT, VERSION)


def test_exact_guard_rejects_cross_objective_semantic_decision_reuse() -> None:
    semantics = activation()
    _assert_reused_semantic_decision_is_rejected(
        replace(
            semantics,
            governance=replace(semantics.governance, objective_id=ObjectiveId(OTHER)),
        )
    )


def test_exact_guard_rejects_stale_version_semantic_decision_reuse() -> None:
    semantics = activation()
    _assert_reused_semantic_decision_is_rejected(
        replace(
            semantics,
            budget=replace(semantics.budget, observed_entity_version=EntityVersion(6)),
        )
    )


def test_exact_guard_rejects_cross_correlation_semantic_decision_reuse() -> None:
    semantics = activation()
    _assert_reused_semantic_decision_is_rejected(
        replace(
            semantics,
            permissions=replace(
                semantics.permissions, correlation_id=CorrelationId(OTHER)
            ),
        )
    )


def test_m7_authority_eligibility_semantics_and_generic_guard_are_distinct_gates() -> (
    None
):
    snapshot = objective(ObjectiveState.DRAFT)
    transition_request = request(ObjectiveState.ACTIVE)
    guard = canonical_guard(snapshot, ObjectiveState.ACTIVE, activation())
    with pytest.raises(UnauthorizedTransition, match="decision is required"):
        transition_entity(
            snapshot,
            transition_request,
            TransitionContext((PassingGuard(),), None, guard),
        )
    worker_request = request(
        ObjectiveState.ACTIVE,
        actor=ActorIdentity(ActorId(VALUE), ActorType.WORKER),
    )
    with pytest.raises(UnauthorizedTransition, match="not eligible"):
        transition_entity(
            snapshot,
            worker_request,
            TransitionContext(
                (PassingGuard(),), authority(snapshot, worker_request), guard
            ),
        )
    with pytest.raises(InvariantViolation, match="Canonical Objective"):
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
    assert (snapshot.state, snapshot.version) == (ObjectiveState.DRAFT, VERSION)


def test_semantic_inputs_are_frozen_typed_evidence_backed_and_not_latest_wins() -> None:
    semantic_decision = decision(ObjectiveBudgetValidityDecision, "budget")
    guard = canonical_guard(
        objective(ObjectiveState.DRAFT), ObjectiveState.ACTIVE, activation()
    )
    with pytest.raises(FrozenInstanceError):
        semantic_decision.status = ObjectiveSemanticDecisionStatus.REJECTED  # type: ignore[misc]
    with pytest.raises(AttributeError):
        semantic_decision.evidence_refs.add(EvidenceRef("later"))  # type: ignore[attr-defined]
    with pytest.raises(FrozenInstanceError):
        guard.observed_entity_version = EntityVersion(8)  # type: ignore[misc]
    assert not (
        {"timestamp", "created_at", "updated_at"}
        & {field.name for field in fields(semantic_decision)}
    )
    assert not any(name.startswith("latest") for name in vars(semantics_module))


def test_semantic_decisions_reject_bare_booleans_and_missing_evidence() -> None:
    with pytest.raises(InvalidDomainValue):
        ObjectiveBudgetValidityDecision(
            ObjectiveSemanticDecisionRef("budget"),
            True,  # type: ignore[arg-type]
            LIFECYCLE_AUTHORITY,
            evidence("budget"),
            ObjectiveId(VALUE),
            VERSION,
            CORRELATION,
        )
    with pytest.raises(InvalidDomainValue):
        ObjectiveBudgetValidityDecision(
            ObjectiveSemanticDecisionRef("budget"),
            ObjectiveSemanticDecisionStatus.PASSED,
            LIFECYCLE_AUTHORITY,
            frozenset(),
            ObjectiveId(VALUE),
            VERSION,
            CORRELATION,
        )


def test_topology_remains_exactly_seventeen_edges_and_archived_is_sink() -> None:
    assert len(LEGAL_EDGES) == 17
    assert not any(
        can_objective_transition(ObjectiveState.ARCHIVED, target)
        for target in ObjectiveState
    )


def test_m7c1_adds_no_other_entity_runtime_or_child_propagation_boundary() -> None:
    forbidden = {
        "TaskSemanticGuard",
        "RunSemanticGuard",
        "OutcomeSemanticGuard",
        "EvaluationSemanticGuard",
        "EffectSemanticGuard",
        "PolicyEngine",
        "PermissionEngine",
        "BudgetEngine",
        "Repository",
        "UnitOfWork",
        "Persistence",
        "Failover",
    }
    assert forbidden.isdisjoint(vars(semantics_module))
    assert not any("child" in name.lower() for name in vars(semantics_module))
