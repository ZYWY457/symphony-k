"""Evaluation conflict-set records preserve explicit append-only structure."""

from dataclasses import fields, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

import symphony_k.domain as domain
from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArtifactRef,
    ConflictSetVersion,
    CorrelationId,
    EffectId,
    EntityVersion,
    Evaluation,
    EvaluationConflictMemberRef,
    EvaluationConflictScopeRef,
    EvaluationConflictSetId,
    EvaluationConflictSetRecord,
    EvaluationConflictSetRef,
    EvaluationId,
    EvaluationMethodRef,
    EvaluationState,
    EvaluationTargetRef,
    EvidenceRef,
    InvalidDomainValue,
    OutcomeId,
    RunId,
    Timestamp,
    can_extend_evaluation_conflict_set,
)

CONFLICT_ID = EvaluationConflictSetId(UUID("12345678-1234-4234-8234-123456789abc"))
OTHER_CONFLICT_ID = EvaluationConflictSetId(
    UUID("87654321-4321-4321-8321-cba987654321")
)
CORRELATION_ID = CorrelationId(UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"))
OTHER_CORRELATION_ID = CorrelationId(UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"))
SCOPE = EvaluationConflictScopeRef("acceptance scope: candidate artifact family")
OTHER_SCOPE = EvaluationConflictScopeRef("different acceptance scope")
RECORDER = ActorIdentity(
    ActorId(UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc")),
    ActorType.EVALUATOR,
)
RECORDED_AT = Timestamp(datetime(2026, 9, 7, 13, 30, tzinfo=UTC))


def member(seed: int, version: int = 3) -> EvaluationConflictMemberRef:
    return EvaluationConflictMemberRef(
        EvaluationId(UUID(int=seed)), EntityVersion(version)
    )


def record(
    *,
    conflict_set_id: EvaluationConflictSetId = CONFLICT_ID,
    version: int = 10,
    previous_version: ConflictSetVersion | None = None,
    members: frozenset[EvaluationConflictMemberRef] | None = None,
    affected_scope: EvaluationConflictScopeRef = SCOPE,
    disagreement_summary: str = "Independent observations materially disagree.",
    evidence_refs: frozenset[EvidenceRef] | None = None,
    recorded_by: ActorIdentity = RECORDER,
    recorded_at: Timestamp = RECORDED_AT,
    correlation_id: CorrelationId = CORRELATION_ID,
) -> EvaluationConflictSetRecord:
    return EvaluationConflictSetRecord(
        conflict_set_id=conflict_set_id,
        version=ConflictSetVersion(version),
        previous_version=previous_version,
        members=frozenset({member(1), member(2)}) if members is None else members,
        affected_scope=affected_scope,
        disagreement_summary=disagreement_summary,
        evidence_refs=frozenset() if evidence_refs is None else evidence_refs,
        recorded_by=recorded_by,
        recorded_at=recorded_at,
        correlation_id=correlation_id,
    )


def test_identity_categories_and_exact_version_reference_are_distinct() -> None:
    shared = UUID("12345678-1234-4234-8234-123456789abc")
    conflict_id = EvaluationConflictSetId(shared)
    correlation_id = CorrelationId(shared)
    evaluation_id = EvaluationId(shared)
    assert len({conflict_id, correlation_id, evaluation_id}) == 3
    reference = EvaluationConflictSetRef(conflict_id, ConflictSetVersion(37))
    assert reference.conflict_set_id is conflict_id
    assert reference.version == ConflictSetVersion(37)
    assert {field.name for field in fields(reference)} == {"conflict_set_id", "version"}
    with pytest.raises(AttributeError):
        reference.version = ConflictSetVersion(38)  # type: ignore[misc]


@pytest.mark.parametrize("invalid", [RunId(UUID(int=1)), UUID(int=1), "raw", None])
def test_member_requires_typed_evaluation_identity(invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        EvaluationConflictMemberRef(invalid, EntityVersion(3))  # type: ignore[arg-type]


@pytest.mark.parametrize("invalid", [3, True, "3", ConflictSetVersion(3), None])
def test_member_requires_typed_observed_entity_version(invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        EvaluationConflictMemberRef(EvaluationId(UUID(int=1)), invalid)  # type: ignore[arg-type]


def test_member_is_a_minimal_immutable_reference() -> None:
    reference = member(1, 7)
    assert {field.name for field in fields(reference)} == {
        "evaluation_id",
        "observed_version",
    }
    for absent in ("evaluation", "state", "result", "verdict", "target", "lookup"):
        assert not hasattr(reference, absent)
    with pytest.raises(AttributeError):
        reference.observed_version = EntityVersion(8)  # type: ignore[misc]


@pytest.mark.parametrize("invalid", ["", " ", "\t\n", None, 1, True])
def test_scope_requires_meaningful_opaque_text(invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        EvaluationConflictScopeRef(invalid)  # type: ignore[arg-type]


def test_scope_preserves_supplied_text_without_a_taxonomy() -> None:
    scope = EvaluationConflictScopeRef("  custom cross-target scope\n")
    assert scope.value == "  custom cross-target scope\n"
    assert not hasattr(scope, "kind")
    assert not hasattr(scope, "targets")


def test_common_scope_does_not_force_identical_evaluation_targets() -> None:
    first = Evaluation(
        member(1).evaluation_id,
        EvaluationState.PENDING,
        EntityVersion(3),
        EvaluationTargetRef(OutcomeId(UUID(int=11)), EntityVersion(4)),
        EvaluationMethodRef("method", "revision"),
    )
    second = Evaluation(
        member(2).evaluation_id,
        EvaluationState.PENDING,
        EntityVersion(8),
        EvaluationTargetRef(EffectId(UUID(int=12)), EntityVersion(9)),
        EvaluationMethodRef("other method", "revision"),
    )
    represented = record(
        members=frozenset(
            {
                EvaluationConflictMemberRef(first.evaluation_id, first.version),
                EvaluationConflictMemberRef(second.evaluation_id, second.version),
            }
        )
    )
    assert first.target != second.target
    assert represented.affected_scope is SCOPE
    assert {member.evaluation_id for member in represented.members} == {
        first.evaluation_id,
        second.evaluation_id,
    }
    assert all(not hasattr(member, "target") for member in represented.members)


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("conflict_set_id", CorrelationId(UUID(int=1))),
        ("conflict_set_id", EvaluationId(UUID(int=1))),
        ("version", EntityVersion(3)),
        ("version", 3),
    ],
)
def test_exact_conflict_set_reference_rejects_wrong_types(
    field: str, invalid: object
) -> None:
    reference = EvaluationConflictSetRef(CONFLICT_ID, ConflictSetVersion(3))
    with pytest.raises(InvalidDomainValue):
        replace(reference, **{field: invalid})  # type: ignore[arg-type]


def test_record_has_the_exact_supporting_snapshot_fields() -> None:
    represented = record()
    assert {field.name for field in fields(represented)} == {
        "conflict_set_id",
        "version",
        "previous_version",
        "members",
        "affected_scope",
        "disagreement_summary",
        "evidence_refs",
        "recorded_by",
        "recorded_at",
        "correlation_id",
    }
    assert represented.version == ConflictSetVersion(10)
    assert represented.previous_version is None


def test_zero_members_are_rejected_even_with_external_evidence() -> None:
    with pytest.raises(InvalidDomainValue):
        record(
            members=frozenset(),
            evidence_refs=frozenset({EvidenceRef("opposing observation")}),
        )


def test_one_member_without_external_conflict_evidence_is_rejected() -> None:
    with pytest.raises(InvalidDomainValue):
        record(members=frozenset({member(1)}))


def test_one_member_with_external_conflict_evidence_is_supported() -> None:
    evidence = EvidenceRef("independent opposing observation")
    represented = record(
        members=frozenset({member(1)}), evidence_refs=frozenset({evidence})
    )
    assert represented.members == frozenset({member(1)})
    assert represented.evidence_refs == frozenset({evidence})


def test_two_or_more_members_need_no_additional_evidence() -> None:
    two = record(members=frozenset({member(1), member(2)}))
    many = record(
        members=frozenset({member(1), member(2), member(3)}),
        evidence_refs=frozenset({EvidenceRef("additional support")}),
    )
    assert len(two.members) == 2 and not two.evidence_refs
    assert len(many.members) == 3 and len(many.evidence_refs) == 1


def test_duplicate_evaluation_identity_with_different_versions_is_rejected() -> None:
    with pytest.raises(InvalidDomainValue):
        record(members=frozenset({member(1, 3), member(1, 4)}))


def test_member_and_evidence_collections_are_immutable() -> None:
    represented = record(
        evidence_refs=frozenset({EvidenceRef("support")}),
    )
    with pytest.raises(AttributeError):
        represented.members.add(member(3))  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        represented.evidence_refs.add(EvidenceRef("new"))  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        represented.members = frozenset({member(1)})  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("conflict_set_id", EvaluationId(UUID(int=1))),
        ("conflict_set_id", UUID(int=1)),
        ("version", EntityVersion(10)),
        ("version", 10),
        ("previous_version", EntityVersion(9)),
        ("previous_version", 9),
        ("members", (member(1), member(2))),
        ("members", frozenset({EvaluationId(UUID(int=1))})),
        ("members", frozenset({member(1), ArtifactRef("wrong")})),
        ("affected_scope", "raw scope"),
        ("affected_scope", EvidenceRef("wrong")),
        ("disagreement_summary", ""),
        ("disagreement_summary", " \n"),
        ("evidence_refs", (EvidenceRef("support"),)),
        ("evidence_refs", frozenset({ArtifactRef("wrong")})),
        ("recorded_by", ActorId(UUID(int=1))),
        ("recorded_by", ActorType.EVALUATOR),
        ("recorded_at", datetime(2026, 9, 7, tzinfo=UTC)),
        ("correlation_id", CONFLICT_ID),
        ("correlation_id", UUID(int=1)),
    ],
)
def test_record_rejects_wrong_field_types(field: str, invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(
            record(evidence_refs=frozenset({EvidenceRef("support")})),
            **{field: invalid},  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("category", list(ActorType))
def test_recorded_actor_category_is_provenance_not_authority(
    category: ActorType,
) -> None:
    actor = ActorIdentity(ActorId(UUID(int=99)), category)
    represented = record(recorded_by=actor)
    assert represented.recorded_by is actor
    assert represented.correlation_id is CORRELATION_ID
    for absent in ("authorize", "transition", "arbitrate", "grant"):
        assert not hasattr(represented, absent)


def test_valid_extension_can_retain_members_and_skip_version_numbers() -> None:
    previous = record(version=10)
    current = record(version=37, previous_version=ConflictSetVersion(10))
    assert can_extend_evaluation_conflict_set(previous, current)


def test_valid_extension_can_add_a_member() -> None:
    previous = record(version=10)
    current = record(
        version=11,
        previous_version=ConflictSetVersion(10),
        members=previous.members | {member(3)},
    )
    assert can_extend_evaluation_conflict_set(previous, current)
    assert len(previous.members) == 2 and len(current.members) == 3


def test_valid_extension_can_add_evidence_and_revise_summary() -> None:
    previous = record(
        version=10, evidence_refs=frozenset({EvidenceRef("original support")})
    )
    current = record(
        version=12,
        previous_version=ConflictSetVersion(10),
        evidence_refs=previous.evidence_refs | {EvidenceRef("new support")},
        disagreement_summary="Expanded explanation for this version.",
        recorded_at=Timestamp(datetime(2026, 9, 7, 14, 0, tzinfo=UTC)),
    )
    assert can_extend_evaluation_conflict_set(previous, current)
    assert previous.disagreement_summary != current.disagreement_summary


@pytest.mark.parametrize("new_version", [3, 4, 99])
def test_retained_member_version_can_stay_or_advance(new_version: int) -> None:
    previous = record(version=10, members=frozenset({member(1, 3), member(2, 8)}))
    current = record(
        version=11,
        previous_version=ConflictSetVersion(10),
        members=frozenset({member(1, new_version), member(2, 8)}),
    )
    assert can_extend_evaluation_conflict_set(previous, current)


def test_member_removal_is_not_a_valid_extension() -> None:
    evidence = frozenset({EvidenceRef("external support")})
    previous = record(version=10, evidence_refs=evidence)
    current = record(
        version=11,
        previous_version=ConflictSetVersion(10),
        members=frozenset({member(1)}),
        evidence_refs=evidence,
    )
    assert not can_extend_evaluation_conflict_set(previous, current)


def test_member_version_regression_is_not_a_valid_extension() -> None:
    previous = record(version=10, members=frozenset({member(1, 4), member(2, 8)}))
    current = record(
        version=11,
        previous_version=ConflictSetVersion(10),
        members=frozenset({member(1, 3), member(2, 8)}),
    )
    assert not can_extend_evaluation_conflict_set(previous, current)


def test_evidence_removal_is_not_a_valid_extension() -> None:
    previous = record(
        version=10,
        evidence_refs=frozenset({EvidenceRef("first"), EvidenceRef("second")}),
    )
    current = record(
        version=11,
        previous_version=ConflictSetVersion(10),
        evidence_refs=frozenset({EvidenceRef("second")}),
    )
    assert not can_extend_evaluation_conflict_set(previous, current)


@pytest.mark.parametrize(
    "current",
    [
        record(
            conflict_set_id=OTHER_CONFLICT_ID,
            version=11,
            previous_version=ConflictSetVersion(10),
        ),
        record(
            version=11,
            previous_version=ConflictSetVersion(10),
            correlation_id=OTHER_CORRELATION_ID,
        ),
        record(
            version=11,
            previous_version=ConflictSetVersion(10),
            affected_scope=OTHER_SCOPE,
        ),
        record(version=11, previous_version=ConflictSetVersion(9)),
        record(version=10, previous_version=ConflictSetVersion(10)),
        record(version=9, previous_version=ConflictSetVersion(10)),
    ],
)
def test_identity_scope_link_and_forward_version_are_required(
    current: EvaluationConflictSetRecord,
) -> None:
    assert not can_extend_evaluation_conflict_set(record(version=10), current)


@pytest.mark.parametrize("invalid", [None, "record", object()])
def test_extension_query_requires_typed_records(invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        can_extend_evaluation_conflict_set(invalid, record())  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        can_extend_evaluation_conflict_set(record(), invalid)  # type: ignore[arg-type]


def test_historical_records_are_not_mutated_by_extension_checks() -> None:
    previous = record(version=10)
    current = record(
        version=20,
        previous_version=ConflictSetVersion(10),
        members=previous.members | {member(3)},
    )
    before = replace(previous)
    assert can_extend_evaluation_conflict_set(previous, current)
    assert previous == before and previous.members == frozenset({member(1), member(2)})
    for field in fields(previous):
        with pytest.raises(AttributeError):
            setattr(previous, field.name, getattr(previous, field.name))


def test_m5b_does_not_add_membership_or_future_behavior_to_evaluation() -> None:
    assert {field.name for field in fields(Evaluation)} == {
        "evaluation_id",
        "state",
        "version",
        "target",
        "method",
        "verifier",
        "result",
    }
    for absent in (
        "ConflictSetState",
        "ConflictSetController",
        "ArbitrationRecord",
        "ArbitrationDisposition",
        "EvaluationConflicted",
        "EvaluationRepository",
    ):
        assert not hasattr(domain, absent)
    for absent in ("conflict_set_ids", "conflicts", "active_conflict"):
        assert not hasattr(Evaluation, absent)
