"""Closed supporting-history identities and deterministic immutable traversal."""

from collections.abc import Iterator
from dataclasses import fields, is_dataclass

from symphony_k.domain.creation_effect_observation import (
    EffectCreationQuarantineContext,
)
from symphony_k.domain.effect_attribution import EffectAttributionRecord
from symphony_k.domain.effect_authorization import EffectAuthorizationFindingRecord
from symphony_k.domain.effect_execution import (
    EffectExecutionAuthorizationRecord,
    EffectPreparationRecord,
    EffectVerificationRecord,
)
from symphony_k.domain.effect_governance import EffectGovernanceFindingRecord
from symphony_k.domain.effect_incident import EffectIncidentRecord
from symphony_k.domain.effect_observation import EffectObservationRecord
from symphony_k.domain.effect_remediation import (
    EffectCompensationCompletionRecord,
    EffectCompensationPlanRecord,
    EffectRollbackRecord,
)
from symphony_k.domain.effect_semantics import (
    EffectQuarantineContext,
    EffectReconciliationRecord,
    EffectRemediationReadinessRecord,
    EffectSimulationBypassDecision,
    EffectSimulationRecord,
)
from symphony_k.domain.evaluation_arbitration import EvaluationArbitrationRecord
from symphony_k.domain.evaluation_conflict import EvaluationConflictSetRecord
from symphony_k.domain.evaluation_invalidation import EvaluationInvalidationRecord

RECORD_IDENTITIES: dict[type, str] = {
    EvaluationConflictSetRecord: "conflict_set_id",
    EvaluationArbitrationRecord: "arbitration_id",
    EvaluationInvalidationRecord: "invalidation_id",
    EffectObservationRecord: "observation_id",
    EffectAttributionRecord: "attribution_id",
    EffectAuthorizationFindingRecord: "finding_id",
    EffectGovernanceFindingRecord: "finding_id",
    EffectIncidentRecord: "record_id",
    EffectPreparationRecord: "preparation_id",
    EffectVerificationRecord: "verification_id",
    EffectExecutionAuthorizationRecord: "authorization_id",
    EffectRollbackRecord: "rollback_record_id",
    EffectCompensationPlanRecord: "plan_id",
    EffectCompensationCompletionRecord: "completion_id",
    EffectQuarantineContext: "context_id",
    EffectCreationQuarantineContext: "context_id",
    EffectReconciliationRecord: "reconciliation_id",
    EffectRemediationReadinessRecord: "readiness_id",
    EffectSimulationBypassDecision: "decision_id",
    EffectSimulationRecord: "simulation_id",
}


def walk(value: object) -> Iterator[object]:
    """Traverse immutable records, preserving complete nested provenance."""
    yield value
    if is_dataclass(value) and not isinstance(value, type):
        for field in fields(value):
            yield from walk(getattr(value, field.name))
    elif isinstance(value, (tuple, frozenset)):
        for item in value:
            yield from walk(item)


def record_key(value: object) -> tuple[str, str, int] | None:
    name = RECORD_IDENTITIES.get(type(value))
    if name is None:
        return None
    version = (
        value.version.value if isinstance(value, EvaluationConflictSetRecord) else 1
    )
    return type(value).__name__, str(getattr(value, name)), version
