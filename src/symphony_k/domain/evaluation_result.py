"""Immutable original verification content; no taxonomy, calibration or runtime."""

from dataclasses import dataclass

from .candidate_refs import EvidenceRef
from .errors import InvalidDomainValue


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InvalidDomainValue(f"{field} must contain non-whitespace text")


@dataclass(frozen=True, slots=True)
class EvaluationMethodRef:
    """Opaque method identity/version, not a validator or dispatch instruction."""

    method_id: str
    method_version: str

    def __post_init__(self) -> None:
        _require_text(self.method_id, "method_id")
        _require_text(self.method_version, "method_version")


@dataclass(frozen=True, slots=True)
class EvaluationVerdict:
    """Recorded judgment text with no fixed verdict taxonomy or truth authority."""

    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, "verdict")


@dataclass(frozen=True, slots=True)
class EvaluationConfidence:
    """Opaque confidence text; no numeric scale, calibration or gate is selected."""

    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, "confidence")


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """Original recorded content, never an effective/arbitrated replacement."""

    verdict: EvaluationVerdict
    confidence: EvaluationConfidence
    reasoning_summary: str
    evidence_refs: frozenset[EvidenceRef] = frozenset()

    def __post_init__(self) -> None:
        if not isinstance(self.verdict, EvaluationVerdict):
            raise InvalidDomainValue("verdict must be an EvaluationVerdict")
        if not isinstance(self.confidence, EvaluationConfidence):
            raise InvalidDomainValue("confidence must be an EvaluationConfidence")
        _require_text(self.reasoning_summary, "reasoning_summary")
        if not isinstance(self.evidence_refs, frozenset):
            raise InvalidDomainValue("evidence_refs must be a frozenset")
        if any(
            not isinstance(reference, EvidenceRef) for reference in self.evidence_refs
        ):
            raise InvalidDomainValue("Every evidence reference must be an EvidenceRef")
