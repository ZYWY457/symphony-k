"""Small opaque candidate-content references, not storage or trusted evidence."""

from dataclasses import dataclass

from .errors import InvalidDomainValue


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    """Opaque artifact identity; it neither loads content nor proves existence."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Artifact reference must contain non-whitespace text"
            )


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    """Opaque evidence identity; existence and independent validity are unproven."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Evidence reference must contain non-whitespace text"
            )
