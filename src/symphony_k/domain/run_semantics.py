"""Canonical Run normal-execution semantic inputs for lifecycle transitions.

These immutable records consume decisions already made outside the domain kernel.
They do not evaluate policy, load state, persist records, control execution, or
mutate a related Task, Objective, Outcome, or Evaluation.
"""

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Final

from .actors import ActorIdentity, ActorType
from .candidate_refs import EvidenceRef
from .errors import InvalidDomainValue, InvariantViolation
from .execution_profile import ExecutionProfileRef
from .ids import CorrelationId, ObjectiveId, OutcomeId, RunId, TaskId
from .objective import ObjectiveState
from .run import Run, RunState
from .task import TaskState
from .version import EntityVersion


class RunSemanticDecisionStatus(Enum):
    """Closed result vocabulary for an already-made Run semantic decision."""

    PASSED = "PASSED"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


class RunVerificationResolutionStatus(Enum):
    """A resolved verification may be favorable or unfavorable to the candidate."""

    RESOLVED_FAVORABLE = "RESOLVED_FAVORABLE"
    RESOLVED_UNFAVORABLE = "RESOLVED_UNFAVORABLE"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class RunSemanticDecisionRef:
    """Opaque decision identity; it never evaluates policy or runtime state."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Run semantic decision reference must contain non-whitespace text"
            )


@dataclass(frozen=True, slots=True)
class RunExecutionOwnershipRef:
    """Opaque durable Task execution-control ownership record identity."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Run execution ownership reference must contain non-whitespace text"
            )


@dataclass(frozen=True, slots=True)
class RunRecoveryBoundaryRef:
    """Opaque durable reference to an already-trusted recovery boundary."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Run recovery boundary reference must contain non-whitespace text"
            )


def _require_evidence(evidence_refs: frozenset[EvidenceRef]) -> None:
    if not isinstance(evidence_refs, frozenset) or not evidence_refs:
        raise InvalidDomainValue("Run semantic decisions require evidence references")
    if any(not isinstance(reference, EvidenceRef) for reference in evidence_refs):
        raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")


def _require_run_snapshot_scope(
    run_id: RunId,
    observed_entity_version: EntityVersion,
    correlation_id: CorrelationId,
) -> None:
    if not isinstance(run_id, RunId):
        raise InvalidDomainValue("run_id must be a RunId")
    if not isinstance(observed_entity_version, EntityVersion):
        raise InvalidDomainValue("observed_entity_version must be an EntityVersion")
    if not isinstance(correlation_id, CorrelationId):
        raise InvalidDomainValue("correlation_id must be a CorrelationId")


@dataclass(frozen=True, slots=True)
class _EvidenceBackedRunDecision:
    decision_ref: RunSemanticDecisionRef
    status: RunSemanticDecisionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    run_id: RunId
    observed_entity_version: EntityVersion
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, RunSemanticDecisionRef):
            raise InvalidDomainValue("decision_ref must be a RunSemanticDecisionRef")
        if not isinstance(self.status, RunSemanticDecisionStatus):
            raise InvalidDomainValue("status must be a RunSemanticDecisionStatus")
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)
        _require_run_snapshot_scope(
            self.run_id, self.observed_entity_version, self.correlation_id
        )


@dataclass(frozen=True, slots=True)
class RunExecutionBoundaryDecision(_EvidenceBackedRunDecision):
    pass


@dataclass(frozen=True, slots=True)
class RunGrantValidityDecision(_EvidenceBackedRunDecision):
    pass


@dataclass(frozen=True, slots=True)
class RunBudgetValidityDecision(_EvidenceBackedRunDecision):
    pass


@dataclass(frozen=True, slots=True)
class RunTrustedStartConfirmationDecision(_EvidenceBackedRunDecision):
    pass


@dataclass(frozen=True, slots=True)
class RunExecutionStoppedDecision(_EvidenceBackedRunDecision):
    pass


@dataclass(frozen=True, slots=True)
class RunVerificationRequestDecision(_EvidenceBackedRunDecision):
    pass


@dataclass(frozen=True, slots=True)
class RunIndependentNormalTerminationDecision(_EvidenceBackedRunDecision):
    pass


@dataclass(frozen=True, slots=True)
class RunArtifactUsagePersistenceDecision(_EvidenceBackedRunDecision):
    pass


@dataclass(frozen=True, slots=True)
class RunNoVerificationWaitRequirementDecision(_EvidenceBackedRunDecision):
    pass


@dataclass(frozen=True, slots=True)
class RunVerificationEvidenceRetentionDecision(_EvidenceBackedRunDecision):
    pass


@dataclass(frozen=True, slots=True)
class RunRecoverableInterruptionDecision(_EvidenceBackedRunDecision):
    """Evidence-backed interruption classification; a worker report is admissible."""


@dataclass(frozen=True, slots=True)
class RunSameAttemptContinuityDecision(_EvidenceBackedRunDecision):
    """Trusted observation that the existing attempt/path/strategy still applies."""

    task_id: TaskId
    predecessor_run_id: RunId | None
    execution_profile_ref: ExecutionProfileRef

    def __post_init__(self) -> None:
        super(RunSameAttemptContinuityDecision, self).__post_init__()
        if not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId")
        if self.predecessor_run_id is not None and not isinstance(
            self.predecessor_run_id, RunId
        ):
            raise InvalidDomainValue("predecessor_run_id must be a RunId or None")
        if not isinstance(self.execution_profile_ref, ExecutionProfileRef):
            raise InvalidDomainValue(
                "execution_profile_ref must be an ExecutionProfileRef"
            )


@dataclass(frozen=True, slots=True)
class RunResumeDecision(_EvidenceBackedRunDecision):
    """Explicit recovery-controller decision to Resume one exact Run snapshot."""


@dataclass(frozen=True, slots=True)
class RunTrustedRecoveryBoundaryDecision(_EvidenceBackedRunDecision):
    """Trusted provenance observation for an already-recorded recovery boundary."""

    recovery_boundary_ref: RunRecoveryBoundaryRef

    def __post_init__(self) -> None:
        super(RunTrustedRecoveryBoundaryDecision, self).__post_init__()
        if not isinstance(self.recovery_boundary_ref, RunRecoveryBoundaryRef):
            raise InvalidDomainValue(
                "recovery_boundary_ref must be a RunRecoveryBoundaryRef"
            )


@dataclass(frozen=True, slots=True)
class RunRecoveryLimitsDecision(_EvidenceBackedRunDecision):
    """Evidence-backed observation that continuation remains within recovery limits."""


@dataclass(frozen=True, slots=True)
class RunExecutionProfileApprovalDecision(_EvidenceBackedRunDecision):
    """Approval observation for one exact execution-profile definition/version."""

    execution_profile_ref: ExecutionProfileRef

    def __post_init__(self) -> None:
        super(RunExecutionProfileApprovalDecision, self).__post_init__()
        if not isinstance(self.execution_profile_ref, ExecutionProfileRef):
            raise InvalidDomainValue(
                "execution_profile_ref must be an ExecutionProfileRef"
            )


@dataclass(frozen=True, slots=True)
class RunTaskStateObservation(_EvidenceBackedRunDecision):
    """An observed Task snapshot, retaining the Task's own identity and version."""

    task_id: TaskId
    observed_task_version: EntityVersion
    observed_state: TaskState

    def __post_init__(self) -> None:
        super(RunTaskStateObservation, self).__post_init__()
        if not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId")
        if not isinstance(self.observed_task_version, EntityVersion):
            raise InvalidDomainValue("observed_task_version must be an EntityVersion")
        if not isinstance(self.observed_state, TaskState):
            raise InvalidDomainValue("observed_state must be a TaskState")


@dataclass(frozen=True, slots=True)
class RunPrimaryObjectiveStateObservation(_EvidenceBackedRunDecision):
    """Observed primary-Objective relation and snapshot for one Task snapshot."""

    task_id: TaskId
    observed_task_version: EntityVersion
    primary_objective_id: ObjectiveId
    observed_objective_version: EntityVersion
    observed_state: ObjectiveState

    def __post_init__(self) -> None:
        super(RunPrimaryObjectiveStateObservation, self).__post_init__()
        if not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId")
        if not isinstance(self.observed_task_version, EntityVersion):
            raise InvalidDomainValue("observed_task_version must be an EntityVersion")
        if not isinstance(self.primary_objective_id, ObjectiveId):
            raise InvalidDomainValue("primary_objective_id must be an ObjectiveId")
        if not isinstance(self.observed_objective_version, EntityVersion):
            raise InvalidDomainValue(
                "observed_objective_version must be an EntityVersion"
            )
        if not isinstance(self.observed_state, ObjectiveState):
            raise InvalidDomainValue("observed_state must be an ObjectiveState")


@dataclass(frozen=True, slots=True)
class RunExecutionOwnershipDecision(_EvidenceBackedRunDecision):
    """A Task ownership observation that must name this exact Run."""

    task_id: TaskId
    observed_task_version: EntityVersion
    ownership_ref: RunExecutionOwnershipRef
    owner_run_id: RunId

    def __post_init__(self) -> None:
        super(RunExecutionOwnershipDecision, self).__post_init__()
        if not isinstance(self.task_id, TaskId):
            raise InvalidDomainValue("task_id must be a TaskId")
        if not isinstance(self.observed_task_version, EntityVersion):
            raise InvalidDomainValue("observed_task_version must be an EntityVersion")
        if not isinstance(self.ownership_ref, RunExecutionOwnershipRef):
            raise InvalidDomainValue("ownership_ref must be a RunExecutionOwnershipRef")
        if not isinstance(self.owner_run_id, RunId):
            raise InvalidDomainValue("owner_run_id must be a RunId")


@dataclass(frozen=True, slots=True)
class RunCandidateOutcomeObservation(_EvidenceBackedRunDecision):
    """A candidate Outcome observation retaining Outcome identity and version."""

    outcome_id: OutcomeId
    observed_outcome_version: EntityVersion
    originating_run_id: RunId

    def __post_init__(self) -> None:
        super(RunCandidateOutcomeObservation, self).__post_init__()
        if not isinstance(self.outcome_id, OutcomeId):
            raise InvalidDomainValue("outcome_id must be an OutcomeId")
        if not isinstance(self.observed_outcome_version, EntityVersion):
            raise InvalidDomainValue(
                "observed_outcome_version must be an EntityVersion"
            )
        if not isinstance(self.originating_run_id, RunId):
            raise InvalidDomainValue("originating_run_id must be a RunId")


@dataclass(frozen=True, slots=True)
class RunVerificationResolutionDecision:
    """Independent verification resolution, without accepting or rejecting Outcome."""

    decision_ref: RunSemanticDecisionRef
    status: RunVerificationResolutionStatus
    decided_by: ActorIdentity
    evidence_refs: frozenset[EvidenceRef]
    run_id: RunId
    observed_entity_version: EntityVersion
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.decision_ref, RunSemanticDecisionRef):
            raise InvalidDomainValue("decision_ref must be a RunSemanticDecisionRef")
        if not isinstance(self.status, RunVerificationResolutionStatus):
            raise InvalidDomainValue("status must be a RunVerificationResolutionStatus")
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        _require_evidence(self.evidence_refs)
        _require_run_snapshot_scope(
            self.run_id, self.observed_entity_version, self.correlation_id
        )


@dataclass(frozen=True, slots=True)
class RunStartSemantics:
    task: RunTaskStateObservation
    primary_objective: RunPrimaryObjectiveStateObservation
    execution_ownership: RunExecutionOwnershipDecision
    execution_profile: RunExecutionProfileApprovalDecision
    boundary: RunExecutionBoundaryDecision
    grants: RunGrantValidityDecision
    budget: RunBudgetValidityDecision
    start_confirmation: RunTrustedStartConfirmationDecision

    def __post_init__(self) -> None:
        for value, expected, name in (
            (self.task, RunTaskStateObservation, "task"),
            (
                self.primary_objective,
                RunPrimaryObjectiveStateObservation,
                "primary_objective",
            ),
            (self.execution_ownership, RunExecutionOwnershipDecision, "ownership"),
            (
                self.execution_profile,
                RunExecutionProfileApprovalDecision,
                "execution_profile",
            ),
            (self.boundary, RunExecutionBoundaryDecision, "boundary"),
            (self.grants, RunGrantValidityDecision, "grants"),
            (self.budget, RunBudgetValidityDecision, "budget"),
            (
                self.start_confirmation,
                RunTrustedStartConfirmationDecision,
                "start_confirmation",
            ),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue(f"{name} has the wrong decision type")


@dataclass(frozen=True, slots=True)
class RunVerificationWaitSemantics:
    execution_stopped: RunExecutionStoppedDecision
    candidate_outcome: RunCandidateOutcomeObservation
    verification_request: RunVerificationRequestDecision

    def __post_init__(self) -> None:
        for value, expected, name in (
            (self.execution_stopped, RunExecutionStoppedDecision, "execution_stopped"),
            (
                self.candidate_outcome,
                RunCandidateOutcomeObservation,
                "candidate_outcome",
            ),
            (
                self.verification_request,
                RunVerificationRequestDecision,
                "verification_request",
            ),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue(f"{name} has the wrong decision type")


@dataclass(frozen=True, slots=True)
class RunDirectCompletionSemantics:
    normal_termination: RunIndependentNormalTerminationDecision
    artifact_usage_persistence: RunArtifactUsagePersistenceDecision
    no_verification_wait_required: RunNoVerificationWaitRequirementDecision

    def __post_init__(self) -> None:
        for value, expected, name in (
            (
                self.normal_termination,
                RunIndependentNormalTerminationDecision,
                "normal_termination",
            ),
            (
                self.artifact_usage_persistence,
                RunArtifactUsagePersistenceDecision,
                "artifact_usage_persistence",
            ),
            (
                self.no_verification_wait_required,
                RunNoVerificationWaitRequirementDecision,
                "no_verification_wait_required",
            ),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue(f"{name} has the wrong decision type")


@dataclass(frozen=True, slots=True)
class RunVerifiedCompletionSemantics:
    normal_termination: RunIndependentNormalTerminationDecision
    verification_resolution: RunVerificationResolutionDecision
    evidence_retention: RunVerificationEvidenceRetentionDecision

    def __post_init__(self) -> None:
        for value, expected, name in (
            (
                self.normal_termination,
                RunIndependentNormalTerminationDecision,
                "normal_termination",
            ),
            (
                self.verification_resolution,
                RunVerificationResolutionDecision,
                "verification_resolution",
            ),
            (
                self.evidence_retention,
                RunVerificationEvidenceRetentionDecision,
                "evidence_retention",
            ),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue(f"{name} has the wrong decision type")


@dataclass(frozen=True, slots=True)
class RunRetryPreparationSemantics:
    """Canonical semantics for preparing a same-attempt Resume."""

    recoverable_interruption: RunRecoverableInterruptionDecision
    same_attempt_continuity: RunSameAttemptContinuityDecision
    resume_decision: RunResumeDecision
    trusted_recovery_boundary: RunTrustedRecoveryBoundaryDecision
    recovery_limits: RunRecoveryLimitsDecision

    def __post_init__(self) -> None:
        for value, expected, name in (
            (
                self.recoverable_interruption,
                RunRecoverableInterruptionDecision,
                "recoverable_interruption",
            ),
            (
                self.same_attempt_continuity,
                RunSameAttemptContinuityDecision,
                "same_attempt_continuity",
            ),
            (self.resume_decision, RunResumeDecision, "resume_decision"),
            (
                self.trusted_recovery_boundary,
                RunTrustedRecoveryBoundaryDecision,
                "trusted_recovery_boundary",
            ),
            (self.recovery_limits, RunRecoveryLimitsDecision, "recovery_limits"),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue(f"{name} has the wrong decision type")


@dataclass(frozen=True, slots=True)
class RunResumeSemantics:
    """Canonical semantics for re-entering RUNNING on the same Run attempt."""

    same_attempt_continuity: RunSameAttemptContinuityDecision
    resume_decision: RunResumeDecision
    trusted_recovery_boundary: RunTrustedRecoveryBoundaryDecision
    task: RunTaskStateObservation
    primary_objective: RunPrimaryObjectiveStateObservation
    boundary: RunExecutionBoundaryDecision
    grants: RunGrantValidityDecision

    def __post_init__(self) -> None:
        for value, expected, name in (
            (
                self.same_attempt_continuity,
                RunSameAttemptContinuityDecision,
                "same_attempt_continuity",
            ),
            (self.resume_decision, RunResumeDecision, "resume_decision"),
            (
                self.trusted_recovery_boundary,
                RunTrustedRecoveryBoundaryDecision,
                "trusted_recovery_boundary",
            ),
            (self.task, RunTaskStateObservation, "task"),
            (
                self.primary_objective,
                RunPrimaryObjectiveStateObservation,
                "primary_objective",
            ),
            (self.boundary, RunExecutionBoundaryDecision, "boundary"),
            (self.grants, RunGrantValidityDecision, "grants"),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue(f"{name} has the wrong decision type")


type RunSemanticInput = (
    RunStartSemantics
    | RunVerificationWaitSemantics
    | RunDirectCompletionSemantics
    | RunVerifiedCompletionSemantics
    | RunRetryPreparationSemantics
    | RunResumeSemantics
)

type _RunSnapshotBoundSemanticDecision = (
    _EvidenceBackedRunDecision | RunVerificationResolutionDecision
)


def _semantic_decisions_for(
    semantics: RunSemanticInput,
) -> tuple[_RunSnapshotBoundSemanticDecision, ...]:
    if isinstance(semantics, RunStartSemantics):
        return (
            semantics.task,
            semantics.primary_objective,
            semantics.execution_ownership,
            semantics.execution_profile,
            semantics.boundary,
            semantics.grants,
            semantics.budget,
            semantics.start_confirmation,
        )
    if isinstance(semantics, RunVerificationWaitSemantics):
        return (
            semantics.execution_stopped,
            semantics.candidate_outcome,
            semantics.verification_request,
        )
    if isinstance(semantics, RunDirectCompletionSemantics):
        return (
            semantics.normal_termination,
            semantics.artifact_usage_persistence,
            semantics.no_verification_wait_required,
        )
    if isinstance(semantics, RunVerifiedCompletionSemantics):
        return (
            semantics.normal_termination,
            semantics.verification_resolution,
            semantics.evidence_retention,
        )
    if isinstance(semantics, RunRetryPreparationSemantics):
        return (
            semantics.recoverable_interruption,
            semantics.same_attempt_continuity,
            semantics.resume_decision,
            semantics.trusted_recovery_boundary,
            semantics.recovery_limits,
        )
    return (
        semantics.same_attempt_continuity,
        semantics.resume_decision,
        semantics.trusted_recovery_boundary,
        semantics.task,
        semantics.primary_objective,
        semantics.boundary,
        semantics.grants,
    )


_INPUT_TYPE_BY_EDGE: Final[
    MappingProxyType[tuple[RunState, RunState], type[RunSemanticInput]]
] = MappingProxyType(
    {
        (RunState.PENDING, RunState.RUNNING): RunStartSemantics,
        (RunState.RUNNING, RunState.WAITING_FOR_VERIFICATION): (
            RunVerificationWaitSemantics
        ),
        (RunState.RUNNING, RunState.COMPLETED): RunDirectCompletionSemantics,
        (
            RunState.WAITING_FOR_VERIFICATION,
            RunState.COMPLETED,
        ): RunVerifiedCompletionSemantics,
        (RunState.RUNNING, RunState.RETRYING): RunRetryPreparationSemantics,
        (RunState.RETRYING, RunState.RUNNING): RunResumeSemantics,
    }
)


def _require_passed(decision: _EvidenceBackedRunDecision, condition: str) -> None:
    if decision.status is not RunSemanticDecisionStatus.PASSED:
        raise InvariantViolation(
            f"Run semantic condition is not satisfied: {condition}"
        )


@dataclass(frozen=True, slots=True)
class RunSemanticGuard:
    """Canonical guard for one exact normal Run transition attempt."""

    run_id: RunId
    observed_entity_version: EntityVersion
    prior_state: RunState
    target_state: RunState
    correlation_id: CorrelationId
    semantic_input: RunSemanticInput

    def __post_init__(self) -> None:
        _require_run_snapshot_scope(
            self.run_id, self.observed_entity_version, self.correlation_id
        )
        if not isinstance(self.prior_state, RunState) or not isinstance(
            self.target_state, RunState
        ):
            raise InvalidDomainValue("prior_state and target_state must be RunState")
        expected = _INPUT_TYPE_BY_EDGE.get((self.prior_state, self.target_state))
        if expected is None or not isinstance(self.semantic_input, expected):
            raise InvalidDomainValue(
                "semantic_input must match a canonical normal Run lifecycle edge"
            )

    def validate(
        self,
        run: Run,
        target_state: RunState,
        correlation_id: CorrelationId,
    ) -> None:
        """Validate exact binding and the accepted normal Run semantics."""
        if not isinstance(run, Run):
            raise InvalidDomainValue("run must be a Run")
        if not isinstance(target_state, RunState):
            raise InvalidDomainValue("target_state must be a RunState")
        if not isinstance(correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if not (
            self.run_id == run.run_id
            and self.observed_entity_version == run.version
            and self.prior_state is run.state
            and self.target_state is target_state
            and self.correlation_id == correlation_id
        ):
            raise InvariantViolation(
                "Run semantic guard does not match the exact request snapshot"
            )
        for decision in _semantic_decisions_for(self.semantic_input):
            if not (
                decision.run_id == self.run_id
                and decision.observed_entity_version == self.observed_entity_version
                and decision.correlation_id == self.correlation_id
            ):
                raise InvariantViolation(
                    "Run semantic decision does not match the exact request snapshot"
                )

        semantics = self.semantic_input
        if isinstance(semantics, RunStartSemantics):
            self._validate_start(run, semantics)
        elif isinstance(semantics, RunVerificationWaitSemantics):
            self._validate_verification_wait(run, semantics)
        elif isinstance(semantics, RunDirectCompletionSemantics):
            self._validate_direct_completion(semantics)
        elif isinstance(semantics, RunVerifiedCompletionSemantics):
            self._validate_verified_completion(semantics)
        elif isinstance(semantics, RunRetryPreparationSemantics):
            self._validate_retry_preparation(run, semantics)
        else:
            self._validate_resume(run, semantics)

    @staticmethod
    def _validate_start(run: Run, semantics: RunStartSemantics) -> None:
        task = semantics.task
        _require_passed(task, "Task IN_PROGRESS observation")
        if task.task_id != run.task_id:
            raise InvariantViolation("Task observation does not identify the Run Task")
        if task.observed_state is not TaskState.IN_PROGRESS:
            raise InvariantViolation("Run Task is not IN_PROGRESS")

        objective = semantics.primary_objective
        _require_passed(objective, "primary Objective observation")
        if (
            objective.task_id != task.task_id
            or objective.observed_task_version != task.observed_task_version
        ):
            raise InvariantViolation(
                "Primary Objective observation does not match the observed Task "
                "snapshot"
            )
        if objective.observed_state is not ObjectiveState.ACTIVE:
            raise InvariantViolation("Run primary Objective is not ACTIVE")

        ownership = semantics.execution_ownership
        _require_passed(ownership, "valid execution ownership")
        if (
            ownership.task_id != task.task_id
            or ownership.observed_task_version != task.observed_task_version
            or ownership.owner_run_id != run.run_id
        ):
            raise InvariantViolation(
                "Execution ownership does not match the observed Task and Run"
            )

        _require_passed(semantics.execution_profile, "execution profile approval")
        if (
            semantics.execution_profile.execution_profile_ref
            != run.execution_profile_ref
        ):
            raise InvariantViolation(
                "Execution profile approval does not match the Run execution profile"
            )
        _require_passed(semantics.boundary, "approved execution boundary")
        _require_passed(semantics.grants, "current execution grants")
        _require_passed(semantics.budget, "applicable budget validity")
        _require_passed(semantics.start_confirmation, "trusted start confirmation")
        if semantics.start_confirmation.decided_by.actor_type is ActorType.WORKER:
            raise InvariantViolation("Worker start confirmation is not trusted")

    @staticmethod
    def _validate_verification_wait(
        run: Run, semantics: RunVerificationWaitSemantics
    ) -> None:
        _require_passed(semantics.execution_stopped, "stopped execution")
        candidate = semantics.candidate_outcome
        _require_passed(candidate, "candidate Outcome observation")
        if candidate.originating_run_id != run.run_id:
            raise InvariantViolation(
                "Candidate Outcome does not originate from this Run"
            )
        _require_passed(semantics.verification_request, "explicit verification request")

    @staticmethod
    def _validate_direct_completion(
        semantics: RunDirectCompletionSemantics,
    ) -> None:
        _require_passed(semantics.normal_termination, "normal termination evidence")
        if semantics.normal_termination.decided_by.actor_type is ActorType.WORKER:
            raise InvariantViolation(
                "Worker normal-termination claim is not independent"
            )
        _require_passed(
            semantics.artifact_usage_persistence,
            "artifact and usage persistence",
        )
        _require_passed(
            semantics.no_verification_wait_required,
            "no Run-level verification wait requirement",
        )

    @staticmethod
    def _validate_verified_completion(
        semantics: RunVerifiedCompletionSemantics,
    ) -> None:
        _require_passed(semantics.normal_termination, "normal termination evidence")
        if semantics.normal_termination.decided_by.actor_type is ActorType.WORKER:
            raise InvariantViolation(
                "Worker normal-termination claim is not independent"
            )
        if semantics.verification_resolution.status not in {
            RunVerificationResolutionStatus.RESOLVED_FAVORABLE,
            RunVerificationResolutionStatus.RESOLVED_UNFAVORABLE,
        }:
            raise InvariantViolation("Required verification is not resolved")
        if semantics.verification_resolution.decided_by.actor_type is ActorType.WORKER:
            raise InvariantViolation(
                "Worker verification resolution is not independent"
            )
        _require_passed(semantics.evidence_retention, "retained verification evidence")

    @staticmethod
    def _validate_same_attempt_continuity(
        run: Run,
        continuity: RunSameAttemptContinuityDecision,
    ) -> None:
        _require_passed(continuity, "same-attempt path and strategy continuity")
        if (
            continuity.task_id != run.task_id
            or continuity.predecessor_run_id != run.predecessor_run_id
            or continuity.execution_profile_ref != run.execution_profile_ref
        ):
            raise InvariantViolation(
                "Same-attempt continuity does not match the Run identity and strategy"
            )

    @staticmethod
    def _validate_resume_decision(
        resume_decision: RunResumeDecision,
    ) -> None:
        _require_passed(resume_decision, "explicit scoped Resume decision")
        if resume_decision.decided_by.actor_type is ActorType.WORKER:
            raise InvariantViolation("Worker cannot authoritatively select Resume")

    @staticmethod
    def _validate_trusted_recovery_boundary(
        recovery_boundary: RunTrustedRecoveryBoundaryDecision,
    ) -> None:
        _require_passed(recovery_boundary, "trusted recovery-boundary provenance")
        if recovery_boundary.decided_by.actor_type is ActorType.WORKER:
            raise InvariantViolation("Worker recovery-boundary claim is not trusted")

    @classmethod
    def _validate_active_task_and_primary_objective(
        cls,
        run: Run,
        task: RunTaskStateObservation,
        objective: RunPrimaryObjectiveStateObservation,
    ) -> None:
        _require_passed(task, "Task IN_PROGRESS observation")
        if task.task_id != run.task_id:
            raise InvariantViolation("Task observation does not identify the Run Task")
        if task.observed_state is not TaskState.IN_PROGRESS:
            raise InvariantViolation("Run Task is not IN_PROGRESS")
        _require_passed(objective, "primary Objective observation")
        if (
            objective.task_id != task.task_id
            or objective.observed_task_version != task.observed_task_version
        ):
            raise InvariantViolation(
                "Primary Objective observation does not match the observed Task "
                "snapshot"
            )
        if objective.observed_state is not ObjectiveState.ACTIVE:
            raise InvariantViolation("Run primary Objective is not ACTIVE")

    @classmethod
    def _validate_retry_preparation(
        cls,
        run: Run,
        semantics: RunRetryPreparationSemantics,
    ) -> None:
        _require_passed(semantics.recoverable_interruption, "recoverable interruption")
        cls._validate_same_attempt_continuity(run, semantics.same_attempt_continuity)
        cls._validate_resume_decision(semantics.resume_decision)
        cls._validate_trusted_recovery_boundary(semantics.trusted_recovery_boundary)
        _require_passed(semantics.recovery_limits, "remaining recovery limits")

    @classmethod
    def _validate_resume(cls, run: Run, semantics: RunResumeSemantics) -> None:
        cls._validate_same_attempt_continuity(run, semantics.same_attempt_continuity)
        cls._validate_resume_decision(semantics.resume_decision)
        cls._validate_trusted_recovery_boundary(semantics.trusted_recovery_boundary)
        cls._validate_active_task_and_primary_objective(
            run, semantics.task, semantics.primary_objective
        )
        _require_passed(semantics.boundary, "approved execution boundary")
        _require_passed(semantics.grants, "current execution grants")
