"""Public embedded governance facade over the accepted Stage 1 kernel."""

from typing import Never

from symphony_k.domain import (
    CreationContext,
    DomainError,
    EffectId,
    Evaluation,
    EvaluationId,
    EvaluationPendingCreationRequest,
    EvaluationState,
    EvaluationTargetRef,
    ObjectiveId,
    Outcome,
    OutcomeId,
    OutcomeProposedCreationRequest,
    OutcomeState,
    Run,
    RunId,
    RunPendingCreationRequest,
    TaskId,
    TransitionContext,
    TransitionRequest,
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

from .binding import (
    TrustedEvaluationBinding,
    TrustedEvaluationTransitionBinding,
    TrustedGovernanceBinder,
    TrustedOutcomeBinding,
    TrustedRunBinding,
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
        trusted_binder: TrustedGovernanceBinder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._objectives = objectives
        self._tasks = tasks
        self._runs = runs
        self._outcomes = outcomes
        self._evaluations = evaluations
        self._effects = effects
        self._trusted_binder = trusted_binder

    def submit_run_candidate(
        self, submission: RunCandidateSubmission
    ) -> MutationResult[Run, RunRef]:
        """Register one PENDING attempt through canonical Stage 1 creation."""
        if not isinstance(submission, RunCandidateSubmission):
            raise InvalidRequestError("Expected RunCandidateSubmission")
        binder = self._require_binder()
        try:
            binding = binder.bind_run_candidate(submission)
        except DomainError as error:
            self._raise(error)
        if not isinstance(binding, TrustedRunBinding):
            raise GovernanceInvariantError(
                "Trusted binder returned an invalid Run binding"
            )
        request = binding.request
        context = binding.context
        self._require_creation_binding(request, context, RunPendingCreationRequest)
        if not (
            request.event_id == submission.event_id
            and request.entity_id == submission.run_id
            and request.requested_by == submission.caller_identity_claim
            and request.reason == submission.reason
            and request.timestamp == submission.timestamp
            and request.correlation_id == submission.correlation_id
            and request.causation_id == submission.causation_id
            and request.entity_spec.task_id == submission.task.task_id
            and request.entity_spec.execution_profile_ref
            == submission.execution_profile_ref
            and request.entity_spec.predecessor_run_id
            == (
                submission.predecessor.run_id
                if submission.predecessor is not None
                else None
            )
        ):
            raise InvalidRequestError(
                "Trusted Run binding changed caller-controlled input"
            )
        scope = request.semantic_input.registration
        if scope is None:
            raise GovernanceInvariantError("Trusted Run binding lacks registration")
        self._require_observation(scope.task.snapshot, submission.task)
        self._require_observation(
            scope.primary_objective.snapshot, submission.primary_objective
        )
        if submission.predecessor is not None:
            if not scope.predecessor_lineage:
                raise InvalidRequestError(
                    "Trusted Run binding lacks the immediate predecessor observation"
                )
            self._require_observation(
                scope.predecessor_lineage[0].snapshot,
                submission.predecessor,
            )
        try:
            result = self._unit_of_work.create(request, context)
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
        binder = self._require_binder()
        try:
            binding = binder.bind_outcome_candidate(submission)
        except DomainError as error:
            self._raise(error)
        if not isinstance(binding, TrustedOutcomeBinding):
            raise GovernanceInvariantError(
                "Trusted binder returned an invalid Outcome binding"
            )
        request = binding.request
        context = binding.context
        self._require_creation_binding(request, context, OutcomeProposedCreationRequest)
        spec = request.entity_spec
        if not (
            request.event_id == submission.event_id
            and request.entity_id == submission.outcome_id
            and request.requested_by == submission.caller_identity_claim
            and request.reason == submission.reason
            and request.timestamp == submission.timestamp
            and request.correlation_id == submission.correlation_id
            and request.causation_id == submission.causation_id
            and spec.run_id == submission.run.run_id
            and spec.producer == submission.producer_identity_claim
            and spec.artifact_refs == submission.artifact_refs
            and spec.evidence_refs == submission.evidence_refs
            and spec.valid_until == submission.valid_until
            and spec.prior_outcome_id
            == (
                submission.prior_outcome.outcome_id
                if submission.prior_outcome is not None
                else None
            )
        ):
            raise InvalidRequestError(
                "Trusted Outcome binding changed caller-controlled input"
            )
        scope = request.semantic_input.proposal
        if scope is None:
            raise GovernanceInvariantError("Trusted Outcome binding lacks proposal")
        self._require_observation(scope.originating_run.snapshot, submission.run)
        if submission.prior_outcome is not None:
            if not scope.prior_lineage:
                raise InvalidRequestError(
                    "Trusted Outcome binding lacks the immediate prior observation"
                )
            self._require_observation(
                scope.prior_lineage[0].snapshot,
                submission.prior_outcome,
            )
        try:
            result = self._unit_of_work.create(request, context)
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
        binder = self._require_binder()
        try:
            binding = binder.bind_evaluation(submission)
        except DomainError as error:
            self._raise(error)
        if not isinstance(binding, TrustedEvaluationBinding):
            raise GovernanceInvariantError(
                "Trusted binder returned an invalid Evaluation binding"
            )
        request = binding.request
        context = binding.context
        self._require_creation_binding(
            request, context, EvaluationPendingCreationRequest
        )
        scope = request.semantic_input.validation
        if scope is None or scope.target_observation is None:
            raise GovernanceInvariantError(
                "Trusted Evaluation binding requires an entity target observation"
            )
        expected_target = self._evaluation_target(submission.target)
        if not (
            request.event_id == submission.event_id
            and request.entity_id == submission.evaluation_id
            and request.requested_by == submission.caller_identity_claim
            and request.reason == submission.reason
            and request.timestamp == submission.timestamp
            and request.correlation_id == submission.correlation_id
            and request.causation_id == submission.causation_id
            and request.entity_spec.target == expected_target
            and request.entity_spec.method == submission.method
            and scope.artifact_refs == submission.artifact_refs
            and scope.evidence_refs == submission.evidence_refs
            and scope.producing_principals == submission.producing_identity_claims
        ):
            raise InvalidRequestError(
                "Trusted Evaluation binding changed caller-controlled input"
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
            result = self._unit_of_work.create(request, context)
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
        binder = self._require_binder()
        try:
            binding = binder.bind_evaluation_transition(submission)
        except DomainError as error:
            self._raise(error)
        if not isinstance(binding, TrustedEvaluationTransitionBinding):
            raise GovernanceInvariantError(
                "Trusted binder returned an invalid Evaluation transition binding"
            )
        request = binding.request
        context = binding.context
        self._require_transition_binding(request, context)
        if not (
            request.event_id == submission.event_id
            and request.target_state is submission.target_state
            and request.actor == submission.caller_identity_claim
            and request.reason == submission.reason
            and request.expected_version == submission.evaluation.version
            and request.timestamp == submission.timestamp
            and request.correlation_id == submission.correlation_id
            and request.causation_id == submission.causation_id
        ):
            raise InvalidRequestError(
                "Trusted Evaluation transition changed caller-controlled input"
            )
        guard = context.evaluation_semantic_guard
        if submission.target_state is EvaluationState.COMPLETED:
            if guard is None:
                raise GovernanceInvariantError(
                    "Trusted Evaluation completion binding lacks a semantic guard"
                )
            try:
                bound_result = guard.validated_completion_result()
            except DomainError as error:
                self._raise(error)
            if bound_result != submission.result_claim:
                raise InvalidRequestError(
                    "Trusted Evaluation binding changed the submitted result claim"
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
                request,
                context,
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

    def _require_binder(self) -> TrustedGovernanceBinder:
        if self._trusted_binder is None:
            raise UnsupportedOperationError(
                "Mutation requires an injected trusted governance binder"
            )
        return self._trusted_binder

    @staticmethod
    def _require_creation_binding(
        request: object, context: object, request_type: type
    ) -> None:
        if not isinstance(request, request_type) or not isinstance(
            context, CreationContext
        ):
            raise GovernanceInvariantError(
                "Trusted binder returned an invalid creation binding"
            )

    @staticmethod
    def _require_transition_binding(request: object, context: object) -> None:
        if not isinstance(request, TransitionRequest) or not isinstance(
            context, TransitionContext
        ):
            raise GovernanceInvariantError(
                "Trusted binder returned an invalid transition binding"
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
