"""Deterministic supplied instants, normalized to UTC without clock defaults."""

from datetime import UTC, datetime, timedelta, timezone, tzinfo

import pytest

from symphony_k.domain import InvalidDomainValue, Timestamp

INSTANT = datetime(2026, 9, 6, 0, 15, 30, 123456, tzinfo=UTC)


@pytest.mark.parametrize("offset", [0, 8, -7])
def test_aware_instants_normalize_and_round_trip(offset: int) -> None:
    supplied = INSTANT.astimezone(timezone(timedelta(hours=offset)))
    timestamp = Timestamp(supplied)
    assert timestamp.value == INSTANT
    assert timestamp.value.tzinfo is UTC
    assert str(timestamp) == "2026-09-06T00:15:30.123456+00:00"
    assert Timestamp(datetime.fromisoformat(str(timestamp))) == timestamp
    assert {timestamp: "instant"}[Timestamp(INSTANT)] == "instant"
    assert supplied.utcoffset() == timedelta(hours=offset)


def test_zero_microseconds_have_a_stable_string_form() -> None:
    assert str(Timestamp(INSTANT.replace(microsecond=0))).endswith(".000000+00:00")


class UnknownOffset(tzinfo):
    def utcoffset(self, dt: datetime | None) -> None:
        return None

    def dst(self, dt: datetime | None) -> None:
        return None

    def tzname(self, dt: datetime | None) -> None:
        return None


@pytest.mark.parametrize(
    "value",
    [INSTANT.replace(tzinfo=None), INSTANT.replace(tzinfo=UnknownOffset())],
)
def test_naive_instants_are_rejected_even_with_a_tzinfo_object(value: datetime) -> None:
    with pytest.raises(InvalidDomainValue):
        Timestamp(value)


@pytest.mark.parametrize("value", [None, "2026-09-06T00:15:30+00:00", 0])
def test_non_datetimes_are_rejected(value: object) -> None:
    with pytest.raises(InvalidDomainValue):
        Timestamp(value)  # type: ignore[arg-type]


def test_unrepresentable_utc_normalization_is_rejected() -> None:
    with pytest.raises(InvalidDomainValue):
        Timestamp(datetime.min.replace(tzinfo=timezone(timedelta(hours=1))))


def test_timestamp_is_immutable() -> None:
    timestamp = Timestamp(INSTANT)
    with pytest.raises(AttributeError):
        timestamp.value = INSTANT + timedelta(days=1)  # type: ignore[misc]
    assert timestamp.value == INSTANT
