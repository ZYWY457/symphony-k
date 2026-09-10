"""M7C4B canonical Outcome acceptance and rejection semantic guards."""

from dataclasses import fields, replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArtifactRef,
    CompletionPolicyRef,
    ConflictSetVersion,
    CorrelationId,
    DomainEntityType,
    Effect,
    EffectId,
    EffectPayloadRef,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    Evaluation,
    EvaluationArbitrationId,
    EvaluationConfidence,
    EvaluationConflictSetId,
    EvaluationConflictSetRef,
    EvaluationEffectiveUseView,
    EvaluationId,
    EvaluationInvalidationId,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationState,
    EvaluationTargetRef,
    EvaluationVerdict,
    EventId,
    EvidenceRef,
    ExecutionProfileRef,
    InvalidDomainValue,
    InvariantViolation,
    Objective,
    ObjectiveId,
    ObjectiveState,
    Outcome,
    OutcomeDisposition,
    OutcomeDispositionPolicyDecision,
    OutcomeDispositionPolicyRef,
    OutcomeDispositionSemantics,
    OutcomeEvaluationEffectiveUseObservation,
    OutcomeEvaluationEffectiveUseSnapshot,
    OutcomeEvaluationRequestRef,
    OutcomeHumanAcceptanceDecision,
    OutcomeId,
    OutcomeSemanticDecisionRef,
    OutcomeSemanticDecisionStatus,
    OutcomeSemanticGuard,
    OutcomeState,
    OutcomeValidationLineage,
    PlannedEffectOrigin,
    Run,
    RunId,
    RunState,
    Task,
    TaskId,
    TaskState,
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
CANDIDATE_VERSION = EntityVersion(17)
VALIDATING_VERSION = EntityVersion(18)
REQUEST_EVALUATION_VERSION = EntityVersion(29)
OBSERVED_EVALUATION_VERSION = EntityVersion(31)
CORRELATION_ID = CorrelationId(VALUE)
JUDGEMENT = EvaluationVerdict("mauve ducks align with the supplied evidence")


def identity(actor_type: ActorType, value: UUID = VALUE) -> ActorIdentity:
    return ActorIdentity(ActorId(value), actor_type)


def outcome() -> Outcome:
    return Outcome(
        OutcomeId(VALUE),
        RunId(VALUE),
        OutcomeState.VALIDATING,
        VALIDATING_VERSION,
        identity(ActorType.WORKER),
        frozenset({ArtifactRef("candidate-a"), ArtifactRef("candidate-b")}),
        frozenset({EvidenceRef("worker-evidence")}),
    )


def lineage(snapshot: Outcome) -> OutcomeValidationLineage:
    return OutcomeValidationLineage(
        snapshot.outcome_id,
        CANDIDATE_VERSION,
        snapshot.version,
        CORRELATION_ID,
        frozenset({ArtifactRef("candidate-a")}),
        OutcomeEvaluationRequestRef(
            "evaluation-request",
            EvaluationId(OTHER),
            REQUEST_EVALUATION_VERSION,
        ),
    )


def effective_use(
    *,
    state: EvaluationState = EvaluationState.COMPLETED,
) -> EvaluationEffectiveUseView:
    if state is EvaluationState.ARBITRATED:
        arbitration_id = EvaluationArbitrationId(VALUE)
        return EvaluationEffectiveUseView(
            EvaluationId(OTHER),
            EvaluationVerdict("original opaque judgement"),
            JUDGEMENT,
            frozenset(),
            frozenset(),
            frozenset({arbitration_id}),
            arbitration_id,
            False,
            frozenset(),
            True,
        )
    return EvaluationEffectiveUseView(
        EvaluationId(OTHER),
        JUDGEMENT,
        JUDGEMENT,
        frozenset(),
        frozenset(),
        frozenset(),
        None,
        False,
        frozenset(),
        True,
    )


def semantics(
    snapshot: Outcome,
    target: OutcomeState,
    *,
    evaluation_state: EvaluationState = EvaluationState.COMPLETED,
    require_human: bool = False,
    include_human: bool | None = None,
) -> OutcomeDispositionSemantics:
    validation_lineage = lineage(snapshot)
    view = effective_use(state=evaluation_state)
    observation = OutcomeEvaluationEffectiveUseObservation(
        validation_lineage.evaluation_request_ref,
        EvaluationId(OTHER),
        OBSERVED_EVALUATION_VERSION,
        evaluation_state,
        EvaluationTargetRef(snapshot.outcome_id, CANDIDATE_VERSION),
        identity(ActorType.EVALUATOR, THIRD),
        view,
        CORRELATION_ID,
        OutcomeEvaluationEffectiveUseSnapshot(
            EvaluationId(OTHER),
            OBSERVED_EVALUATION_VERSION,
            evaluation_state,
            EvaluationTargetRef(snapshot.outcome_id, CANDIDATE_VERSION),
            view,
        ),
    )
    disposition = (
        OutcomeDisposition.ACCEPTED
        if target is OutcomeState.ACCEPTED
        else OutcomeDisposition.REJECTED
    )
    policy_ref = OutcomeDispositionPolicyRef("outcome-disposition", "v7")
    policy = OutcomeDispositionPolicyDecision(
        OutcomeSemanticDecisionRef("disposition-policy-decision"),
        OutcomeSemanticDecisionStatus.PASSED,
        identity(ActorType.POLICY_ENGINE, THIRD),
        frozenset({EvidenceRef("policy-evidence")}),
        validation_lineage,
        observation.evaluation_id,
        observation.observed_evaluation_version,
        JUDGEMENT,
        disposition,
        policy_ref,
        require_human,
    )
    if include_human is None:
        include_human = require_human
    human = None
    if include_human:
        human = OutcomeHumanAcceptanceDecision(
            OutcomeSemanticDecisionRef("human-acceptance"),
            True,
            identity(ActorType.HUMAN_OPERATOR, OTHER),
            frozenset({EvidenceRef("human-evidence")}),
            validation_lineage,
            observation.evaluation_id,
            observation.observed_evaluation_version,
            JUDGEMENT,
            OutcomeDisposition.ACCEPTED,
            policy_ref,
            policy.decision_ref,
        )
    return OutcomeDispositionSemantics(validation_lineage, observation, policy, human)


def request(
    snapshot: Outcome,
    target: OutcomeState,
    *,
    actor: ActorIdentity | None = None,
) -> TransitionRequest[OutcomeState]:
    return TransitionRequest(
        EventId(VALUE),
        target,
        actor or identity(ActorType.SCHEDULER),
        TransitionReason("Apply explicit Outcome disposition"),
        snapshot.version,
        Timestamp(datetime(2026, 9, 10, tzinfo=UTC)),
        CORRELATION_ID,
    )


def guard(
    snapshot: Outcome,
    target: OutcomeState,
    semantic_input: OutcomeDispositionSemantics | None = None,
) -> OutcomeSemanticGuard:
    return OutcomeSemanticGuard(
        snapshot.outcome_id,
        snapshot.version,
        snapshot.state,
        target,
        CORRELATION_ID,
        semantic_input or semantics(snapshot, target),
    )


def context(
    snapshot: Outcome,
    transition_request: TransitionRequest[OutcomeState],
    semantic_guard: OutcomeSemanticGuard | None = None,
    *,
    authority_status: TransitionAuthorityStatus = TransitionAuthorityStatus.AUTHORIZED,
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
        outcome_semantic_guard=semantic_guard
        or guard(snapshot, transition_request.target_state),
    )


class PassingGuard:
    def validate(
        self,
        entity: LifecycleEntity,
        transition_request: TransitionRequest[LifecycleState],
    ) -> None:
        assert entity.version == transition_request.expected_version


@pytest.mark.parametrize(
    ("target", "evaluation_state"),
    [
        (OutcomeState.ACCEPTED, EvaluationState.COMPLETED),
        (OutcomeState.REJECTED, EvaluationState.COMPLETED),
        (OutcomeState.ACCEPTED, EvaluationState.ARBITRATED),
        (OutcomeState.REJECTED, EvaluationState.ARBITRATED),
    ],
)
def test_explicit_disposition_accepts_completed_or_arbitrated_effective_use(
    target: OutcomeState, evaluation_state: EvaluationState
) -> None:
    snapshot = outcome()
    semantic_input = semantics(snapshot, target, evaluation_state=evaluation_state)
    transition_request = request(snapshot, target)
    before = tuple(getattr(snapshot, field.name) for field in fields(snapshot))

    result = transition_entity(
        snapshot,
        transition_request,
        context(snapshot, transition_request, guard(snapshot, target, semantic_input)),
    )

    assert result.entity.state is target
    assert result.entity.version == VALIDATING_VERSION.next()
    assert result.event.metadata.prior_state is OutcomeState.VALIDATING
    assert result.event.metadata.new_state is target
    assert tuple(getattr(snapshot, field.name) for field in fields(snapshot)) == before
    for field in fields(snapshot):
        if field.name not in {"state", "version"}:
            assert getattr(result.entity, field.name) == getattr(snapshot, field.name)


@pytest.mark.parametrize(
    ("outcome_id", "observed_version", "correlation_id"),
    [
        (OutcomeId(OTHER), VALIDATING_VERSION, CORRELATION_ID),
        (OutcomeId(VALUE), EntityVersion(19), CORRELATION_ID),
        (OutcomeId(VALUE), VALIDATING_VERSION, CorrelationId(OTHER)),
    ],
)
def test_disposition_guard_binds_exact_outcome_snapshot_and_correlation(
    outcome_id: OutcomeId,
    observed_version: EntityVersion,
    correlation_id: CorrelationId,
) -> None:
    snapshot = outcome()
    semantic_input = semantics(snapshot, OutcomeState.ACCEPTED)
    forged = OutcomeSemanticGuard(
        outcome_id,
        observed_version,
        OutcomeState.VALIDATING,
        OutcomeState.ACCEPTED,
        correlation_id,
        semantic_input,
    )
    transition_request = request(snapshot, OutcomeState.ACCEPTED)

    with pytest.raises(InvariantViolation, match="exact request snapshot"):
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, forged),
        )


def test_disposition_guard_binds_exact_source_and_target_state() -> None:
    snapshot = outcome()
    accepted_guard = guard(snapshot, OutcomeState.ACCEPTED)
    with pytest.raises(InvariantViolation, match="exact request snapshot"):
        accepted_guard.validate(
            replace(snapshot, state=OutcomeState.ACCEPTED),
            OutcomeState.ACCEPTED,
            CORRELATION_ID,
        )
    with pytest.raises(InvariantViolation, match="exact request snapshot"):
        accepted_guard.validate(snapshot, OutcomeState.REJECTED, CORRELATION_ID)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: replace(value, outcome_id=OutcomeId(OTHER)),
        lambda value: replace(value, candidate_version=EntityVersion(16)),
        lambda value: replace(value, validating_version=EntityVersion(19)),
        lambda value: replace(value, correlation_id=CorrelationId(OTHER)),
        lambda value: replace(value, artifact_refs=frozenset({ArtifactRef("foreign")})),
        lambda value: replace(
            value,
            evaluation_request_ref=OutcomeEvaluationRequestRef(
                "other-request", EvaluationId(OTHER), REQUEST_EVALUATION_VERSION
            ),
        ),
    ],
)
def test_validation_start_lineage_is_exact_bound(mutation: object) -> None:
    snapshot = outcome()
    semantic_input = semantics(snapshot, OutcomeState.ACCEPTED)
    with pytest.raises((InvalidDomainValue, InvariantViolation)):
        changed = mutation(semantic_input.validation_lineage)  # type: ignore[operator]
        forged = replace(semantic_input, validation_lineage=changed)
        transition_request = request(snapshot, OutcomeState.ACCEPTED)
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard(snapshot, OutcomeState.ACCEPTED, forged),
            ),
        )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: replace(value, evaluation_id=EvaluationId(VALUE)),
        lambda value: replace(value, observed_evaluation_version=EntityVersion(30)),
        lambda value: replace(
            value,
            request_ref=OutcomeEvaluationRequestRef(
                "evaluation-request", EvaluationId(VALUE), REQUEST_EVALUATION_VERSION
            ),
        ),
        lambda value: replace(
            value, target=EvaluationTargetRef(OutcomeId(OTHER), CANDIDATE_VERSION)
        ),
        lambda value: replace(
            value,
            target=EvaluationTargetRef(OutcomeId(VALUE), VALIDATING_VERSION),
        ),
        lambda value: replace(value, correlation_id=CorrelationId(OTHER)),
        lambda value: replace(value, observed_state=EvaluationState.INVALID),
        lambda value: replace(value, verifier=identity(ActorType.WORKER, THIRD)),
        lambda value: replace(value, verifier=identity(ActorType.EVALUATOR)),
        lambda value: replace(value, verifier=identity(ActorType.SCHEDULER, THIRD)),
    ],
)
def test_effective_use_observation_rejects_provenance_substitution(
    mutation: object,
) -> None:
    snapshot = outcome()
    semantic_input = semantics(snapshot, OutcomeState.ACCEPTED)
    changed = mutation(semantic_input.evaluation)  # type: ignore[operator]
    forged = replace(semantic_input, evaluation=changed)
    transition_request = request(snapshot, OutcomeState.ACCEPTED)

    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard(snapshot, OutcomeState.ACCEPTED, forged),
            ),
        )


@pytest.mark.parametrize(
    ("source_state", "relabelled_state"),
    [
        (EvaluationState.COMPLETED, EvaluationState.ARBITRATED),
        (EvaluationState.ARBITRATED, EvaluationState.COMPLETED),
    ],
)
def test_effective_use_provenance_cannot_be_relabelled_across_states(
    source_state: EvaluationState, relabelled_state: EvaluationState
) -> None:
    snapshot = outcome()
    semantic_input = semantics(
        snapshot, OutcomeState.ACCEPTED, evaluation_state=source_state
    )
    observation = semantic_input.evaluation
    relabelled_snapshot = replace(
        observation.effective_use_snapshot,
        observed_state=relabelled_state,
    )
    forged = replace(
        semantic_input,
        evaluation=replace(
            observation,
            observed_state=relabelled_state,
            effective_use_snapshot=relabelled_snapshot,
        ),
    )
    transition_request = request(snapshot, OutcomeState.ACCEPTED)

    with pytest.raises(InvariantViolation, match="effective-use provenance"):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard(snapshot, OutcomeState.ACCEPTED, forged),
            ),
        )


def unusable_views() -> tuple[EvaluationEffectiveUseView, ...]:
    conflict_ref = EvaluationConflictSetRef(
        EvaluationConflictSetId(VALUE), ConflictSetVersion(2)
    )
    base = effective_use()
    return (
        replace(base, eligible_for_effective_use=False),
        replace(
            base,
            effective_judgement=None,
            eligible_for_effective_use=False,
        ),
        replace(
            base,
            applicable_conflicts=frozenset({conflict_ref}),
            unresolved_conflicts=frozenset({conflict_ref}),
        ),
        replace(
            base,
            effective_judgement=None,
            arbitration_ambiguous=True,
            eligible_for_effective_use=False,
        ),
        replace(
            base,
            invalidation_ids=frozenset({EvaluationInvalidationId(VALUE)}),
        ),
    )


@pytest.mark.parametrize("view", unusable_views())
def test_ineligible_conflicted_ambiguous_or_invalid_effective_use_rejects(
    view: EvaluationEffectiveUseView,
) -> None:
    snapshot = outcome()
    semantic_input = semantics(snapshot, OutcomeState.REJECTED)
    forged = replace(
        semantic_input,
        evaluation=replace(semantic_input.evaluation, effective_use=view),
    )
    transition_request = request(snapshot, OutcomeState.REJECTED)

    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard(snapshot, OutcomeState.REJECTED, forged),
            ),
        )
    assert (snapshot.state, snapshot.version) == (
        OutcomeState.VALIDATING,
        VALIDATING_VERSION,
    )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: replace(value, status=OutcomeSemanticDecisionStatus.REJECTED),
        lambda value: replace(value, decided_by=identity(ActorType.WORKER)),
        lambda value: replace(value, decided_by=identity(ActorType.SCHEDULER)),
        lambda value: replace(value, decided_by=identity(ActorType.POLICY_ENGINE)),
        lambda value: replace(value, evaluation_id=EvaluationId(VALUE)),
        lambda value: replace(value, observed_evaluation_version=EntityVersion(30)),
        lambda value: replace(
            value, effective_judgement=EvaluationVerdict("substituted judgement")
        ),
        lambda value: replace(value, disposition=OutcomeDisposition.REJECTED),
        lambda value: replace(
            value,
            validation_lineage=replace(
                value.validation_lineage,
                artifact_refs=frozenset({ArtifactRef("candidate-b")}),
            ),
        ),
    ],
)
def test_disposition_policy_is_mandatory_current_and_exact(mutation: object) -> None:
    snapshot = outcome()
    semantic_input = semantics(snapshot, OutcomeState.ACCEPTED)
    changed = mutation(semantic_input.policy_decision)  # type: ignore[operator]
    forged = replace(semantic_input, policy_decision=changed)
    transition_request = request(snapshot, OutcomeState.ACCEPTED)

    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard(snapshot, OutcomeState.ACCEPTED, forged),
            ),
        )


def test_accept_support_cannot_be_reused_for_rejection_or_infer_rejection() -> None:
    snapshot = outcome()
    accepted_input = semantics(snapshot, OutcomeState.ACCEPTED)
    transition_request = request(snapshot, OutcomeState.REJECTED)

    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard(snapshot, OutcomeState.REJECTED, accepted_input),
            ),
        )
    assert snapshot.state is OutcomeState.VALIDATING


def test_reject_support_cannot_be_reused_for_acceptance() -> None:
    snapshot = outcome()
    rejected_input = semantics(snapshot, OutcomeState.REJECTED)
    transition_request = request(snapshot, OutcomeState.ACCEPTED)

    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard(snapshot, OutcomeState.ACCEPTED, rejected_input),
            ),
        )


def test_human_acceptance_is_required_exactly_when_policy_requires_it() -> None:
    snapshot = outcome()
    target = OutcomeState.ACCEPTED
    transition_request = request(snapshot, target)
    missing = semantics(snapshot, target, require_human=True, include_human=False)
    with pytest.raises(InvariantViolation, match="human acceptance is missing"):
        transition_entity(
            snapshot,
            transition_request,
            context(snapshot, transition_request, guard(snapshot, target, missing)),
        )

    optional = semantics(snapshot, target, require_human=False, include_human=False)
    result = transition_entity(
        snapshot,
        transition_request,
        context(snapshot, transition_request, guard(snapshot, target, optional)),
    )
    assert result.entity.state is OutcomeState.ACCEPTED


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: replace(value, affirmative=False),
        lambda value: replace(value, decided_by=identity(ActorType.WORKER)),
        lambda value: replace(value, decided_by=identity(ActorType.POLICY_ENGINE)),
        lambda value: replace(value, decided_by=identity(ActorType.HUMAN_OPERATOR)),
        lambda value: replace(value, evaluation_id=EvaluationId(VALUE)),
        lambda value: replace(value, observed_evaluation_version=EntityVersion(30)),
        lambda value: replace(
            value, effective_judgement=EvaluationVerdict("substituted judgement")
        ),
        lambda value: replace(
            value, policy_ref=OutcomeDispositionPolicyRef("foreign", "v1")
        ),
        lambda value: replace(
            value, policy_decision_ref=OutcomeSemanticDecisionRef("foreign")
        ),
    ],
)
def test_required_human_acceptance_is_affirmative_human_and_exact(
    mutation: object,
) -> None:
    snapshot = outcome()
    semantic_input = semantics(snapshot, OutcomeState.ACCEPTED, require_human=True)
    assert semantic_input.human_acceptance is not None
    changed = mutation(semantic_input.human_acceptance)  # type: ignore[operator]
    forged = replace(semantic_input, human_acceptance=changed)
    transition_request = request(snapshot, OutcomeState.ACCEPTED)

    with pytest.raises(InvariantViolation):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard(snapshot, OutcomeState.ACCEPTED, forged),
            ),
        )


@pytest.mark.parametrize(
    ("target", "actor_type", "authority_status"),
    [
        (
            OutcomeState.ACCEPTED,
            ActorType.WORKER,
            TransitionAuthorityStatus.AUTHORIZED,
        ),
        (
            OutcomeState.REJECTED,
            ActorType.WORKER,
            TransitionAuthorityStatus.AUTHORIZED,
        ),
        (
            OutcomeState.ACCEPTED,
            ActorType.EVALUATOR,
            TransitionAuthorityStatus.AUTHORIZED,
        ),
        (
            OutcomeState.REJECTED,
            ActorType.HUMAN_OPERATOR,
            TransitionAuthorityStatus.AUTHORIZED,
        ),
        (
            OutcomeState.ACCEPTED,
            ActorType.SCHEDULER,
            TransitionAuthorityStatus.DENIED,
        ),
    ],
)
def test_m7b1_and_m7b2_remain_mandatory_for_disposition(
    target: OutcomeState,
    actor_type: ActorType,
    authority_status: TransitionAuthorityStatus,
) -> None:
    snapshot = outcome()
    transition_request = request(snapshot, target, actor=identity(actor_type))
    with pytest.raises(UnauthorizedTransition):
        transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                authority_status=authority_status,
            ),
        )


def test_generic_guard_cannot_replace_canonical_disposition_semantics() -> None:
    snapshot = outcome()
    transition_request = request(snapshot, OutcomeState.ACCEPTED)
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


def test_free_form_evaluation_verdict_is_not_parsed_as_pass_or_fail() -> None:
    snapshot = outcome()
    accepted_input = semantics(snapshot, OutcomeState.ACCEPTED)
    rejected_input = semantics(snapshot, OutcomeState.REJECTED)

    for target, semantic_input in (
        (OutcomeState.ACCEPTED, accepted_input),
        (OutcomeState.REJECTED, rejected_input),
    ):
        transition_request = request(snapshot, target)
        result = transition_entity(
            snapshot,
            transition_request,
            context(
                snapshot,
                transition_request,
                guard(snapshot, target, semantic_input),
            ),
        )
        assert result.entity.state is target


def test_outcome_and_evaluation_version_domains_remain_distinct() -> None:
    snapshot = outcome()
    semantic_input = semantics(snapshot, OutcomeState.ACCEPTED)
    assert CANDIDATE_VERSION.next() == snapshot.version
    assert REQUEST_EVALUATION_VERSION != CANDIDATE_VERSION
    assert OBSERVED_EVALUATION_VERSION != snapshot.version
    assert (
        semantic_input.evaluation.target.version
        == semantic_input.validation_lineage.candidate_version
    )
    assert semantic_input.evaluation.target.version != snapshot.version


@pytest.mark.parametrize("target", [OutcomeState.ACCEPTED, OutcomeState.REJECTED])
def test_disposition_does_not_propagate_to_other_lifecycles(
    target: OutcomeState,
) -> None:
    snapshot = outcome()
    objective = Objective(
        ObjectiveId(VALUE),
        ObjectiveState.ACTIVE,
        EntityVersion(4),
        "Keep lifecycle decisions separate",
        ("No propagation",),
        identity(ActorType.HUMAN_OPERATOR),
        CompletionPolicyRef("objective-completion", "v1"),
    )
    task = Task(
        TaskId(VALUE),
        TaskState.IN_PROGRESS,
        EntityVersion(5),
        "Validate the candidate",
        objective.objective_id,
        CompletionPolicyRef("task-completion", "v1"),
    )
    run = Run(
        snapshot.run_id,
        task.task_id,
        RunState.WAITING_FOR_VERIFICATION,
        EntityVersion(6),
        ExecutionProfileRef("profile", "v1"),
    )
    evaluation = Evaluation(
        EvaluationId(OTHER),
        EvaluationState.COMPLETED,
        OBSERVED_EVALUATION_VERSION,
        EvaluationTargetRef(snapshot.outcome_id, CANDIDATE_VERSION),
        EvaluationMethodRef("independent", "v1"),
        identity(ActorType.EVALUATOR, THIRD),
        EvaluationResult(
            JUDGEMENT,
            EvaluationConfidence("opaque confidence"),
            "Independent reasoning summary",
            frozenset({EvidenceRef("evaluation-evidence")}),
        ),
    )
    effect = Effect(
        EffectId(VALUE),
        EffectState.PLANNED,
        EntityVersion(7),
        PlannedEffectOrigin(task.task_id, identity(ActorType.WORKER), run.run_id),
        EffectTargetRef("external-target"),
        EffectPayloadRef("payload"),
    )
    related_before = (objective, task, run, evaluation, effect)
    transition_request = request(snapshot, target)

    result = transition_entity(
        snapshot,
        transition_request,
        context(snapshot, transition_request),
    )

    assert result.entity.state is target
    assert (objective, task, run, evaluation, effect) == related_before
    assert objective.state is ObjectiveState.ACTIVE
    assert task.state is TaskState.IN_PROGRESS
    assert run.state is RunState.WAITING_FOR_VERIFICATION
    assert evaluation.state is EvaluationState.COMPLETED
    assert effect.state is EffectState.PLANNED
