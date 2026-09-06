"""Immutable untrusted candidate snapshots and structural Outcome topology.

Producer identity and content references are provenance, not acceptance authority
or verified truth. M7 will enforce authority/guards; no transition runs here.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final

from .actors import ActorIdentity
from .candidate_refs import ArtifactRef, EvidenceRef
from .errors import InvalidDomainValue
from .ids import OutcomeId, RunId
from .time import Timestamp
from .version import EntityVersion


class OutcomeState(Enum):
    """Candidate lifecycle labels, not proof of the justification behind them."""

    PROPOSED = "PROPOSED"  # A candidate exists but is not trusted.
    VALIDATING = "VALIDATING"  # Verification is in progress, not necessarily favorable.
    ACCEPTED = "ACCEPTED"  # Independently validated and accepted according to policy.
    REJECTED = "REJECTED"  # Verification/arbitration found the candidate unacceptable.
    SUPERSEDED = "SUPERSEDED"  # Replaced by a distinct candidate, preserving history.
    EXPIRED = "EXPIRED"  # Time, assumptions, dependencies or external conditions stale.


@dataclass(frozen=True, slots=True)
class Outcome:
    """A candidate snapshot with one originating RunId and no Task ownership.

    State/version are explicit. Constructing a snapshot is not authoritative
    creation, validation or acceptance; no producer/Run/content lookup occurs.
    """

    outcome_id: OutcomeId
    run_id: RunId
    state: OutcomeState
    version: EntityVersion
    producer: ActorIdentity
    artifact_refs: frozenset[ArtifactRef]
    evidence_refs: frozenset[EvidenceRef] = frozenset()
    valid_until: Timestamp | None = None
    prior_outcome_id: OutcomeId | None = None
    superseded_by_outcome_id: OutcomeId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.outcome_id, OutcomeId):
            raise InvalidDomainValue("outcome_id must be an OutcomeId")
        if not isinstance(self.run_id, RunId):
            raise InvalidDomainValue("run_id must be a RunId")
        if not isinstance(self.state, OutcomeState):
            raise InvalidDomainValue("state must be an OutcomeState")
        if not isinstance(self.version, EntityVersion):
            raise InvalidDomainValue("version must be an EntityVersion")
        if not isinstance(self.producer, ActorIdentity):
            raise InvalidDomainValue("producer must be an ActorIdentity")
        if not isinstance(self.artifact_refs, frozenset) or not self.artifact_refs:
            raise InvalidDomainValue("artifact_refs must be a nonempty frozenset")
        if any(
            not isinstance(reference, ArtifactRef) for reference in self.artifact_refs
        ):
            raise InvalidDomainValue("Every artifact reference must be an ArtifactRef")
        if not isinstance(self.evidence_refs, frozenset):
            raise InvalidDomainValue("evidence_refs must be a frozenset")
        if any(
            not isinstance(reference, EvidenceRef) for reference in self.evidence_refs
        ):
            raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")
        if self.valid_until is not None and not isinstance(self.valid_until, Timestamp):
            raise InvalidDomainValue("valid_until must be a Timestamp or None")
        for name, identity in (
            ("prior_outcome_id", self.prior_outcome_id),
            ("superseded_by_outcome_id", self.superseded_by_outcome_id),
        ):
            if identity is not None:
                if not isinstance(identity, OutcomeId):
                    raise InvalidDomainValue(f"{name} must be an OutcomeId or None")
                if identity == self.outcome_id:
                    raise InvalidDomainValue(f"{name} cannot reference this Outcome")
        if (
            self.state is OutcomeState.SUPERSEDED
            and self.superseded_by_outcome_id is None
        ):
            raise InvalidDomainValue(
                "A SUPERSEDED snapshot must retain its replacement ID"
            )


# Creation registers an untrusted candidate; no acceptance or version is assigned.
OUTCOME_CREATION_STATE: Final[OutcomeState] = OutcomeState.PROPOSED

_OUTCOME_TRANSITIONS: Final[frozenset[tuple[OutcomeState, OutcomeState]]] = frozenset(
    {
        (OutcomeState.PROPOSED, OutcomeState.VALIDATING),
        (OutcomeState.VALIDATING, OutcomeState.ACCEPTED),
        (OutcomeState.VALIDATING, OutcomeState.REJECTED),
        (OutcomeState.PROPOSED, OutcomeState.SUPERSEDED),
        (OutcomeState.VALIDATING, OutcomeState.SUPERSEDED),
        (OutcomeState.ACCEPTED, OutcomeState.SUPERSEDED),
        (OutcomeState.REJECTED, OutcomeState.SUPERSEDED),
        (OutcomeState.PROPOSED, OutcomeState.EXPIRED),
        (OutcomeState.VALIDATING, OutcomeState.EXPIRED),
        (OutcomeState.ACCEPTED, OutcomeState.EXPIRED),
        (OutcomeState.REJECTED, OutcomeState.EXPIRED),
    }
)


def can_outcome_transition(source: OutcomeState, target: OutcomeState) -> bool:
    """Return structural membership, not authority, verification or acceptance.

    No actor, Run, Task, Evaluation, policy, content, lineage or clock is read.
    True does not authorize a transition or establish the candidate as trusted.
    """
    if not isinstance(source, OutcomeState) or not isinstance(target, OutcomeState):
        raise InvalidDomainValue("source and target must be OutcomeState values")
    return (source, target) in _OUTCOME_TRANSITIONS
