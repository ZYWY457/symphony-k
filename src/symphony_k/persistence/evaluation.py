"""Durable closure of the existing Evaluation multi-member guard contract."""

from __future__ import annotations

from typing import TYPE_CHECKING

from symphony_k.domain import ConcurrencyConflict, Evaluation, InvariantViolation
from symphony_k.domain.evaluation_arbitration import EvaluationArbitrationRecord
from symphony_k.domain.evaluation_conflict import EvaluationConflictSetRecord
from symphony_k.domain.evaluation_invalidation import EvaluationInvalidationRecord
from symphony_k.domain.evaluation_semantics import (
    EvaluationArbitrationSemantics,
    EvaluationConflictSemantics,
)
from symphony_k.domain.transition_engine import LifecycleEntity

from ._storage import Storage

if TYPE_CHECKING:
    from .service import TransitionOperation


def validate_evaluation_batch(
    storage: Storage,
    operations: tuple[TransitionOperation, ...],
    sources: tuple[LifecycleEntity, ...],
) -> None:
    """No lifecycle rules here: bind M7's declared participants to durable truth."""
    by_id = {item[0]: item for item in operations}
    conflict_history = tuple(
        item
        for item in storage._records(EvaluationConflictSetRecord)
        if isinstance(item, EvaluationConflictSetRecord)
    )
    latest = {
        item.conflict_set_id: item
        for item in sorted(conflict_history, key=lambda item: item.version.value)
    }
    arbitration_history = frozenset(
        item
        for item in storage._records(EvaluationArbitrationRecord)
        if isinstance(item, EvaluationArbitrationRecord)
    )
    invalidation_history = frozenset(
        item
        for item in storage._records(EvaluationInvalidationRecord)
        if isinstance(item, EvaluationInvalidationRecord)
    )
    for source, (_, _, context) in zip(sources, operations, strict=True):
        if not isinstance(source, Evaluation):
            continue
        guard = context.evaluation_semantic_guard
        assert guard is not None
        semantic = guard.semantic_input
        if isinstance(semantic, EvaluationConflictSemantics):
            conflict = semantic.conflict_set
            if latest.get(conflict.conflict_set_id) != semantic.previous_conflict_set:
                raise ConcurrencyConflict(
                    "Conflict-set history is not the durable current version"
                )
            for observation in semantic.participant_observations:
                current = storage.load(observation.evaluation_id)
                if not isinstance(current, Evaluation) or (
                    current.version != observation.observed_version
                    or current.state != observation.observed_state
                    or current.target != observation.target
                ):
                    raise ConcurrencyConflict(
                        "Conflict participant observation is stale"
                    )
                if (
                    observation.evaluation_id in by_id
                    and observation.evaluation_id
                    not in semantic.intended_conflicted_evaluation_ids
                ):
                    raise InvariantViolation(
                        "An already-conflicted member cannot change while gaining "
                        "unresolved conflict membership in the same batch"
                    )
            for entity_id in semantic.intended_conflicted_evaluation_ids:
                operation = by_id.get(entity_id)
                if operation is None:
                    raise InvariantViolation(
                        "Conflict requires all affected participants atomically"
                    )
                peer_guard = operation[2].evaluation_semantic_guard
                if peer_guard is None or not isinstance(
                    peer_guard.semantic_input, EvaluationConflictSemantics
                ):
                    raise InvariantViolation(
                        "Conflict peer lacks the same conflict operation"
                    )
                if peer_guard.semantic_input != semantic:
                    raise InvariantViolation(
                        "Conflict participants must share the exact semantic batch"
                    )
        elif isinstance(semantic, EvaluationArbitrationSemantics):
            applicable = frozenset(
                item
                for item in latest.values()
                if any(
                    member.evaluation_id == source.evaluation_id
                    for member in item.members
                )
            )
            if semantic.applicable_conflict_sets != applicable:
                raise ConcurrencyConflict(
                    "Arbitration omitted or substituted current conflict history"
                )
            historical = semantic.arbitration_history - {semantic.arbitration}
            relevant = frozenset(
                item
                for item in arbitration_history
                if any(
                    decision.evaluation_id == source.evaluation_id
                    for decision in item.decisions
                )
            )
            if not relevant <= historical or not historical <= arbitration_history:
                raise ConcurrencyConflict(
                    "Arbitration history is not authoritative and complete"
                )
            relevant_invalidations = frozenset(
                item
                for item in invalidation_history
                if item.evaluation_id == source.evaluation_id
            )
            if semantic.invalidation_history != relevant_invalidations:
                raise ConcurrencyConflict(
                    "Invalidation history is not authoritative and complete"
                )
            for decision in semantic.arbitration.decisions:
                current = storage.load(decision.evaluation_id)
                if current.version != decision.observed_version:
                    raise ConcurrencyConflict(
                        "Arbitration participant version is stale"
                    )
                operation = by_id.get(decision.evaluation_id)
                if operation is None:
                    raise InvariantViolation(
                        "Arbitration requires all affected decisions atomically"
                    )
                peer_guard = operation[2].evaluation_semantic_guard
                if peer_guard is None or not isinstance(
                    peer_guard.semantic_input, EvaluationArbitrationSemantics
                ):
                    raise InvariantViolation(
                        "Arbitration peer lacks its semantic guard"
                    )
                if peer_guard.semantic_input.arbitration != semantic.arbitration:
                    raise InvariantViolation(
                        "Arbitration participants refer to different decisions"
                    )
