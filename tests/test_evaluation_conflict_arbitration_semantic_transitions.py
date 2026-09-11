"""Canonical conflict and arbitration guards for the final Evaluation edges."""

from collections.abc import Callable
from dataclasses import fields
from datetime import UTC, datetime
from uuid import UUID

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ArbitrationDisposition,
    ConflictSetVersion,
    CorrelationId,
    DomainEntityType,
    EntityVersion,
    Evaluation,
    EvaluationArbitrationId,
    EvaluationArbitrationMemberDecision,
    EvaluationArbitrationPolicyRef,
    EvaluationArbitrationRecord,
    EvaluationArbitrationSemantics,
    EvaluationConfidence,
    EvaluationConflictMemberRef,
    EvaluationConflictParticipantObservation,
    EvaluationConflictScopeMaterialityProvenance,
    EvaluationConflictScopeRef,
    EvaluationConflictSemantics,
    EvaluationConflictSetId,
    EvaluationConflictSetRecord,
    EvaluationConflictSetRef,
    EvaluationId,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationSemanticGuard,
    EvaluationState,
    EvaluationTargetRef,
    EvaluationVerdict,
    EventId,
    EvidenceRef,
    InvariantViolation,
    OutcomeId,
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
THIRD = UUID("11111111-2222-4333-8444-555555555555")
VERSION = EntityVersion(7)
CORRELATION = CorrelationId(VALUE)
NOW = Timestamp(datetime(2026, 9, 11, tzinfo=UTC))
TARGET = EvaluationTargetRef(OutcomeId(VALUE), EntityVersion(3))
OTHER_TARGET = EvaluationTargetRef(OutcomeId(OTHER), EntityVersion(3))
METHOD = EvaluationMethodRef("independent-check", "v1")
CONFLICT_ID = EvaluationConflictSetId(OTHER)
ARBITRATION_ID = EvaluationArbitrationId(THIRD)


def actor(kind: ActorType, value: UUID = VALUE) -> ActorIdentity:
    return ActorIdentity(ActorId(value), kind)


EVALUATOR = actor(ActorType.EVALUATOR)
ARBITRATOR = actor(ActorType.ARBITRATOR)
HUMAN = actor(ActorType.HUMAN_OPERATOR)


def result() -> EvaluationResult:
    return EvaluationResult(
        EvaluationVerdict("opaque original judgement"),
        EvaluationConfidence("opaque confidence"),
        "Independent summary.",
        frozenset({EvidenceRef("result")}),
    )


def evaluation(
    state: EvaluationState, *, version: EntityVersion = VERSION
) -> Evaluation:
    return Evaluation(
        EvaluationId(VALUE),
        state,
        version,
        TARGET,
        METHOD,
        EVALUATOR,
        result()
        if state in {EvaluationState.COMPLETED, EvaluationState.CONFLICTED}
        else None,
    )


def request(
    current: Evaluation, target: EvaluationState, principal: ActorIdentity
) -> TransitionRequest[EvaluationState]:
    return TransitionRequest(
        EventId(THIRD),
        target,
        principal,
        TransitionReason("canonical edge"),
        current.version,
        NOW,
        CORRELATION,
    )


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
    semantic: EvaluationConflictSemantics | EvaluationArbitrationSemantics,
    *,
    status: TransitionAuthorityStatus = TransitionAuthorityStatus.AUTHORIZED,
) -> TransitionContext:
    return TransitionContext(
        (PassingGuard(),),
        TransitionAuthorityDecision(
            transition_request.actor,
            DomainEntityType.EVALUATION,
            current.evaluation_id,
            current.version,
            current.state,
            transition_request.target_state,
            status,
            transition_request.correlation_id,
        ),
        evaluation_semantic_guard=EvaluationSemanticGuard(
            current.evaluation_id,
            current.version,
            current.state,
            transition_request.target_state,
            transition_request.correlation_id,
            semantic,
        ),
    )


def conflict_record(
    current: Evaluation,
    *,
    conflict_id: EvaluationConflictSetId = CONFLICT_ID,
    version: int = 2,
    members: frozenset[EvaluationConflictMemberRef] | None = None,
    previous_version: int | None = None,
) -> EvaluationConflictSetRecord:
    return EvaluationConflictSetRecord(
        conflict_id,
        ConflictSetVersion(version),
        None if previous_version is None else ConflictSetVersion(previous_version),
        members
        or frozenset(
            {
                EvaluationConflictMemberRef(current.evaluation_id, current.version),
                EvaluationConflictMemberRef(EvaluationId(OTHER), EntityVersion(4)),
            }
        ),
        EvaluationConflictScopeRef("same acceptance scope"),
        "Material disagreement.",
        frozenset(),
        EVALUATOR,
        NOW,
        CORRELATION,
    )


def conflict_semantics(
    current: Evaluation,
    *,
    record: EvaluationConflictSetRecord | None = None,
    observations: frozenset[EvaluationConflictParticipantObservation] | None = None,
    intended: frozenset[EvaluationId] | None = None,
    previous: EvaluationConflictSetRecord | None = None,
) -> EvaluationConflictSemantics:
    represented = record or conflict_record(current)
    observed = observations or frozenset(
        {
            EvaluationConflictParticipantObservation(
                current.evaluation_id, current.version, current.state, current.target
            ),
            EvaluationConflictParticipantObservation(
                EvaluationId(OTHER),
                EntityVersion(4),
                EvaluationState.COMPLETED,
                OTHER_TARGET,
            ),
        }
    )
    return EvaluationConflictSemantics(
        represented,
        observed,
        EvaluationConflictScopeMaterialityProvenance(
            EvaluationConflictSetRef(represented.conflict_set_id, represented.version),
            represented.members,
            represented.affected_scope,
            represented.correlation_id,
            frozenset({EvidenceRef("scope materiality")}),
        ),
        intended
        or frozenset(
            item.evaluation_id
            for item in observed
            if item.observed_state
            in {EvaluationState.RUNNING, EvaluationState.COMPLETED}
        ),
        previous,
    )


def decision(
    current: Evaluation, *, verdict: EvaluationVerdict | None = None
) -> EvaluationArbitrationMemberDecision:
    original = current.result
    assert original is not None
    judgement = verdict or original.verdict
    return EvaluationArbitrationMemberDecision(
        current.evaluation_id,
        current.version,
        ArbitrationDisposition.UPHELD,
        original.verdict,
        judgement,
    )


def arbitration(
    current: Evaluation,
    *,
    conflict: EvaluationConflictSetRecord | None = None,
    arbitration_id: EvaluationArbitrationId = ARBITRATION_ID,
    prior: EvaluationArbitrationId | None = None,
) -> EvaluationArbitrationRecord:
    decisions = frozenset({decision(current)})
    if conflict is not None:
        decisions = frozenset(
            {
                decision(current),
                EvaluationArbitrationMemberDecision(
                    EvaluationId(OTHER),
                    EntityVersion(4),
                    ArbitrationDisposition.MODIFIED,
                    None,
                    EvaluationVerdict("other effective judgement"),
                ),
            }
        )
    return EvaluationArbitrationRecord(
        arbitration_id,
        None
        if conflict is None
        else EvaluationConflictSetRef(conflict.conflict_set_id, conflict.version),
        decisions,
        "Arbitration rationale.",
        frozenset({EvidenceRef("arbitration evidence")}),
        EvaluationArbitrationPolicyRef("arbitration", "v1"),
        ARBITRATOR,
        NOW,
        CORRELATION,
        prior,
    )


def arbitration_semantics(
    current: Evaluation,
    *,
    record: EvaluationArbitrationRecord,
    conflicts: frozenset[EvaluationConflictSetRecord] = frozenset(),
    history: frozenset[EvaluationArbitrationRecord] | None = None,
) -> EvaluationArbitrationSemantics:
    return EvaluationArbitrationSemantics(
        record, conflicts, history or frozenset({record}), frozenset()
    )


@pytest.mark.parametrize("source", [EvaluationState.RUNNING, EvaluationState.COMPLETED])
def test_conflict_transitions_bind_full_participant_batch_and_preserve_content(
    source: EvaluationState,
) -> None:
    current = evaluation(source)
    transition_request = request(current, EvaluationState.CONFLICTED, EVALUATOR)
    semantic = conflict_semantics(current)
    transitioned = transition_entity(
        current, transition_request, context(current, transition_request, semantic)
    ).entity
    assert (transitioned.state, transitioned.version) == (
        EvaluationState.CONFLICTED,
        VERSION.next(),
    )
    for field in fields(current):
        if field.name not in {"state", "version"}:
            assert getattr(transitioned, field.name) == getattr(current, field.name)
    assert semantic.intended_conflicted_evaluation_ids == frozenset(
        {EvaluationId(VALUE), EvaluationId(OTHER)}
    )


@pytest.mark.parametrize(
    "semantic",
    [
        lambda current: conflict_semantics(
            current, intended=frozenset({current.evaluation_id})
        ),
        lambda current: conflict_semantics(
            current,
            observations=frozenset(
                {
                    EvaluationConflictParticipantObservation(
                        current.evaluation_id,
                        current.version,
                        current.state,
                        current.target,
                    )
                }
            ),
        ),
        lambda current: conflict_semantics(
            current,
            observations=frozenset(
                {
                    EvaluationConflictParticipantObservation(
                        current.evaluation_id,
                        EntityVersion(8),
                        current.state,
                        current.target,
                    ),
                    EvaluationConflictParticipantObservation(
                        EvaluationId(OTHER),
                        EntityVersion(4),
                        EvaluationState.COMPLETED,
                        OTHER_TARGET,
                    ),
                }
            ),
        ),
    ],
)
def test_conflict_rejects_partial_or_stale_full_participant_sets(
    semantic: Callable[[Evaluation], EvaluationConflictSemantics],
) -> None:
    current = evaluation(EvaluationState.RUNNING)
    transition_request = request(current, EvaluationState.CONFLICTED, EVALUATOR)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(current, transition_request, semantic(current)),
        )


def test_conflict_extension_requires_append_only_prior_provenance() -> None:
    current = evaluation(EvaluationState.COMPLETED)
    prior = conflict_record(current, version=1)
    extended = conflict_record(current, version=2, previous_version=1)
    transition_request = request(current, EvaluationState.CONFLICTED, EVALUATOR)
    transition_entity(
        current,
        transition_request,
        context(
            current,
            transition_request,
            conflict_semantics(current, record=extended, previous=prior),
        ),
    )
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                conflict_semantics(current, record=extended),
            ),
        )


def test_direct_arbitration_preserves_result_and_annotations() -> None:
    current = evaluation(EvaluationState.COMPLETED)
    record = arbitration(current)
    transition_request = request(current, EvaluationState.ARBITRATED, ARBITRATOR)
    transitioned = transition_entity(
        current,
        transition_request,
        context(
            current, transition_request, arbitration_semantics(current, record=record)
        ),
    )
    assert transitioned.entity.result == current.result
    assert transitioned.event.metadata.annotations == frozenset(
        {("arbitration_id", str(record.arbitration_id.value))}
    )


def test_conflict_linked_arbitration_requires_every_current_conflict_to_resolve() -> (
    None
):
    current = evaluation(EvaluationState.CONFLICTED)
    resolved = conflict_record(current)
    unresolved = conflict_record(current, conflict_id=EvaluationConflictSetId(THIRD))
    record = arbitration(current, conflict=resolved)
    transition_request = request(current, EvaluationState.ARBITRATED, ARBITRATOR)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                arbitration_semantics(
                    current, record=record, conflicts=frozenset({resolved, unresolved})
                ),
            ),
        )
    transitioned = transition_entity(
        current,
        transition_request,
        context(
            current,
            transition_request,
            arbitration_semantics(
                current, record=record, conflicts=frozenset({resolved})
            ),
        ),
    )
    assert transitioned.entity.state is EvaluationState.ARBITRATED


def test_arbitration_rejects_nonterminal_lineage_and_ineligible_authority() -> None:
    current = evaluation(EvaluationState.COMPLETED)
    intended = arbitration(current)
    later = arbitration(
        current,
        arbitration_id=EvaluationArbitrationId(OTHER),
        prior=intended.arbitration_id,
    )
    transition_request = request(current, EvaluationState.ARBITRATED, ARBITRATOR)
    with pytest.raises(InvariantViolation):
        transition_entity(
            current,
            transition_request,
            context(
                current,
                transition_request,
                arbitration_semantics(
                    current, record=intended, history=frozenset({intended, later})
                ),
            ),
        )
    worker_request = request(
        current, EvaluationState.ARBITRATED, actor(ActorType.WORKER)
    )
    with pytest.raises(UnauthorizedTransition):
        transition_entity(
            current,
            worker_request,
            context(
                current, worker_request, arbitration_semantics(current, record=intended)
            ),
        )


def test_conflict_event_has_exact_conflict_reference_and_worker_is_ineligible() -> None:
    current = evaluation(EvaluationState.RUNNING)
    semantic = conflict_semantics(current)
    transition_request = request(current, EvaluationState.CONFLICTED, EVALUATOR)
    transitioned = transition_entity(
        current, transition_request, context(current, transition_request, semantic)
    )
    assert transitioned.event.metadata.annotations == frozenset(
        {
            ("conflict_set_id", str(semantic.conflict_set.conflict_set_id.value)),
            ("conflict_set_version", str(semantic.conflict_set.version.value)),
        }
    )
    worker_request = request(
        current, EvaluationState.CONFLICTED, actor(ActorType.WORKER)
    )
    with pytest.raises(UnauthorizedTransition):
        transition_entity(
            current, worker_request, context(current, worker_request, semantic)
        )
