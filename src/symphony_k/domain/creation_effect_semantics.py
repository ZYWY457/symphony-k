"""Pure Effect intent registration. No preparation, authorization or execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .creation_relationships import (
    CreationProvenanceRef,
    CreationRelationshipObservation,
    CreationRequestIdentity,
    require_current,
)
from .creation_run_outcome_evaluation import _CreationDecision, require_decision
from .effect import EffectDeduplicationRef
from .effect_governance import EffectGovernancePolicyRef
from .errors import InvalidDomainValue, InvalidRelationship, InvariantViolation
from .ids import EffectId
from .run import Run
from .task import Task

if TYPE_CHECKING:
    from .creation import PlannedEffectCreationRequest, PlannedEffectCreationSpec


@dataclass(frozen=True, slots=True)
class PlannedEffectIntentScope:
    effect_id: EffectId
    request_identity: CreationRequestIdentity
    spec: PlannedEffectCreationSpec
    task: CreationRelationshipObservation
    run: CreationRelationshipObservation | None
    intent_ref: CreationProvenanceRef
    risk_ref: CreationProvenanceRef
    reversibility_ref: CreationProvenanceRef
    permission_requirements_ref: CreationProvenanceRef
    authorization_class_ref: CreationProvenanceRef
    policy_refs: frozenset[EffectGovernancePolicyRef]
    deduplication_ref: EffectDeduplicationRef

    def __post_init__(self) -> None:
        from .creation import PlannedEffectCreationSpec

        for value, expected in (
            (self.effect_id, EffectId),
            (self.request_identity, CreationRequestIdentity),
            (self.spec, PlannedEffectCreationSpec),
            (self.task, CreationRelationshipObservation),
            (self.intent_ref, CreationProvenanceRef),
            (self.risk_ref, CreationProvenanceRef),
            (self.reversibility_ref, CreationProvenanceRef),
            (self.permission_requirements_ref, CreationProvenanceRef),
            (self.authorization_class_ref, CreationProvenanceRef),
            (self.deduplication_ref, EffectDeduplicationRef),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue("Invalid planned Effect intent scope")
        if self.run is not None and not isinstance(
            self.run, CreationRelationshipObservation
        ):
            raise InvalidDomainValue("Invalid planned Effect Run observation")
        if (
            not isinstance(self.policy_refs, frozenset)
            or not self.policy_refs
            or any(
                not isinstance(item, EffectGovernancePolicyRef)
                for item in self.policy_refs
            )
        ):
            raise InvalidDomainValue(
                "Intent requires immutable exact policy references"
            )


@dataclass(frozen=True, slots=True)
class PlannedEffectIntentDecision(_CreationDecision):
    scope: PlannedEffectIntentScope

    def __post_init__(self) -> None:
        _CreationDecision.__post_init__(self)
        if not isinstance(self.scope, PlannedEffectIntentScope):
            raise InvalidDomainValue("Invalid Effect intent decision scope")


def validate_planned_effect_creation(
    request: PlannedEffectCreationRequest,
) -> PlannedEffectIntentScope:
    semantics = request.semantic_input
    scope, decision = semantics.intent, semantics.decision
    if scope is None or decision is None:
        raise InvariantViolation(
            "Canonical entity-specific creation semantics are not implemented"
        )
    identity = CreationRequestIdentity(
        request.requested_by,
        request.causation_id,
        request.correlation_id,
        semantics.provenance_ref,
    )
    if (
        scope.effect_id != request.entity_id
        or scope.spec != request.entity_spec
        or scope.request_identity != identity
        or decision.scope != scope
    ):
        raise InvariantViolation(
            "Effect intent decision must exact-bind request and semantic scope"
        )
    principals = (request.requested_by, scope.spec.origin.proposed_by)
    require_decision(decision, principals)
    task = require_current(scope.task, identity, scope.spec.origin.task_id, principals)
    if not isinstance(task, Task):
        raise InvalidRelationship("Planned Effect requires an existing Task")
    run_id = scope.spec.origin.run_id
    if run_id is None:
        if scope.run is not None:
            raise InvalidRelationship(
                "Unattributed Run observation cannot supply ownership"
            )
    else:
        if scope.run is None:
            raise InvalidRelationship("Attributed Run requires current observation")
        run = require_current(scope.run, identity, run_id, principals)
        if not isinstance(run, Run) or run.task_id != task.task_id:
            raise InvalidRelationship("Effect Run must belong to the accountable Task")
    return scope


def planned_effect_annotations(
    scope: PlannedEffectIntentScope, decision: PlannedEffectIntentDecision
) -> frozenset[tuple[str, str]]:
    values = [
        ("semantic_decision_ref", decision.decision_ref.value),
        ("intent_ref", scope.intent_ref.value),
        ("risk_ref", scope.risk_ref.value),
        ("reversibility_ref", scope.reversibility_ref.value),
        ("permission_requirements_ref", scope.permission_requirements_ref.value),
        ("authorization_class_ref", scope.authorization_class_ref.value),
        ("deduplication_ref", scope.deduplication_ref.value),
    ]
    for index, policy in enumerate(
        sorted(
            scope.policy_refs, key=lambda item: (item.policy_id, item.policy_version)
        )
    ):
        values.extend(
            (
                (f"intent_policy.{index:04d}.id", policy.policy_id),
                (f"intent_policy.{index:04d}.version", policy.policy_version),
            )
        )
    evidence = decision.evidence_refs
    for prefix, observation in (("task", scope.task), ("run", scope.run)):
        if observation is not None:
            assert observation.snapshot is not None
            values.extend(
                (
                    (f"{prefix}.observation_ref", observation.observation_ref.value),
                    (
                        f"{prefix}.observed_version",
                        str(observation.snapshot.version.value),
                    ),
                )
            )
            evidence |= observation.evidence_refs
    values.extend(
        (f"semantic_evidence_ref.{index:04d}", item.value)
        for index, item in enumerate(sorted(evidence, key=lambda item: item.value))
    )
    return frozenset(values)
