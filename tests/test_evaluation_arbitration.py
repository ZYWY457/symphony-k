"""Evaluation arbitration records preserve judgment history and provenance."""

from dataclasses import fields, replace
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

import pytest

import symphony_k.domain as domain
from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArbitrationDisposition,
    ArtifactRef,
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
    EvaluationConflictSetRef,
    EvaluationId,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationState,
    EvaluationTargetRef,
    EvaluationVerdict,
    EvidenceRef,
    InvalidDomainValue,
    OutcomeId,
    Timestamp,
    can_arbitrate_evaluation_conflict_set,
)

ARBITRATION_ID = EvaluationArbitrationId(UUID("11111111-1111-4111-8111-111111111111"))
PRIOR_ARBITRATION_ID = EvaluationArbitrationId(
    UUID("22222222-2222-4222-8222-222222222222")
)
CONFLICT_ID = EvaluationConflictSetId(UUID("33333333-3333-4333-8333-333333333333"))
OTHER_CONFLICT_ID = EvaluationConflictSetId(
    UUID("44444444-4444-4444-8444-444444444444")
)
CORRELATION_ID = CorrelationId(UUID("55555555-5555-4555-8555-555555555555"))
OTHER_CORRELATION_ID = CorrelationId(UUID("66666666-6666-4666-8666-666666666666"))
DECIDER = ActorIdentity(
    ActorId(UUID("77777777-7777-4777-8777-777777777777")),
    ActorType.ARBITRATOR,
)
DECIDED_AT = Timestamp(datetime(2026, 9, 8, 9, 0, tzinfo=UTC))
POLICY = EvaluationArbitrationPolicyRef("arbitration-policy", "v1")
PRIOR = EvaluationVerdict("Original opaque judgement")
EFFECTIVE = EvaluationVerdict("Revised opaque judgement")


def decision(
    seed: int = 1,
    version: int = 3,
    disposition: ArbitrationDisposition = ArbitrationDisposition.UPHELD,
    prior: EvaluationVerdict | None = PRIOR,
    effective: EvaluationVerdict = PRIOR,
) -> EvaluationArbitrationMemberDecision:
    return EvaluationArbitrationMemberDecision(
        EvaluationId(UUID(int=seed)),
        EntityVersion(version),
        disposition,
        prior,
        effective,
    )


def arbitration(
    *,
    arbitration_id: EvaluationArbitrationId = ARBITRATION_ID,
    conflict_set_ref: EvaluationConflictSetRef | None = None,
    decisions: frozenset[EvaluationArbitrationMemberDecision] | None = None,
    rationale: str = "Independent arbitration considered the recorded evidence.",
    evidence_refs: frozenset[EvidenceRef] | None = None,
    policy_ref: EvaluationArbitrationPolicyRef = POLICY,
    decided_by: ActorIdentity = DECIDER,
    decided_at: Timestamp = DECIDED_AT,
    correlation_id: CorrelationId = CORRELATION_ID,
    prior_arbitration_id: EvaluationArbitrationId | None = None,
) -> EvaluationArbitrationRecord:
    return EvaluationArbitrationRecord(
        arbitration_id=arbitration_id,
        conflict_set_ref=conflict_set_ref,
        decisions=frozenset({decision()}) if decisions is None else decisions,
        rationale=rationale,
        evidence_refs=(
            frozenset({EvidenceRef("arbitration evidence")})
            if evidence_refs is None
            else evidence_refs
        ),
        policy_ref=policy_ref,
        decided_by=decided_by,
        decided_at=decided_at,
        correlation_id=correlation_id,
        prior_arbitration_id=prior_arbitration_id,
    )


def conflict_set(
    *,
    conflict_set_id: EvaluationConflictSetId = CONFLICT_ID,
    version: int = 7,
    members: frozenset[EvaluationConflictMemberRef] | None = None,
    correlation_id: CorrelationId = CORRELATION_ID,
) -> EvaluationConflictSetRecord:
    represented_members = (
        frozenset(
            {
                EvaluationConflictMemberRef(
                    EvaluationId(UUID(int=1)), EntityVersion(3)
                ),
                EvaluationConflictMemberRef(
                    EvaluationId(UUID(int=2)), EntityVersion(8)
                ),
            }
        )
        if members is None
        else members
    )
    return EvaluationConflictSetRecord(
        conflict_set_id=conflict_set_id,
        version=ConflictSetVersion(version),
        previous_version=None,
        members=represented_members,
        affected_scope=EvaluationConflictScopeRef("shared acceptance scope"),
        disagreement_summary="Materially conflicting observations.",
        evidence_refs=frozenset({EvidenceRef("external conflict evidence")}),
        recorded_by=DECIDER,
        recorded_at=DECIDED_AT,
        correlation_id=correlation_id,
    )


def conflict_arbitration(
    represented_conflict: EvaluationConflictSetRecord,
    *,
    conflict_set_ref: EvaluationConflictSetRef | None = None,
    decisions: frozenset[EvaluationArbitrationMemberDecision] | None = None,
    correlation_id: CorrelationId | None = None,
) -> EvaluationArbitrationRecord:
    represented_decisions = (
        frozenset(
            decision(member.evaluation_id.value.int, member.observed_version.value)
            for member in represented_conflict.members
        )
        if decisions is None
        else decisions
    )
    return arbitration(
        conflict_set_ref=(
            EvaluationConflictSetRef(
                represented_conflict.conflict_set_id, represented_conflict.version
            )
            if conflict_set_ref is None
            else conflict_set_ref
        ),
        decisions=represented_decisions,
        correlation_id=(
            represented_conflict.correlation_id
            if correlation_id is None
            else correlation_id
        ),
    )


def test_arbitration_identity_is_nominal_immutable_and_hashable() -> None:
    shared = UUID("12345678-1234-4234-8234-123456789abc")
    identities = {
        EvaluationArbitrationId(shared),
        EvaluationId(shared),
        EvaluationConflictSetId(shared),
        CorrelationId(shared),
    }
    assert len(identities) == 4
    parsed = EvaluationArbitrationId.from_string(str(shared))
    assert parsed == EvaluationArbitrationId(shared)
    assert {parsed: "record"}[EvaluationArbitrationId(shared)] == "record"
    with pytest.raises(AttributeError):
        parsed.value = UUID(int=9)  # type: ignore[misc]


def test_disposition_inventory_is_exact_and_not_a_lifecycle_enum() -> None:
    assert {member.name for member in ArbitrationDisposition} == {
        "UPHELD",
        "MODIFIED",
        "REVERSED",
    }
    assert not hasattr(ArbitrationDisposition, "OVERRIDDEN")
    assert not issubclass(ArbitrationDisposition, EvaluationState)
    assert issubclass(ArbitrationDisposition, Enum)


@pytest.mark.parametrize("invalid", ["", " ", "\t\n", None, 1, True])
@pytest.mark.parametrize("field", ["policy_id", "policy_version"])
def test_policy_reference_requires_meaningful_opaque_text(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(POLICY, **{field: invalid})  # type: ignore[arg-type]


def test_policy_reference_is_immutable_and_has_no_policy_behavior() -> None:
    assert POLICY.policy_id == "arbitration-policy"
    assert POLICY.policy_version == "v1"
    assert {field.name for field in fields(POLICY)} == {"policy_id", "policy_version"}
    for absent in ("evaluate", "authorize", "grant", "is_satisfied"):
        assert not hasattr(POLICY, absent)
    with pytest.raises(AttributeError):
        POLICY.policy_version = "v2"  # type: ignore[misc]


def test_upheld_requires_and_preserves_prior_judgement() -> None:
    represented = decision()
    assert represented.prior_effective_judgement is PRIOR
    assert represented.effective_judgement is PRIOR
    with pytest.raises(InvalidDomainValue):
        decision(prior=None)
    with pytest.raises(InvalidDomainValue):
        decision(effective=EFFECTIVE)


def test_modified_can_establish_or_change_an_effective_judgement() -> None:
    established = decision(
        disposition=ArbitrationDisposition.MODIFIED,
        prior=None,
        effective=EFFECTIVE,
    )
    changed = decision(
        disposition=ArbitrationDisposition.MODIFIED,
        prior=PRIOR,
        effective=EFFECTIVE,
    )
    assert established.prior_effective_judgement is None
    assert changed.effective_judgement is EFFECTIVE
    with pytest.raises(InvalidDomainValue):
        decision(disposition=ArbitrationDisposition.MODIFIED)


def test_reversed_requires_a_changed_prior_judgement() -> None:
    represented = decision(
        disposition=ArbitrationDisposition.REVERSED,
        prior=PRIOR,
        effective=EFFECTIVE,
    )
    assert represented.effective_judgement is EFFECTIVE
    with pytest.raises(InvalidDomainValue):
        decision(
            disposition=ArbitrationDisposition.REVERSED,
            prior=None,
            effective=EFFECTIVE,
        )
    with pytest.raises(InvalidDomainValue):
        decision(disposition=ArbitrationDisposition.REVERSED)


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("evaluation_id", EvaluationConflictSetId(UUID(int=1))),
        ("evaluation_id", UUID(int=1)),
        ("observed_version", ConflictSetVersion(3)),
        ("observed_version", 3),
        ("disposition", "UPHELD"),
        ("prior_effective_judgement", "prior"),
        ("effective_judgement", "effective"),
        ("effective_judgement", None),
    ],
)
def test_member_decision_rejects_wrong_field_types(field: str, invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(decision(), **{field: invalid})  # type: ignore[arg-type]


def test_member_decision_is_minimal_and_immutable() -> None:
    represented = decision()
    assert {field.name for field in fields(represented)} == {
        "evaluation_id",
        "observed_version",
        "disposition",
        "prior_effective_judgement",
        "effective_judgement",
    }
    for absent in ("evaluation", "result", "evidence_refs", "reasoning", "state"):
        assert not hasattr(represented, absent)
    with pytest.raises(AttributeError):
        represented.disposition = ArbitrationDisposition.REVERSED  # type: ignore[misc]


def test_record_has_exact_immutable_provenance_fields() -> None:
    represented = arbitration(prior_arbitration_id=PRIOR_ARBITRATION_ID)
    assert {field.name for field in fields(represented)} == {
        "arbitration_id",
        "conflict_set_ref",
        "decisions",
        "rationale",
        "evidence_refs",
        "policy_ref",
        "decided_by",
        "decided_at",
        "correlation_id",
        "prior_arbitration_id",
    }
    assert represented.prior_arbitration_id is PRIOR_ARBITRATION_ID
    with pytest.raises(AttributeError):
        represented.rationale = "replacement"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        represented.decisions.add(decision(2))  # type: ignore[attr-defined]


def test_record_requires_decisions_and_unique_evaluation_ids() -> None:
    with pytest.raises(InvalidDomainValue):
        arbitration(decisions=frozenset())
    duplicate_id = frozenset({decision(1, 3), decision(1, 4)})
    with pytest.raises(InvalidDomainValue):
        arbitration(
            conflict_set_ref=EvaluationConflictSetRef(
                CONFLICT_ID, ConflictSetVersion(7)
            ),
            decisions=duplicate_id,
        )


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("arbitration_id", EvaluationId(UUID(int=1))),
        ("conflict_set_ref", CONFLICT_ID),
        ("decisions", (decision(),)),
        ("decisions", frozenset({EvaluationId(UUID(int=1))})),
        ("rationale", ""),
        ("rationale", " \n"),
        ("evidence_refs", (EvidenceRef("support"),)),
        ("evidence_refs", frozenset({ArtifactRef("wrong")})),
        ("policy_ref", "policy"),
        ("decided_by", ActorType.ARBITRATOR),
        ("decided_at", datetime(2026, 9, 8, tzinfo=UTC)),
        ("correlation_id", CONFLICT_ID),
        ("prior_arbitration_id", EvaluationId(UUID(int=2))),
    ],
)
def test_record_rejects_wrong_or_empty_fields(field: str, invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(arbitration(), **{field: invalid})  # type: ignore[arg-type]


def test_direct_arbitration_requires_exactly_one_decision() -> None:
    represented = arbitration()
    assert represented.conflict_set_ref is None
    assert len(represented.decisions) == 1
    with pytest.raises(InvalidDomainValue):
        arbitration(decisions=frozenset({decision(1), decision(2)}))


@pytest.mark.parametrize("category", list(ActorType))
def test_decider_category_records_provenance_but_grants_no_authority(
    category: ActorType,
) -> None:
    actor = ActorIdentity(ActorId(UUID(int=91)), category)
    represented = arbitration(decided_by=actor)
    assert represented.decided_by is actor
    for absent in ("authorize", "grant", "transition", "apply"):
        assert not hasattr(represented, absent)


def test_prior_arbitration_lineage_is_optional_and_cannot_self_reference() -> None:
    assert arbitration().prior_arbitration_id is None
    assert (
        arbitration(prior_arbitration_id=PRIOR_ARBITRATION_ID).prior_arbitration_id
        is PRIOR_ARBITRATION_ID
    )
    with pytest.raises(InvalidDomainValue):
        arbitration(prior_arbitration_id=ARBITRATION_ID)


def test_one_member_conflict_arbitration_is_supported() -> None:
    represented_conflict = conflict_set(
        members=frozenset(
            {EvaluationConflictMemberRef(EvaluationId(UUID(int=1)), EntityVersion(3))}
        )
    )
    represented_arbitration = conflict_arbitration(represented_conflict)
    assert can_arbitrate_evaluation_conflict_set(
        represented_conflict, represented_arbitration
    )


def test_multi_member_equal_or_later_versions_are_compatible() -> None:
    represented_conflict = conflict_set()
    equal = conflict_arbitration(represented_conflict)
    later = conflict_arbitration(
        represented_conflict,
        decisions=frozenset({decision(1, 4), decision(2, 99)}),
    )
    assert can_arbitrate_evaluation_conflict_set(represented_conflict, equal)
    assert can_arbitrate_evaluation_conflict_set(represented_conflict, later)


def test_direct_arbitration_is_not_conflict_compatible() -> None:
    assert not can_arbitrate_evaluation_conflict_set(conflict_set(), arbitration())


@pytest.mark.parametrize(
    "represented_arbitration",
    [
        conflict_arbitration(
            conflict_set(),
            conflict_set_ref=EvaluationConflictSetRef(
                OTHER_CONFLICT_ID, ConflictSetVersion(7)
            ),
        ),
        conflict_arbitration(
            conflict_set(),
            conflict_set_ref=EvaluationConflictSetRef(
                CONFLICT_ID, ConflictSetVersion(8)
            ),
        ),
        conflict_arbitration(conflict_set(), correlation_id=OTHER_CORRELATION_ID),
        conflict_arbitration(conflict_set(), decisions=frozenset({decision(1, 3)})),
        conflict_arbitration(
            conflict_set(),
            decisions=frozenset({decision(1, 3), decision(2, 8), decision(3, 1)}),
        ),
        conflict_arbitration(
            conflict_set(), decisions=frozenset({decision(1, 2), decision(2, 8)})
        ),
    ],
)
def test_conflict_compatibility_rejects_reference_coverage_and_version_mismatch(
    represented_arbitration: EvaluationArbitrationRecord,
) -> None:
    assert not can_arbitrate_evaluation_conflict_set(
        conflict_set(), represented_arbitration
    )


@pytest.mark.parametrize("invalid", [None, "record", object()])
def test_conflict_compatibility_requires_typed_records(invalid: object) -> None:
    represented_conflict = conflict_set()
    represented_arbitration = conflict_arbitration(represented_conflict)
    with pytest.raises(InvalidDomainValue):
        can_arbitrate_evaluation_conflict_set(
            invalid,  # type: ignore[arg-type]
            represented_arbitration,
        )
    with pytest.raises(InvalidDomainValue):
        can_arbitrate_evaluation_conflict_set(
            represented_conflict,
            invalid,  # type: ignore[arg-type]
        )


def test_arbitration_creation_does_not_mutate_evaluation_or_original_result() -> None:
    original_result = EvaluationResult(
        PRIOR,
        EvaluationConfidence("opaque confidence"),
        "Original reasoning remains historical content.",
        frozenset({EvidenceRef("original evidence")}),
    )
    original = Evaluation(
        EvaluationId(UUID(int=1)),
        EvaluationState.COMPLETED,
        EntityVersion(3),
        EvaluationTargetRef(OutcomeId(UUID(int=20)), EntityVersion(2)),
        EvaluationMethodRef("method", "v1"),
        DECIDER,
        original_result,
    )
    before = replace(original)
    represented = arbitration(
        decisions=frozenset(
            {
                decision(
                    1,
                    3,
                    ArbitrationDisposition.REVERSED,
                    PRIOR,
                    EFFECTIVE,
                )
            }
        )
    )
    assert represented.decisions != frozenset()
    assert original == before
    assert original.result is original_result
    assert original.result.verdict is PRIOR
    assert original.state is EvaluationState.COMPLETED
    assert original.version == EntityVersion(3)
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
        "effective_judgement",
        "arbitration_id",
        "arbitration_disposition",
        "override",
        "arbitrate",
    ):
        assert not hasattr(original, absent)


def test_m5c1_exposes_no_resolution_event_or_repository_behavior() -> None:
    for absent in (
        "is_evaluation_resolved",
        "current_effective_judgement",
        "remaining_open_conflicts",
        "can_release_evaluation",
        "EvaluationArbitrated",
        "EvaluationArbitrationRepository",
        "ArbitrationState",
        "ArbitrationController",
    ):
        assert not hasattr(domain, absent)
