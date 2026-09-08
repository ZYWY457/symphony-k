"""Effect pre-commit provenance remains exact, immutable, and orthogonal."""

from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

import symphony_k.domain.effect_execution as execution_module
from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CorrelationId,
    Effect,
    EffectAuthorizationFindingId,
    EffectExecutionAuthorizationId,
    EffectExecutionAuthorizationRecord,
    EffectGovernanceFindingId,
    EffectId,
    EffectIncidentId,
    EffectObservationId,
    EffectPayloadRef,
    EffectPreparationRecord,
    EffectPreparationRecordId,
    EffectRollbackRecordId,
    EffectState,
    EffectTargetRef,
    EffectVerificationRecord,
    EffectVerificationRecordId,
    EntityVersion,
    EvidenceRef,
    InvalidDomainValue,
    PlannedEffectOrigin,
    TaskId,
    Timestamp,
    can_attach_effect_preparation_record,
    can_authorize_effect_preparation,
    can_use_effect_verification_for_authorization,
    can_verify_effect_preparation,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
EFFECT_ID = EffectId(VALUE)
PREPARATION_ID = EffectPreparationRecordId(VALUE)
VERIFICATION_ID = EffectVerificationRecordId(VALUE)
AUTHORIZATION_ID = EffectExecutionAuthorizationId(VALUE)
VERSION = EntityVersion(7)
CORRELATION = CorrelationId(VALUE)


def actor(category: ActorType) -> ActorIdentity:
    return ActorIdentity(ActorId(VALUE), category)


def instant(day: int = 8) -> Timestamp:
    return Timestamp(datetime(2026, 9, day, tzinfo=UTC))


def effect(
    *,
    effect_id: EffectId = EFFECT_ID,
    version: EntityVersion = VERSION,
    state: EffectState = EffectState.SIMULATED,
) -> Effect:
    return Effect(
        effect_id,
        state,
        version,
        PlannedEffectOrigin(
            TaskId(VALUE),
            actor(ActorType.WORKER),
        ),
        EffectTargetRef("deployment target"),
        EffectPayloadRef("sha256:prepared-payload"),
    )


def preparation(
    *,
    preparation_id: EffectPreparationRecordId = PREPARATION_ID,
    effect_id: EffectId = EFFECT_ID,
    version: EntityVersion = VERSION,
    correlation: CorrelationId = CORRELATION,
) -> EffectPreparationRecord:
    return EffectPreparationRecord(
        preparation_id,
        effect_id,
        version,
        "Exact deployment payload prepared without external mutation",
        actor(ActorType.EFFECT_CONTROLLER),
        actor(ActorType.SYSTEM),
        instant(),
        instant(9),
        correlation,
    )


def verification(
    *,
    verification_id: EffectVerificationRecordId = VERIFICATION_ID,
    preparation_id: EffectPreparationRecordId = PREPARATION_ID,
    effect_id: EffectId = EFFECT_ID,
    version: EntityVersion = VERSION,
    correlation: CorrelationId = CORRELATION,
) -> EffectVerificationRecord:
    return EffectVerificationRecord(
        verification_id,
        preparation_id,
        effect_id,
        version,
        "Independent checks verified the exact prepared payload",
        frozenset({EvidenceRef("verification report")}),
        actor(ActorType.EVALUATOR),
        actor(ActorType.SYSTEM),
        instant(),
        instant(9),
        correlation,
    )


def authorization(
    *,
    authorization_id: EffectExecutionAuthorizationId = AUTHORIZATION_ID,
    preparation_id: EffectPreparationRecordId = PREPARATION_ID,
    effect_id: EffectId = EFFECT_ID,
    version: EntityVersion = VERSION,
    verification_ids: frozenset[EffectVerificationRecordId] = frozenset(
        {VERIFICATION_ID}
    ),
    correlation: CorrelationId = CORRELATION,
    authorized_by: ActorIdentity | None = None,
) -> EffectExecutionAuthorizationRecord:
    return EffectExecutionAuthorizationRecord(
        authorization_id,
        preparation_id,
        effect_id,
        version,
        verification_ids,
        "Prospective permission for the exact prepared and verified payload",
        frozenset({EvidenceRef("authorization decision")}),
        authorized_by or actor(ActorType.POLICY_ENGINE),
        actor(ActorType.SYSTEM),
        instant(),
        instant(9),
        correlation,
    )


def test_precommit_record_identities_are_nominal_and_distinct() -> None:
    assert (
        len(
            {
                EffectPreparationRecordId(VALUE),
                EffectVerificationRecordId(VALUE),
                EffectExecutionAuthorizationId(VALUE),
                EffectAuthorizationFindingId(VALUE),
                EffectId(VALUE),
                EffectObservationId(VALUE),
                EffectGovernanceFindingId(VALUE),
                EffectIncidentId(VALUE),
                EffectRollbackRecordId(VALUE),
                CorrelationId(VALUE),
            }
        )
        == 10
    )


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("preparation_id", EffectId(VALUE)),
        ("effect_id", EffectObservationId(VALUE)),
        ("observed_effect_version", 7),
        ("preparation_summary", " \t"),
        ("prepared_by", ActorId(VALUE)),
        ("recorded_by", ActorType.SYSTEM),
        ("prepared_at", datetime(2026, 9, 8, tzinfo=UTC)),
        ("recorded_at", datetime(2026, 9, 9, tzinfo=UTC)),
        ("correlation_id", EffectId(VALUE)),
    ],
)
def test_preparation_rejects_invalid_or_missing_provenance(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(preparation(), **{field: invalid})  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("verification_id", EffectPreparationRecordId(VALUE)),
        ("preparation_id", EffectVerificationRecordId(VALUE)),
        ("effect_id", EffectObservationId(VALUE)),
        ("observed_effect_version", 7),
        ("verification_summary", " \t"),
        ("evidence_refs", frozenset()),
        ("evidence_refs", frozenset({"raw"})),
        ("verified_by", ActorId(VALUE)),
        ("recorded_by", ActorType.SYSTEM),
        ("verified_at", datetime(2026, 9, 8, tzinfo=UTC)),
        ("recorded_at", datetime(2026, 9, 9, tzinfo=UTC)),
        ("correlation_id", EffectId(VALUE)),
    ],
)
def test_verification_rejects_invalid_or_missing_provenance(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(verification(), **{field: invalid})  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("authorization_id", EffectAuthorizationFindingId(VALUE)),
        ("preparation_id", EffectVerificationRecordId(VALUE)),
        ("effect_id", EffectObservationId(VALUE)),
        ("authorized_effect_version", 7),
        ("verification_ids", frozenset()),
        ("verification_ids", frozenset({EffectPreparationRecordId(VALUE)})),
        ("authorization_summary", " \t"),
        ("evidence_refs", frozenset()),
        ("evidence_refs", frozenset({"raw"})),
        ("authorized_by", ActorId(VALUE)),
        ("recorded_by", ActorType.SYSTEM),
        ("authorized_at", datetime(2026, 9, 8, tzinfo=UTC)),
        ("recorded_at", datetime(2026, 9, 9, tzinfo=UTC)),
        ("correlation_id", EffectId(VALUE)),
    ],
)
def test_authorization_rejects_invalid_or_missing_provenance(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(authorization(), **{field: invalid})  # type: ignore[arg-type]


@pytest.mark.parametrize("record", [preparation(), verification(), authorization()])
def test_precommit_records_are_frozen(
    record: (
        EffectPreparationRecord
        | EffectVerificationRecord
        | EffectExecutionAuthorizationRecord
    ),
) -> None:
    for field in fields(record):
        with pytest.raises(FrozenInstanceError):
            setattr(record, field.name, getattr(record, field.name))


def test_records_expose_only_the_required_provenance_dimensions() -> None:
    assert tuple(field.name for field in fields(EffectPreparationRecord)) == (
        "preparation_id",
        "effect_id",
        "observed_effect_version",
        "preparation_summary",
        "prepared_by",
        "recorded_by",
        "prepared_at",
        "recorded_at",
        "correlation_id",
    )
    assert tuple(field.name for field in fields(EffectVerificationRecord)) == (
        "verification_id",
        "preparation_id",
        "effect_id",
        "observed_effect_version",
        "verification_summary",
        "evidence_refs",
        "verified_by",
        "recorded_by",
        "verified_at",
        "recorded_at",
        "correlation_id",
    )
    assert tuple(
        field.name for field in fields(EffectExecutionAuthorizationRecord)
    ) == (
        "authorization_id",
        "preparation_id",
        "effect_id",
        "authorized_effect_version",
        "verification_ids",
        "authorization_summary",
        "evidence_refs",
        "authorized_by",
        "recorded_by",
        "authorized_at",
        "recorded_at",
        "correlation_id",
    )


@pytest.mark.parametrize("state", list(EffectState))
def test_preparation_attachment_requires_only_exact_identity_and_version(
    state: EffectState,
) -> None:
    snapshot = effect(state=state)
    assert can_attach_effect_preparation_record(snapshot, preparation())
    assert not can_attach_effect_preparation_record(
        snapshot, preparation(effect_id=EffectId(OTHER))
    )
    assert not can_attach_effect_preparation_record(
        snapshot, preparation(version=EntityVersion(6))
    )
    assert not can_attach_effect_preparation_record(
        snapshot, preparation(version=EntityVersion(8))
    )
    assert snapshot.state is state


def test_preparation_and_verification_require_explicit_exact_context() -> None:
    prepared = preparation()
    assert can_verify_effect_preparation(prepared, verification())
    assert not can_verify_effect_preparation(
        prepared,
        verification(preparation_id=EffectPreparationRecordId(OTHER)),
    )
    assert not can_verify_effect_preparation(
        prepared, verification(effect_id=EffectId(OTHER))
    )
    assert not can_verify_effect_preparation(
        prepared, verification(version=EntityVersion(6))
    )
    assert not can_verify_effect_preparation(
        prepared, verification(version=EntityVersion(8))
    )
    assert not can_verify_effect_preparation(
        prepared, verification(correlation=CorrelationId(OTHER))
    )
    assert can_verify_effect_preparation(
        replace(prepared, prepared_at=instant(9), recorded_at=instant()),
        replace(verification(), verified_at=instant(7), recorded_at=instant(6)),
    )


def test_preparation_and_authorization_require_explicit_exact_context() -> None:
    prepared = preparation()
    assert can_authorize_effect_preparation(prepared, authorization())
    assert not can_authorize_effect_preparation(
        prepared,
        authorization(preparation_id=EffectPreparationRecordId(OTHER)),
    )
    assert not can_authorize_effect_preparation(
        prepared, authorization(effect_id=EffectId(OTHER))
    )
    assert not can_authorize_effect_preparation(
        prepared, authorization(version=EntityVersion(6))
    )
    assert not can_authorize_effect_preparation(
        prepared, authorization(version=EntityVersion(8))
    )
    assert not can_authorize_effect_preparation(
        prepared, authorization(correlation=CorrelationId(OTHER))
    )
    assert can_authorize_effect_preparation(
        replace(prepared, prepared_at=instant(9), recorded_at=instant()),
        replace(authorization(), authorized_at=instant(7), recorded_at=instant(6)),
    )


def test_authorization_uses_only_explicitly_referenced_exact_verification() -> None:
    checked = verification()
    grant = authorization()
    assert can_use_effect_verification_for_authorization(checked, grant)
    assert not can_use_effect_verification_for_authorization(
        replace(checked, verification_id=EffectVerificationRecordId(OTHER)), grant
    )
    assert not can_use_effect_verification_for_authorization(
        replace(checked, preparation_id=EffectPreparationRecordId(OTHER)), grant
    )
    assert not can_use_effect_verification_for_authorization(
        replace(checked, effect_id=EffectId(OTHER)), grant
    )
    assert not can_use_effect_verification_for_authorization(
        replace(checked, observed_effect_version=EntityVersion(6)), grant
    )
    assert not can_use_effect_verification_for_authorization(
        replace(checked, observed_effect_version=EntityVersion(8)), grant
    )
    assert not can_use_effect_verification_for_authorization(
        replace(checked, correlation_id=CorrelationId(OTHER)), grant
    )
    assert can_use_effect_verification_for_authorization(
        replace(checked, verified_at=instant(10), recorded_at=instant(11)),
        replace(grant, authorized_at=instant(7), recorded_at=instant(6)),
    )


def test_changed_effect_version_inherits_no_precommit_provenance() -> None:
    changed = effect(version=EntityVersion(8))
    prepared = preparation()
    checked = verification()
    grant = authorization()
    assert not can_attach_effect_preparation_record(changed, prepared)
    assert not can_verify_effect_preparation(
        preparation(version=changed.version), checked
    )
    assert not can_authorize_effect_preparation(
        preparation(version=changed.version), grant
    )
    assert not can_use_effect_verification_for_authorization(
        verification(version=changed.version), grant
    )


def test_human_authorization_is_representable_without_actor_type_policy() -> None:
    human = actor(ActorType.HUMAN_OPERATOR)
    record = authorization(authorized_by=human)
    assert record.authorized_by is human
    assert can_authorize_effect_preparation(preparation(), record)


def test_records_are_orthogonal_to_lifecycle_occurrence_and_historical_truth() -> None:
    snapshot = effect(state=EffectState.PLANNED)
    prepared = preparation()
    checked = verification()
    grant = authorization()
    assert snapshot.state is EffectState.PLANNED
    assert checked.verification_id in grant.verification_ids
    assert not isinstance(grant.authorization_id, EffectAuthorizationFindingId)
    for record in (prepared, checked, grant):
        for name in (
            "state",
            "status",
            "occurrence_status",
            "governance_status",
            "incident_status",
            "prior_finding_id",
            "original_commit_observation_id",
        ):
            assert not hasattr(record, name)


def test_module_has_no_retroactive_resolver_mutation_or_execution_api() -> None:
    for name in (
        "EffectObservationRecord",
        "EffectAuthorizationFindingRecord",
        "EffectGovernanceFindingRecord",
        "EffectIncidentRecord",
        "EffectRollbackRecord",
        "EffectCompensationPlanRecord",
        "EffectCompensationCompletionRecord",
        "latest_authorization",
        "effective_authorization",
        "authorize_occurrence",
        "authorization_finding",
        "governance_finding",
        "transition",
        "commit",
        "execute",
        "rollback",
        "compensate",
        "repository",
        "policy_engine",
        "permission_engine",
        "risk_engine",
        "break_glass",
        "approve",
    ):
        assert not hasattr(execution_module, name)
        assert not hasattr(authorization(), name)


@pytest.mark.parametrize(
    ("function", "left", "right"),
    [
        (can_attach_effect_preparation_record, effect(), EFFECT_ID),
        (can_verify_effect_preparation, preparation(), PREPARATION_ID),
        (can_authorize_effect_preparation, preparation(), AUTHORIZATION_ID),
        (
            can_use_effect_verification_for_authorization,
            verification(),
            AUTHORIZATION_ID,
        ),
    ],
)
def test_compatibility_helpers_reject_wrong_record_types(
    function: object, left: object, right: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        function(left, right)  # type: ignore[operator]
