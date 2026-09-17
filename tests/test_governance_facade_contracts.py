"""Replay, stale-binding, substitution, and concurrency facade contracts."""

from dataclasses import replace

import pytest

from symphony_k.domain import (
    EntityVersion,
    EvaluationState,
    EventId,
    OutcomeId,
    OutcomeState,
)
from symphony_k.governance import (
    ConflictError,
    EvaluationSubmission,
    EvaluationTransitionSubmission,
    GovernanceFacade,
    InvalidRequestError,
    OutcomeCandidateSubmission,
    OutcomeRef,
    reference_of,
)
from symphony_k.persistence.service import LifecycleService
from symphony_k.persistence.sqlite import SQLiteStore
from tests import test_creation_run_outcome_evaluation as creation_fx
from tests import test_evaluation_semantic_transitions as evaluation_fx
from tests.persistence_fixtures import advance_fixture, seed_related, seed_snapshot


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


def test_stale_run_version_cannot_back_new_outcome() -> None:
    store = SQLiteStore()
    facade = facade_for(store)
    request = creation_fx.outcome_request()
    seed_related(store, request)
    advance_fixture(store, creation_fx.RUN.run_id)

    with pytest.raises(ConflictError, match="differs from durable head"):
        facade.submit_outcome_candidate(
            OutcomeCandidateSubmission(
                request,
                creation_fx.context(request),
                reference_of(creation_fx.RUN),
            )
        )
    store.close()


def test_cross_entity_evaluation_target_substitution_fails() -> None:
    store = SQLiteStore()
    facade = facade_for(store)
    request = creation_fx.evaluation_request("outcome")
    seed_related(store, request)

    with pytest.raises(InvalidRequestError, match="exact target"):
        facade.submit_evaluation(
            EvaluationSubmission(
                request,
                creation_fx.context(request),
                OutcomeRef(OutcomeId.new(), creation_fx.OUTCOME.version),
            )
        )
    store.close()


def test_superseded_candidate_is_not_eligible_as_current_submission_target() -> None:
    store = SQLiteStore()
    facade = facade_for(store)
    request = creation_fx.evaluation_request("outcome")
    scope = request.semantic_input.validation
    assert scope is not None and scope.target_observation is not None
    superseded = replace(
        creation_fx.OUTCOME,
        state=OutcomeState.SUPERSEDED,
        version=creation_fx.OUTCOME.version.next(),
        superseded_by_outcome_id=OutcomeId.new(),
    )
    target = request.entity_spec.target
    changed_spec = replace(
        request.entity_spec,
        target=type(target)(superseded.outcome_id, superseded.version),
    )
    changed_scope = replace(
        scope,
        spec=changed_spec,
        target_observation=replace(
            scope.target_observation,
            snapshot=superseded,
        ),
    )
    changed = creation_fx.with_evaluation_scope(
        replace(request, entity_spec=changed_spec),
        changed_scope,
    )
    seed_related(store, changed)

    with pytest.raises(ConflictError, match="Superseded"):
        facade.submit_evaluation(
            EvaluationSubmission(
                changed,
                creation_fx.context(changed),
                reference_of(superseded),
            )
        )
    store.close()


def test_identical_creation_replay_survives_related_head_advancement() -> None:
    store = SQLiteStore()
    facade = facade_for(store)
    request = creation_fx.outcome_request()
    seed_related(store, request)
    submission = OutcomeCandidateSubmission(
        request,
        creation_fx.context(request),
        reference_of(creation_fx.RUN),
    )

    first = facade.submit_outcome_candidate(submission)
    advance_fixture(store, creation_fx.RUN.run_id)
    replay = facade.submit_outcome_candidate(submission)

    assert replay == first
    assert len(store.events.for_entity(request.entity_id)) == 1
    store.close()


def test_evaluation_replay_and_optimistic_concurrency_are_preserved() -> None:
    store = SQLiteStore()
    facade = facade_for(store)
    pending = evaluation_fx.evaluation(verifier=evaluation_fx.EVALUATOR)
    seed_snapshot(store, pending)
    transition = evaluation_fx.request(pending, EvaluationState.RUNNING)
    submission = EvaluationTransitionSubmission(
        reference_of(pending),
        evaluation_target_ref(),
        transition,
        evaluation_fx.context(
            pending,
            transition,
            evaluation_fx.start_semantics(pending),
        ),
    )

    first = facade.advance_evaluation(submission)
    replay = facade.advance_evaluation(submission)
    assert replay == first

    conflict_request = replace(transition, event_id=EventId.new())
    conflict = EvaluationTransitionSubmission(
        reference_of(pending),
        submission.target,
        conflict_request,
        evaluation_fx.context(
            pending,
            conflict_request,
            evaluation_fx.start_semantics(pending),
        ),
    )
    with pytest.raises(ConflictError, match="Stored version"):
        facade.advance_evaluation(conflict)
    assert store.evaluations.load(pending.evaluation_id).version == EntityVersion(8)
    store.close()


def test_evaluation_transition_rejects_target_substitution() -> None:
    store = SQLiteStore()
    facade = facade_for(store)
    pending = evaluation_fx.evaluation(verifier=evaluation_fx.EVALUATOR)
    seed_snapshot(store, pending)
    transition = evaluation_fx.request(pending, EvaluationState.RUNNING)
    assert isinstance(evaluation_fx.TARGET.version, EntityVersion)

    with pytest.raises(InvalidRequestError, match="persisted Evaluation"):
        facade.advance_evaluation(
            EvaluationTransitionSubmission(
                reference_of(pending),
                OutcomeRef(OutcomeId.new(), evaluation_fx.TARGET.version),
                transition,
                evaluation_fx.context(
                    pending,
                    transition,
                    evaluation_fx.start_semantics(pending),
                ),
            )
        )
    store.close()
