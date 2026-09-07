"""Evaluation snapshots and structural topology; no verification or history engine."""

from dataclasses import dataclass
from enum import Enum
from typing import Final

from .actors import ActorIdentity
from .errors import InvalidDomainValue
from .evaluation_result import EvaluationMethodRef, EvaluationResult
from .evaluation_target import EvaluationTargetRef
from .ids import EvaluationId
from .version import EntityVersion


class EvaluationState(Enum):
    """Lifecycle labels, distinct from the content of a verification judgment."""

    PENDING = "PENDING"  # Requested, potentially without an assigned verifier.
    RUNNING = "RUNNING"  # Verification in progress; no completed result recorded.
    COMPLETED = "COMPLETED"  # A recorded result exists, not necessarily favorable.
    CONFLICTED = "CONFLICTED"  # Material conflict; membership records come in M5B.
    ARBITRATED = "ARBITRATED"  # Arbitration occurred; records/dispositions come in M5C.
    INVALID = "INVALID"  # Unusable Evaluation, not a negative verdict.


@dataclass(frozen=True, slots=True)
class Evaluation:
    """An immutable snapshot retaining original content and verifier provenance.

    Construction does not perform verification, authorize a transition or append
    history. Cross-record independence and no-delete enforcement remain deferred.
    """

    evaluation_id: EvaluationId
    state: EvaluationState
    version: EntityVersion
    target: EvaluationTargetRef
    method: EvaluationMethodRef
    verifier: ActorIdentity | None = None
    result: EvaluationResult | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.evaluation_id, EvaluationId):
            raise InvalidDomainValue("evaluation_id must be an EvaluationId")
        if not isinstance(self.state, EvaluationState):
            raise InvalidDomainValue("state must be an EvaluationState")
        if not isinstance(self.version, EntityVersion):
            raise InvalidDomainValue("version must be an EntityVersion")
        if not isinstance(self.target, EvaluationTargetRef):
            raise InvalidDomainValue("target must be an EvaluationTargetRef")
        if not isinstance(self.method, EvaluationMethodRef):
            raise InvalidDomainValue("method must be an EvaluationMethodRef")
        if self.verifier is not None and not isinstance(self.verifier, ActorIdentity):
            raise InvalidDomainValue("verifier must be an ActorIdentity or None")
        if self.result is not None and not isinstance(self.result, EvaluationResult):
            raise InvalidDomainValue("result must be an EvaluationResult or None")
        if self.state in (EvaluationState.PENDING, EvaluationState.RUNNING):
            if self.result is not None:
                raise InvalidDomainValue(
                    "PENDING and RUNNING snapshots cannot have a result"
                )
        elif self.state is EvaluationState.COMPLETED and self.result is None:
            raise InvalidDomainValue("A COMPLETED snapshot requires an original result")


EVALUATION_CREATION_STATE: Final[EvaluationState] = EvaluationState.PENDING

_EVALUATION_TRANSITIONS: Final[frozenset[tuple[EvaluationState, EvaluationState]]] = (
    frozenset(
        {
            (EvaluationState.PENDING, EvaluationState.RUNNING),
            (EvaluationState.RUNNING, EvaluationState.COMPLETED),
            (EvaluationState.RUNNING, EvaluationState.CONFLICTED),
            (EvaluationState.COMPLETED, EvaluationState.CONFLICTED),
            (EvaluationState.COMPLETED, EvaluationState.ARBITRATED),
            (EvaluationState.CONFLICTED, EvaluationState.ARBITRATED),
            (EvaluationState.PENDING, EvaluationState.INVALID),
            (EvaluationState.RUNNING, EvaluationState.INVALID),
            (EvaluationState.COMPLETED, EvaluationState.INVALID),
            (EvaluationState.CONFLICTED, EvaluationState.INVALID),
        }
    )
)


def can_evaluation_transition(source: EvaluationState, target: EvaluationState) -> bool:
    """Return structural membership only, never verification or authority.

    No target lookup, result judgment, conflict resolution, arbitration,
    invalidation analysis, version mutation, persistence or events occur here.
    """
    if not isinstance(source, EvaluationState) or not isinstance(
        target, EvaluationState
    ):
        raise InvalidDomainValue("source and target must be EvaluationState values")
    return (source, target) in _EVALUATION_TRANSITIONS
