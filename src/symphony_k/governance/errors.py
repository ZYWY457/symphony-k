"""Caller-safe error categories for the public governance facade."""

from enum import Enum

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


class GovernanceErrorCategory(Enum):
    """Stable categories callers may use without inspecting persistence details."""

    INVALID_REQUEST = "INVALID_REQUEST"
    AUTHORITY_DENIED = "AUTHORITY_DENIED"
    CONFLICT = "CONFLICT"
    NOT_FOUND = "NOT_FOUND"
    INVARIANT_VIOLATION = "INVARIANT_VIOLATION"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"


class GovernanceFacadeError(Exception):
    """Base rejection retaining the original domain cause when one exists."""

    category: GovernanceErrorCategory

    def __init__(
        self, message: str, *, domain_error: DomainError | None = None
    ) -> None:
        super().__init__(message)
        self.domain_error = domain_error


class InvalidRequestError(GovernanceFacadeError):
    category = GovernanceErrorCategory.INVALID_REQUEST


class AuthorityDeniedError(GovernanceFacadeError):
    category = GovernanceErrorCategory.AUTHORITY_DENIED


class ConflictError(GovernanceFacadeError):
    category = GovernanceErrorCategory.CONFLICT


class NotFoundError(GovernanceFacadeError):
    category = GovernanceErrorCategory.NOT_FOUND


class GovernanceInvariantError(GovernanceFacadeError):
    category = GovernanceErrorCategory.INVARIANT_VIOLATION


class UnsupportedOperationError(GovernanceFacadeError):
    category = GovernanceErrorCategory.UNSUPPORTED_OPERATION


def translate_domain_error(error: DomainError) -> GovernanceFacadeError:
    """Map accepted domain rejections without converting them into success."""
    message = str(error) or type(error).__name__
    if isinstance(error, UnauthorizedTransition):
        return AuthorityDeniedError(message, domain_error=error)
    if isinstance(error, ConcurrencyConflict):
        return ConflictError(message, domain_error=error)
    if isinstance(error, EntityNotFound):
        return NotFoundError(message, domain_error=error)
    if isinstance(error, (InvalidDomainValue, InvalidRelationship, InvalidTransition)):
        return InvalidRequestError(message, domain_error=error)
    if isinstance(
        error,
        (InvariantViolation, CompletionPolicyNotSatisfied, ImmutableRecordViolation),
    ):
        return GovernanceInvariantError(message, domain_error=error)
    return GovernanceInvariantError(message, domain_error=error)
