"""Domain errors are separately catchable without infrastructure context."""

import pytest

from symphony_k.domain import (
    CompletionPolicyNotSatisfied,
    ConcurrencyConflict,
    DomainError,
    EntityNotFound,
    ImmutableRecordViolation,
    InvalidDomainValue,
    InvalidRelationship,
    InvalidTransition,
    InvariantViolation,
    UnauthorizedTransition,
)

REQUIRED_ERRORS = (
    InvalidTransition,
    UnauthorizedTransition,
    InvariantViolation,
    ConcurrencyConflict,
    EntityNotFound,
    InvalidRelationship,
    CompletionPolicyNotSatisfied,
    ImmutableRecordViolation,
)


@pytest.mark.parametrize("error_type", REQUIRED_ERRORS)
def test_required_errors_are_distinguishable(error_type: type[DomainError]) -> None:
    error = error_type("rejected")
    with pytest.raises(DomainError) as caught:
        raise error
    assert type(caught.value) is error_type
    assert str(caught.value) == "rejected"
    for other_type in REQUIRED_ERRORS:
        if other_type is not error_type:
            assert not isinstance(caught.value, other_type)


def test_constructor_validation_is_a_domain_and_value_error() -> None:
    error = InvalidDomainValue("invalid input")
    assert isinstance(error, DomainError)
    assert isinstance(error, ValueError)
    assert not isinstance(error, InvalidTransition)
