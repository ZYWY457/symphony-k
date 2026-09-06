"""Static-only API contracts checked by `mypy src tests`.

Targeted ignores are negative assertions: strict mypy rejects an unused ignore
if these invalid argument combinations ever become type-compatible.
"""

from typing import TYPE_CHECKING, assert_type
from uuid import UUID

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    EffectId,
    EvaluationId,
    ObjectiveId,
    OutcomeId,
    RunId,
    TaskId,
)

if TYPE_CHECKING:
    value = UUID("12345678-1234-4234-8234-123456789abc")

    def requires_objective(identity: ObjectiveId) -> ObjectiveId:
        return identity

    assert_type(ObjectiveId.new(), ObjectiveId)
    assert_type(TaskId.new(), TaskId)
    assert_type(RunId.new(), RunId)
    assert_type(OutcomeId.new(), OutcomeId)
    assert_type(EvaluationId.new(), EvaluationId)
    assert_type(EffectId.new(), EffectId)
    assert_type(ActorId.new(), ActorId)
    assert_type(ObjectiveId.from_string(str(value)), ObjectiveId)
    assert_type(requires_objective(ObjectiveId(value)), ObjectiveId)

    requires_objective(TaskId(value))  # type: ignore[arg-type]
    requires_objective(RunId(value))  # type: ignore[arg-type]
    requires_objective(OutcomeId(value))  # type: ignore[arg-type]
    requires_objective(EvaluationId(value))  # type: ignore[arg-type]
    requires_objective(EffectId(value))  # type: ignore[arg-type]
    requires_objective(ActorId(value))  # type: ignore[arg-type]
    requires_objective(value)  # type: ignore[arg-type]
    requires_objective(str(value))  # type: ignore[arg-type]
    ActorIdentity(TaskId(value), ActorType.WORKER)  # type: ignore[arg-type]
    ActorIdentity(ActorId(value), "SYSTEM")  # type: ignore[arg-type]
