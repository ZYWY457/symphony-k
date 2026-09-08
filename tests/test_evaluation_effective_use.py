from dataclasses import fields, replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

import symphony_k.domain as domain
from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArbitrationDisposition,
    ConflictSetVersion,
    CorrelationId,
    EntityVersion,
    Evaluation,
    EvaluationArbitrationId,
    EvaluationArbitrationMemberDecision,
    EvaluationArbitrationPolicyRef,
    EvaluationArbitrationRecord,
    EvaluationConfidence,
    EvaluationConflictMemberRef,
    EvaluationConflictScopeRef,
    EvaluationConflictSetId,
    EvaluationConflictSetRecord,
    EvaluationEffectiveUseView,
    EvaluationId,
    EvaluationInvalidationId,
    EvaluationInvalidationRecord,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationState,
    EvaluationTargetRef,
    EvaluationVerdict,
    EvidenceRef,
    InvalidDomainValue,
    InvalidRelationship,
    InvariantViolation,
    RunId,
    Timestamp,
    derive_evaluation_effective_use,
)


def uid(value: int) -> UUID:
    return UUID(int=value)


SUBJECT_ID = EvaluationId(uid(1))
OTHER_ID = EvaluationId(uid(2))
ACTOR = ActorIdentity(ActorId(uid(3)), ActorType.ARBITRATOR)
ORIGINAL = EvaluationVerdict("PASS")
NEGATIVE = EvaluationVerdict("FAIL")
MODIFIED = EvaluationVerdict("PASS_WITH_LIMITS")
FINAL = EvaluationVerdict("PASS_AFTER_REVIEW")
METHOD = EvaluationMethodRef("test", "v1")
TARGET = EvaluationTargetRef(RunId(uid(4)), EntityVersion(1))
POLICY = EvaluationArbitrationPolicyRef("arbitration", "v1")
BASE_TIME = datetime(2026, 9, 8, tzinfo=UTC)


def evaluation(
    state: EvaluationState,
    *,
    verdict: EvaluationVerdict | None = ORIGINAL,
    evaluation_id: EvaluationId = SUBJECT_ID,
) -> Evaluation:
    result = (
        None
        if verdict is None
        else EvaluationResult(
            verdict,
            EvaluationConfidence("high"),
            "Independent evidence assessed.",
        )
    )
    return Evaluation(
        evaluation_id,
        state,
        EntityVersion(3),
        TARGET,
        METHOD,
        ACTOR,
        result,
    )


def conflict(
    number: int,
    *,
    version: int = 2,
    evaluation_id: EvaluationId = SUBJECT_ID,
) -> EvaluationConflictSetRecord:
    return EvaluationConflictSetRecord(
        EvaluationConflictSetId(uid(100 + number)),
        ConflictSetVersion(version),
        None,
        frozenset({EvaluationConflictMemberRef(evaluation_id, EntityVersion(2))}),
        EvaluationConflictScopeRef(f"scope-{number}"),
        "Material disagreement.",
        frozenset({EvidenceRef(f"conflict-{number}")}),
        ACTOR,
        Timestamp(BASE_TIME),
        CorrelationId(uid(200 + number)),
    )


def decision(
    effective: EvaluationVerdict,
    *,
    prior: EvaluationVerdict | None = ORIGINAL,
    evaluation_id: EvaluationId = SUBJECT_ID,
) -> EvaluationArbitrationMemberDecision:
    return EvaluationArbitrationMemberDecision(
        evaluation_id,
        EntityVersion(3),
        ArbitrationDisposition.MODIFIED
        if prior is None or prior != effective
        else ArbitrationDisposition.UPHELD,
        prior,
        effective,
    )


def arbitration(
    number: int,
    member_decision: EvaluationArbitrationMemberDecision,
    *,
    conflict_set: EvaluationConflictSetRecord | None = None,
    prior_id: EvaluationArbitrationId | None = None,
    decided_at: datetime = BASE_TIME,
) -> EvaluationArbitrationRecord:
    return EvaluationArbitrationRecord(
        EvaluationArbitrationId(uid(300 + number)),
        None
        if conflict_set is None
        else domain.EvaluationConflictSetRef(
            conflict_set.conflict_set_id, conflict_set.version
        ),
        frozenset({member_decision}),
        "Explicit review decision.",
        frozenset({EvidenceRef(f"arbitration-{number}")}),
        POLICY,
        ACTOR,
        Timestamp(decided_at),
        conflict_set.correlation_id
        if conflict_set is not None
        else CorrelationId(uid(400 + number)),
        prior_id,
    )


def invalidation(
    number: int = 1, *, evaluation_id: EvaluationId = SUBJECT_ID
) -> EvaluationInvalidationRecord:
    return EvaluationInvalidationRecord(
        EvaluationInvalidationId(uid(500 + number)),
        evaluation_id,
        EntityVersion(2),
        "Established verifier defect.",
        frozenset({EvidenceRef(f"invalidation-{number}")}),
        ACTOR,
        Timestamp(BASE_TIME),
        CorrelationId(uid(600 + number)),
    )


def derive(
    subject: Evaluation,
    *,
    conflicts: frozenset[EvaluationConflictSetRecord] = frozenset(),
    arbitrations: frozenset[EvaluationArbitrationRecord] = frozenset(),
    invalidations: frozenset[EvaluationInvalidationRecord] = frozenset(),
) -> EvaluationEffectiveUseView:
    return derive_evaluation_effective_use(
        subject,
        applicable_conflict_sets=conflicts,
        arbitration_records=arbitrations,
        invalidation_records=invalidations,
    )


@pytest.mark.parametrize("verdict", [ORIGINAL, NEGATIVE])
def test_completed_without_history_uses_original_judgement(
    verdict: EvaluationVerdict,
) -> None:
    view = derive(evaluation(EvaluationState.COMPLETED, verdict=verdict))
    assert view.original_judgement is verdict
    assert view.effective_judgement is verdict
    assert view.eligible_for_effective_use
    assert not view.applicable_conflicts
    assert not view.supporting_arbitration_ids


@pytest.mark.parametrize("state", [EvaluationState.PENDING, EvaluationState.RUNNING])
def test_in_progress_evaluation_has_no_effective_judgement(
    state: EvaluationState,
) -> None:
    view = derive(evaluation(state, verdict=None))
    assert view.original_judgement is None
    assert view.effective_judgement is None
    assert not view.eligible_for_effective_use


@pytest.mark.parametrize("count", [1, 2])
def test_every_unresolved_conflict_blocks_effective_use(count: int) -> None:
    conflicts = frozenset(conflict(number) for number in range(1, count + 1))
    view = derive(evaluation(EvaluationState.CONFLICTED), conflicts=conflicts)
    assert view.applicable_conflicts == view.unresolved_conflicts
    assert len(view.unresolved_conflicts) == count
    assert view.effective_judgement is None
    assert not view.eligible_for_effective_use


def test_resolving_one_of_two_conflicts_leaves_the_other_unresolved() -> None:
    first, second = conflict(1), conflict(2)
    resolved = arbitration(1, decision(MODIFIED), conflict_set=first)
    view = derive(
        evaluation(EvaluationState.CONFLICTED),
        conflicts=frozenset({first, second}),
        arbitrations=frozenset({resolved}),
    )
    assert view.unresolved_conflicts == frozenset(
        {domain.EvaluationConflictSetRef(second.conflict_set_id, second.version)}
    )
    assert not view.eligible_for_effective_use


def test_exact_arbitration_of_both_conflicts_allows_arbitrated_use() -> None:
    first, second = conflict(1), conflict(2)
    first_decision = arbitration(1, decision(MODIFIED), conflict_set=first)
    second_decision = arbitration(
        2,
        decision(FINAL, prior=MODIFIED),
        conflict_set=second,
        prior_id=first_decision.arbitration_id,
    )
    view = derive(
        evaluation(EvaluationState.ARBITRATED),
        conflicts=frozenset({first, second}),
        arbitrations=frozenset({first_decision, second_decision}),
    )
    assert not view.unresolved_conflicts
    assert view.terminal_arbitration_id == second_decision.arbitration_id
    assert view.effective_judgement is FINAL
    assert view.eligible_for_effective_use


def test_older_conflict_version_arbitration_does_not_cover_current_version() -> None:
    old = conflict(1, version=2)
    current = replace(old, version=ConflictSetVersion(3))
    stale_arbitration = arbitration(1, decision(MODIFIED), conflict_set=old)
    view = derive(
        evaluation(EvaluationState.ARBITRATED),
        conflicts=frozenset({current}),
        arbitrations=frozenset({stale_arbitration}),
    )
    assert view.unresolved_conflicts == frozenset(
        {domain.EvaluationConflictSetRef(current.conflict_set_id, current.version)}
    )
    assert view.effective_judgement is None
    assert not view.eligible_for_effective_use


def test_direct_arbitration_does_not_resolve_a_conflict_set() -> None:
    current = conflict(1)
    direct = arbitration(1, decision(MODIFIED))
    view = derive(
        evaluation(EvaluationState.ARBITRATED),
        conflicts=frozenset({current}),
        arbitrations=frozenset({direct}),
    )
    assert view.unresolved_conflicts == view.applicable_conflicts
    assert view.effective_judgement is None
    assert not view.eligible_for_effective_use


def test_direct_arbitration_derives_its_member_judgement() -> None:
    record = arbitration(1, decision(MODIFIED))
    view = derive(
        evaluation(EvaluationState.ARBITRATED), arbitrations=frozenset({record})
    )
    assert view.supporting_arbitration_ids == frozenset({record.arbitration_id})
    assert view.terminal_arbitration_id == record.arbitration_id
    assert view.effective_judgement is MODIFIED
    assert view.eligible_for_effective_use


def test_linear_lineage_derives_only_the_explicit_terminal_decision() -> None:
    first = arbitration(1, decision(MODIFIED), decided_at=BASE_TIME + timedelta(days=2))
    second = arbitration(
        2,
        decision(FINAL, prior=MODIFIED),
        prior_id=first.arbitration_id,
        decided_at=BASE_TIME,
    )
    view = derive(
        evaluation(EvaluationState.ARBITRATED), arbitrations=frozenset({first, second})
    )
    assert view.terminal_arbitration_id == second.arbitration_id
    assert view.effective_judgement is FINAL


def test_missing_prior_lineage_record_is_rejected() -> None:
    record = arbitration(
        1,
        decision(MODIFIED),
        prior_id=EvaluationArbitrationId(uid(999)),
    )
    with pytest.raises(InvalidRelationship, match="incomplete"):
        derive(evaluation(EvaluationState.ARBITRATED), arbitrations=frozenset({record}))


def test_repeated_arbitration_identity_is_rejected() -> None:
    first = arbitration(1, decision(MODIFIED))
    duplicate = replace(first, rationale="A conflicting record under the same ID.")
    with pytest.raises(InvariantViolation, match="repeated identity"):
        derive(
            evaluation(EvaluationState.ARBITRATED),
            arbitrations=frozenset({first, duplicate}),
        )


def test_prior_record_for_another_evaluation_does_not_establish_precedence() -> None:
    unrelated = arbitration(9, decision(NEGATIVE, evaluation_id=OTHER_ID))
    relevant = arbitration(1, decision(MODIFIED), prior_id=unrelated.arbitration_id)
    view = derive(
        evaluation(EvaluationState.ARBITRATED),
        arbitrations=frozenset({unrelated, relevant}),
    )
    assert view.supporting_arbitration_ids == frozenset({relevant.arbitration_id})
    assert view.terminal_arbitration_id == relevant.arbitration_id


def test_multi_record_lineage_cycle_is_rejected() -> None:
    first_id, second_id = (
        EvaluationArbitrationId(uid(301)),
        EvaluationArbitrationId(uid(302)),
    )
    first = arbitration(1, decision(MODIFIED), prior_id=second_id)
    second = arbitration(2, decision(FINAL, prior=MODIFIED), prior_id=first_id)
    with pytest.raises(InvariantViolation, match="cycle"):
        derive(
            evaluation(EvaluationState.ARBITRATED),
            arbitrations=frozenset({first, second}),
        )


@pytest.mark.parametrize("same_value", [False, True])
def test_disconnected_decisions_are_ambiguous_even_when_values_match(
    same_value: bool,
) -> None:
    first = arbitration(1, decision(MODIFIED), decided_at=BASE_TIME)
    second = arbitration(
        2,
        decision(MODIFIED if same_value else FINAL),
        decided_at=BASE_TIME + timedelta(days=10),
    )
    view = derive(
        evaluation(EvaluationState.ARBITRATED), arbitrations=frozenset({first, second})
    )
    assert view.arbitration_ambiguous
    assert view.terminal_arbitration_id is None
    assert view.effective_judgement is None
    assert not view.eligible_for_effective_use


def test_forked_lineage_has_multiple_terminal_heads_and_is_ambiguous() -> None:
    root = arbitration(1, decision(MODIFIED))
    left = arbitration(2, decision(FINAL, prior=MODIFIED), prior_id=root.arbitration_id)
    right = arbitration(
        3, decision(NEGATIVE, prior=MODIFIED), prior_id=root.arbitration_id
    )
    view = derive(
        evaluation(EvaluationState.ARBITRATED),
        arbitrations=frozenset({root, left, right}),
    )
    assert view.arbitration_ambiguous
    assert view.supporting_arbitration_ids == frozenset(
        {root.arbitration_id, left.arbitration_id, right.arbitration_id}
    )


def test_first_arbitration_cannot_fabricate_a_prior_judgement() -> None:
    record = arbitration(1, decision(MODIFIED, prior=NEGATIVE))
    with pytest.raises(InvariantViolation, match="differs from the original"):
        derive(evaluation(EvaluationState.ARBITRATED), arbitrations=frozenset({record}))


def test_subsequent_arbitration_must_continue_the_judgement_chain() -> None:
    first = arbitration(1, decision(MODIFIED))
    second = arbitration(
        2, decision(FINAL, prior=NEGATIVE), prior_id=first.arbitration_id
    )
    with pytest.raises(InvariantViolation, match="historically inconsistent"):
        derive(
            evaluation(EvaluationState.ARBITRATED),
            arbitrations=frozenset({first, second}),
        )


def test_no_original_result_can_establish_judgement_via_modified_none() -> None:
    record = arbitration(1, decision(MODIFIED, prior=None))
    view = derive(
        evaluation(EvaluationState.ARBITRATED, verdict=None),
        arbitrations=frozenset({record}),
    )
    assert view.original_judgement is None
    assert view.effective_judgement is MODIFIED
    assert view.eligible_for_effective_use


def test_conflicted_stays_ineligible_even_when_every_conflict_is_addressed() -> None:
    current = conflict(1)
    record = arbitration(1, decision(MODIFIED), conflict_set=current)
    view = derive(
        evaluation(EvaluationState.CONFLICTED),
        conflicts=frozenset({current}),
        arbitrations=frozenset({record}),
    )
    assert not view.unresolved_conflicts
    assert view.effective_judgement is None
    assert not view.eligible_for_effective_use


def test_invalid_is_always_unusable_and_retains_all_provenance() -> None:
    current = conflict(1)
    record = arbitration(1, decision(MODIFIED), conflict_set=current)
    invalidated = invalidation()
    view = derive(
        evaluation(EvaluationState.INVALID),
        conflicts=frozenset({current}),
        arbitrations=frozenset({record}),
        invalidations=frozenset({invalidated}),
    )
    assert view.original_judgement is ORIGINAL
    assert view.supporting_arbitration_ids == frozenset({record.arbitration_id})
    assert view.invalidation_ids == frozenset({invalidated.invalidation_id})
    assert view.effective_judgement is None
    assert not view.eligible_for_effective_use


def test_invalid_requires_invalidation_provenance() -> None:
    with pytest.raises(InvariantViolation, match="requires invalidation"):
        derive(evaluation(EvaluationState.INVALID))


def test_invalidation_history_blocks_completed_and_arbitrated_use() -> None:
    completed = derive(
        evaluation(EvaluationState.COMPLETED),
        invalidations=frozenset({invalidation()}),
    )
    record = arbitration(1, decision(MODIFIED))
    arbitrated = derive(
        evaluation(EvaluationState.ARBITRATED),
        arbitrations=frozenset({record}),
        invalidations=frozenset({invalidation()}),
    )
    assert completed.effective_judgement is None
    assert arbitrated.effective_judgement is None
    assert not completed.eligible_for_effective_use
    assert not arbitrated.eligible_for_effective_use


def test_duplicate_current_conflict_set_identity_is_rejected() -> None:
    current = conflict(1, version=2)
    newer = replace(current, version=ConflictSetVersion(3))
    with pytest.raises(InvariantViolation, match="At most one current version"):
        derive(
            evaluation(EvaluationState.CONFLICTED),
            conflicts=frozenset({current, newer}),
        )


def test_incorrectly_scoped_conflict_or_invalidation_is_rejected() -> None:
    with pytest.raises(InvalidRelationship, match="conflict set"):
        derive(
            evaluation(EvaluationState.CONFLICTED),
            conflicts=frozenset({conflict(1, evaluation_id=OTHER_ID)}),
        )
    with pytest.raises(InvalidRelationship, match="invalidation"):
        derive(
            evaluation(EvaluationState.COMPLETED),
            invalidations=frozenset({invalidation(evaluation_id=OTHER_ID)}),
        )


def test_repeated_invalidation_identity_is_rejected() -> None:
    first = invalidation()
    duplicate = replace(first, reason="A second claim under the same identity.")
    with pytest.raises(InvariantViolation, match="repeated identity"):
        derive(
            evaluation(EvaluationState.INVALID),
            invalidations=frozenset({first, duplicate}),
        )


def test_pending_running_arbitration_and_arbitrated_without_history_rejected() -> None:
    record = arbitration(1, decision(MODIFIED))
    for state in (EvaluationState.PENDING, EvaluationState.RUNNING):
        with pytest.raises(InvalidRelationship, match="cannot have arbitration"):
            derive(evaluation(state, verdict=None), arbitrations=frozenset({record}))
    with pytest.raises(InvariantViolation, match="requires arbitration"):
        derive(evaluation(EvaluationState.ARBITRATED))


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("conflicts", []),
        ("conflicts", frozenset({"conflict"})),
        ("arbitrations", []),
        ("arbitrations", frozenset({"arbitration"})),
        ("invalidations", []),
        ("invalidations", frozenset({"invalidation"})),
    ],
)
def test_resolution_inputs_require_typed_frozensets(
    field: str, invalid: object
) -> None:
    arguments: dict[str, object] = {
        "conflicts": frozenset(),
        "arbitrations": frozenset(),
        "invalidations": frozenset(),
    }
    arguments[field] = invalid
    with pytest.raises(InvalidDomainValue):
        derive(
            evaluation(EvaluationState.COMPLETED),
            conflicts=arguments["conflicts"],  # type: ignore[arg-type]
            arbitrations=arguments["arbitrations"],  # type: ignore[arg-type]
            invalidations=arguments["invalidations"],  # type: ignore[arg-type]
        )


def test_derivation_preserves_all_supplied_history() -> None:
    subject = evaluation(EvaluationState.INVALID)
    current = conflict(1)
    record = arbitration(1, decision(MODIFIED), conflict_set=current)
    invalidated = invalidation()
    before = (replace(subject), replace(current), replace(record), replace(invalidated))
    derive(
        subject,
        conflicts=frozenset({current}),
        arbitrations=frozenset({record}),
        invalidations=frozenset({invalidated}),
    )
    assert (subject, current, record, invalidated) == before
    assert {field.name for field in fields(Evaluation)} == {
        "evaluation_id",
        "state",
        "version",
        "target",
        "method",
        "verifier",
        "result",
    }


def test_derived_view_is_frozen_and_exposes_only_the_stable_read_contract() -> None:
    view = derive(evaluation(EvaluationState.COMPLETED))
    assert {field.name for field in fields(EvaluationEffectiveUseView)} == {
        "evaluation_id",
        "original_judgement",
        "effective_judgement",
        "applicable_conflicts",
        "unresolved_conflicts",
        "supporting_arbitration_ids",
        "terminal_arbitration_id",
        "arbitration_ambiguous",
        "invalidation_ids",
        "eligible_for_effective_use",
    }
    with pytest.raises(AttributeError):
        view.effective_judgement = NEGATIVE  # type: ignore[misc]
    for absent in (
        "repository",
        "query",
        "transition",
        "events",
        "authorize",
        "latest_arbitration",
        "current_conflict_set",
    ):
        assert not hasattr(view, absent)
