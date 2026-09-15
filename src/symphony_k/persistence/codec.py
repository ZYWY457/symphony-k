"""Deterministic, non-executable JSON for the closed Stage 1 record vocabulary."""

import json
from collections.abc import Callable
from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
from typing import cast
from uuid import UUID

from ._codec_types import RECORD_TYPES

type Json = None | bool | int | str | list[Json] | dict[str, Json]

_TYPES = {cls.__name__: cls for cls in RECORD_TYPES}
if len(_TYPES) != len(RECORD_TYPES):
    raise RuntimeError("Codec type tags must be unique")


def _json(value: Json) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _encode(value: object) -> Json:
    if value is None or type(value) in (bool, int, str):
        return cast(Json, value)
    if type(value) is UUID:
        return {"type": "uuid", "value": str(value)}
    if type(value) is datetime:
        return {"type": "datetime", "value": value.isoformat(timespec="microseconds")}
    if type(value) in (tuple, frozenset):
        items = [_encode(item) for item in cast(tuple[object, ...], value)]
        if isinstance(value, frozenset):
            items.sort(key=_json)
        return {"type": type(value).__name__, "items": items}
    cls = type(value)
    if _TYPES.get(cls.__name__) is not cls:
        raise ValueError(f"Unsupported persistence type: {cls.__name__}")
    if isinstance(value, Enum):
        return {"type": cls.__name__, "value": _encode(value.value)}
    if is_dataclass(value) and not isinstance(value, type):
        return {
            "type": cls.__name__,
            "fields": {
                field.name: _encode(getattr(value, field.name))
                for field in fields(value)
            },
        }
    raise ValueError("Unsupported persistence value")


def _decode(value: Json) -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if not isinstance(value, dict) or not isinstance(value.get("type"), str):
        raise ValueError("Encoded record must have a type tag")
    tag = cast(str, value["type"])
    if tag in {"tuple", "frozenset"}:
        if set(value) != {"type", "items"} or not isinstance(value["items"], list):
            raise ValueError("Invalid collection encoding")
        items = [_decode(item) for item in value["items"]]
        return tuple(items) if tag == "tuple" else frozenset(items)
    if tag in {"uuid", "datetime"}:
        if set(value) != {"type", "value"} or not isinstance(value["value"], str):
            raise ValueError("Invalid scalar encoding")
        return (
            UUID(value["value"])
            if tag == "uuid"
            else datetime.fromisoformat(value["value"])
        )
    cls = _TYPES.get(tag)
    if cls is None:
        raise ValueError("Unknown persistence type tag")
    if issubclass(cls, Enum):
        if set(value) != {"type", "value"}:
            raise ValueError("Invalid enum encoding")
        return cls(_decode(value["value"]))
    data = value.get("fields")
    if set(value) != {"type", "fields"} or not isinstance(data, dict):
        raise ValueError("Invalid record encoding")
    if not is_dataclass(cls):
        raise ValueError("Type is not a record")
    if set(data) != {field.name for field in fields(cls)}:
        raise ValueError("Record fields do not match the closed schema")
    constructor = cast(Callable[..., object], cls)
    return constructor(**{key: _decode(item) for key, item in data.items()})


def encode(value: object) -> str:
    """Encode explicit type tags, field names, enum values and canonical sets."""
    return _json({"format": 1, "record": _encode(value)})


def _unique_keys(items: list[tuple[str, Json]]) -> dict[str, Json]:
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("Duplicate JSON key")
    return result


def decode(text: str) -> object:
    """Construct only allowlisted immutable records; reject noncanonical input."""
    value: Json = json.loads(text, object_pairs_hook=_unique_keys)
    if not isinstance(value, dict) or set(value) != {"format", "record"}:
        raise ValueError("Invalid persistence envelope")
    if type(value["format"]) is not int or value["format"] != 1:
        raise ValueError("Unsupported persistence format")
    result = _decode(value["record"])
    if encode(result) != text:
        raise ValueError("Persistence input is not canonical")
    return result


def fingerprint(request: object) -> str:
    return sha256(encode(request).encode("utf-8")).hexdigest()
