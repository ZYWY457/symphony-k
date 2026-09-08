"""Immutable Evaluation arbitration decisions and structural compatibility."""

from dataclasses import dataclass
from enum import Enum

from .actors import ActorIdentity
from .candidate_refs import EvidenceRef
from .errors import InvalidDomainValue
from .evaluation_conflict import (
    EvaluationConflictSetRecord,
    EvaluationConflictSetRef,
)
from .evaluation_result import EvaluationVerdict
from .ids import CorrelationId, EvaluationArbitrationId, EvaluationId
from .time import Timestamp
from .version import EntityVersion


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InvalidDomainValue(f"{field} must contain non-whitespace text")


class ArbitrationDisposition(Enum):
    """How arbitration affects a prior effective judgment; not lifecycle state."""

    UPHELD = "UPHELD"
    MODIFIED = "MODIFIED"
    REVERSED = "REVERSED"


@dataclass(frozen=True, slots=True)
class EvaluationArbitrationPolicyRef:
    """Opaque policy identity/version; it proves no authority or policy result."""

    policy_id: str
    policy_version: str

    def __post_init__(self) -> None:
        _require_text(self.policy_id, "policy_id")
        _require_text(self.policy_version, "policy_version")


@dataclass(frozen=True, slots=True)
class EvaluationArbitrationMemberDecision:
    """An explicit effective judgment for one observed Evaluation projection."""

    evaluation_id: EvaluationId
    observed_version: EntityVersion
    disposition: ArbitrationDisposition
    prior_effective_judgement: EvaluationVerdict | None
    effective_judgement: EvaluationVerdict

    def __post_init__(self) -> None:
        if not isinstance(self.evaluation_id, EvaluationId):
            raise InvalidDomainValue("evaluation_id must be an EvaluationId")
        if not isinstance(self.observed_version, EntityVersion):
            raise InvalidDomainValue("observed_version must be an EntityVersion")
        if not isinstance(self.disposition, ArbitrationDisposition):
            raise InvalidDomainValue("disposition must be an ArbitrationDisposition")
        if self.prior_effective_judgement is not None and not isinstance(
            self.prior_effective_judgement, EvaluationVerdict
        ):
            raise InvalidDomainValue(
                "prior_effective_judgement must be an EvaluationVerdict or None"
            )
        if not isinstance(self.effective_judgement, EvaluationVerdict):
            raise InvalidDomainValue("effective_judgement must be an EvaluationVerdict")

        prior = self.prior_effective_judgement
        effective = self.effective_judgement
        if self.disposition is ArbitrationDisposition.UPHELD:
            if prior is None or effective != prior:
                raise InvalidDomainValue(
                    "UPHELD requires an unchanged prior effective judgement"
                )
        elif self.disposition is ArbitrationDisposition.MODIFIED:
            if prior is not None and effective == prior:
                raise InvalidDomainValue(
                    "MODIFIED requires a changed judgement when a prior exists"
                )
        elif prior is None or effective == prior:
            raise InvalidDomainValue(
                "REVERSED requires a changed prior effective judgement"
            )


@dataclass(frozen=True, slots=True)
class EvaluationArbitrationRecord:
    """One immutable direct or conflict-set-linked arbitration decision record.

    Construction records judgment and provenance only. It grants no authority,
    performs no lookup, and executes no Evaluation lifecycle transition.
    """

    arbitration_id: EvaluationArbitrationId
    conflict_set_ref: EvaluationConflictSetRef | None
    decisions: frozenset[EvaluationArbitrationMemberDecision]
    rationale: str
    evidence_refs: frozenset[EvidenceRef]
    policy_ref: EvaluationArbitrationPolicyRef
    decided_by: ActorIdentity
    decided_at: Timestamp
    correlation_id: CorrelationId
    prior_arbitration_id: EvaluationArbitrationId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.arbitration_id, EvaluationArbitrationId):
            raise InvalidDomainValue(
                "arbitration_id must be an EvaluationArbitrationId"
            )
        if self.conflict_set_ref is not None and not isinstance(
            self.conflict_set_ref, EvaluationConflictSetRef
        ):
            raise InvalidDomainValue(
                "conflict_set_ref must be an EvaluationConflictSetRef or None"
            )
        if not isinstance(self.decisions, frozenset):
            raise InvalidDomainValue("decisions must be a frozenset")
        if any(
            not isinstance(decision, EvaluationArbitrationMemberDecision)
            for decision in self.decisions
        ):
            raise InvalidDomainValue(
                "Every decision must be an EvaluationArbitrationMemberDecision"
            )
        if not self.decisions:
            raise InvalidDomainValue(
                "An arbitration record requires at least one decision"
            )
        decision_ids = {decision.evaluation_id for decision in self.decisions}
        if len(decision_ids) != len(self.decisions):
            raise InvalidDomainValue(
                "Each EvaluationId may appear at most once in an arbitration record"
            )
        if self.conflict_set_ref is None and len(self.decisions) != 1:
            raise InvalidDomainValue(
                "Direct Evaluation arbitration requires exactly one decision"
            )
        _require_text(self.rationale, "rationale")
        if not isinstance(self.evidence_refs, frozenset):
            raise InvalidDomainValue("evidence_refs must be a frozenset")
        if any(
            not isinstance(reference, EvidenceRef) for reference in self.evidence_refs
        ):
            raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")
        if not isinstance(self.policy_ref, EvaluationArbitrationPolicyRef):
            raise InvalidDomainValue(
                "policy_ref must be an EvaluationArbitrationPolicyRef"
            )
        if not isinstance(self.decided_by, ActorIdentity):
            raise InvalidDomainValue("decided_by must be an ActorIdentity")
        if not isinstance(self.decided_at, Timestamp):
            raise InvalidDomainValue("decided_at must be a Timestamp")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")
        if self.prior_arbitration_id is not None and not isinstance(
            self.prior_arbitration_id, EvaluationArbitrationId
        ):
            raise InvalidDomainValue(
                "prior_arbitration_id must be an EvaluationArbitrationId or None"
            )
        if self.prior_arbitration_id == self.arbitration_id:
            raise InvalidDomainValue("An arbitration record cannot reference itself")


def can_arbitrate_evaluation_conflict_set(
    conflict_set: EvaluationConflictSetRecord,
    arbitration: EvaluationArbitrationRecord,
) -> bool:
    """Return exact conflict arbitration compatibility without resolving history."""
    if not isinstance(conflict_set, EvaluationConflictSetRecord) or not isinstance(
        arbitration, EvaluationArbitrationRecord
    ):
        raise InvalidDomainValue(
            "conflict_set and arbitration must be their respective record types"
        )
    reference = arbitration.conflict_set_ref
    if reference is None:
        return False
    if reference.conflict_set_id != conflict_set.conflict_set_id:
        return False
    if reference.version != conflict_set.version:
        return False
    if arbitration.correlation_id != conflict_set.correlation_id:
        return False

    decisions = {
        decision.evaluation_id: decision.observed_version
        for decision in arbitration.decisions
    }
    members = {
        member.evaluation_id: member.observed_version for member in conflict_set.members
    }
    if decisions.keys() != members.keys():
        return False
    return all(
        decisions[evaluation_id].value >= observed_version.value
        for evaluation_id, observed_version in members.items()
    )
