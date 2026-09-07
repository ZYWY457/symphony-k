"""Immutable Evaluation conflict-set provenance and structural history rules."""

from dataclasses import dataclass

from .actors import ActorIdentity
from .candidate_refs import EvidenceRef
from .errors import InvalidDomainValue
from .ids import CorrelationId, EvaluationConflictSetId, EvaluationId
from .time import Timestamp
from .version import ConflictSetVersion, EntityVersion


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InvalidDomainValue(f"{field} must contain non-whitespace text")


@dataclass(frozen=True, slots=True)
class EvaluationConflictMemberRef:
    """One Evaluation identity and the exact version observed for this record."""

    evaluation_id: EvaluationId
    observed_version: EntityVersion

    def __post_init__(self) -> None:
        if not isinstance(self.evaluation_id, EvaluationId):
            raise InvalidDomainValue("evaluation_id must be an EvaluationId")
        if not isinstance(self.observed_version, EntityVersion):
            raise InvalidDomainValue("observed_version must be an EntityVersion")


@dataclass(frozen=True, slots=True)
class EvaluationConflictScopeRef:
    """Opaque common acceptance or verification scope; no taxonomy or proof."""

    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, "affected scope")


@dataclass(frozen=True, slots=True)
class EvaluationConflictSetRef:
    """An exact conflict-set version reference that performs no lookup."""

    conflict_set_id: EvaluationConflictSetId
    version: ConflictSetVersion

    def __post_init__(self) -> None:
        if not isinstance(self.conflict_set_id, EvaluationConflictSetId):
            raise InvalidDomainValue(
                "conflict_set_id must be an EvaluationConflictSetId"
            )
        if not isinstance(self.version, ConflictSetVersion):
            raise InvalidDomainValue("version must be a ConflictSetVersion")


@dataclass(frozen=True, slots=True)
class EvaluationConflictSetRecord:
    """A complete immutable snapshot of one supporting conflict-set version.

    Construction records provenance and structural support only. It neither
    determines materiality nor grants transition or arbitration authority.
    """

    conflict_set_id: EvaluationConflictSetId
    version: ConflictSetVersion
    previous_version: ConflictSetVersion | None
    members: frozenset[EvaluationConflictMemberRef]
    affected_scope: EvaluationConflictScopeRef
    disagreement_summary: str
    evidence_refs: frozenset[EvidenceRef]
    recorded_by: ActorIdentity
    recorded_at: Timestamp
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not isinstance(self.conflict_set_id, EvaluationConflictSetId):
            raise InvalidDomainValue(
                "conflict_set_id must be an EvaluationConflictSetId"
            )
        if not isinstance(self.version, ConflictSetVersion):
            raise InvalidDomainValue("version must be a ConflictSetVersion")
        if self.previous_version is not None and not isinstance(
            self.previous_version, ConflictSetVersion
        ):
            raise InvalidDomainValue(
                "previous_version must be a ConflictSetVersion or None"
            )
        if not isinstance(self.members, frozenset):
            raise InvalidDomainValue("members must be a frozenset")
        if any(
            not isinstance(member, EvaluationConflictMemberRef)
            for member in self.members
        ):
            raise InvalidDomainValue(
                "Every member must be an EvaluationConflictMemberRef"
            )
        if not self.members:
            raise InvalidDomainValue(
                "A conflict set must contain at least one Evaluation member"
            )
        member_ids = {member.evaluation_id for member in self.members}
        if len(member_ids) != len(self.members):
            raise InvalidDomainValue(
                "Each EvaluationId may appear at most once in a conflict-set record"
            )
        if not isinstance(self.affected_scope, EvaluationConflictScopeRef):
            raise InvalidDomainValue(
                "affected_scope must be an EvaluationConflictScopeRef"
            )
        _require_text(self.disagreement_summary, "disagreement_summary")
        if not isinstance(self.evidence_refs, frozenset):
            raise InvalidDomainValue("evidence_refs must be a frozenset")
        if any(
            not isinstance(reference, EvidenceRef) for reference in self.evidence_refs
        ):
            raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")
        if len(self.members) == 1 and not self.evidence_refs:
            raise InvalidDomainValue(
                "A single-member conflict set requires external conflict evidence"
            )
        if not isinstance(self.recorded_by, ActorIdentity):
            raise InvalidDomainValue("recorded_by must be an ActorIdentity")
        if not isinstance(self.recorded_at, Timestamp):
            raise InvalidDomainValue("recorded_at must be a Timestamp")
        if not isinstance(self.correlation_id, CorrelationId):
            raise InvalidDomainValue("correlation_id must be a CorrelationId")


def can_extend_evaluation_conflict_set(
    previous: EvaluationConflictSetRecord,
    current: EvaluationConflictSetRecord,
) -> bool:
    """Return append-only structural compatibility without committing history."""
    if not isinstance(previous, EvaluationConflictSetRecord) or not isinstance(
        current, EvaluationConflictSetRecord
    ):
        raise InvalidDomainValue(
            "previous and current must be EvaluationConflictSetRecord values"
        )
    if previous.conflict_set_id != current.conflict_set_id:
        return False
    if current.version.value <= previous.version.value:
        return False
    if current.previous_version != previous.version:
        return False
    if previous.correlation_id != current.correlation_id:
        return False
    if previous.affected_scope != current.affected_scope:
        return False

    current_members = {
        member.evaluation_id: member.observed_version for member in current.members
    }
    for prior_member in previous.members:
        current_version = current_members.get(prior_member.evaluation_id)
        if current_version is None:
            return False
        if current_version.value < prior_member.observed_version.value:
            return False

    return previous.evidence_refs <= current.evidence_refs
