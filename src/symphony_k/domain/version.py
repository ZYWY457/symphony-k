"""Immutable version values without a persistence or locking strategy."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import InvalidDomainValue


@dataclass(frozen=True, slots=True)
class EntityVersion:
    """A non-negative integer; entity creation selects its initial value later."""

    value: int

    def __post_init__(self) -> None:
        if type(self.value) is not int or self.value < 0:
            raise InvalidDomainValue("Entity version must be a non-negative integer")

    def next(self) -> EntityVersion:
        """Return an incremented value without mutating this version."""
        return EntityVersion(self.value + 1)
