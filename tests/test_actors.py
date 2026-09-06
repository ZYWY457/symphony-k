"""Actor identity is a value, never an authorization decision."""

from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    InvalidDomainValue,
    TaskId,
)

ACTOR_ID = ActorId(UUID("12345678-1234-4234-8234-123456789abc"))


def test_actor_categories_match_the_accepted_inventory() -> None:
    assert {member.name: member.value for member in ActorType} == {
        "REQUESTER": "REQUESTER",
        "SCHEDULER": "SCHEDULER",
        "RUN_CONTROLLER": "RUN_CONTROLLER",
        "WORKER": "WORKER",
        "EVALUATOR": "EVALUATOR",
        "ARBITRATOR": "ARBITRATOR",
        "EFFECT_CONTROLLER": "EFFECT_CONTROLLER",
        "POLICY_ENGINE": "POLICY_ENGINE",
        "HUMAN_OPERATOR": "HUMAN_OPERATOR",
        "SYSTEM": "SYSTEM",
    }


@pytest.mark.parametrize("category", list(ActorType))
def test_identity_preserves_both_fields_for_every_category(category: ActorType) -> None:
    identity = ActorIdentity(ACTOR_ID, category)
    assert identity.actor_id == ACTOR_ID
    assert identity.actor_type is category
    assert {identity: "found"}[ActorIdentity(ACTOR_ID, category)] == "found"
    assert not hasattr(identity, "permissions")
    assert not hasattr(identity, "is_authorized")
    with pytest.raises(AttributeError):
        identity.actor_type = ActorType.WORKER  # type: ignore[misc]
    with pytest.raises(AttributeError):
        identity.actor_id = ActorId(UUID(int=0))  # type: ignore[misc]


def test_principal_and_category_are_independent() -> None:
    worker = ActorIdentity(ACTOR_ID, ActorType.WORKER)
    system = ActorIdentity(ACTOR_ID, ActorType.SYSTEM)
    assert worker.actor_id == system.actor_id
    assert worker != system
    assert worker != ActorIdentity(ActorId(UUID(int=0)), ActorType.WORKER)
    assert ActorType.SYSTEM != "SYSTEM"  # type: ignore[comparison-overlap]


@pytest.mark.parametrize("raw", ["WORKER", "SYSTEM", "administrator", "", None, 1])
def test_identity_rejects_raw_categories(raw: object) -> None:
    with pytest.raises(InvalidDomainValue):
        ActorIdentity(ACTOR_ID, raw)  # type: ignore[arg-type]


def test_identity_rejects_wrong_id_kinds() -> None:
    with pytest.raises(InvalidDomainValue):
        ActorIdentity(TaskId(ACTOR_ID.value), ActorType.SYSTEM)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        ActorIdentity(ACTOR_ID.value, ActorType.SYSTEM)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        ActorType("administrator")
