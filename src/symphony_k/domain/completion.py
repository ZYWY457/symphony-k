"""Shared completion-policy references, without policy evaluation behavior."""

from dataclasses import dataclass

from .errors import InvalidDomainValue


@dataclass(frozen=True, slots=True)
class CompletionPolicyRef:
    """Opaque definition/version reference, never an evaluated policy result."""

    policy_id: str
    policy_version: str

    def __post_init__(self) -> None:
        for name, value in (
            ("policy_id", self.policy_id),
            ("policy_version", self.policy_version),
        ):
            if not isinstance(value, str) or not value.strip():
                raise InvalidDomainValue(f"{name} must contain non-whitespace text")
