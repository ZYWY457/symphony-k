"""Effect attribution records preserve immutable creation-time provenance."""

from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

import symphony_k.domain.effect_attribution as attribution_module
from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    CorrelationId,
    Effect,
    EffectAttributionId,
    EffectAttributionRecord,
    EffectExternalOperationRef,
    EffectId,
    EffectPayloadRef,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    EvidenceRef,
    InvalidDomainValue,
    ObservedEffectOrigin,
    PlannedEffectOrigin,
    RunId,
    TaskId,
    Timestamp,
    can_attach_effect_attribution,
    can_follow_effect_attribution,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
THIRD = UUID("abcdefab-cdef-4def-8def-abcdefabcdef")
ATTRIBUTION_ID = EffectAttributionId(VALUE)
EFFECT_ID = EffectId(VALUE)
TASK_ID = TaskId(VALUE)
RUN_ID = RunId(VALUE)
VERSION = EntityVersion(7)
CORRELATION = CorrelationId(VALUE)


def actor(category: ActorType) -> ActorIdentity:
    return ActorIdentity(ActorId(VALUE), category)


def instant(day: int = 8) -> Timestamp:
    return Timestamp(datetime(2026, 9, day, tzinfo=UTC))


def record(
    *,
    attribution_id: EffectAttributionId = ATTRIBUTION_ID,
    effect_id: EffectId = EFFECT_ID,
    version: EntityVersion = VERSION,
    task_id: TaskId = TASK_ID,
    run_id: RunId | None = None,
    correlation: CorrelationId = CORRELATION,
    prior: EffectAttributionId | None = None,
) -> EffectAttributionRecord:
    return EffectAttributionRecord(
        attribution_id,
        effect_id,
        version,
        task_id,
        run_id,
        frozenset({EvidenceRef("independent receipt")}),
        "Evidence verifies this association",
        actor(ActorType.EVALUATOR),
        actor(ActorType.EFFECT_CONTROLLER),
        instant(),
        instant(9),
        correlation,
        prior,
    )


def observed_effect(
    *, task_id: TaskId | None = None, run_id: RunId | None = None
) -> Effect:
    return Effect(
        EFFECT_ID,
        EffectState.COMMITTED,
        VERSION,
        ObservedEffectOrigin(
            EffectExternalOperationRef("operation"),
            frozenset({EvidenceRef("creation evidence")}),
            actor(ActorType.EFFECT_CONTROLLER),
            instant(),
            task_id,
            run_id,
            None if task_id is not None else "Attribution unknown",
        ),
        EffectTargetRef("target"),
        None,
    )


def test_attribution_identity_is_nominal_and_record_is_frozen() -> None:
    value = record()
    assert len({ATTRIBUTION_ID, EFFECT_ID, TASK_ID, RUN_ID, CORRELATION}) == 5
    for field in fields(value):
        with pytest.raises(FrozenInstanceError):
            setattr(value, field.name, getattr(value, field.name))
    with pytest.raises(AttributeError):
        value.evidence_refs.add(EvidenceRef("later"))  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("attribution_id", EffectId(VALUE)),
        ("effect_id", EffectAttributionId(VALUE)),
        ("observed_effect_version", 7),
        ("task_id", RunId(VALUE)),
        ("run_id", TaskId(VALUE)),
        ("evidence_refs", frozenset()),
        ("evidence_refs", frozenset({"raw"})),
        ("attribution_summary", " \t"),
        ("verified_by", ActorId(VALUE)),
        ("recorded_by", ActorType.EFFECT_CONTROLLER),
        ("verified_at", datetime(2026, 9, 8, tzinfo=UTC)),
        ("recorded_at", datetime(2026, 9, 9, tzinfo=UTC)),
        ("correlation_id", EffectId(VALUE)),
        ("prior_attribution_id", EffectId(OTHER)),
    ],
)
def test_record_rejects_wrong_typed_or_empty_fields(field: str, invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(record(), **{field: invalid})  # type: ignore[arg-type]


def test_record_rejects_self_reference_but_allows_explicit_prior() -> None:
    with pytest.raises(InvalidDomainValue):
        record(prior=ATTRIBUTION_ID)
    assert record(
        attribution_id=EffectAttributionId(OTHER), prior=ATTRIBUTION_ID
    ).prior_attribution_id == ATTRIBUTION_ID


def test_observed_effect_attachment_preserves_known_and_unknown_origin() -> None:
    unlinked = observed_effect()
    assert can_attach_effect_attribution(unlinked, record())
    assert can_attach_effect_attribution(unlinked, record(run_id=RUN_ID))
    assert unlinked.origin.task_id is None
    assert unlinked.origin.run_id is None
    assert unlinked.origin.unlinked_reason == "Attribution unknown"

    known_task = observed_effect(task_id=TASK_ID)
    assert can_attach_effect_attribution(known_task, record())
    assert not can_attach_effect_attribution(
        known_task, record(task_id=TaskId(OTHER))
    )
    assert can_attach_effect_attribution(known_task, record(run_id=RUN_ID))

    known_run = observed_effect(task_id=TASK_ID, run_id=RUN_ID)
    assert can_attach_effect_attribution(known_run, record(run_id=RUN_ID))
    assert not can_attach_effect_attribution(known_run, record(run_id=RunId(OTHER)))


def test_attachment_requires_exact_observation_effect_identity_and_version() -> None:
    effect = observed_effect()
    assert not can_attach_effect_attribution(effect, record(effect_id=EffectId(OTHER)))
    assert not can_attach_effect_attribution(effect, record(version=EntityVersion(6)))
    assert not can_attach_effect_attribution(effect, record(version=EntityVersion(8)))
    planned = Effect(
        EFFECT_ID,
        EffectState.PLANNED,
        VERSION,
        PlannedEffectOrigin(TASK_ID, actor(ActorType.WORKER)),
        EffectTargetRef("target"),
        EffectPayloadRef("payload"),
    )
    assert not can_attach_effect_attribution(planned, record())


def test_lineage_refines_only_same_task_effect_and_correlation() -> None:
    previous = record()
    with_run = record(
        attribution_id=EffectAttributionId(OTHER),
        prior=previous.attribution_id,
        run_id=RUN_ID,
    )
    assert can_follow_effect_attribution(previous, with_run)
    assert can_follow_effect_attribution(
        previous, replace(with_run, run_id=None, observed_effect_version=EntityVersion(8))
    )
    known_run = replace(previous, run_id=RUN_ID)
    same_run = replace(with_run, prior_attribution_id=known_run.attribution_id)
    assert can_follow_effect_attribution(known_run, same_run)
    assert not can_follow_effect_attribution(known_run, replace(same_run, run_id=RunId(THIRD)))
    assert not can_follow_effect_attribution(previous, replace(with_run, task_id=TaskId(OTHER)))
    assert not can_follow_effect_attribution(previous, replace(with_run, effect_id=EffectId(OTHER)))
    assert not can_follow_effect_attribution(previous, replace(with_run, correlation_id=CorrelationId(OTHER)))
    assert not can_follow_effect_attribution(previous, replace(with_run, observed_effect_version=EntityVersion(6)))
    assert can_follow_effect_attribution(previous, replace(with_run, observed_effect_version=VERSION))
    assert not can_follow_effect_attribution(
        previous, replace(with_run, prior_attribution_id=EffectAttributionId(THIRD))
    )


def test_attribution_is_supporting_history_without_resolver_or_authority() -> None:
    value = record()
    for name in (
        "authorized", "policy_passed", "execution_allowed", "incident_status",
        "current_task", "current_run", "latest_attribution", "effective_attribution",
    ):
        assert not hasattr(value, name)
        assert not hasattr(attribution_module, name)
    with pytest.raises(InvalidDomainValue):
        can_attach_effect_attribution(observed_effect(), value.effect_id)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        can_follow_effect_attribution(value, value.attribution_id)  # type: ignore[arg-type]
