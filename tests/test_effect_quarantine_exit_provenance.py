"""Public-transition regressions for Issue #60 and its #59 quarantine exits."""

from dataclasses import dataclass, replace
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
    EffectCompensationResumeProvenance,
    EffectCompensationStartSemantics,
    EffectDeduplicationRef,
    EffectId,
    EffectObservationId,
    EffectObservationRecord,
    EffectObservationScope,
    EffectOccurrenceStatus,
    EffectOperationScope,
    EffectPayloadRef,
    EffectPendingCommitSemantics,
    EffectPreparationRecord,
    EffectPreparationRecordId,
    EffectQuarantineCompensationCompletionSemantics,
    EffectQuarantineCompensationMode,
    EffectQuarantineCompensationStartSemantics,
    EffectQuarantineContext,
    EffectQuarantineContextId,
    EffectQuarantinePendingCommitSemantics,
    EffectQuarantineReason,
    EffectQuarantineRollbackSemantics,
    EffectQuarantineSemantics,
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
    EffectRemediationReadinessId,
    EffectRemediationReadinessRecord,
    EffectRemediationReadinessStatus,
    EffectRollbackRecord,
    EffectRollbackRecordId,
    EffectRollbackSemantics,
    EffectSemanticGuard,
    EffectSimulationBypassBasis,
    EffectSimulationBypassDecision,
    EffectSimulationBypassDecisionId,
    EffectSimulationBypassStatus,
    EffectState,
    EffectTargetRef,
    EffectVerificationRecord,
    EffectVerificationRecordId,
    EntityVersion,
    EventId,
    EvidenceRef,
    InvariantViolation,
    ObservedEffectOrigin,
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
ATTACK = UUID("99999999-4321-4321-8321-cba987654321")


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
    prior_start_event: DomainEvent | None = None,
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
        effect_prior_compensation_start_event=prior_start_event,
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


@dataclass(frozen=True)
class ResumeCompletionFixture:
    plan: EffectCompensationPlanRecord
    original: EffectObservationRecord
    prior_authorization: EffectRemediationAuthorizationSemantics
    s1: DomainEvent
    quarantine_context: EffectQuarantineContext
    reconciliation: EffectReconciliationRecord
    resume_authorization: EffectRemediationAuthorizationSemantics
    quarantined: Effect
    resume: EffectQuarantineCompensationStartSemantics
    resume_request: TransitionRequest[EffectState]
    compensating: Effect
    s2: DomainEvent
    completion: EffectCompensationCompletionSemantics
    request: TransitionRequest[EffectState]


def resume_completion_fixture() -> ResumeCompletionFixture:
    committed = Effect(
        EffectId(VALUE),
        EffectState.COMMITTED,
        EntityVersion(15),
        PlannedEffectOrigin(TaskId(VALUE), actor(ActorType.WORKER, PRODUCER)),
        EffectTargetRef("target-a"),
        EffectPayloadRef("payload-a"),
    )
    original = original_observation(committed)
    plan = compensation_plan(committed)
    prior_authorization = remediation_authorization(
        compensation_scope(committed, plan, committed.version), CONTROLLER
    )
    s1_request = transition_request(
        committed, EffectState.COMPENSATING, CONTROLLER, OTHER
    )
    s1_result = transition_entity(
        committed,
        s1_request,
        transition_context(
            committed,
            s1_request,
            EffectCompensationStartSemantics(original, plan, prior_authorization),
        ),
    )

    quarantine_scope = EffectObservationScope(
        s1_result.entity.effect_id,
        s1_result.entity.version,
        EffectState.COMPENSATING,
        EffectState.QUARANTINED,
        s1_result.entity.target_ref,
        EffectExternalOperationRef("operation-a"),
        EffectDeduplicationRef("dedupe-a"),
        CORRELATION,
    )
    quarantine_context = EffectQuarantineContext(
        EffectQuarantineContextId(VALUE),
        quarantine_scope,
        EffectQuarantineReason.COMPENSATION_OR_REMEDIATION_UNCERTAINTY,
        "Controlled remediation reconciliation.",
        frozenset({EvidenceRef("quarantine")}),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        original_commit_observation_id=original.observation_id,
        compensation_plan_id=plan.plan_id,
    )
    quarantine_request = transition_request(
        s1_result.entity, EffectState.QUARANTINED, CONTROLLER, ATTACK
    )
    quarantine_result = transition_entity(
        s1_result.entity,
        quarantine_request,
        transition_context(
            s1_result.entity,
            quarantine_request,
            EffectQuarantineSemantics(
                quarantine_scope,
                quarantine_context,
                original_commit_observation=original,
                compensation_plan=plan,
            ),
        ),
    )

    reconciliation = reconciliation_for(
        quarantine_result.entity, quarantine_context, CURRENT_CONTROLLER
    )
    resume_authorization = remediation_authorization(
        compensation_scope(
            quarantine_result.entity,
            plan,
            quarantine_result.entity.version,
        ),
        CURRENT_CONTROLLER,
    )
    resume_semantics = EffectQuarantineCompensationStartSemantics(
        quarantine_context,
        reconciliation,
        EffectQuarantineCompensationMode.RESUME_EXISTING_PLAN,
        EffectCompensationStartSemantics(original, plan, resume_authorization),
    )
    s2_request = transition_request(
        quarantine_result.entity,
        EffectState.COMPENSATING,
        CURRENT_CONTROLLER,
        VALUE,
    )
    s2_result = transition_entity(
        quarantine_result.entity,
        s2_request,
        transition_context(
            quarantine_result.entity,
            s2_request,
            resume_semantics,
            s1_result.event,
        ),
    )

    completion_record = EffectCompensationCompletionRecord(
        EffectCompensationCompletionId(VALUE),
        plan.plan_id,
        s2_result.entity.effect_id,
        s2_result.entity.version,
        original.observation_id,
        "All linked Effects completed.",
        "The original occurrence remains historical.",
        frozenset({EvidenceRef("completion")}),
        actor(ActorType.EVALUATOR, EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER, CURRENT_CONTROLLER),
        NOW,
        NOW,
        CORRELATION,
    )
    completion = EffectCompensationCompletionSemantics(
        original,
        plan,
        completion_record,
        resume_authorization,
        EffectCompensationResumeProvenance(
            s1_result.event.event_id,
            prior_authorization,
            quarantine_context.context_id,
            reconciliation.reconciliation_id,
        ),
    )
    completion_request = transition_request(
        s2_result.entity, EffectState.COMPENSATED, CURRENT_CONTROLLER, ATTACK
    )
    return ResumeCompletionFixture(
        plan,
        original,
        prior_authorization,
        s1_result.event,
        quarantine_context,
        reconciliation,
        resume_authorization,
        quarantine_result.entity,
        resume_semantics,
        s2_request,
        s2_result.entity,
        s2_result.event,
        completion,
        completion_request,
    )


def complete_resume(
    fixture: ResumeCompletionFixture,
    *,
    completion: EffectCompensationCompletionSemantics | None = None,
    s1: DomainEvent | None = None,
    s2: DomainEvent | None = None,
) -> Effect:
    selected_completion = completion or fixture.completion
    return transition_entity(
        fixture.compensating,
        fixture.request,
        transition_context(
            fixture.compensating,
            fixture.request,
            selected_completion,
            s2 or fixture.s2,
            s1 or fixture.s1,
        ),
    ).entity


def test_full_resume_sequence_completes_and_consumes_s2() -> None:
    fixture = resume_completion_fixture()
    result = transition_entity(
        fixture.compensating,
        fixture.request,
        transition_context(
            fixture.compensating,
            fixture.request,
            fixture.completion,
            fixture.s2,
            fixture.s1,
        ),
    )
    assert result.entity.state is EffectState.COMPENSATED
    assert (
        "compensation_start_event_id",
        str(fixture.s2.event_id.value),
    ) in result.event.metadata.annotations
    assert (
        "prior_compensation_start_event_id",
        str(fixture.s1.event_id.value),
    ) in result.event.metadata.annotations
    assert (
        "quarantine_context_id",
        str(fixture.quarantine_context.context_id.value),
    ) in result.event.metadata.annotations
    assert (
        "reconciliation_id",
        str(fixture.reconciliation.reconciliation_id.value),
    ) in result.event.metadata.annotations


@pytest.mark.parametrize(
    "attack",
    [
        "s1",
        "s1-version",
        "s2",
        "s2-missing-quarantine",
        "s2-missing-reconciliation",
        "s2-extra-annotation",
        "quarantine",
        "reconciliation",
        "plan",
        "linked",
        "authorization",
        "prior-authorization",
    ],
)
def test_resume_completion_rejects_every_lineage_substitution(attack: str) -> None:
    fixture = resume_completion_fixture()
    completion = fixture.completion
    s1 = fixture.s1
    s2 = fixture.s2
    resume = completion.resume_provenance
    assert resume is not None
    if attack == "s1":
        s1 = replace(s1, event_id=EventId(ATTACK))
    elif attack == "s1-version":
        s1 = replace(s1, entity_version=EntityVersion(s1.entity_version.value - 1))
    elif attack == "s2":
        s2 = replace(s2, event_id=EventId(ATTACK))
    elif attack in {"s2-missing-quarantine", "s2-missing-reconciliation"}:
        removed_key = (
            "quarantine_context_id"
            if attack == "s2-missing-quarantine"
            else "reconciliation_id"
        )
        s2 = replace(
            s2,
            metadata=replace(
                s2.metadata,
                annotations=frozenset(
                    annotation
                    for annotation in s2.metadata.annotations
                    if annotation[0] != removed_key
                ),
            ),
        )
    elif attack == "s2-extra-annotation":
        s2 = replace(
            s2,
            metadata=replace(
                s2.metadata,
                annotations=s2.metadata.annotations
                | frozenset({("unrestricted_subset", "forbidden")}),
            ),
        )
    elif attack == "quarantine":
        completion = replace(
            completion,
            resume_provenance=replace(
                resume, quarantine_context_id=EffectQuarantineContextId(OTHER)
            ),
        )
    elif attack == "reconciliation":
        completion = replace(
            completion,
            resume_provenance=replace(
                resume, reconciliation_id=EffectReconciliationRecordId(VALUE)
            ),
        )
    elif attack == "plan":
        completion = replace(
            completion,
            compensation_plan=replace(
                completion.compensation_plan,
                plan_id=EffectCompensationPlanId(OTHER),
            ),
        )
    elif attack == "linked":
        completion = replace(
            completion,
            compensation_plan=replace(
                completion.compensation_plan,
                compensating_effect_ids=frozenset({EffectId(ATTACK)}),
            ),
        )
    elif attack == "authorization":
        changed_policy = replace(
            completion.authorization.policy_decision,
            decision_ref=EffectRemediationAuthorizationRef("substituted-resume"),
        )
        changed_human = completion.authorization.human_authorization
        assert changed_human is not None
        completion = replace(
            completion,
            authorization=EffectRemediationAuthorizationSemantics(
                changed_policy,
                replace(
                    changed_human,
                    policy_decision_ref=changed_policy.decision_ref,
                ),
            ),
        )
    else:
        prior = resume.prior_authorization
        changed_policy = replace(
            prior.policy_decision,
            decision_ref=EffectRemediationAuthorizationRef("substituted-prior"),
        )
        changed_human = prior.human_authorization
        assert changed_human is not None
        completion = replace(
            completion,
            resume_provenance=replace(
                resume,
                prior_authorization=EffectRemediationAuthorizationSemantics(
                    changed_policy,
                    replace(
                        changed_human,
                        policy_decision_ref=changed_policy.decision_ref,
                    ),
                ),
            ),
        )
    with pytest.raises(InvariantViolation):
        complete_resume(fixture, completion=completion, s1=s1, s2=s2)


def test_resume_completion_requires_typed_quarantine_provenance() -> None:
    fixture = resume_completion_fixture()
    with pytest.raises(InvariantViolation):
        complete_resume(
            fixture, completion=replace(fixture.completion, resume_provenance=None)
        )


def pending_exit_semantics(
    current: Effect,
) -> EffectQuarantinePendingCommitSemantics:
    assert current.payload_ref is not None
    operation_scope = EffectOperationScope(
        current.effect_id,
        current.version,
        current.target_ref,
        current.payload_ref,
        CORRELATION,
    )
    preparation = EffectPreparationRecord(
        EffectPreparationRecordId(VALUE),
        current.effect_id,
        current.version,
        "Prepared exact intended operation.",
        actor(ActorType.WORKER, PLANNER),
        actor(ActorType.SCHEDULER, OTHER),
        NOW,
        NOW,
        CORRELATION,
    )
    verification = EffectVerificationRecord(
        EffectVerificationRecordId(VALUE),
        preparation.preparation_id,
        current.effect_id,
        current.version,
        "Independent verification passed.",
        frozenset({EvidenceRef("verification")}),
        actor(ActorType.EVALUATOR, EVALUATOR),
        actor(ActorType.SCHEDULER, OTHER),
        NOW,
        NOW,
        CORRELATION,
    )
    readiness = EffectRemediationReadinessRecord(
        EffectRemediationReadinessId(VALUE),
        operation_scope,
        EffectRemediationReadinessStatus.COMPENSATION_PREPARED,
        "Compensation is prepared.",
        frozenset({EvidenceRef("readiness")}),
        actor(ActorType.SCHEDULER, OTHER),
        actor(ActorType.SCHEDULER, OTHER),
        NOW,
        NOW,
    )
    bypass = EffectSimulationBypassDecision(
        EffectSimulationBypassDecisionId(VALUE),
        operation_scope,
        EffectSimulationBypassStatus.ACCEPTED,
        EffectSimulationBypassBasis.IMPRACTICAL,
        "Representative simulation is impractical.",
        frozenset({EvidenceRef("bypass")}),
        actor(ActorType.HUMAN_OPERATOR, HUMAN),
        actor(ActorType.SCHEDULER, OTHER),
        NOW,
        NOW,
    )
    uncertain = EffectObservationRecord(
        EffectObservationId(VALUE),
        current.effect_id,
        EntityVersion(current.version.value - 1),
        EffectExternalOperationRef("operation-a"),
        EffectDeduplicationRef("dedupe-a"),
        EffectOccurrenceStatus.UNCERTAIN,
        current.target_ref,
        current.payload_ref,
        frozenset({EvidenceRef("uncertain")}),
        actor(ActorType.EVALUATOR, EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        None,
        NOW,
        CORRELATION,
    )
    disproved = replace(
        uncertain,
        observation_id=EffectObservationId(OTHER),
        observed_effect_version=current.version,
        occurrence_status=EffectOccurrenceStatus.DISPROVED,
        prior_observation_id=uncertain.observation_id,
    )
    entry_scope = EffectObservationScope(
        current.effect_id,
        EntityVersion(current.version.value - 1),
        EffectState.PENDING_COMMIT,
        EffectState.QUARANTINED,
        current.target_ref,
        EffectExternalOperationRef("operation-a"),
        EffectDeduplicationRef("dedupe-a"),
        CORRELATION,
    )
    context = EffectQuarantineContext(
        EffectQuarantineContextId(VALUE),
        entry_scope,
        EffectQuarantineReason.UNKNOWN_OR_SUSPECTED_OCCURRENCE,
        "Uncertain occurrence was quarantined.",
        frozenset({EvidenceRef("quarantine")}),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        prior_observation_id=uncertain.observation_id,
    )
    pending = EffectPendingCommitSemantics(
        operation_scope,
        preparation,
        verification,
        readiness,
        EffectDeduplicationRef("idempotency-key-v1"),
        simulation_bypass=bypass,
    )
    return EffectQuarantinePendingCommitSemantics(
        context,
        uncertain,
        disproved,
        EffectReconciliationRecord(
            EffectReconciliationRecordId(OTHER),
            current.effect_id,
            current.version,
            context.context_id,
            EffectReconciliationConclusion.NO_IN_FLIGHT_OR_DUPLICATE,
            "No in-flight or duplicate operation remains.",
            frozenset({EvidenceRef("reconciliation")}),
            actor(ActorType.EVALUATOR, EVALUATOR),
            actor(ActorType.EFFECT_CONTROLLER, CURRENT_CONTROLLER),
            NOW,
            NOW,
            CORRELATION,
        ),
        pending,
    )


def test_pending_commit_reentry_exact_binds_disproof_and_annotations() -> None:
    current = quarantined()
    semantics = pending_exit_semantics(current)
    request = transition_request(
        current, EffectState.PENDING_COMMIT, CURRENT_CONTROLLER, ATTACK
    )
    result = transition_entity(
        current, request, transition_context(current, request, semantics)
    )
    assert result.entity.state is EffectState.PENDING_COMMIT
    assert result.event.metadata.annotations == frozenset(
        {
            (
                "quarantine_context_id",
                str(semantics.quarantine_context.context_id.value),
            ),
            (
                "reconciliation_id",
                str(semantics.reconciliation.reconciliation_id.value),
            ),
        }
    )


@pytest.mark.parametrize(
    "attack",
    [
        "missing-predecessor",
        "wrong-predecessor",
        "stale-preparation",
        "stale-verification",
        "context-recorder",
        "reason-source",
    ],
)
def test_pending_commit_reentry_rejects_history_and_preparation_attacks(
    attack: str,
) -> None:
    current = quarantined()
    semantics = pending_exit_semantics(current)
    if attack == "missing-predecessor":
        semantics = replace(
            semantics,
            disproved_observation=replace(
                semantics.disproved_observation, prior_observation_id=None
            ),
        )
    elif attack == "wrong-predecessor":
        semantics = replace(
            semantics,
            disproved_observation=replace(
                semantics.disproved_observation,
                prior_observation_id=EffectObservationId(ATTACK),
            ),
        )
    elif attack == "stale-preparation":
        stale = replace(
            semantics.pending_commit.preparation,
            observed_effect_version=EntityVersion(current.version.value - 1),
        )
        semantics = replace(
            semantics,
            pending_commit=replace(
                semantics.pending_commit,
                preparation=stale,
                verification=replace(
                    semantics.pending_commit.verification,
                    preparation_id=stale.preparation_id,
                ),
            ),
        )
    elif attack == "stale-verification":
        semantics = replace(
            semantics,
            pending_commit=replace(
                semantics.pending_commit,
                verification=replace(
                    semantics.pending_commit.verification,
                    observed_effect_version=EntityVersion(current.version.value - 1),
                ),
            ),
        )
    elif attack == "context-recorder":
        semantics = replace(
            semantics,
            quarantine_context=replace(
                semantics.quarantine_context,
                recorded_by=actor(ActorType.SYSTEM, CONTROLLER),
            ),
        )
    else:
        semantics = replace(
            semantics,
            quarantine_context=replace(
                semantics.quarantine_context,
                reason=EffectQuarantineReason.POST_COMMIT_PROBLEM,
            ),
        )
    request = transition_request(
        current, EffectState.PENDING_COMMIT, CURRENT_CONTROLLER, ATTACK
    )
    with pytest.raises(InvariantViolation):
        transition_entity(
            current, request, transition_context(current, request, semantics)
        )


def test_pending_commit_reentry_rejects_observed_origin() -> None:
    planned = quarantined()
    current = replace(
        planned,
        origin=ObservedEffectOrigin(
            EffectExternalOperationRef("operation-a"),
            frozenset({EvidenceRef("observation")}),
            actor(ActorType.EVALUATOR, EVALUATOR),
            NOW,
            unlinked_reason="Attribution is not yet known.",
        ),
    )
    semantics = pending_exit_semantics(current)
    request = transition_request(
        current, EffectState.PENDING_COMMIT, CURRENT_CONTROLLER, ATTACK
    )
    with pytest.raises(InvariantViolation, match="Observed origin"):
        transition_entity(
            current, request, transition_context(current, request, semantics)
        )


def rollback_exit_semantics(current: Effect) -> EffectQuarantineRollbackSemantics:
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
    scope = EffectRemediationAuthorizationScope(
        current.effect_id,
        current.version,
        original.observation_id,
        EffectRemediationKind.ROLLBACK,
        CORRELATION,
        restoration_operation_ref=rollback.restoration_operation_ref,
    )
    return EffectQuarantineRollbackSemantics(
        context,
        reconciliation_for(current, context, CURRENT_CONTROLLER),
        EffectRollbackSemantics(
            original,
            rollback,
            remediation_authorization(scope, CURRENT_CONTROLLER),
        ),
    )


@pytest.mark.parametrize(
    "attack",
    ["context-original", "rollback-evidence", "authorization", "recorder", "reason"],
)
def test_rollback_exit_rejects_provenance_substitutions(attack: str) -> None:
    current = quarantined()
    semantics = rollback_exit_semantics(current)
    if attack == "context-original":
        semantics = replace(
            semantics,
            quarantine_context=replace(
                semantics.quarantine_context,
                original_commit_observation_id=EffectObservationId(VALUE),
            ),
        )
    elif attack == "rollback-evidence":
        semantics = replace(
            semantics,
            rollback=replace(
                semantics.rollback,
                rollback_record=replace(
                    semantics.rollback.rollback_record,
                    observed_effect_version=EntityVersion(current.version.value - 1),
                ),
            ),
        )
    elif attack == "authorization":
        policy = semantics.rollback.authorization.policy_decision
        wrong_scope = replace(
            policy.scope,
            restoration_operation_ref=EffectExternalOperationRef("restore-b"),
        )
        human = semantics.rollback.authorization.human_authorization
        assert human is not None
        semantics = replace(
            semantics,
            rollback=replace(
                semantics.rollback,
                authorization=EffectRemediationAuthorizationSemantics(
                    replace(policy, scope=wrong_scope),
                    replace(human, scope=wrong_scope),
                ),
            ),
        )
    elif attack == "recorder":
        semantics = replace(
            semantics,
            quarantine_context=replace(
                semantics.quarantine_context,
                recorded_by=actor(ActorType.SYSTEM, CONTROLLER),
            ),
        )
    else:
        semantics = replace(
            semantics,
            quarantine_context=replace(
                semantics.quarantine_context,
                reason=(EffectQuarantineReason.COMPENSATION_OR_REMEDIATION_UNCERTAINTY),
            ),
        )
    request = transition_request(
        current, EffectState.ROLLED_BACK, CURRENT_CONTROLLER, ATTACK
    )
    with pytest.raises(InvariantViolation):
        transition_entity(
            current, request, transition_context(current, request, semantics)
        )


@pytest.mark.parametrize(
    "attack",
    [
        "missing-human",
        "wrong-recorder",
        "wrong-version",
        "plan",
        "linked",
        "s1-id",
        "s1-version",
        "s1-quarantine-annotation",
        "s1-reconciliation-annotation",
    ],
)
def test_compensation_resume_rejects_authorization_and_lineage_attacks(
    attack: str,
) -> None:
    fixture = resume_completion_fixture()
    semantics = fixture.resume
    s1 = fixture.s1
    authorization = semantics.compensation.authorization
    plan = semantics.compensation.compensation_plan
    if attack == "missing-human":
        authorization = replace(authorization, human_authorization=None)
    elif attack == "wrong-recorder":
        authorization = EffectRemediationAuthorizationSemantics(
            replace(
                authorization.policy_decision,
                recorded_by=actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
            ),
            replace(
                authorization.human_authorization,
                recorded_by=actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
            )
            if authorization.human_authorization is not None
            else None,
        )
    elif attack == "wrong-version":
        wrong_scope = replace(
            authorization.policy_decision.scope,
            authorized_effect_version=EntityVersion(
                fixture.quarantined.version.value - 1
            ),
        )
        human = authorization.human_authorization
        assert human is not None
        authorization = EffectRemediationAuthorizationSemantics(
            replace(authorization.policy_decision, scope=wrong_scope),
            replace(human, scope=wrong_scope),
        )
    elif attack == "plan":
        plan = replace(plan, plan_id=EffectCompensationPlanId(OTHER))
    elif attack == "linked":
        plan = replace(plan, compensating_effect_ids=frozenset({EffectId(ATTACK)}))
    elif attack == "s1-id":
        s1 = replace(s1, event_id=EventId(ATTACK))
    elif attack == "s1-version":
        s1 = replace(s1, entity_version=EntityVersion(s1.entity_version.value - 1))
    else:
        key = (
            "quarantine_context_id"
            if attack == "s1-quarantine-annotation"
            else "reconciliation_id"
        )
        s1 = replace(
            s1,
            metadata=replace(
                s1.metadata,
                annotations=s1.metadata.annotations | frozenset({(key, str(ATTACK))}),
            ),
        )
    semantics = replace(
        semantics,
        compensation=replace(
            semantics.compensation,
            compensation_plan=plan,
            authorization=authorization,
        ),
    )
    with pytest.raises(InvariantViolation):
        transition_entity(
            fixture.quarantined,
            fixture.resume_request,
            transition_context(
                fixture.quarantined,
                fixture.resume_request,
                semantics,
                s1,
            ),
        )


@dataclass(frozen=True)
class DirectCompletionFixture:
    current: Effect
    semantics: EffectQuarantineCompensationCompletionSemantics
    request: TransitionRequest[EffectState]
    start: DomainEvent


def direct_completion_fixture() -> DirectCompletionFixture:
    current = quarantined()
    plan = compensation_plan(current)
    context = quarantine_compensation_context(current, plan)
    authorization = remediation_authorization(
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
            original_observation(current), plan, completion, authorization
        ),
    )
    return DirectCompletionFixture(
        current,
        semantics,
        transition_request(
            current, EffectState.COMPENSATED, CURRENT_CONTROLLER, ATTACK
        ),
        start_event(current, plan, authorization),
    )


@pytest.mark.parametrize(
    "attack",
    [
        "context-original",
        "historical-authorization",
        "historical-start",
        "plan",
        "linked",
        "verifier-historical-controller",
        "verifier-current-controller",
    ],
)
def test_direct_completion_rejects_original_commit_and_principal_attacks(
    attack: str,
) -> None:
    fixture = direct_completion_fixture()
    semantics = fixture.semantics
    start = fixture.start
    completion = semantics.completion
    if attack == "context-original":
        semantics = replace(
            semantics,
            quarantine_context=replace(
                semantics.quarantine_context,
                original_commit_observation_id=EffectObservationId(VALUE),
            ),
        )
    elif attack == "historical-authorization":
        authorization = completion.authorization
        semantics = replace(
            semantics,
            completion=replace(
                completion,
                authorization=EffectRemediationAuthorizationSemantics(
                    replace(
                        authorization.policy_decision,
                        recorded_by=actor(
                            ActorType.EFFECT_CONTROLLER, CURRENT_CONTROLLER
                        ),
                    ),
                    replace(
                        authorization.human_authorization,
                        recorded_by=actor(
                            ActorType.EFFECT_CONTROLLER, CURRENT_CONTROLLER
                        ),
                    )
                    if authorization.human_authorization is not None
                    else None,
                ),
            ),
        )
    elif attack == "historical-start":
        start = replace(start, event_id=EventId(ATTACK))
    elif attack in {"plan", "linked"}:
        plan = completion.compensation_plan
        plan = (
            replace(plan, plan_id=EffectCompensationPlanId(OTHER))
            if attack == "plan"
            else replace(plan, compensating_effect_ids=frozenset({EffectId(ATTACK)}))
        )
        semantics = replace(
            semantics,
            completion=replace(completion, compensation_plan=plan),
        )
    else:
        principal = (
            CONTROLLER
            if attack.endswith("historical-controller")
            else CURRENT_CONTROLLER
        )
        semantics = replace(
            semantics,
            completion=replace(
                completion,
                completion_record=replace(
                    completion.completion_record,
                    verified_by=actor(ActorType.EVALUATOR, principal),
                ),
            ),
        )
    with pytest.raises(InvariantViolation):
        transition_entity(
            fixture.current,
            fixture.request,
            transition_context(fixture.current, fixture.request, semantics, start),
        )
