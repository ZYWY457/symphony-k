"""Observed external reality stays separate from authorization and intent."""

from dataclasses import replace

import pytest

from symphony_k.domain import (
    ActorType,
    CommittedEffectObservationCreationRequest,
    CreationSemanticDecisionStatus,
    DomainEventType,
    EffectAuthorizationFindingId,
    EffectDeduplicationRef,
    EffectExternalOperationRef,
    EffectGovernanceFindingId,
    EffectId,
    EffectIncidentId,
    EffectIncidentRecordId,
    EffectObservationId,
    EffectPayloadRef,
    EffectQuarantineContextId,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    EventId,
    EvidenceRef,
    InvalidDomainValue,
    InvalidRelationship,
    InvariantViolation,
    ObservedEffectCreationSemanticInput,
    ObservedEffectCreationSpec,
    ObservedEffectOrigin,
    QuarantinedEffectObservationCreationRequest,
    TaskId,
    TransitionReason,
    UnauthorizedTransition,
    create_entity,
)
from symphony_k.domain.creation_effect_observation import (
    EffectCreationQuarantineContext,
    ObservedEffectRegistrationDecision,
    ObservedEffectRegistrationScope,
)
from symphony_k.domain.creation_relationships import CreationProvenanceRef
from symphony_k.domain.effect_authorization import (
    EffectAuthorizationFindingRecord,
    EffectAuthorizationStatus,
)
from symphony_k.domain.effect_governance import (
    EffectGovernanceFindingRecord,
    EffectGovernancePolicyRef,
    EffectGovernanceStatus,
)
from symphony_k.domain.effect_incident import EffectIncidentRecord, EffectIncidentStatus
from symphony_k.domain.effect_observation import (
    EffectObservationRecord,
    EffectOccurrenceStatus,
)
from symphony_k.domain.effect_semantics import EffectQuarantineReason
from tests.test_creation_planned_effect import CONTROLLER
from tests.test_creation_run_outcome_evaluation import (
    DECIDER,
    EVIDENCE,
    IDENTITY,
    NOW,
    OBSERVER,
    RUN,
    TASK,
    WORKER,
    RejectGuard,
    actor,
    context,
    observation,
    uid,
)

type ObservedRequest = (
    CommittedEffectObservationCreationRequest
    | QuarantinedEffectObservationCreationRequest
)


def observed_request(
    uncertain: bool = False,
    linked: bool = False,
    status: EffectAuthorizationStatus = EffectAuthorizationStatus.UNAUTHORIZED,
) -> ObservedRequest:
    effect_id = EffectId(uid(80))
    origin = ObservedEffectOrigin(
        EffectExternalOperationRef("operation"),
        EVIDENCE,
        OBSERVER,
        NOW,
        TASK.task_id if linked else None,
        RUN.run_id if linked else None,
        None if linked else "External operation has no known accountable Task",
    )
    spec = ObservedEffectCreationSpec(
        origin, EffectTargetRef("target"), EffectPayloadRef("payload")
    )
    record = EffectObservationRecord(
        EffectObservationId(uid(81)),
        effect_id,
        EntityVersion(1),
        origin.external_operation_ref,
        EffectDeduplicationRef("dedup"),
        EffectOccurrenceStatus.UNCERTAIN
        if uncertain
        else EffectOccurrenceStatus.CONFIRMED,
        spec.target_ref,
        spec.payload_ref,
        EVIDENCE,
        OBSERVER,
        CONTROLLER,
        NOW,
        None if uncertain else NOW,
        NOW,
        IDENTITY.correlation_id,
    )
    authorization = EffectAuthorizationFindingRecord(
        EffectAuthorizationFindingId(uid(82)),
        effect_id,
        EntityVersion(1),
        status,
        "Prior authorization finding, not a new grant",
        EVIDENCE,
        DECIDER,
        CONTROLLER,
        NOW,
        NOW,
        IDENTITY.correlation_id,
    )
    governance = EffectGovernanceFindingRecord(
        EffectGovernanceFindingId(uid(83)),
        effect_id,
        EntityVersion(1),
        EffectGovernancePolicyRef("policy", "1"),
        EffectGovernanceStatus.NON_COMPLIANT,
        "Observed policy violation",
        EVIDENCE,
        DECIDER,
        CONTROLLER,
        NOW,
        NOW,
        IDENTITY.correlation_id,
    )
    incident = EffectIncidentRecord(
        EffectIncidentRecordId(uid(84)),
        EffectIncidentId(uid(85)),
        effect_id,
        EntityVersion(1),
        EffectIncidentStatus.OPEN,
        "Reconcile external operation",
        EVIDENCE,
        DECIDER,
        CONTROLLER,
        NOW,
        NOW,
        IDENTITY.correlation_id,
    )
    quarantine = (
        EffectCreationQuarantineContext(
            EffectQuarantineContextId(uid(86)),
            EffectQuarantineReason.UNKNOWN_OR_SUSPECTED_OCCURRENCE,
            CreationProvenanceRef("reconciliation"),
            EVIDENCE,
            CONTROLLER,
            NOW,
            incident.record_id,
        )
        if uncertain
        else None
    )
    scope = ObservedEffectRegistrationScope(
        effect_id,
        IDENTITY,
        spec,
        record.deduplication_ref,
        record,
        CreationProvenanceRef("independent-anchor"),
        authorization,
        (governance,),
        (incident,),
        observation(TASK, "task") if linked else None,
        observation(RUN, "run") if linked else None,
        quarantine,
    )
    decision = ObservedEffectRegistrationDecision(
        CreationProvenanceRef("observation-decision"),
        CreationSemanticDecisionStatus.PASSED,
        DECIDER,
        NOW,
        EVIDENCE,
        scope,
    )
    request_type = (
        QuarantinedEffectObservationCreationRequest
        if uncertain
        else CommittedEffectObservationCreationRequest
    )
    return request_type(
        EventId(uid(87)),
        effect_id,
        WORKER,
        TransitionReason("Register observed occurrence"),
        NOW,
        IDENTITY.correlation_id,
        IDENTITY.causation_id,
        spec,
        ObservedEffectCreationSemanticInput(IDENTITY.provenance_ref, scope, decision),
    )


def with_scope(
    request: ObservedRequest, scope: ObservedEffectRegistrationScope
) -> ObservedRequest:
    decision = request.semantic_input.decision
    assert decision is not None
    return replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            registration=scope,
            decision=replace(decision, scope=scope),
        ),
    )


@pytest.mark.parametrize("status", list(EffectAuthorizationStatus))
@pytest.mark.parametrize("uncertain", [False, True])
@pytest.mark.parametrize("linked", [False, True])
def test_observed_reality_is_recordable_regardless_of_authorization(
    status: EffectAuthorizationStatus, uncertain: bool, linked: bool
) -> None:
    request = observed_request(uncertain, linked, status)
    result = create_entity(request, context(request, CONTROLLER))
    assert result.entity.state is (
        EffectState.QUARANTINED if uncertain else EffectState.COMMITTED
    )
    assert result.entity.origin == request.entity_spec.origin
    assert result.entity.version == result.event.entity_version == EntityVersion(1)
    assert result.event.event_type is (
        DomainEventType.EFFECT_QUARANTINED
        if uncertain
        else DomainEventType.EFFECT_COMMITTED
    )
    assert result.event.metadata.prior_state is None
    assert not hasattr(result, "executor")
    assert not hasattr(result, "retry")


@pytest.mark.parametrize("uncertain", [False, True])
@pytest.mark.parametrize(
    "field",
    [
        "operation",
        "dedup",
        "target",
        "payload",
        "evidence",
        "observer",
        "recorder",
        "effect",
        "version",
        "correlation",
        "prior",
    ],
)
def test_each_observation_binding_is_exact(uncertain: bool, field: str) -> None:
    request = observed_request(uncertain)
    scope = request.semantic_input.registration
    assert scope is not None
    record = scope.observation
    if field == "operation":
        record = replace(
            record, external_operation_ref=EffectExternalOperationRef("substitute")
        )
    elif field == "dedup":
        record = replace(record, deduplication_ref=EffectDeduplicationRef("substitute"))
    elif field == "target":
        record = replace(record, target_ref=EffectTargetRef("substitute"))
    elif field == "payload":
        record = replace(record, payload_ref=None)
    elif field == "evidence":
        record = replace(record, evidence_refs=frozenset({EvidenceRef("substitute")}))
    elif field == "observer":
        record = replace(record, observed_by=actor(99, ActorType.SCHEDULER))
    elif field == "recorder":
        record = replace(record, recorded_by=actor(99, ActorType.EFFECT_CONTROLLER))
    elif field == "effect":
        record = replace(record, effect_id=EffectId(uid(99)))
    elif field == "version":
        record = replace(record, observed_effect_version=EntityVersion(2))
    elif field == "correlation":
        record = replace(record, correlation_id=type(IDENTITY.correlation_id)(uid(99)))
    else:
        record = replace(record, prior_observation_id=EffectObservationId(uid(99)))
    request = with_scope(request, replace(scope, observation=record))
    with pytest.raises(InvariantViolation):
        create_entity(request, context(request, CONTROLLER))


@pytest.mark.parametrize("uncertain", [False, True])
@pytest.mark.parametrize("status", list(EffectOccurrenceStatus))
def test_occurrence_status_selects_only_its_canonical_target(
    uncertain: bool, status: EffectOccurrenceStatus
) -> None:
    request = observed_request(uncertain)
    scope = request.semantic_input.registration
    assert scope is not None
    request = with_scope(
        request,
        replace(
            scope, observation=replace(scope.observation, occurrence_status=status)
        ),
    )
    expected = (
        EffectOccurrenceStatus.UNCERTAIN
        if uncertain
        else EffectOccurrenceStatus.CONFIRMED
    )
    if status is expected:
        create_entity(request, context(request, CONTROLLER))
    else:
        with pytest.raises(InvariantViolation):
            create_entity(request, context(request, CONTROLLER))


@pytest.mark.parametrize("relabel", [False, True])
def test_worker_self_report_cannot_anchor_occurrence(relabel: bool) -> None:
    request = observed_request()
    scope = request.semantic_input.registration
    assert scope is not None
    observer = replace(WORKER, actor_type=ActorType.SCHEDULER) if relabel else WORKER
    spec = replace(
        request.entity_spec,
        origin=replace(request.entity_spec.origin, observed_by=observer),
    )
    request = replace(request, entity_spec=spec)
    request = with_scope(
        request,
        replace(
            scope,
            spec=spec,
            observation=replace(scope.observation, observed_by=observer),
        ),
    )
    with pytest.raises(InvariantViolation):
        create_entity(request, context(request, CONTROLLER))


def test_observer_cannot_relabel_as_recording_controller() -> None:
    request = observed_request()
    with pytest.raises(UnauthorizedTransition):
        create_entity(
            request,
            context(request, replace(OBSERVER, actor_type=ActorType.EFFECT_CONTROLLER)),
        )


def test_unknown_payload_remains_unknown() -> None:
    request = observed_request()
    scope = request.semantic_input.registration
    assert scope is not None
    spec = replace(request.entity_spec, payload_ref=None)
    request = replace(request, entity_spec=spec)
    request = with_scope(
        request,
        replace(
            scope, spec=spec, observation=replace(scope.observation, payload_ref=None)
        ),
    )
    assert (
        create_entity(request, context(request, CONTROLLER)).entity.payload_ref is None
    )


def test_linked_run_task_mismatch_rejected() -> None:
    request = observed_request(linked=True)
    scope = request.semantic_input.registration
    assert scope is not None
    request = with_scope(
        request,
        replace(scope, run=observation(replace(RUN, task_id=TaskId(uid(99))), "run")),
    )
    with pytest.raises(InvalidRelationship):
        create_entity(request, context(request, CONTROLLER))


def test_unlinked_attribution_cannot_fabricate_ownership() -> None:
    request = observed_request()
    scope = request.semantic_input.registration
    assert scope is not None
    request = with_scope(request, replace(scope, task=observation(TASK, "task")))
    with pytest.raises(InvalidRelationship):
        create_entity(request, context(request, CONTROLLER))
    with pytest.raises(InvalidDomainValue):
        replace(request.entity_spec.origin, task_id=TASK.task_id)


@pytest.mark.parametrize(
    "field", ["quarantine", "incident", "authorization", "governance", "anchor"]
)
def test_registration_bundle_substitution_fails(field: str) -> None:
    request = observed_request(True)
    scope = request.semantic_input.registration
    assert scope is not None and scope.quarantine is not None
    if field == "quarantine":
        scope = replace(scope, quarantine=None)
    elif field == "incident":
        scope = replace(scope, incidents=())
    elif field == "authorization":
        scope = replace(
            scope,
            authorization_finding=replace(
                scope.authorization_finding, effect_id=EffectId(uid(99))
            ),
        )
    elif field == "governance":
        scope = replace(
            scope,
            governance_findings=(
                replace(
                    scope.governance_findings[0],
                    recorded_by=actor(99, ActorType.EFFECT_CONTROLLER),
                ),
            ),
        )
    else:
        request = replace(
            request,
            semantic_input=replace(
                request.semantic_input,
                registration=replace(
                    scope, evidence_anchor_ref=CreationProvenanceRef("substitute")
                ),
            ),
        )
    if field != "anchor":
        request = with_scope(request, scope)
    with pytest.raises(InvariantViolation):
        create_entity(request, context(request, CONTROLLER))


@pytest.mark.parametrize("uncertain", [False, True])
def test_observation_guard_failure_returns_no_result(uncertain: bool) -> None:
    request = observed_request(uncertain)
    with pytest.raises(InvariantViolation, match="guard rejected"):
        create_entity(
            request, replace(context(request, CONTROLLER), guards=(RejectGuard(),))
        )


@pytest.mark.parametrize("uncertain", [False, True])
def test_observed_annotations_exact_reference_vocabulary(uncertain: bool) -> None:
    request = observed_request(uncertain)
    expected = {
        "requested_by.actor_id": str(WORKER.actor_id),
        "requested_by.actor_type": "WORKER",
        "applying_service.actor_id": str(actor(6, ActorType.SYSTEM).actor_id),
        "applying_service.actor_type": "SYSTEM",
        "creation_authority_decision_ref": str(uid(30)),
        "identifier_availability_ref": str(uid(32)),
        "semantic_provenance_ref": str(IDENTITY.provenance_ref),
        "authority_policy_or_grant_ref.0000": str(uid(31)),
        "semantic_decision_ref": "observation-decision",
        "observation_ref": str(uid(81)),
        "evidence_anchor_ref": "independent-anchor",
        "external_operation_ref": "operation",
        "deduplication_ref": "dedup",
        "authorization_finding_ref": str(uid(82)),
        "governance_finding_ref.0000": str(uid(83)),
        "incident_record_ref.0000": str(uid(84)),
        "semantic_evidence_ref.0000": "evidence:a",
        "semantic_evidence_ref.0001": "evidence:z",
    }
    if uncertain:
        expected.update(
            {
                "quarantine_context_ref": str(uid(86)),
                "reconciliation_ref": "reconciliation",
            }
        )
    assert (
        dict(
            create_entity(
                request, context(request, CONTROLLER)
            ).event.metadata.annotations
        )
        == expected
    )
