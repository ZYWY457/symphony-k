"""M7C6A canonical Effect preparation and commit-eligibility semantic guards."""

from collections.abc import Callable
from dataclasses import fields, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CorrelationId,
    DomainEntityType,
    DomainEventType,
    Effect,
    EffectDeduplicationRef,
    EffectId,
    EffectOperationScope,
    EffectPayloadRef,
    EffectPendingCommitSemantics,
    EffectPreparationRecord,
    EffectPreparationRecordId,
    EffectRemediationReadinessId,
    EffectRemediationReadinessRecord,
    EffectRemediationReadinessStatus,
    EffectSemanticGuard,
    EffectSimulationBypassBasis,
    EffectSimulationBypassDecision,
    EffectSimulationBypassDecisionId,
    EffectSimulationBypassStatus,
    EffectSimulationRecord,
    EffectSimulationRecordId,
    EffectSimulationScopeRef,
    EffectSimulationSemantics,
    EffectState,
    EffectTargetRef,
    EffectVerificationRecord,
    EffectVerificationRecordId,
    EntityVersion,
    EventId,
    EvidenceRef,
    InvalidDomainValue,
    InvariantViolation,
    PlannedEffectOrigin,
    TaskId,
    Timestamp,
    TransitionAuthorityDecision,
    TransitionAuthorityStatus,
    TransitionContext,
    TransitionReason,
    TransitionRequest,
    UnauthorizedTransition,
    can_effect_transition,
    transition_entity,
)
from symphony_k.domain.transition_engine import LifecycleEntity, LifecycleState

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
PRODUCER = UUID("00000000-1234-4234-8234-123456789abc")
PREPARER = UUID("11111111-1234-4234-8234-123456789abc")
VERIFIER = UUID("22222222-1234-4234-8234-123456789abc")
CONTROLLER = UUID("33333333-1234-4234-8234-123456789abc")
BYPASS_DECIDER = UUID("44444444-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
VERSION = EntityVersion(17)
CORRELATION = CorrelationId(VALUE)
OTHER_CORRELATION = CorrelationId(OTHER)
NOW = Timestamp(datetime(2026, 9, 11, tzinfo=UTC))
type SemanticChanges = Callable[[Effect], dict[str, object]]


def identity(actor_type: ActorType, value: UUID) -> ActorIdentity:
    return ActorIdentity(ActorId(value), actor_type)


def effect(
    state: EffectState = EffectState.PLANNED,
    *,
    proposed_by: ActorIdentity | None = None,
) -> Effect:
    return Effect(
        EffectId(VALUE),
        state,
        VERSION,
        PlannedEffectOrigin(
            TaskId(VALUE), proposed_by or identity(ActorType.WORKER, PRODUCER)
        ),
        EffectTargetRef("target-a"),
        EffectPayloadRef("payload-a"),
    )


def scope(
    current: Effect,
    *,
    effect_id: EffectId | None = None,
    version: EntityVersion | None = None,
    target: EffectTargetRef | None = None,
    payload: EffectPayloadRef | None = None,
    correlation: CorrelationId = CORRELATION,
) -> EffectOperationScope:
    assert current.payload_ref is not None
    return EffectOperationScope(
        effect_id or current.effect_id,
        version or current.version,
        target or current.target_ref,
        payload or current.payload_ref,
        correlation,
    )


def simulation(
    current: Effect, *, operation_scope: EffectOperationScope | None = None
) -> EffectSimulationRecord:
    return EffectSimulationRecord(
        EffectSimulationRecordId(VALUE),
        operation_scope or scope(current),
        EffectSimulationScopeRef("dry-run-target-contract"),
        "Dry-run established the proposed mutation representation without execution.",
        frozenset({EvidenceRef("simulation-evidence")}),
        identity(ActorType.WORKER, PREPARER),
        identity(ActorType.SCHEDULER, OTHER),
        NOW,
        NOW,
    )


def preparation(
    current: Effect,
    *,
    correlation: CorrelationId = CORRELATION,
    prepared_by: ActorIdentity | None = None,
) -> EffectPreparationRecord:
    return EffectPreparationRecord(
        EffectPreparationRecordId(VALUE),
        current.effect_id,
        current.version,
        "Prepared exact intended operation for pre-commit review.",
        prepared_by or identity(ActorType.WORKER, PREPARER),
        identity(ActorType.SCHEDULER, OTHER),
        NOW,
        NOW,
        correlation,
    )


def verification(
    current: Effect,
    prepared: EffectPreparationRecord,
    *,
    preparation_id: EffectPreparationRecordId | None = None,
    verified_by: ActorIdentity | None = None,
    correlation: CorrelationId = CORRELATION,
) -> EffectVerificationRecord:
    return EffectVerificationRecord(
        EffectVerificationRecordId(VALUE),
        preparation_id or prepared.preparation_id,
        current.effect_id,
        current.version,
        "Independent pre-commit verification passed for the exact preparation.",
        frozenset({EvidenceRef("verification-evidence")}),
        verified_by or identity(ActorType.EVALUATOR, VERIFIER),
        identity(ActorType.SCHEDULER, OTHER),
        NOW,
        NOW,
        correlation,
    )


def readiness(
    current: Effect, *, operation_scope: EffectOperationScope | None = None
) -> EffectRemediationReadinessRecord:
    return EffectRemediationReadinessRecord(
        EffectRemediationReadinessId(VALUE),
        operation_scope or scope(current),
        EffectRemediationReadinessStatus.COMPENSATION_PREPARED,
        "Compensation planning is prepared if a later commit requires remediation.",
        frozenset({EvidenceRef("remediation-readiness-evidence")}),
        identity(ActorType.SCHEDULER, OTHER),
        identity(ActorType.SCHEDULER, OTHER),
        NOW,
        NOW,
    )


def bypass(
    current: Effect,
    *,
    operation_scope: EffectOperationScope | None = None,
    status: EffectSimulationBypassStatus = EffectSimulationBypassStatus.ACCEPTED,
    decided_by: ActorIdentity | None = None,
) -> EffectSimulationBypassDecision:
    return EffectSimulationBypassDecision(
        EffectSimulationBypassDecisionId(VALUE),
        operation_scope or scope(current),
        status,
        EffectSimulationBypassBasis.IMPRACTICAL,
        "A representative dry run is impractical for the exact operation target.",
        frozenset({EvidenceRef("bypass-evidence")}),
        decided_by or identity(ActorType.HUMAN_OPERATOR, BYPASS_DECIDER),
        identity(ActorType.SCHEDULER, OTHER),
        NOW,
        NOW,
    )


def pending_semantics(
    current: Effect, **changes: object
) -> EffectPendingCommitSemantics:
    prepared = changes.pop("preparation", preparation(current))
    assert isinstance(prepared, EffectPreparationRecord)
    values: dict[str, object] = {
        "operation_scope": scope(current),
        "preparation": prepared,
        "verification": verification(current, prepared),
        "remediation_readiness": readiness(current),
        "deduplication_ref": EffectDeduplicationRef("idempotency-key-v1"),
        "simulation": simulation(current)
        if current.state is EffectState.SIMULATED
        else None,
        "simulation_bypass": bypass(current)
        if current.state is EffectState.PLANNED
        else None,
    }
    values.update(changes)
    return EffectPendingCommitSemantics(**values)  # type: ignore[arg-type]


def request(current: Effect, target: EffectState) -> TransitionRequest[EffectState]:
    return TransitionRequest(
        EventId(VALUE),
        target,
        identity(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        TransitionReason("Canonical Effect preparation transition"),
        current.version,
        NOW,
        CORRELATION,
    )


def context(
    current: Effect,
    transition_request: TransitionRequest[EffectState],
    semantics: EffectSimulationSemantics | EffectPendingCommitSemantics | None,
    *,
    authority: TransitionAuthorityDecision | None = None,
) -> TransitionContext:
    guard = None
    if semantics is not None:
        assert current.payload_ref is not None
        guard = EffectSemanticGuard(
            current.effect_id,
            current.version,
            current.state,
            transition_request.target_state,
            current.target_ref,
            current.payload_ref,
            transition_request.correlation_id,
            semantics,
        )
    return TransitionContext(
        (PassingGuard(),),
        authority
        or TransitionAuthorityDecision(
            transition_request.actor,
            DomainEntityType.EFFECT,
            current.effect_id,
            current.version,
            current.state,
            transition_request.target_state,
            TransitionAuthorityStatus.AUTHORIZED,
            transition_request.correlation_id,
        ),
        effect_semantic_guard=guard,
    )


class PassingGuard:
    def validate(
        self,
        entity: LifecycleEntity,
        transition_request: TransitionRequest[LifecycleState],
    ) -> None:
        assert entity.version == transition_request.expected_version


def test_simulation_binds_provenance_and_changes_only_state_version() -> None:
    current = effect()
    transition_request = request(current, EffectState.SIMULATED)
    before = tuple(getattr(current, field.name) for field in fields(current))
    result = transition_entity(
        current,
        transition_request,
        context(
            current, transition_request, EffectSimulationSemantics(simulation(current))
        ),
    )
    assert result.entity.state is EffectState.SIMULATED
    assert result.entity.version == current.version.next()
    assert result.event.event_type is DomainEventType.EFFECT_SIMULATED
    for field in fields(current):
        if field.name not in {"state", "version"}:
            assert getattr(result.entity, field.name) == getattr(current, field.name)
    assert tuple(getattr(current, field.name) for field in fields(current)) == before
    assert not hasattr(result.entity, "observation")
    assert not hasattr(result.entity, "authorization")


@pytest.mark.parametrize(
    "operation_scope",
    [
        lambda current: scope(current, effect_id=EffectId(OTHER)),
        lambda current: scope(current, version=EntityVersion(18)),
        lambda current: scope(current, target=EffectTargetRef("target-b")),
        lambda current: scope(current, payload=EffectPayloadRef("payload-b")),
        lambda current: scope(current, correlation=OTHER_CORRELATION),
    ],
)
def test_simulation_rejects_every_substituted_scope_dimension(
    operation_scope: Callable[[Effect], EffectOperationScope],
) -> None:
    current = effect()
    transition_request = request(current, EffectState.SIMULATED)
    mismatched_scope = operation_scope(current)
    with pytest.raises(InvariantViolation, match="Simulation provenance"):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                EffectSimulationSemantics(
                    simulation(current, operation_scope=mismatched_scope)
                ),
            ),
        )


def test_simulation_requires_provenance_and_separate_preparer() -> None:
    current = effect()
    transition_request = request(current, EffectState.SIMULATED)
    with pytest.raises(InvariantViolation, match="semantic guard is required"):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, None),
        )
    self_prepared = replace(
        simulation(current),
        simulated_by=identity(ActorType.WORKER, CONTROLLER),
    )
    with pytest.raises(InvariantViolation, match="separate from Effect controller"):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                EffectSimulationSemantics(self_prepared),
            ),
        )


def test_pending_commit_requires_guard_and_all_effect_edges_require_guards() -> None:
    current = effect()
    direct = request(current, EffectState.PENDING_COMMIT)
    with pytest.raises(InvariantViolation, match="semantic guard is required"):
        transition_entity(current, direct, context(current, direct, None))
    canonical_edges = {
        (EffectState.PLANNED, EffectState.SIMULATED),
        (EffectState.PLANNED, EffectState.PENDING_COMMIT),
        (EffectState.SIMULATED, EffectState.PENDING_COMMIT),
        (EffectState.PLANNED, EffectState.COMMITTED),
        (EffectState.SIMULATED, EffectState.COMMITTED),
        (EffectState.PENDING_COMMIT, EffectState.COMMITTED),
        (EffectState.QUARANTINED, EffectState.COMMITTED),
        (EffectState.PLANNED, EffectState.QUARANTINED),
        (EffectState.SIMULATED, EffectState.QUARANTINED),
        (EffectState.PENDING_COMMIT, EffectState.QUARANTINED),
        (EffectState.COMMITTED, EffectState.ROLLED_BACK),
        (EffectState.COMMITTED, EffectState.COMPENSATING),
        (EffectState.COMMITTED, EffectState.QUARANTINED),
        (EffectState.COMPENSATING, EffectState.COMPENSATED),
        (EffectState.COMPENSATING, EffectState.QUARANTINED),
    }
    remaining = {
        (source, target)
        for source in EffectState
        for target in EffectState
        if can_effect_transition(source, target)
        and (source, target) not in canonical_edges
    }
    assert (
        sum(
            can_effect_transition(source, target)
            for source in EffectState
            for target in EffectState
        )
        == 19
    )
    canonical_edges |= remaining
    assert len(canonical_edges) == 19
    assert not remaining - canonical_edges
    for source, target in remaining:
        snapshot = effect(source)
        unimplemented = request(snapshot, target)
        with pytest.raises(
            InvariantViolation, match="Canonical Effect semantic guard is required"
        ):
            transition_entity(
                snapshot,
                unimplemented,
                context(snapshot, unimplemented, None),
            )


def test_pending_commit_requires_exact_preparation_and_verification() -> None:
    current = effect(EffectState.SIMULATED)
    transition_request = request(current, EffectState.PENDING_COMMIT)
    result = transition_entity(
        current,
        transition_request,
        context(current, transition_request, pending_semantics(current)),
    )
    assert result.entity.state is EffectState.PENDING_COMMIT
    assert result.entity.version == current.version.next()
    assert result.event.event_type is DomainEventType.EFFECT_PENDING_COMMIT
    assert all(
        getattr(result.entity, field.name) == getattr(current, field.name)
        for field in fields(current)
        if field.name not in {"state", "version"}
    )


@pytest.mark.parametrize(
    "changes",
    [
        lambda current: {
            "operation_scope": scope(current, target=EffectTargetRef("target-b"))
        },
        lambda current: {
            "preparation": preparation(current, correlation=OTHER_CORRELATION)
        },
        lambda current: {
            "verification": verification(
                current,
                preparation(current),
                preparation_id=EffectPreparationRecordId(OTHER),
            )
        },
        lambda current: {
            "remediation_readiness": readiness(
                current,
                operation_scope=scope(current, payload=EffectPayloadRef("payload-b")),
            )
        },
        lambda current: {
            "simulation": simulation(
                current, operation_scope=scope(current, correlation=OTHER_CORRELATION)
            )
        },
    ],
)
def test_pending_commit_rejects_mismatched_supporting_provenance(
    changes: SemanticChanges,
) -> None:
    current = effect(EffectState.SIMULATED)
    transition_request = request(current, EffectState.PENDING_COMMIT)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                pending_semantics(current, **changes(current)),
            ),
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"verification": None},
        {"deduplication_ref": None},
    ],
)
def test_pending_commit_record_shapes_are_mandatory(changes: dict[str, object]) -> None:
    current = effect(EffectState.SIMULATED)
    with pytest.raises(InvalidDomainValue):
        pending_semantics(current, **changes)


def test_simulated_pending_commit_requires_simulation_provenance() -> None:
    current = effect(EffectState.SIMULATED)
    transition_request = request(current, EffectState.PENDING_COMMIT)
    with pytest.raises(InvariantViolation, match="requires simulation provenance"):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                pending_semantics(current, simulation=None),
            ),
        )


@pytest.mark.parametrize(
    "verified_by",
    [
        identity(ActorType.WORKER, VERIFIER),
        identity(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        identity(ActorType.EVALUATOR, PREPARER),
    ],
)
def test_pending_commit_rejects_worker_only_or_nonindependent_verifier(
    verified_by: ActorIdentity,
) -> None:
    current = effect(EffectState.SIMULATED)
    transition_request = request(current, EffectState.PENDING_COMMIT)
    prepared = preparation(current)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                pending_semantics(
                    current,
                    verification=verification(
                        current, prepared, verified_by=verified_by
                    ),
                ),
            ),
        )


@pytest.mark.parametrize("state", [EffectState.PLANNED, EffectState.SIMULATED])
def test_pending_commit_rejects_producer_verifying_under_evaluator_role(
    state: EffectState,
) -> None:
    current = effect(state)
    transition_request = request(current, EffectState.PENDING_COMMIT)
    prepared = preparation(current, prepared_by=identity(ActorType.WORKER, PREPARER))
    producer_as_evaluator = identity(ActorType.EVALUATOR, PRODUCER)

    with pytest.raises(InvariantViolation, match="producing principal"):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                pending_semantics(
                    current,
                    verification=verification(
                        current, prepared, verified_by=producer_as_evaluator
                    ),
                ),
            ),
        )


def test_planned_to_pending_commit_requires_accepted_independent_bypass() -> None:
    current = effect()
    transition_request = request(current, EffectState.PENDING_COMMIT)
    result = transition_entity(
        current,
        transition_request,
        context(current, transition_request, pending_semantics(current)),
    )
    assert result.entity.state is EffectState.PENDING_COMMIT
    for bypass_status in (
        EffectSimulationBypassStatus.REJECTED,
        EffectSimulationBypassStatus.UNRESOLVED,
    ):
        with pytest.raises(InvariantViolation, match="bypass"):
            transition_entity(
                current,
                transition_request,
                context(
                    current,
                    transition_request,
                    pending_semantics(
                        current, simulation_bypass=bypass(current, status=bypass_status)
                    ),
                ),
            )
    with pytest.raises(InvariantViolation, match="requires explicit simulation bypass"):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                pending_semantics(current, simulation_bypass=None),
            ),
        )


def test_bypass_is_exact_bound_and_separate_from_controller() -> None:
    current = effect()
    transition_request = request(current, EffectState.PENDING_COMMIT)
    for changed_bypass in (
        bypass(current, operation_scope=scope(current, effect_id=EffectId(OTHER))),
        bypass(current, operation_scope=scope(current, version=EntityVersion(18))),
        bypass(
            current, operation_scope=scope(current, target=EffectTargetRef("target-b"))
        ),
        bypass(
            current,
            operation_scope=scope(current, payload=EffectPayloadRef("payload-b")),
        ),
        bypass(current, operation_scope=scope(current, correlation=OTHER_CORRELATION)),
        bypass(current, decided_by=identity(ActorType.HUMAN_OPERATOR, CONTROLLER)),
    ):
        with pytest.raises(InvariantViolation):
            transition_entity(
                current,
                transition_request,
                context(
                    current,
                    transition_request,
                    pending_semantics(current, simulation_bypass=changed_bypass),
                ),
            )


@pytest.mark.parametrize(
    "status",
    [TransitionAuthorityStatus.DENIED, TransitionAuthorityStatus.UNRESOLVED],
)
def test_effect_m7b_authority_stays_mandatory_and_independent(
    status: TransitionAuthorityStatus,
) -> None:
    current = effect()
    transition_request = request(current, EffectState.SIMULATED)
    semantic = EffectSimulationSemantics(simulation(current))
    assert current.payload_ref is not None
    with pytest.raises(UnauthorizedTransition, match="decision is required"):
        transition_entity(
            current,
            transition_request,
            TransitionContext(
                (PassingGuard(),),
                effect_semantic_guard=EffectSemanticGuard(
                    current.effect_id,
                    current.version,
                    current.state,
                    transition_request.target_state,
                    current.target_ref,
                    current.payload_ref,
                    CORRELATION,
                    semantic,
                ),
            ),
        )
    with pytest.raises(UnauthorizedTransition):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                semantic,
                authority=replace(
                    TransitionAuthorityDecision(
                        transition_request.actor,
                        DomainEntityType.EFFECT,
                        current.effect_id,
                        current.version,
                        current.state,
                        transition_request.target_state,
                        TransitionAuthorityStatus.AUTHORIZED,
                        CORRELATION,
                    ),
                    decision=status,
                ),
            ),
        )
    for actor_type in (
        ActorType.WORKER,
        ActorType.EVALUATOR,
        ActorType.HUMAN_OPERATOR,
    ):
        ineligible_request = replace(
            transition_request,
            actor=identity(actor_type, CONTROLLER),
        )
        with pytest.raises(UnauthorizedTransition):
            transition_entity(
                current,
                ineligible_request,
                context(
                    current,
                    ineligible_request,
                    semantic,
                    authority=TransitionAuthorityDecision(
                        ineligible_request.actor,
                        DomainEntityType.EFFECT,
                        current.effect_id,
                        current.version,
                        current.state,
                        ineligible_request.target_state,
                        TransitionAuthorityStatus.AUTHORIZED,
                        CORRELATION,
                    ),
                ),
            )
