"""Governed intent registration remains separate from Effect execution."""

from dataclasses import replace

import pytest

from symphony_k.domain import (
    ActorType,
    CreationSemanticDecisionStatus,
    DomainEventType,
    Effect,
    EffectDeduplicationRef,
    EffectId,
    EffectPayloadRef,
    EffectState,
    EffectTargetRef,
    EntityNotFound,
    EntityVersion,
    EventId,
    InvalidRelationship,
    InvariantViolation,
    PlannedEffectCreationRequest,
    PlannedEffectCreationSemanticInput,
    PlannedEffectCreationSpec,
    PlannedEffectOrigin,
    TaskId,
    TransitionReason,
    UnauthorizedTransition,
    create_entity,
)
from symphony_k.domain.creation_effect_semantics import (
    PlannedEffectIntentDecision,
    PlannedEffectIntentScope,
)
from symphony_k.domain.creation_relationships import (
    CreationObservationStatus,
    CreationProvenanceRef,
)
from symphony_k.domain.effect_governance import EffectGovernancePolicyRef
from tests.test_creation_run_outcome_evaluation import (
    DECIDER,
    EVIDENCE,
    IDENTITY,
    NOW,
    RUN,
    TASK,
    WORKER,
    RejectGuard,
    actor,
    context,
    observation,
    uid,
)

CONTROLLER = actor(70, ActorType.EFFECT_CONTROLLER)


def planned_request(with_run: bool = True) -> PlannedEffectCreationRequest:
    spec = PlannedEffectCreationSpec(
        PlannedEffectOrigin(TASK.task_id, WORKER, RUN.run_id if with_run else None),
        EffectTargetRef("target"),
        EffectPayloadRef("payload"),
    )
    scope = PlannedEffectIntentScope(
        EffectId(uid(71)),
        IDENTITY,
        spec,
        observation(TASK, "task"),
        observation(RUN, "run") if with_run else None,
        CreationProvenanceRef("intent"),
        CreationProvenanceRef("risk:low:v1"),
        CreationProvenanceRef("reversibility:reversible:v1"),
        CreationProvenanceRef("permissions:v1"),
        CreationProvenanceRef("authorization-class:policy:v1"),
        frozenset({EffectGovernancePolicyRef("policy", "1")}),
        EffectDeduplicationRef("dedup:1"),
    )
    decision = PlannedEffectIntentDecision(
        CreationProvenanceRef("intent-decision"),
        CreationSemanticDecisionStatus.PASSED,
        DECIDER,
        NOW,
        EVIDENCE,
        scope,
    )
    return PlannedEffectCreationRequest(
        EventId(uid(72)),
        scope.effect_id,
        WORKER,
        TransitionReason("Plan intent"),
        NOW,
        IDENTITY.correlation_id,
        IDENTITY.causation_id,
        spec,
        PlannedEffectCreationSemanticInput(IDENTITY.provenance_ref, scope, decision),
    )


def with_scope(
    request: PlannedEffectCreationRequest, scope: PlannedEffectIntentScope
) -> PlannedEffectCreationRequest:
    decision = request.semantic_input.decision
    assert decision is not None
    return replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            intent=scope,
            decision=replace(decision, scope=scope),
        ),
    )


@pytest.mark.parametrize("with_run", [False, True])
def test_planned_effect_is_only_intent(with_run: bool) -> None:
    request = planned_request(with_run)
    result = create_entity(request, context(request, CONTROLLER))
    assert result.entity == Effect(
        request.entity_id,
        EffectState.PLANNED,
        EntityVersion(1),
        request.entity_spec.origin,
        request.entity_spec.target_ref,
        request.entity_spec.payload_ref,
    )
    assert result.event.event_type is DomainEventType.EFFECT_PLANNED
    assert result.event.metadata.prior_state is None
    assert result.event.entity_version == EntityVersion(1)
    assert not hasattr(result, "authorization")
    assert not hasattr(result, "dispatch")


@pytest.mark.parametrize("field", ["task", "run"])
@pytest.mark.parametrize(
    "status",
    [
        CreationObservationStatus.MISSING,
        CreationObservationStatus.STALE,
        CreationObservationStatus.UNRESOLVED,
    ],
)
def test_planned_relationships_require_current_observations(
    field: str, status: CreationObservationStatus
) -> None:
    request = planned_request()
    scope = request.semantic_input.intent
    assert scope is not None and scope.run is not None
    original = scope.task if field == "task" else scope.run
    changed = replace(
        original,
        status=status,
        snapshot=original.snapshot
        if status is CreationObservationStatus.STALE
        else None,
    )
    scope = (
        replace(scope, task=changed) if field == "task" else replace(scope, run=changed)
    )
    request = with_scope(request, scope)
    with pytest.raises((EntityNotFound, InvariantViolation)):
        create_entity(request, context(request, CONTROLLER))


@pytest.mark.parametrize(
    "field",
    [
        "proposer",
        "target",
        "payload",
        "risk",
        "reversibility",
        "permission",
        "authorization",
        "dedup",
        "policy",
        "intent",
    ],
)
def test_intent_each_exact_binding_rejects_substitution(field: str) -> None:
    request = planned_request()
    scope = request.semantic_input.intent
    assert scope is not None
    if field == "proposer":
        request = replace(
            request,
            entity_spec=replace(
                request.entity_spec,
                origin=replace(
                    request.entity_spec.origin, proposed_by=actor(99, ActorType.WORKER)
                ),
            ),
        )
    elif field == "target":
        request = replace(
            request,
            entity_spec=replace(
                request.entity_spec, target_ref=EffectTargetRef("other")
            ),
        )
    elif field == "payload":
        request = replace(
            request,
            entity_spec=replace(
                request.entity_spec, payload_ref=EffectPayloadRef("other")
            ),
        )
    else:
        if field == "risk":
            scope = replace(scope, risk_ref=CreationProvenanceRef("other"))
        elif field == "reversibility":
            scope = replace(scope, reversibility_ref=CreationProvenanceRef("other"))
        elif field == "permission":
            scope = replace(
                scope, permission_requirements_ref=CreationProvenanceRef("other")
            )
        elif field == "authorization":
            scope = replace(
                scope, authorization_class_ref=CreationProvenanceRef("other")
            )
        elif field == "dedup":
            scope = replace(scope, deduplication_ref=EffectDeduplicationRef("other"))
        elif field == "policy":
            scope = replace(
                scope, policy_refs=frozenset({EffectGovernancePolicyRef("policy", "2")})
            )
        else:
            scope = replace(scope, intent_ref=CreationProvenanceRef("other"))
        request = replace(
            request, semantic_input=replace(request.semantic_input, intent=scope)
        )
    with pytest.raises(InvariantViolation):
        create_entity(request, context(request, CONTROLLER))


def test_effect_run_must_belong_to_task() -> None:
    request = planned_request()
    scope = request.semantic_input.intent
    assert scope is not None
    request = with_scope(
        request,
        replace(scope, run=observation(replace(RUN, task_id=TaskId(uid(99))), "run")),
    )
    with pytest.raises(InvalidRelationship):
        create_entity(request, context(request, CONTROLLER))


def test_planned_effect_authority_and_guard_fail_closed() -> None:
    request = planned_request()
    with pytest.raises(UnauthorizedTransition):
        create_entity(request, context(request))
    with pytest.raises(UnauthorizedTransition):
        create_entity(
            request,
            context(request, replace(WORKER, actor_type=ActorType.EFFECT_CONTROLLER)),
        )
    with pytest.raises(InvariantViolation, match="guard rejected"):
        create_entity(
            request, replace(context(request, CONTROLLER), guards=(RejectGuard(),))
        )


def test_planned_effect_annotations_are_exact_references() -> None:
    request = planned_request()
    result = create_entity(request, context(request, CONTROLLER))
    annotations = dict(result.event.metadata.annotations)
    expected = {
        "requested_by.actor_id": str(WORKER.actor_id),
        "requested_by.actor_type": "WORKER",
        "applying_service.actor_id": str(actor(6, ActorType.SYSTEM).actor_id),
        "applying_service.actor_type": "SYSTEM",
        "creation_authority_decision_ref": str(uid(30)),
        "identifier_availability_ref": str(uid(32)),
        "semantic_provenance_ref": str(IDENTITY.provenance_ref),
        "authority_policy_or_grant_ref.0000": str(uid(31)),
        "semantic_decision_ref": "intent-decision",
        "intent_ref": "intent",
        "risk_ref": "risk:low:v1",
        "reversibility_ref": "reversibility:reversible:v1",
        "permission_requirements_ref": "permissions:v1",
        "authorization_class_ref": "authorization-class:policy:v1",
        "deduplication_ref": "dedup:1",
        "intent_policy.0000.id": "policy",
        "intent_policy.0000.version": "1",
        "task.observation_ref": "task",
        "task.observed_version": "3",
        "run.observation_ref": "run",
        "run.observed_version": "4",
        "semantic_evidence_ref.0000": "evidence:a",
        "semantic_evidence_ref.0001": "evidence:z",
    }
    assert annotations == expected
