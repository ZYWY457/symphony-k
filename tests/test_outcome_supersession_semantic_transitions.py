"""M7C4C canonical Outcome supersession semantic guards."""

from dataclasses import fields, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArtifactRef,
    CorrelationId,
    DomainEntityType,
    EntityVersion,
    EventId,
    EvidenceRef,
    ExecutionProfileRef,
    InvalidDomainValue,
    InvariantViolation,
    Outcome,
    OutcomeAcceptanceScopeCompatibilityDecision,
    OutcomeAcceptanceScopeRef,
    OutcomeId,
    OutcomeOriginatingRunObservation,
    OutcomePriorLineageObservation,
    OutcomeReplacementObservation,
    OutcomeSemanticDecisionRef,
    OutcomeSemanticDecisionStatus,
    OutcomeSemanticGuard,
    OutcomeState,
    OutcomeSupersessionSemantics,
    Run,
    RunId,
    RunState,
    TaskId,
    Timestamp,
    TransitionAuthorityDecision,
    TransitionAuthorityStatus,
    TransitionContext,
    TransitionReason,
    TransitionRequest,
    UnauthorizedTransition,
    transition_entity,
)
from symphony_k.domain.transition_engine import LifecycleEntity, LifecycleState

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
THIRD = UUID("aaaaaaaa-1234-4234-8234-123456789abc")
CORRELATION = CorrelationId(VALUE)


def identity(actor_type: ActorType, value: UUID = VALUE) -> ActorIdentity:
    return ActorIdentity(ActorId(value), actor_type)


def source(state: OutcomeState = OutcomeState.PROPOSED) -> Outcome:
    return Outcome(
        OutcomeId(VALUE),
        RunId(VALUE),
        state,
        EntityVersion(10),
        identity(ActorType.WORKER),
        frozenset({ArtifactRef("source-artifact")}),
        frozenset({EvidenceRef("source-evidence")}),
    )


def replacement(state: OutcomeState = OutcomeState.PROPOSED) -> Outcome:
    return Outcome(
        OutcomeId(OTHER),
        RunId(OTHER),
        state,
        EntityVersion(3),  # EntityVersion values across candidates are not chronology.
        identity(ActorType.WORKER, OTHER),
        frozenset({ArtifactRef("replacement-artifact")}),
        frozenset({EvidenceRef("replacement-evidence")}),
        prior_outcome_id=OutcomeId(VALUE),
    )


def semantics(
    current: Outcome,
    candidate: Outcome,
    *,
    task_id: TaskId | None = None,
    lineage: tuple[OutcomePriorLineageObservation, ...] | None = None,
) -> OutcomeSupersessionSemantics:
    task_id = task_id or TaskId(VALUE)
    return OutcomeSupersessionSemantics(
        OutcomeReplacementObservation(
            candidate.outcome_id,
            candidate.version,
            candidate.state,
            candidate.run_id,
            candidate.prior_outcome_id,
            candidate.superseded_by_outcome_id,
            CORRELATION,
        ),
        OutcomeOriginatingRunObservation(
            current.outcome_id,
            current.version,
            current.run_id,
            EntityVersion(20),
            task_id,
        ),
        OutcomeOriginatingRunObservation(
            candidate.outcome_id,
            candidate.version,
            candidate.run_id,
            EntityVersion(21),
            task_id,
        ),
        OutcomeAcceptanceScopeCompatibilityDecision(
            OutcomeSemanticDecisionRef("scope-decision"),
            OutcomeSemanticDecisionStatus.PASSED,
            identity(ActorType.POLICY_ENGINE, THIRD),
            frozenset({EvidenceRef("scope-evidence")}),
            current.outcome_id,
            current.version,
            candidate.outcome_id,
            candidate.version,
            task_id,
            OutcomeAcceptanceScopeRef("acceptance-scope", "v1"),
            CORRELATION,
        ),
        lineage
        or (
            OutcomePriorLineageObservation(
                current.outcome_id, current.version, current.prior_outcome_id
            ),
        ),
    )


def request(
    current: Outcome, actor: ActorIdentity | None = None
) -> TransitionRequest[OutcomeState]:
    return TransitionRequest(
        EventId(VALUE),
        OutcomeState.SUPERSEDED,
        actor or identity(ActorType.SCHEDULER),
        TransitionReason("Replace a candidate with its direct successor"),
        current.version,
        Timestamp(datetime(2026, 9, 10, tzinfo=UTC)),
        CORRELATION,
    )


def context(
    current: Outcome,
    transition_request: TransitionRequest[OutcomeState],
    semantic_input: OutcomeSupersessionSemantics,
) -> TransitionContext:
    return TransitionContext(
        (PassingGuard(),),
        TransitionAuthorityDecision(
            transition_request.actor,
            DomainEntityType.OUTCOME,
            current.outcome_id,
            current.version,
            current.state,
            OutcomeState.SUPERSEDED,
            TransitionAuthorityStatus.AUTHORIZED,
            CORRELATION,
        ),
        outcome_semantic_guard=OutcomeSemanticGuard(
            current.outcome_id,
            current.version,
            current.state,
            OutcomeState.SUPERSEDED,
            CORRELATION,
            semantic_input,
        ),
    )


class PassingGuard:
    def validate(
        self,
        entity: LifecycleEntity,
        transition_request: TransitionRequest[LifecycleState],
    ) -> None:
        assert entity.version == transition_request.expected_version


@pytest.mark.parametrize(
    ("source_state", "replacement_state"),
    [
        (OutcomeState.PROPOSED, OutcomeState.PROPOSED),
        (OutcomeState.VALIDATING, OutcomeState.VALIDATING),
        (OutcomeState.REJECTED, OutcomeState.REJECTED),
        (OutcomeState.ACCEPTED, OutcomeState.ACCEPTED),
    ],
)
def test_valid_supersession_projects_only_source(
    source_state: OutcomeState, replacement_state: OutcomeState
) -> None:
    current = source(source_state)
    candidate = replacement(replacement_state)
    semantic_input = semantics(current, candidate)
    transition_request = request(current)
    source_before = tuple(getattr(current, field.name) for field in fields(current))
    replacement_before = tuple(
        getattr(candidate, field.name) for field in fields(candidate)
    )

    result = transition_entity(
        current,
        transition_request,
        context(current, transition_request, semantic_input),
    )

    assert result.entity.state is OutcomeState.SUPERSEDED
    assert result.entity.version == current.version.next()
    assert result.entity.superseded_by_outcome_id == candidate.outcome_id
    assert result.event.metadata.prior_state is source_state
    assert result.event.metadata.annotations == frozenset(
        {("replacement_outcome_id", str(candidate.outcome_id.value))}
    )
    assert (
        tuple(getattr(current, field.name) for field in fields(current))
        == source_before
    )
    assert (
        tuple(getattr(candidate, field.name) for field in fields(candidate))
        == replacement_before
    )
    for field in fields(current):
        if field.name not in {"state", "version", "superseded_by_outcome_id"}:
            assert getattr(result.entity, field.name) == getattr(current, field.name)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda current, candidate, value: replace(
            value, replacement=replace(value.replacement, outcome_id=current.outcome_id)
        ),
        lambda current, candidate, value: replace(
            value,
            replacement=replace(value.replacement, prior_outcome_id=OutcomeId(THIRD)),
        ),
        lambda current, candidate, value: replace(
            value,
            replacement=replace(value.replacement, observed_state=OutcomeState.EXPIRED),
        ),
        lambda current, candidate, value: replace(
            value,
            replacement=replace(value.replacement, correlation_id=CorrelationId(OTHER)),
        ),
        lambda current, candidate, value: replace(
            value,
            source_run=replace(value.source_run, originating_run_id=RunId(THIRD)),
        ),
        lambda current, candidate, value: replace(
            value,
            replacement_run=replace(
                value.replacement_run, observed_outcome_version=EntityVersion(4)
            ),
        ),
        lambda current, candidate, value: replace(
            value, replacement_run=replace(value.replacement_run, task_id=TaskId(THIRD))
        ),
        lambda current, candidate, value: replace(
            value,
            acceptance_scope_decision=replace(
                value.acceptance_scope_decision,
                source_outcome_version=EntityVersion(11),
            ),
        ),
        lambda current, candidate, value: replace(
            value,
            acceptance_scope_decision=replace(
                value.acceptance_scope_decision,
                decided_by=identity(ActorType.WORKER, THIRD),
            ),
        ),
    ],
)
def test_supersession_rejects_substituted_cross_entity_provenance(
    mutate: object,
) -> None:
    current = source()
    candidate = replacement()
    forged = mutate(current, candidate, semantics(current, candidate))  # type: ignore[operator]
    transition_request = request(current)

    with pytest.raises(InvariantViolation):
        transition_entity(
            current, transition_request, context(current, transition_request, forged)
        )
    assert current.state is OutcomeState.PROPOSED
    assert current.superseded_by_outcome_id is None


def test_accepted_source_requires_an_already_accepted_replacement() -> None:
    current = source(OutcomeState.ACCEPTED)
    candidate = replacement(OutcomeState.PROPOSED)
    transition_request = request(current)

    with pytest.raises(InvariantViolation, match="already-ACCEPTED"):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, semantics(current, candidate)),
        )


@pytest.mark.parametrize(
    "lineage",
    [
        (
            OutcomePriorLineageObservation(
                OutcomeId(VALUE), EntityVersion(10), OutcomeId(THIRD)
            ),
            OutcomePriorLineageObservation(OutcomeId(OTHER), EntityVersion(9), None),
        ),
        (
            OutcomePriorLineageObservation(
                OutcomeId(VALUE), EntityVersion(10), OutcomeId(THIRD)
            ),
            OutcomePriorLineageObservation(
                OutcomeId(THIRD), EntityVersion(9), OutcomeId(THIRD)
            ),
        ),
        (
            OutcomePriorLineageObservation(
                OutcomeId(VALUE), EntityVersion(10), OutcomeId(THIRD)
            ),
        ),
    ],
)
def test_incomplete_discontinuous_or_cyclic_lineage_rejects(
    lineage: tuple[OutcomePriorLineageObservation, ...],
) -> None:
    current = replace(source(), prior_outcome_id=OutcomeId(THIRD))
    candidate = replacement()
    transition_request = request(current)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                semantics(current, candidate, lineage=lineage),
            ),
        )


def test_replacement_already_in_source_ancestry_rejects() -> None:
    current = replace(source(), prior_outcome_id=OutcomeId(OTHER))
    candidate = replacement()
    lineage = (
        OutcomePriorLineageObservation(
            current.outcome_id, current.version, OutcomeId(OTHER)
        ),
        OutcomePriorLineageObservation(OutcomeId(OTHER), EntityVersion(9), None),
    )
    transition_request = request(current)
    with pytest.raises(InvariantViolation, match="source ancestry"):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                semantics(current, candidate, lineage=lineage),
            ),
        )


def test_existing_source_replacement_link_is_not_overwritten() -> None:
    current = replace(source(), superseded_by_outcome_id=OutcomeId(THIRD))
    candidate = replacement()
    transition_request = request(current)
    with pytest.raises(InvariantViolation, match="already has a replacement"):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, semantics(current, candidate)),
        )


def test_worker_cannot_self_authorize_supersession() -> None:
    current = source()
    candidate = replacement()
    transition_request = request(current, identity(ActorType.WORKER))
    with pytest.raises(UnauthorizedTransition):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, semantics(current, candidate)),
        )


def test_expiry_edges_remain_outside_canonical_semantic_coverage() -> None:
    current = source()
    candidate = replacement()
    with pytest.raises(InvalidDomainValue, match="does not support"):
        OutcomeSemanticGuard(
            current.outcome_id,
            current.version,
            current.state,
            OutcomeState.EXPIRED,
            CORRELATION,
            semantics(current, candidate),
        )


def test_supersession_does_not_propagate_to_runs() -> None:
    current = source()
    candidate = replacement()
    source_run = Run(
        current.run_id,
        TaskId(VALUE),
        RunState.WAITING_FOR_VERIFICATION,
        EntityVersion(20),
        ExecutionProfileRef("source", "v1"),
    )
    replacement_run = Run(
        candidate.run_id,
        TaskId(VALUE),
        RunState.COMPLETED,
        EntityVersion(21),
        ExecutionProfileRef("replacement", "v1"),
    )
    before = (source_run, replacement_run)
    transition_request = request(current)
    transition_entity(
        current,
        transition_request,
        context(current, transition_request, semantics(current, candidate)),
    )
    assert (source_run, replacement_run) == before
