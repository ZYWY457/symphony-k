"""Public G1/M1A facade operations over the accepted Stage 1 kernel."""

from dataclasses import fields, replace
from typing import get_type_hints

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CreationAuthorityDecision,
    CreationContext,
    Effect,
    EffectId,
    EntityVersion,
    Evaluation,
    EvaluationPendingCreationRequest,
    EvaluationResult,
    EvaluationSemanticGuard,
    EvaluationState,
    Objective,
    ObjectiveId,
    Outcome,
    OutcomeId,
    OutcomeProposedCreationRequest,
    OutcomeState,
    Run,
    RunId,
    RunPendingCreationRequest,
    RunState,
    Task,
    TaskId,
    TransitionAuthorityDecision,
    TransitionContext,
    TransitionRequest,
)
from symphony_k.governance import (
    AuthorityDeniedError,
    EffectRef,
    EvaluationRef,
    EvaluationSubmission,
    EvaluationTargetReference,
    EvaluationTransitionSubmission,
    GovernanceFacade,
    InvalidRequestError,
    NotFoundError,
    ObjectiveRef,
    OutcomeCandidateSubmission,
    OutcomeRef,
    RunCandidateSubmission,
    RunRef,
    TaskRef,
    TrustedEvaluationBinding,
    TrustedEvaluationTransitionBinding,
    TrustedOutcomeBinding,
    TrustedRunBinding,
    UnsupportedOperationError,
    reference_of,
)
from symphony_k.persistence.service import LifecycleService
from symphony_k.persistence.sqlite import SQLiteStore
from tests import test_creation_run_outcome_evaluation as creation_fx
from tests import test_evaluation_semantic_transitions as evaluation_fx
from tests.persistence_fixtures import seed_related, seed_snapshot


class TrustedFixtureBinder:
    """Test-only stand-in for an authenticated boundary-owned provider."""

    def __init__(self, *allowed_identities: ActorIdentity) -> None:
        self.allowed_actor_ids = {actor.actor_id for actor in allowed_identities}
        self.runs: dict[object, TrustedRunBinding] = {}
        self.outcomes: dict[object, TrustedOutcomeBinding] = {}
        self.evaluations: dict[object, TrustedEvaluationBinding] = {}
        self.transitions: dict[object, TrustedEvaluationTransitionBinding] = {}

    def _authorize(self, claim: ActorIdentity) -> None:
        if claim.actor_id not in self.allowed_actor_ids:
            raise AuthorityDeniedError("Caller identity claim is not authenticated")

    def bind_run_candidate(
        self, submission: RunCandidateSubmission
    ) -> TrustedRunBinding:
        self._authorize(submission.caller_identity_claim)
        return self.runs[submission.event_id]

    def bind_outcome_candidate(
        self, submission: OutcomeCandidateSubmission
    ) -> TrustedOutcomeBinding:
        self._authorize(submission.caller_identity_claim)
        return self.outcomes[submission.event_id]

    def bind_evaluation(
        self, submission: EvaluationSubmission
    ) -> TrustedEvaluationBinding:
        self._authorize(submission.caller_identity_claim)
        return self.evaluations[submission.event_id]

    def bind_evaluation_transition(
        self, submission: EvaluationTransitionSubmission
    ) -> TrustedEvaluationTransitionBinding:
        self._authorize(submission.caller_identity_claim)
        return self.transitions[submission.event_id]

    def register_creation(
        self,
        request: (
            RunPendingCreationRequest
            | OutcomeProposedCreationRequest
            | EvaluationPendingCreationRequest
        ),
        context: CreationContext,
    ) -> None:
        if isinstance(request, RunPendingCreationRequest):
            self.runs[request.event_id] = TrustedRunBinding(request, context)
        elif isinstance(request, OutcomeProposedCreationRequest):
            self.outcomes[request.event_id] = TrustedOutcomeBinding(request, context)
        else:
            self.evaluations[request.event_id] = TrustedEvaluationBinding(
                request, context
            )

    def register_transition(
        self,
        request: TransitionRequest[EvaluationState],
        context: TransitionContext,
    ) -> None:
        self.transitions[request.event_id] = TrustedEvaluationTransitionBinding(
            request, context
        )


def facade_for(
    store: SQLiteStore, binder: TrustedFixtureBinder | None = None
) -> GovernanceFacade:
    return GovernanceFacade(
        unit_of_work=LifecycleService(store),
        objectives=store.objectives,
        tasks=store.tasks,
        runs=store.runs,
        outcomes=store.outcomes,
        evaluations=store.evaluations,
        effects=store.effects,
        trusted_binder=binder,
    )


def run_submission(request: RunPendingCreationRequest) -> RunCandidateSubmission:
    scope = request.semantic_input.registration
    assert scope is not None
    assert isinstance(scope.task.snapshot, Task)
    assert isinstance(scope.primary_objective.snapshot, Objective)
    predecessor = None
    if scope.predecessor_lineage:
        predecessor_snapshot = scope.predecessor_lineage[0].snapshot
        assert isinstance(predecessor_snapshot, Run)
        predecessor = reference_of(predecessor_snapshot)
    return RunCandidateSubmission(
        request.event_id,
        request.entity_id,
        request.requested_by,
        request.reason,
        request.timestamp,
        request.correlation_id,
        request.causation_id,
        reference_of(scope.task.snapshot),
        reference_of(scope.primary_objective.snapshot),
        request.entity_spec.execution_profile_ref,
        predecessor,
    )


def outcome_submission(
    request: OutcomeProposedCreationRequest,
) -> OutcomeCandidateSubmission:
    scope = request.semantic_input.proposal
    assert scope is not None
    assert isinstance(scope.originating_run.snapshot, Run)
    prior = None
    if scope.prior_lineage:
        prior_snapshot = scope.prior_lineage[0].snapshot
        assert isinstance(prior_snapshot, Outcome)
        prior = reference_of(prior_snapshot)
    spec = request.entity_spec
    return OutcomeCandidateSubmission(
        request.event_id,
        request.entity_id,
        request.requested_by,
        request.reason,
        request.timestamp,
        request.correlation_id,
        request.causation_id,
        reference_of(scope.originating_run.snapshot),
        spec.producer,
        spec.artifact_refs,
        spec.evidence_refs,
        spec.valid_until,
        prior,
    )


def evaluation_submission(
    request: EvaluationPendingCreationRequest,
) -> EvaluationSubmission:
    scope = request.semantic_input.validation
    assert scope is not None and scope.target_observation is not None
    target_snapshot = scope.target_observation.snapshot
    target: EvaluationTargetReference
    if isinstance(target_snapshot, Run):
        target = reference_of(target_snapshot)
    elif isinstance(target_snapshot, Outcome):
        target = reference_of(target_snapshot)
    else:
        assert isinstance(target_snapshot, Effect)
        target = reference_of(target_snapshot)
    return EvaluationSubmission(
        request.event_id,
        request.entity_id,
        request.requested_by,
        request.reason,
        request.timestamp,
        request.correlation_id,
        request.causation_id,
        target,
        request.entity_spec.method,
        scope.artifact_refs,
        scope.evidence_refs,
        scope.producing_principals,
    )


def transition_submission(
    current: Evaluation,
    target: OutcomeRef,
    request: TransitionRequest[EvaluationState],
    *,
    result_claim: EvaluationResult | None = None,
) -> EvaluationTransitionSubmission:
    return EvaluationTransitionSubmission(
        reference_of(current),
        target,
        request.target_state,
        request.event_id,
        request.actor,
        request.reason,
        request.timestamp,
        request.correlation_id,
        request.causation_id,
        result_claim,
    )


def evaluation_target_ref() -> OutcomeRef:
    assert isinstance(evaluation_fx.TARGET.reference, OutcomeId)
    assert isinstance(evaluation_fx.TARGET.version, EntityVersion)
    return OutcomeRef(evaluation_fx.TARGET.reference, evaluation_fx.TARGET.version)


def test_public_exact_references_cover_all_six_core_entities() -> None:
    values = (
        ObjectiveRef(creation_fx.OBJECTIVE.objective_id, creation_fx.OBJECTIVE.version),
        TaskRef(creation_fx.TASK.task_id, creation_fx.TASK.version),
        RunRef(creation_fx.RUN.run_id, creation_fx.RUN.version),
        OutcomeRef(creation_fx.OUTCOME.outcome_id, creation_fx.OUTCOME.version),
        EvaluationRef(
            evaluation_fx.evaluation().evaluation_id,
            evaluation_fx.evaluation().version,
        ),
        EffectRef(creation_fx.EFFECT.effect_id, creation_fx.EFFECT.version),
    )
    snapshots = (
        creation_fx.OBJECTIVE,
        creation_fx.TASK,
        creation_fx.RUN,
        creation_fx.OUTCOME,
        evaluation_fx.evaluation(),
        creation_fx.EFFECT,
    )
    assert tuple(reference_of(snapshot) for snapshot in snapshots) == values


def test_injected_trusted_binder_permits_legal_candidate_flows() -> None:
    store = SQLiteStore()
    binder = TrustedFixtureBinder(creation_fx.WORKER)
    facade = facade_for(store, binder)
    run_request = creation_fx.run_request()
    seed_related(store, run_request)
    binder.register_creation(run_request, creation_fx.context(run_request))

    run_result = facade.submit_run_candidate(run_submission(run_request))
    assert run_result.snapshot.entity.state is RunState.PENDING

    outcome_request = creation_fx.outcome_request()
    seed_related(store, outcome_request)
    binder.register_creation(outcome_request, creation_fx.context(outcome_request))
    outcome_result = facade.submit_outcome_candidate(
        outcome_submission(outcome_request)
    )
    assert outcome_result.snapshot.entity.state is OutcomeState.PROPOSED
    assert not hasattr(facade, "complete_run")
    assert not hasattr(facade, "accept_outcome")
    store.close()


def test_fresh_privileged_actor_claim_cannot_manufacture_authority() -> None:
    store = SQLiteStore()
    binder = TrustedFixtureBinder(creation_fx.WORKER)
    facade = facade_for(store, binder)
    request = creation_fx.outcome_request()
    seed_related(store, request)
    binder.register_creation(request, creation_fx.context(request))
    forged = ActorIdentity(ActorId.new(), ActorType.SCHEDULER)

    with pytest.raises(AuthorityDeniedError, match="not authenticated"):
        facade.submit_outcome_candidate(
            replace(outcome_submission(request), caller_identity_claim=forged)
        )

    with pytest.raises(NotFoundError):
        facade.read_current(request.entity_id)
    store.close()


def test_public_dtos_cannot_carry_raw_trusted_stage_one_authority() -> None:
    dto_fields = {
        field.name
        for dto in (
            RunCandidateSubmission,
            OutcomeCandidateSubmission,
            EvaluationSubmission,
            EvaluationTransitionSubmission,
        )
        for field in fields(dto)
    }
    assert "context" not in dto_fields
    assert "request" not in dto_fields
    annotations = " ".join(
        repr(get_type_hints(dto))
        for dto in (
            RunCandidateSubmission,
            OutcomeCandidateSubmission,
            EvaluationSubmission,
            EvaluationTransitionSubmission,
        )
    )
    for trusted_type in (
        CreationContext,
        CreationAuthorityDecision,
        TransitionContext,
        TransitionAuthorityDecision,
        EvaluationSemanticGuard,
    ):
        assert trusted_type.__name__ not in annotations

    store = SQLiteStore()
    with pytest.raises(
        InvalidRequestError, match="Expected OutcomeCandidateSubmission"
    ):
        facade_for(store).submit_outcome_candidate(
            creation_fx.outcome_request()  # type: ignore[arg-type]
        )
    store.close()


def test_missing_trusted_binder_fails_closed() -> None:
    store = SQLiteStore()
    request = creation_fx.outcome_request()
    seed_related(store, request)
    with pytest.raises(UnsupportedOperationError, match="trusted governance binder"):
        facade_for(store).submit_outcome_candidate(outcome_submission(request))
    with pytest.raises(NotFoundError):
        facade_for(store).read_current(request.entity_id)
    store.close()


def test_independent_evaluation_request_and_result_use_exact_target() -> None:
    store = SQLiteStore()
    binder = TrustedFixtureBinder(creation_fx.WORKER, evaluation_fx.EVALUATOR)
    facade = facade_for(store, binder)
    request = creation_fx.evaluation_request("outcome")
    seed_related(store, request)
    binder.register_creation(request, creation_fx.context(request))

    pending = facade.submit_evaluation(evaluation_submission(request))
    assert pending.snapshot.entity.state is EvaluationState.PENDING
    assert pending.snapshot.entity.verifier is not None
    assert pending.snapshot.entity.verifier.actor_type is ActorType.EVALUATOR

    running = evaluation_fx.evaluation(
        EvaluationState.RUNNING,
        verifier=evaluation_fx.EVALUATOR,
    )
    seed_snapshot(store, running)
    transition = evaluation_fx.request(running, EvaluationState.COMPLETED)
    context = evaluation_fx.context(
        running,
        transition,
        evaluation_fx.completion_semantics(running),
    )
    binder.register_transition(transition, context)
    completed = facade.advance_evaluation(
        transition_submission(
            running,
            evaluation_target_ref(),
            transition,
            result_claim=evaluation_fx.result(),
        )
    )
    assert completed.snapshot.entity.state is EvaluationState.COMPLETED
    assert completed.snapshot.entity.result is not None
    assert completed.snapshot.entity.result.evidence_refs
    store.close()


def test_authoritative_reads_are_public_and_missing_identity_is_explicit() -> None:
    store = SQLiteStore()
    facade = facade_for(store)
    seed_snapshot(store, creation_fx.OUTCOME)
    assert facade.read_current(creation_fx.OUTCOME.outcome_id) == facade.read(
        reference_of(creation_fx.OUTCOME)
    )
    with pytest.raises(NotFoundError):
        facade.read_current(OutcomeId.new())
    store.close()


def test_real_effect_dispatch_is_explicitly_unavailable() -> None:
    store = SQLiteStore()
    facade = facade_for(store)
    with pytest.raises(UnsupportedOperationError, match="not available"):
        facade.dispatch_effect(EffectRef(EffectId.new(), EntityVersion(1)))
    store.close()


def test_reference_types_reject_cross_family_identities() -> None:
    with pytest.raises(InvalidRequestError, match="exact reference"):
        ObjectiveRef(TaskId.new(), EntityVersion(1))  # type: ignore[arg-type]
    with pytest.raises(InvalidRequestError, match="exact reference"):
        RunRef(ObjectiveId.new(), EntityVersion(1))  # type: ignore[arg-type]
    with pytest.raises(InvalidRequestError, match="exact reference"):
        OutcomeRef(RunId.new(), EntityVersion(1))  # type: ignore[arg-type]
