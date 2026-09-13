"""Direct deterministic regression tests for Issue #59 quarantine exits."""

from dataclasses import replace
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
    EffectId,
    EffectObservationId,
    EffectObservationRecord,
    EffectObservationScope,
    EffectOccurrenceStatus,
    EffectPayloadRef,
    EffectQuarantineCompensationCompletionSemantics,
    EffectQuarantineCompensationMode,
    EffectQuarantineCompensationStartSemantics,
    EffectQuarantineContext,
    EffectQuarantineContextId,
    EffectQuarantineReason,
    EffectQuarantineRollbackSemantics,
    EffectReconciliationConclusion,
    EffectReconciliationRecord,
    EffectReconciliationRecordId,
    EffectRemediationAuthorizationDecision,
    EffectRemediationAuthorizationRef,
    EffectRemediationAuthorizationScope,
    EffectRemediationAuthorizationSemantics,
    EffectRemediationAuthorizationStatus,
    EffectRemediationHumanAuthorization,
    EffectRemediationKind,
    EffectRemediationPolicyRef,
    EffectRollbackRecord,
    EffectRollbackRecordId,
    EffectRollbackSemantics,
    EffectSemanticGuard,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    EventId,
    EvidenceRef,
    InvariantViolation,
    PlannedEffectOrigin,
    TaskId,
    Timestamp,
    TransitionAuthorityDecision,
    TransitionAuthorityStatus,
    TransitionContext,
    TransitionReason,
    TransitionRequest,
    transition_entity,
)
from symphony_k.domain.effect import EffectExternalOperationRef

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
PRODUCER = UUID("00000000-1234-4234-8234-123456789abc")
CONTROLLER = UUID("33333333-1234-4234-8234-123456789abc")
EVALUATOR = UUID("22222222-1234-4234-8234-123456789abc")
CURRENT_CONTROLLER = UUID("34333333-1234-4234-8234-123456789abc")
PLANNER = UUID("11111111-1234-4234-8234-123456789abc")
POLICY = UUID("44444444-1234-4234-8234-123456789abc")
HUMAN = UUID("55555555-1234-4234-8234-123456789abc")
NOW = Timestamp(datetime(2026, 9, 13, tzinfo=UTC))
CORRELATION = CorrelationId(VALUE)


def actor(kind: ActorType, value: UUID) -> ActorIdentity:
    return ActorIdentity(ActorId(value), kind)


def quarantined() -> Effect:
    return Effect(
        EffectId(VALUE),
        EffectState.QUARANTINED,
        EntityVersion(17),
        PlannedEffectOrigin(TaskId(VALUE), actor(ActorType.WORKER, PRODUCER)),
        EffectTargetRef("target-a"),
        EffectPayloadRef("payload-a"),
    )


def original_observation(current: Effect) -> EffectObservationRecord:
    return EffectObservationRecord(
        EffectObservationId(OTHER),
        current.effect_id,
        EntityVersion(12),
        EffectExternalOperationRef("operation-a"),
        EffectDeduplicationRef("dedupe-a"),
        EffectOccurrenceStatus.CONFIRMED,
        current.target_ref,
        current.payload_ref,
        frozenset({EvidenceRef("original receipt")}),
        actor(ActorType.EVALUATOR, EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        NOW,
        NOW,
        CORRELATION,
    )


def compensation_plan(current: Effect) -> EffectCompensationPlanRecord:
    return EffectCompensationPlanRecord(
        EffectCompensationPlanId(VALUE),
        current.effect_id,
        EntityVersion(15),
        EffectObservationId(OTHER),
        frozenset({EffectId(UUID("99999999-1234-4234-8234-123456789abc"))}),
        "A governed compensation plan retains the original occurrence.",
        frozenset({EvidenceRef("plan")}),
        actor(ActorType.WORKER, PLANNER),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        NOW,
        CORRELATION,
    )


def remediation_authorization(
    scope: EffectRemediationAuthorizationScope, recorder: UUID
) -> EffectRemediationAuthorizationSemantics:
    decision = EffectRemediationAuthorizationDecision(
        EffectRemediationAuthorizationRef("policy-decision"),
        scope,
        EffectRemediationPolicyRef("remediation", "v1"),
        EffectRemediationAuthorizationStatus.AUTHORIZED,
        True,
        frozenset({EvidenceRef("policy")}),
        actor(ActorType.POLICY_ENGINE, POLICY),
        actor(ActorType.EFFECT_CONTROLLER, recorder),
        NOW,
        NOW,
    )
    return EffectRemediationAuthorizationSemantics(
        decision,
        EffectRemediationHumanAuthorization(
            EffectRemediationAuthorizationRef("human-decision"),
            scope,
            decision.policy_ref,
            decision.decision_ref,
            True,
            frozenset({EvidenceRef("human")}),
            actor(ActorType.HUMAN_OPERATOR, HUMAN),
            actor(ActorType.EFFECT_CONTROLLER, recorder),
            NOW,
            NOW,
        ),
    )


def compensation_scope(
    current: Effect, plan: EffectCompensationPlanRecord, version: EntityVersion
) -> EffectRemediationAuthorizationScope:
    return EffectRemediationAuthorizationScope(
        current.effect_id,
        version,
        plan.original_commit_observation_id,
        EffectRemediationKind.COMPENSATION,
        CORRELATION,
        compensation_plan_id=plan.plan_id,
        compensating_effect_ids=plan.compensating_effect_ids,
    )


def quarantine_compensation_context(
    current: Effect, plan: EffectCompensationPlanRecord
) -> EffectQuarantineContext:
    return EffectQuarantineContext(
        EffectQuarantineContextId(VALUE),
        EffectObservationScope(
            current.effect_id,
            EntityVersion(16),
            EffectState.COMPENSATING,
            EffectState.QUARANTINED,
            current.target_ref,
            EffectExternalOperationRef("operation-a"),
            EffectDeduplicationRef("dedupe-a"),
            CORRELATION,
        ),
        EffectQuarantineReason.COMPENSATION_OR_REMEDIATION_UNCERTAINTY,
        "Controlled remediation reconciliation.",
        frozenset({EvidenceRef("quarantine")}),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        original_commit_observation_id=plan.original_commit_observation_id,
        compensation_plan_id=plan.plan_id,
    )


def quarantine_post_commit_context(current: Effect) -> EffectQuarantineContext:
    return EffectQuarantineContext(
        EffectQuarantineContextId(VALUE),
        EffectObservationScope(
            current.effect_id,
            EntityVersion(16),
            EffectState.COMMITTED,
            EffectState.QUARANTINED,
            current.target_ref,
            EffectExternalOperationRef("operation-a"),
            EffectDeduplicationRef("dedupe-a"),
            CORRELATION,
        ),
        EffectQuarantineReason.POST_COMMIT_PROBLEM,
        "Controlled post-commit remediation reconciliation.",
        frozenset({EvidenceRef("quarantine")}),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        original_commit_observation_id=EffectObservationId(OTHER),
    )


def reconciliation_for(
    current: Effect, context: EffectQuarantineContext, controller: UUID
) -> EffectReconciliationRecord:
    return EffectReconciliationRecord(
        EffectReconciliationRecordId(OTHER),
        current.effect_id,
        current.version,
        context.context_id,
        EffectReconciliationConclusion.REMEDIAL_UNCERTAINTY_RECONCILED,
        "Independent reconciliation closed the remediation uncertainty.",
        frozenset({EvidenceRef("reconciliation")}),
        actor(ActorType.EVALUATOR, EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER, controller),
        NOW,
        NOW,
        CORRELATION,
    )


def transition_request(
    current: Effect, target: EffectState, controller: UUID, event: UUID
) -> TransitionRequest[EffectState]:
    return TransitionRequest(
        EventId(event),
        target,
        actor(ActorType.EFFECT_CONTROLLER, controller),
        TransitionReason("Canonical quarantine exit"),
        current.version,
        NOW,
        CORRELATION,
    )


def transition_context(
    current: Effect,
    request: TransitionRequest[EffectState],
    semantics: object,
    start_event: DomainEvent | None = None,
) -> TransitionContext:
    guard = EffectSemanticGuard(
        current.effect_id,
        current.version,
        current.state,
        request.target_state,
        current.target_ref,
        current.payload_ref,
        CORRELATION,
        semantics,  # type: ignore[arg-type]
    )
    return TransitionContext(
        (PassingGuard(),),
        TransitionAuthorityDecision(
            request.actor,
            DomainEntityType.EFFECT,
            current.effect_id,
            current.version,
            current.state,
            request.target_state,
            TransitionAuthorityStatus.AUTHORIZED,
            CORRELATION,
        ),
        effect_semantic_guard=guard,
        effect_compensation_start_event=start_event,
    )


class PassingGuard:
    def validate(self, entity: object, request: object) -> None:
        del entity, request


def start_event(
    current: Effect,
    plan: EffectCompensationPlanRecord,
    authorization: EffectRemediationAuthorizationSemantics,
) -> DomainEvent:
    annotations = frozenset(
        {
            ("compensation_start_event_id", str(OTHER)),
            ("compensation_plan_id", str(plan.plan_id.value)),
            (
                "compensating_effect_ids",
                ",".join(
                    sorted(str(value.value) for value in plan.compensating_effect_ids)
                ),
            ),
            (
                "original_commit_observation_id",
                str(plan.original_commit_observation_id.value),
            ),
            (
                "remediation_authorization_ref",
                authorization.policy_decision.decision_ref.value,
            ),
        }
    )
    return DomainEvent(
        EventId(OTHER),
        DomainEventType.EFFECT_COMPENSATION_STARTED,
        DomainEntityType.EFFECT,
        current.effect_id,
        EntityVersion(16),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        CORRELATION,
        None,
        TransitionReason("Historical compensation start"),
        DomainEventMetadata(
            EffectState.COMMITTED, EffectState.COMPENSATING, annotations
        ),
    )


def test_post_commit_rollback_and_new_compensation_retain_exit_provenance() -> None:
    current = quarantined()
    context = quarantine_post_commit_context(current)
    original = original_observation(current)
    rollback = EffectRollbackRecord(
        EffectRollbackRecordId(VALUE),
        current.effect_id,
        current.version,
        original.observation_id,
        EffectExternalOperationRef("restore-a"),
        "Independent restoration evidence.",
        frozenset({EvidenceRef("rollback")}),
        actor(ActorType.EVALUATOR, EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER, CURRENT_CONTROLLER),
        NOW,
        NOW,
        CORRELATION,
    )
    rollback_scope = EffectRemediationAuthorizationScope(
        current.effect_id,
        current.version,
        original.observation_id,
        EffectRemediationKind.ROLLBACK,
        CORRELATION,
        restoration_operation_ref=rollback.restoration_operation_ref,
    )
    rollback_semantics = EffectQuarantineRollbackSemantics(
        context,
        reconciliation_for(current, context, CURRENT_CONTROLLER),
        EffectRollbackSemantics(
            original,
            rollback,
            remediation_authorization(rollback_scope, CURRENT_CONTROLLER),
        ),
    )
    rollback_request = transition_request(
        current, EffectState.ROLLED_BACK, CURRENT_CONTROLLER, VALUE
    )
    rollback_result = transition_entity(
        current,
        rollback_request,
        transition_context(current, rollback_request, rollback_semantics),
    )
    assert rollback_result.entity.state is EffectState.ROLLED_BACK
    assert (
        "quarantine_context_id",
        str(context.context_id.value),
    ) in rollback_result.event.metadata.annotations
    assert (
        "reconciliation_id",
        str(OTHER),
    ) in rollback_result.event.metadata.annotations

    plan = replace(
        compensation_plan(current),
        observed_effect_version=current.version,
        recorded_by=actor(ActorType.EFFECT_CONTROLLER, CURRENT_CONTROLLER),
    )
    compensation_semantics = EffectQuarantineCompensationStartSemantics(
        context,
        reconciliation_for(current, context, CURRENT_CONTROLLER),
        EffectQuarantineCompensationMode.NEW_PLAN,
        EffectCompensationStartSemantics(
            original,
            plan,
            remediation_authorization(
                compensation_scope(current, plan, current.version), CURRENT_CONTROLLER
            ),
        ),
    )
    compensation_request = transition_request(
        current, EffectState.COMPENSATING, CURRENT_CONTROLLER, VALUE
    )
    compensation_result = transition_entity(
        current,
        compensation_request,
        transition_context(current, compensation_request, compensation_semantics),
    )
    assert compensation_result.entity.state is EffectState.COMPENSATING
    assert (
        "quarantine_context_id",
        str(context.context_id.value),
    ) in compensation_result.event.metadata.annotations
    assert (
        "reconciliation_id",
        str(OTHER),
    ) in compensation_result.event.metadata.annotations


def test_resume_exact_binds_s1_and_emits_s2_with_quarantine_provenance() -> None:
    current = quarantined()
    plan = compensation_plan(current)
    context = quarantine_compensation_context(current, plan)
    authorization = remediation_authorization(
        compensation_scope(current, plan, current.version), CURRENT_CONTROLLER
    )
    semantics = EffectQuarantineCompensationStartSemantics(
        context,
        reconciliation_for(current, context, CURRENT_CONTROLLER),
        EffectQuarantineCompensationMode.RESUME_EXISTING_PLAN,
        EffectCompensationStartSemantics(
            original_observation(current), plan, authorization
        ),
    )
    request = transition_request(
        current, EffectState.COMPENSATING, CURRENT_CONTROLLER, VALUE
    )
    historical_start = start_event(current, plan, authorization)
    result = transition_entity(
        current,
        request,
        transition_context(current, request, semantics, historical_start),
    )
    assert result.entity.state is EffectState.COMPENSATING
    assert (
        "compensation_start_event_id",
        str(VALUE),
    ) in result.event.metadata.annotations
    assert (
        "prior_compensation_start_event_id",
        str(OTHER),
    ) in result.event.metadata.annotations
    assert (
        "quarantine_context_id",
        str(context.context_id.value),
    ) in result.event.metadata.annotations
    assert ("reconciliation_id", str(OTHER)) in result.event.metadata.annotations
    for invalid_context in (
        replace(context, recorded_by=actor(ActorType.SYSTEM, CONTROLLER)),
        replace(context, reason=EffectQuarantineReason.POST_COMMIT_PROBLEM),
    ):
        invalid_semantics = replace(
            semantics,
            quarantine_context=invalid_context,
            reconciliation=replace(
                semantics.reconciliation,
                quarantine_context_id=invalid_context.context_id,
            ),
        )
        with pytest.raises(InvariantViolation, match="Quarantine exit"):
            transition_entity(
                current,
                request,
                transition_context(
                    current, request, invalid_semantics, historical_start
                ),
            )
    with pytest.raises(InvariantViolation, match="Compensation start event"):
        transition_entity(
            current,
            request,
            transition_context(
                current,
                request,
                semantics,
                replace(historical_start, entity_version=EntityVersion(15)),
            ),
        )


def test_direct_completion_binds_historical_authorization_to_s1() -> None:
    current = quarantined()
    plan = compensation_plan(current)
    context = quarantine_compensation_context(current, plan)
    historical_authorization = remediation_authorization(
        compensation_scope(current, plan, plan.observed_effect_version), CONTROLLER
    )
    completion = EffectCompensationCompletionRecord(
        EffectCompensationCompletionId(VALUE),
        plan.plan_id,
        current.effect_id,
        current.version,
        plan.original_commit_observation_id,
        "All linked Effects completed.",
        "The original occurrence remains historical.",
        frozenset({EvidenceRef("completion")}),
        actor(ActorType.EVALUATOR, EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER, CURRENT_CONTROLLER),
        NOW,
        NOW,
        CORRELATION,
    )
    semantics = EffectQuarantineCompensationCompletionSemantics(
        context,
        reconciliation_for(current, context, CURRENT_CONTROLLER),
        EffectCompensationCompletionSemantics(
            original_observation(current), plan, completion, historical_authorization
        ),
    )
    request = transition_request(
        current, EffectState.COMPENSATED, CURRENT_CONTROLLER, VALUE
    )
    result = transition_entity(
        current,
        request,
        transition_context(
            current,
            request,
            semantics,
            start_event(current, plan, historical_authorization),
        ),
    )
    assert result.entity.state is EffectState.COMPENSATED
    assert (
        "quarantine_context_id",
        str(context.context_id.value),
    ) in result.event.metadata.annotations
    assert ("reconciliation_id", str(OTHER)) in result.event.metadata.annotations
    with pytest.raises(
        InvariantViolation, match="historical compensation-start controller"
    ):
        transition_entity(
            current,
            request,
            transition_context(
                current,
                request,
                semantics,
                replace(
                    start_event(current, plan, historical_authorization),
                    actor=actor(ActorType.EFFECT_CONTROLLER, CURRENT_CONTROLLER),
                ),
            ),
        )
