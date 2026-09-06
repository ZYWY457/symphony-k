"""Opaque execution-configuration references, with no runtime integration."""

from dataclasses import dataclass

from .errors import InvalidDomainValue


@dataclass(frozen=True, slots=True)
class ExecutionProfileRef:
    """A profile definition/version reference, not approval or executable config."""

    profile_id: str
    profile_version: str

    def __post_init__(self) -> None:
        for name, value in (
            ("profile_id", self.profile_id),
            ("profile_version", self.profile_version),
        ):
            if not isinstance(value, str) or not value.strip():
                raise InvalidDomainValue(f"{name} must contain non-whitespace text")
