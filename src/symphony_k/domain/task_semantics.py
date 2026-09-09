"""Canonical Task-only semantic inputs for lifecycle transitions.

These immutable records consume decisions already made outside the domain kernel.
They do not evaluate policy, load evidence, inspect related entities, persist
records, or start, resume, stop, or own execution.
"""

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Final

from .actors import ActorIdentity
from .candidate_refs import EvidenceRef
from .completion import CompletionPolicyRef
from .errors import CompletionPolicyNotSatisfied, InvalidDomainValue, InvariantViolation
from .ids import CorrelationId, ObjectiveId, RunId, TaskId
from .objective import ObjectiveState
from .task import Task, TaskState
from .version import EntityVersion


class TaskSemanticDecisionStatus(Enum):
    """Closed result vocabulary for an already-made Task semantic decision."""

    PASSED = "PASSED"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


class TaskCompletionBlockerStatus(Enum):
    """Completion-blocker disposition; absence is never clearance."""

    CLEARED = "CLEARED"
    LAWFULLY_WAIVED = "LAWFULLY_WAIVED"
    BLOCKED = "BLOCKED"
    UNRESOLVED = "UNRESOLVED"


class TaskExecutionOwnershipStatus(Enum):
    """Observed execution ownership, separate from lifecycle authority."""

    NO_ACTIVE_OWNERSHIP = "NO_ACTIVE_OWNERSHIP"
    ACTIVE_OWNERSHIP = "ACTIVE_OWNERSHIP"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class TaskSemanticDecisionRef:
    """Opaque decision identity; it never evaluates policy or runtime state."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Task semantic decision reference must contain non-whitespace text"
            )


@dataclass(frozen=True, slots=True)
class TaskExecutionOwnershipRef:
    """Opaque durable execution-control ownership record identity."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Task execution ownership reference must contain non-whitespace text"
            )


def _require_evidence(evidence_refs: frozenset[EvidenceRef]) -> None:
    if not isinstance(evidence_refs, frozenset) or not evidence_refs:
        raise InvalidDomainValue("Semantic decisions require evidence references")
    if any(not isinstance(reference, EvidenceRef) for reference in evidence_refs):
        raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")


def _require_task_snapshot_scope(
    task_id: TaskId,
    observed_entity_version: EntityVersion,
    correlation_id: CorrelationId,
) -> None:
    if not isinstance(task_id, TaskId):
        raise InvalidDomainValue("task_id must be a TaskId")
    if not isinstance(observed_entity_version, EntityVersion):
        raise InvalidDomainValue("observed_entity_version must be an EntityVersion")
    if not isinstance(correlation_id, CorrelationId):
        raise InvalidDomainValue("correlation_id must be a CorrelationId")


@dataclass(frozen=True, slots=True)
class _EvidenceBackedTaskDecision:
    decision_ref: TaskSemanticDecisionRef
    status: TaskSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    task_id: TaskId
    observed_entity_version: EntityVersion
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, TaskSemanticDecisionRef):
            raise InvalidDomainValue("decision_ref must be a TaskSemanticDecisionRef")
        if not isinstance(self.status, TaskSemanticDecisionStatus):
            raise InvalidDomainValue("status must be a TaskSemanticDecisionStatus")
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)
        _require_task_snapshot_scope(
            self.task_id, self.observed_entity_version, self.correlation_id
        )


@dataclass(frozen=True, slots=True)
class TaskDefinitionGovernanceDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskDependencyReadinessDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskBudgetValidityDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskPermissionValidityDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskCurrentBlockerDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskBlockerResolutionDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskEvidenceIndependenceDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskCompletionAcceptanceDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskRequiredEffectsDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskRiskDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskFailureEvidenceDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskRecoveryDispositionDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskTerminationDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskExecutionAuthorizationEndedDecision(_EvidenceBackedTaskDecision):
    pass


@dataclass(frozen=True, slots=True)
class TaskPrimaryObjectiveStateDecision(_EvidenceBackedTaskDecision):
    """Observed primary Objective state for exactly one Task snapshot."""

    primary_objective_id: ObjectiveId
    observed_state: ObjectiveState

    def __post_init__(self) -> None:
        super(TaskPrimaryObjectiveStateDecision, self).__post_init__()
        if not isinstance(self.primary_objective_id, ObjectiveId):
            raise InvalidDomainValue("primary_objective_id must be an ObjectiveId")
        if not isinstance(self.observed_state, ObjectiveState):
            raise InvalidDomainValue("observed_state must be an ObjectiveState")


@dataclass(frozen=True, slots=True)
class TaskCompletionPolicyDecision(_EvidenceBackedTaskDecision):
    completion_policy_ref: CompletionPolicyRef

    def __post_init__(self) -> None:
        super(TaskCompletionPolicyDecision, self).__post_init__()
        if not isinstance(self.completion_policy_ref, CompletionPolicyRef):
            raise InvalidDomainValue(
                "completion_policy_ref must be a CompletionPolicyRef"
            )


@dataclass(frozen=True, slots=True)
class TaskCompletionBlockerDecision:
    decision_ref: TaskSemanticDecisionRef
    status: TaskCompletionBlockerStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    task_id: TaskId
    observed_entity_version: EntityVersion
    correlation_id: CorrelationId
    waiver_policy_ref: CompletionPolicyRef | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, TaskSemanticDecisionRef):
            raise InvalidDomainValue("decision_ref must be a TaskSemanticDecisionRef")
        if not isinstance(self.status, TaskCompletionBlockerStatus):
            raise InvalidDomainValue("status must be a TaskCompletionBlockerStatus")
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)
        _require_task_snapshot_scope(
            self.task_id, self.observed_entity_version, self.correlation_id
        )
        if self.status is TaskCompletionBlockerStatus.LAWFULLY_WAIVED:
            if not isinstance(self.waiver_policy_ref, CompletionPolicyRef):
                raise InvalidDomainValue(
                    "A lawful completion-blocker waiver requires its policy reference"
                )
        elif self.waiver_policy_ref is not None:
            raise InvalidDomainValue(
                "waiver_policy_ref is valid only for a lawful waiver"
            )


@dataclass(frozen=True, slots=True)
class TaskExecutionOwnershipDecision:
    """Evidence-backed ownership observation, not a scheduler/runtime controller."""

    decision_ref: TaskSemanticDecisionRef
    status: TaskExecutionOwnershipStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    task_id: TaskId
    observed_entity_version: EntityVersion
    correlation_id: CorrelationId
    linked_run_id: RunId | None = None
    execution_control_ref: TaskExecutionOwnershipRef | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, TaskSemanticDecisionRef):
            raise InvalidDomainValue("decision_ref must be a TaskSemanticDecisionRef")
        if not isinstance(self.status, TaskExecutionOwnershipStatus):
            raise InvalidDomainValue("status must be a TaskExecutionOwnershipStatus")
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)
        _require_task_snapshot_scope(
            self.task_id, self.observed_entity_version, self.correlation_id
        )
        if self.linked_run_id is not None and not isinstance(self.linked_run_id, RunId):
            raise InvalidDomainValue("linked_run_id must be a RunId or None")
        if self.execution_control_ref is not None and not isinstance(
            self.execution_control_ref, TaskExecutionOwnershipRef
        ):
            raise InvalidDomainValue(
                "execution_control_ref must be a TaskExecutionOwnershipRef or None"
            )
        has_owner = (
            self.linked_run_id is not None or self.execution_control_ref is not None
        )
        if self.status is TaskExecutionOwnershipStatus.ACTIVE_OWNERSHIP:
            if not has_owner or (
                self.linked_run_id is not None
                and self.execution_control_ref is not None
            ):
                raise InvalidDomainValue(
                    "Active execution ownership requires exactly one owner reference"
                )
        elif has_owner:
            raise InvalidDomainValue(
                "Only active execution ownership may contain an owner reference"
            )


@dataclass(frozen=True, slots=True)
class TaskReadinessSemantics:
    governance: TaskDefinitionGovernanceDecision
    dependencies: TaskDependencyReadinessDecision
    budget: TaskBudgetValidityDecision
    permissions: TaskPermissionValidityDecision
    primary_objective: TaskPrimaryObjectiveStateDecision

    def __post_init__(self) -> None:
        for value, expected, name in (
            (self.governance, TaskDefinitionGovernanceDecision, "governance"),
            (self.dependencies, TaskDependencyReadinessDecision, "dependencies"),
            (self.budget, TaskBudgetValidityDecision, "budget"),
            (self.permissions, TaskPermissionValidityDecision, "permissions"),
            (
                self.primary_objective,
                TaskPrimaryObjectiveStateDecision,
                "primary_objective",
            ),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue(f"{name} has the wrong decision type")


@dataclass(frozen=True, slots=True)
class TaskBlockingSemantics:
    blocker: TaskCurrentBlockerDecision

    def __post_init__(self) -> None:
        if not isinstance(self.blocker, TaskCurrentBlockerDecision):
            raise InvalidDomainValue("blocker must be a TaskCurrentBlockerDecision")


@dataclass(frozen=True, slots=True)
class TaskReadinessAfterBlockSemantics:
    blocker_resolution: TaskBlockerResolutionDecision
    readiness: TaskReadinessSemantics
    execution_ownership: TaskExecutionOwnershipDecision

    def __post_init__(self) -> None:
        if not isinstance(self.blocker_resolution, TaskBlockerResolutionDecision):
            raise InvalidDomainValue(
                "blocker_resolution must be a TaskBlockerResolutionDecision"
            )
        if not isinstance(self.readiness, TaskReadinessSemantics):
            raise InvalidDomainValue("readiness must be a TaskReadinessSemantics")
        if not isinstance(self.execution_ownership, TaskExecutionOwnershipDecision):
            raise InvalidDomainValue(
                "execution_ownership must be a TaskExecutionOwnershipDecision"
            )


@dataclass(frozen=True, slots=True)
class TaskStartSemantics:
    readiness: TaskReadinessSemantics
    execution_ownership: TaskExecutionOwnershipDecision

    def __post_init__(self) -> None:
        if not isinstance(self.readiness, TaskReadinessSemantics):
            raise InvalidDomainValue("readiness must be a TaskReadinessSemantics")
        if not isinstance(self.execution_ownership, TaskExecutionOwnershipDecision):
            raise InvalidDomainValue(
                "execution_ownership must be a TaskExecutionOwnershipDecision"
            )


@dataclass(frozen=True, slots=True)
class TaskResumeSemantics:
    blocker_resolution: TaskBlockerResolutionDecision
    primary_objective: TaskPrimaryObjectiveStateDecision
    execution_ownership: TaskExecutionOwnershipDecision

    def __post_init__(self) -> None:
        if not isinstance(self.blocker_resolution, TaskBlockerResolutionDecision):
            raise InvalidDomainValue(
                "blocker_resolution must be a TaskBlockerResolutionDecision"
            )
        if not isinstance(self.primary_objective, TaskPrimaryObjectiveStateDecision):
            raise InvalidDomainValue(
                "primary_objective must be a TaskPrimaryObjectiveStateDecision"
            )
        if not isinstance(self.execution_ownership, TaskExecutionOwnershipDecision):
            raise InvalidDomainValue(
                "execution_ownership must be a TaskExecutionOwnershipDecision"
            )


@dataclass(frozen=True, slots=True)
class TaskCompletionSemantics:
    completion_policy: TaskCompletionPolicyDecision
    evidence_independence: TaskEvidenceIndependenceDecision
    acceptance: TaskCompletionAcceptanceDecision
    required_effects: TaskRequiredEffectsDecision
    risk: TaskRiskDecision
    completion_blockers: TaskCompletionBlockerDecision

    def __post_init__(self) -> None:
        for value, expected, name in (
            (self.completion_policy, TaskCompletionPolicyDecision, "completion_policy"),
            (
                self.evidence_independence,
                TaskEvidenceIndependenceDecision,
                "evidence_independence",
            ),
            (self.acceptance, TaskCompletionAcceptanceDecision, "acceptance"),
            (self.required_effects, TaskRequiredEffectsDecision, "required_effects"),
            (self.risk, TaskRiskDecision, "risk"),
            (
                self.completion_blockers,
                TaskCompletionBlockerDecision,
                "completion_blockers",
            ),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue(f"{name} has the wrong decision type")


@dataclass(frozen=True, slots=True)
class TaskFailureSemantics:
    failure_evidence: TaskFailureEvidenceDecision
    recovery_disposition: TaskRecoveryDispositionDecision

    def __post_init__(self) -> None:
        if not isinstance(self.failure_evidence, TaskFailureEvidenceDecision):
            raise InvalidDomainValue(
                "failure_evidence must be a TaskFailureEvidenceDecision"
            )
        if not isinstance(self.recovery_disposition, TaskRecoveryDispositionDecision):
            raise InvalidDomainValue(
                "recovery_disposition must be a TaskRecoveryDispositionDecision"
            )


@dataclass(frozen=True, slots=True)
class TaskCancellationSemantics:
    termination: TaskTerminationDecision
    execution_authorization_ended: TaskExecutionAuthorizationEndedDecision

    def __post_init__(self) -> None:
        if not isinstance(self.termination, TaskTerminationDecision):
            raise InvalidDomainValue("termination must be a TaskTerminationDecision")
        if not isinstance(
            self.execution_authorization_ended, TaskExecutionAuthorizationEndedDecision
        ):
            raise InvalidDomainValue(
                "execution_authorization_ended must be a "
                "TaskExecutionAuthorizationEndedDecision"
            )


type TaskSemanticInput = (
    TaskReadinessSemantics
    | TaskBlockingSemantics
    | TaskReadinessAfterBlockSemantics
    | TaskStartSemantics
    | TaskResumeSemantics
    | TaskCompletionSemantics
    | TaskFailureSemantics
    | TaskCancellationSemantics
)

type _TaskSnapshotBoundSemanticDecision = (
    _EvidenceBackedTaskDecision
    | TaskCompletionBlockerDecision
    | TaskExecutionOwnershipDecision
)


def _semantic_decisions_for(
    semantics: TaskSemanticInput,
) -> tuple[_TaskSnapshotBoundSemanticDecision, ...]:
    if isinstance(semantics, TaskReadinessSemantics):
        return (
            semantics.governance,
            semantics.dependencies,
            semantics.budget,
            semantics.permissions,
            semantics.primary_objective,
        )
    if isinstance(semantics, TaskBlockingSemantics):
        return (semantics.blocker,)
    if isinstance(semantics, TaskReadinessAfterBlockSemantics):
        return (
            semantics.blocker_resolution,
            *_semantic_decisions_for(semantics.readiness),
            semantics.execution_ownership,
        )
    if isinstance(semantics, TaskStartSemantics):
        return (
            *_semantic_decisions_for(semantics.readiness),
            semantics.execution_ownership,
        )
    if isinstance(semantics, TaskResumeSemantics):
        return (
            semantics.blocker_resolution,
            semantics.primary_objective,
            semantics.execution_ownership,
        )
    if isinstance(semantics, TaskCompletionSemantics):
        return (
            semantics.completion_policy,
            semantics.evidence_independence,
            semantics.acceptance,
            semantics.required_effects,
            semantics.risk,
            semantics.completion_blockers,
        )
    if isinstance(semantics, TaskFailureSemantics):
        return (semantics.failure_evidence, semantics.recovery_disposition)
    return (semantics.termination, semantics.execution_authorization_ended)


_INPUT_TYPE_BY_EDGE: Final[
    MappingProxyType[tuple[TaskState, TaskState], type[TaskSemanticInput]]
] = MappingProxyType(
    {
        (TaskState.DRAFT, TaskState.READY): TaskReadinessSemantics,
        (TaskState.DRAFT, TaskState.BLOCKED): TaskBlockingSemantics,
        (TaskState.READY, TaskState.BLOCKED): TaskBlockingSemantics,
        (TaskState.IN_PROGRESS, TaskState.BLOCKED): TaskBlockingSemantics,
        (TaskState.BLOCKED, TaskState.READY): TaskReadinessAfterBlockSemantics,
        (TaskState.READY, TaskState.IN_PROGRESS): TaskStartSemantics,
        (TaskState.BLOCKED, TaskState.IN_PROGRESS): TaskResumeSemantics,
        (TaskState.IN_PROGRESS, TaskState.COMPLETED): TaskCompletionSemantics,
        (TaskState.BLOCKED, TaskState.COMPLETED): TaskCompletionSemantics,
        (TaskState.READY, TaskState.FAILED): TaskFailureSemantics,
        (TaskState.IN_PROGRESS, TaskState.FAILED): TaskFailureSemantics,
        (TaskState.BLOCKED, TaskState.FAILED): TaskFailureSemantics,
        (TaskState.DRAFT, TaskState.CANCELLED): TaskCancellationSemantics,
        (TaskState.READY, TaskState.CANCELLED): TaskCancellationSemantics,
        (TaskState.IN_PROGRESS, TaskState.CANCELLED): TaskCancellationSemantics,
        (TaskState.BLOCKED, TaskState.CANCELLED): TaskCancellationSemantics,
    }
)


def _require_passed(decision: _EvidenceBackedTaskDecision, condition: str) -> None:
    if decision.status is not TaskSemanticDecisionStatus.PASSED:
        raise InvariantViolation(
            f"Task semantic condition is not satisfied: {condition}"
        )


@dataclass(frozen=True, slots=True)
class TaskSemanticGuard:
    """Canonical guard for one exact Task snapshot transition attempt."""

    task_id: TaskId
    observed_entity_version: EntityVersion
    prior_state: TaskState
    target_state: TaskState
    correlation_id: CorrelationId
    semantic_input: TaskSemanticInput

    def __post_init__(self) -> None:
        _require_task_snapshot_scope(
            self.task_id, self.observed_entity_version, self.correlation_id
        )
        if not isinstance(self.prior_state, TaskState) or not isinstance(
            self.target_state, TaskState
        ):
            raise InvalidDomainValue("prior_state and target_state must be TaskState")
        expected = _INPUT_TYPE_BY_EDGE.get((self.prior_state, self.target_state))
        if expected is None or not isinstance(self.semantic_input, expected):
            raise InvalidDomainValue(
                "semantic_input must match a canonical Task lifecycle edge"
            )

    def validate(
        self,
        task: Task,
        target_state: TaskState,
        correlation_id: CorrelationId,
    ) -> None:
        """Validate exact binding and the accepted edge-specific Task semantics."""
        if not isinstance(task, Task):
            raise InvalidDomainValue("task must be a Task")
        if not isinstance(target_state, TaskState):
            raise InvalidDomainValue("target_state must be a TaskState")
        if not isinstance(correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if not (
            self.task_id == task.task_id
            and self.observed_entity_version == task.version
            and self.prior_state is task.state
            and self.target_state is target_state
            and self.correlation_id == correlation_id
        ):
            raise InvariantViolation(
                "Task semantic guard does not match the exact request snapshot"
            )
        for decision in _semantic_decisions_for(self.semantic_input):
            if not (
                decision.task_id == self.task_id
                and decision.observed_entity_version == self.observed_entity_version
                and decision.correlation_id == self.correlation_id
            ):
                raise InvariantViolation(
                    "Task semantic decision does not match the exact request snapshot"
                )

        semantics = self.semantic_input
        if isinstance(semantics, TaskReadinessSemantics):
            self._validate_readiness(task, semantics)
        elif isinstance(semantics, TaskBlockingSemantics):
            _require_passed(semantics.blocker, "identified current blocker")
        elif isinstance(semantics, TaskReadinessAfterBlockSemantics):
            _require_passed(semantics.blocker_resolution, "all blockers resolved")
            self._validate_readiness(task, semantics.readiness)
            self._require_no_active_ownership(semantics.execution_ownership)
        elif isinstance(semantics, TaskStartSemantics):
            self._validate_readiness(task, semantics.readiness)
            self._require_active_ownership(semantics.execution_ownership)
        elif isinstance(semantics, TaskResumeSemantics):
            _require_passed(semantics.blocker_resolution, "all blockers resolved")
            self._require_active_primary_objective(task, semantics.primary_objective)
            self._require_active_ownership(semantics.execution_ownership)
        elif isinstance(semantics, TaskCompletionSemantics):
            self._validate_completion(task, semantics)
        elif isinstance(semantics, TaskFailureSemantics):
            _require_passed(semantics.failure_evidence, "recorded failure evidence")
            _require_passed(
                semantics.recovery_disposition,
                "permitted recovery exhausted or ruled out",
            )
        else:
            _require_passed(semantics.termination, "authorized termination decision")
            _require_passed(
                semantics.execution_authorization_ended,
                "continuing execution is no longer authorized",
            )

    @staticmethod
    def _require_active_primary_objective(
        task: Task, decision: TaskPrimaryObjectiveStateDecision
    ) -> None:
        if decision.primary_objective_id != task.primary_objective_id:
            raise InvariantViolation(
                "Primary Objective evidence does not identify the Task primary "
                "Objective"
            )
        _require_passed(decision, "primary Objective observation")
        if decision.observed_state is not ObjectiveState.ACTIVE:
            raise InvariantViolation("Task primary Objective is not ACTIVE")

    def _validate_readiness(
        self, task: Task, semantics: TaskReadinessSemantics
    ) -> None:
        _require_passed(semantics.governance, "definition and governance approval")
        _require_passed(semantics.dependencies, "dependency readiness")
        _require_passed(semantics.budget, "applicable budget validity")
        _require_passed(semantics.permissions, "applicable permission validity")
        self._require_active_primary_objective(task, semantics.primary_objective)

    @staticmethod
    def _require_no_active_ownership(
        decision: TaskExecutionOwnershipDecision,
    ) -> None:
        if decision.status is not TaskExecutionOwnershipStatus.NO_ACTIVE_OWNERSHIP:
            raise InvariantViolation(
                "Task execution ownership is active or unresolved; it cannot be readied"
            )

    @staticmethod
    def _require_active_ownership(
        decision: TaskExecutionOwnershipDecision,
    ) -> None:
        if decision.status is not TaskExecutionOwnershipStatus.ACTIVE_OWNERSHIP:
            raise InvariantViolation("Task has no recorded active execution ownership")

    @staticmethod
    def _validate_completion(task: Task, semantics: TaskCompletionSemantics) -> None:
        if (
            semantics.completion_policy.completion_policy_ref
            != task.completion_policy_ref
        ):
            raise CompletionPolicyNotSatisfied(
                "Completion decision does not use the current CompletionPolicyRef"
            )
        if semantics.completion_policy.status is not TaskSemanticDecisionStatus.PASSED:
            raise CompletionPolicyNotSatisfied(
                "Current Task completion policy is not satisfied"
            )
        _require_passed(
            semantics.evidence_independence, "independent completion evidence"
        )
        _require_passed(semantics.acceptance, "required acceptance checks")
        _require_passed(semantics.required_effects, "required effect checks")
        _require_passed(semantics.risk, "required risk checks")
        blockers = semantics.completion_blockers
        if blockers.status is TaskCompletionBlockerStatus.CLEARED:
            return
        if blockers.status is TaskCompletionBlockerStatus.LAWFULLY_WAIVED:
            if blockers.waiver_policy_ref != task.completion_policy_ref:
                raise CompletionPolicyNotSatisfied(
                    "Completion-blocker waiver is not scoped to the current policy"
                )
            return
        raise CompletionPolicyNotSatisfied(
            "Completion blockers are not resolved or lawfully waived"
        )
