"""M7C4D canonical Outcome expiry semantic guards."""

from dataclasses import fields
from datetime import UTC, datetime, timedelta
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
    InvalidDomainValue,
    InvariantViolation,
    Outcome,
    OutcomeExpiryDecision,
    OutcomeExpirySemantics,
    OutcomeId,
    OutcomeSemanticDecisionRef,
    OutcomeSemanticDecisionStatus,
    OutcomeSemanticGuard,
    OutcomeStaleBasis,
    OutcomeState,
    RunId,
    Timestamp,
    TransitionAuthorityDecision,
    TransitionAuthorityStatus,
    TransitionContext,
    TransitionReason,
    TransitionRequest,
    UnauthorizedTransition,
    can_outcome_transition,
    transition_entity,
)
from symphony_k.domain.transition_engine import LifecycleEntity, LifecycleState

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
VERSION = EntityVersion(17)
CORRELATION = CorrelationId(VALUE)
NOW = Timestamp(datetime(2026, 9, 11, tzinfo=UTC))


def identity(actor_type: ActorType, value: UUID = VALUE) -> ActorIdentity:
    return ActorIdentity(ActorId(value), actor_type)


def outcome(
    state: OutcomeState,
    *,
    valid_until: Timestamp | None = None,
) -> Outcome:
    return Outcome(
        OutcomeId(VALUE),
        RunId(VALUE),
        state,
        VERSION,
        identity(ActorType.WORKER),
        frozenset({ArtifactRef("candidate")}),
        frozenset({EvidenceRef("producer-evidence")}),
        valid_until,
    )


def expiry_semantics(
    current: Outcome,
    *,
    basis: OutcomeStaleBasis = OutcomeStaleBasis.ASSUMPTIONS_STALE,
    status: OutcomeSemanticDecisionStatus = OutcomeSemanticDecisionStatus.PASSED,
    decided_by: ActorIdentity | None = None,
    evidence_refs: frozenset[EvidenceRef] | None = None,
    outcome_id: OutcomeId | None = None,
    version: EntityVersion | None = None,
    correlation: CorrelationId = CORRELATION,
) -> OutcomeExpirySemantics:
    return OutcomeExpirySemantics(
        OutcomeExpiryDecision(
            OutcomeSemanticDecisionRef("stale-input-decision"),
            status,
            decided_by or identity(ActorType.POLICY_ENGINE, OTHER),
            evidence_refs
            if evidence_refs is not None
            else frozenset({EvidenceRef("stale")}),
            outcome_id or current.outcome_id,
            version or current.version,
            basis,
            correlation,
        )
    )


def request(
    current: Outcome,
    *,
    timestamp: Timestamp = NOW,
    actor: ActorIdentity | None = None,
) -> TransitionRequest[OutcomeState]:
    return TransitionRequest(
        EventId(VALUE),
        OutcomeState.EXPIRED,
        actor or identity(ActorType.SCHEDULER),
        TransitionReason("Recorded stale input makes this candidate unusable"),
        current.version,
        timestamp,
        CORRELATION,
    )


def context(
    current: Outcome,
    transition_request: TransitionRequest[OutcomeState],
    semantics: OutcomeExpirySemantics,
    *,
    authority: TransitionAuthorityDecision | None = None,
) -> TransitionContext:
    return TransitionContext(
        (PassingGuard(),),
        authority
        or TransitionAuthorityDecision(
            transition_request.actor,
            DomainEntityType.OUTCOME,
            current.outcome_id,
            current.version,
            current.state,
            OutcomeState.EXPIRED,
            TransitionAuthorityStatus.AUTHORIZED,
            transition_request.correlation_id,
        ),
        outcome_semantic_guard=OutcomeSemanticGuard(
            current.outcome_id,
            current.version,
            current.state,
            OutcomeState.EXPIRED,
            transition_request.correlation_id,
            semantics,
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
    "source",
    [
        OutcomeState.PROPOSED,
        OutcomeState.VALIDATING,
        OutcomeState.ACCEPTED,
        OutcomeState.REJECTED,
    ],
)
@pytest.mark.parametrize("basis", list(OutcomeStaleBasis))
def test_all_expiry_edges_and_stale_bases_are_canonical(
    source: OutcomeState, basis: OutcomeStaleBasis
) -> None:
    current = outcome(
        source,
        valid_until=NOW
        if basis is OutcomeStaleBasis.VALIDITY_HORIZON_ELAPSED
        else None,
    )
    transition_request = request(current)
    result = transition_entity(
        current,
        transition_request,
        context(current, transition_request, expiry_semantics(current, basis=basis)),
    )
    assert result.entity.state is OutcomeState.EXPIRED
    assert result.entity.version == current.version.next()


def test_expiry_exact_binds_outcome_version_and_correlation() -> None:
    current = outcome(OutcomeState.ACCEPTED)
    transition_request = request(current)
    for semantic in (
        expiry_semantics(current, outcome_id=OutcomeId(OTHER)),
        expiry_semantics(current, version=EntityVersion(18)),
        expiry_semantics(current, correlation=CorrelationId(OTHER)),
    ):
        with pytest.raises(InvariantViolation, match="exact request snapshot"):
            transition_entity(
                current,
                transition_request,
                context(current, transition_request, semantic),
            )
        assert (current.state, current.version) == (OutcomeState.ACCEPTED, VERSION)


def test_horizon_expiry_uses_request_timestamp_at_boundary_without_a_clock() -> None:
    current = outcome(OutcomeState.PROPOSED, valid_until=NOW)
    semantic = expiry_semantics(
        current, basis=OutcomeStaleBasis.VALIDITY_HORIZON_ELAPSED
    )
    at_boundary = request(current, timestamp=NOW)
    assert (
        transition_entity(
            current, at_boundary, context(current, at_boundary, semantic)
        ).entity.state
        is OutcomeState.EXPIRED
    )
    before = request(
        current, timestamp=Timestamp(NOW.value - timedelta(microseconds=1))
    )
    with pytest.raises(InvariantViolation, match="has not elapsed"):
        transition_entity(current, before, context(current, before, semantic))
    assert "datetime" not in vars(
        __import__("symphony_k.domain.outcome_semantics", fromlist=["*"])
    )


def test_horizon_requires_valid_until_but_other_stale_basis_does_not() -> None:
    current = outcome(OutcomeState.VALIDATING)
    transition_request = request(current)
    with pytest.raises(InvariantViolation, match="no validity horizon"):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                expiry_semantics(
                    current, basis=OutcomeStaleBasis.VALIDITY_HORIZON_ELAPSED
                ),
            ),
        )
    assert (
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, expiry_semantics(current)),
        ).entity.state
        is OutcomeState.EXPIRED
    )


@pytest.mark.parametrize(
    "semantic",
    [
        lambda current: expiry_semantics(
            current, status=OutcomeSemanticDecisionStatus.UNRESOLVED
        ),
        lambda current: expiry_semantics(
            current, decided_by=identity(ActorType.WORKER)
        ),
        lambda current: expiry_semantics(
            current, decided_by=identity(ActorType.EVALUATOR)
        ),
    ],
)
def test_expiry_rejects_nonpassed_or_non_authoritative_decisions(
    semantic: object,
) -> None:
    current = outcome(OutcomeState.REJECTED)
    transition_request = request(current)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, semantic(current)),  # type: ignore[operator]
        )
    assert (current.state, current.version) == (OutcomeState.REJECTED, VERSION)


def test_expiry_requires_evidence_and_preserves_all_history() -> None:
    current = outcome(OutcomeState.ACCEPTED, valid_until=NOW)
    with pytest.raises(InvalidDomainValue, match="evidence"):
        expiry_semantics(current, evidence_refs=frozenset())
    transition_request = request(current)
    before = tuple(getattr(current, field.name) for field in fields(current))
    result = transition_entity(
        current,
        transition_request,
        context(current, transition_request, expiry_semantics(current)),
    )
    assert tuple(getattr(current, field.name) for field in fields(current)) == before
    for field in fields(current):
        if field.name not in {"state", "version"}:
            assert getattr(result.entity, field.name) == getattr(current, field.name)


def test_m7b_authority_remains_mandatory_for_expiry() -> None:
    current = outcome(OutcomeState.PROPOSED)
    transition_request = request(current, actor=identity(ActorType.WORKER))
    with pytest.raises(UnauthorizedTransition):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                expiry_semantics(current),
                authority=TransitionAuthorityDecision(
                    transition_request.actor,
                    DomainEntityType.OUTCOME,
                    current.outcome_id,
                    current.version,
                    current.state,
                    OutcomeState.EXPIRED,
                    TransitionAuthorityStatus.AUTHORIZED,
                    CORRELATION,
                ),
            ),
        )
    authorized_request = request(current)
    with pytest.raises(UnauthorizedTransition):
        transition_entity(
            current,
            authorized_request,
            TransitionContext(
                (PassingGuard(),),
                outcome_semantic_guard=OutcomeSemanticGuard(
                    current.outcome_id,
                    current.version,
                    current.state,
                    OutcomeState.EXPIRED,
                    CORRELATION,
                    expiry_semantics(current),
                ),
            ),
        )
    assert (current.state, current.version) == (OutcomeState.PROPOSED, VERSION)


def test_outcome_topology_remains_all_eleven_existing_edges() -> None:
    assert {
        (source, target)
        for source in OutcomeState
        for target in OutcomeState
        if can_outcome_transition(source, target)
    } == {
        (OutcomeState.PROPOSED, OutcomeState.VALIDATING),
        (OutcomeState.VALIDATING, OutcomeState.ACCEPTED),
        (OutcomeState.VALIDATING, OutcomeState.REJECTED),
        *(
            (state, OutcomeState.SUPERSEDED)
            for state in (
                OutcomeState.PROPOSED,
                OutcomeState.VALIDATING,
                OutcomeState.ACCEPTED,
                OutcomeState.REJECTED,
            )
        ),
        *(
            (state, OutcomeState.EXPIRED)
            for state in (
                OutcomeState.PROPOSED,
                OutcomeState.VALIDATING,
                OutcomeState.ACCEPTED,
                OutcomeState.REJECTED,
            )
        ),
    }
