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
    InvalidRequestError,
    OutcomeRef,
)
from symphony_k.persistence.sqlite import SQLiteStore
from tests import test_creation_run_outcome_evaluation as creation_fx
from tests import test_evaluation_semantic_transitions as evaluation_fx
from tests.persistence_fixtures import advance_fixture, seed_related, seed_snapshot
from tests.test_governance_facade import (
    TrustedFixtureBinder,
    evaluation_submission,
    evaluation_target_ref,
    facade_for,
    outcome_submission,
    run_submission,
    transition_submission,
)


def test_stale_run_version_cannot_back_new_outcome() -> None:
    store = SQLiteStore()
    binder = TrustedFixtureBinder(creation_fx.WORKER)
    facade = facade_for(store, binder)
    request = creation_fx.outcome_request()
    seed_related(store, request)
    binder.register_creation(request, creation_fx.context(request))
    advance_fixture(store, creation_fx.RUN.run_id)

    with pytest.raises(ConflictError, match="differs from durable head"):
        facade.submit_outcome_candidate(outcome_submission(request))
    store.close()


def test_same_predecessor_run_id_with_different_version_is_rejected() -> None:
    store = SQLiteStore()
    binder = TrustedFixtureBinder(creation_fx.WORKER)
    facade = facade_for(store, binder)
    request = creation_fx.run_request(predecessor=True)
    seed_related(store, request)
    binder.register_creation(request, creation_fx.context(request))
    submission = run_submission(request)
    assert submission.predecessor is not None

    with pytest.raises(InvalidRequestError, match="exact public reference"):
        facade.submit_run_candidate(
            replace(
                submission,
                predecessor=replace(
                    submission.predecessor,
                    version=EntityVersion(submission.predecessor.version.value - 1),
                ),
            )
        )
    store.close()


def test_same_prior_outcome_id_with_different_version_is_rejected() -> None:
    store = SQLiteStore()
    binder = TrustedFixtureBinder(creation_fx.WORKER)
    facade = facade_for(store, binder)
    request = creation_fx.outcome_request(prior=True)
    seed_related(store, request)
    binder.register_creation(request, creation_fx.context(request))
    submission = outcome_submission(request)
    assert submission.prior_outcome is not None

    with pytest.raises(InvalidRequestError, match="exact public reference"):
        facade.submit_outcome_candidate(
            replace(
                submission,
                prior_outcome=replace(
                    submission.prior_outcome,
                    version=EntityVersion(submission.prior_outcome.version.value - 1),
                ),
            )
        )
    store.close()


def test_exact_bound_run_and_outcome_lineage_still_succeeds() -> None:
    store = SQLiteStore()
    binder = TrustedFixtureBinder(creation_fx.WORKER)
    facade = facade_for(store, binder)
    run_request = creation_fx.run_request(predecessor=True)
    outcome_request = creation_fx.outcome_request(prior=True)
    seed_related(store, run_request)
    seed_related(store, outcome_request)
    binder.register_creation(run_request, creation_fx.context(run_request))
    binder.register_creation(outcome_request, creation_fx.context(outcome_request))

    run_result = facade.submit_run_candidate(run_submission(run_request))
    outcome_result = facade.submit_outcome_candidate(
        outcome_submission(outcome_request)
    )

    assert run_result.snapshot.entity.predecessor_run_id == creation_fx.RUN.run_id
    assert (
        outcome_result.snapshot.entity.prior_outcome_id
        == creation_fx.OUTCOME.outcome_id
    )
    store.close()


def test_cross_entity_evaluation_target_substitution_fails() -> None:
    store = SQLiteStore()
    binder = TrustedFixtureBinder(creation_fx.WORKER)
    facade = facade_for(store, binder)
    request = creation_fx.evaluation_request("outcome")
    seed_related(store, request)
    binder.register_creation(request, creation_fx.context(request))

    with pytest.raises(InvalidRequestError, match="changed caller-controlled"):
        facade.submit_evaluation(
            replace(
                evaluation_submission(request),
                target=OutcomeRef(OutcomeId.new(), creation_fx.OUTCOME.version),
            )
        )
    store.close()


def test_superseded_candidate_is_not_eligible_as_current_submission_target() -> None:
    store = SQLiteStore()
    binder = TrustedFixtureBinder(creation_fx.WORKER)
    facade = facade_for(store, binder)
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
        target_observation=replace(scope.target_observation, snapshot=superseded),
    )
    changed = creation_fx.with_evaluation_scope(
        replace(request, entity_spec=changed_spec), changed_scope
    )
    seed_related(store, changed)
    binder.register_creation(changed, creation_fx.context(changed))

    with pytest.raises(ConflictError, match="Superseded"):
        facade.submit_evaluation(evaluation_submission(changed))
    store.close()


def test_identical_creation_replay_survives_related_head_advancement() -> None:
    store = SQLiteStore()
    binder = TrustedFixtureBinder(creation_fx.WORKER)
    facade = facade_for(store, binder)
    request = creation_fx.outcome_request()
    seed_related(store, request)
    binder.register_creation(request, creation_fx.context(request))
    submission = outcome_submission(request)

    first = facade.submit_outcome_candidate(submission)
    advance_fixture(store, creation_fx.RUN.run_id)
    replay = facade.submit_outcome_candidate(submission)

    assert replay == first
    assert len(store.events.for_entity(request.entity_id)) == 1
    store.close()


def test_evaluation_replay_and_optimistic_concurrency_are_preserved() -> None:
    store = SQLiteStore()
    binder = TrustedFixtureBinder(evaluation_fx.EVALUATOR)
    facade = facade_for(store, binder)
    pending = evaluation_fx.evaluation(verifier=evaluation_fx.EVALUATOR)
    seed_snapshot(store, pending)
    transition = evaluation_fx.request(pending, EvaluationState.RUNNING)
    context = evaluation_fx.context(
        pending, transition, evaluation_fx.start_semantics(pending)
    )
    binder.register_transition(transition, context)
    submission = transition_submission(pending, evaluation_target_ref(), transition)

    first = facade.advance_evaluation(submission)
    replay = facade.advance_evaluation(submission)
    assert replay == first

    conflict_request = replace(transition, event_id=EventId.new())
    conflict_context = evaluation_fx.context(
        pending, conflict_request, evaluation_fx.start_semantics(pending)
    )
    binder.register_transition(conflict_request, conflict_context)
    conflict = transition_submission(pending, evaluation_target_ref(), conflict_request)
    with pytest.raises(ConflictError, match="Stored version"):
        facade.advance_evaluation(conflict)
    assert store.evaluations.load(pending.evaluation_id).version == EntityVersion(8)
    store.close()


def test_evaluation_transition_rejects_target_substitution() -> None:
    store = SQLiteStore()
    binder = TrustedFixtureBinder(evaluation_fx.EVALUATOR)
    facade = facade_for(store, binder)
    pending = evaluation_fx.evaluation(verifier=evaluation_fx.EVALUATOR)
    seed_snapshot(store, pending)
    transition = evaluation_fx.request(pending, EvaluationState.RUNNING)
    binder.register_transition(
        transition,
        evaluation_fx.context(
            pending, transition, evaluation_fx.start_semantics(pending)
        ),
    )
    assert isinstance(evaluation_fx.TARGET.version, EntityVersion)

    with pytest.raises(InvalidRequestError, match="persisted Evaluation"):
        facade.advance_evaluation(
            transition_submission(
                pending,
                OutcomeRef(OutcomeId.new(), evaluation_fx.TARGET.version),
                transition,
            )
        )
    store.close()


def test_evaluation_completion_cannot_replace_caller_result_claim() -> None:
    store = SQLiteStore()
    binder = TrustedFixtureBinder(evaluation_fx.EVALUATOR)
    facade = facade_for(store, binder)
    running = evaluation_fx.evaluation(
        EvaluationState.RUNNING, verifier=evaluation_fx.EVALUATOR
    )
    seed_snapshot(store, running)
    transition = evaluation_fx.request(running, EvaluationState.COMPLETED)
    binder.register_transition(
        transition,
        evaluation_fx.context(
            running, transition, evaluation_fx.completion_semantics(running)
        ),
    )

    with pytest.raises(InvalidRequestError, match="result claim"):
        facade.advance_evaluation(
            transition_submission(
                running,
                evaluation_target_ref(),
                transition,
                result_claim=evaluation_fx.different_result(),
            )
        )
    assert store.evaluations.load(running.evaluation_id) == running
    store.close()
