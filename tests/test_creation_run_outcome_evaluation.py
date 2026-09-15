"""M7D3 registration proofs; shared grants are refreshed in semantic attacks."""

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArtifactRef,
    CausationId,
    CompletionPolicyRef,
    CorrelationId,
    CreationAuthorityDecision,
    CreationAuthorityDecisionId,
    CreationAuthorityStatus,
    CreationContext,
    CreationRequest,
    CreationSemanticDecisionStatus,
    DomainEventType,
    Effect,
    EffectId,
    EffectPayloadRef,
    EffectState,
    EffectTargetRef,
    EntityNotFound,
    EntityVersion,
    EvaluationCreationSemanticInput,
    EvaluationCreationSpec,
    EvaluationId,
    EvaluationMethodRef,
    EvaluationPendingCreationRequest,
    EvaluationTargetRef,
    EventId,
    EvidenceRef,
    ExecutionProfileRef,
    IdentifierAvailability,
    IdentifierAvailabilityId,
    IdentifierAvailabilityStatus,
    InvalidDomainValue,
    InvalidRelationship,
    InvariantViolation,
    Objective,
    ObjectiveId,
    ObjectiveState,
    Outcome,
    OutcomeCreationSemanticInput,
    OutcomeCreationSpec,
    OutcomeId,
    OutcomeProposedCreationRequest,
    OutcomeState,
    PlannedEffectOrigin,
    Run,
    RunCreationSemanticInput,
    RunCreationSpec,
    RunId,
    RunPendingCreationRequest,
    RunState,
    Task,
    TaskId,
    TaskState,
    Timestamp,
    TransitionReason,
    UnauthorizedTransition,
    create_entity,
)
from symphony_k.domain.creation_relationships import (
    CreationObservationStatus,
    CreationProvenanceRef,
    CreationRelationshipObservation,
    CreationRequestIdentity,
    RelatedSnapshot,
    related_id,
)
from symphony_k.domain.creation_run_outcome_evaluation import (
    EvaluationRequestDecision,
    EvaluationRequestScope,
    OutcomeProposalDecision,
    OutcomeProposalScope,
    RunCreationLineageKind,
    RunRegistrationDecision,
    RunRegistrationScope,
)
from symphony_k.domain.outcome_semantics import OutcomeAcceptanceScopeRef


def uid(number: int) -> UUID:
    return UUID(int=number)


def actor(number: int, role: ActorType) -> ActorIdentity:
    return ActorIdentity(ActorId(uid(number)), role)


NOW = Timestamp(datetime(2026, 9, 15, tzinfo=UTC))
WORKER = actor(1, ActorType.WORKER)
DECIDER = actor(2, ActorType.POLICY_ENGINE)
OBSERVER = actor(3, ActorType.SCHEDULER)
SCHEDULER = actor(4, ActorType.SCHEDULER)
IDENTITY = CreationRequestIdentity(
    WORKER, CausationId(uid(10)), CorrelationId(uid(11)), CausationId(uid(12))
)
EVIDENCE = frozenset({EvidenceRef("evidence:z"), EvidenceRef("evidence:a")})
POLICY = CompletionPolicyRef("completion", "1")
PROFILE = ExecutionProfileRef("profile", "1")
OBJECTIVE = Objective(
    ObjectiveId(uid(20)),
    ObjectiveState.ACTIVE,
    EntityVersion(2),
    "Goal",
    ("Criterion",),
    actor(5, ActorType.HUMAN_OPERATOR),
    POLICY,
)
TASK = Task(
    TaskId(uid(21)),
    TaskState.READY,
    EntityVersion(3),
    "Work",
    OBJECTIVE.objective_id,
    POLICY,
)
RUN = Run(RunId(uid(22)), TASK.task_id, RunState.RUNNING, EntityVersion(4), PROFILE)
OUTCOME = Outcome(
    OutcomeId(uid(23)),
    RUN.run_id,
    OutcomeState.PROPOSED,
    EntityVersion(5),
    WORKER,
    frozenset({ArtifactRef("artifact:a")}),
    EVIDENCE,
)
EFFECT = Effect(
    EffectId(uid(24)),
    EffectState.PLANNED,
    EntityVersion(6),
    PlannedEffectOrigin(TASK.task_id, WORKER),
    EffectTargetRef("target"),
    EffectPayloadRef("payload"),
)


def observation(
    snapshot: RelatedSnapshot, name: str
) -> CreationRelationshipObservation:
    return CreationRelationshipObservation(
        CreationProvenanceRef(name),
        IDENTITY,
        related_id(snapshot),
        CreationObservationStatus.CURRENT,
        snapshot,
        OBSERVER,
        NOW,
        EVIDENCE,
    )


def context(
    request: CreationRequest, authority: ActorIdentity = SCHEDULER
) -> CreationContext:
    return CreationContext(
        CreationAuthorityDecision(
            CreationAuthorityDecisionId(uid(30)),
            request.scope,
            authority,
            CreationAuthorityStatus.AUTHORIZED,
            (CausationId(uid(31)),),
            NOW,
        ),
        IdentifierAvailability(
            IdentifierAvailabilityId(uid(32)),
            request.scope,
            request.entity_type,
            request.entity_id,
            IdentifierAvailabilityStatus.AVAILABLE,
            OBSERVER,
            NOW,
            request.correlation_id,
        ),
        actor(6, ActorType.SYSTEM),
    )


def run_request(predecessor: bool = False) -> RunPendingCreationRequest:
    spec = RunCreationSpec(TASK.task_id, PROFILE, RUN.run_id if predecessor else None)
    scope = RunRegistrationScope(
        RunId(uid(40)),
        IDENTITY,
        spec,
        observation(TASK, "task"),
        observation(OBJECTIVE, "objective"),
        CreationProvenanceRef("attempt"),
        CreationProvenanceRef("profile-selection"),
        RunCreationLineageKind.REASSIGNMENT
        if predecessor
        else RunCreationLineageKind.NEW_ATTEMPT,
        CreationProvenanceRef("transfer") if predecessor else None,
        (observation(RUN, "predecessor"),) if predecessor else (),
    )
    decision = RunRegistrationDecision(
        CreationProvenanceRef("run-decision"),
        CreationSemanticDecisionStatus.PASSED,
        DECIDER,
        NOW,
        EVIDENCE,
        scope,
    )
    return RunPendingCreationRequest(
        EventId(uid(41)),
        scope.run_id,
        WORKER,
        TransitionReason("Register"),
        NOW,
        IDENTITY.correlation_id,
        IDENTITY.causation_id,
        spec,
        RunCreationSemanticInput(IDENTITY.provenance_ref, scope, decision),
    )


def outcome_request(prior: bool = False) -> OutcomeProposedCreationRequest:
    spec = OutcomeCreationSpec(
        RUN.run_id,
        WORKER,
        OUTCOME.artifact_refs,
        EVIDENCE,
        prior_outcome_id=OUTCOME.outcome_id if prior else None,
    )
    scope = OutcomeProposalScope(
        OutcomeId(uid(50)),
        IDENTITY,
        spec,
        observation(RUN, "run"),
        TASK.task_id,
        OutcomeAcceptanceScopeRef("acceptance", "1"),
        CreationProvenanceRef("proposal"),
        (observation(OUTCOME, "prior"),) if prior else (),
        (observation(RUN, "prior-run"),) if prior else (),
        OutcomeAcceptanceScopeRef("acceptance", "1") if prior else None,
        CreationProvenanceRef("lineage") if prior else None,
    )
    decision = OutcomeProposalDecision(
        CreationProvenanceRef("outcome-decision"),
        CreationSemanticDecisionStatus.PASSED,
        DECIDER,
        NOW,
        EVIDENCE,
        scope,
    )
    return OutcomeProposedCreationRequest(
        EventId(uid(51)),
        scope.outcome_id,
        WORKER,
        TransitionReason("Propose"),
        NOW,
        IDENTITY.correlation_id,
        IDENTITY.causation_id,
        spec,
        OutcomeCreationSemanticInput(IDENTITY.provenance_ref, scope, decision),
    )


def evaluation_request(
    kind: str = "run", assigned: bool = True
) -> EvaluationPendingCreationRequest:
    snapshots: dict[str, Run | Outcome | Effect] = {
        "run": RUN,
        "outcome": OUTCOME,
        "effect": EFFECT,
    }
    snapshot = snapshots.get(kind)
    if isinstance(snapshot, Run):
        target = EvaluationTargetRef(snapshot.run_id, snapshot.version)
    elif isinstance(snapshot, Outcome):
        target = EvaluationTargetRef(snapshot.outcome_id, snapshot.version)
    elif isinstance(snapshot, Effect):
        target = EvaluationTargetRef(snapshot.effect_id, snapshot.version)
    else:
        target = EvaluationTargetRef(EvidenceRef("evidence:a"))
    spec = EvaluationCreationSpec(
        target,
        EvaluationMethodRef("method", "1"),
        actor(7, ActorType.EVALUATOR) if assigned else None,
    )
    scope = EvaluationRequestScope(
        EvaluationId(uid(60)),
        IDENTITY,
        spec,
        CreationProvenanceRef("validation-scope"),
        CreationProvenanceRef("validation-policy"),
        OUTCOME.artifact_refs,
        EVIDENCE,
        (WORKER,),
        observation(snapshot, "target") if snapshot is not None else None,
        CreationProvenanceRef("anchor") if snapshot is None else None,
        None if assigned else CreationProvenanceRef("assignment"),
    )
    decision = EvaluationRequestDecision(
        CreationProvenanceRef("evaluation-decision"),
        CreationSemanticDecisionStatus.PASSED,
        DECIDER,
        NOW,
        EVIDENCE,
        scope,
    )
    return EvaluationPendingCreationRequest(
        EventId(uid(61)),
        scope.evaluation_id,
        WORKER,
        TransitionReason("Validate"),
        NOW,
        IDENTITY.correlation_id,
        IDENTITY.causation_id,
        spec,
        EvaluationCreationSemanticInput(IDENTITY.provenance_ref, scope, decision),
    )


def with_run_scope(
    request: RunPendingCreationRequest, scope: RunRegistrationScope
) -> RunPendingCreationRequest:
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


def with_outcome_scope(
    request: OutcomeProposedCreationRequest, scope: OutcomeProposalScope
) -> OutcomeProposedCreationRequest:
    decision = request.semantic_input.decision
    assert decision is not None
    return replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            proposal=scope,
            decision=replace(decision, scope=scope),
        ),
    )


def with_evaluation_scope(
    request: EvaluationPendingCreationRequest, scope: EvaluationRequestScope
) -> EvaluationPendingCreationRequest:
    decision = request.semantic_input.decision
    assert decision is not None
    return replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            validation=scope,
            decision=replace(decision, scope=scope),
        ),
    )


@pytest.mark.parametrize("predecessor", [False, True])
def test_run_registration_preserves_pending_attempt(predecessor: bool) -> None:
    request = run_request(predecessor)
    result = create_entity(request, context(request))
    assert result.entity == Run(
        request.entity_id,
        TASK.task_id,
        RunState.PENDING,
        EntityVersion(1),
        PROFILE,
        RUN.run_id if predecessor else None,
    )
    assert result.event.event_type is DomainEventType.RUN_CREATED
    assert RUN.state is RunState.RUNNING


@pytest.mark.parametrize("prior", [False, True])
def test_worker_proposal_remains_unvalidated_claim(prior: bool) -> None:
    request = outcome_request(prior)
    result = create_entity(request, context(request))
    assert result.entity.state is OutcomeState.PROPOSED
    assert result.entity.producer == WORKER
    assert result.entity.superseded_by_outcome_id is None
    assert result.event.event_type is DomainEventType.OUTCOME_PROPOSED


@pytest.mark.parametrize("kind", ["run", "outcome", "effect", "evidence"])
@pytest.mark.parametrize("assigned", [False, True])
def test_pending_evaluation_targets(kind: str, assigned: bool) -> None:
    request = evaluation_request(kind, assigned)
    result = create_entity(request, context(request))
    assert result.entity.result is None
    assert result.entity.target == request.entity_spec.target
    assert result.event.event_type is DomainEventType.EVALUATION_REQUESTED
    assert result.event.metadata.prior_state is None
    assert result.entity.version == result.event.entity_version == EntityVersion(1)


@pytest.mark.parametrize("field", ["task", "primary_objective"])
@pytest.mark.parametrize(
    "status",
    [
        CreationObservationStatus.MISSING,
        CreationObservationStatus.STALE,
        CreationObservationStatus.UNRESOLVED,
    ],
)
def test_run_missing_stale_relationships(
    field: str, status: CreationObservationStatus
) -> None:
    request = run_request()
    scope = request.semantic_input.registration
    assert scope is not None
    original = scope.task if field == "task" else scope.primary_objective
    changed = replace(
        original,
        status=status,
        snapshot=original.snapshot
        if status is CreationObservationStatus.STALE
        else None,
    )
    scope = (
        replace(scope, task=changed)
        if field == "task"
        else replace(scope, primary_objective=changed)
    )
    request = with_run_scope(request, scope)
    with pytest.raises((EntityNotFound, InvariantViolation)):
        create_entity(request, context(request))


@pytest.mark.parametrize(
    "state",
    [
        TaskState.DRAFT,
        TaskState.BLOCKED,
        TaskState.COMPLETED,
        TaskState.FAILED,
        TaskState.CANCELLED,
    ],
)
def test_run_task_lifecycle_ineligible(state: TaskState) -> None:
    request = run_request()
    scope = request.semantic_input.registration
    assert scope is not None
    request = with_run_scope(
        request, replace(scope, task=observation(replace(TASK, state=state), "task"))
    )
    with pytest.raises(InvariantViolation):
        create_entity(request, context(request))


@pytest.mark.parametrize(
    "state", [value for value in ObjectiveState if value is not ObjectiveState.ACTIVE]
)
def test_run_objective_lifecycle_ineligible(state: ObjectiveState) -> None:
    request = run_request()
    scope = request.semantic_input.registration
    assert scope is not None
    request = with_run_scope(
        request,
        replace(
            scope,
            primary_objective=observation(replace(OBJECTIVE, state=state), "objective"),
        ),
    )
    with pytest.raises(InvariantViolation):
        create_entity(request, context(request))


@pytest.mark.parametrize(
    "attack",
    [
        "task-id",
        "objective-id",
        "profile",
        "attempt",
        "lineage-kind",
        "wrong-task",
        "self",
        "cycle",
        "skip",
    ],
)
def test_run_scope_and_lineage_attacks(attack: str) -> None:
    request = run_request(True)
    scope = request.semantic_input.registration
    assert scope is not None
    if attack == "task-id":
        scope = replace(
            scope, task=observation(replace(TASK, task_id=TaskId(uid(99))), "task")
        )
    elif attack == "objective-id":
        scope = replace(
            scope,
            task=observation(
                replace(TASK, primary_objective_id=ObjectiveId(uid(99))), "task"
            ),
        )
    elif attack == "profile":
        request = replace(
            request,
            entity_spec=replace(
                request.entity_spec,
                execution_profile_ref=ExecutionProfileRef("other", "1"),
            ),
        )
    elif attack == "attempt":
        request = replace(
            request,
            semantic_input=replace(
                request.semantic_input,
                registration=replace(scope, attempt_ref=CreationProvenanceRef("other")),
            ),
        )
    elif attack == "lineage-kind":
        scope = replace(scope, lineage_kind=RunCreationLineageKind.NEW_ATTEMPT)
    elif attack == "wrong-task":
        scope = replace(
            scope,
            predecessor_lineage=(
                observation(replace(RUN, task_id=TaskId(uid(99))), "predecessor"),
            ),
        )
    elif attack == "self":
        request = replace(
            request,
            entity_spec=replace(
                request.entity_spec, predecessor_run_id=request.entity_id
            ),
        )
        scope = replace(scope, spec=request.entity_spec)
    elif attack == "cycle":
        scope = replace(
            scope,
            predecessor_lineage=(
                observation(
                    replace(RUN, predecessor_run_id=request.entity_id), "predecessor"
                ),
                observation(RUN, "repeated"),
            ),
        )
    else:
        scope = replace(
            scope,
            predecessor_lineage=(
                observation(
                    replace(RUN, predecessor_run_id=RunId(uid(99))), "predecessor"
                ),
            ),
        )
    if attack not in {"profile", "attempt"}:
        request = with_run_scope(request, scope)
    with pytest.raises((InvariantViolation, InvalidRelationship)):
        create_entity(request, context(request))


@pytest.mark.parametrize(
    "attack",
    [
        "missing",
        "stale",
        "run",
        "producer",
        "artifact",
        "evidence",
        "scope",
        "task",
        "prior-run",
        "cycle",
        "skip",
    ],
)
def test_outcome_binding_and_lineage_attacks(attack: str) -> None:
    request = outcome_request(True)
    scope = request.semantic_input.proposal
    assert scope is not None
    if attack in {"missing", "stale"}:
        scope = replace(
            scope,
            originating_run=replace(
                scope.originating_run,
                status=CreationObservationStatus.MISSING
                if attack == "missing"
                else CreationObservationStatus.STALE,
                snapshot=None if attack == "missing" else RUN,
            ),
        )
    elif attack == "run":
        request = replace(
            request, entity_spec=replace(request.entity_spec, run_id=RunId(uid(99)))
        )
    elif attack == "producer":
        request = replace(
            request,
            entity_spec=replace(
                request.entity_spec, producer=actor(99, ActorType.WORKER)
            ),
        )
    elif attack == "artifact":
        request = replace(
            request,
            entity_spec=replace(
                request.entity_spec,
                artifact_refs=frozenset({ArtifactRef("substitute")}),
            ),
        )
    elif attack == "evidence":
        request = replace(
            request,
            entity_spec=replace(
                request.entity_spec,
                evidence_refs=frozenset({EvidenceRef("substitute")}),
            ),
        )
    elif attack == "scope":
        scope = replace(
            scope, prior_acceptance_scope=OutcomeAcceptanceScopeRef("other", "1")
        )
    elif attack == "task":
        scope = replace(
            scope,
            prior_runs=(
                observation(replace(RUN, task_id=TaskId(uid(99))), "prior-run"),
            ),
        )
    elif attack == "prior-run":
        scope = replace(
            scope,
            prior_lineage=(
                observation(replace(OUTCOME, run_id=RunId(uid(99))), "prior"),
            ),
        )
    elif attack == "cycle":
        scope = replace(
            scope,
            prior_lineage=(
                observation(
                    replace(OUTCOME, prior_outcome_id=request.entity_id), "prior"
                ),
                observation(OUTCOME, "repeat"),
            ),
            prior_runs=(observation(RUN, "prior-run"), observation(RUN, "repeat-run")),
        )
    else:
        scope = replace(
            scope,
            prior_lineage=(
                observation(
                    replace(OUTCOME, prior_outcome_id=OutcomeId(uid(99))), "prior"
                ),
            ),
        )
    request = with_outcome_scope(request, scope)
    with pytest.raises((EntityNotFound, InvariantViolation, InvalidRelationship)):
        create_entity(request, context(request))


@pytest.mark.parametrize(
    "attack",
    [
        "missing",
        "stale",
        "version",
        "method",
        "policy",
        "scope",
        "assignment",
        "non-independent",
        "unassigned",
    ],
)
def test_evaluation_scope_attacks(attack: str) -> None:
    request = evaluation_request()
    scope = request.semantic_input.validation
    assert scope is not None and scope.target_observation is not None
    if attack in {"missing", "stale"}:
        scope = replace(
            scope,
            target_observation=replace(
                scope.target_observation,
                status=CreationObservationStatus.MISSING
                if attack == "missing"
                else CreationObservationStatus.STALE,
                snapshot=None if attack == "missing" else RUN,
            ),
        )
    elif attack == "version":
        request = replace(
            request,
            entity_spec=replace(
                request.entity_spec,
                target=EvaluationTargetRef(RUN.run_id, EntityVersion(99)),
            ),
        )
        scope = replace(scope, spec=request.entity_spec)
    elif attack == "method":
        request = replace(
            request,
            entity_spec=replace(
                request.entity_spec, method=EvaluationMethodRef("other", "1")
            ),
        )
    elif attack in {"policy", "scope"}:
        changed = (
            replace(scope, validation_policy_ref=CreationProvenanceRef("other"))
            if attack == "policy"
            else replace(scope, validation_scope_ref=CreationProvenanceRef("other"))
        )
        request = replace(
            request, semantic_input=replace(request.semantic_input, validation=changed)
        )
    elif attack in {"assignment", "non-independent"}:
        verifier = (
            actor(99, ActorType.WORKER)
            if attack == "assignment"
            else replace(WORKER, actor_type=ActorType.EVALUATOR)
        )
        request = replace(
            request, entity_spec=replace(request.entity_spec, verifier=verifier)
        )
        scope = replace(scope, spec=request.entity_spec)
    else:
        request = replace(
            request, entity_spec=replace(request.entity_spec, verifier=None)
        )
        scope = replace(scope, spec=request.entity_spec)
    if attack not in {"policy", "scope"}:
        request = with_evaluation_scope(request, scope)
    with pytest.raises((EntityNotFound, InvariantViolation)):
        create_entity(request, context(request))


@dataclass(frozen=True)
class RejectGuard:
    def validate(self, request: CreationRequest) -> None:
        raise InvariantViolation("guard rejected")


@pytest.mark.parametrize(
    "creation_request", [run_request(), outcome_request(), evaluation_request()]
)
def test_guard_failure_and_authority_relabel_return_no_result(
    creation_request: CreationRequest,
) -> None:
    request = creation_request
    with pytest.raises(InvariantViolation, match="guard rejected"):
        create_entity(request, replace(context(request), guards=(RejectGuard(),)))
    with pytest.raises(UnauthorizedTransition):
        create_entity(
            request, context(request, replace(WORKER, actor_type=ActorType.SCHEDULER))
        )


def test_evidence_version_and_empty_artifacts_are_structurally_rejected() -> None:
    with pytest.raises(InvalidDomainValue):
        EvaluationTargetRef(EvidenceRef("evidence:a"), EntityVersion(1))  # type: ignore[call-overload]
    with pytest.raises(InvalidDomainValue):
        replace(outcome_request().entity_spec, artifact_refs=frozenset())


@pytest.mark.parametrize("kind", ["run", "outcome", "evaluation"])
def test_exact_canonical_annotations(kind: str) -> None:
    requests: dict[str, CreationRequest] = {
        "run": run_request(),
        "outcome": outcome_request(),
        "evaluation": evaluation_request(),
    }
    request = requests[kind]
    expected = {
        "requested_by.actor_id": str(WORKER.actor_id),
        "requested_by.actor_type": "WORKER",
        "applying_service.actor_id": str(ActorId(uid(6))),
        "applying_service.actor_type": "SYSTEM",
        "creation_authority_decision_ref": str(CreationAuthorityDecisionId(uid(30))),
        "identifier_availability_ref": str(IdentifierAvailabilityId(uid(32))),
        "semantic_provenance_ref": str(IDENTITY.provenance_ref),
        "authority_policy_or_grant_ref.0000": str(CausationId(uid(31))),
        "semantic_decision_ref": f"{kind}-decision",
        "semantic_evidence_ref.0000": "evidence:a",
        "semantic_evidence_ref.0001": "evidence:z",
    }
    if kind == "run":
        expected.update(
            {
                "attempt_ref": "attempt",
                "profile_selection_ref": "profile-selection",
                "task.observation_ref": "task",
                "task.observed_version": "3",
                "primary_objective.observation_ref": "objective",
                "primary_objective.observed_version": "2",
            }
        )
    elif kind == "outcome":
        expected.update(
            {
                "proposal_ref": "proposal",
                "task_id": str(TASK.task_id),
                "acceptance_scope.id": "acceptance",
                "acceptance_scope.version": "1",
                "originating_run.observation_ref": "run",
                "originating_run.observed_version": "4",
            }
        )
    else:
        expected.update(
            {
                "validation_scope_ref": "validation-scope",
                "validation_policy_ref": "validation-policy",
                "artifact_ref.0000": "artifact:a",
                "target.observation_ref": "target",
                "target.observed_version": "4",
            }
        )
    first = create_entity(request, context(request))
    second = create_entity(request, context(request))
    assert dict(first.event.metadata.annotations) == expected
    assert second == first


@pytest.mark.parametrize("kind", ["run", "outcome", "evaluation"])
@pytest.mark.parametrize(
    "status",
    [
        CreationSemanticDecisionStatus.REJECTED,
        CreationSemanticDecisionStatus.UNRESOLVED,
    ],
)
def test_nonpassed_semantic_decisions_fail(
    kind: str, status: CreationSemanticDecisionStatus
) -> None:
    requests: dict[
        str,
        RunPendingCreationRequest
        | OutcomeProposedCreationRequest
        | EvaluationPendingCreationRequest,
    ] = {
        "run": run_request(),
        "outcome": outcome_request(),
        "evaluation": evaluation_request(),
    }
    request = requests[kind]
    decision = request.semantic_input.decision
    assert decision is not None
    changed = replace(
        request,
        semantic_input=replace(
            request.semantic_input,
            decision=replace(decision, status=status),  # type: ignore[arg-type]
        ),
    )
    with pytest.raises(InvariantViolation):
        create_entity(changed, context(changed))


def test_creation_modules_have_no_execution_dependencies() -> None:
    import ast
    from pathlib import Path

    domain = Path(__file__).resolve().parents[1] / "src" / "symphony_k" / "domain"
    for path in domain.glob("creation*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(
                    item.name in {"dataclasses", "enum", "typing"}
                    for item in node.names
                )
            if isinstance(node, ast.ImportFrom):
                assert node.level == 1 or node.module in {
                    "__future__",
                    "dataclasses",
                    "enum",
                    "typing",
                }
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {
                    "transition_entity",
                    "open",
                    "exec",
                    "eval",
                    "__import__",
                }


@pytest.mark.parametrize("kind", ["effect", "outcome"])
def test_target_producer_cannot_be_omitted_from_independence_scope(kind: str) -> None:
    request = evaluation_request(kind)
    scope = request.semantic_input.validation
    assert scope is not None
    request = with_evaluation_scope(
        request, replace(scope, producing_principals=(actor(99, ActorType.WORKER),))
    )
    with pytest.raises(InvariantViolation):
        create_entity(request, context(request))
