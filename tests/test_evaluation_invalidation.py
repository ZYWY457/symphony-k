"""Evaluation invalidation records preserve unusable-verification provenance."""

from dataclasses import MISSING, fields, replace
from datetime import UTC, datetime
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
    EvaluationInvalidationId,
    EvaluationInvalidationRecord,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationState,
    EvaluationTargetRef,
    EvaluationVerdict,
    EvidenceRef,
    InvalidDomainValue,
    OutcomeId,
    Timestamp,
    can_invalidate_evaluation,
)

EVALUATION_ID = EvaluationId(UUID("11111111-1111-4111-8111-111111111111"))
OTHER_EVALUATION_ID = EvaluationId(UUID("22222222-2222-4222-8222-222222222222"))
INVALIDATION_ID = EvaluationInvalidationId(UUID("33333333-3333-4333-8333-333333333333"))
CORRELATION_ID = CorrelationId(UUID("44444444-4444-4444-8444-444444444444"))
OBSERVED_VERSION = EntityVersion(7)
INVALIDATOR = ActorIdentity(
    ActorId(UUID("55555555-5555-4555-8555-555555555555")),
    ActorType.EVALUATOR,
)
INVALIDATED_AT = Timestamp(datetime(2026, 9, 8, 14, 0, tzinfo=UTC))
EVIDENCE = EvidenceRef("independent verifier-failure evidence")
METHOD = EvaluationMethodRef("verification-method", "v1")
TARGET = EvaluationTargetRef(OutcomeId(UUID(int=20)), EntityVersion(2))


def invalidation(
    *,
    invalidation_id: EvaluationInvalidationId = INVALIDATION_ID,
    evaluation_id: EvaluationId = EVALUATION_ID,
    observed_version: EntityVersion = OBSERVED_VERSION,
    reason: str = "The verifier failed to execute the required independent check.",
    evidence_refs: frozenset[EvidenceRef] = frozenset({EVIDENCE}),
    invalidated_by: ActorIdentity = INVALIDATOR,
    invalidated_at: Timestamp = INVALIDATED_AT,
    correlation_id: CorrelationId = CORRELATION_ID,
) -> EvaluationInvalidationRecord:
    return EvaluationInvalidationRecord(
        invalidation_id=invalidation_id,
        evaluation_id=evaluation_id,
        observed_version=observed_version,
        reason=reason,
        evidence_refs=evidence_refs,
        invalidated_by=invalidated_by,
        invalidated_at=invalidated_at,
        correlation_id=correlation_id,
    )


def evaluation(
    state: EvaluationState = EvaluationState.PENDING,
    *,
    evaluation_id: EvaluationId = EVALUATION_ID,
    version: EntityVersion = OBSERVED_VERSION,
    result: EvaluationResult | None = None,
) -> Evaluation:
    if state is EvaluationState.COMPLETED and result is None:
        result = EvaluationResult(
            EvaluationVerdict("FAIL"),
            EvaluationConfidence("high"),
            "The requirement is not satisfied.",
            frozenset({EvidenceRef("negative-verdict evidence")}),
        )
    return Evaluation(
        evaluation_id,
        state,
        version,
        TARGET,
        METHOD,
        INVALIDATOR,
        result,
    )


def test_invalidation_identity_is_nominal_immutable_and_distinct() -> None:
    shared = UUID("12345678-1234-4234-8234-123456789abc")
    identities = {
        EvaluationInvalidationId(shared),
        EvaluationId(shared),
        EvaluationArbitrationId(shared),
        EvaluationConflictSetId(shared),
        CorrelationId(shared),
    }
    assert len(identities) == 5
    parsed = EvaluationInvalidationId.from_string(str(shared))
    assert parsed == EvaluationInvalidationId(shared)
    with pytest.raises(AttributeError):
        parsed.value = UUID(int=9)  # type: ignore[misc]


def test_record_has_exact_required_immutable_fields() -> None:
    represented = invalidation()
    assert {field.name for field in fields(represented)} == {
        "invalidation_id",
        "evaluation_id",
        "observed_version",
        "reason",
        "evidence_refs",
        "invalidated_by",
        "invalidated_at",
        "correlation_id",
    }
    assert all(
        field.default is MISSING and field.default_factory is MISSING
        for field in fields(represented)
    )
    with pytest.raises(AttributeError):
        represented.reason = "replacement"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        represented.evidence_refs.add(EvidenceRef("replacement"))  # type: ignore[attr-defined]


@pytest.mark.parametrize("invalid_reason", ["", " ", "\t\n", None, 1, True])
def test_reason_requires_meaningful_free_form_text(invalid_reason: object) -> None:
    with pytest.raises(InvalidDomainValue):
        invalidation(reason=invalid_reason)  # type: ignore[arg-type]


def test_reason_remains_free_form_without_a_taxonomy() -> None:
    reason = "  custom method defect explanation\n"
    represented = invalidation(reason=reason)
    assert represented.reason == reason
    assert not hasattr(domain, "EvaluationInvalidationReason")
    assert not hasattr(domain, "InvalidationReason")


def test_at_least_one_typed_evidence_reference_is_required() -> None:
    with pytest.raises(InvalidDomainValue):
        invalidation(evidence_refs=frozenset())
    with pytest.raises(InvalidDomainValue):
        invalidation(evidence_refs=(EVIDENCE,))  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        invalidation(evidence_refs=frozenset({ArtifactRef("wrong type")}))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("invalidation_id", EvaluationArbitrationId(UUID(int=1))),
        ("evaluation_id", EvaluationInvalidationId(UUID(int=1))),
        ("observed_version", ConflictSetVersion(7)),
        ("observed_version", 7),
        ("invalidated_by", ActorType.EVALUATOR),
        ("invalidated_at", datetime(2026, 9, 8, tzinfo=UTC)),
        ("correlation_id", EvaluationConflictSetId(UUID(int=1))),
    ],
)
def test_record_rejects_wrong_field_types(field: str, invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(invalidation(), **{field: invalid})  # type: ignore[arg-type]


@pytest.mark.parametrize("category", list(ActorType))
def test_actor_category_is_provenance_not_authority(category: ActorType) -> None:
    actor = ActorIdentity(ActorId(UUID(int=91)), category)
    represented = invalidation(invalidated_by=actor)
    assert represented.invalidated_by is actor
    for absent in ("authorize", "grant", "authenticate", "apply", "transition"):
        assert not hasattr(represented, absent)


@pytest.mark.parametrize(
    "state",
    [
        EvaluationState.PENDING,
        EvaluationState.RUNNING,
        EvaluationState.COMPLETED,
        EvaluationState.CONFLICTED,
    ],
)
def test_exact_accepted_source_states_are_compatible(state: EvaluationState) -> None:
    assert can_invalidate_evaluation(evaluation(state), invalidation())


@pytest.mark.parametrize("state", [EvaluationState.ARBITRATED, EvaluationState.INVALID])
def test_strict_sink_states_are_not_compatible(state: EvaluationState) -> None:
    assert not can_invalidate_evaluation(evaluation(state), invalidation())


def test_compatibility_requires_exact_identity_and_version() -> None:
    represented = evaluation()
    assert not can_invalidate_evaluation(
        represented, invalidation(evaluation_id=OTHER_EVALUATION_ID)
    )
    assert not can_invalidate_evaluation(
        represented, invalidation(observed_version=EntityVersion(6))
    )
    assert not can_invalidate_evaluation(
        represented, invalidation(observed_version=EntityVersion(8))
    )


@pytest.mark.parametrize("invalid", [None, "record", object()])
def test_compatibility_requires_typed_inputs(invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        can_invalidate_evaluation(invalid, invalidation())  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        can_invalidate_evaluation(evaluation(), invalid)  # type: ignore[arg-type]


def test_negative_completed_verdict_is_not_invalidation() -> None:
    represented = evaluation(EvaluationState.COMPLETED)
    assert represented.result is not None
    assert represented.result.verdict == EvaluationVerdict("FAIL")
    assert represented.state is EvaluationState.COMPLETED
    assert can_invalidate_evaluation(represented, invalidation())
    assert represented.state is EvaluationState.COMPLETED


def test_invalidation_creation_and_query_preserve_original_evaluation_result() -> None:
    original = evaluation(EvaluationState.COMPLETED)
    original_result = original.result
    before = replace(original)
    represented = invalidation()
    assert can_invalidate_evaluation(original, represented)
    assert original == before
    assert original.result is original_result
    assert original.state is EvaluationState.COMPLETED
    assert original.version == EntityVersion(7)
    assert {field.name for field in fields(Evaluation)} == {
        "evaluation_id",
        "state",
        "version",
        "target",
        "method",
        "verifier",
        "result",
    }
    for absent in ("invalidation", "invalidation_id", "invalidate", "usable"):
        assert not hasattr(original, absent)


def test_conflict_and_arbitration_history_are_untouched() -> None:
    member = EvaluationConflictMemberRef(EVALUATION_ID, EntityVersion(7))
    conflict = EvaluationConflictSetRecord(
        EvaluationConflictSetId(UUID(int=60)),
        ConflictSetVersion(3),
        None,
        frozenset({member}),
        EvaluationConflictScopeRef("acceptance scope"),
        "Material disagreement.",
        frozenset({EvidenceRef("conflict evidence")}),
        INVALIDATOR,
        INVALIDATED_AT,
        CORRELATION_ID,
    )
    judgement = EvaluationVerdict("original judgement")
    arbitration = EvaluationArbitrationRecord(
        EvaluationArbitrationId(UUID(int=61)),
        EvaluationConflictSetRef(conflict.conflict_set_id, conflict.version),
        frozenset(
            {
                EvaluationArbitrationMemberDecision(
                    EVALUATION_ID,
                    EntityVersion(7),
                    ArbitrationDisposition.UPHELD,
                    judgement,
                    judgement,
                )
            }
        ),
        "Independent decision.",
        frozenset({EvidenceRef("arbitration evidence")}),
        EvaluationArbitrationPolicyRef("policy", "v1"),
        INVALIDATOR,
        INVALIDATED_AT,
        CORRELATION_ID,
    )
    conflict_before = replace(conflict)
    arbitration_before = replace(arbitration)
    represented = invalidation()
    assert represented.evaluation_id == member.evaluation_id
    assert conflict == conflict_before and conflict.members == frozenset({member})
    assert arbitration == arbitration_before


def test_m5c2_exposes_no_lifecycle_resolution_event_or_repository_behavior() -> None:
    for absent in (
        "InvalidationState",
        "EvaluationInvalidationState",
        "InvalidationController",
        "EvaluationInvalidated",
        "EvaluationInvalidationRepository",
        "current_effective_judgement",
        "is_evaluation_usable",
        "remaining_open_conflicts",
        "is_conflict_resolved",
        "latest_arbitration_wins",
    ):
        assert not hasattr(domain, absent)
