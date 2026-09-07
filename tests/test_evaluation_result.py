"""Original method/judgment content stays immutable and uninterpreted."""

from dataclasses import fields, replace

import pytest

from symphony_k.domain import (
    ArtifactRef,
    EvaluationConfidence,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationVerdict,
    EvidenceRef,
    InvalidDomainValue,
)


@pytest.fixture
def result() -> EvaluationResult:
    return EvaluationResult(
        verdict=EvaluationVerdict("Does not satisfy the requested requirement"),
        confidence=EvaluationConfidence("uncalibrated supplied assessment"),
        reasoning_summary="  The observed output lacks the requested property.\n",
        evidence_refs=frozenset({EvidenceRef("opaque observed output")}),
    )


def test_method_reference_is_opaque_and_immutable() -> None:
    method = EvaluationMethodRef("  method description\n", "not-semver")
    assert method.method_id == "  method description\n"
    assert method.method_version == "not-semver"
    assert {method: "found"}[replace(method)] == "found"
    with pytest.raises(AttributeError):
        method.method_id = "replacement"  # type: ignore[misc]
    for name in ("execute", "dispatch", "validator", "plugin", "judge"):
        assert not hasattr(method, name)


@pytest.mark.parametrize("field", ["method_id", "method_version"])
@pytest.mark.parametrize("invalid", ["", " ", "\t\n", None, 1, True])
def test_method_validation(field: str, invalid: object) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(EvaluationMethodRef("method", "version"), **{field: invalid})  # type: ignore[arg-type]


@pytest.mark.parametrize("wrapper", [EvaluationVerdict, EvaluationConfidence])
@pytest.mark.parametrize(
    "text",
    [
        "  supplied description\n",
        "unfavorable",
        "137% on a method-specific scale",
        "-12 custom units",
    ],
)
def test_opaque_content_has_no_taxonomy_or_numeric_range(
    wrapper: type[EvaluationVerdict] | type[EvaluationConfidence], text: str
) -> None:
    value = wrapper(text)
    assert value.value == text
    assert {value: "found"}[wrapper(text)] == "found"
    assert not hasattr(wrapper, "__members__")
    with pytest.raises(AttributeError):
        value.value = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("wrapper", [EvaluationVerdict, EvaluationConfidence])
@pytest.mark.parametrize("invalid", ["", " ", "\t\n", None, 1, 0.5, True])
def test_opaque_content_requires_meaningful_text(
    wrapper: type[EvaluationVerdict] | type[EvaluationConfidence], invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        wrapper(invalid)  # type: ignore[arg-type]


def test_result_preserves_original_content(result: EvaluationResult) -> None:
    assert result.verdict.value == "Does not satisfy the requested requirement"
    assert result.confidence.value == "uncalibrated supplied assessment"
    assert (
        result.reasoning_summary
        == "  The observed output lacks the requested property.\n"
    )
    assert result.evidence_refs == frozenset({EvidenceRef("opaque observed output")})
    assert {result: "found"}[replace(result)] == "found"
    assert {field.name for field in fields(result)} == {
        "verdict",
        "confidence",
        "reasoning_summary",
        "evidence_refs",
    }


@pytest.mark.parametrize("field", [field.name for field in fields(EvaluationResult)])
def test_result_fields_cannot_be_mutated_or_deleted(
    result: EvaluationResult, field: str
) -> None:
    with pytest.raises(AttributeError):
        setattr(result, field, getattr(result, field))
    with pytest.raises(AttributeError):
        delattr(result, field)


def test_nested_original_content_is_immutable(result: EvaluationResult) -> None:
    with pytest.raises(AttributeError):
        result.verdict.value = "different judgment"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        result.confidence.value = "different confidence"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        result.evidence_refs.add(EvidenceRef("new"))  # type: ignore[attr-defined]
    reference = next(iter(result.evidence_refs))
    with pytest.raises(AttributeError):
        reference.value = "different evidence"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("verdict", "raw judgment"),
        ("verdict", EvaluationConfidence("same text")),
        ("verdict", None),
        ("confidence", EvaluationVerdict("same text")),
        ("confidence", "raw confidence"),
        ("confidence", 0.5),
        ("confidence", None),
        ("reasoning_summary", ""),
        ("reasoning_summary", " \n"),
        ("reasoning_summary", None),
        ("evidence_refs", None),
        ("evidence_refs", ()),
        ("evidence_refs", []),
        ("evidence_refs", {EvidenceRef("e")}),
        ("evidence_refs", frozenset({"raw"})),
        ("evidence_refs", frozenset({ArtifactRef("wrong reference type")})),
        ("evidence_refs", frozenset({EvidenceRef("e"), None})),
    ],
)
def test_result_rejects_malformed_content(
    result: EvaluationResult, field: str, invalid: object
) -> None:
    with pytest.raises(InvalidDomainValue):
        replace(result, **{field: invalid})  # type: ignore[arg-type]


def test_evidence_is_a_set_not_an_independent_validation(
    result: EvaluationResult,
) -> None:
    refs = frozenset((EvidenceRef("worker claim"), EvidenceRef("worker claim")))
    represented = replace(result, evidence_refs=refs)
    assert len(represented.evidence_refs) == 1
    assert replace(result, evidence_refs=frozenset()).evidence_refs == frozenset()
    for name in (
        "effective_verdict",
        "arbitration_disposition",
        "override",
        "conflict_set",
        "policy_passed",
        "verified",
    ):
        assert not hasattr(represented, name)
