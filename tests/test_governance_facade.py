"""Public G1/M1 facade operations over the accepted Stage 1 kernel."""

from dataclasses import replace

import pytest

from symphony_k.domain import (
    ActorType,
    EffectId,
    EntityVersion,
    EvaluationState,
    ObjectiveId,
    OutcomeId,
    OutcomeState,
    RunId,
    RunState,
    TaskId,
)
from symphony_k.governance import (
    AuthorityDeniedError,
    EffectRef,
    EvaluationRef,
    EvaluationSubmission,
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
    UnsupportedOperationError,
    reference_of,
)
from symphony_k.persistence.service import LifecycleService
from symphony_k.persistence.sqlite import SQLiteStore
from tests import test_creation_run_outcome_evaluation as creation_fx
from tests import test_evaluation_semantic_transitions as evaluation_fx
from tests.persistence_fixtures import seed_related, seed_snapshot


def facade_for(store: SQLiteStore) -> GovernanceFacade:
    return GovernanceFacade(
        unit_of_work=LifecycleService(store),
        objectives=store.objectives,
        tasks=store.tasks,
        runs=store.runs,
        outcomes=store.outcomes,
        evaluations=store.evaluations,
        effects=store.effects,
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


def test_run_and_outcome_submission_remain_non_authoritative_candidates() -> None:
    store = SQLiteStore()
    facade = facade_for(store)
    run_request = creation_fx.run_request()
    seed_related(store, run_request)

    run_result = facade.submit_run_candidate(
        RunCandidateSubmission(
            run_request,
            creation_fx.context(run_request),
            reference_of(creation_fx.TASK),
            reference_of(creation_fx.OBJECTIVE),
        )
    )
    assert run_result.snapshot.entity.state is RunState.PENDING

    outcome_request = creation_fx.outcome_request()
    seed_related(store, outcome_request)
    outcome_result = facade.submit_outcome_candidate(
        OutcomeCandidateSubmission(
            outcome_request,
            creation_fx.context(outcome_request),
            reference_of(creation_fx.RUN),
        )
    )
    assert outcome_result.snapshot.entity.state is OutcomeState.PROPOSED
    assert not hasattr(facade, "complete_run")
    assert not hasattr(facade, "accept_outcome")
    store.close()


def test_worker_identity_relabel_cannot_create_candidate_authority() -> None:
    store = SQLiteStore()
    facade = facade_for(store)
    request = creation_fx.outcome_request()
    seed_related(store, request)
    forged_authority = replace(
        creation_fx.WORKER,
        actor_type=ActorType.SCHEDULER,
    )

    with pytest.raises(AuthorityDeniedError) as caught:
        facade.submit_outcome_candidate(
            OutcomeCandidateSubmission(
                request,
                creation_fx.context(request, forged_authority),
                reference_of(creation_fx.RUN),
            )
        )

    assert caught.value.__cause__ is caught.value.domain_error
    assert not hasattr(facade, "_connection")
    with pytest.raises(NotFoundError):
        facade.read_current(request.entity_id)
    store.close()


def test_independent_evaluation_request_and_result_use_exact_target() -> None:
    store = SQLiteStore()
    facade = facade_for(store)
    request = creation_fx.evaluation_request("outcome")
    seed_related(store, request)

    pending = facade.submit_evaluation(
        EvaluationSubmission(
            request,
            creation_fx.context(request),
            reference_of(creation_fx.OUTCOME),
        )
    )
    assert pending.snapshot.entity.state is EvaluationState.PENDING
    assert pending.snapshot.entity.verifier is not None
    assert pending.snapshot.entity.verifier.actor_type is ActorType.EVALUATOR

    running = evaluation_fx.evaluation(
        EvaluationState.RUNNING,
        verifier=evaluation_fx.EVALUATOR,
    )
    seed_snapshot(store, running)
    transition = evaluation_fx.request(running, EvaluationState.COMPLETED)
    completed = facade.advance_evaluation(
        EvaluationTransitionSubmission(
            reference_of(running),
            evaluation_target_ref(),
            transition,
            evaluation_fx.context(
                running,
                transition,
                evaluation_fx.completion_semantics(running),
            ),
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

    current = facade.read_current(creation_fx.OUTCOME.outcome_id)
    exact = facade.read(reference_of(creation_fx.OUTCOME))
    assert current == exact
    assert current.entity == creation_fx.OUTCOME
    assert not hasattr(facade, "_connection")

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
