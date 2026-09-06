"""Transition reason values only; no lifecycle or transition behavior."""

from dataclasses import dataclass

from .errors import InvalidDomainValue


@dataclass(frozen=True, slots=True)
class TransitionReason:
    """Meaningful caller-supplied text, preserved exactly and granting no authority."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidDomainValue(
                "Transition reason must contain non-whitespace text"
            )

    def __str__(self) -> str:
        return self.value
