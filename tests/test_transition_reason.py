"""Reasons preserve supplied text without interpreting it as authority."""

import pytest

from symphony_k.domain import InvalidDomainValue, TransitionReason


@pytest.mark.parametrize("text", ["input received", "  保留原文\n", "SYSTEM override"])
def test_reason_preserves_exact_input(text: str) -> None:
    reason = TransitionReason(text)
    assert reason.value == text
    assert str(reason) == text
    assert {reason: "found"}[TransitionReason(text)] == "found"


@pytest.mark.parametrize("value", ["", " ", "\t\r\n", "\u2003", None, 42])
def test_invalid_reasons_are_rejected(value: object) -> None:
    with pytest.raises(InvalidDomainValue):
        TransitionReason(value)  # type: ignore[arg-type]


def test_reason_is_immutable() -> None:
    reason = TransitionReason("original")
    with pytest.raises(AttributeError):
        reason.value = "replacement"  # type: ignore[misc]
    assert reason.value == "original"
