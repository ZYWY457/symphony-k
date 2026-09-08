"""Pure effective-use derivation from caller-supplied Evaluation history."""

from dataclasses import dataclass

from .errors import InvalidDomainValue, InvalidRelationship, InvariantViolation
from .evaluation import Evaluation, EvaluationState
from .evaluation_arbitration import (
    EvaluationArbitrationMemberDecision,
    EvaluationArbitrationRecord,
    can_arbitrate_evaluation_conflict_set,
)
from .evaluation_conflict import (
    EvaluationConflictSetRecord,
    EvaluationConflictSetRef,
)
from .evaluation_invalidation import EvaluationInvalidationRecord
from .evaluation_result import EvaluationVerdict
from .ids import EvaluationArbitrationId, EvaluationId, EvaluationInvalidationId


@dataclass(frozen=True, slots=True)
class EvaluationEffectiveUseView:
    """Immutable read view; never an authoritative lifecycle projection."""

    evaluation_id: EvaluationId
    original_judgement: EvaluationVerdict | None
    effective_judgement: EvaluationVerdict | None
    applicable_conflicts: frozenset[EvaluationConflictSetRef]
    unresolved_conflicts: frozenset[EvaluationConflictSetRef]
    supporting_arbitration_ids: frozenset[EvaluationArbitrationId]
    terminal_arbitration_id: EvaluationArbitrationId | None
    arbitration_ambiguous: bool
    invalidation_ids: frozenset[EvaluationInvalidationId]
    eligible_for_effective_use: bool

    def __post_init__(self) -> None:
        if not isinstance(self.evaluation_id, EvaluationId):
            raise InvalidDomainValue("evaluation_id must be an EvaluationId")
        for value, name in (
            (self.original_judgement, "original_judgement"),
            (self.effective_judgement, "effective_judgement"),
        ):
            if value is not None and not isinstance(value, EvaluationVerdict):
                raise InvalidDomainValue(f"{name} must be an EvaluationVerdict or None")
        _require_frozenset(
            self.applicable_conflicts,
            EvaluationConflictSetRef,
            "applicable_conflicts",
        )
        _require_frozenset(
            self.unresolved_conflicts,
            EvaluationConflictSetRef,
            "unresolved_conflicts",
        )
        _require_frozenset(
            self.supporting_arbitration_ids,
            EvaluationArbitrationId,
            "supporting_arbitration_ids",
        )
        _require_frozenset(
            self.invalidation_ids,
            EvaluationInvalidationId,
            "invalidation_ids",
        )
        if not self.unresolved_conflicts <= self.applicable_conflicts:
            raise InvalidDomainValue(
                "unresolved_conflicts must be a subset of applicable_conflicts"
            )
        if self.terminal_arbitration_id is not None and not isinstance(
            self.terminal_arbitration_id, EvaluationArbitrationId
        ):
            raise InvalidDomainValue(
                "terminal_arbitration_id must be an EvaluationArbitrationId or None"
            )
        if (
            self.terminal_arbitration_id is not None
            and self.terminal_arbitration_id not in self.supporting_arbitration_ids
        ):
            raise InvalidDomainValue(
                "terminal_arbitration_id must identify a supporting arbitration"
            )
        if not isinstance(self.arbitration_ambiguous, bool):
            raise InvalidDomainValue("arbitration_ambiguous must be a bool")
        if not isinstance(self.eligible_for_effective_use, bool):
            raise InvalidDomainValue("eligible_for_effective_use must be a bool")
        if self.arbitration_ambiguous and (
            self.terminal_arbitration_id is not None
            or self.effective_judgement is not None
            or self.eligible_for_effective_use
        ):
            raise InvalidDomainValue(
                "Ambiguous arbitration cannot identify an effective terminal decision"
            )
        if self.eligible_for_effective_use and self.effective_judgement is None:
            raise InvalidDomainValue(
                "Effective-use eligibility requires an effective judgement"
            )


def _require_frozenset(value: object, item_type: type[object], name: str) -> None:
    if not isinstance(value, frozenset):
        raise InvalidDomainValue(f"{name} must be a frozenset")
    if any(not isinstance(item, item_type) for item in value):
        raise InvalidDomainValue(f"Every {name} item must be a {item_type.__name__}")


def _decision_for(
    record: EvaluationArbitrationRecord, evaluation_id: EvaluationId
) -> EvaluationArbitrationMemberDecision | None:
    return next(
        (
            decision
            for decision in record.decisions
            if decision.evaluation_id == evaluation_id
        ),
        None,
    )


def _derive_arbitration_lineage(
    evaluation: Evaluation,
    records: frozenset[EvaluationArbitrationRecord],
) -> tuple[
    frozenset[EvaluationArbitrationId],
    EvaluationArbitrationId | None,
    EvaluationVerdict | None,
    bool,
]:
    all_by_id: dict[EvaluationArbitrationId, EvaluationArbitrationRecord] = {}
    for record in records:
        if record.arbitration_id in all_by_id:
            raise InvariantViolation("Arbitration history contains a repeated identity")
        all_by_id[record.arbitration_id] = record

    relevant = {
        record.arbitration_id: record
        for record in records
        if _decision_for(record, evaluation.evaluation_id) is not None
    }
    relevant_ids = frozenset(relevant)
    if (
        evaluation.state in (EvaluationState.PENDING, EvaluationState.RUNNING)
        and relevant
    ):
        raise InvalidRelationship(
            "PENDING and RUNNING Evaluations cannot have arbitration decisions"
        )
    if evaluation.state is EvaluationState.ARBITRATED and not relevant:
        raise InvariantViolation(
            "An ARBITRATED Evaluation requires arbitration history"
        )

    prior_by_id: dict[EvaluationArbitrationId, EvaluationArbitrationId | None] = {}
    for arbitration_id, record in relevant.items():
        prior_id = record.prior_arbitration_id
        if prior_id is None:
            prior_by_id[arbitration_id] = None
        elif prior_id in relevant:
            prior_by_id[arbitration_id] = prior_id
        elif prior_id in all_by_id:
            # A supplied prior record without a decision for this Evaluation does not
            # establish Evaluation-specific judgement precedence.
            prior_by_id[arbitration_id] = None
        else:
            raise InvalidRelationship(
                "Evaluation-specific arbitration lineage is incomplete"
            )

    for start in relevant:
        visited: set[EvaluationArbitrationId] = set()
        current: EvaluationArbitrationId | None = start
        while current is not None:
            if current in visited:
                raise InvariantViolation(
                    "Evaluation arbitration lineage contains a cycle"
                )
            visited.add(current)
            current = prior_by_id[current]

    referenced_priors = {
        prior_id for prior_id in prior_by_id.values() if prior_id is not None
    }
    terminal_ids = set(relevant) - referenced_priors
    if len(terminal_ids) > 1:
        return relevant_ids, None, None, True
    if not terminal_ids:
        return relevant_ids, None, None, False

    terminal_id = terminal_ids.pop()
    reverse_chain: list[EvaluationArbitrationId] = []
    current = terminal_id
    while current is not None:
        reverse_chain.append(current)
        current = prior_by_id[current]
    chain = list(reversed(reverse_chain))

    original = evaluation.result.verdict if evaluation.result is not None else None
    previous: EvaluationVerdict | None = original
    for index, arbitration_id in enumerate(chain):
        decision = _decision_for(relevant[arbitration_id], evaluation.evaluation_id)
        if decision is None:  # pragma: no cover - established by relevant construction
            raise InvariantViolation("Relevant arbitration lost its member decision")
        claimed_prior = decision.prior_effective_judgement
        if index == 0:
            if original is None and claimed_prior is not None:
                raise InvariantViolation(
                    "First arbitration fabricated a prior effective judgement"
                )
            if original is not None and claimed_prior is not None:
                if claimed_prior != original:
                    raise InvariantViolation(
                        "First arbitration prior judgement differs from the original"
                    )
        elif claimed_prior != previous:
            raise InvariantViolation(
                "Arbitration judgement chain is historically inconsistent"
            )
        previous = decision.effective_judgement

    return relevant_ids, terminal_id, previous, False


def derive_evaluation_effective_use(
    evaluation: Evaluation,
    *,
    applicable_conflict_sets: frozenset[EvaluationConflictSetRecord],
    arbitration_records: frozenset[EvaluationArbitrationRecord],
    invalidation_records: frozenset[EvaluationInvalidationRecord],
) -> EvaluationEffectiveUseView:
    """Derive effective use from a caller-provided complete current history slice.

    This function cannot prove repository completeness and never selects current
    conflict-set versions or queries storage.
    """
    if not isinstance(evaluation, Evaluation):
        raise InvalidDomainValue("evaluation must be an Evaluation")
    _require_frozenset(
        applicable_conflict_sets,
        EvaluationConflictSetRecord,
        "applicable_conflict_sets",
    )
    _require_frozenset(
        arbitration_records,
        EvaluationArbitrationRecord,
        "arbitration_records",
    )
    _require_frozenset(
        invalidation_records,
        EvaluationInvalidationRecord,
        "invalidation_records",
    )

    conflicts_by_id = {}
    for conflict in applicable_conflict_sets:
        if conflict.conflict_set_id in conflicts_by_id:
            raise InvariantViolation(
                "At most one current version per conflict-set identity may be supplied"
            )
        if evaluation.evaluation_id not in {
            member.evaluation_id for member in conflict.members
        }:
            raise InvalidRelationship(
                "Every applicable conflict set must contain the subject Evaluation"
            )
        conflicts_by_id[conflict.conflict_set_id] = conflict

    seen_invalidation_ids: set[EvaluationInvalidationId] = set()
    for invalidation in invalidation_records:
        if invalidation.invalidation_id in seen_invalidation_ids:
            raise InvariantViolation(
                "Invalidation history contains a repeated identity"
            )
        seen_invalidation_ids.add(invalidation.invalidation_id)
        if invalidation.evaluation_id != evaluation.evaluation_id:
            raise InvalidRelationship(
                "Every invalidation record must concern the subject Evaluation"
            )
    if evaluation.state is EvaluationState.INVALID and not invalidation_records:
        raise InvariantViolation(
            "An INVALID Evaluation requires invalidation provenance"
        )

    supporting_ids, terminal_id, arbitrated_judgement, ambiguous = (
        _derive_arbitration_lineage(evaluation, arbitration_records)
    )
    applicable_refs = frozenset(
        EvaluationConflictSetRef(conflict.conflict_set_id, conflict.version)
        for conflict in applicable_conflict_sets
    )
    unresolved_refs = frozenset(
        EvaluationConflictSetRef(conflict.conflict_set_id, conflict.version)
        for conflict in applicable_conflict_sets
        if not any(
            can_arbitrate_evaluation_conflict_set(conflict, arbitration)
            for arbitration in arbitration_records
        )
    )
    invalidation_ids = frozenset(
        invalidation.invalidation_id for invalidation in invalidation_records
    )
    original = evaluation.result.verdict if evaluation.result is not None else None

    effective: EvaluationVerdict | None = None
    eligible = False
    if evaluation.state is EvaluationState.COMPLETED:
        eligible = (
            original is not None
            and not applicable_refs
            and not supporting_ids
            and not invalidation_ids
        )
        effective = original if eligible else None
    elif evaluation.state is EvaluationState.ARBITRATED:
        eligible = (
            not ambiguous
            and arbitrated_judgement is not None
            and not unresolved_refs
            and not invalidation_ids
        )
        effective = arbitrated_judgement if eligible else None

    return EvaluationEffectiveUseView(
        evaluation_id=evaluation.evaluation_id,
        original_judgement=original,
        effective_judgement=effective,
        applicable_conflicts=applicable_refs,
        unresolved_conflicts=unresolved_refs,
        supporting_arbitration_ids=supporting_ids,
        terminal_arbitration_id=None if ambiguous else terminal_id,
        arbitration_ambiguous=ambiguous,
        invalidation_ids=invalidation_ids,
        eligible_for_effective_use=eligible,
    )
