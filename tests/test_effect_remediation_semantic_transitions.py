"""M7C6C canonical Effect rollback and compensation semantic guards."""

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
    DomainEvent,
    DomainEventMetadata,
    DomainEventType,
    Effect,
    EffectCompensationCompletionId,
    EffectCompensationCompletionRecord,
    EffectCompensationCompletionSemantics,
    EffectCompensationPlanId,
    EffectCompensationPlanRecord,
    EffectCompensationStartSemantics,
    EffectDeduplicationRef,
    EffectExecutionAuthorizationId,
    EffectExecutionAuthorizationRecord,
    EffectExternalOperationRef,
    EffectId,
    EffectObservationId,
    EffectObservationRecord,
    EffectOccurrenceStatus,
    EffectPayloadRef,
    EffectPreparationRecordId,
    EffectRemediationAuthorizationDecision,
    EffectRemediationAuthorizationRef,
    EffectRemediationAuthorizationScope,
    EffectRemediationAuthorizationSemantics,
    EffectRemediationAuthorizationStatus,
    EffectRemediationHumanAuthorization,
    EffectRemediationKind,
    EffectRollbackRecord,
    EffectRollbackRecordId,
    EffectRollbackSemantics,
    EffectSemanticGuard,
    EffectState,
    EffectTargetRef,
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
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
PRODUCER = UUID("00000000-1234-4234-8234-123456789abc")
ORIGINAL_OBSERVER = UUID("01000000-1234-4234-8234-123456789abc")
PLANNER = UUID("11111111-1234-4234-8234-123456789abc")
VERIFIER = UUID("22222222-1234-4234-8234-123456789abc")
START_CONTROLLER = UUID("33333333-1234-4234-8234-123456789abc")
COMPLETION_CONTROLLER = UUID("34333333-1234-4234-8234-123456789abc")
POLICY = UUID("44444444-1234-4234-8234-123456789abc")
HUMAN = UUID("55555555-1234-4234-8234-123456789abc")
COMMITTED_VERSION = EntityVersion(17)
ORIGINAL_VERSION = EntityVersion(12)
CORRELATION = CorrelationId(VALUE)
ORIGINAL_CORRELATION = CorrelationId(OTHER)
NOW = Timestamp(datetime(2026, 9, 13, tzinfo=UTC))
ORIGINAL_OPERATION = EffectExternalOperationRef("original-operation")
RESTORATION_OPERATION = EffectExternalOperationRef("restoration-operation")
DEDUPLICATION = EffectDeduplicationRef("original-deduplication")
ORIGINAL_OBSERVATION_ID = EffectObservationId(VALUE)
PLAN_ID = EffectCompensationPlanId(VALUE)
COMPENSATING_EFFECT_ID = EffectId(OTHER)


def actor(actor_type: ActorType, value: UUID) -> ActorIdentity:
    return ActorIdentity(ActorId(value), actor_type)


def effect(
    state: EffectState,
    version: EntityVersion = COMMITTED_VERSION,
) -> Effect:
    return Effect(
        EffectId(VALUE),
        state,
        version,
        PlannedEffectOrigin(TaskId(VALUE), actor(ActorType.WORKER, PRODUCER)),
        EffectTargetRef("target-a"),
        EffectPayloadRef("payload-a"),
    )


def original_observation(
    current: Effect,
    *,
    observation_id: EffectObservationId = ORIGINAL_OBSERVATION_ID,
    version: EntityVersion = ORIGINAL_VERSION,
) -> EffectObservationRecord:
    return EffectObservationRecord(
        observation_id,
        current.effect_id,
        version,
        ORIGINAL_OPERATION,
        DEDUPLICATION,
        EffectOccurrenceStatus.CONFIRMED,
        current.target_ref,
        current.payload_ref,
        frozenset({EvidenceRef("original external receipt")}),
        actor(ActorType.EVALUATOR, ORIGINAL_OBSERVER),
        actor(ActorType.EFFECT_CONTROLLER, START_CONTROLLER),
        NOW,
        NOW,
        NOW,
        ORIGINAL_CORRELATION,
    )


def rollback_record(
    current: Effect,
    *,
    verified_by: ActorIdentity | None = None,
    original_id: EffectObservationId = ORIGINAL_OBSERVATION_ID,
    operation: EffectExternalOperationRef = RESTORATION_OPERATION,
) -> EffectRollbackRecord:
    return EffectRollbackRecord(
        EffectRollbackRecordId(VALUE),
        current.effect_id,
        current.version,
        original_id,
        operation,
        "Independent evidence establishes restoration of the prior state.",
        frozenset({EvidenceRef("restoration readback")}),
        verified_by or actor(ActorType.EVALUATOR, VERIFIER),
        actor(ActorType.EFFECT_CONTROLLER, START_CONTROLLER),
        NOW,
        NOW,
        CORRELATION,
    )


def compensation_plan(
    current: Effect,
    *,
    plan_id: EffectCompensationPlanId = PLAN_ID,
    compensating_ids: frozenset[EffectId] = frozenset({COMPENSATING_EFFECT_ID}),
) -> EffectCompensationPlanRecord:
    return EffectCompensationPlanRecord(
        plan_id,
        current.effect_id,
        current.version,
        ORIGINAL_OBSERVATION_ID,
        compensating_ids,
        "Governed linked Effects compensate without erasing the original action.",
        frozenset({EvidenceRef("compensation plan evidence")}),
        actor(ActorType.WORKER, PLANNER),
        actor(ActorType.EFFECT_CONTROLLER, START_CONTROLLER),
        NOW,
        NOW,
        CORRELATION,
    )


def authorization_scope(
    current: Effect,
    *,
    plan: EffectCompensationPlanRecord | None = None,
    operation: EffectExternalOperationRef = RESTORATION_OPERATION,
) -> EffectRemediationAuthorizationScope:
    if plan is None:
        return EffectRemediationAuthorizationScope(
            current.effect_id,
            current.version,
            ORIGINAL_OBSERVATION_ID,
            EffectRemediationKind.ROLLBACK,
            CORRELATION,
            restoration_operation_ref=operation,
        )
    return EffectRemediationAuthorizationScope(
        current.effect_id,
        plan.observed_effect_version,
        ORIGINAL_OBSERVATION_ID,
        EffectRemediationKind.COMPENSATION,
        CORRELATION,
        compensation_plan_id=plan.plan_id,
        compensating_effect_ids=plan.compensating_effect_ids,
    )


def authorization(
    scope: EffectRemediationAuthorizationScope,
    *,
    status: EffectRemediationAuthorizationStatus = (
        EffectRemediationAuthorizationStatus.AUTHORIZED
    ),
    human_required: bool = True,
    policy_actor: ActorIdentity | None = None,
    human_actor: ActorIdentity | None = None,
    include_human: bool = True,
) -> EffectRemediationAuthorizationSemantics:
    policy_ref = EffectRemediationAuthorizationRef("remediation-policy-authorization")
    policy = EffectRemediationAuthorizationDecision(
        policy_ref,
        scope,
        status,
        policy_actor or actor(ActorType.POLICY_ENGINE, POLICY),
        frozenset({EvidenceRef("policy authorization evidence")}),
        human_required,
    )
    human = None
    if include_human:
        human = EffectRemediationHumanAuthorization(
            EffectRemediationAuthorizationRef("human-remediation-authorization"),
            scope,
            policy_ref,
            True,
            human_actor or actor(ActorType.HUMAN_OPERATOR, HUMAN),
            frozenset({EvidenceRef("explicit human authorization evidence")}),
        )
    return EffectRemediationAuthorizationSemantics(policy, human)


def rollback_semantics(
    current: Effect,
    *,
    original: EffectObservationRecord | None = None,
    rollback: EffectRollbackRecord | None = None,
    authorized: EffectRemediationAuthorizationSemantics | None = None,
) -> EffectRollbackSemantics:
    record = rollback or rollback_record(current)
    return EffectRollbackSemantics(
        original or original_observation(current),
        record,
        authorized or authorization(authorization_scope(current)),
    )


def start_semantics(
    current: Effect,
    *,
    plan: EffectCompensationPlanRecord | None = None,
    authorized: EffectRemediationAuthorizationSemantics | None = None,
) -> EffectCompensationStartSemantics:
    selected_plan = plan or compensation_plan(current)
    return EffectCompensationStartSemantics(
        original_observation(current),
        selected_plan,
        authorized or authorization(authorization_scope(current, plan=selected_plan)),
    )


def completion_record(
    current: Effect,
    plan: EffectCompensationPlanRecord,
    *,
    verified_by: ActorIdentity | None = None,
) -> EffectCompensationCompletionRecord:
    return EffectCompensationCompletionRecord(
        EffectCompensationCompletionId(VALUE),
        plan.plan_id,
        current.effect_id,
        current.version,
        ORIGINAL_OBSERVATION_ID,
        "Every linked compensation Effect completed.",
        "The original occurrence remains historical and externally observable.",
        frozenset({EvidenceRef("independent compensation completion evidence")}),
        verified_by or actor(ActorType.EVALUATOR, VERIFIER),
        actor(ActorType.EFFECT_CONTROLLER, COMPLETION_CONTROLLER),
        NOW,
        NOW,
        CORRELATION,
    )


def completion_semantics(
    current: Effect,
    plan: EffectCompensationPlanRecord,
    *,
    completion: EffectCompensationCompletionRecord | None = None,
    authorized: EffectRemediationAuthorizationSemantics | None = None,
) -> EffectCompensationCompletionSemantics:
    committed = effect(EffectState.COMMITTED, plan.observed_effect_version)
    return EffectCompensationCompletionSemantics(
        original_observation(current),
        plan,
        completion or completion_record(current, plan),
        authorized or authorization(authorization_scope(committed, plan=plan)),
    )


def request(
    current: Effect,
    target: EffectState,
    *,
    controller: UUID = START_CONTROLLER,
    event_id: UUID = VALUE,
) -> TransitionRequest[EffectState]:
    return TransitionRequest(
        EventId(event_id),
        target,
        actor(ActorType.EFFECT_CONTROLLER, controller),
        TransitionReason("Canonical Effect remediation transition"),
        current.version,
        NOW,
        CORRELATION,
    )


def context(
    current: Effect,
    transition_request: TransitionRequest[EffectState],
    semantics: (
        EffectRollbackSemantics
        | EffectCompensationStartSemantics
        | EffectCompensationCompletionSemantics
        | None
    ),
    *,
    authority: TransitionAuthorityDecision | None = None,
    with_authority: bool = True,
    start_event: DomainEvent | None = None,
) -> TransitionContext:
    guard = None
    if semantics is not None:
        guard = EffectSemanticGuard(
            current.effect_id,
            current.version,
            current.state,
            transition_request.target_state,
            current.target_ref,
            current.payload_ref,
            CORRELATION,
            semantics,
        )
    return TransitionContext(
        (PassingGuard(),),
        (
            authority
            or TransitionAuthorityDecision(
                transition_request.actor,
                DomainEntityType.EFFECT,
                current.effect_id,
                current.version,
                current.state,
                transition_request.target_state,
                TransitionAuthorityStatus.AUTHORIZED,
                CORRELATION,
            )
            if with_authority
            else None
        ),
        effect_semantic_guard=guard,
        effect_compensation_start_event=start_event,
    )


class PassingGuard:
    def validate(
        self,
        entity: LifecycleEntity,
        transition_request: TransitionRequest[LifecycleState],
    ) -> None:
        assert entity.version == transition_request.expected_version


def transition_compensation_start() -> tuple[
    EffectCompensationPlanRecord, Effect, DomainEvent
]:
    committed = effect(EffectState.COMMITTED)
    plan = compensation_plan(committed)
    transition_request = request(committed, EffectState.COMPENSATING)
    result = transition_entity(
        committed,
        transition_request,
        context(committed, transition_request, start_semantics(committed, plan=plan)),
    )
    return plan, result.entity, result.event


def test_valid_rollback_exact_binds_commit_restoration_and_authorization() -> None:
    current = effect(EffectState.COMMITTED)
    transition_request = request(current, EffectState.ROLLED_BACK)
    before = tuple(getattr(current, field.name) for field in fields(current))
    result = transition_entity(
        current,
        transition_request,
        context(current, transition_request, rollback_semantics(current)),
    )
    assert result.entity.state is EffectState.ROLLED_BACK
    assert result.entity.version == current.version.next()
    assert all(
        getattr(result.entity, field.name) == before[index]
        for index, field in enumerate(fields(current))
        if field.name not in {"state", "version"}
    )
    assert result.event.event_type is DomainEventType.EFFECT_ROLLED_BACK
    assert result.event.metadata.annotations == frozenset(
        {
            ("rollback_record_id", str(VALUE)),
            ("original_commit_observation_id", str(VALUE)),
            ("remediation_authorization_ref", "remediation-policy-authorization"),
        }
    )


@pytest.mark.parametrize(
    "original",
    [
        lambda current: original_observation(
            current, observation_id=EffectObservationId(OTHER)
        ),
        lambda current: original_observation(
            current, version=EntityVersion(current.version.value + 1)
        ),
    ],
)
def test_rollback_rejects_wrong_or_future_original_commit(
    original: Callable[[Effect], EffectObservationRecord],
) -> None:
    current = effect(EffectState.COMMITTED)
    transition_request = request(current, EffectState.ROLLED_BACK)
    supplied = original(current)
    with pytest.raises(InvariantViolation, match="Original commit observation"):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                rollback_semantics(current, original=supplied),
            ),
        )


def test_rollback_accepts_compatible_historical_commit_version() -> None:
    current = effect(EffectState.COMMITTED)
    transition_request = request(current, EffectState.ROLLED_BACK)
    historical = original_observation(current, version=EntityVersion(1))
    result = transition_entity(
        current,
        transition_request,
        context(
            current,
            transition_request,
            rollback_semantics(current, original=historical),
        ),
    )
    assert result.entity.state is EffectState.ROLLED_BACK


def test_rollback_authorization_must_bind_actual_restoration_operation() -> None:
    current = effect(EffectState.COMMITTED)
    transition_request = request(current, EffectState.ROLLED_BACK)
    wrong_scope = authorization_scope(
        current, operation=EffectExternalOperationRef("different-restoration")
    )
    with pytest.raises(InvariantViolation, match="policy authorization"):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                rollback_semantics(current, authorized=authorization(wrong_scope)),
            ),
        )


def test_normal_commit_authorization_cannot_substitute_for_remediation() -> None:
    current = effect(EffectState.COMMITTED)
    normal_commit_authorization = EffectExecutionAuthorizationRecord(
        EffectExecutionAuthorizationId(VALUE),
        EffectPreparationRecordId(VALUE),
        current.effect_id,
        current.version,
        frozenset({EffectVerificationRecordId(VALUE)}),
        "Normal prospective commit authorization is not remedy authorization.",
        frozenset({EvidenceRef("normal commit authorization evidence")}),
        actor(ActorType.POLICY_ENGINE, POLICY),
        actor(ActorType.EFFECT_CONTROLLER, START_CONTROLLER),
        NOW,
        NOW,
        CORRELATION,
    )
    with pytest.raises(
        InvalidDomainValue, match="EffectRemediationAuthorizationSemantics"
    ):
        EffectRollbackSemantics(
            original_observation(current),
            rollback_record(current),
            normal_commit_authorization,  # type: ignore[arg-type]
        )


def test_rollback_verifier_cannot_relabel_controller_principal() -> None:
    current = effect(EffectState.COMMITTED)
    transition_request = request(current, EffectState.ROLLED_BACK)
    relabeled = actor(ActorType.EVALUATOR, START_CONTROLLER)
    record = rollback_record(current, verified_by=relabeled)
    with pytest.raises(InvariantViolation, match="independent EVALUATOR principal"):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                rollback_semantics(current, rollback=record),
            ),
        )


@pytest.mark.parametrize(
    ("status", "human_required", "include_human"),
    [
        (EffectRemediationAuthorizationStatus.DENIED, True, True),
        (EffectRemediationAuthorizationStatus.UNRESOLVED, True, True),
        (EffectRemediationAuthorizationStatus.AUTHORIZED, True, False),
    ],
)
def test_compensation_start_requires_authorized_plan_and_required_human(
    status: EffectRemediationAuthorizationStatus,
    human_required: bool,
    include_human: bool,
) -> None:
    current = effect(EffectState.COMMITTED)
    plan = compensation_plan(current)
    authorized = authorization(
        authorization_scope(current, plan=plan),
        status=status,
        human_required=human_required,
        include_human=include_human,
    )
    transition_request = request(current, EffectState.COMPENSATING)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                start_semantics(current, plan=plan, authorized=authorized),
            ),
        )


def test_compensation_start_exact_binds_plan_linked_effects_and_event_lineage() -> None:
    plan, compensating, event = transition_compensation_start()
    assert compensating.state is EffectState.COMPENSATING
    assert compensating.version == COMMITTED_VERSION.next()
    assert event.event_type is DomainEventType.EFFECT_COMPENSATION_STARTED
    assert event.metadata.annotations == frozenset(
        {
            ("compensation_start_event_id", str(event.event_id.value)),
            ("compensation_plan_id", str(plan.plan_id.value)),
            ("compensating_effect_ids", str(COMPENSATING_EFFECT_ID.value)),
            ("original_commit_observation_id", str(ORIGINAL_OBSERVATION_ID.value)),
            ("remediation_authorization_ref", "remediation-policy-authorization"),
        }
    )


def test_compensation_start_rejects_linked_identity_authorization_substitution() -> (
    None
):
    current = effect(EffectState.COMMITTED)
    plan = compensation_plan(current)
    different = EffectId(UUID("99999999-1234-4234-8234-123456789abc"))
    wrong_plan = replace(plan, compensating_effect_ids=frozenset({different}))
    authorized = authorization(authorization_scope(current, plan=plan))
    transition_request = request(current, EffectState.COMPENSATING)
    with pytest.raises(InvariantViolation, match="policy authorization"):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                start_semantics(current, plan=wrong_plan, authorized=authorized),
            ),
        )


def test_valid_compensation_completion_exact_binds_start_and_preserves_residual() -> (
    None
):
    plan, compensating, start_event = transition_compensation_start()
    transition_request = request(
        compensating,
        EffectState.COMPENSATED,
        controller=COMPLETION_CONTROLLER,
        event_id=OTHER,
    )
    semantics = completion_semantics(compensating, plan)
    before = tuple(getattr(compensating, field.name) for field in fields(compensating))
    result = transition_entity(
        compensating,
        transition_request,
        context(
            compensating,
            transition_request,
            semantics,
            start_event=start_event,
        ),
    )
    assert result.entity.state is EffectState.COMPENSATED
    assert result.entity.version == compensating.version.next()
    assert all(
        getattr(result.entity, field.name) == before[index]
        for index, field in enumerate(fields(compensating))
        if field.name not in {"state", "version"}
    )
    assert semantics.completion_record.residual_impact_summary.startswith(
        "The original occurrence remains historical"
    )
    assert result.event.event_type is DomainEventType.EFFECT_COMPENSATED
    assert (
        "compensation_completion_id",
        str(semantics.completion_record.completion_id.value),
    ) in result.event.metadata.annotations
    assert (
        "compensation_start_event_id",
        str(start_event.event_id.value),
    ) in result.event.metadata.annotations


@pytest.mark.parametrize("substitution", ["plan", "linked-effects", "start-lineage"])
def test_compensation_completion_rejects_plan_or_start_substitution(
    substitution: str,
) -> None:
    plan, compensating, start_event = transition_compensation_start()
    selected_plan = plan
    selected_event = start_event
    if substitution == "plan":
        selected_plan = replace(plan, plan_id=EffectCompensationPlanId(OTHER))
    elif substitution == "linked-effects":
        selected_plan = replace(
            plan,
            compensating_effect_ids=frozenset(
                {EffectId(UUID("99999999-1234-4234-8234-123456789abc"))}
            ),
        )
    else:
        selected_event = replace(start_event, event_id=EventId(OTHER))
    completion = completion_record(compensating, selected_plan)
    committed = effect(EffectState.COMMITTED, selected_plan.observed_effect_version)
    authorized = authorization(authorization_scope(committed, plan=selected_plan))
    semantics = completion_semantics(
        compensating,
        selected_plan,
        completion=completion,
        authorized=authorized,
    )
    transition_request = request(
        compensating,
        EffectState.COMPENSATED,
        controller=COMPLETION_CONTROLLER,
        event_id=UUID("77777777-1234-4234-8234-123456789abc"),
    )
    with pytest.raises(InvariantViolation, match="start event"):
        transition_entity(
            compensating,
            transition_request,
            context(
                compensating,
                transition_request,
                semantics,
                start_event=selected_event,
            ),
        )


def test_completion_requires_independent_verifier_from_start_controller() -> None:
    plan, compensating, start_event = transition_compensation_start()
    relabeled = actor(ActorType.EVALUATOR, START_CONTROLLER)
    completion = completion_record(compensating, plan, verified_by=relabeled)
    semantics = completion_semantics(compensating, plan, completion=completion)
    transition_request = request(
        compensating,
        EffectState.COMPENSATED,
        controller=COMPLETION_CONTROLLER,
        event_id=OTHER,
    )
    with pytest.raises(InvariantViolation, match="compensation-start controller"):
        transition_entity(
            compensating,
            transition_request,
            context(
                compensating,
                transition_request,
                semantics,
                start_event=start_event,
            ),
        )


def test_completion_requires_actual_start_event() -> None:
    plan, compensating, _ = transition_compensation_start()
    transition_request = request(
        compensating,
        EffectState.COMPENSATED,
        controller=COMPLETION_CONTROLLER,
        event_id=OTHER,
    )
    with pytest.raises(InvariantViolation, match="authoritative start event"):
        transition_entity(
            compensating,
            transition_request,
            context(
                compensating,
                transition_request,
                completion_semantics(compensating, plan),
            ),
        )


def test_generic_guard_cannot_substitute_for_remediation_semantic_guard() -> None:
    current = effect(EffectState.COMMITTED)
    transition_request = request(current, EffectState.ROLLED_BACK)
    with pytest.raises(InvariantViolation, match="semantic guard is required"):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, None),
        )


def test_m7b1_and_m7b2_remain_mandatory_before_remediation_semantics() -> None:
    current = effect(EffectState.COMMITTED)
    transition_request = request(current, EffectState.ROLLED_BACK)
    semantics = rollback_semantics(current)
    with pytest.raises(UnauthorizedTransition, match="decision is required"):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                semantics,
                with_authority=False,
            ),
        )

    worker_request = replace(
        transition_request, actor=actor(ActorType.WORKER, START_CONTROLLER)
    )
    worker_authority = TransitionAuthorityDecision(
        worker_request.actor,
        DomainEntityType.EFFECT,
        current.effect_id,
        current.version,
        current.state,
        worker_request.target_state,
        TransitionAuthorityStatus.AUTHORIZED,
        CORRELATION,
    )
    with pytest.raises(UnauthorizedTransition, match="not eligible"):
        transition_entity(
            current,
            worker_request,
            context(
                current,
                worker_request,
                semantics,
                authority=worker_authority,
            ),
        )


IMPLEMENTED_EFFECT_EDGES: frozenset[tuple[EffectState, EffectState]] = frozenset(
    {
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
        (EffectState.COMMITTED, EffectState.QUARANTINED),
        (EffectState.COMPENSATING, EffectState.QUARANTINED),
        (EffectState.COMMITTED, EffectState.ROLLED_BACK),
        (EffectState.COMMITTED, EffectState.COMPENSATING),
        (EffectState.COMPENSATING, EffectState.COMPENSATED),
    }
)
DEFERRED_QUARANTINE_EDGES: frozenset[tuple[EffectState, EffectState]] = frozenset(
    {
        (EffectState.QUARANTINED, EffectState.PENDING_COMMIT),
        (EffectState.QUARANTINED, EffectState.ROLLED_BACK),
        (EffectState.QUARANTINED, EffectState.COMPENSATING),
        (EffectState.QUARANTINED, EffectState.COMPENSATED),
    }
)


def edge_sort_key(edge: tuple[EffectState, EffectState]) -> tuple[str, str]:
    return edge[0].value, edge[1].value


SORTED_IMPLEMENTED_EFFECT_EDGES: tuple[tuple[EffectState, EffectState], ...] = tuple(
    sorted(IMPLEMENTED_EFFECT_EDGES, key=edge_sort_key)
)


@pytest.mark.parametrize(
    ("source", "target"),
    SORTED_IMPLEMENTED_EFFECT_EDGES,
)
def test_exactly_fifteen_effect_edges_reach_canonical_semantic_guard(
    source: EffectState, target: EffectState
) -> None:
    current = effect(source)
    transition_request = request(current, target)
    with pytest.raises(InvariantViolation, match="semantic guard is required"):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, None),
        )


@pytest.mark.parametrize(("source", "target"), DEFERRED_QUARANTINE_EDGES)
def test_exactly_four_quarantine_remediation_edges_remain_deny_by_default(
    source: EffectState, target: EffectState
) -> None:
    assert can_effect_transition(source, target)
    current = effect(source)
    transition_request = request(current, target)
    with pytest.raises(InvariantViolation, match="denies this unimplemented edge"):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, None),
        )


def test_effect_topology_remains_exactly_nineteen_with_strict_sinks() -> None:
    structural_edges = {
        (source, target)
        for source in EffectState
        for target in EffectState
        if can_effect_transition(source, target)
    }
    assert structural_edges == IMPLEMENTED_EFFECT_EDGES | DEFERRED_QUARANTINE_EDGES
    assert len(structural_edges) == 19
    assert not can_effect_transition(EffectState.COMMITTED, EffectState.COMPENSATED)
    for sink in (EffectState.ROLLED_BACK, EffectState.COMPENSATED):
        assert all(not can_effect_transition(sink, target) for target in EffectState)


def test_fabricated_start_event_metadata_cannot_complete_compensation() -> None:
    plan, compensating, start_event = transition_compensation_start()
    fabricated = replace(
        start_event,
        metadata=DomainEventMetadata(
            EffectState.COMMITTED,
            EffectState.COMPENSATING,
            frozenset(
                {
                    ("compensation_start_event_id", str(start_event.event_id.value)),
                    ("compensation_plan_id", str(plan.plan_id.value)),
                }
            ),
        ),
    )
    transition_request = request(
        compensating,
        EffectState.COMPENSATED,
        controller=COMPLETION_CONTROLLER,
        event_id=OTHER,
    )
    with pytest.raises(InvariantViolation, match="start event"):
        transition_entity(
            compensating,
            transition_request,
            context(
                compensating,
                transition_request,
                completion_semantics(compensating, plan),
                start_event=fabricated,
            ),
        )
