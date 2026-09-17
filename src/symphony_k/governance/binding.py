"""Injected trusted boundary for canonical Stage 1 request construction."""

from dataclasses import dataclass
from typing import Protocol

from symphony_k.domain import (
    CreationContext,
    EvaluationPendingCreationRequest,
    EvaluationState,
    OutcomeProposedCreationRequest,
    RunPendingCreationRequest,
    TransitionContext,
    TransitionRequest,
)

from .types import (
    EvaluationSubmission,
    EvaluationTransitionSubmission,
    OutcomeCandidateSubmission,
    RunCandidateSubmission,
)


@dataclass(frozen=True, slots=True)
class TrustedRunBinding:
    request: RunPendingCreationRequest
    context: CreationContext


@dataclass(frozen=True, slots=True)
class TrustedOutcomeBinding:
    request: OutcomeProposedCreationRequest
    context: CreationContext


@dataclass(frozen=True, slots=True)
class TrustedEvaluationBinding:
    request: EvaluationPendingCreationRequest
    context: CreationContext


@dataclass(frozen=True, slots=True)
class TrustedEvaluationTransitionBinding:
    request: TransitionRequest[EvaluationState]
    context: TransitionContext


class TrustedGovernanceBinder(Protocol):
    """Boundary-owned provider of authenticated authority and provenance."""

    def bind_run_candidate(
        self, submission: RunCandidateSubmission
    ) -> TrustedRunBinding: ...

    def bind_outcome_candidate(
        self, submission: OutcomeCandidateSubmission
    ) -> TrustedOutcomeBinding: ...

    def bind_evaluation(
        self, submission: EvaluationSubmission
    ) -> TrustedEvaluationBinding: ...

    def bind_evaluation_transition(
        self, submission: EvaluationTransitionSubmission
    ) -> TrustedEvaluationTransitionBinding: ...
