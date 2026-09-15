"""Observation-only registration of external reality; no execution capability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .actors import ActorIdentity, ActorType
from .candidate_refs import EvidenceRef
from .creation_relationships import (
    CreationProvenanceRef,
    CreationRelationshipObservation,
    CreationRequestIdentity,
    require_current,
    require_independent,
)
from .creation_run_outcome_evaluation import _CreationDecision, require_decision
from .creation_semantics import _require_evidence
from .effect import EffectDeduplicationRef, EffectState
from .effect_authorization import EffectAuthorizationFindingRecord
from .effect_governance import EffectGovernanceFindingRecord
from .effect_incident import EffectIncidentRecord
from .effect_observation import EffectObservationRecord, EffectOccurrenceStatus
from .effect_semantics import EffectQuarantineReason
from .errors import InvalidDomainValue, InvalidRelationship, InvariantViolation
from .ids import EffectId, EffectIncidentRecordId, EffectQuarantineContextId
from .run import Run
from .task import Task
from .time import Timestamp
from .version import EntityVersion

if TYPE_CHECKING:
    from .creation import (
        CommittedEffectObservationCreationRequest,
        ObservedEffectCreationSpec,
        QuarantinedEffectObservationCreationRequest,
    )


@dataclass(frozen=True, slots=True)
class EffectCreationQuarantineContext:
    context_id: EffectQuarantineContextId
    reason: EffectQuarantineReason
    reconciliation_ref: CreationProvenanceRef
    evidence_refs: frozenset[EvidenceRef]
    recorded_by: ActorIdentity
    recorded_at: Timestamp
    incident_record_id: EffectIncidentRecordId | None = None

    def __post_init__(self) -> None:
        for value, expected in (
            (self.context_id, EffectQuarantineContextId),
            (self.reason, EffectQuarantineReason),
            (self.reconciliation_ref, CreationProvenanceRef),
            (self.recorded_by, ActorIdentity),
            (self.recorded_at, Timestamp),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue("Invalid creation quarantine context")
        _require_evidence(self.evidence_refs)
        if self.incident_record_id is not None and not isinstance(
            self.incident_record_id, EffectIncidentRecordId
        ):
            raise InvalidDomainValue("Invalid quarantine incident reference")


@dataclass(frozen=True, slots=True)
class ObservedEffectRegistrationScope:
    effect_id: EffectId
    request_identity: CreationRequestIdentity
    spec: ObservedEffectCreationSpec
    deduplication_ref: EffectDeduplicationRef
    observation: EffectObservationRecord
    evidence_anchor_ref: CreationProvenanceRef
    authorization_finding: EffectAuthorizationFindingRecord
    governance_findings: tuple[EffectGovernanceFindingRecord, ...] = ()
    incidents: tuple[EffectIncidentRecord, ...] = ()
    task: CreationRelationshipObservation | None = None
    run: CreationRelationshipObservation | None = None
    quarantine: EffectCreationQuarantineContext | None = None

    def __post_init__(self) -> None:
        from .creation import ObservedEffectCreationSpec

        for value, expected in (
            (self.effect_id, EffectId),
            (self.request_identity, CreationRequestIdentity),
            (self.spec, ObservedEffectCreationSpec),
            (self.deduplication_ref, EffectDeduplicationRef),
            (self.observation, EffectObservationRecord),
            (self.evidence_anchor_ref, CreationProvenanceRef),
            (self.authorization_finding, EffectAuthorizationFindingRecord),
        ):
            if not isinstance(value, expected):
                raise InvalidDomainValue("Invalid observed Effect registration scope")
        for records, record_type in (
            (self.governance_findings, EffectGovernanceFindingRecord),
            (self.incidents, EffectIncidentRecord),
        ):
            if not isinstance(records, tuple) or any(
                not isinstance(item, record_type) for item in records
            ):
                raise InvalidDomainValue(
                    "Observation findings must be immutable typed tuples"
                )
        for observation in (self.task, self.run):
            if observation is not None and not isinstance(
                observation, CreationRelationshipObservation
            ):
                raise InvalidDomainValue(
                    "Invalid observed Effect attribution observation"
                )
        if self.quarantine is not None and not isinstance(
            self.quarantine, EffectCreationQuarantineContext
        ):
            raise InvalidDomainValue("Invalid observed Effect quarantine context")


@dataclass(frozen=True, slots=True)
class ObservedEffectRegistrationDecision(_CreationDecision):
    scope: ObservedEffectRegistrationScope

    def __post_init__(self) -> None:
        _CreationDecision.__post_init__(self)
        if not isinstance(self.scope, ObservedEffectRegistrationScope):
            raise InvalidDomainValue("Invalid observation registration decision scope")


def validate_observed_effect_creation(
    request: CommittedEffectObservationCreationRequest
    | QuarantinedEffectObservationCreationRequest,
    controller: ActorIdentity,
) -> ObservedEffectRegistrationScope:
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
        scope.effect_id != request.entity_id
        or scope.spec != request.entity_spec
        or scope.request_identity != identity
        or decision.scope != scope
    ):
        raise InvariantViolation(
            "Observation registration decision must exact-bind request and bundle"
        )
    origin = scope.spec.origin
    require_decision(decision, (request.requested_by, origin.observed_by))
    require_independent(origin.observed_by, (request.requested_by,))
    record = scope.observation
    if not (
        record.effect_id == scope.effect_id
        and record.observed_effect_version == EntityVersion(1)
        and record.external_operation_ref == origin.external_operation_ref
        and record.deduplication_ref == scope.deduplication_ref
        and record.target_ref == scope.spec.target_ref
        and record.payload_ref == scope.spec.payload_ref
        and record.evidence_refs == origin.observation_evidence_refs
        and record.observed_by == origin.observed_by
        and record.observed_at == origin.observed_at
        and record.recorded_by == controller
        and record.correlation_id == request.correlation_id
        and record.prior_observation_id is None
    ):
        raise InvariantViolation(
            "Observation must exactly match immutable origin and recording scope"
        )
    if controller.actor_type is not ActorType.EFFECT_CONTROLLER:
        raise InvariantViolation(
            "Observation recorder must be the authoritative Effect Controller"
        )
    if (
        record.observed_at.value > record.recorded_at.value
        or record.recorded_at.value > request.timestamp.value
    ):
        raise InvariantViolation("Observation chronology exceeds creation event time")
    if (
        record.occurrence_at is not None
        and record.occurrence_at.value > record.observed_at.value
    ):
        raise InvariantViolation("Occurrence time cannot follow its observation")
    if request.target_state is EffectState.COMMITTED:
        if (
            record.occurrence_status is not EffectOccurrenceStatus.CONFIRMED
            or record.occurrence_at is None
            or scope.quarantine is not None
        ):
            raise InvariantViolation(
                "COMMITTED requires confirmed timed occurrence without quarantine"
            )
    else:
        if (
            record.occurrence_status is not EffectOccurrenceStatus.UNCERTAIN
            or scope.quarantine is None
        ):
            raise InvariantViolation(
                "QUARANTINED creation requires uncertain occurrence and context"
            )
        quarantine = scope.quarantine
        if (
            quarantine.reason
            is not EffectQuarantineReason.UNKNOWN_OR_SUSPECTED_OCCURRENCE
            or quarantine.recorded_by != controller
            or quarantine.recorded_at.value > request.timestamp.value
        ):
            raise InvariantViolation(
                "Quarantine context must describe suspected occurrence"
            )
        if (
            quarantine.incident_record_id is not None
            and quarantine.incident_record_id
            not in {item.record_id for item in scope.incidents}
        ):
            raise InvariantViolation(
                "Quarantine incident reference must resolve in this bundle"
            )
    findings: tuple[
        EffectAuthorizationFindingRecord
        | EffectGovernanceFindingRecord
        | EffectIncidentRecord,
        ...,
    ] = (scope.authorization_finding,) + scope.governance_findings + scope.incidents
    for finding in findings:
        if (
            finding.effect_id != scope.effect_id
            or finding.observed_effect_version != EntityVersion(1)
            or finding.correlation_id != request.correlation_id
            or finding.recorded_by != controller
        ):
            raise InvariantViolation(
                "Findings must exact-bind initial Effect recording scope"
            )
        require_independent(finding.determined_by, (request.requested_by,))
        if (
            finding.determined_at.value > finding.recorded_at.value
            or finding.recorded_at.value > request.timestamp.value
        ):
            raise InvariantViolation("Finding chronology exceeds creation event time")
        if isinstance(finding, EffectIncidentRecord):
            if finding.prior_record_id is not None:
                raise InvariantViolation(
                    "Initial incident must not fabricate prior Effect history"
                )
        elif finding.prior_finding_id is not None:
            raise InvariantViolation(
                "Initial finding must not fabricate prior Effect history"
            )
    if len({item.finding_id for item in scope.governance_findings}) != len(
        scope.governance_findings
    ) or len({item.record_id for item in scope.incidents}) != len(scope.incidents):
        raise InvariantViolation(
            "Observation bundle must not duplicate finding identities"
        )
    if origin.task_id is None:
        if scope.task is not None or scope.run is not None:
            raise InvalidRelationship(
                "Unlinked observation cannot fabricate Task/Run attribution"
            )
    else:
        if scope.task is None:
            raise InvalidRelationship(
                "Known Task attribution requires current observation"
            )
        task = require_current(
            scope.task, identity, origin.task_id, (request.requested_by,)
        )
        if not isinstance(task, Task):
            raise InvalidRelationship("Attributed entity must be a Task")
        if origin.run_id is None:
            if scope.run is not None:
                raise InvalidRelationship("Unattributed Run cannot supply ownership")
        else:
            if scope.run is None:
                raise InvalidRelationship(
                    "Known Run attribution requires current observation"
                )
            run = require_current(
                scope.run, identity, origin.run_id, (request.requested_by,)
            )
            if not isinstance(run, Run) or run.task_id != task.task_id:
                raise InvalidRelationship(
                    "Observed Effect Run must belong to attributed Task"
                )
    return scope


def observed_effect_annotations(
    scope: ObservedEffectRegistrationScope, decision: ObservedEffectRegistrationDecision
) -> frozenset[tuple[str, str]]:
    values = [
        ("semantic_decision_ref", decision.decision_ref.value),
        ("observation_ref", str(scope.observation.observation_id)),
        ("evidence_anchor_ref", scope.evidence_anchor_ref.value),
        ("external_operation_ref", scope.observation.external_operation_ref.value),
        ("deduplication_ref", scope.deduplication_ref.value),
        ("authorization_finding_ref", str(scope.authorization_finding.finding_id)),
    ]
    evidence = (
        decision.evidence_refs
        | scope.observation.evidence_refs
        | scope.authorization_finding.evidence_refs
    )
    for index, finding in enumerate(
        sorted(scope.governance_findings, key=lambda item: str(item.finding_id))
    ):
        values.append((f"governance_finding_ref.{index:04d}", str(finding.finding_id)))
        evidence |= finding.evidence_refs
    for index, incident in enumerate(
        sorted(scope.incidents, key=lambda item: str(item.record_id))
    ):
        values.append((f"incident_record_ref.{index:04d}", str(incident.record_id)))
        evidence |= incident.evidence_refs
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
    if scope.quarantine is not None:
        values.extend(
            (
                ("quarantine_context_ref", str(scope.quarantine.context_id)),
                ("reconciliation_ref", scope.quarantine.reconciliation_ref.value),
            )
        )
        evidence |= scope.quarantine.evidence_refs
    values.extend(
        (f"semantic_evidence_ref.{index:04d}", item.value)
        for index, item in enumerate(sorted(evidence, key=lambda item: item.value))
    )
    return frozenset(values)
