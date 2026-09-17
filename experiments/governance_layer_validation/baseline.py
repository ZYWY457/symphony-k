"""Fair small application-level comparison baseline for Issue #85."""

from __future__ import annotations

from dataclasses import dataclass, replace
from threading import Lock


class BaselineRejection(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class Candidate:
    candidate_id: str
    version: int
    producer: str
    payload: str
    state: str = "PROPOSED"


@dataclass(frozen=True, slots=True)
class Evaluation:
    evaluation_id: str
    candidate_id: str
    candidate_version: int
    evaluator: str
    verdict: str
    evidence: str


@dataclass(frozen=True, slots=True)
class Approval:
    effect_id: str
    effect_version: int
    target: str
    payload: str
    authorized_by: str
    correlation: str


@dataclass(frozen=True, slots=True)
class Effect:
    effect_id: str
    version: int
    target: str
    payload: str
    state: str = "PLANNED"
    occurred: bool = False
    compensated: bool = False


class BaselineService:
    """Competent bounded service: exact checks, CAS and append-only-by-API log."""

    def __init__(self) -> None:
        self._candidates: dict[str, Candidate] = {}
        self._evaluations: dict[str, Evaluation] = {}
        self._effects: dict[str, Effect] = {}
        self._events: list[dict[str, object]] = []
        self._committed_keys: dict[str, tuple[str, str]] = {}
        self._lock = Lock()

    def record_candidate(self, candidate: Candidate) -> Candidate:
        with self._lock:
            if candidate.candidate_id in self._candidates:
                raise BaselineRejection("candidate identity already exists")
            self._candidates[candidate.candidate_id] = candidate
            self._append(
                "candidate_recorded", candidate.candidate_id, candidate.version
            )
            return candidate

    def revise_candidate(
        self, candidate_id: str, expected: int, payload: str
    ) -> Candidate:
        with self._lock:
            current = self._candidate(candidate_id)
            self._require_version(current.version, expected)
            revised = replace(current, version=current.version + 1, payload=payload)
            self._candidates[candidate_id] = revised
            self._append("candidate_revised", candidate_id, revised.version)
            return revised

    def record_evaluation(self, evaluation: Evaluation) -> Evaluation:
        with self._lock:
            current = self._candidate(evaluation.candidate_id)
            if evaluation.evaluator == current.producer:
                raise BaselineRejection("producer cannot evaluate own candidate")
            self._require_version(current.version, evaluation.candidate_version)
            if evaluation.evaluation_id in self._evaluations:
                raise BaselineRejection("evaluation identity already exists")
            self._evaluations[evaluation.evaluation_id] = evaluation
            self._append(
                "evaluation_recorded", evaluation.candidate_id, current.version
            )
            return evaluation

    def dispose(
        self,
        candidate_id: str,
        expected: int,
        evaluation_id: str,
        actor: str,
        disposition: str,
    ) -> Candidate:
        with self._lock:
            current = self._candidate(candidate_id)
            self._require_version(current.version, expected)
            evaluation = self._evaluations.get(evaluation_id)
            if evaluation is None or (
                evaluation.candidate_id != candidate_id
                or evaluation.candidate_version != current.version
            ):
                raise BaselineRejection("evaluation is not exact-current")
            if actor == current.producer:
                raise BaselineRejection("producer cannot dispose own candidate")
            if disposition not in {"ACCEPTED", "REJECTED"}:
                raise BaselineRejection("invalid disposition")
            updated = replace(current, version=current.version + 1, state=disposition)
            self._candidates[candidate_id] = updated
            self._append("candidate_disposed", candidate_id, updated.version)
            return updated

    def request_effect(self, effect: Effect) -> Effect:
        with self._lock:
            if effect.effect_id in self._effects:
                raise BaselineRejection("effect identity already exists")
            self._effects[effect.effect_id] = effect
            self._append("effect_requested", effect.effect_id, effect.version)
            return effect

    def commit_effect(
        self, effect_id: str, expected: int, approval: Approval | None, key: str
    ) -> Effect:
        with self._lock:
            current = self._effect(effect_id)
            self._require_version(current.version, expected)
            if approval is None or (
                approval.effect_id != effect_id
                or approval.effect_version != current.version
                or approval.target != current.target
                or approval.payload != current.payload
                or not approval.authorized_by.startswith("human:")
            ):
                raise BaselineRejection("missing or non-exact Human authorization")
            prior = self._committed_keys.get(key)
            operation = (current.target, current.payload)
            if prior is not None and prior != operation:
                raise BaselineRejection("replayed key changed operation")
            self._committed_keys[key] = operation
            committed = replace(
                current,
                version=current.version + 1,
                state="COMMITTED",
                occurred=True,
            )
            self._effects[effect_id] = committed
            self._append("effect_committed", effect_id, committed.version)
            return committed

    def compensate(self, effect_id: str, expected: int) -> Effect:
        with self._lock:
            current = self._effect(effect_id)
            self._require_version(current.version, expected)
            if not current.occurred or current.state != "COMMITTED":
                raise BaselineRejection(
                    "only a committed occurrence can be compensated"
                )
            result = replace(
                current,
                version=current.version + 1,
                state="COMPENSATED",
                compensated=True,
            )
            self._effects[effect_id] = result
            self._append("effect_compensated", effect_id, result.version)
            return result

    def audit(self) -> tuple[dict[str, object], ...]:
        return tuple(dict(event) for event in self._events)

    def effect(self, effect_id: str) -> Effect:
        return self._effect(effect_id)

    def _append(self, kind: str, entity_id: str, version: int) -> None:
        self._events.append(
            {
                "sequence": len(self._events) + 1,
                "kind": kind,
                "entity_id": entity_id,
                "version": version,
            }
        )

    def _candidate(self, candidate_id: str) -> Candidate:
        try:
            return self._candidates[candidate_id]
        except KeyError as exc:
            raise BaselineRejection("unknown candidate") from exc

    def _effect(self, effect_id: str) -> Effect:
        try:
            return self._effects[effect_id]
        except KeyError as exc:
            raise BaselineRejection("unknown effect") from exc

    @staticmethod
    def _require_version(current: int, expected: int) -> None:
        if current != expected:
            raise BaselineRejection("stale version")
