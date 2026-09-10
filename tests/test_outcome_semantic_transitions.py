"""M7C4A canonical semantics for starting independent Outcome validation."""

from dataclasses import dataclass, fields, replace
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
    EffectId,
    EntityVersion,
    Evaluation,
    EvaluationId,
    EvaluationMethodRef,
    EvaluationState,
    EvaluationTargetRef,
    EventId,
    EvidenceRef,
    InvariantViolation,
    Outcome,
    OutcomeEvaluationRequestObservation,
    OutcomeEvaluationRequestRef,
    OutcomeId,
    OutcomeSemanticDecisionRef,
    OutcomeSemanticDecisionStatus,
    OutcomeSemanticGuard,
    OutcomeState,
    OutcomeValidationArtifactScope,
    OutcomeValidationPolicyDecision,
    OutcomeValidationPolicyRef,
    OutcomeValidationStartSemantics,
    RunId,
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
VERSION = EntityVersion(17)
EVALUATION_VERSION = EntityVersion(29)
CORRELATION_ID = CorrelationId(VALUE)


def identity(actor_type: ActorType, value: UUID = VALUE) -> ActorIdentity:
    return ActorIdentity(ActorId(value), actor_type)


def outcome() -> Outcome:
    return Outcome(
        OutcomeId(VALUE),
        RunId(VALUE),
        OutcomeState.PROPOSED,
        VERSION,
        identity(ActorType.WORKER),
        frozenset({ArtifactRef("candidate-a"), ArtifactRef("candidate-b")}),
        frozenset({EvidenceRef("worker-evidence")}),
    )


def evaluation(snapshot: Outcome) -> Evaluation:
    return Evaluation(
        EvaluationId(OTHER),
        EvaluationState.PENDING,
        EVALUATION_VERSION,
        EvaluationTargetRef(snapshot.outcome_id, snapshot.version),
        EvaluationMethodRef("independent-method", "v1"),
    )


def semantics(
    snapshot: Outcome,
    *,
    correlation_id: CorrelationId = CORRELATION_ID,
    policy_actor: ActorIdentity | None = None,
    request_actor: ActorIdentity | None = None,
    verifier: ActorIdentity | None = None,
) -> OutcomeValidationStartSemantics:
    return OutcomeValidationStartSemantics(
        OutcomeValidationArtifactScope(
            snapshot.outcome_id,
            snapshot.version,
            correlation_id,
            snapshot.artifact_refs,
        ),
        OutcomeValidationPolicyDecision(
            OutcomeSemanticDecisionRef("policy-decision"),
            OutcomeSemanticDecisionStatus.PASSED,
            policy_actor or identity(ActorType.POLICY_ENGINE),
            frozenset({EvidenceRef("policy-evidence")}),
            snapshot.outcome_id,
            snapshot.version,
            correlation_id,
            OutcomeValidationPolicyRef("validation-policy", "v3"),
        ),
        OutcomeEvaluationRequestObservation(
            OutcomeEvaluationRequestRef(
                "evaluation-request", EvaluationId(OTHER), EVALUATION_VERSION
            ),
            EvaluationId(OTHER),
            EVALUATION_VERSION,
            EvaluationState.PENDING,
            EvaluationTargetRef(snapshot.outcome_id, snapshot.version),
            EvaluationMethodRef("independent-method", "v1"),
            request_actor or identity(ActorType.SCHEDULER),
            verifier,
            snapshot.outcome_id,
            snapshot.version,
            correlation_id,
        ),
    )


def guard(
    snapshot: Outcome,
    *,
    outcome_id: OutcomeId | None = None,
    observed_version: EntityVersion | None = None,
    prior_state: OutcomeState = OutcomeState.PROPOSED,
    target_state: OutcomeState = OutcomeState.VALIDATING,
    correlation_id: CorrelationId = CORRELATION_ID,
    semantic_input: OutcomeValidationStartSemantics | None = None,
) -> OutcomeSemanticGuard:
    return OutcomeSemanticGuard(
        outcome_id or snapshot.outcome_id,
        observed_version or snapshot.version,
        prior_state,
        target_state,
        correlation_id,
        semantic_input or semantics(snapshot, correlation_id=correlation_id),
    )


def request(
    snapshot: Outcome,
    *,
    actor: ActorIdentity | None = None,
    correlation_id: CorrelationId = CORRELATION_ID,
) -> TransitionRequest[OutcomeState]:
    return TransitionRequest(
        EventId(VALUE),
        OutcomeState.VALIDATING,
        actor or identity(ActorType.SCHEDULER),
        TransitionReason("Start independent validation"),
        snapshot.version,
        Timestamp(datetime(2026, 9, 10, tzinfo=UTC)),
        correlation_id,
    )


def context(
    snapshot: Outcome,
    transition_request: TransitionRequest[OutcomeState],
    semantic_guard: OutcomeSemanticGuard | None = None,
    *,
    authority_status: TransitionAuthorityStatus = TransitionAuthorityStatus.AUTHORIZED,
    with_outcome_guard: bool = True,
) -> TransitionContext:
    return TransitionContext(
        (PassingGuard(),),
        TransitionAuthorityDecision(
            transition_request.actor,
            DomainEntityType.OUTCOME,
            snapshot.outcome_id,
            snapshot.version,
            snapshot.state,
            transition_request.target_state,
            authority_status,
            transition_request.correlation_id,
        ),
        outcome_semantic_guard=(
            semantic_guard
            if semantic_guard is not None
            else guard(snapshot)
            if with_outcome_guard
            else None
        ),
    )


@dataclass(frozen=True, slots=True)
class PassingGuard:
    def validate(
        self,
        entity: LifecycleEntity,
        transition_request: TransitionRequest[LifecycleState],
    ) -> None:
        assert entity.version == transition_request.expected_version


def test_validation_start_succeeds_only_with_complete_canonical_semantics() -> None:
    snapshot = outcome()
    observed_evaluation = evaluation(snapshot)
    before = tuple(getattr(snapshot, field.name) for field in fields(snapshot))
    result = transition_entity(
        snapshot, request(snapshot), context(snapshot, request(snapshot))
    )

    assert result.entity.state is OutcomeState.VALIDATING
    assert result.entity.version == EntityVersion(18)
    assert result.event.metadata.prior_state is OutcomeState.PROPOSED
    assert result.event.metadata.new_state is OutcomeState.VALIDATING
    assert observed_evaluation.state is EvaluationState.PENDING
    assert observed_evaluation.version == EVALUATION_VERSION
    assert observed_evaluation.result is None
    assert tuple(getattr(snapshot, field.name) for field in fields(snapshot)) == before
    for field in fields(snapshot):
        if field.name not in {"state", "version"}:
            assert getattr(result.entity, field.name) == getattr(snapshot, field.name)


@pytest.mark.parametrize(
    ("outcome_id", "observed_version", "prior_state", "target_state", "correlation"),
    [
        (
            OutcomeId(OTHER),
            VERSION,
            OutcomeState.PROPOSED,
            OutcomeState.VALIDATING,
            CORRELATION_ID,
        ),
        (
            OutcomeId(VALUE),
            EntityVersion(16),
            OutcomeState.PROPOSED,
            OutcomeState.VALIDATING,
            CORRELATION_ID,
        ),
        (
            OutcomeId(VALUE),
            VERSION,
            OutcomeState.PROPOSED,
            OutcomeState.VALIDATING,
            CorrelationId(OTHER),
        ),
    ],
)
def test_guard_exact_snapshot_binding_rejects_laundering(
    outcome_id: OutcomeId,
    observed_version: EntityVersion,
    prior_state: OutcomeState,
    target_state: OutcomeState,
    correlation: CorrelationId,
) -> None:
    snapshot = outcome()
    transition_request = request(snapshot)
    forged = guard(
        snapshot,
        outcome_id=outcome_id,
        observed_version=observed_version,
        prior_state=prior_state,
        target_state=target_state,
        correlation_id=correlation,
        semantic_input=semantics(snapshot, correlation_id=correlation),
    )
    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot, transition_request, context(snapshot, transition_request, forged)
        )
    assert (snapshot.state, snapshot.version) == (OutcomeState.PROPOSED, VERSION)


def test_guard_source_binding_rejects_a_snapshot_in_another_source_state() -> None:
    snapshot = replace(outcome(), state=OutcomeState.VALIDATING)
    with pytest.raises(InvariantViolation, match="exact request snapshot"):
        guard(outcome()).validate(snapshot, OutcomeState.VALIDATING, CORRELATION_ID)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: replace(value, artifact_refs=frozenset({ArtifactRef("foreign")})),
        lambda value: replace(
            value,
            outcome_id=OutcomeId(OTHER),
        ),
        lambda value: replace(value, observed_entity_version=EntityVersion(16)),
        lambda value: replace(value, correlation_id=CorrelationId(OTHER)),
    ],
)
def test_artifact_scope_must_be_current_exact_and_non_foreign(mutation: object) -> None:
    snapshot = outcome()
    input_value = semantics(snapshot)
    changed_scope = mutation(input_value.artifact_scope)  # type: ignore[operator]
    forged = guard(
        snapshot, semantic_input=replace(input_value, artifact_scope=changed_scope)
    )
    transition_request = request(snapshot)
    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot, transition_request, context(snapshot, transition_request, forged)
        )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: replace(value, status=OutcomeSemanticDecisionStatus.REJECTED),
        lambda value: replace(value, status=OutcomeSemanticDecisionStatus.UNRESOLVED),
        lambda value: replace(value, outcome_id=OutcomeId(OTHER)),
        lambda value: replace(value, observed_entity_version=EntityVersion(16)),
        lambda value: replace(value, correlation_id=CorrelationId(OTHER)),
        lambda value: replace(value, decided_by=identity(ActorType.WORKER)),
    ],
)
def test_validation_policy_requires_exact_non_worker_applicable_provenance(
    mutation: object,
) -> None:
    snapshot = outcome()
    input_value = semantics(snapshot)
    changed_policy = mutation(input_value.validation_policy)  # type: ignore[operator]
    forged = guard(
        snapshot, semantic_input=replace(input_value, validation_policy=changed_policy)
    )
    transition_request = request(snapshot)
    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot, transition_request, context(snapshot, transition_request, forged)
        )


@pytest.mark.parametrize(
    "target",
    [
        EvaluationTargetRef(OutcomeId(OTHER), VERSION),
        EvaluationTargetRef(OutcomeId(VALUE), EntityVersion(16)),
        EvaluationTargetRef(RunId(VALUE), VERSION),
        EvaluationTargetRef(EffectId(VALUE), VERSION),
        EvaluationTargetRef(EvidenceRef("arbitrary-evidence")),
    ],
)
def test_evaluation_must_target_the_exact_current_outcome_snapshot(
    target: EvaluationTargetRef,
) -> None:
    snapshot = outcome()
    input_value = semantics(snapshot)
    observation = replace(input_value.evaluation_request, target=target)
    forged = guard(
        snapshot, semantic_input=replace(input_value, evaluation_request=observation)
    )
    transition_request = request(snapshot)
    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot, transition_request, context(snapshot, transition_request, forged)
        )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: replace(value, observed_state=EvaluationState.RUNNING),
        lambda value: replace(value, outcome_id=OutcomeId(OTHER)),
        lambda value: replace(value, observed_outcome_version=EntityVersion(16)),
        lambda value: replace(value, correlation_id=CorrelationId(OTHER)),
        lambda value: replace(value, requested_by=identity(ActorType.WORKER)),
        lambda value: replace(value, verifier=identity(ActorType.WORKER)),
    ],
)
def test_evaluation_request_must_remain_independent_current_and_pending(
    mutation: object,
) -> None:
    snapshot = outcome()
    input_value = semantics(snapshot)
    observation = mutation(input_value.evaluation_request)  # type: ignore[operator]
    forged = guard(
        snapshot, semantic_input=replace(input_value, evaluation_request=observation)
    )
    transition_request = request(snapshot)
    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot, transition_request, context(snapshot, transition_request, forged)
        )


def test_evaluation_version_is_distinct_from_outcome_version() -> None:
    snapshot = outcome()
    semantic_input = semantics(snapshot)
    assert (
        semantic_input.evaluation_request.observed_evaluation_version
        == EVALUATION_VERSION
    )
    assert (
        semantic_input.evaluation_request.observed_evaluation_version
        != snapshot.version
    )
    result = transition_entity(
        snapshot, request(snapshot), context(snapshot, request(snapshot))
    )
    assert result.entity.version == EntityVersion(18)


@pytest.mark.parametrize(
    "attribute,value",
    [
        ("evaluation_id", EvaluationId(VALUE)),
        ("observed_evaluation_version", EntityVersion(30)),
    ],
)
def test_evaluation_request_provenance_rejects_snapshot_substitution(
    attribute: str, value: EvaluationId | EntityVersion
) -> None:
    snapshot = outcome()
    semantic_input = semantics(snapshot)
    observation = semantic_input.evaluation_request
    object.__setattr__(observation, attribute, value)
    transition_request = request(snapshot)

    with pytest.raises(InvariantViolation, match="provenance does not match"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard(snapshot, semantic_input=semantic_input),
            ),
        )


def test_outcome_version_cannot_substitute_for_evaluation_version() -> None:
    snapshot = outcome()
    semantic_input = semantics(snapshot)
    observation = semantic_input.evaluation_request
    object.__setattr__(observation, "observed_evaluation_version", snapshot.version)
    transition_request = request(snapshot)

    with pytest.raises(InvariantViolation, match="provenance does not match"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard(snapshot, semantic_input=semantic_input),
            ),
        )


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (OutcomeState.VALIDATING, OutcomeState.ACCEPTED),
        (OutcomeState.VALIDATING, OutcomeState.REJECTED),
        (OutcomeState.PROPOSED, OutcomeState.SUPERSEDED),
        (OutcomeState.VALIDATING, OutcomeState.SUPERSEDED),
        (OutcomeState.ACCEPTED, OutcomeState.SUPERSEDED),
        (OutcomeState.REJECTED, OutcomeState.SUPERSEDED),
        (OutcomeState.PROPOSED, OutcomeState.EXPIRED),
        (OutcomeState.VALIDATING, OutcomeState.EXPIRED),
        (OutcomeState.ACCEPTED, OutcomeState.EXPIRED),
        (OutcomeState.REJECTED, OutcomeState.EXPIRED),
    ],
)
def test_other_outcome_edges_remain_semantically_deny_by_default(
    source: OutcomeState, target: OutcomeState
) -> None:
    snapshot = replace(outcome(), state=source)
    transition_request = TransitionRequest(
        EventId(VALUE),
        target,
        identity(ActorType.SCHEDULER),
        TransitionReason("Future Outcome semantic edge"),
        snapshot.version,
        Timestamp(datetime(2026, 9, 10, tzinfo=UTC)),
        CORRELATION_ID,
    )
    with pytest.raises(InvariantViolation, match="Canonical Outcome semantic guard"):
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, with_outcome_guard=False),
        )


def test_generic_guard_cannot_replace_canonical_outcome_semantics() -> None:
    snapshot = outcome()
    transition_request = request(snapshot)
    authority = TransitionAuthorityDecision(
        transition_request.actor,
        DomainEntityType.OUTCOME,
        snapshot.outcome_id,
        snapshot.version,
        snapshot.state,
        transition_request.target_state,
        TransitionAuthorityStatus.AUTHORIZED,
        transition_request.correlation_id,
    )
    with pytest.raises(InvariantViolation, match="Canonical Outcome semantic guard"):
        transition_entity(
            snapshot,
            transition_request,
            TransitionContext((PassingGuard(),), authority),
        )


@pytest.mark.parametrize(
    ("actor_type", "authority_status", "error"),
    [
        (
            ActorType.WORKER,
            TransitionAuthorityStatus.AUTHORIZED,
            UnauthorizedTransition,
        ),
        (
            ActorType.EVALUATOR,
            TransitionAuthorityStatus.AUTHORIZED,
            UnauthorizedTransition,
        ),
        (ActorType.SCHEDULER, TransitionAuthorityStatus.DENIED, UnauthorizedTransition),
    ],
)
def test_m7b1_and_m7b2_remain_required(
    actor_type: ActorType,
    authority_status: TransitionAuthorityStatus,
    error: type[Exception],
) -> None:
    snapshot = outcome()
    transition_request = request(snapshot, actor=identity(actor_type))
    with pytest.raises(error):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                authority_status=authority_status,
            ),
        )
