"""Public embedded governance facade over the accepted Stage 1 kernel."""

from typing import Never

from symphony_k.domain import (
    DomainError,
    EffectId,
    Evaluation,
    EvaluationId,
    EvaluationTargetRef,
    ObjectiveId,
    Outcome,
    OutcomeId,
    OutcomeState,
    Run,
    RunId,
    TaskId,
)
from symphony_k.domain.transition_engine import LifecycleEntityId
from symphony_k.persistence.ports import (
    EffectRepository,
    EvaluationRepository,
    ObjectiveRepository,
    OutcomeRepository,
    RunRepository,
    TaskRepository,
    UnitOfWork,
)

from .errors import (
    ConflictError,
    GovernanceInvariantError,
    InvalidRequestError,
    UnsupportedOperationError,
    translate_domain_error,
)
from .types import (
    AuthoritativeSnapshot,
    EffectRef,
    EntityReference,
    EvaluationRef,
    EvaluationSubmission,
    EvaluationTargetReference,
    EvaluationTransitionSubmission,
    GovernanceEntity,
    MutationResult,
    ObjectiveRef,
    OutcomeCandidateSubmission,
    OutcomeRef,
    RunCandidateSubmission,
    RunRef,
    TaskRef,
    reference_of,
)


class GovernanceFacade:
    """A narrow public boundary that never grants candidate disposition authority."""

    def __init__(
        self,
        *,
        unit_of_work: UnitOfWork,
        objectives: ObjectiveRepository,
        tasks: TaskRepository,
        runs: RunRepository,
        outcomes: OutcomeRepository,
        evaluations: EvaluationRepository,
        effects: EffectRepository,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._objectives = objectives
        self._tasks = tasks
        self._runs = runs
        self._outcomes = outcomes
        self._evaluations = evaluations
        self._effects = effects

    def submit_run_candidate(
        self, submission: RunCandidateSubmission
    ) -> MutationResult[Run, RunRef]:
        """Register one PENDING attempt through canonical Stage 1 creation."""
        if not isinstance(submission, RunCandidateSubmission):
            raise InvalidRequestError("Expected RunCandidateSubmission")
        scope = submission.request.semantic_input.registration
        if scope is None:
            raise InvalidRequestError("Run submission lacks canonical registration")
        self._require_observation(scope.task.snapshot, submission.task)
        self._require_observation(
            scope.primary_objective.snapshot, submission.primary_objective
        )
        if submission.request.entity_spec.task_id != submission.task.task_id:
            raise InvalidRequestError("Run request does not match its exact TaskRef")
        try:
            result = self._unit_of_work.create(submission.request, submission.context)
        except DomainError as error:
            self._raise(error)
        entity = result.entity
        if not isinstance(entity, Run):
            raise GovernanceInvariantError("Stage 1 returned a non-Run result")
        return MutationResult(
            AuthoritativeSnapshot(reference_of(entity), entity), result.event
        )

    def submit_outcome_candidate(
        self, submission: OutcomeCandidateSubmission
    ) -> MutationResult[Outcome, OutcomeRef]:
        """Persist one PROPOSED candidate without accepting or completing it."""
        if not isinstance(submission, OutcomeCandidateSubmission):
            raise InvalidRequestError("Expected OutcomeCandidateSubmission")
        scope = submission.request.semantic_input.proposal
        if scope is None:
            raise InvalidRequestError("Outcome submission lacks canonical proposal")
        self._require_observation(scope.originating_run.snapshot, submission.run)
        if submission.request.entity_spec.run_id != submission.run.run_id:
            raise InvalidRequestError("Outcome request does not match its exact RunRef")
        try:
            result = self._unit_of_work.create(submission.request, submission.context)
        except DomainError as error:
            self._raise(error)
        entity = result.entity
        if not isinstance(entity, Outcome):
            raise GovernanceInvariantError("Stage 1 returned a non-Outcome result")
        return MutationResult(
            AuthoritativeSnapshot(reference_of(entity), entity), result.event
        )

    def submit_evaluation(
        self, submission: EvaluationSubmission
    ) -> MutationResult[Evaluation, EvaluationRef]:
        """Create a PENDING independently scoped Evaluation request."""
        if not isinstance(submission, EvaluationSubmission):
            raise InvalidRequestError("Expected EvaluationSubmission")
        scope = submission.request.semantic_input.validation
        if scope is None or scope.target_observation is None:
            raise InvalidRequestError(
                "Facade Evaluation submission requires an entity target observation"
            )
        expected_target = self._evaluation_target(submission.target)
        if submission.request.entity_spec.target != expected_target:
            raise InvalidRequestError(
                "Evaluation request does not match its exact target reference"
            )
        self._require_observation(scope.target_observation.snapshot, submission.target)
        observed = scope.target_observation.snapshot
        if isinstance(observed, Outcome) and observed.state in {
            OutcomeState.SUPERSEDED,
            OutcomeState.EXPIRED,
        }:
            raise ConflictError(
                "Superseded or expired Outcome is not a current candidate"
            )
        try:
            result = self._unit_of_work.create(submission.request, submission.context)
        except DomainError as error:
            self._raise(error)
        entity = result.entity
        if not isinstance(entity, Evaluation):
            raise GovernanceInvariantError("Stage 1 returned a non-Evaluation result")
        return MutationResult(
            AuthoritativeSnapshot(reference_of(entity), entity), result.event
        )

    def advance_evaluation(
        self, submission: EvaluationTransitionSubmission
    ) -> MutationResult[Evaluation, EvaluationRef]:
        """Start or complete an Evaluation through canonical authority and guards."""
        if not isinstance(submission, EvaluationTransitionSubmission):
            raise InvalidRequestError("Expected EvaluationTransitionSubmission")
        if submission.request.expected_version != submission.evaluation.version:
            raise InvalidRequestError(
                "Evaluation request expected_version must match EvaluationRef"
            )
        try:
            historical = self._evaluations.load_version(
                submission.evaluation.evaluation_id,
                submission.evaluation.version,
            )
            if historical.target != self._evaluation_target(submission.target):
                raise InvalidRequestError(
                    "Evaluation transition target does not match persisted Evaluation"
                )
            result = self._unit_of_work.transition(
                submission.evaluation.evaluation_id,
                submission.request,
                submission.context,
            )
        except DomainError as error:
            self._raise(error)
        entity = result.entity
        if not isinstance(entity, Evaluation):
            raise GovernanceInvariantError("Stage 1 returned a non-Evaluation result")
        return MutationResult(
            AuthoritativeSnapshot(reference_of(entity), entity), result.event
        )

    def read_current(
        self, entity_id: LifecycleEntityId
    ) -> AuthoritativeSnapshot[GovernanceEntity, EntityReference]:
        """Read the authoritative head without exposing private storage records."""
        try:
            entity = self._load_current(entity_id)
        except DomainError as error:
            self._raise(error)
        return AuthoritativeSnapshot(reference_of(entity), entity)

    def read(
        self, reference: EntityReference
    ) -> AuthoritativeSnapshot[GovernanceEntity, EntityReference]:
        """Read the exact durable version named by a public reference."""
        if not isinstance(
            reference,
            (ObjectiveRef, TaskRef, RunRef, OutcomeRef, EvaluationRef, EffectRef),
        ):
            raise InvalidRequestError("Expected an exact governance reference")
        try:
            entity = self._load_version(reference)
        except DomainError as error:
            self._raise(error)
        return AuthoritativeSnapshot(reference_of(entity), entity)

    def dispatch_effect(self, effect: EffectRef) -> Never:
        """Fail closed until a separately governed real Effect gateway exists."""
        if not isinstance(effect, EffectRef):
            raise InvalidRequestError("Effect dispatch requires an exact EffectRef")
        raise UnsupportedOperationError(
            "Real Effect dispatch is not available in the G1/M1 facade"
        )

    def _load_current(self, entity_id: LifecycleEntityId) -> GovernanceEntity:
        if isinstance(entity_id, ObjectiveId):
            return self._objectives.load(entity_id)
        if isinstance(entity_id, TaskId):
            return self._tasks.load(entity_id)
        if isinstance(entity_id, RunId):
            return self._runs.load(entity_id)
        if isinstance(entity_id, OutcomeId):
            return self._outcomes.load(entity_id)
        if isinstance(entity_id, EvaluationId):
            return self._evaluations.load(entity_id)
        if isinstance(entity_id, EffectId):
            return self._effects.load(entity_id)
        raise InvalidRequestError("Expected a typed lifecycle entity ID")

    def _load_version(self, reference: EntityReference) -> GovernanceEntity:
        if isinstance(reference, ObjectiveRef):
            return self._objectives.load_version(
                reference.objective_id, reference.version
            )
        if isinstance(reference, TaskRef):
            return self._tasks.load_version(reference.task_id, reference.version)
        if isinstance(reference, RunRef):
            return self._runs.load_version(reference.run_id, reference.version)
        if isinstance(reference, OutcomeRef):
            return self._outcomes.load_version(reference.outcome_id, reference.version)
        if isinstance(reference, EvaluationRef):
            return self._evaluations.load_version(
                reference.evaluation_id, reference.version
            )
        return self._effects.load_version(reference.effect_id, reference.version)

    @staticmethod
    def _evaluation_target(reference: EvaluationTargetReference) -> EvaluationTargetRef:
        if isinstance(reference, RunRef):
            return EvaluationTargetRef(reference.run_id, reference.version)
        if isinstance(reference, OutcomeRef):
            return EvaluationTargetRef(reference.outcome_id, reference.version)
        return EvaluationTargetRef(reference.effect_id, reference.version)

    @staticmethod
    def _require_observation(
        snapshot: GovernanceEntity | None, reference: EntityReference
    ) -> None:
        if snapshot is None or reference_of(snapshot) != reference:
            raise InvalidRequestError(
                "Submission observation does not match its exact public reference"
            )

    @staticmethod
    def _raise(error: DomainError) -> Never:
        translated = translate_domain_error(error)
        raise translated from error
