"""Effect authorization and governance findings are immutable supporting history."""

from collections.abc import Callable
from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

import symphony_k.domain.effect_authorization as authorization_module
import symphony_k.domain.effect_governance as governance_module
from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CorrelationId,
    Effect,
    EffectAuthorizationFindingId,
    EffectAuthorizationFindingRecord,
    EffectAuthorizationStatus,
    EffectExternalOperationRef,
    EffectGovernanceFindingId,
    EffectGovernanceFindingRecord,
    EffectGovernancePolicyRef,
    EffectGovernanceStatus,
    EffectId,
    EffectObservationId,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    EvidenceRef,
    InvalidDomainValue,
    ObservedEffectOrigin,
    Timestamp,
    can_attach_effect_authorization_finding,
    can_attach_effect_governance_finding,
    can_follow_effect_authorization_finding,
    can_follow_effect_governance_finding,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
THIRD = UUID("abcdefab-cdef-4def-8def-abcdefabcdef")
EFFECT_ID = EffectId(VALUE)
VERSION = EntityVersion(7)
CORRELATION = CorrelationId(VALUE)
POLICY = EffectGovernancePolicyRef("change-control", "v1")
AUTHORIZATION_FINDING_ID = EffectAuthorizationFindingId(VALUE)
GOVERNANCE_FINDING_ID = EffectGovernanceFindingId(VALUE)


def actor(category: ActorType) -> ActorIdentity:
    return ActorIdentity(ActorId(VALUE), category)


def instant(day: int = 8) -> Timestamp:
    return Timestamp(datetime(2026, 9, day, tzinfo=UTC))


def effect(state: EffectState = EffectState.COMMITTED) -> Effect:
    return Effect(
        EFFECT_ID,
        state,
        VERSION,
        ObservedEffectOrigin(
            EffectExternalOperationRef("provider-operation"),
            frozenset({EvidenceRef("independent receipt")}),
            actor(ActorType.EFFECT_CONTROLLER),
            instant(),
            None,
            None,
            "Task attribution is unknown",
        ),
        EffectTargetRef("target"),
        None,
    )


def authorization(
    *,
    finding_id: EffectAuthorizationFindingId = AUTHORIZATION_FINDING_ID,
    effect_id: EffectId = EFFECT_ID,
    version: EntityVersion = VERSION,
    status: EffectAuthorizationStatus = EffectAuthorizationStatus.UNKNOWN,
    correlation: CorrelationId = CORRELATION,
    prior: EffectAuthorizationFindingId | None = None,
) -> EffectAuthorizationFindingRecord:
    return EffectAuthorizationFindingRecord(
        finding_id,
        effect_id,
        version,
        status,
        "Evidence establishes the historical authorization finding",
        frozenset({EvidenceRef("authorization evidence")}),
        actor(ActorType.EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER),
        instant(),
        instant(9),
        correlation,
        prior,
    )


def governance(
    *,
    finding_id: EffectGovernanceFindingId = GOVERNANCE_FINDING_ID,
    effect_id: EffectId = EFFECT_ID,
    version: EntityVersion = VERSION,
    policy: EffectGovernancePolicyRef = POLICY,
    status: EffectGovernanceStatus = EffectGovernanceStatus.UNKNOWN,
    correlation: CorrelationId = CORRELATION,
    prior: EffectGovernanceFindingId | None = None,
) -> EffectGovernanceFindingRecord:
    return EffectGovernanceFindingRecord(
        finding_id,
        effect_id,
        version,
        policy,
        status,
        "Evidence establishes the policy-scoped governance finding",
        frozenset({EvidenceRef("governance evidence")}),
        actor(ActorType.EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER),
        instant(),
        instant(9),
        correlation,
        prior,
    )


def test_finding_ids_and_status_inventories_are_nominal_and_separate() -> None:
    assert (
        len(
            {
                EffectAuthorizationFindingId(VALUE),
                EffectGovernanceFindingId(VALUE),
                EffectId(VALUE),
                EffectObservationId(VALUE),
                CorrelationId(VALUE),
            }
        )
        == 5
    )
    assert set(EffectAuthorizationStatus.__members__) == {
        "AUTHORIZED",
        "UNAUTHORIZED",
        "UNKNOWN",
    }
    assert set(EffectGovernanceStatus.__members__) == {
        "COMPLIANT",
        "NON_COMPLIANT",
        "UNKNOWN",
    }
    assert "AUTHORIZED" not in EffectState.__members__
    assert "NON_COMPLIANT" not in EffectState.__members__


@pytest.mark.parametrize(
    ("factory", "field", "invalid"),
    [
        (authorization, "finding_id", EffectId(VALUE)),
        (authorization, "effect_id", EffectAuthorizationFindingId(VALUE)),
        (authorization, "observed_effect_version", 7),
        (authorization, "status", "AUTHORIZED"),
        (authorization, "finding_summary", " \t"),
        (authorization, "evidence_refs", frozenset()),
        (authorization, "evidence_refs", frozenset({"raw"})),
        (authorization, "determined_by", ActorId(VALUE)),
        (authorization, "recorded_by", ActorType.EFFECT_CONTROLLER),
        (authorization, "determined_at", datetime(2026, 9, 8, tzinfo=UTC)),
        (authorization, "recorded_at", datetime(2026, 9, 9, tzinfo=UTC)),
        (authorization, "correlation_id", EffectId(VALUE)),
        (authorization, "prior_finding_id", EffectId(OTHER)),
        (governance, "finding_id", EffectId(VALUE)),
        (governance, "effect_id", EffectGovernanceFindingId(VALUE)),
        (governance, "observed_effect_version", 7),
        (governance, "policy_ref", "current-policy"),
        (governance, "status", "COMPLIANT"),
        (governance, "finding_summary", " \t"),
        (governance, "evidence_refs", frozenset()),
        (governance, "evidence_refs", frozenset({"raw"})),
        (governance, "determined_by", ActorId(VALUE)),
        (governance, "recorded_by", ActorType.EFFECT_CONTROLLER),
        (governance, "determined_at", datetime(2026, 9, 8, tzinfo=UTC)),
        (governance, "recorded_at", datetime(2026, 9, 9, tzinfo=UTC)),
        (governance, "correlation_id", EffectId(VALUE)),
        (governance, "prior_finding_id", EffectId(OTHER)),
    ],
)
def test_records_reject_invalid_typed_or_empty_values(
    factory: Callable[
        [], EffectAuthorizationFindingRecord | EffectGovernanceFindingRecord
    ],
    field: str,
    invalid: object,
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(factory(), **{field: invalid})  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "policy_id, policy_version", [("", "v1"), (" ", "v1"), ("p", ""), ("p", "\t")]
)
def test_governance_policy_reference_requires_immutable_exact_identity(
    policy_id: str, policy_version: str
) -> None:
    with pytest.raises(InvalidDomainValue):
        EffectGovernancePolicyRef(policy_id, policy_version)
    with pytest.raises(FrozenInstanceError):
        POLICY.policy_version = "v2"  # type: ignore[misc]


def test_records_are_frozen_and_prior_self_reference_is_rejected() -> None:
    authorization_record = authorization()
    governance_record = governance()
    for record in (authorization_record, governance_record):
        for field in fields(record):
            with pytest.raises(FrozenInstanceError):
                setattr(record, field.name, getattr(record, field.name))
        with pytest.raises(AttributeError):
            record.evidence_refs.add(EvidenceRef("later"))  # type: ignore[attr-defined]
    with pytest.raises(InvalidDomainValue):
        authorization(prior=authorization_record.finding_id)
    with pytest.raises(InvalidDomainValue):
        governance(prior=governance_record.finding_id)


def test_committed_confirmed_occurrence_can_remain_unauthorized() -> None:
    committed = effect()
    unauthorized = authorization(status=EffectAuthorizationStatus.UNAUTHORIZED)
    assert can_attach_effect_authorization_finding(committed, unauthorized)
    assert committed.state is EffectState.COMMITTED
    assert unauthorized.status is EffectAuthorizationStatus.UNAUTHORIZED


@pytest.mark.parametrize("state", list(EffectState))
def test_findings_attach_to_any_matching_effect_lifecycle_snapshot(
    state: EffectState,
) -> None:
    snapshot = effect(state)
    assert can_attach_effect_authorization_finding(snapshot, authorization())
    assert can_attach_effect_governance_finding(snapshot, governance())


def test_attachment_requires_exact_effect_id_and_version_without_mutation() -> None:
    snapshot = effect()
    assert not can_attach_effect_authorization_finding(
        snapshot, authorization(effect_id=EffectId(OTHER))
    )
    assert not can_attach_effect_authorization_finding(
        snapshot, authorization(version=EntityVersion(6))
    )
    assert not can_attach_effect_authorization_finding(
        snapshot, authorization(version=EntityVersion(8))
    )
    assert not can_attach_effect_governance_finding(
        snapshot, governance(effect_id=EffectId(OTHER))
    )
    assert not can_attach_effect_governance_finding(
        snapshot, governance(version=EntityVersion(6))
    )
    assert not can_attach_effect_governance_finding(
        snapshot, governance(version=EntityVersion(8))
    )
    with pytest.raises(InvalidDomainValue):
        can_attach_effect_authorization_finding(snapshot, EFFECT_ID)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        can_attach_effect_governance_finding(snapshot, EFFECT_ID)  # type: ignore[arg-type]


def test_authorization_lineage_requires_explicit_lineage_context() -> None:
    previous = authorization()
    current = authorization(
        finding_id=EffectAuthorizationFindingId(OTHER),
        status=EffectAuthorizationStatus.AUTHORIZED,
        prior=previous.finding_id,
    )
    unauthorized = replace(current, status=EffectAuthorizationStatus.UNAUTHORIZED)
    assert can_follow_effect_authorization_finding(previous, current)
    assert can_follow_effect_authorization_finding(previous, unauthorized)
    assert not can_follow_effect_authorization_finding(
        previous, replace(current, prior_finding_id=EffectAuthorizationFindingId(THIRD))
    )
    assert not can_follow_effect_authorization_finding(
        previous, replace(current, effect_id=EffectId(OTHER))
    )
    assert not can_follow_effect_authorization_finding(
        previous, replace(current, correlation_id=CorrelationId(OTHER))
    )
    assert not can_follow_effect_authorization_finding(
        previous, replace(current, observed_effect_version=EntityVersion(6))
    )
    assert can_follow_effect_authorization_finding(
        previous, replace(current, observed_effect_version=EntityVersion(8))
    )


def test_governance_lineage_requires_explicit_lineage_context() -> None:
    previous = governance()
    current = governance(
        finding_id=EffectGovernanceFindingId(OTHER),
        status=EffectGovernanceStatus.COMPLIANT,
        prior=previous.finding_id,
    )
    assert can_follow_effect_governance_finding(previous, current)
    assert not can_follow_effect_governance_finding(
        previous,
        replace(current, policy_ref=EffectGovernancePolicyRef("change-control", "v2")),
    )
    assert not can_follow_effect_governance_finding(
        previous, replace(current, prior_finding_id=EffectGovernanceFindingId(THIRD))
    )
    assert not can_follow_effect_governance_finding(
        previous, replace(current, effect_id=EffectId(OTHER))
    )
    assert not can_follow_effect_governance_finding(
        previous, replace(current, correlation_id=CorrelationId(OTHER))
    )
    assert not can_follow_effect_governance_finding(
        previous, replace(current, observed_effect_version=EntityVersion(6))
    )
    assert can_follow_effect_governance_finding(
        previous, replace(current, observed_effect_version=EntityVersion(8))
    )


def test_findings_have_no_authority_propagation_or_latest_wins_resolution() -> None:
    authorization_record = authorization()
    governance_record = governance()
    for name in (
        "authorize",
        "grant",
        "approve",
        "permission_token",
        "execution_allowed",
        "current_authorization_status",
        "latest_authorization_finding",
    ):
        assert not hasattr(authorization_record, name)
        assert not hasattr(authorization_module, name)
    for name in ("authorize", "execution_allowed", "latest_governance_finding"):
        assert not hasattr(governance_record, name)
        assert not hasattr(governance_module, name)
    assert authorization_record.status is EffectAuthorizationStatus.UNKNOWN
    assert (
        authorization_record.status.value != EffectAuthorizationStatus.AUTHORIZED.value
    )
    assert governance_record.status is EffectGovernanceStatus.UNKNOWN
    assert governance_record.policy_ref == POLICY
