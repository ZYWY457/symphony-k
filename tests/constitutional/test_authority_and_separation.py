"""Workers request; independent authorities decide; entity states stay distinct."""

from dataclasses import replace
from itertools import product

import pytest

from symphony_k.domain import (
    ActorType,
    ConcurrencyConflict,
    CreationRequestVariant,
    EffectState,
    Evaluation,
    EvaluationConfidence,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationState,
    EvaluationVerdict,
    ObjectiveState,
    Outcome,
    OutcomeState,
    RunState,
    TaskState,
    UnauthorizedTransition,
    can_effect_transition,
    can_evaluation_transition,
    can_objective_transition,
    can_outcome_transition,
    can_run_transition,
    can_task_transition,
    create_entity,
)
from symphony_k.persistence.service import LifecycleService
from symphony_k.persistence.sqlite import SQLiteStore
from tests import test_outcome_disposition_semantic_transitions as outcome_fixtures
from tests import test_run_semantic_transitions as run_fixtures
from tests.persistence_fixtures import data_rows, seed_related, seed_snapshot
from tests.test_creation_integrated import CASES, creation_context
from tests.test_creation_objective_task import task_request
from tests.test_creation_run_outcome_evaluation import (
    context as creator_context,
)
from tests.test_creation_run_outcome_evaluation import (
    independent_evaluation_request,
)


def disposition_evaluation(outcome: Outcome) -> Evaluation:
    observation = outcome_fixtures.semantics(outcome, OutcomeState.ACCEPTED).evaluation
    original = observation.effective_use.original_judgement
    assert original is not None
    return Evaluation(
        observation.evaluation_id,
        observation.observed_state,
        observation.observed_evaluation_version,
        observation.target,
        EvaluationMethodRef("constitutional-evaluator", "1"),
        observation.verifier,
        EvaluationResult(
            original,
            EvaluationConfidence("independently checked"),
            "Original independently recorded judgement",
        ),
    )


def test_worker_cannot_complete_own_run() -> None:
    store = SQLiteStore()
    run = run_fixtures.run(RunState.RUNNING)
    seed_snapshot(store, run)
    request = run_fixtures.request(RunState.COMPLETED)
    worker = replace(request.actor, actor_type=ActorType.WORKER)
    request = replace(request, actor=worker)
    context = run_fixtures.context(
        run,
        request,
        run_fixtures.canonical_guard(
            run, RunState.COMPLETED, run_fixtures.direct_completion_semantics()
        ),
    )
    before = data_rows(store)
    with pytest.raises(UnauthorizedTransition):
        LifecycleService(store).transition(run.run_id, request, context)
    assert data_rows(store) == before
    store.close()


def test_worker_cannot_accept_own_outcome() -> None:
    store = SQLiteStore()
    outcome = outcome_fixtures.outcome()
    seed_snapshot(store, outcome)
    request = outcome_fixtures.request(
        outcome, OutcomeState.ACCEPTED, actor=outcome.producer
    )
    before = data_rows(store)
    with pytest.raises(UnauthorizedTransition):
        LifecycleService(store).transition(
            outcome.outcome_id, request, outcome_fixtures.context(outcome, request)
        )
    assert data_rows(store) == before
    store.close()


def test_run_completion_does_not_accept_outcome() -> None:
    store = SQLiteStore()
    run = run_fixtures.run(RunState.RUNNING)
    seed_snapshot(store, run)
    candidate = create_entity(CASES[3], creation_context(CASES[3])).entity
    assert isinstance(candidate, Outcome)
    candidate = replace(candidate, run_id=run.run_id)
    seed_snapshot(store, candidate)
    request = run_fixtures.request(RunState.COMPLETED)
    context = run_fixtures.context(
        run,
        request,
        run_fixtures.canonical_guard(
            run, RunState.COMPLETED, run_fixtures.direct_completion_semantics()
        ),
    )
    result = LifecycleService(store).transition(run.run_id, request, context)
    assert result.entity.state is RunState.COMPLETED
    assert store.outcomes.load(candidate.outcome_id) == candidate
    assert candidate.state is OutcomeState.PROPOSED
    store.close()


def test_outcome_acceptance_does_not_satisfy_objective_automatically() -> None:
    store = SQLiteStore()
    outcome = outcome_fixtures.outcome()
    seed_snapshot(store, outcome)
    seed_snapshot(store, disposition_evaluation(outcome))
    run = store.runs.load(outcome.run_id)
    task = store.tasks.load(run.task_id)
    objective = store.objectives.load(task.primary_objective_id)
    request = outcome_fixtures.request(outcome, OutcomeState.ACCEPTED)
    result = LifecycleService(store).transition(
        outcome.outcome_id, request, outcome_fixtures.context(outcome, request)
    )
    assert result.entity.state is OutcomeState.ACCEPTED
    assert store.objectives.load(objective.objective_id) == objective
    assert objective.state is not ObjectiveState.SATISFIED
    assert store.tasks.load(task.task_id) == task
    store.close()


@pytest.mark.parametrize("attack", ["stale", "judgement"])
def test_outcome_acceptance_uses_authoritative_evaluation_truth(attack: str) -> None:
    store = SQLiteStore()
    outcome = outcome_fixtures.outcome()
    seed_snapshot(store, outcome)
    evaluation = disposition_evaluation(outcome)
    if attack == "stale":
        evaluation = replace(
            evaluation,
            version=evaluation.version.next(),
            state=EvaluationState.CONFLICTED,
        )
    else:
        assert evaluation.result is not None
        evaluation = replace(
            evaluation,
            result=replace(
                evaluation.result,
                verdict=EvaluationVerdict("Different recorded judgement"),
            ),
        )
    seed_snapshot(store, evaluation)
    request = outcome_fixtures.request(outcome, OutcomeState.ACCEPTED)
    before = data_rows(store)
    with pytest.raises(ConcurrencyConflict):
        LifecycleService(store).transition(
            outcome.outcome_id, request, outcome_fixtures.context(outcome, request)
        )
    assert data_rows(store) == before
    store.close()


def test_secondary_objective_link_does_not_propagate_state() -> None:
    store = SQLiteStore()
    request = task_request()
    ids = seed_related(store, request)
    before = tuple(store.load(identity) for identity in ids)
    assert request.entity_spec.contributes_to
    created = LifecycleService(store).create(request, creation_context(request))
    assert created.entity.state is TaskState.DRAFT
    assert tuple(store.load(identity) for identity in ids) == before
    store.close()


def test_creation_none_is_absence_not_state() -> None:
    for request in CASES:
        result = create_entity(request, creation_context(request))
        assert result.event.metadata.prior_state is None
        assert all(state.name != "NONE" for state in type(result.entity.state))
        assert not hasattr(request, "expected_version")


def test_exactly_43_states() -> None:
    families = (
        ObjectiveState,
        TaskState,
        RunState,
        OutcomeState,
        EvaluationState,
        EffectState,
    )
    assert tuple(len(family) for family in families) == (8, 7, 8, 6, 6, 8)
    assert sum(map(len, families)) == 43


def test_exactly_99_lifecycle_edges() -> None:
    counts = (
        sum(
            can_objective_transition(a, b) for a, b in product(ObjectiveState, repeat=2)
        ),
        sum(can_task_transition(a, b) for a, b in product(TaskState, repeat=2)),
        sum(can_run_transition(a, b) for a, b in product(RunState, repeat=2)),
        sum(can_outcome_transition(a, b) for a, b in product(OutcomeState, repeat=2)),
        sum(
            can_evaluation_transition(a, b)
            for a, b in product(EvaluationState, repeat=2)
        ),
        sum(can_effect_transition(a, b) for a, b in product(EffectState, repeat=2)),
    )
    assert counts == (17, 16, 18, 11, 10, 19)
    assert len(CreationRequestVariant) == 8
    assert sum(counts) + len(CreationRequestVariant) == 99


def test_worker_relabel_cannot_acquire_creation_authority() -> None:
    store = SQLiteStore()
    request = independent_evaluation_request("evidence")
    validation = request.semantic_input.validation
    assert validation is not None
    producer = validation.producing_principals[0]
    assert producer.actor_id != request.requested_by.actor_id
    forged = replace(producer, actor_type=ActorType.EVALUATOR)
    before = data_rows(store)
    with pytest.raises(UnauthorizedTransition, match="relabelling"):
        LifecycleService(store).create(request, creator_context(request, forged))
    assert data_rows(store) == before
    assert (
        LifecycleService(store).create(request, creation_context(request)).entity.state
        is EvaluationState.PENDING
    )
    store.close()


def test_system_is_not_creation_superuser() -> None:
    for request in CASES:
        context = creation_context(request)
        authority = context.authority_decision
        assert authority is not None
        forged = replace(authority.decided_by, actor_type=ActorType.SYSTEM)
        with pytest.raises(UnauthorizedTransition):
            create_entity(request, creator_context(request, forged))
