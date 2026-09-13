"""Direct deterministic regression tests for Issue #58 quarantine exits."""

from dataclasses import replace
from datetime import UTC, datetime
from typing import cast
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CorrelationId,
    Effect,
    EffectDeduplicationRef,
    EffectId,
    EffectObservationScope,
    EffectPayloadRef,
    EffectQuarantineContext,
    EffectQuarantineContextId,
    EffectQuarantineReason,
    EffectReconciliationConclusion,
    EffectReconciliationRecord,
    EffectReconciliationRecordId,
    EffectSemanticGuard,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    EvidenceRef,
    InvariantViolation,
    PlannedEffectOrigin,
    TaskId,
    Timestamp,
)
from symphony_k.domain.effect import EffectExternalOperationRef

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
PRODUCER = UUID("00000000-1234-4234-8234-123456789abc")
CONTROLLER = UUID("33333333-1234-4234-8234-123456789abc")
EVALUATOR = UUID("22222222-1234-4234-8234-123456789abc")
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


def entry(effect: Effect, source: EffectState) -> EffectQuarantineContext:
    return EffectQuarantineContext(
        EffectQuarantineContextId(VALUE),
        EffectObservationScope(
            effect.effect_id,
            EntityVersion(16),
            source,
            EffectState.QUARANTINED,
            effect.target_ref,
            EffectExternalOperationRef("operation-a"),
            EffectDeduplicationRef("dedupe-a"),
            CORRELATION,
        ),
        EffectQuarantineReason.COMPENSATION_OR_REMEDIATION_UNCERTAINTY,
        "Independent evidence requires controlled reconciliation.",
        frozenset({EvidenceRef("entry evidence")}),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
    )


def reconciliation(
    effect: Effect, context: EffectQuarantineContext
) -> EffectReconciliationRecord:
    return EffectReconciliationRecord(
        EffectReconciliationRecordId(VALUE),
        effect.effect_id,
        effect.version,
        context.context_id,
        EffectReconciliationConclusion.REMEDIAL_UNCERTAINTY_RECONCILED,
        "Independent evaluator reconciled the recorded uncertainty.",
        frozenset({EvidenceRef("reconciliation evidence")}),
        actor(ActorType.EVALUATOR, EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        NOW,
        CORRELATION,
    )


@pytest.mark.parametrize(
    ("exit_name", "source"),
    [
        ("pending-commit", EffectState.PENDING_COMMIT),
        ("rollback", EffectState.COMMITTED),
        ("compensation-start", EffectState.COMMITTED),
        ("compensation-completion", EffectState.COMPENSATING),
    ],
)
def test_each_quarantine_exit_exact_binds_its_immediate_legal_entry(
    exit_name: str, source: EffectState
) -> None:
    current = quarantined()
    context = entry(current, source)
    EffectSemanticGuard._validate_quarantine_exit(
        cast(EffectSemanticGuard, None),
        current,
        context,
        reconciliation(current, context),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        CORRELATION,
    )


@pytest.mark.parametrize(
    "context_change",
    [
        lambda context: replace(
            context,
            observation_scope=replace(
                context.observation_scope, observed_effect_version=EntityVersion(15)
            ),
        ),
        lambda context: replace(
            context,
            observation_scope=replace(
                context.observation_scope, source_state=EffectState.QUARANTINED
            ),
        ),
    ],
)
def test_exit_rejects_non_immediate_or_non_incoming_quarantine_entry(
    context_change: object,
) -> None:
    current = quarantined()
    assert callable(context_change)
    invalid = context_change(entry(current, EffectState.PENDING_COMMIT))
    with pytest.raises(InvariantViolation, match="Quarantine exit"):
        EffectSemanticGuard._validate_quarantine_exit(
            cast(EffectSemanticGuard, None),
            current,
            invalid,
            reconciliation(current, invalid),
            actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
            CORRELATION,
        )


def test_exit_rejects_producer_actor_id_relabelled_as_evaluator() -> None:
    current = quarantined()
    context = entry(current, EffectState.PENDING_COMMIT)
    invalid = replace(
        reconciliation(current, context),
        reconciled_by=actor(ActorType.EVALUATOR, PRODUCER),
    )
    with pytest.raises(InvariantViolation, match="Quarantine exit"):
        EffectSemanticGuard._validate_quarantine_exit(
            cast(EffectSemanticGuard, None),
            current,
            context,
            invalid,
            actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
            CORRELATION,
        )
