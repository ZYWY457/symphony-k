"""Immutable Objective snapshots and structural lifecycle topology only.

Construction does not create authoritative work. The future Transition Engine
owns authority/guards, version changes, and events; these types do none of those.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final

from .actors import ActorIdentity
from .errors import InvalidDomainValue
from .ids import ObjectiveId
from .time import Timestamp
from .version import EntityVersion


class ObjectiveState(Enum):
    """Lifecycle labels; their justification requires future transition guards."""

    DRAFT = "DRAFT"  # Defined but not authorized for execution.
    ACTIVE = "ACTIVE"  # Authorized and capable of owning work.
    BLOCKED = "BLOCKED"  # Still valid, but temporarily unable to progress.
    SATISFIED = "SATISFIED"  # Completion policy and designated acceptance satisfied.
    FAILED = "FAILED"  # Not achievable under accepted constraints.
    CANCELLED = "CANCELLED"  # Intentionally terminated.
    EXPIRED = "EXPIRED"  # Validity horizon ended.
    ARCHIVED = "ARCHIVED"  # Historical sink.


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InvalidDomainValue(f"{field} must contain non-whitespace text")


@dataclass(frozen=True, slots=True)
class CompletionPolicyRef:
    """Opaque definition/version reference, never an evaluated policy result."""

    policy_id: str
    policy_version: str

    def __post_init__(self) -> None:
        _require_text(self.policy_id, "policy_id")
        _require_text(self.policy_version, "policy_version")


@dataclass(frozen=True, slots=True)
class Objective:
    """A structurally validated snapshot, not proof that its state is justified.

    State and version are supplied explicitly; construction is not the DRAFT
    creation transition. Goal boundedness, acceptance, policy satisfaction and
    expiry are governance/transition concerns rather than constructor checks.
    """

    objective_id: ObjectiveId
    state: ObjectiveState
    version: EntityVersion
    goal: str
    acceptance_criteria: tuple[str, ...]
    acceptance_authority: ActorIdentity
    completion_policy_ref: CompletionPolicyRef
    valid_until: Timestamp | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.objective_id, ObjectiveId):
            raise InvalidDomainValue("objective_id must be an ObjectiveId")
        if not isinstance(self.state, ObjectiveState):
            raise InvalidDomainValue("state must be an ObjectiveState")
        if not isinstance(self.version, EntityVersion):
            raise InvalidDomainValue("version must be an EntityVersion")
        _require_text(self.goal, "goal")
        if (
            not isinstance(self.acceptance_criteria, tuple)
            or not self.acceptance_criteria
        ):
            raise InvalidDomainValue("acceptance_criteria must be a nonempty tuple")
        for criterion in self.acceptance_criteria:
            _require_text(criterion, "acceptance criterion")
        if not isinstance(self.acceptance_authority, ActorIdentity):
            raise InvalidDomainValue("acceptance_authority must be an ActorIdentity")
        if not isinstance(self.completion_policy_ref, CompletionPolicyRef):
            raise InvalidDomainValue(
                "completion_policy_ref must be a CompletionPolicyRef"
            )
        if self.valid_until is not None and not isinstance(self.valid_until, Timestamp):
            raise InvalidDomainValue("valid_until must be a Timestamp or None")


# Absence before creation is not a lifecycle state. This does not assign a version.
OBJECTIVE_CREATION_STATE: Final[ObjectiveState] = ObjectiveState.DRAFT

_OBJECTIVE_TRANSITIONS: Final[frozenset[tuple[ObjectiveState, ObjectiveState]]] = (
    frozenset(
        {
            (ObjectiveState.DRAFT, ObjectiveState.ACTIVE),
            (ObjectiveState.ACTIVE, ObjectiveState.BLOCKED),
            (ObjectiveState.BLOCKED, ObjectiveState.ACTIVE),
            (ObjectiveState.ACTIVE, ObjectiveState.SATISFIED),
            (ObjectiveState.BLOCKED, ObjectiveState.SATISFIED),
            (ObjectiveState.ACTIVE, ObjectiveState.FAILED),
            (ObjectiveState.BLOCKED, ObjectiveState.FAILED),
            (ObjectiveState.DRAFT, ObjectiveState.CANCELLED),
            (ObjectiveState.ACTIVE, ObjectiveState.CANCELLED),
            (ObjectiveState.BLOCKED, ObjectiveState.CANCELLED),
            (ObjectiveState.DRAFT, ObjectiveState.EXPIRED),
            (ObjectiveState.ACTIVE, ObjectiveState.EXPIRED),
            (ObjectiveState.BLOCKED, ObjectiveState.EXPIRED),
            (ObjectiveState.SATISFIED, ObjectiveState.ARCHIVED),
            (ObjectiveState.FAILED, ObjectiveState.ARCHIVED),
            (ObjectiveState.CANCELLED, ObjectiveState.ARCHIVED),
            (ObjectiveState.EXPIRED, ObjectiveState.ARCHIVED),
        }
    )
)


def can_objective_transition(source: ObjectiveState, target: ObjectiveState) -> bool:
    """Return structural edge membership, never authorization or safe execution.

    No Objective, actor, policy, clock or version is read or changed. Every edge
    still needs the future Transition Engine's independent authority and guards.
    """
    if not isinstance(source, ObjectiveState) or not isinstance(target, ObjectiveState):
        raise InvalidDomainValue("source and target must be ObjectiveState values")
    return (source, target) in _OBJECTIVE_TRANSITIONS
