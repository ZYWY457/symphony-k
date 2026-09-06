"""Actor identity and classification only; these types grant no authority."""

from dataclasses import dataclass
from enum import Enum

from .errors import InvalidDomainValue
from .ids import ActorId


class ActorType(Enum):
    """Accepted actor categories; SYSTEM is an ordinary classification."""

    REQUESTER = "REQUESTER"
    SCHEDULER = "SCHEDULER"
    RUN_CONTROLLER = "RUN_CONTROLLER"
    WORKER = "WORKER"
    EVALUATOR = "EVALUATOR"
    ARBITRATOR = "ARBITRATOR"
    EFFECT_CONTROLLER = "EFFECT_CONTROLLER"
    POLICY_ENGINE = "POLICY_ENGINE"
    HUMAN_OPERATOR = "HUMAN_OPERATOR"
    SYSTEM = "SYSTEM"


@dataclass(frozen=True, slots=True)
class ActorIdentity:
    """Who a principal is and which category it is operating as."""

    actor_id: ActorId
    actor_type: ActorType

    def __post_init__(self) -> None:
        if not isinstance(self.actor_id, ActorId):
            raise InvalidDomainValue("actor_id must be an ActorId")
        if not isinstance(self.actor_type, ActorType):
            raise InvalidDomainValue("actor_type must be an ActorType")
