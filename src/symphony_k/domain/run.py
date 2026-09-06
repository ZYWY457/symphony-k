"""Immutable execution-attempt snapshots and structural Run topology only.

No authority, runtime, recovery, version mutation or events are implemented.
Worker self-completion checks remain the responsibility of M7's Transition Engine.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final

from .errors import InvalidDomainValue
from .execution_profile import ExecutionProfileRef
from .ids import RunId, TaskId
from .version import EntityVersion


class RunState(Enum):
    """Execution lifecycle labels; snapshots do not prove transition guards."""

    PENDING = "PENDING"  # The attempt exists but has not started.
    RUNNING = "RUNNING"  # Execution is active.
    WAITING_FOR_VERIFICATION = (
        "WAITING_FOR_VERIFICATION"  # Run-level wait, not acceptance.
    )
    RETRYING = "RETRYING"  # Continuation of this same trustworthy attempt is prepared.
    REASSIGNED = (
        "REASSIGNED"  # This attempt has closed with responsibility transferred.
    )
    COMPLETED = "COMPLETED"  # Normal execution closure, not result correctness.
    FAILED = "FAILED"  # This attempt cannot continue on its recovery path.
    ABORTED = "ABORTED"  # This attempt was forcibly terminated.


@dataclass(frozen=True, slots=True)
class Run:
    """An immutable snapshot of one attempt, identified exclusively by RunId.

    State/version are explicit; construction is not authoritative creation or
    transition execution. Task and predecessor references are passive IDs.
    No constructor validates external existence, authority or recovery evidence.
    """

    run_id: RunId
    task_id: TaskId
    state: RunState
    version: EntityVersion
    execution_profile_ref: ExecutionProfileRef
    predecessor_run_id: RunId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.run_id, RunId):
            raise InvalidDomainValue("run_id must be a RunId")
        if not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId")
        if not isinstance(self.state, RunState):
            raise InvalidDomainValue("state must be a RunState")
        if not isinstance(self.version, EntityVersion):
            raise InvalidDomainValue("version must be an EntityVersion")
        if not isinstance(self.execution_profile_ref, ExecutionProfileRef):
            raise InvalidDomainValue(
                "execution_profile_ref must be an ExecutionProfileRef"
            )
        if self.predecessor_run_id is not None:
            if not isinstance(self.predecessor_run_id, RunId):
                raise InvalidDomainValue("predecessor_run_id must be a RunId or None")
            if self.predecessor_run_id == self.run_id:
                raise InvalidDomainValue("A Run cannot be its own predecessor")


# Creation's only destination; no NONE enum value or default entity version.
RUN_CREATION_STATE: Final[RunState] = RunState.PENDING

_RUN_TRANSITIONS: Final[frozenset[tuple[RunState, RunState]]] = frozenset(
    {
        (RunState.PENDING, RunState.RUNNING),
        (RunState.RUNNING, RunState.WAITING_FOR_VERIFICATION),
        (RunState.RUNNING, RunState.RETRYING),
        (RunState.RETRYING, RunState.RUNNING),
        (RunState.PENDING, RunState.REASSIGNED),
        (RunState.RUNNING, RunState.REASSIGNED),
        (RunState.WAITING_FOR_VERIFICATION, RunState.REASSIGNED),
        (RunState.RETRYING, RunState.REASSIGNED),
        (RunState.RUNNING, RunState.COMPLETED),
        (RunState.WAITING_FOR_VERIFICATION, RunState.COMPLETED),
        (RunState.PENDING, RunState.FAILED),
        (RunState.RUNNING, RunState.FAILED),
        (RunState.WAITING_FOR_VERIFICATION, RunState.FAILED),
        (RunState.RETRYING, RunState.FAILED),
        (RunState.PENDING, RunState.ABORTED),
        (RunState.RUNNING, RunState.ABORTED),
        (RunState.WAITING_FOR_VERIFICATION, RunState.ABORTED),
        (RunState.RETRYING, RunState.ABORTED),
    }
)


def can_run_transition(source: RunState, target: RunState) -> bool:
    """Return structural membership only, not permission to execute a transition.

    Reads no Run, actor, Task, Objective, profile, evidence, budget or recovery
    state. This query cannot enforce Worker restrictions or execute a recovery.
    """
    if not isinstance(source, RunState) or not isinstance(target, RunState):
        raise InvalidDomainValue("source and target must be RunState values")
    return (source, target) in _RUN_TRANSITIONS
