"""Artifact and evidence references are distinct opaque values, not loaders."""

from dataclasses import fields

import pytest

from symphony_k.domain import ArtifactRef, EvidenceRef, InvalidDomainValue


@pytest.mark.parametrize("reference_type", [ArtifactRef, EvidenceRef])
def test_reference_preserves_text_without_selecting_a_storage_format(
    reference_type: type[ArtifactRef] | type[EvidenceRef],
) -> None:
    text = "  opaque supplied identity / not a URI\n"
    reference = reference_type(text)
    assert reference.value == text
    assert {field.name for field in fields(reference)} == {"value"}
    assert {reference: "found"}[reference_type(text)] == "found"
    assert reference != reference_type("other")
    for name in ("load", "read", "exists", "verify", "digest", "serialize", "trusted"):
        assert not hasattr(reference, name)
    with pytest.raises(AttributeError):
        reference.value = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("reference_type", [ArtifactRef, EvidenceRef])
@pytest.mark.parametrize("invalid", ["", " ", "\t\n", None, 1, True])
def test_invalid_reference_values_are_rejected(
    reference_type: type[ArtifactRef] | type[EvidenceRef], invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        reference_type(invalid)  # type: ignore[arg-type]


def test_artifact_and_evidence_have_distinct_runtime_identity() -> None:
    artifact = ArtifactRef("same identity text")
    evidence = EvidenceRef("same identity text")
    assert len({artifact, evidence}) == 2
    with pytest.raises(InvalidDomainValue):
        ArtifactRef(evidence)  # type: ignore[arg-type]
    with pytest.raises(InvalidDomainValue):
        EvidenceRef(artifact)  # type: ignore[arg-type]
