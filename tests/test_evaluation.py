"""Evaluation representation and original-content boundaries, not verification."""

from dataclasses import MISSING, fields, replace
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArtifactRef,
    EntityVersion,
    Evaluation,
    EvaluationConfidence,
    EvaluationId,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationState,
    EvaluationTargetRef,
    EvaluationVerdict,
    EvidenceRef,
    InvalidDomainValue,
    Outcome,
    OutcomeId,
    OutcomeState,
    RunId,
    can_evaluation_transition,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")


@pytest.fixture
def snapshot() -> Evaluation:
    return Evaluation(
        evaluation_id=EvaluationId(VALUE),
        state=EvaluationState.PENDING,
        version=EntityVersion(17),
        target=EvaluationTargetRef(OutcomeId(VALUE), EntityVersion(3)),
        method=EvaluationMethodRef("opaque method", "revision"),
    )


@pytest.fixture
def result() -> EvaluationResult:
    return EvaluationResult(
        EvaluationVerdict("Requirement is not met"),
        EvaluationConfidence("Uncalibrated supplied assessment"),
        "The observed candidate lacks the requested property.",
        frozenset({EvidenceRef("opaque observation")}),
    )


def test_typed_snapshot_fields_and_unassigned_request(snapshot: Evaluation) -> None:
    assert snapshot.evaluation_id == EvaluationId(VALUE)
    assert snapshot.state is EvaluationState.PENDING
    assert snapshot.version == EntityVersion(17)
    assert snapshot.target == EvaluationTargetRef(OutcomeId(VALUE), EntityVersion(3))
    assert snapshot.method == EvaluationMethodRef("opaque method", "revision")
    assert snapshot.verifier is None
    assert snapshot.result is None
    assert {field.name for field in fields(Evaluation)} == {
        "evaluation_id",
        "state",
        "version",
        "target",
        "method",
        "verifier",
        "result",
    }


def test_state_and_version_have_no_defaults() -> None:
    definitions = {field.name: field for field in fields(Evaluation)}
    for name in ("evaluation_id", "state", "version", "target", "method"):
        assert definitions[name].default is MISSING
        assert definitions[name].default_factory is MISSING


@pytest.mark.parametrize("version", [0, 1, 41])
def test_snapshot_does_not_assign_a_global_initial_version(
    snapshot: Evaluation, version: int
) -> None:
    represented = replace(snapshot, version=EntityVersion(version))
    assert represented.version.value == version
    assert snapshot.version.value == 17


@pytest.mark.parametrize("state", list(EvaluationState))
@pytest.mark.parametrize("has_result", [False, True])
def test_exact_result_presence_matrix(
    snapshot: Evaluation,
    result: EvaluationResult,
    state: EvaluationState,
    has_result: bool,
) -> None:
    allowed = {
        EvaluationState.PENDING: {False},
        EvaluationState.RUNNING: {False},
        EvaluationState.COMPLETED: {True},
        EvaluationState.CONFLICTED: {False, True},
        EvaluationState.ARBITRATED: {False, True},
        EvaluationState.INVALID: {False, True},
    }
    supplied = result if has_result else None
    if has_result in allowed[state]:
        represented = replace(snapshot, state=state, result=supplied)
        assert represented.result is supplied
        assert represented.state is state
        assert represented.version == snapshot.version
    else:
        with pytest.raises(InvalidDomainValue):
            replace(snapshot, state=state, result=supplied)
    assert snapshot.state is EvaluationState.PENDING and snapshot.result is None


@pytest.mark.parametrize("field", [field.name for field in fields(Evaluation)])
def test_snapshot_fields_are_immutable(snapshot: Evaluation, field: str) -> None:
    with pytest.raises(AttributeError):
        setattr(snapshot, field, getattr(snapshot, field))
    with pytest.raises(AttributeError):
        delattr(snapshot, field)


@pytest.mark.parametrize("category", list(ActorType))
def test_verifier_provenance_has_no_role_authority_semantics(
    snapshot: Evaluation, category: ActorType
) -> None:
    verifier = ActorIdentity(ActorId(VALUE), category)
    represented = replace(snapshot, verifier=verifier)
    assert represented.verifier is verifier
    assert represented.state is EvaluationState.PENDING
    assert represented.version == snapshot.version


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("evaluation_id", RunId(VALUE)),
        ("evaluation_id", VALUE),
        ("evaluation_id", None),
        ("state", "PENDING"),
        ("state", OutcomeState.VALIDATING),
        ("state", None),
        ("version", 0),
        ("version", True),
        ("version", None),
        ("target", OutcomeId(VALUE)),
        ("target", "target"),
        ("target", None),
        ("method", "method"),
        ("method", None),
        ("method", EvaluationVerdict("text")),
        ("verifier", ActorId(VALUE)),
        ("verifier", ActorType.EVALUATOR),
        ("verifier", "verifier"),
        ("result", True),
        ("result", "result"),
        ("result", EvaluationVerdict("text")),
    ],
)
def test_snapshot_rejects_malformed_fields(
    snapshot: Evaluation, field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, **{field: invalid})  # type: ignore[arg-type]


def test_unfavorable_verdict_is_a_completed_evaluation(
    snapshot: Evaluation, result: EvaluationResult
) -> None:
    completed = replace(snapshot, state=EvaluationState.COMPLETED, result=result)
    assert completed.state is EvaluationState.COMPLETED
    assert completed.result is result
    assert completed.result.verdict.value == "Requirement is not met"


@pytest.mark.parametrize(
    "state",
    [EvaluationState.CONFLICTED, EvaluationState.ARBITRATED, EvaluationState.INVALID],
)
def test_later_projection_preserves_original_result_and_verifier(
    snapshot: Evaluation, result: EvaluationResult, state: EvaluationState
) -> None:
    verifier = ActorIdentity(ActorId(VALUE), ActorType.EVALUATOR)
    completed = replace(
        snapshot, state=EvaluationState.COMPLETED, result=result, verifier=verifier
    )
    represented = replace(completed, state=state)
    assert represented.result is result
    assert represented.verifier is verifier
    assert represented.method is completed.method
    assert represented.target is completed.target
    assert completed.state is EvaluationState.COMPLETED
    with pytest.raises(AttributeError):
        represented.result = None  # type: ignore[misc]
    with pytest.raises(AttributeError):
        verifier.actor_type = ActorType.HUMAN_OPERATOR  # type: ignore[misc]
    with pytest.raises(AttributeError):
        represented.method.method_id = "replacement"  # type: ignore[misc]
    assert represented.result is result
    assert result.verdict.value == "Requirement is not met"


def test_structural_queries_do_not_verify_authorize_or_accept_an_outcome(
    snapshot: Evaluation, result: EvaluationResult
) -> None:
    producer = ActorIdentity(ActorId(VALUE), ActorType.WORKER)
    outcome = Outcome(
        OutcomeId(VALUE),
        RunId(VALUE),
        OutcomeState.VALIDATING,
        EntityVersion(3),
        producer,
        frozenset({ArtifactRef("candidate")}),
    )
    completed = replace(
        snapshot, state=EvaluationState.COMPLETED, verifier=producer, result=result
    )
    assert completed.target.reference == outcome.outcome_id
    assert can_evaluation_transition(completed.state, EvaluationState.CONFLICTED)
    assert can_evaluation_transition(completed.state, EvaluationState.ARBITRATED)
    assert can_evaluation_transition(completed.state, EvaluationState.INVALID)
    assert completed.verifier is producer  # No producer-independence guard is run here.
    assert (
        completed.state is EvaluationState.COMPLETED and completed.version.value == 17
    )
    assert outcome.state is OutcomeState.VALIDATING and outcome.version.value == 3
    for name in (
        "start",
        "complete",
        "transition",
        "with_state",
        "delete",
        "verify",
        "change_verdict",
        "override_result",
        "replace_evidence",
        "set_effective_verdict",
        "conflict_set",
        "arbitration_record",
        "arbitration_disposition",
        "invalidation_history",
        "effective_verdict",
        "events",
        "authorize",
    ):
        assert not hasattr(completed, name)
