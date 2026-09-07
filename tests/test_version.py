"""Version validation without assigning entity defaults or implementing locks."""

import pytest

from symphony_k.domain import ConflictSetVersion, EntityVersion, InvalidDomainValue


@pytest.mark.parametrize("value", [0, 1, 17, 2**100])
def test_non_negative_versions_and_pure_increment(value: int) -> None:
    version = EntityVersion(value)
    following = version.next()
    assert following == EntityVersion(value + 1)
    assert following is not version
    assert version.value == value
    assert {version: "found"}[EntityVersion(value)] == "found"


@pytest.mark.parametrize("value", [-1, -100, True, False, 1.0, "1", None])
def test_invalid_versions_are_rejected(value: object) -> None:
    with pytest.raises(InvalidDomainValue):
        EntityVersion(value)  # type: ignore[arg-type]


def test_version_is_immutable() -> None:
    version = EntityVersion(0)
    with pytest.raises(AttributeError):
        version.value = 1  # type: ignore[misc]
    assert version.value == 0


@pytest.mark.parametrize("value", [0, 1, 17, 2**100])
def test_conflict_set_version_is_explicit_and_non_negative(value: int) -> None:
    version = ConflictSetVersion(value)
    assert version.value == value
    assert {version: "found"}[ConflictSetVersion(value)] == "found"
    assert version != EntityVersion(value)  # type: ignore[comparison-overlap]
    assert not hasattr(version, "next")


@pytest.mark.parametrize("value", [-1, -100, True, False, 1.0, "1", None])
def test_invalid_conflict_set_versions_are_rejected(value: object) -> None:
    with pytest.raises(InvalidDomainValue):
        ConflictSetVersion(value)  # type: ignore[arg-type]


def test_conflict_set_version_is_immutable() -> None:
    version = ConflictSetVersion(37)
    with pytest.raises(AttributeError):
        version.value = 38  # type: ignore[misc]
    assert version.value == 37
