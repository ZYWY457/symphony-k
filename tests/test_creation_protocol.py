"""M7D1 shared creation protocol: exact binding and deliberate default denial."""

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CausationId,
    CompletionPolicyRef,
    CorrelationId,
    CreationAuthorityDecision,
    CreationAuthorityDecisionId,
    CreationAuthorityStatus,
    CreationContext,
    CreationRequestVariant,
    CreationResult,
    DomainEntityType,
    DomainEvent,
    DomainEventMetadata,
    DomainEventType,
    EntityVersion,
    EventId,
    IdentifierAvailability,
    IdentifierAvailabilityId,
    IdentifierAvailabilityStatus,
    InvalidDomainValue,
    InvariantViolation,
    Objective,
    ObjectiveCreationSemanticInput,
    ObjectiveCreationSpec,
    ObjectiveDraftCreationRequest,
    ObjectiveId,
    ObjectiveState,
    Timestamp,
    TransitionReason,
    UnauthorizedTransition,
    create_entity,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
THIRD = UUID("aaaaaaaa-4321-4321-8321-cba987654321")


def actor(value: UUID, actor_type: ActorType) -> ActorIdentity:
    return ActorIdentity(ActorId(value), actor_type)


def timestamp() -> Timestamp:
    return Timestamp(datetime(2026, 9, 13, tzinfo=UTC))


def request(
    *, requested_by: ActorIdentity | None = None
) -> ObjectiveDraftCreationRequest:
    requester = requested_by or actor(VALUE, ActorType.REQUESTER)
    return ObjectiveDraftCreationRequest(
        EventId(VALUE),
        ObjectiveId(OTHER),
        requester,
        TransitionReason("Register bounded objective"),
        timestamp(),
        CorrelationId(VALUE),
        CausationId(OTHER),
        ObjectiveCreationSpec(
            "Restore one payment path",
            ("A deterministic acceptance check passes",),
            actor(THIRD, ActorType.HUMAN_OPERATOR),
            CompletionPolicyRef("objective-policy", "1"),
        ),
        ObjectiveCreationSemanticInput(CausationId(VALUE)),
    )


def authority(
    creation_request: ObjectiveDraftCreationRequest,
    *,
    decided_by: ActorIdentity | None = None,
    status: CreationAuthorityStatus = CreationAuthorityStatus.AUTHORIZED,
) -> CreationAuthorityDecision:
    return CreationAuthorityDecision(
        CreationAuthorityDecisionId(VALUE),
        creation_request.scope,
        decided_by or actor(OTHER, ActorType.SCHEDULER),
        status,
        (CausationId(VALUE),),
        timestamp(),
    )


def availability(
    creation_request: ObjectiveDraftCreationRequest,
    *,
    status: IdentifierAvailabilityStatus = IdentifierAvailabilityStatus.AVAILABLE,
) -> IdentifierAvailability:
    return IdentifierAvailability(
        IdentifierAvailabilityId(VALUE),
        creation_request.scope,
        DomainEntityType.OBJECTIVE,
        creation_request.entity_id,
        status,
        actor(UUID("bbbbbbbb-4321-4321-8321-cba987654321"), ActorType.SCHEDULER),
        timestamp(),
        creation_request.correlation_id,
    )


def context(creation_request: ObjectiveDraftCreationRequest) -> CreationContext:
    return CreationContext(
        authority(creation_request),
        availability(creation_request),
        actor(THIRD, ActorType.SYSTEM),
    )


def creation_event(creation_request: ObjectiveDraftCreationRequest) -> DomainEvent:
    return DomainEvent(
        creation_request.event_id,
        DomainEventType.OBJECTIVE_CREATED,
        DomainEntityType.OBJECTIVE,
        creation_request.entity_id,
        EntityVersion(1),
        authority(creation_request).decided_by,
        creation_request.timestamp,
        creation_request.correlation_id,
        creation_request.causation_id,
        creation_request.reason,
        DomainEventMetadata(None, ObjectiveState.DRAFT),
    )


def test_exactly_eight_closed_creation_request_variants() -> None:
    assert len(CreationRequestVariant) == 8
    assert {member.value for member in CreationRequestVariant} == {
        "OBJECTIVE_DRAFT",
        "TASK_DRAFT",
        "RUN_PENDING",
        "OUTCOME_PROPOSED",
        "EVALUATION_PENDING",
        "EFFECT_PLANNED",
        "EFFECT_COMMITTED",
        "EFFECT_QUARANTINED",
    }


def test_normalized_scope_is_immutable_and_has_no_source_state_or_version() -> None:
    scope = request().scope
    assert scope.target_state is ObjectiveState.DRAFT
    assert not hasattr(scope, "prior_state")
    assert not hasattr(scope, "version")
    assert not hasattr(scope, "expected_version")
    with pytest.raises(FrozenInstanceError):
        scope.entity_id = ObjectiveId(VALUE)  # type: ignore[misc]


def test_authority_rejects_a_decision_reused_for_a_relabelled_requester() -> None:
    original = request()
    substituted = replace(original, requested_by=actor(THIRD, ActorType.REQUESTER))
    forged_context = CreationContext(
        authority(original),
        availability(substituted),
        actor(THIRD, ActorType.SYSTEM),
    )
    with pytest.raises(UnauthorizedTransition, match="exact-bind request scope"):
        create_entity(substituted, forged_context)


def test_availability_rejects_a_observation_reused_for_changed_specification() -> None:
    original = request()
    substituted = replace(
        original,
        entity_spec=replace(original.entity_spec, goal="Change the requested goal"),
    )
    forged_context = CreationContext(
        authority(substituted),
        availability(original),
        actor(THIRD, ActorType.SYSTEM),
    )
    with pytest.raises(InvariantViolation, match="exact-bind request scope"):
        create_entity(substituted, forged_context)


def test_worker_cannot_relabel_its_principal_as_scheduler_authority() -> None:
    worker = actor(VALUE, ActorType.WORKER)
    creation_request = request(requested_by=worker)
    relabelled = actor(VALUE, ActorType.SCHEDULER)
    with pytest.raises(UnauthorizedTransition, match="cannot relabel"):
        create_entity(
            creation_request,
            CreationContext(
                authority(creation_request, decided_by=relabelled),
                availability(creation_request),
                actor(THIRD, ActorType.SYSTEM),
            ),
        )


def test_system_has_no_implicit_superuser_creation_authority() -> None:
    creation_request = request()
    with pytest.raises(UnauthorizedTransition, match="not eligible"):
        create_entity(
            creation_request,
            CreationContext(
                authority(
                    creation_request,
                    decided_by=actor(OTHER, ActorType.SYSTEM),
                ),
                availability(creation_request),
                actor(THIRD, ActorType.SYSTEM),
            ),
        )


def test_identifier_observation_must_not_be_requester_self_attestation() -> None:
    creation_request = request()
    with pytest.raises(InvalidDomainValue, match="must differ from the requester"):
        replace(
            availability(creation_request),
            observed_by=actor(VALUE, ActorType.SCHEDULER),
        )


def test_result_requires_canonical_version_one_and_matching_event() -> None:
    creation_request = request()
    decision = authority(creation_request)
    observed = availability(creation_request)
    snapshot = Objective(
        creation_request.entity_id,
        ObjectiveState.DRAFT,
        EntityVersion(1),
        creation_request.entity_spec.goal,
        creation_request.entity_spec.acceptance_criteria,
        creation_request.entity_spec.acceptance_authority,
        creation_request.entity_spec.completion_policy_ref,
    )
    result = CreationResult(
        snapshot,
        creation_event(creation_request),
        creation_request,
        decision,
        observed,
    )
    assert result.entity.version == EntityVersion(1)
    assert result.event.entity_version == EntityVersion(1)
    with pytest.raises(InvalidDomainValue, match="canonical version-1"):
        replace(result, entity=replace(snapshot, version=EntityVersion(2)))


def test_result_rejects_non_none_prior_state() -> None:
    creation_request = request()
    snapshot = Objective(
        creation_request.entity_id,
        ObjectiveState.DRAFT,
        EntityVersion(1),
        creation_request.entity_spec.goal,
        creation_request.entity_spec.acceptance_criteria,
        creation_request.entity_spec.acceptance_authority,
        creation_request.entity_spec.completion_policy_ref,
    )
    non_creation_event = DomainEvent(
        creation_request.event_id,
        DomainEventType.OBJECTIVE_ACTIVATED,
        DomainEntityType.OBJECTIVE,
        creation_request.entity_id,
        EntityVersion(1),
        authority(creation_request).decided_by,
        creation_request.timestamp,
        creation_request.correlation_id,
        creation_request.causation_id,
        creation_request.reason,
        DomainEventMetadata(ObjectiveState.DRAFT, ObjectiveState.ACTIVE),
    )
    with pytest.raises(
        InvalidDomainValue, match="exactly describe the creation result"
    ):
        CreationResult(
            snapshot,
            non_creation_event,
            creation_request,
            authority(creation_request),
            availability(creation_request),
        )


def test_shared_checks_fail_closed_before_entity_semantics_exist() -> None:
    creation_request = request()
    with pytest.raises(InvariantViolation, match="not implemented"):
        create_entity(creation_request, context(creation_request))
