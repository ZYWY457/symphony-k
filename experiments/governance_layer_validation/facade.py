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
    Evaluation,
    EvaluationArbitrationRecord,
    EvaluationId,
    EvaluationPendingCreationRequest,
    EvaluationState,
    Outcome,
    OutcomeEvaluationEffectiveUseObservation,
    OutcomeId,
    OutcomeProposedCreationRequest,
    OutcomeState,
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
from symphony_k.persistence._records import walk
from symphony_k.persistence.codec import decode
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
class AuthorizationEvidenceBinding:
    binding_id: str
    effect_id: str
    effect_version: int
    authorized_by: str
    outcome_id: str
    outcome_version: int
    disposition_event_id: str
    evaluation_id: str
    evaluation_version: int
    effective_judgement: str
    evidence_refs: tuple[str, ...]
    arbitration_ids: tuple[str, ...]


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
            CREATE TABLE IF NOT EXISTS strategic_authorization_bindings (
                binding_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS strategic_bindings_no_update
            BEFORE UPDATE ON strategic_authorization_bindings
            BEGIN SELECT RAISE(ABORT, 'append-only authorization binding'); END;
            CREATE TRIGGER IF NOT EXISTS strategic_bindings_no_delete
            BEFORE DELETE ON strategic_authorization_bindings
            BEGIN SELECT RAISE(ABORT, 'append-only authorization binding'); END;
            """
        )

    def bind_authorization_evidence(
        self,
        port: Port,
        authorization: HumanAuthorization,
        outcome_id: OutcomeId,
        evaluation_id: EvaluationId,
    ) -> AuthorizationEvidenceBinding:
        """Persist an exact experimental authorization-to-judgment binding."""
        if self._lane(port) is not AuthorityLane.EFFECT_GATEWAY:
            raise UnauthorizedTransition("Only the trusted Effect gateway can bind")
        binding = self._derive_authorization_binding(
            authorization, outcome_id, evaluation_id
        )
        payload = json.dumps(
            {
                field: getattr(binding, field)
                for field in AuthorizationEvidenceBinding.__dataclass_fields__
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        with self._store._transaction():
            self._store._connection.execute(
                "INSERT INTO strategic_authorization_bindings(binding_id,payload) "
                "VALUES (?,?)",
                (binding.binding_id, payload),
            )
            self._record_integration(
                "authorization_evidence_binding",
                {
                    "binding_id": binding.binding_id,
                    "effect_id": binding.effect_id,
                    "effect_version": str(binding.effect_version),
                    "authorized_by": binding.authorized_by,
                    "outcome_id": binding.outcome_id,
                    "outcome_version": str(binding.outcome_version),
                    "disposition_event_id": binding.disposition_event_id,
                    "evaluation_id": binding.evaluation_id,
                    "evaluation_version": str(binding.evaluation_version),
                    "effective_judgement": binding.effective_judgement,
                    "evidence_refs": ",".join(binding.evidence_refs),
                    "arbitration_ids": ",".join(binding.arbitration_ids),
                },
            )
        return binding

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
        binding = self._load_authorization_binding(authorization.evidence_ref)
        expected = self._derive_authorization_binding(
            authorization,
            OutcomeId.from_string(binding.outcome_id),
            EvaluationId.from_string(binding.evaluation_id),
        )
        if binding != expected:
            raise UnauthorizedTransition(
                "Human authorization evidence binding is not exact-current"
            )
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
                "disposition_event_id": binding.disposition_event_id,
                "evaluation_id": binding.evaluation_id,
                "evaluation_version": str(binding.evaluation_version),
                "effective_judgement": binding.effective_judgement,
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
            "authorization_bindings": tuple(
                json.loads(payload)
                for (payload,) in self._store._connection.execute(
                    "SELECT payload FROM strategic_authorization_bindings "
                    "ORDER BY binding_id"
                )
            ),
        }

    def _record_integration(self, kind: str, payload: dict[str, str]) -> None:
        self._store._connection.execute(
            "INSERT INTO strategic_integration_records(kind,payload) VALUES (?,?)",
            (kind, json.dumps(payload, sort_keys=True, separators=(",", ":"))),
        )

    def _load_authorization_binding(
        self, binding_id: str
    ) -> AuthorizationEvidenceBinding:
        row = self._store._connection.execute(
            "SELECT payload FROM strategic_authorization_bindings WHERE binding_id=?",
            (binding_id,),
        ).fetchone()
        if row is None:
            raise UnauthorizedTransition(
                "Human authorization lacks a trusted evidence binding"
            )
        payload = json.loads(row[0])
        payload["evidence_refs"] = tuple(payload["evidence_refs"])
        payload["arbitration_ids"] = tuple(payload["arbitration_ids"])
        return AuthorizationEvidenceBinding(**payload)

    def _derive_authorization_binding(
        self,
        authorization: HumanAuthorization,
        outcome_id: OutcomeId,
        evaluation_id: EvaluationId,
    ) -> AuthorizationEvidenceBinding:
        if not isinstance(outcome_id, OutcomeId) or not isinstance(
            evaluation_id, EvaluationId
        ):
            raise UnauthorizedTransition("Binding identities are not exact domain IDs")
        effect = self._store.load(authorization.effect_id)
        outcome = self._store.load(outcome_id)
        evaluation = self._store.load(evaluation_id)
        if not isinstance(effect, Effect) or not (
            effect.version == authorization.effect_version
            and effect.target_ref == authorization.target_ref
            and effect.payload_ref == authorization.payload_ref
        ):
            raise UnauthorizedTransition("Binding Effect is not exact-current")
        if (
            not isinstance(outcome, Outcome)
            or outcome.state is not OutcomeState.ACCEPTED
        ):
            raise UnauthorizedTransition("Binding requires an accepted Outcome")
        if not isinstance(evaluation, Evaluation) or evaluation.state not in {
            EvaluationState.COMPLETED,
            EvaluationState.ARBITRATED,
        }:
            raise UnauthorizedTransition("Binding requires an effective Evaluation")
        if evaluation.result is None or not evaluation.result.evidence_refs:
            raise UnauthorizedTransition(
                "Binding requires persisted Evaluation evidence"
            )
        events = self._store.events.for_entity(outcome.outcome_id)
        disposition = events[-1]
        if (
            disposition.entity_version != outcome.version
            or disposition.metadata.new_state is not OutcomeState.ACCEPTED
        ):
            raise UnauthorizedTransition("Accepted disposition event is not current")
        row = self._store._connection.execute(
            "SELECT provenance FROM operations WHERE event_id=?",
            (str(disposition.event_id),),
        ).fetchone()
        if row is None:
            raise UnauthorizedTransition("Disposition operation provenance is absent")
        observations = tuple(
            item
            for item in walk(decode(row[0]))
            if isinstance(item, OutcomeEvaluationEffectiveUseObservation)
        )
        observation = next(
            (
                item
                for item in observations
                if item.evaluation_id == evaluation.evaluation_id
                and item.observed_evaluation_version == evaluation.version
                and item.observed_state == evaluation.state
                and item.target == evaluation.target
                and item.verifier == evaluation.verifier
                and item.effective_use.eligible_for_effective_use
            ),
            None,
        )
        if observation is None:
            raise UnauthorizedTransition(
                "Disposition does not use the exact persisted Evaluation"
            )
        arbitration_ids = tuple(
            sorted(
                str(item.value)
                for item in observation.effective_use.supporting_arbitration_ids
            )
        )
        durable_arbitrations = {
            str(item.arbitration_id.value)
            for item in self._store.supporting_records(EvaluationArbitrationRecord)
        }
        if not set(arbitration_ids) <= durable_arbitrations:
            raise UnauthorizedTransition("Effective arbitration is not durable")
        effective_judgement = observation.effective_use.effective_judgement
        assert effective_judgement is not None
        return AuthorizationEvidenceBinding(
            authorization.evidence_ref,
            str(effect.effect_id),
            effect.version.value,
            str(authorization.authorized_by.actor_id),
            str(outcome.outcome_id),
            outcome.version.value,
            str(disposition.event_id),
            str(evaluation.evaluation_id),
            evaluation.version.value,
            effective_judgement.value,
            tuple(sorted(item.value for item in evaluation.result.evidence_refs)),
            arbitration_ids,
        )

    def _lane(self, port: Port) -> AuthorityLane:
        issued = self._ports.get(port.lane)
        if issued is None or issued._secret is not port._secret:
            raise UnauthorizedTransition("Unknown or forged authority port")
        return port.lane


def issue_test_ports() -> tuple[Port, Port, Port, Port]:
    """Trusted-launch fixture. Individual actors receive only their own port."""
    return tuple(Port(lane, object()) for lane in AuthorityLane)  # type: ignore[return-value]
