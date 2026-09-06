"""Explicit, timezone-aware domain timestamps with canonical UTC values."""

from dataclasses import dataclass
from datetime import UTC, datetime

from .errors import InvalidDomainValue


@dataclass(frozen=True, slots=True)
class Timestamp:
    """A supplied instant normalized to UTC; no implicit wall-clock default."""

    value: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.value, datetime):
            raise InvalidDomainValue("Timestamp value must be a datetime")
        try:
            if self.value.tzinfo is None or self.value.utcoffset() is None:
                raise InvalidDomainValue("Timestamp must be timezone-aware")
            normalized = self.value.astimezone(UTC)
        except (ValueError, OverflowError, TypeError) as exc:
            raise InvalidDomainValue(
                "Timestamp must represent an aware UTC instant"
            ) from exc
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value.isoformat(timespec="microseconds")
