"""M7C6B canonical observation and quarantine semantic transition guards."""

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
    Effect,
    EffectAuthorizationFindingId,
    EffectAuthorizationFindingRecord,
    EffectAuthorizationStatus,
    EffectCompensationPlanId,
    EffectCompensationPlanRecord,
    EffectConfirmedOccurrenceSemantics,
    EffectDeduplicationRef,
    EffectExternalOperationRef,
    EffectGovernanceFindingId,
    EffectGovernanceFindingRecord,
    EffectGovernancePolicyRef,
    EffectGovernanceStatus,
    EffectId,
    EffectObservationId,
    EffectObservationRecord,
    EffectObservationScope,
    EffectOccurrenceStatus,
    EffectPayloadRef,
    EffectQuarantineContext,
    EffectQuarantineContextId,
    EffectQuarantineReason,
    EffectQuarantineSemantics,
    EffectSemanticGuard,
    EffectState,
    EffectTargetRef,
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
    can_effect_transition,
    transition_entity,
)
from symphony_k.domain.transition_engine import LifecycleEntity, LifecycleState

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
PRODUCER = UUID("00000000-1234-4234-8234-123456789abc")
CONTROLLER = UUID("33333333-1234-4234-8234-123456789abc")
OBSERVER = UUID("44444444-1234-4234-8234-123456789abc")
VERSION = EntityVersion(17)
CORRELATION = CorrelationId(VALUE)
NOW = Timestamp(datetime(2026, 9, 12, tzinfo=UTC))
OPERATION = EffectExternalOperationRef("external-operation-a")
DEDUPLICATION = EffectDeduplicationRef("provider-deduplication-a")


def actor(actor_type: ActorType, value: UUID) -> ActorIdentity:
    return ActorIdentity(ActorId(value), actor_type)


def effect(state: EffectState) -> Effect:
    return Effect(
        EffectId(VALUE),
        state,
        VERSION,
        PlannedEffectOrigin(TaskId(VALUE), actor(ActorType.WORKER, PRODUCER)),
        EffectTargetRef("target-a"),
        EffectPayloadRef("payload-a"),
    )


def scope(current: Effect, target: EffectState) -> EffectObservationScope:
    return EffectObservationScope(
        current.effect_id,
        current.version,
        current.state,
        target,
        current.target_ref,
        OPERATION,
        DEDUPLICATION,
        CORRELATION,
    )


def observation(
    current: Effect,
    *,
    status: EffectOccurrenceStatus,
    version: EntityVersion | None = None,
    observation_id: EffectObservationId | None = None,
    occurrence_at: Timestamp | None = None,
    observed_by: ActorIdentity | None = None,
    prior: EffectObservationId | None = None,
    target_ref: EffectTargetRef | None = None,
    payload_ref: EffectPayloadRef | None = None,
) -> EffectObservationRecord:
    return EffectObservationRecord(
        observation_id or EffectObservationId(VALUE),
        current.effect_id,
        version or current.version,
        OPERATION,
        DEDUPLICATION,
        status,
        target_ref or current.target_ref,
        payload_ref if payload_ref is not None else current.payload_ref,
        frozenset({EvidenceRef("independent external receipt")}),
        observed_by or actor(ActorType.EVALUATOR, OBSERVER),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        occurrence_at,
        NOW,
        CORRELATION,
        prior,
    )


def authorization(
    current: Effect,
    status: EffectAuthorizationStatus = EffectAuthorizationStatus.UNKNOWN,
) -> EffectAuthorizationFindingRecord:
    return EffectAuthorizationFindingRecord(
        EffectAuthorizationFindingId(VALUE),
        current.effect_id,
        current.version,
        status,
        "Prior authorization is historically unknown.",
        frozenset({EvidenceRef("authorization audit")}),
        actor(ActorType.EVALUATOR, OBSERVER),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        NOW,
        CORRELATION,
    )


def governance(current: Effect) -> EffectGovernanceFindingRecord:
    return EffectGovernanceFindingRecord(
        EffectGovernanceFindingId(VALUE),
        current.effect_id,
        current.version,
        EffectGovernancePolicyRef("policy-a", "1"),
        EffectGovernanceStatus.NON_COMPLIANT,
        "The independently confirmed occurrence violates policy-a.",
        frozenset({EvidenceRef("governance audit")}),
        actor(ActorType.EVALUATOR, OBSERVER),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        NOW,
        CORRELATION,
    )


def quarantine_context(
    current: Effect,
    *,
    reason: EffectQuarantineReason,
    prior: EffectObservationId | None = None,
    original: EffectObservationId | None = None,
    plan: EffectCompensationPlanId | None = None,
    source_state: EffectState | None = None,
    version: EntityVersion | None = None,
) -> EffectQuarantineContext:
    historical_source = source_state or current.state
    historical_version = version or current.version
    if current.state is EffectState.QUARANTINED and source_state is None:
        historical_source = EffectState.PENDING_COMMIT
        historical_version = EntityVersion(current.version.value - 1)
    return EffectQuarantineContext(
        EffectQuarantineContextId(OTHER),
        EffectObservationScope(
            current.effect_id,
            historical_version,
            historical_source,
            EffectState.QUARANTINED,
            current.target_ref,
            OPERATION,
            DEDUPLICATION,
            CORRELATION,
        ),
        reason,
        "Evidence requires controlled reconciliation without automatic execution.",
        frozenset({EvidenceRef("quarantine evidence")}),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        prior,
        original,
        None,
        plan,
    )


def request(current: Effect, target: EffectState) -> TransitionRequest[EffectState]:
    return TransitionRequest(
        EventId(VALUE),
        target,
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        TransitionReason("Canonical Effect observation or quarantine transition"),
        current.version,
        NOW,
        CORRELATION,
    )


def context(
    current: Effect,
    transition_request: TransitionRequest[EffectState],
    semantics: EffectConfirmedOccurrenceSemantics | EffectQuarantineSemantics | None,
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
        effect_semantic_guard=guard,
    )


class PassingGuard:
    def validate(
        self,
        entity: LifecycleEntity,
        transition_request: TransitionRequest[LifecycleState],
    ) -> None:
        assert entity.version == transition_request.expected_version


def confirmed_semantics(
    current: Effect,
    status: EffectAuthorizationStatus = EffectAuthorizationStatus.UNKNOWN,
) -> EffectConfirmedOccurrenceSemantics:
    return EffectConfirmedOccurrenceSemantics(
        scope(current, EffectState.COMMITTED),
        observation(
            current,
            status=EffectOccurrenceStatus.CONFIRMED,
            occurrence_at=NOW,
        ),
        authorization(current, status),
        governance(current),
    )


@pytest.mark.parametrize(
    ("state", "authorization_status"),
    [
        (EffectState.PLANNED, EffectAuthorizationStatus.AUTHORIZED),
        (EffectState.SIMULATED, EffectAuthorizationStatus.UNAUTHORIZED),
        (EffectState.PENDING_COMMIT, EffectAuthorizationStatus.UNKNOWN),
    ],
)
def test_confirmed_occurrence_edges_are_observation_only(
    state: EffectState, authorization_status: EffectAuthorizationStatus
) -> None:
    current = effect(state)
    transition_request = request(current, EffectState.COMMITTED)
    result = transition_entity(
        current,
        transition_request,
        context(
            current,
            transition_request,
            confirmed_semantics(current, authorization_status),
        ),
    )
    assert result.entity.state is EffectState.COMMITTED
    assert result.entity.version == current.version.next()
    assert all(
        getattr(result.entity, field.name) == getattr(current, field.name)
        for field in fields(current)
        if field.name not in {"state", "version"}
    )


def test_quarantined_reconciliation_requires_confirmed_lineage() -> None:
    current = effect(EffectState.QUARANTINED)
    prior = observation(
        current,
        status=EffectOccurrenceStatus.UNCERTAIN,
        version=EntityVersion(16),
        observation_id=EffectObservationId(OTHER),
    )
    confirmed = observation(
        current,
        status=EffectOccurrenceStatus.CONFIRMED,
        occurrence_at=NOW,
        prior=prior.observation_id,
    )
    semantics = EffectConfirmedOccurrenceSemantics(
        scope(current, EffectState.COMMITTED),
        confirmed,
        authorization(current),
        quarantine_context=quarantine_context(
            current,
            reason=EffectQuarantineReason.UNKNOWN_OR_SUSPECTED_OCCURRENCE,
            prior=prior.observation_id,
        ),
        prior_observation=prior,
    )
    transition_request = request(current, EffectState.COMMITTED)
    assert (
        transition_entity(
            current, transition_request, context(current, transition_request, semantics)
        ).entity.state
        is EffectState.COMMITTED
    )


def test_reconciliation_preserves_truthful_unknown_observed_payload() -> None:
    current = Effect(
        EffectId(VALUE),
        EffectState.QUARANTINED,
        VERSION,
        ObservedEffectOrigin(
            OPERATION,
            frozenset({EvidenceRef("earlier independent receipt")}),
            actor(ActorType.EVALUATOR, OBSERVER),
            NOW,
            None,
            None,
            "Task attribution remains unknown.",
        ),
        EffectTargetRef("target-a"),
        None,
    )
    prior = observation(
        current,
        status=EffectOccurrenceStatus.UNCERTAIN,
        version=EntityVersion(16),
        observation_id=EffectObservationId(OTHER),
    )
    confirmed = observation(
        current,
        status=EffectOccurrenceStatus.CONFIRMED,
        occurrence_at=NOW,
        prior=prior.observation_id,
    )
    semantics = EffectConfirmedOccurrenceSemantics(
        scope(current, EffectState.COMMITTED),
        confirmed,
        authorization(current),
    )
    transition_request = request(current, EffectState.COMMITTED)
    result = transition_entity(
        current, transition_request, context(current, transition_request, semantics)
    )
    assert result.entity.payload_ref is None


@pytest.mark.parametrize(
    "prior_change",
    [
        lambda current, prior: replace(
            prior, target_ref=EffectTargetRef("other-target")
        ),
        lambda current, prior: replace(
            prior, payload_ref=EffectPayloadRef("other-payload")
        ),
        lambda current, prior: replace(
            prior, observed_effect_version=EntityVersion(18)
        ),
    ],
)
def test_reconciliation_rejects_incompatible_historical_prior_observation(
    prior_change: object,
) -> None:
    current = effect(EffectState.QUARANTINED)
    prior = observation(
        current,
        status=EffectOccurrenceStatus.UNCERTAIN,
        version=EntityVersion(16),
        observation_id=EffectObservationId(OTHER),
    )
    assert callable(prior_change)
    invalid_prior = prior_change(current, prior)
    confirmed = observation(
        current,
        status=EffectOccurrenceStatus.CONFIRMED,
        occurrence_at=NOW,
        prior=invalid_prior.observation_id,
    )
    semantics = EffectConfirmedOccurrenceSemantics(
        scope(current, EffectState.COMMITTED),
        confirmed,
        authorization(current),
        quarantine_context=quarantine_context(
            current,
            reason=EffectQuarantineReason.UNKNOWN_OR_SUSPECTED_OCCURRENCE,
            prior=invalid_prior.observation_id,
            version=invalid_prior.observed_effect_version,
        ),
        prior_observation=invalid_prior,
    )
    transition_request = request(current, EffectState.COMMITTED)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current, transition_request, context(current, transition_request, semantics)
        )


def test_reconciliation_rejects_fabricated_quarantined_self_scope() -> None:
    current = effect(EffectState.QUARANTINED)
    prior = observation(
        current,
        status=EffectOccurrenceStatus.UNCERTAIN,
        version=EntityVersion(16),
        observation_id=EffectObservationId(OTHER),
    )
    semantics = EffectConfirmedOccurrenceSemantics(
        scope(current, EffectState.COMMITTED),
        observation(
            current,
            status=EffectOccurrenceStatus.CONFIRMED,
            occurrence_at=NOW,
            prior=prior.observation_id,
        ),
        authorization(current),
        quarantine_context=quarantine_context(
            current,
            reason=EffectQuarantineReason.UNKNOWN_OR_SUSPECTED_OCCURRENCE,
            prior=prior.observation_id,
            source_state=EffectState.QUARANTINED,
            version=EntityVersion(16),
        ),
        prior_observation=prior,
    )
    transition_request = request(current, EffectState.COMMITTED)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current, transition_request, context(current, transition_request, semantics)
        )


@pytest.mark.parametrize(
    "state",
    [EffectState.PLANNED, EffectState.SIMULATED, EffectState.PENDING_COMMIT],
)
def test_pre_commit_quarantine_requires_uncertain_observation(
    state: EffectState,
) -> None:
    current = effect(state)
    uncertain = observation(current, status=EffectOccurrenceStatus.UNCERTAIN)
    semantics = EffectQuarantineSemantics(
        scope(current, EffectState.QUARANTINED),
        quarantine_context(
            current,
            reason=EffectQuarantineReason.UNKNOWN_OR_SUSPECTED_OCCURRENCE,
            prior=uncertain.observation_id,
        ),
        observation=uncertain,
    )
    transition_request = request(current, EffectState.QUARANTINED)
    assert (
        transition_entity(
            current, transition_request, context(current, transition_request, semantics)
        ).entity.state
        is EffectState.QUARANTINED
    )


def original_commit(current: Effect) -> EffectObservationRecord:
    return observation(
        current,
        status=EffectOccurrenceStatus.CONFIRMED,
        occurrence_at=NOW,
    )


def test_committed_quarantine_retains_known_occurrence() -> None:
    current = effect(EffectState.COMMITTED)
    original = original_commit(current)
    semantics = EffectQuarantineSemantics(
        scope(current, EffectState.QUARANTINED),
        quarantine_context(
            current,
            reason=EffectQuarantineReason.POST_COMMIT_PROBLEM,
            original=original.observation_id,
        ),
        original_commit_observation=original,
    )
    transition_request = request(current, EffectState.QUARANTINED)
    assert (
        transition_entity(
            current, transition_request, context(current, transition_request, semantics)
        ).entity.state
        is EffectState.QUARANTINED
    )


@pytest.mark.parametrize("state", [EffectState.COMMITTED, EffectState.COMPENSATING])
def test_post_commit_quarantine_rejects_incompatible_original_payload(
    state: EffectState,
) -> None:
    current = effect(state)
    original = replace(
        original_commit(current), payload_ref=EffectPayloadRef("other-payload")
    )
    plan = None
    if state is EffectState.COMPENSATING:
        plan = EffectCompensationPlanRecord(
            EffectCompensationPlanId(OTHER),
            current.effect_id,
            current.version,
            original.observation_id,
            frozenset({EffectId(OTHER)}),
            "A separate governed compensation remains incomplete and unsafe.",
            frozenset({EvidenceRef("compensation incident")}),
            actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
            actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
            NOW,
            NOW,
            CORRELATION,
        )
    semantics = EffectQuarantineSemantics(
        scope(current, EffectState.QUARANTINED),
        quarantine_context(
            current,
            reason=(
                EffectQuarantineReason.POST_COMMIT_PROBLEM
                if state is EffectState.COMMITTED
                else EffectQuarantineReason.COMPENSATION_OR_REMEDIATION_UNCERTAINTY
            ),
            original=original.observation_id,
            plan=plan.plan_id if plan is not None else None,
        ),
        original_commit_observation=original,
        compensation_plan=plan,
    )
    transition_request = request(current, EffectState.QUARANTINED)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current, transition_request, context(current, transition_request, semantics)
        )


def test_post_commit_quarantine_allows_earlier_original_observation_version() -> None:
    current = effect(EffectState.COMMITTED)
    original = replace(
        original_commit(current), observed_effect_version=EntityVersion(16)
    )
    semantics = EffectQuarantineSemantics(
        scope(current, EffectState.QUARANTINED),
        quarantine_context(
            current,
            reason=EffectQuarantineReason.POST_COMMIT_PROBLEM,
            original=original.observation_id,
        ),
        original_commit_observation=original,
    )
    transition_request = request(current, EffectState.QUARANTINED)
    assert (
        transition_entity(
            current, transition_request, context(current, transition_request, semantics)
        ).entity.state
        is EffectState.QUARANTINED
    )


def test_compensating_quarantine_requires_existing_plan_without_completion() -> None:
    current = effect(EffectState.COMPENSATING)
    original = original_commit(current)
    plan = EffectCompensationPlanRecord(
        EffectCompensationPlanId(OTHER),
        current.effect_id,
        current.version,
        original.observation_id,
        frozenset({EffectId(OTHER)}),
        "A separate governed compensation remains incomplete and unsafe.",
        frozenset({EvidenceRef("compensation incident")}),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        actor(ActorType.EFFECT_CONTROLLER, CONTROLLER),
        NOW,
        NOW,
        CORRELATION,
    )
    semantics = EffectQuarantineSemantics(
        scope(current, EffectState.QUARANTINED),
        quarantine_context(
            current,
            reason=EffectQuarantineReason.COMPENSATION_OR_REMEDIATION_UNCERTAINTY,
            original=original.observation_id,
            plan=plan.plan_id,
        ),
        original_commit_observation=original,
        compensation_plan=plan,
    )
    transition_request = request(current, EffectState.QUARANTINED)
    assert (
        transition_entity(
            current, transition_request, context(current, transition_request, semantics)
        ).entity.state
        is EffectState.QUARANTINED
    )


@pytest.mark.parametrize(
    "changes",
    [
        lambda current, semantics: replace(
            semantics,
            observation=replace(
                semantics.observation,
                occurrence_status=EffectOccurrenceStatus.UNCERTAIN,
            ),
        ),
        lambda current, semantics: replace(
            semantics, observation=replace(semantics.observation, occurrence_at=None)
        ),
        lambda current, semantics: replace(
            semantics,
            observation=replace(
                semantics.observation,
                observed_by=actor(ActorType.EVALUATOR, PRODUCER),
            ),
        ),
        lambda current, semantics: replace(
            semantics,
            observation=replace(
                semantics.observation,
                observed_by=actor(ActorType.WORKER, OBSERVER),
            ),
        ),
        lambda current, semantics: replace(
            semantics,
            authorization_finding=replace(
                semantics.authorization_finding,
                observed_effect_version=EntityVersion(16),
            ),
        ),
    ],
)
def test_confirmed_occurrence_rejects_missing_or_self_confirmed_facts(
    changes: object,
) -> None:
    current = effect(EffectState.PLANNED)
    transition_request = request(current, EffectState.COMMITTED)
    semantics = confirmed_semantics(current)
    assert callable(changes)
    invalid = changes(current, semantics)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current, transition_request, context(current, transition_request, invalid)
        )


def test_pre_commit_quarantine_rejects_confirmed_or_disproved_occurrence() -> None:
    current = effect(EffectState.PLANNED)
    transition_request = request(current, EffectState.QUARANTINED)
    for status in (EffectOccurrenceStatus.CONFIRMED, EffectOccurrenceStatus.DISPROVED):
        value = observation(
            current,
            status=status,
            occurrence_at=NOW if status is EffectOccurrenceStatus.CONFIRMED else None,
        )
        semantics = EffectQuarantineSemantics(
            scope(current, EffectState.QUARANTINED),
            quarantine_context(
                current,
                reason=EffectQuarantineReason.UNKNOWN_OR_SUSPECTED_OCCURRENCE,
                prior=value.observation_id,
            ),
            observation=value,
        )
        with pytest.raises(InvariantViolation):
            transition_entity(
                current,
                transition_request,
                context(current, transition_request, semantics),
            )


def test_exact_fifteen_edges_are_canonical_and_four_remain_denied() -> None:
    canonical = {
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
    structural = {
        (source, target)
        for source in EffectState
        for target in EffectState
        if can_effect_transition(source, target)
    }
    assert len(structural) == 19
    assert len(canonical) == 15
    assert structural - canonical == {
        (EffectState.QUARANTINED, EffectState.PENDING_COMMIT),
        (EffectState.QUARANTINED, EffectState.ROLLED_BACK),
        (EffectState.QUARANTINED, EffectState.COMPENSATING),
        (EffectState.QUARANTINED, EffectState.COMPENSATED),
    }
    for source, target in structural - canonical:
        current = effect(source)
        transition_request = request(current, target)
        with pytest.raises(InvariantViolation, match="denies this unimplemented edge"):
            transition_entity(
                current, transition_request, context(current, transition_request, None)
            )
