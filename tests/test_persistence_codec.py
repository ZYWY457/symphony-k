"""Lossless snapshots, full semantic requests, events and closed decoding."""

from dataclasses import replace

import pytest

from symphony_k.domain import CreationRequest, TransitionReason, create_entity
from symphony_k.persistence.codec import decode, encode, fingerprint
from tests.test_creation_integrated import CASES, creation_context


@pytest.mark.parametrize("creation_request", CASES)
def test_all_creation_snapshots_events_and_full_requests_round_trip(
    creation_request: CreationRequest,
) -> None:
    result = create_entity(creation_request, creation_context(creation_request))
    for value in (creation_request, result.entity, result.event):
        restored = decode(encode(value))
        assert restored == value
        assert type(restored) is type(value)
        assert encode(restored) == encode(value)


@pytest.mark.parametrize("creation_request", CASES)
def test_fingerprint_binds_the_complete_request(
    creation_request: CreationRequest,
) -> None:
    assert fingerprint(creation_request) == fingerprint(
        decode(encode(creation_request))
    )
    changed = replace(creation_request, reason=TransitionReason("Different reason"))
    assert fingerprint(changed) != fingerprint(creation_request)


def test_frozensets_are_canonical_and_tuples_keep_order() -> None:
    assert encode(frozenset({"a", "b"})) == encode(frozenset({"b", "a"}))
    assert encode(("a", "b")) != encode(("b", "a"))
    assert decode(encode(frozenset({("k", "v")}))) == frozenset({("k", "v")})


@pytest.mark.parametrize(
    "text",
    [
        '{"format":1,"record":{"type":"os.system","fields":{}}}',
        '{"format":1,"format":1,"record":null}',
        '{"format":2,"record":null}',
        '{"format":1,"record":{"type":"Objective","fields":{}}}',
        '{"format":1,"record":{"type":"tuple","items":[],"code":"x"}}',
    ],
)
def test_unknown_types_versions_and_schema_fields_are_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        decode(text)


def test_arbitrary_objects_are_not_serializable() -> None:
    with pytest.raises(ValueError):
        encode(object())
