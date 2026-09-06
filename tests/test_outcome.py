"""Candidate representation and immutable provenance without verification."""

from dataclasses import MISSING, fields, replace
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArtifactRef,
    CompletionPolicyRef,
    EntityVersion,
    EvidenceRef,
    ExecutionProfileRef,
    InvalidDomainValue,
    Objective,
    ObjectiveId,
    ObjectiveState,
    Outcome,
    OutcomeId,
    OutcomeState,
    Run,
    RunId,
    RunState,
    Task,
    TaskId,
    TaskState,
    Timestamp,
    can_outcome_transition,
)

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")


@pytest.fixture
def snapshot() -> Outcome:
    return Outcome(
        outcome_id=OutcomeId(VALUE),
        run_id=RunId(VALUE),
        state=OutcomeState.PROPOSED,
        version=EntityVersion(17),
        producer=ActorIdentity(ActorId(VALUE), ActorType.WORKER),
        artifact_refs=frozenset({ArtifactRef("opaque candidate identity")}),
    )


def test_candidate_fields_preserve_provenance_without_task_ownership(
    snapshot: Outcome,
) -> None:
    assert snapshot.outcome_id == OutcomeId(VALUE)
    assert snapshot.run_id == RunId(VALUE)
    assert snapshot.producer == ActorIdentity(ActorId(VALUE), ActorType.WORKER)
    assert snapshot.state is OutcomeState.PROPOSED
    assert snapshot.version == EntityVersion(17)
    assert snapshot.artifact_refs == frozenset(
        {ArtifactRef("opaque candidate identity")}
    )
    assert snapshot.evidence_refs == frozenset()
    assert snapshot.valid_until is None
    assert snapshot.prior_outcome_id is None
    assert snapshot.superseded_by_outcome_id is None
    assert {field.name for field in fields(Outcome)} == {
        "outcome_id",
        "run_id",
        "state",
        "version",
        "producer",
        "artifact_refs",
        "evidence_refs",
        "valid_until",
        "prior_outcome_id",
        "superseded_by_outcome_id",
    }


def test_state_version_and_origin_are_explicit() -> None:
    definitions = {field.name: field for field in fields(Outcome)}
    for name in (
        "outcome_id",
        "run_id",
        "state",
        "version",
        "producer",
        "artifact_refs",
    ):
        assert definitions[name].default is MISSING
        assert definitions[name].default_factory is MISSING


@pytest.mark.parametrize("state", list(OutcomeState))
@pytest.mark.parametrize("version", [0, 1, 41])
def test_snapshots_represent_states_without_executing_creation_or_verification(
    snapshot: Outcome, state: OutcomeState, version: int
) -> None:
    replacement = OutcomeId(OTHER) if state is OutcomeState.SUPERSEDED else None
    represented = replace(
        snapshot,
        state=state,
        version=EntityVersion(version),
        superseded_by_outcome_id=replacement,
    )
    assert represented.state is state
    assert represented.version.value == version
    assert represented.evidence_refs == frozenset()
    assert represented.run_id == snapshot.run_id
    assert snapshot.state is OutcomeState.PROPOSED and snapshot.version.value == 17


@pytest.mark.parametrize("field", [field.name for field in fields(Outcome)])
def test_all_snapshot_fields_are_immutable(snapshot: Outcome, field: str) -> None:
    original = getattr(snapshot, field)
    with pytest.raises(AttributeError):
        setattr(snapshot, field, original)
    with pytest.raises(AttributeError):
        delattr(snapshot, field)
    assert getattr(snapshot, field) == original


def test_origin_and_nested_values_cannot_be_mutated(snapshot: Outcome) -> None:
    with pytest.raises(AttributeError):
        snapshot.run_id = RunId(OTHER)  # type: ignore[misc]
    with pytest.raises(AttributeError):
        snapshot.producer.actor_type = ActorType.HUMAN_OPERATOR  # type: ignore[misc]
    artifact = next(iter(snapshot.artifact_refs))
    with pytest.raises(AttributeError):
        artifact.value = "changed content identity"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        snapshot.artifact_refs.add(ArtifactRef("second"))  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        snapshot.evidence_refs |= frozenset({EvidenceRef("claim")})  # type: ignore[misc]
    assert snapshot.run_id == RunId(VALUE)
    assert snapshot.evidence_refs == frozenset()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("outcome_id", RunId(VALUE)),
        ("outcome_id", TaskId(VALUE)),
        ("outcome_id", VALUE),
        ("outcome_id", str(VALUE)),
        ("outcome_id", None),
        ("run_id", OutcomeId(VALUE)),
        ("run_id", TaskId(VALUE)),
        ("run_id", VALUE),
        ("run_id", str(VALUE)),
        ("run_id", None),
        ("run_id", (RunId(VALUE), RunId(OTHER))),
        ("producer", ActorId(VALUE)),
        ("producer", ActorType.WORKER),
        ("producer", "worker"),
        ("producer", None),
        ("state", "PROPOSED"),
        ("state", RunState.COMPLETED),
        ("state", None),
        ("version", 0),
        ("version", True),
        ("version", None),
        ("valid_until", datetime(2026, 9, 7, tzinfo=UTC)),
        ("valid_until", "2026-09-07T00:00:00+00:00"),
    ],
)
def test_wrong_or_raw_provenance_fields_are_rejected(
    snapshot: Outcome, field: str, value: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, **{field: value})  # type: ignore[arg-type]


def test_run_objects_are_not_origin_references(snapshot: Outcome) -> None:
    run = Run(
        RunId(VALUE),
        TaskId(VALUE),
        RunState.COMPLETED,
        EntityVersion(3),
        ExecutionProfileRef("profile", "revision"),
    )
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, run_id=run)  # type: ignore[arg-type]


@pytest.mark.parametrize("category", list(ActorType))
def test_all_producer_categories_are_provenance_not_authority(
    snapshot: Outcome, category: ActorType
) -> None:
    producer = ActorIdentity(ActorId(VALUE), category)
    represented = replace(snapshot, producer=producer)
    assert represented.producer == producer
    assert represented.state is OutcomeState.PROPOSED
    assert not hasattr(represented, "acceptance_authority")


@pytest.mark.parametrize(
    "references",
    [
        frozenset(),
        None,
        (),
        [],
        {ArtifactRef("artifact")},
        "artifact",
        frozenset({"raw"}),
        frozenset({EvidenceRef("evidence")}),
        frozenset({ArtifactRef("artifact"), None}),
    ],
)
def test_artifacts_must_be_nonempty_immutable_and_typed(
    snapshot: Outcome, references: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, artifact_refs=references)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "references",
    [
        None,
        (),
        [],
        {EvidenceRef("evidence")},
        "evidence",
        frozenset({"raw"}),
        frozenset({ArtifactRef("artifact")}),
        frozenset({EvidenceRef("evidence"), None}),
    ],
)
def test_evidence_is_immutable_and_typed_not_independently_validated(
    snapshot: Outcome, references: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, evidence_refs=references)  # type: ignore[arg-type]


def test_reference_sets_remove_duplicate_semantic_entries(snapshot: Outcome) -> None:
    artifacts = frozenset((ArtifactRef("a"), ArtifactRef("b"), ArtifactRef("a")))
    evidence = frozenset((EvidenceRef("worker claim"), EvidenceRef("worker claim")))
    represented = replace(snapshot, artifact_refs=artifacts, evidence_refs=evidence)
    assert len(represented.artifact_refs) == 2
    assert len(represented.evidence_refs) == 1
    assert represented.artifact_refs == frozenset((ArtifactRef("b"), ArtifactRef("a")))
    assert represented.state is OutcomeState.PROPOSED
    assert {represented: "found"}[replace(represented)] == "found"


@pytest.mark.parametrize("field", ["prior_outcome_id", "superseded_by_outcome_id"])
@pytest.mark.parametrize(
    "invalid", [VALUE, str(VALUE), RunId(OTHER), TaskId(OTHER), OutcomeId(VALUE)]
)
def test_lineage_is_typed_and_never_self_referential(
    snapshot: Outcome, field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, **{field: invalid})  # type: ignore[arg-type]


def test_superseded_snapshot_requires_a_replacement_identity(snapshot: Outcome) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(snapshot, state=OutcomeState.SUPERSEDED)
    represented = replace(
        snapshot,
        state=OutcomeState.SUPERSEDED,
        superseded_by_outcome_id=OutcomeId(OTHER),
    )
    assert represented.run_id == snapshot.run_id
    assert represented.superseded_by_outcome_id == OutcomeId(OTHER)


def test_candidate_lineage_preserves_history_without_cross_record_guards(
    snapshot: Outcome,
) -> None:
    earlier = replace(snapshot, state=OutcomeState.ACCEPTED)
    later = replace(
        snapshot,
        outcome_id=OutcomeId(OTHER),
        run_id=RunId(OTHER),
        prior_outcome_id=earlier.outcome_id,
    )
    # Explicit descriptive snapshots: no automatic backlink synchronization or lookup.
    superseded = replace(
        earlier,
        state=OutcomeState.SUPERSEDED,
        superseded_by_outcome_id=later.outcome_id,
    )
    assert earlier.state is OutcomeState.ACCEPTED
    assert earlier.superseded_by_outcome_id is None
    assert later.state is OutcomeState.PROPOSED
    assert later.prior_outcome_id == earlier.outcome_id
    assert superseded.run_id == earlier.run_id
    assert superseded.artifact_refs == earlier.artifact_refs
    assert superseded.superseded_by_outcome_id == later.outcome_id
    assert can_outcome_transition(earlier.state, OutcomeState.SUPERSEDED)


def test_horizon_and_expiry_are_not_automatic(snapshot: Outcome) -> None:
    horizon = Timestamp(datetime(2000, 1, 1, 8, tzinfo=timezone(timedelta(hours=8))))
    represented = replace(snapshot, valid_until=horizon)
    assert represented.valid_until is horizon
    assert horizon.value == datetime(2000, 1, 1, tzinfo=UTC)
    assert represented.state is OutcomeState.PROPOSED
    assert replace(snapshot, state=OutcomeState.EXPIRED).valid_until is None


def test_completed_run_does_not_accept_candidates_or_propagate_to_parents(
    snapshot: Outcome,
) -> None:
    objective = Objective(
        ObjectiveId(VALUE),
        ObjectiveState.ACTIVE,
        EntityVersion(9),
        "Bounded result",
        ("Criterion",),
        snapshot.producer,
        CompletionPolicyRef("policy", "revision"),
    )
    task = Task(
        TaskId(VALUE),
        TaskState.IN_PROGRESS,
        EntityVersion(11),
        "Work",
        objective.objective_id,
        objective.completion_policy_ref,
    )
    run = Run(
        RunId(VALUE),
        task.task_id,
        RunState.COMPLETED,
        EntityVersion(13),
        ExecutionProfileRef("profile", "revision"),
    )
    assert not hasattr(run, "outcomes")  # Zero candidates need no child collection.
    candidates = [
        replace(
            snapshot,
            outcome_id=OutcomeId(UUID(int=index + 1)),
            run_id=run.run_id,
            state=state,
        )
        for index, state in enumerate(
            (OutcomeState.PROPOSED, OutcomeState.VALIDATING, OutcomeState.REJECTED)
        )
    ]
    assert len({candidate.outcome_id for candidate in candidates}) == 3
    assert all(candidate.run_id == run.run_id for candidate in candidates)
    assert [candidate.state for candidate in candidates] == [
        OutcomeState.PROPOSED,
        OutcomeState.VALIDATING,
        OutcomeState.REJECTED,
    ]
    assert can_outcome_transition(candidates[1].state, OutcomeState.ACCEPTED)
    accepted_snapshot = replace(candidates[1], state=OutcomeState.ACCEPTED)
    assert accepted_snapshot.evidence_refs == frozenset()
    assert candidates[1].state is OutcomeState.VALIDATING
    assert candidates[1].version == accepted_snapshot.version == EntityVersion(17)
    assert run.state is RunState.COMPLETED and run.version.value == 13
    assert task.state is TaskState.IN_PROGRESS and task.version.value == 11
    assert objective.state is ObjectiveState.ACTIVE and objective.version.value == 9
    for name in (
        "validate",
        "accept",
        "reject",
        "supersede",
        "expire",
        "transition",
        "with_state",
        "verification_passed",
        "evaluation_passed",
        "policy_passed",
        "human_approved",
        "trusted",
        "task_id",
        "primary_objective_id",
        "evaluation",
        "events",
    ):
        assert not hasattr(accepted_snapshot, name)
