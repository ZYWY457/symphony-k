"""Pure creation registration, candidate proposal and validation-request evidence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from .actors import ActorIdentity, ActorType
from .candidate_refs import ArtifactRef, EvidenceRef
from .creation_relationships import (
    CreationProvenanceRef,
    CreationRelationshipObservation,
    CreationRequestIdentity,
    require_current,
    require_independent,
)
from .creation_semantics import CreationSemanticDecisionStatus, _require_evidence
from .effect import Effect, PlannedEffectOrigin
from .errors import InvalidDomainValue, InvalidRelationship, InvariantViolation
from .evaluation_target import EvaluationTargetRef
from .ids import EvaluationId, OutcomeId, RunId, TaskId
from .objective import Objective, ObjectiveState
from .outcome import Outcome
from .outcome_semantics import OutcomeAcceptanceScopeRef
from .run import Run
from .task import Task, TaskState
from .time import Timestamp

if TYPE_CHECKING:
    from .creation import (
        EvaluationCreationSpec,
        EvaluationPendingCreationRequest,
        OutcomeCreationSpec,
        OutcomeProposedCreationRequest,
        RunCreationSpec,
        RunPendingCreationRequest,
    )


def _require_tuple(value: tuple[CreationRelationshipObservation, ...]) -> None:
    if not isinstance(value, tuple) or any(
        not isinstance(item, CreationRelationshipObservation) for item in value
    ):
        raise InvalidDomainValue("Lineage must be a tuple of relationship observations")


class RunCreationLineageKind(Enum):
    NEW_ATTEMPT = "NEW_ATTEMPT"
    RECOVERY = "RECOVERY"
    REASSIGNMENT = "REASSIGNMENT"


@dataclass(frozen=True, slots=True)
class RunRegistrationScope:
    run_id: RunId
    request_identity: CreationRequestIdentity
    spec: RunCreationSpec
    task: CreationRelationshipObservation
    primary_objective: CreationRelationshipObservation
    attempt_ref: CreationProvenanceRef
    profile_selection_ref: CreationProvenanceRef
    lineage_kind: RunCreationLineageKind
    lineage_decision_ref: CreationProvenanceRef | None = None
    predecessor_lineage: tuple[CreationRelationshipObservation, ...] = ()

    def __post_init__(self) -> None:
        from .creation import RunCreationSpec

        for value, expected in (
            (self.run_id, RunId),
            (self.request_identity, CreationRequestIdentity),
            (self.spec, RunCreationSpec),
            (self.task, CreationRelationshipObservation),
            (self.primary_objective, CreationRelationshipObservation),
            (self.attempt_ref, CreationProvenanceRef),
            (self.profile_selection_ref, CreationProvenanceRef),
            (self.lineage_kind, RunCreationLineageKind),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue("Invalid Run registration scope")
        if self.lineage_decision_ref is not None and not isinstance(
            self.lineage_decision_ref, CreationProvenanceRef
        ):
            raise InvalidDomainValue("Invalid Run lineage decision reference")
        _require_tuple(self.predecessor_lineage)


@dataclass(frozen=True, slots=True)
class OutcomeProposalScope:
    outcome_id: OutcomeId
    request_identity: CreationRequestIdentity
    spec: OutcomeCreationSpec
    originating_run: CreationRelationshipObservation
    task_id: TaskId
    acceptance_scope: OutcomeAcceptanceScopeRef
    proposal_ref: CreationProvenanceRef
    prior_lineage: tuple[CreationRelationshipObservation, ...] = ()
    prior_runs: tuple[CreationRelationshipObservation, ...] = ()
    prior_acceptance_scope: OutcomeAcceptanceScopeRef | None = None
    lineage_decision_ref: CreationProvenanceRef | None = None

    def __post_init__(self) -> None:
        from .creation import OutcomeCreationSpec

        for value, expected in (
            (self.outcome_id, OutcomeId),
            (self.request_identity, CreationRequestIdentity),
            (self.spec, OutcomeCreationSpec),
            (self.originating_run, CreationRelationshipObservation),
            (self.task_id, TaskId),
            (self.acceptance_scope, OutcomeAcceptanceScopeRef),
            (self.proposal_ref, CreationProvenanceRef),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue("Invalid Outcome proposal scope")
        _require_tuple(self.prior_lineage)
        _require_tuple(self.prior_runs)
        if self.prior_acceptance_scope is not None and not isinstance(
            self.prior_acceptance_scope, OutcomeAcceptanceScopeRef
        ):
            raise InvalidDomainValue("Invalid prior acceptance scope")
        if self.lineage_decision_ref is not None and not isinstance(
            self.lineage_decision_ref, CreationProvenanceRef
        ):
            raise InvalidDomainValue("Invalid Outcome lineage decision reference")


@dataclass(frozen=True, slots=True)
class EvaluationRequestScope:
    evaluation_id: EvaluationId
    request_identity: CreationRequestIdentity
    spec: EvaluationCreationSpec
    validation_scope_ref: CreationProvenanceRef
    validation_policy_ref: CreationProvenanceRef
    artifact_refs: frozenset[ArtifactRef]
    evidence_refs: frozenset[EvidenceRef]
    producing_principals: tuple[ActorIdentity, ...]
    target_observation: CreationRelationshipObservation | None = None
    evidence_anchor_ref: CreationProvenanceRef | None = None
    assignment_requirement_ref: CreationProvenanceRef | None = None

    def __post_init__(self) -> None:
        from .creation import EvaluationCreationSpec

        for value, expected in (
            (self.evaluation_id, EvaluationId),
            (self.request_identity, CreationRequestIdentity),
            (self.spec, EvaluationCreationSpec),
            (self.validation_scope_ref, CreationProvenanceRef),
            (self.validation_policy_ref, CreationProvenanceRef),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue("Invalid Evaluation request scope")
        for values, reference_type in (
            (self.artifact_refs, ArtifactRef),
            (self.evidence_refs, EvidenceRef),
        ):
            if not isinstance(values, frozenset) or any(
                not isinstance(item, reference_type) for item in values
            ):
                raise InvalidDomainValue("Invalid immutable Evaluation input scope")
        if (
            not isinstance(self.producing_principals, tuple)
            or not self.producing_principals
            or any(
                not isinstance(item, ActorIdentity)
                for item in self.producing_principals
            )
        ):
            raise InvalidDomainValue(
                "Producing/executing principal provenance is required"
            )
        if self.target_observation is not None and not isinstance(
            self.target_observation, CreationRelationshipObservation
        ):
            raise InvalidDomainValue("Invalid Evaluation target observation")
        for reference in (self.evidence_anchor_ref, self.assignment_requirement_ref):
            if reference is not None and not isinstance(
                reference, CreationProvenanceRef
            ):
                raise InvalidDomainValue("Invalid Evaluation provenance reference")


@dataclass(frozen=True, slots=True)
class _CreationDecision:
    decision_ref: CreationProvenanceRef
    status: CreationSemanticDecisionStatus
    decided_by: ActorIdentity
    decided_at: Timestamp
    evidence_refs: frozenset[EvidenceRef]

    def __post_init__(self) -> None:
        for value, expected in (
            (self.decision_ref, CreationProvenanceRef),
            (self.status, CreationSemanticDecisionStatus),
            (self.decided_by, ActorIdentity),
            (self.decided_at, Timestamp),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue("Invalid creation semantic decision")
        _require_evidence(self.evidence_refs)


@dataclass(frozen=True, slots=True)
class RunRegistrationDecision(_CreationDecision):
    scope: RunRegistrationScope

    def __post_init__(self) -> None:
        _CreationDecision.__post_init__(self)
        if not isinstance(self.scope, RunRegistrationScope):
            raise InvalidDomainValue("Invalid Run decision scope")


@dataclass(frozen=True, slots=True)
class OutcomeProposalDecision(_CreationDecision):
    scope: OutcomeProposalScope

    def __post_init__(self) -> None:
        _CreationDecision.__post_init__(self)
        if not isinstance(self.scope, OutcomeProposalScope):
            raise InvalidDomainValue("Invalid Outcome decision scope")


@dataclass(frozen=True, slots=True)
class EvaluationRequestDecision(_CreationDecision):
    scope: EvaluationRequestScope

    def __post_init__(self) -> None:
        _CreationDecision.__post_init__(self)
        if not isinstance(self.scope, EvaluationRequestScope):
            raise InvalidDomainValue("Invalid Evaluation decision scope")


def require_decision(
    decision: _CreationDecision, principals: tuple[ActorIdentity, ...]
) -> None:
    require_independent(decision.decided_by, principals)
    if decision.status is not CreationSemanticDecisionStatus.PASSED:
        raise InvariantViolation("Creation semantic decision did not pass")


def validate_run_creation(request: RunPendingCreationRequest) -> RunRegistrationScope:
    semantics = request.semantic_input
    scope, decision = semantics.registration, semantics.decision
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
        scope.run_id != request.entity_id
        or scope.request_identity != identity
        or scope.spec != request.entity_spec
        or decision.scope != scope
    ):
        raise InvariantViolation(
            "Run registration decision must exact-bind request and semantic scope"
        )
    principals = (request.requested_by,)
    require_decision(decision, principals)
    task = require_current(scope.task, identity, scope.spec.task_id, principals)
    if not isinstance(task, Task) or task.state not in {
        TaskState.READY,
        TaskState.IN_PROGRESS,
    }:
        raise InvariantViolation("Run registration requires READY/IN_PROGRESS Task")
    objective = require_current(
        scope.primary_objective, identity, task.primary_objective_id, principals
    )
    if (
        not isinstance(objective, Objective)
        or objective.state is not ObjectiveState.ACTIVE
    ):
        raise InvariantViolation("Run registration requires ACTIVE primary Objective")
    expected = scope.spec.predecessor_run_id
    if expected is None:
        if (
            scope.predecessor_lineage
            or scope.lineage_decision_ref is not None
            or scope.lineage_kind is not RunCreationLineageKind.NEW_ATTEMPT
        ):
            raise InvalidRelationship(
                "New attempt must not fabricate predecessor lineage"
            )
    elif (
        scope.lineage_kind is RunCreationLineageKind.NEW_ATTEMPT
        or scope.lineage_decision_ref is None
        or not scope.predecessor_lineage
    ):
        raise InvalidRelationship(
            "Predecessor requires explicit recovery/reassignment lineage"
        )
    seen = {scope.run_id}
    for observation in scope.predecessor_lineage:
        if expected is None or expected in seen:
            raise InvalidRelationship("Run lineage is cyclic or discontinuous")
        predecessor = require_current(observation, identity, expected, principals)
        if not isinstance(predecessor, Run) or predecessor.task_id != task.task_id:
            raise InvalidRelationship("Run predecessor must belong to the same Task")
        seen.add(expected)
        expected = predecessor.predecessor_run_id
    if expected is not None:
        raise InvalidRelationship("Run predecessor lineage is incomplete")
    return scope


def validate_outcome_creation(
    request: OutcomeProposedCreationRequest,
) -> OutcomeProposalScope:
    semantics = request.semantic_input
    scope, decision = semantics.proposal, semantics.decision
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
        scope.outcome_id != request.entity_id
        or scope.request_identity != identity
        or scope.spec != request.entity_spec
        or decision.scope != scope
    ):
        raise InvariantViolation(
            "Outcome proposal decision must exact-bind request and semantic scope"
        )
    principals = (request.requested_by, scope.spec.producer)
    require_decision(decision, principals)
    run = require_current(
        scope.originating_run, identity, scope.spec.run_id, principals
    )
    if not isinstance(run, Run) or run.task_id != scope.task_id:
        raise InvalidRelationship(
            "Outcome must retain originating Run/Task relationship"
        )
    expected = scope.spec.prior_outcome_id
    if expected is None:
        if (
            scope.prior_lineage
            or scope.prior_runs
            or scope.prior_acceptance_scope is not None
            or scope.lineage_decision_ref is not None
        ):
            raise InvalidRelationship(
                "New proposal must not fabricate prior-candidate lineage"
            )
    elif (
        not scope.prior_lineage
        or scope.prior_acceptance_scope != scope.acceptance_scope
        or scope.lineage_decision_ref is None
    ):
        raise InvalidRelationship(
            "Prior Outcome requires exact common acceptance scope and lineage"
        )
    if len(scope.prior_lineage) != len(scope.prior_runs):
        raise InvalidRelationship("Every prior Outcome requires exact Run provenance")
    seen = {scope.outcome_id}
    for observation, run_observation in zip(
        scope.prior_lineage, scope.prior_runs, strict=True
    ):
        if expected is None or expected in seen:
            raise InvalidRelationship("Outcome lineage is cyclic or discontinuous")
        prior = require_current(observation, identity, expected, principals)
        if not isinstance(prior, Outcome):
            raise InvalidRelationship("Prior candidate must be an Outcome")
        prior_run = require_current(run_observation, identity, prior.run_id, principals)
        if not isinstance(prior_run, Run) or prior_run.task_id != scope.task_id:
            raise InvalidRelationship("Prior Outcome must have the same Task scope")
        seen.add(expected)
        expected = prior.prior_outcome_id
    if expected is not None:
        raise InvalidRelationship("Outcome lineage is incomplete")
    return scope


def validate_evaluation_creation(
    request: EvaluationPendingCreationRequest,
) -> EvaluationRequestScope:
    semantics = request.semantic_input
    scope, decision = semantics.validation, semantics.decision
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
        scope.evaluation_id != request.entity_id
        or scope.request_identity != identity
        or scope.spec != request.entity_spec
        or decision.scope != scope
    ):
        raise InvariantViolation(
            "Evaluation decision must exact-bind request and semantic scope"
        )
    principals = (request.requested_by,) + scope.producing_principals
    require_decision(decision, principals)
    target: EvaluationTargetRef = scope.spec.target
    if isinstance(target.reference, EvidenceRef):
        if (
            target.version is not None
            or scope.target_observation is not None
            or scope.evidence_anchor_ref is None
            or target.reference not in scope.evidence_refs
        ):
            raise InvariantViolation(
                "Evidence target requires independent unversioned anchor"
            )
    else:
        if scope.target_observation is None or scope.evidence_anchor_ref is not None:
            raise InvariantViolation("Entity target requires exact current observation")
        snapshot = require_current(
            scope.target_observation, identity, target.reference, principals
        )
        if (
            not isinstance(snapshot, (Run, Outcome, Effect))
            or snapshot.version != target.version
        ):
            raise InvariantViolation("Evaluation target version must match observation")
        if isinstance(snapshot, Outcome):
            if (
                snapshot.producer not in scope.producing_principals
                or not scope.artifact_refs.issubset(snapshot.artifact_refs)
                or not scope.evidence_refs.issubset(snapshot.evidence_refs)
            ):
                raise InvariantViolation(
                    "Evaluation must retain exact Outcome producer/input scope"
                )
        if isinstance(snapshot, Effect):
            producer = (
                snapshot.origin.proposed_by
                if isinstance(snapshot.origin, PlannedEffectOrigin)
                else snapshot.origin.observed_by
            )
            if producer not in scope.producing_principals:
                raise InvariantViolation(
                    "Evaluation must retain Effect origin principal"
                )
    verifier = scope.spec.verifier
    if verifier is None:
        if scope.assignment_requirement_ref is None:
            raise InvariantViolation(
                "Unassigned Evaluation requires explicit assignment requirement"
            )
    else:
        if verifier.actor_type is not ActorType.EVALUATOR or any(
            verifier.actor_id == actor.actor_id for actor in scope.producing_principals
        ):
            raise InvariantViolation(
                "Assigned verifier must be an independent EVALUATOR"
            )
        if scope.assignment_requirement_ref is not None:
            raise InvariantViolation(
                "Assigned Evaluation must not claim pending assignment"
            )
    return scope


def creation_scope_annotations(
    scope: RunRegistrationScope | OutcomeProposalScope | EvaluationRequestScope,
    decision: RunRegistrationDecision
    | OutcomeProposalDecision
    | EvaluationRequestDecision,
) -> frozenset[tuple[str, str]]:
    """Closed deterministic vocabulary; evidence bodies and caller metadata excluded."""
    values = [("semantic_decision_ref", decision.decision_ref.value)]
    evidence = decision.evidence_refs
    observations: list[tuple[str, CreationRelationshipObservation]] = []
    if isinstance(scope, RunRegistrationScope):
        values.extend(
            (
                ("attempt_ref", scope.attempt_ref.value),
                ("profile_selection_ref", scope.profile_selection_ref.value),
            )
        )
        observations.extend(
            (("task", scope.task), ("primary_objective", scope.primary_objective))
        )
        observations.extend(
            (f"predecessor.{index:04d}", item)
            for index, item in enumerate(scope.predecessor_lineage)
        )
        if scope.lineage_decision_ref is not None:
            values.append(("lineage_decision_ref", scope.lineage_decision_ref.value))
    elif isinstance(scope, OutcomeProposalScope):
        values.extend(
            (
                ("proposal_ref", scope.proposal_ref.value),
                ("task_id", str(scope.task_id)),
                ("acceptance_scope.id", scope.acceptance_scope.scope_id),
                ("acceptance_scope.version", scope.acceptance_scope.scope_version),
            )
        )
        observations.append(("originating_run", scope.originating_run))
        observations.extend(
            (f"prior_outcome.{index:04d}", item)
            for index, item in enumerate(scope.prior_lineage)
        )
        observations.extend(
            (f"prior_run.{index:04d}", item)
            for index, item in enumerate(scope.prior_runs)
        )
        evidence |= scope.spec.evidence_refs
        if scope.lineage_decision_ref is not None:
            values.append(("lineage_decision_ref", scope.lineage_decision_ref.value))
    else:
        values.extend(
            (
                ("validation_scope_ref", scope.validation_scope_ref.value),
                ("validation_policy_ref", scope.validation_policy_ref.value),
            )
        )
        evidence |= scope.evidence_refs
        values.extend(
            (f"artifact_ref.{index:04d}", item.value)
            for index, item in enumerate(
                sorted(scope.artifact_refs, key=lambda item: item.value)
            )
        )
        if scope.target_observation is not None:
            observations.append(("target", scope.target_observation))
        if scope.evidence_anchor_ref is not None:
            values.append(("evidence_anchor_ref", scope.evidence_anchor_ref.value))
        if scope.assignment_requirement_ref is not None:
            values.append(
                ("assignment_requirement_ref", scope.assignment_requirement_ref.value)
            )
    for prefix, observation in observations:
        assert observation.snapshot is not None
        values.extend(
            (
                (f"{prefix}.observation_ref", observation.observation_ref.value),
                (f"{prefix}.observed_version", str(observation.snapshot.version.value)),
            )
        )
        evidence |= observation.evidence_refs
    values.extend(
        (f"semantic_evidence_ref.{index:04d}", item.value)
        for index, item in enumerate(sorted(evidence, key=lambda item: item.value))
    )
    return frozenset(values)
