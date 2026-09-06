"""The shared policy reference keeps its existing API and value semantics."""

from dataclasses import fields, replace

import pytest

from symphony_k.domain import CompletionPolicyRef, InvalidDomainValue
from symphony_k.domain.completion import CompletionPolicyRef as SharedRef
from symphony_k.domain.objective import CompletionPolicyRef as ObjectiveModuleRef


def test_public_and_previous_module_imports_share_one_type() -> None:
    assert CompletionPolicyRef is SharedRef
    assert ObjectiveModuleRef is SharedRef
    assert [field.name for field in fields(CompletionPolicyRef)] == [
        "policy_id",
        "policy_version",
    ]


def test_reference_value_semantics_are_unchanged() -> None:
    reference = SharedRef("  opaque policy definition\n", "not-semver")
    assert reference.policy_id == "  opaque policy definition\n"
    assert reference.policy_version == "not-semver"
    assert reference == ObjectiveModuleRef(
        reference.policy_id, reference.policy_version
    )
    assert {reference: "found"}[replace(reference)] == "found"
    with pytest.raises(AttributeError):
        reference.policy_version = "changed"  # type: ignore[misc]
    assert not hasattr(reference, "evaluate")
    assert not hasattr(reference, "policy_passed")


@pytest.mark.parametrize("field", ["policy_id", "policy_version"])
@pytest.mark.parametrize("invalid", ["", " ", "\t\n", None, 1, True])
def test_validation_type_and_messages_are_preserved(
    field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue) as caught:
        replace(SharedRef("definition", "revision"), **{field: invalid})  # type: ignore[arg-type]
    assert str(caught.value) == f"{field} must contain non-whitespace text"
