"""Canonical Evaluation start, completion, and invalidation semantics."""

from dataclasses import dataclass, fields
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
    Evaluation,
    EvaluationCompletionDecision,
    EvaluationCompletionSemantics,
    EvaluationConfidence,
    EvaluationConflictClearanceDecision,
    EvaluationId,
    EvaluationInputReadinessDecision,
    EvaluationInvalidationId,
    EvaluationInvalidationRecord,
    EvaluationInvalidationSemantics,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationSemanticDecisionRef,
    EvaluationSemanticDecisionStatus,
    EvaluationSemanticGuard,
    EvaluationStartSemantics,
    EvaluationState,
    EvaluationTargetRef,
    EvaluationVerdict,
    EvaluationVerifierIndependenceDecision,
    EventId,
    EvidenceRef,
    InvalidDomainValue,
    InvariantViolation,
    Outcome,
    OutcomeId,
    OutcomeState,
    RunId,
    Timestamp,
    TransitionAuthorityDecision,
    TransitionAuthorityStatus,
    TransitionContext,
    TransitionReason,
    TransitionRequest,
    UnauthorizedTransition,
    can_evaluation_transition,
    transition_entity,
)
from symphony_k.domain.transition_engine import LifecycleEntity, LifecycleState

VALUE = UUID("12345678-1234-4234-8234-123456789abc")
OTHER = UUID("87654321-4321-4321-8321-cba987654321")
THIRD = UUID("11111111-2222-4333-8444-555555555555")
VERSION = EntityVersion(7)
CORRELATION = CorrelationId(VALUE)
NOW = Timestamp(datetime(2026, 9, 11, tzinfo=UTC))
TARGET = EvaluationTargetRef(OutcomeId(VALUE), EntityVersion(3))
METHOD = EvaluationMethodRef("independent-check", "v1")


def identity(actor_type: ActorType, value: UUID = VALUE) -> ActorIdentity:
    return ActorIdentity(ActorId(value), actor_type)


EVALUATOR = identity(ActorType.EVALUATOR)
OTHER_EVALUATOR = identity(ActorType.EVALUATOR, OTHER)
POLICY = identity(ActorType.POLICY_ENGINE, OTHER)
SCHEDULER = identity(ActorType.SCHEDULER, THIRD)


def result(*, evidence_refs: frozenset[EvidenceRef] | None = None) -> EvaluationResult:
    return EvaluationResult(
        EvaluationVerdict("Requirement not met"),
        EvaluationConfidence("opaque confidence"),
        "Independent reasoning summary.",
        evidence_refs
        if evidence_refs is not None
        else frozenset({EvidenceRef("result")}),
    )


def different_result() -> EvaluationResult:
    return EvaluationResult(
        EvaluationVerdict("Different recorded content"),
        EvaluationConfidence("different confidence"),
        "Different independent reasoning summary.",
        frozenset({EvidenceRef("different-result")}),
    )


def evaluation(
    state: EvaluationState = EvaluationState.PENDING,
    *,
    verifier: ActorIdentity | None = None,
    original_result: EvaluationResult | None = None,
) -> Evaluation:
    if state is EvaluationState.COMPLETED and original_result is None:
        original_result = result()
    return Evaluation(
        EvaluationId(VALUE), state, VERSION, TARGET, METHOD, verifier, original_result
    )


def start_semantics(
    current: Evaluation,
    *,
    verifier: ActorIdentity = EVALUATOR,
    independence_status: EvaluationSemanticDecisionStatus = (
        EvaluationSemanticDecisionStatus.PASSED
    ),
    readiness_status: EvaluationSemanticDecisionStatus = (
        EvaluationSemanticDecisionStatus.PASSED
    ),
    independence_verifier: ActorIdentity | None = None,
    readiness_verifier: ActorIdentity | None = None,
    evaluation_id: EvaluationId | None = None,
    version: EntityVersion | None = None,
    correlation: CorrelationId = CORRELATION,
    independence_by: ActorIdentity = POLICY,
    readiness_by: ActorIdentity = SCHEDULER,
) -> EvaluationStartSemantics:
    return EvaluationStartSemantics(
        verifier,
        EvaluationVerifierIndependenceDecision(
            EvaluationSemanticDecisionRef("independence"),
            independence_status,
            independence_by,
            frozenset({EvidenceRef("independence")}),
            evaluation_id or current.evaluation_id,
            version or current.version,
            current.target,
            current.method,
            independence_verifier or verifier,
            correlation,
        ),
        EvaluationInputReadinessDecision(
            EvaluationSemanticDecisionRef("input-readiness"),
            readiness_status,
            readiness_by,
            frozenset({EvidenceRef("input-readiness")}),
            evaluation_id or current.evaluation_id,
            version or current.version,
            current.target,
            current.method,
            readiness_verifier or verifier,
            correlation,
        ),
    )


def completion_semantics(
    current: Evaluation,
    *,
    original_result: EvaluationResult | None = None,
    completion_status: EvaluationSemanticDecisionStatus = (
        EvaluationSemanticDecisionStatus.PASSED
    ),
    clearance_status: EvaluationSemanticDecisionStatus = (
        EvaluationSemanticDecisionStatus.PASSED
    ),
    completion_by: ActorIdentity | None = None,
    clearance_by: ActorIdentity | None = None,
    completion_result: EvaluationResult | None = None,
    clearance_result: EvaluationResult | None = None,
    correlation: CorrelationId = CORRELATION,
) -> EvaluationCompletionSemantics:
    assert current.verifier is not None
    supplied_result = original_result or result()
    return EvaluationCompletionSemantics(
        supplied_result,
        EvaluationCompletionDecision(
            EvaluationSemanticDecisionRef("completion"),
            completion_status,
            completion_by or current.verifier,
            frozenset({EvidenceRef("completion")}),
            current.evaluation_id,
            current.version,
            current.target,
            current.method,
            current.verifier,
            completion_result or supplied_result,
            correlation,
        ),
        EvaluationConflictClearanceDecision(
            EvaluationSemanticDecisionRef("conflict-clearance"),
            clearance_status,
            clearance_by or current.verifier,
            frozenset({EvidenceRef("clearance")}),
            current.evaluation_id,
            current.version,
            current.target,
            current.method,
            current.verifier,
            clearance_result or supplied_result,
            correlation,
        ),
    )


def invalidation_semantics(
    current: Evaluation,
    *,
    invalidated_by: ActorIdentity = EVALUATOR,
    evaluation_id: EvaluationId | None = None,
    version: EntityVersion | None = None,
    correlation: CorrelationId = CORRELATION,
) -> EvaluationInvalidationSemantics:
    return EvaluationInvalidationSemantics(
        EvaluationInvalidationRecord(
            EvaluationInvalidationId(OTHER),
            evaluation_id or current.evaluation_id,
            version or current.version,
            "Anchored method defect.",
            frozenset({EvidenceRef("invalidation")}),
            invalidated_by,
            NOW,
            correlation,
        )
    )


def request(
    current: Evaluation,
    target: EvaluationState,
    *,
    actor: ActorIdentity | None = None,
    correlation: CorrelationId = CORRELATION,
) -> TransitionRequest[EvaluationState]:
    return TransitionRequest(
        EventId(VALUE),
        target,
        actor or EVALUATOR,
        TransitionReason("Canonical Evaluation transition"),
        current.version,
        NOW,
        correlation,
    )


@dataclass(frozen=True, slots=True)
class PassingGuard:
    def validate(
        self,
        entity: LifecycleEntity,
        transition_request: TransitionRequest[LifecycleState],
    ) -> None:
        assert entity.version == transition_request.expected_version


def context(
    current: Evaluation,
    transition_request: TransitionRequest[EvaluationState],
    semantic_input: (
        EvaluationStartSemantics
        | EvaluationCompletionSemantics
        | EvaluationInvalidationSemantics
    ),
    *,
    authority: TransitionAuthorityDecision | None = None,
) -> TransitionContext:
    return TransitionContext(
        (PassingGuard(),),
        authority
        or TransitionAuthorityDecision(
            transition_request.actor,
            DomainEntityType.EVALUATION,
            current.evaluation_id,
            current.version,
            current.state,
            transition_request.target_state,
            TransitionAuthorityStatus.AUTHORIZED,
            transition_request.correlation_id,
        ),
        evaluation_semantic_guard=EvaluationSemanticGuard(
            current.evaluation_id,
            current.version,
            current.state,
            transition_request.target_state,
            transition_request.correlation_id,
            semantic_input,
        ),
    )


def test_start_succeeds_with_preassigned_exact_independent_verifier() -> None:
    current = evaluation(verifier=EVALUATOR)
    transition_request = request(current, EvaluationState.RUNNING)
    transitioned = transition_entity(
        current,
        transition_request,
        context(current, transition_request, start_semantics(current)),
    ).entity
    assert transitioned.state is EvaluationState.RUNNING
    assert transitioned.version == VERSION.next()
    assert transitioned.verifier == EVALUATOR
    assert transitioned.result is None


def test_start_binds_verifier_only_when_initially_unassigned() -> None:
    current = evaluation()
    transition_request = request(current, EvaluationState.RUNNING)
    transitioned = transition_entity(
        current,
        transition_request,
        context(current, transition_request, start_semantics(current)),
    ).entity
    assert transitioned.verifier == EVALUATOR
    for field in fields(current):
        if field.name not in {"state", "version", "verifier"}:
            assert getattr(transitioned, field.name) == getattr(current, field.name)


@pytest.mark.parametrize(
    "semantic",
    [
        lambda current: start_semantics(current, verifier=OTHER_EVALUATOR),
        lambda current: start_semantics(current, independence_verifier=OTHER_EVALUATOR),
        lambda current: start_semantics(current, readiness_verifier=OTHER_EVALUATOR),
        lambda current: start_semantics(
            current, verifier=identity(ActorType.SCHEDULER)
        ),
    ],
)
def test_start_rejects_verifier_replacement_or_substitution(semantic: object) -> None:
    current = evaluation(verifier=EVALUATOR)
    transition_request = request(current, EvaluationState.RUNNING)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, semantic(current)),  # type: ignore[operator]
        )
    assert (current.state, current.version, current.verifier) == (
        EvaluationState.PENDING,
        VERSION,
        EVALUATOR,
    )


@pytest.mark.parametrize(
    "semantic",
    [
        lambda current: start_semantics(
            current, independence_status=EvaluationSemanticDecisionStatus.UNRESOLVED
        ),
        lambda current: start_semantics(
            current, readiness_status=EvaluationSemanticDecisionStatus.REJECTED
        ),
        lambda current: start_semantics(current, evaluation_id=EvaluationId(OTHER)),
        lambda current: start_semantics(current, version=EntityVersion(8)),
        lambda current: start_semantics(current, correlation=CorrelationId(OTHER)),
        lambda current: start_semantics(
            current, independence_by=identity(ActorType.WORKER)
        ),
        lambda current: start_semantics(
            current, readiness_by=identity(ActorType.EVALUATOR)
        ),
    ],
)
def test_start_requires_exact_passed_provenance(semantic: object) -> None:
    current = evaluation()
    transition_request = request(current, EvaluationState.RUNNING)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, semantic(current)),  # type: ignore[operator]
        )
    assert (current.state, current.version) == (EvaluationState.PENDING, VERSION)


def test_worker_cannot_self_authorize_evaluation_start() -> None:
    current = evaluation()
    worker = identity(ActorType.WORKER)
    transition_request = request(current, EvaluationState.RUNNING, actor=worker)
    with pytest.raises(UnauthorizedTransition):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, start_semantics(current)),
        )


def test_completion_appends_exact_result_and_preserves_evaluation_content() -> None:
    current = evaluation(EvaluationState.RUNNING, verifier=EVALUATOR)
    supplied_result = result()
    transition_request = request(current, EvaluationState.COMPLETED)
    transitioned = transition_entity(
        current,
        transition_request,
        context(
            current,
            transition_request,
            completion_semantics(current, original_result=supplied_result),
        ),
    ).entity
    assert transitioned.state is EvaluationState.COMPLETED
    assert transitioned.version == VERSION.next()
    assert transitioned.result is supplied_result
    assert (transitioned.target, transitioned.method, transitioned.verifier) == (
        current.target,
        current.method,
        current.verifier,
    )


@pytest.mark.parametrize(
    "semantic",
    [
        lambda current: completion_semantics(
            current, completion_result=different_result()
        ),
        lambda current: completion_semantics(
            current, clearance_result=different_result()
        ),
        lambda current: completion_semantics(
            current,
            original_result=result(),
            completion_result=different_result(),
            clearance_result=different_result(),
        ),
        lambda current: completion_semantics(
            current,
            original_result=different_result(),
            completion_result=result(),
            clearance_result=result(),
        ),
    ],
    ids=(
        "completion-result-substitution",
        "conflict-clearance-result-substitution",
        "paired-decision-result-substitution",
        "intended-result-substitution",
    ),
)
def test_completion_rejects_result_substitution_against_intended_result(
    semantic: object,
) -> None:
    current = evaluation(EvaluationState.RUNNING, verifier=EVALUATOR)
    transition_request = request(current, EvaluationState.COMPLETED)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, semantic(current)),  # type: ignore[operator]
        )
    assert (current.state, current.version, current.result) == (
        EvaluationState.RUNNING,
        VERSION,
        None,
    )


def test_completion_projects_the_validated_independently_scoped_result() -> None:
    current = evaluation(EvaluationState.RUNNING, verifier=EVALUATOR)
    intended_result = result()
    transition_request = request(current, EvaluationState.COMPLETED)
    semantic = completion_semantics(current, original_result=intended_result)
    guard = EvaluationSemanticGuard(
        current.evaluation_id,
        current.version,
        current.state,
        transition_request.target_state,
        transition_request.correlation_id,
        semantic,
    )
    transitioned = transition_entity(
        current,
        transition_request,
        TransitionContext(
            (PassingGuard(),),
            TransitionAuthorityDecision(
                transition_request.actor,
                DomainEntityType.EVALUATION,
                current.evaluation_id,
                current.version,
                current.state,
                transition_request.target_state,
                TransitionAuthorityStatus.AUTHORIZED,
                transition_request.correlation_id,
            ),
            evaluation_semantic_guard=guard,
        ),
    ).entity
    assert guard.validated_completion_result() is intended_result
    assert transitioned.result is intended_result


@pytest.mark.parametrize(
    "semantic",
    [
        lambda current: completion_semantics(current, completion_by=OTHER_EVALUATOR),
        lambda current: completion_semantics(
            current, clearance_result=different_result()
        ),
        lambda current: completion_semantics(
            current, original_result=result(evidence_refs=frozenset())
        ),
        lambda current: completion_semantics(
            current, completion_status=EvaluationSemanticDecisionStatus.REJECTED
        ),
        lambda current: completion_semantics(
            current, clearance_status=EvaluationSemanticDecisionStatus.UNRESOLVED
        ),
        lambda current: completion_semantics(
            current, clearance_by=identity(ActorType.WORKER)
        ),
    ],
)
def test_completion_rejects_principal_result_or_clearance_substitution(
    semantic: object,
) -> None:
    current = evaluation(EvaluationState.RUNNING, verifier=EVALUATOR)
    transition_request = request(current, EvaluationState.COMPLETED)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, semantic(current)),  # type: ignore[operator]
        )
    assert (current.state, current.version, current.result) == (
        EvaluationState.RUNNING,
        VERSION,
        None,
    )


def test_unfavorable_evaluation_can_complete_without_changing_outcome() -> None:
    current = evaluation(EvaluationState.RUNNING, verifier=EVALUATOR)
    outcome = Outcome(
        OutcomeId(VALUE),
        RunId(VALUE),
        OutcomeState.VALIDATING,
        EntityVersion(3),
        identity(ActorType.WORKER),
        frozenset({ArtifactRef("candidate")}),
    )
    negative = result()
    transition_request = request(current, EvaluationState.COMPLETED)
    completed = transition_entity(
        current,
        transition_request,
        context(
            current,
            transition_request,
            completion_semantics(current, original_result=negative),
        ),
    ).entity
    assert completed.result is negative
    assert completed.result.verdict.value == "Requirement not met"
    assert outcome.state is OutcomeState.VALIDATING


@pytest.mark.parametrize(
    "source",
    [
        EvaluationState.PENDING,
        EvaluationState.RUNNING,
        EvaluationState.COMPLETED,
        EvaluationState.CONFLICTED,
    ],
)
def test_all_canonical_invalidation_sources_preserve_original_content(
    source: EvaluationState,
) -> None:
    current = evaluation(
        source,
        verifier=EVALUATOR,
        original_result=result()
        if source in {EvaluationState.COMPLETED, EvaluationState.CONFLICTED}
        else None,
    )
    transition_request = request(current, EvaluationState.INVALID)
    transitioned = transition_entity(
        current,
        transition_request,
        context(
            current,
            transition_request,
            invalidation_semantics(current),
        ),
    ).entity
    assert (transitioned.state, transitioned.version) == (
        EvaluationState.INVALID,
        VERSION.next(),
    )
    for field in fields(current):
        if field.name not in {"state", "version"}:
            assert getattr(transitioned, field.name) == getattr(current, field.name)


@pytest.mark.parametrize(
    "semantic",
    [
        lambda current: invalidation_semantics(
            current, evaluation_id=EvaluationId(OTHER)
        ),
        lambda current: invalidation_semantics(current, version=EntityVersion(8)),
        lambda current: invalidation_semantics(
            current, correlation=CorrelationId(OTHER)
        ),
    ],
)
def test_invalidation_rejects_identity_version_and_correlation_substitution(
    semantic: object,
) -> None:
    current = evaluation(EvaluationState.COMPLETED, verifier=EVALUATOR)
    transition_request = request(current, EvaluationState.INVALID)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, semantic(current)),  # type: ignore[operator]
        )
    assert (current.state, current.version) == (EvaluationState.COMPLETED, VERSION)


def test_invalidation_principal_substitution_and_worker_are_rejected() -> None:
    current = evaluation(EvaluationState.CONFLICTED, verifier=EVALUATOR)
    transition_request = request(
        current, EvaluationState.INVALID, actor=OTHER_EVALUATOR
    )
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                invalidation_semantics(current, invalidated_by=EVALUATOR),
            ),
        )
    worker = identity(ActorType.WORKER)
    worker_request = request(current, EvaluationState.INVALID, actor=worker)
    with pytest.raises(UnauthorizedTransition):
        transition_entity(
            current,
            worker_request,
            context(
                current,
                worker_request,
                invalidation_semantics(current, invalidated_by=worker),
            ),
        )


def test_negative_result_does_not_imply_invalidation_or_mutate_conflict_state() -> None:
    current = evaluation(
        EvaluationState.CONFLICTED,
        verifier=EVALUATOR,
        original_result=result(),
    )
    assert current.result is not None
    assert current.result.verdict.value == "Requirement not met"
    assert current.state is EvaluationState.CONFLICTED


def test_generic_guard_cannot_substitute_for_evaluation_semantic_guard() -> None:
    current = evaluation()
    transition_request = request(current, EvaluationState.RUNNING)
    authority = TransitionAuthorityDecision(
        EVALUATOR,
        DomainEntityType.EVALUATION,
        current.evaluation_id,
        current.version,
        current.state,
        EvaluationState.RUNNING,
        TransitionAuthorityStatus.AUTHORIZED,
        CORRELATION,
    )
    with pytest.raises(InvariantViolation, match="Canonical Evaluation semantic guard"):
        transition_entity(
            current,
            transition_request,
            TransitionContext((PassingGuard(),), authority),
        )


@pytest.mark.parametrize(
    "authority",
    [
        None,
        TransitionAuthorityStatus.DENIED,
        TransitionAuthorityStatus.UNRESOLVED,
    ],
)
def test_m7b1_authority_remains_mandatory(authority: object) -> None:
    current = evaluation()
    transition_request = request(current, EvaluationState.RUNNING)
    semantic = start_semantics(current)
    if authority is None:
        transition_context = TransitionContext(
            (PassingGuard(),),
            evaluation_semantic_guard=EvaluationSemanticGuard(
                current.evaluation_id,
                current.version,
                current.state,
                EvaluationState.RUNNING,
                CORRELATION,
                semantic,
            ),
        )
    else:
        transition_context = context(
            current,
            transition_request,
            semantic,
            authority=TransitionAuthorityDecision(
                EVALUATOR,
                DomainEntityType.EVALUATION,
                current.evaluation_id,
                current.version,
                current.state,
                EvaluationState.RUNNING,
                authority,  # type: ignore[arg-type]
                CORRELATION,
            ),
        )
    with pytest.raises(UnauthorizedTransition):
        transition_entity(current, transition_request, transition_context)


def test_topology_includes_all_ten_canonical_evaluation_edges() -> None:
    edges = {
        (source, target)
        for source in EvaluationState
        for target in EvaluationState
        if can_evaluation_transition(source, target)
    }
    assert len(edges) == 10
    conflict_and_arbitration = {
        (EvaluationState.RUNNING, EvaluationState.CONFLICTED),
        (EvaluationState.COMPLETED, EvaluationState.CONFLICTED),
        (EvaluationState.COMPLETED, EvaluationState.ARBITRATED),
        (EvaluationState.CONFLICTED, EvaluationState.ARBITRATED),
    }
    assert conflict_and_arbitration.issubset(edges)
    assert not can_evaluation_transition(
        EvaluationState.ARBITRATED, EvaluationState.INVALID
    )
    assert not any(
        can_evaluation_transition(EvaluationState.INVALID, target)
        for target in EvaluationState
    )


def test_failed_semantics_leave_the_source_snapshot_unchanged() -> None:
    current = evaluation(EvaluationState.RUNNING, verifier=EVALUATOR)
    transition_request = request(current, EvaluationState.COMPLETED)
    before = tuple(getattr(current, field.name) for field in fields(current))
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                completion_semantics(
                    current,
                    clearance_status=EvaluationSemanticDecisionStatus.UNRESOLVED,
                ),
            ),
        )
    assert tuple(getattr(current, field.name) for field in fields(current)) == before


def test_semantic_records_reject_empty_evidence_and_wrong_typed_input() -> None:
    current = evaluation()
    with pytest.raises(InvalidDomainValue):
        EvaluationVerifierIndependenceDecision(
            EvaluationSemanticDecisionRef("independence"),
            EvaluationSemanticDecisionStatus.PASSED,
            POLICY,
            frozenset(),
            current.evaluation_id,
            current.version,
            current.target,
            current.method,
            EVALUATOR,
            CORRELATION,
        )
    with pytest.raises(InvalidDomainValue):
        EvaluationSemanticGuard(
            current.evaluation_id,
            current.version,
            current.state,
            EvaluationState.RUNNING,
            CORRELATION,
            invalidation_semantics(current),
        )
