"""Execution references retain opaque identity/version, not executable config."""

from dataclasses import fields, replace

import pytest

from symphony_k.domain import ExecutionProfileRef, InvalidDomainValue


def test_profile_reference_preserves_opaque_values() -> None:
    reference = ExecutionProfileRef("  profile definition\n", "not-semver")
    assert reference.profile_id == "  profile definition\n"
    assert reference.profile_version == "not-semver"
    assert reference == ExecutionProfileRef(
        reference.profile_id, reference.profile_version
    )
    assert {reference: "found"}[replace(reference)] == "found"
    assert {field.name for field in fields(reference)} == {
        "profile_id",
        "profile_version",
    }
    for name in (
        "execute",
        "resolve",
        "approved",
        "agent",
        "model",
        "sandbox",
        "permissions",
    ):
        assert not hasattr(reference, name)


@pytest.mark.parametrize("field", ["profile_id", "profile_version"])
@pytest.mark.parametrize("value", ["", " ", "\t\n", None, 0, True])
def test_invalid_profile_values_are_rejected(field: str, value: object) -> None:
    with pytest.raises(InvalidDomainValue) as caught:
        replace(ExecutionProfileRef("profile", "revision"), **{field: value})  # type: ignore[arg-type]
    assert str(caught.value) == f"{field} must contain non-whitespace text"


@pytest.mark.parametrize("field", ["profile_id", "profile_version"])
def test_profile_reference_is_immutable(field: str) -> None:
    reference = ExecutionProfileRef("profile", "revision")
    with pytest.raises(AttributeError):
        setattr(reference, field, "replacement")
    with pytest.raises(AttributeError):
        delattr(reference, field)
