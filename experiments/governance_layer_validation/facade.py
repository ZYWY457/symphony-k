"""Thin, experimental trust boundary over the accepted Stage 1 kernel.

This is deliberately not a proposed public API.  Callers still have to build
Stage 1 request/context objects.  Opaque ports model an authenticated launch
boundary; actor labels inside caller-supplied data are never capabilities.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import cast

from symphony_k.domain import (
    ActorIdentity,
    ActorType,
    CorrelationId,
    CreationContext,
    CreationRequest,
    Effect,
    EffectId,
    EffectPayloadRef,
    EffectState,
    EffectTargetRef,
    EntityVersion,
    EvaluationPendingCreationRequest,
    OutcomeProposedCreationRequest,
    PlannedEffectCreationRequest,
    TransitionContext,
    TransitionRequest,
    UnauthorizedTransition,
)
from symphony_k.domain.transition_engine import (
    LifecycleEntity,
    LifecycleEntityId,
    LifecycleState,
    TransitionResult,
)
from symphony_k.persistence.service import LifecycleService
from symphony_k.persistence.sqlite import SQLiteStore


class AuthorityLane(Enum):
    WORKER = "worker"
    EVALUATOR = "evaluator"
    DISPOSITION = "disposition"
    EFFECT_GATEWAY = "effect_gateway"


@dataclass(frozen=True, slots=True)
class Port:
    """Unforgeable-by-value capability issued by the integration boundary."""

    lane: AuthorityLane
    _secret: object


@dataclass(frozen=True, slots=True)
class HumanAuthorization:
    effect_id: EffectId
    effect_version: EntityVersion
    target_ref: EffectTargetRef
    payload_ref: EffectPayloadRef | None
    correlation_id: CorrelationId
    authorized_by: ActorIdentity
    evidence_ref: str

    def __post_init__(self) -> None:
        if self.authorized_by.actor_type is not ActorType.HUMAN_OPERATOR:
            raise UnauthorizedTransition("Sensitive Effect requires Human authority")
        if not self.evidence_ref.strip():
            raise ValueError("Human authorization evidence_ref must not be blank")


@dataclass(frozen=True, slots=True)
class ExternalReceipt:
    operation_key: str
    target: str
    payload: str | None


class FakeExternalSystem:
    """Independent state: intentionally outside Symphony-K persistence."""

    def __init__(self) -> None:
        self._receipts: dict[str, ExternalReceipt] = {}
        self._state: dict[str, str | None] = {}

    def commit(
        self,
        operation_key: str,
        target: EffectTargetRef,
        payload: EffectPayloadRef | None,
    ) -> ExternalReceipt:
        prior = self._receipts.get(operation_key)
        value = None if payload is None else payload.value
        if prior is not None:
            if prior.target != target.value or prior.payload != value:
                raise UnauthorizedTransition("Idempotency key was rebound")
            return prior
        receipt = ExternalReceipt(operation_key, target.value, value)
        self._state[target.value] = value
        self._receipts[operation_key] = receipt
        return receipt

    def state(self, target: str) -> str | None:
        return self._state.get(target)


class GovernanceFacade:
    """Four-operation experimental facade; no production API commitment."""

    def __init__(self, store: SQLiteStore, ports: tuple[Port, ...]) -> None:
        self._store = store
        self._service = LifecycleService(store)
        self._ports = {port.lane: port for port in ports}
        store._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS strategic_integration_records (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                payload TEXT NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS strategic_records_no_update
            BEFORE UPDATE ON strategic_integration_records
            BEGIN SELECT RAISE(ABORT, 'append-only strategic history'); END;
            CREATE TRIGGER IF NOT EXISTS strategic_records_no_delete
            BEFORE DELETE ON strategic_integration_records
            BEGIN SELECT RAISE(ABORT, 'append-only strategic history'); END;
            """
        )

    def submit_creation(
        self, port: Port, request: CreationRequest, context: CreationContext
    ) -> TransitionResult[LifecycleEntity]:
        lane = self._lane(port)
        allowed = (
            lane is AuthorityLane.WORKER
            and isinstance(
                request, (OutcomeProposedCreationRequest, PlannedEffectCreationRequest)
            )
        ) or (
            lane is AuthorityLane.EVALUATOR
            and isinstance(request, EvaluationPendingCreationRequest)
        )
        if not allowed:
            raise UnauthorizedTransition("Port cannot submit this creation variant")
        return self._service.create(request, context)

    def apply_transition(
        self,
        port: Port,
        entity_id: LifecycleEntityId,
        request: TransitionRequest[LifecycleState],
        context: TransitionContext,
    ) -> TransitionResult[LifecycleEntity]:
        lane = self._lane(port)
        current = self._store.load(entity_id)
        if lane is AuthorityLane.WORKER:
            raise UnauthorizedTransition("Worker port has no lifecycle authority")
        if lane is AuthorityLane.EVALUATOR and type(current).__name__ != "Evaluation":
            raise UnauthorizedTransition("Evaluator port is Evaluation-scoped")
        if lane is AuthorityLane.DISPOSITION and type(current).__name__ != "Outcome":
            raise UnauthorizedTransition("Disposition port is Outcome-scoped")
        if lane is AuthorityLane.EFFECT_GATEWAY and not isinstance(current, Effect):
            raise UnauthorizedTransition("Effect gateway is Effect-scoped")
        if (
            isinstance(current, Effect)
            and request.target_state is EffectState.COMMITTED
        ):
            raise UnauthorizedTransition("Use commit_effect for external occurrence")
        return self._service.transition(entity_id, request, context)

    def commit_effect(
        self,
        port: Port,
        external: FakeExternalSystem,
        authorization: HumanAuthorization | None,
        operation_key: str,
        request: TransitionRequest[EffectState],
        context: TransitionContext,
    ) -> TransitionResult[LifecycleEntity]:
        if self._lane(port) is not AuthorityLane.EFFECT_GATEWAY:
            raise UnauthorizedTransition("Only the trusted Effect gateway can commit")
        if authorization is None:
            raise UnauthorizedTransition("Human authorization is required")
        current = cast(Effect, self._store.load(authorization.effect_id))
        if not (
            current.version == authorization.effect_version
            and current.target_ref == authorization.target_ref
            and current.payload_ref == authorization.payload_ref
            and request.expected_version == authorization.effect_version
            and request.correlation_id == authorization.correlation_id
            and request.target_state is EffectState.COMMITTED
        ):
            raise UnauthorizedTransition("Human authorization is not exact-current")
        receipt = external.commit(
            operation_key, current.target_ref, current.payload_ref
        )
        result = self._service.transition(current.effect_id, request, context)
        self._record_integration(
            "human_authorization",
            {
                "effect_id": str(current.effect_id),
                "effect_version": str(current.version.value),
                "authorized_by": str(authorization.authorized_by.actor_id),
                "evidence_ref": authorization.evidence_ref,
            },
        )
        self._record_integration(
            "external_receipt",
            {
                "effect_id": str(current.effect_id),
                "operation_key": receipt.operation_key,
                "target": receipt.target,
                "payload": receipt.payload or "",
            },
        )
        return result

    def export_audit(
        self, port: Port, entity_id: LifecycleEntityId
    ) -> dict[str, object]:
        self._lane(port)
        events = self._store.events.for_entity(entity_id)
        return {
            "entity_id": str(entity_id),
            "events": [
                {
                    "event_id": str(event.event_id),
                    "event_type": event.event_type.value,
                    "version": event.entity_version.value,
                    "actor_type": event.actor.actor_type.value,
                    "correlation_id": str(event.correlation_id),
                    "annotations": dict(event.metadata.annotations),
                }
                for event in events
            ],
            "integration_records": tuple(
                {"kind": kind, **json.loads(payload)}
                for kind, payload in self._store._connection.execute(
                    "SELECT kind,payload FROM strategic_integration_records "
                    "ORDER BY sequence"
                )
            ),
        }

    def _record_integration(self, kind: str, payload: dict[str, str]) -> None:
        self._store._connection.execute(
            "INSERT INTO strategic_integration_records(kind,payload) VALUES (?,?)",
            (kind, json.dumps(payload, sort_keys=True, separators=(",", ":"))),
        )

    def _lane(self, port: Port) -> AuthorityLane:
        issued = self._ports.get(port.lane)
        if issued is None or issued._secret is not port._secret:
            raise UnauthorizedTransition("Unknown or forged authority port")
        return port.lane


def issue_test_ports() -> tuple[Port, Port, Port, Port]:
    """Trusted-launch fixture. Individual actors receive only their own port."""
    return tuple(Port(lane, object()) for lane in AuthorityLane)  # type: ignore[return-value]
