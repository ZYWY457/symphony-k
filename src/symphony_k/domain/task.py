"""Immutable Task snapshots and structural topology, with passive Objective IDs.

No Objective state is read or propagated. Authority, existence checks, guards,
version changes and events belong to the future centralized Transition Engine.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final

from .completion import CompletionPolicyRef
from .errors import InvalidDomainValue
from .ids import ObjectiveId, TaskId
from .version import EntityVersion


class TaskState(Enum):
    """Lifecycle labels; snapshots do not prove the conditions behind them."""

    DRAFT = "DRAFT"  # Definition exists but is not executable.
    READY = "READY"  # Valid and eligible for scheduling.
    IN_PROGRESS = "IN_PROGRESS"  # Actively attempted or retained by execution control.
    BLOCKED = "BLOCKED"  # Temporarily unable to progress.
    COMPLETED = "COMPLETED"  # Task Completion Policy satisfied.
    FAILED = "FAILED"  # Unsuccessful under allowed recovery policy.
    CANCELLED = "CANCELLED"  # Intentionally terminated.


@dataclass(frozen=True, slots=True)
class Task:
    """A structurally validated snapshot; construction executes no transition.

    State/version are explicit. One primary ObjectiveId records ownership;
    secondary IDs are non-authoritative. Neither relationship proves existence
    or grants permission, and no Objective objects are retained or modified.
    """

    task_id: TaskId
    state: TaskState
    version: EntityVersion
    definition: str
    primary_objective_id: ObjectiveId
    completion_policy_ref: CompletionPolicyRef
    contributes_to: frozenset[ObjectiveId] = frozenset()

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId")
        if not isinstance(self.state, TaskState):
            raise InvalidDomainValue("state must be a TaskState")
        if not isinstance(self.version, EntityVersion):
            raise InvalidDomainValue("version must be an EntityVersion")
        if not isinstance(self.definition, str) or not self.definition.strip():
            raise InvalidDomainValue("definition must contain non-whitespace text")
        if not isinstance(self.primary_objective_id, ObjectiveId):
            raise InvalidDomainValue("primary_objective_id must be an ObjectiveId")
        if not isinstance(self.completion_policy_ref, CompletionPolicyRef):
            raise InvalidDomainValue(
                "completion_policy_ref must be a CompletionPolicyRef"
            )
        if not isinstance(self.contributes_to, frozenset):
            raise InvalidDomainValue(
                "contributes_to must be a frozenset of ObjectiveId"
            )
        if any(
            not isinstance(identity, ObjectiveId) for identity in self.contributes_to
        ):
            raise InvalidDomainValue("Every contribution must be an ObjectiveId")
        if self.primary_objective_id in self.contributes_to:
            raise InvalidDomainValue("Primary Objective cannot also be a contribution")


# Only creation's destination is represented; no NONE state or initial version.
TASK_CREATION_STATE: Final[TaskState] = TaskState.DRAFT

_TASK_TRANSITIONS: Final[frozenset[tuple[TaskState, TaskState]]] = frozenset(
    {
        (TaskState.DRAFT, TaskState.READY),
        (TaskState.DRAFT, TaskState.BLOCKED),
        (TaskState.READY, TaskState.BLOCKED),
        (TaskState.IN_PROGRESS, TaskState.BLOCKED),
        (TaskState.BLOCKED, TaskState.READY),
        (TaskState.READY, TaskState.IN_PROGRESS),
        (TaskState.BLOCKED, TaskState.IN_PROGRESS),
        (TaskState.IN_PROGRESS, TaskState.COMPLETED),
        (TaskState.BLOCKED, TaskState.COMPLETED),
        (TaskState.READY, TaskState.FAILED),
        (TaskState.IN_PROGRESS, TaskState.FAILED),
        (TaskState.BLOCKED, TaskState.FAILED),
        (TaskState.DRAFT, TaskState.CANCELLED),
        (TaskState.READY, TaskState.CANCELLED),
        (TaskState.IN_PROGRESS, TaskState.CANCELLED),
        (TaskState.BLOCKED, TaskState.CANCELLED),
    }
)


def can_task_transition(source: TaskState, target: TaskState) -> bool:
    """Return structural membership only, never authority or execution safety.

    This reads no Task, Objective, policy, dependency, budget, grant or execution
    ownership and mutates nothing. A True result is not permission to transition.
    """
    if not isinstance(source, TaskState) or not isinstance(target, TaskState):
        raise InvalidDomainValue("source and target must be TaskState values")
    return (source, target) in _TASK_TRANSITIONS
