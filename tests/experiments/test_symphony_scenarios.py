"""G5-G8 and H1-H5 against accepted Stage 1 plus the thin facade."""

import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from threading import Barrier

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from experiments.governance_layer_validation import (  # noqa: E402
    FakeExternalSystem,
    GovernanceFacade,
    HumanAuthorization,
    Port,
    issue_test_ports,
)
from symphony_k.domain import (  # noqa: E402
    ActorId,
    ActorIdentity,
    ActorType,
    Effect,
    EffectAuthorizationStatus,
    EffectCompensationStartSemantics,
    EffectState,
    Evaluation,
    EvaluationConfidence,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationState,
    EventId,
    EvidenceRef,
    Outcome,
    OutcomeState,
    UnauthorizedTransition,
)
from symphony_k.persistence.service import LifecycleService  # noqa: E402
from symphony_k.persistence.sqlite import SQLiteStore  # noqa: E402
from tests import (
    test_effect_observation_quarantine_semantic_transitions as occurrence_fx,  # noqa: E402
)
from tests import (
    test_effect_remediation_semantic_transitions as remediation_fx,  # noqa: E402
)
from tests import (
    test_evaluation_semantic_transitions as evaluation_fx,  # noqa: E402
)
from tests import (
    test_outcome_disposition_semantic_transitions as outcome_fx,  # noqa: E402
)
from tests.persistence_fixtures import seed_related, seed_snapshot  # noqa: E402
from tests.test_creation_integrated import creation_context  # noqa: E402
from tests.test_creation_objective_task import objective_request  # noqa: E402
from tests.test_creation_run_outcome_evaluation import (  # noqa: E402
    independent_evaluation_request,
    outcome_request,
)
from tests.test_persistence_service import objective_transition  # noqa: E402


def setup() -> tuple[GovernanceFacade, tuple[Port, Port, Port, Port], SQLiteStore]:
    store = SQLiteStore()
    ports = issue_test_ports()
    return GovernanceFacade(store, ports), ports, store


def human_authorization(current: Effect) -> HumanAuthorization:
    return HumanAuthorization(
        current.effect_id,
        current.version,
        current.target_ref,
        current.payload_ref,
        occurrence_fx.CORRELATION,
        ActorIdentity(ActorId.new(), ActorType.HUMAN_OPERATOR),
        "human-approval:issue-85-fixture",
    )


def seed_disposition_evaluation(store: SQLiteStore, snapshot: Outcome) -> Evaluation:
    observed = outcome_fx.semantics(snapshot, OutcomeState.ACCEPTED).evaluation
    assert observed.effective_use.original_judgement is not None
    result = EvaluationResult(
        observed.effective_use.original_judgement,
        EvaluationConfidence("high"),
        "Exact deterministic strategic fixture.",
        frozenset({EvidenceRef("evidence:strategic-binding")}),
    )
    evaluation = Evaluation(
        observed.evaluation_id,
        observed.observed_state,
        observed.observed_evaluation_version,
        observed.target,
        EvaluationMethodRef("strategic", "1"),
        observed.verifier,
        result,
    )
    seed_snapshot(store, evaluation)
    return evaluation


def bind_human_authorization(
    facade: GovernanceFacade,
    ports: tuple[Port, Port, Port, Port],
    store: SQLiteStore,
    effect: Effect,
) -> HumanAuthorization:
    outcome = outcome_fx.outcome()
    seed_snapshot(store, outcome)
    evaluation = seed_disposition_evaluation(store, outcome)
    request = replace(
        outcome_fx.request(outcome, OutcomeState.ACCEPTED), event_id=EventId.new()
    )
    facade.apply_transition(
        ports[2], outcome.outcome_id, request, outcome_fx.context(outcome, request)
    )
    authorization = human_authorization(effect)
    facade.bind_authorization_evidence(
        ports[3], authorization, outcome.outcome_id, evaluation.evaluation_id
    )
    return authorization


def test_g5_replay_returns_original_receipt_without_fresh_authority() -> None:
    facade, ports, store = setup()
    snapshot = outcome_fx.outcome()
    seed_snapshot(store, snapshot)
    seed_disposition_evaluation(store, snapshot)
    request = outcome_fx.request(snapshot, OutcomeState.ACCEPTED)
    context = outcome_fx.context(snapshot, request)
    first = facade.apply_transition(ports[2], snapshot.outcome_id, request, context)
    replay = facade.apply_transition(ports[2], snapshot.outcome_id, request, context)
    assert replay == first
    assert store.outcomes.load(snapshot.outcome_id).version == first.entity.version
    assert len(store.events.for_entity(snapshot.outcome_id)) == 2


def test_g6_commit_without_exact_human_authorization_is_rejected() -> None:
    facade, ports, store = setup()
    current = occurrence_fx.effect(EffectState.PLANNED)
    seed_snapshot(store, current)
    request = occurrence_fx.request(current, EffectState.COMMITTED)
    context = occurrence_fx.context(
        current,
        request,
        occurrence_fx.confirmed_semantics(
            current, EffectAuthorizationStatus.AUTHORIZED
        ),
    )
    fake = FakeExternalSystem()
    with pytest.raises(UnauthorizedTransition, match="Human authorization"):
        facade.commit_effect(
            ports[3],
            fake,
            None,
            "operation:a",
            request,
            context,
        )
    assert fake.state(current.target_ref.value) is None


def test_nonblank_but_unbound_authorization_evidence_is_rejected() -> None:
    facade, ports, store = setup()
    current = occurrence_fx.effect(EffectState.PLANNED)
    seed_snapshot(store, current)
    request = occurrence_fx.request(current, EffectState.COMMITTED)
    fake = FakeExternalSystem()
    with pytest.raises(UnauthorizedTransition, match="trusted evidence binding"):
        facade.commit_effect(
            ports[3],
            fake,
            human_authorization(current),
            "operation:unbound",
            request,
            occurrence_fx.context(
                current,
                request,
                occurrence_fx.confirmed_semantics(
                    current, EffectAuthorizationStatus.AUTHORIZED
                ),
            ),
        )
    assert fake.state(current.target_ref.value) is None


def test_g7_confirmed_occurrence_cannot_be_rewritten_out_of_history() -> None:
    facade, ports, store = setup()
    current = occurrence_fx.effect(EffectState.PLANNED)
    seed_snapshot(store, current)
    request = occurrence_fx.request(current, EffectState.COMMITTED)
    context = occurrence_fx.context(
        current,
        request,
        occurrence_fx.confirmed_semantics(
            current, EffectAuthorizationStatus.AUTHORIZED
        ),
    )
    facade.commit_effect(
        ports[3],
        FakeExternalSystem(),
        bind_human_authorization(facade, ports, store, current),
        "operation:a",
        request,
        context,
    )
    with pytest.raises(sqlite3.IntegrityError, match="append-only history"):
        store._connection.execute(
            "DELETE FROM events WHERE entity_id = ?", (str(current.effect_id),)
        )
    assert store.effects.load(current.effect_id).state is EffectState.COMMITTED


def test_g8_two_stale_writers_have_exactly_one_winner(tmp_path: Path) -> None:
    database = str(tmp_path / "g8.sqlite")
    initial = SQLiteStore(database)
    creation = objective_request()
    LifecycleService(initial).create(creation, creation_context(creation))
    initial.close()
    barrier = Barrier(2)

    def write() -> str:
        store = SQLiteStore(database)
        snapshot = store.objectives.load(creation.entity_id)
        request, context = objective_transition(snapshot)
        barrier.wait(timeout=10)
        try:
            LifecycleService(store).transition(snapshot.objective_id, request, context)
            return "updated"
        except Exception:
            return "conflict"
        finally:
            store.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = (pool.submit(write), pool.submit(write))
        assert sorted(future.result(timeout=10) for future in futures) == [
            "conflict",
            "updated",
        ]


def test_h1_legitimate_candidate_recording() -> None:
    facade, ports, store = setup()
    request = outcome_request()
    seed_related(store, request)
    result = facade.submit_creation(ports[0], request, creation_context(request))
    assert result.entity.state is OutcomeState.PROPOSED


def test_h2_independent_exact_candidate_evaluation_request() -> None:
    facade, ports, store = setup()
    request = independent_evaluation_request("outcome")
    seed_related(store, request)
    created = facade.submit_creation(ports[1], request, creation_context(request))
    assert isinstance(created.entity, Evaluation)
    assert created.entity.verifier is not None
    start_request = evaluation_fx.request(
        created.entity, EvaluationState.RUNNING, actor=created.entity.verifier
    )
    started = facade.apply_transition(
        ports[1],
        created.entity.evaluation_id,
        start_request,
        evaluation_fx.context(
            created.entity,
            start_request,
            evaluation_fx.start_semantics(
                created.entity, verifier=created.entity.verifier
            ),
        ),
    )
    assert isinstance(started.entity, Evaluation)
    finish_request = replace(
        evaluation_fx.request(
            started.entity,
            EvaluationState.COMPLETED,
            actor=started.entity.verifier,
        ),
        event_id=EventId.new(),
    )
    completed = facade.apply_transition(
        ports[1],
        started.entity.evaluation_id,
        finish_request,
        evaluation_fx.context(
            started.entity,
            finish_request,
            evaluation_fx.completion_semantics(started.entity),
        ),
    )
    assert isinstance(completed.entity, Evaluation)
    assert completed.entity.state is EvaluationState.COMPLETED
    assert completed.entity.result is not None
    assert completed.entity.result.evidence_refs


def test_h3_current_evidence_disposition() -> None:
    facade, ports, store = setup()
    snapshot = outcome_fx.outcome()
    seed_snapshot(store, snapshot)
    seed_disposition_evaluation(store, snapshot)
    request = outcome_fx.request(snapshot, OutcomeState.ACCEPTED)
    result = facade.apply_transition(
        ports[2], snapshot.outcome_id, request, outcome_fx.context(snapshot, request)
    )
    assert result.entity.state is OutcomeState.ACCEPTED


def test_h4_human_authorized_gateway_commit_has_receipt_and_occurrence(
    tmp_path: Path,
) -> None:
    database = str(tmp_path / "h4.sqlite")
    store = SQLiteStore(database)
    ports = issue_test_ports()
    facade = GovernanceFacade(store, ports)
    current = occurrence_fx.effect(EffectState.PLANNED)
    seed_snapshot(store, current)
    request = occurrence_fx.request(current, EffectState.COMMITTED)
    context = occurrence_fx.context(
        current,
        request,
        occurrence_fx.confirmed_semantics(
            current, EffectAuthorizationStatus.AUTHORIZED
        ),
    )
    external = FakeExternalSystem()
    result = facade.commit_effect(
        ports[3],
        external,
        bind_human_authorization(facade, ports, store, current),
        "operation:a",
        request,
        context,
    )
    packet = facade.export_audit(ports[3], current.effect_id)
    assert result.entity.state is EffectState.COMMITTED
    assert current.payload_ref is not None
    assert external.state(current.target_ref.value) == current.payload_ref.value
    records = packet["integration_records"]
    assert isinstance(records, tuple)
    assert {item["kind"] for item in records if isinstance(item, dict)} == {
        "authorization_evidence_binding",
        "human_authorization",
        "external_receipt",
    }
    bindings = packet["authorization_bindings"]
    assert isinstance(bindings, tuple) and len(bindings) == 1
    store.close()
    reopened = SQLiteStore(database)
    reopened_facade = GovernanceFacade(reopened, ports)
    reopened_packet = reopened_facade.export_audit(ports[3], current.effect_id)
    assert reopened_packet["integration_records"] == packet["integration_records"]
    assert reopened.effects.load(current.effect_id).state is EffectState.COMMITTED
    reopened.close()


def test_h5_compensation_preserves_original_occurrence() -> None:
    facade, ports, store = setup()
    planned = remediation_fx.effect(EffectState.PLANNED)
    seed_snapshot(store, planned)
    commit_request = occurrence_fx.request(planned, EffectState.COMMITTED)
    commit_semantics = occurrence_fx.confirmed_semantics(
        planned, EffectAuthorizationStatus.AUTHORIZED
    )
    committed_result = facade.commit_effect(
        ports[3],
        FakeExternalSystem(),
        bind_human_authorization(facade, ports, store, planned),
        "operation:compensate",
        commit_request,
        occurrence_fx.context(
            planned,
            commit_request,
            commit_semantics,
        ),
    )
    assert isinstance(committed_result.entity, Effect)
    committed = committed_result.entity
    plan = remediation_fx.compensation_plan(committed)
    start_semantics = EffectCompensationStartSemantics(
        commit_semantics.observation,
        plan,
        remediation_fx.authorization(
            remediation_fx.authorization_scope(committed, plan=plan)
        ),
    )
    start_request = remediation_fx.request(committed, EffectState.COMPENSATING)
    start_request = replace(start_request, event_id=EventId.new())
    started = facade.apply_transition(
        ports[3],
        committed.effect_id,
        start_request,
        remediation_fx.context(
            committed,
            start_request,
            start_semantics,
        ),
    )
    assert isinstance(started.entity, Effect)
    finish_request = remediation_fx.request(
        started.entity,
        EffectState.COMPENSATED,
        controller=remediation_fx.COMPLETION_CONTROLLER,
        event_id=remediation_fx.OTHER,
    )
    completion_semantics = replace(
        remediation_fx.completion_semantics(started.entity, plan),
        original_commit_observation=commit_semantics.observation,
    )
    completed = facade.apply_transition(
        ports[3],
        committed.effect_id,
        finish_request,
        remediation_fx.context(
            started.entity,
            finish_request,
            completion_semantics,
            start_event=started.event,
        ),
    )
    assert completed.entity.state is EffectState.COMPENSATED
    events = store.events.for_entity(committed.effect_id)
    assert [event.event_type.name for event in events][-3:] == [
        "EFFECT_COMMITTED",
        "EFFECT_COMPENSATION_STARTED",
        "EFFECT_COMPENSATED",
    ]
