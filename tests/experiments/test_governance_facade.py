"""Issue #85 thin-boundary adversarial probes independent of production source."""

import sys
from dataclasses import replace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from experiments.governance_layer_validation import (  # noqa: E402
    GovernanceFacade,
    Port,
    issue_test_ports,
)
from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    EntityVersion,
    OutcomeState,
    UnauthorizedTransition,
)
from symphony_k.persistence.sqlite import SQLiteStore
from tests import test_outcome_disposition_semantic_transitions as outcome_fx
from tests.persistence_fixtures import seed_snapshot


def facade_with_ports() -> tuple[
    GovernanceFacade, tuple[Port, Port, Port, Port], SQLiteStore
]:
    store = SQLiteStore()
    ports = issue_test_ports()
    return GovernanceFacade(store, ports), ports, store


def test_g1_worker_self_declared_authoritative_success_is_rejected() -> None:
    facade, ports, store = facade_with_ports()
    snapshot = outcome_fx.outcome()
    seed_snapshot(store, snapshot)
    request = outcome_fx.request(snapshot, OutcomeState.ACCEPTED)
    with pytest.raises(UnauthorizedTransition, match="Worker port"):
        facade.apply_transition(
            ports[0],
            snapshot.outcome_id,
            request,
            outcome_fx.context(snapshot, request),
        )
    assert store.outcomes.load(snapshot.outcome_id) == snapshot


def test_g2_worker_cannot_self_accept_by_relabeling_actor() -> None:
    facade, ports, store = facade_with_ports()
    snapshot = outcome_fx.outcome()
    seed_snapshot(store, snapshot)
    request = outcome_fx.request(snapshot, OutcomeState.ACCEPTED)
    forged = replace(
        ports[0],
        lane=ports[2].lane,
    )
    with pytest.raises(UnauthorizedTransition, match="forged"):
        facade.apply_transition(
            forged, snapshot.outcome_id, request, outcome_fx.context(snapshot, request)
        )


def test_g3_stale_evidence_cannot_dispose_current_candidate() -> None:
    facade, ports, store = facade_with_ports()
    snapshot = outcome_fx.outcome()
    seed_snapshot(store, snapshot)
    stale = replace(snapshot, version=EntityVersion(snapshot.version.value - 1))
    request = outcome_fx.request(snapshot, OutcomeState.ACCEPTED)
    context = outcome_fx.context(snapshot, request)
    stale_request = replace(request, expected_version=stale.version)
    with pytest.raises(Exception, match="version|snapshot"):
        facade.apply_transition(ports[2], snapshot.outcome_id, stale_request, context)


def test_g4_cross_entity_authority_substitution_is_rejected() -> None:
    facade, ports, store = facade_with_ports()
    snapshot = outcome_fx.outcome()
    other = replace(snapshot, outcome_id=type(snapshot.outcome_id).new())
    seed_snapshot(store, snapshot)
    seed_snapshot(store, other)
    request = outcome_fx.request(snapshot, OutcomeState.ACCEPTED)
    with pytest.raises(Exception, match="match|snapshot"):
        facade.apply_transition(
            ports[2], other.outcome_id, request, outcome_fx.context(snapshot, request)
        )


def test_forged_port_actor_label_never_grants_capability() -> None:
    facade, ports, _ = facade_with_ports()
    forged_identity = ActorIdentity(ActorId.new(), ActorType.HUMAN_OPERATOR)
    assert forged_identity.actor_type is ActorType.HUMAN_OPERATOR
    forged = Port(ports[2].lane, object())
    with pytest.raises(UnauthorizedTransition, match="forged"):
        facade.export_audit(forged, outcome_fx.outcome().outcome_id)
