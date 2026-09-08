"""Immutable Evaluation invalidation provenance and structural compatibility."""

from dataclasses import dataclass
from typing import Final

from .actors import ActorIdentity
from .candidate_refs import EvidenceRef
from .errors import InvalidDomainValue
from .evaluation import Evaluation, EvaluationState
from .ids import CorrelationId, EvaluationId, EvaluationInvalidationId
from .time import Timestamp
from .version import EntityVersion


@dataclass(frozen=True, slots=True)
class EvaluationInvalidationRecord:
    """Evidence-backed provenance for why one Evaluation snapshot is unusable.

    Construction records a supporting judgment only. It grants no authority and
    performs no Evaluation transition, repository lookup or history resolution.
    """

    invalidation_id: EvaluationInvalidationId
    evaluation_id: EvaluationId
    observed_version: EntityVersion
    reason: str
    evidence_refs: frozenset[EvidenceRef]
    invalidated_by: ActorIdentity
    invalidated_at: Timestamp
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.invalidation_id, EvaluationInvalidationId):
            raise InvalidDomainValue(
                "invalidation_id must be an EvaluationInvalidationId"
            )
        if not isinstance(self.evaluation_id, EvaluationId):
            raise InvalidDomainValue("evaluation_id must be an EvaluationId")
        if not isinstance(self.observed_version, EntityVersion):
            raise InvalidDomainValue("observed_version must be an EntityVersion")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise InvalidDomainValue("reason must contain non-whitespace text")
        if not isinstance(self.evidence_refs, frozenset):
            raise InvalidDomainValue("evidence_refs must be a frozenset")
        if any(
            not isinstance(reference, EvidenceRef) for reference in self.evidence_refs
        ):
            raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")
        if not self.evidence_refs:
            raise InvalidDomainValue(
                "An invalidation record requires at least one EvidenceRef"
            )
        if not isinstance(self.invalidated_by, ActorIdentity):
            raise InvalidDomainValue("invalidated_by must be an ActorIdentity")
        if not isinstance(self.invalidated_at, Timestamp):
            raise InvalidDomainValue("invalidated_at must be a Timestamp")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")


_INVALIDATION_SOURCE_STATES: Final[frozenset[EvaluationState]] = frozenset(
    {
        EvaluationState.PENDING,
        EvaluationState.RUNNING,
        EvaluationState.COMPLETED,
        EvaluationState.CONFLICTED,
    }
)


def can_invalidate_evaluation(
    evaluation: Evaluation,
    invalidation: EvaluationInvalidationRecord,
) -> bool:
    """Return exact snapshot compatibility without proving or applying invalidity."""
    if not isinstance(evaluation, Evaluation) or not isinstance(
        invalidation, EvaluationInvalidationRecord
    ):
        raise InvalidDomainValue(
            "evaluation and invalidation must be their respective record types"
        )
    return (
        invalidation.evaluation_id == evaluation.evaluation_id
        and invalidation.observed_version == evaluation.version
        and evaluation.state in _INVALIDATION_SOURCE_STATES
    )
