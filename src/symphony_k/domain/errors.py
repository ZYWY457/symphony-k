"""Typed domain rejections, independent of execution and storage mechanisms."""


class DomainError(Exception):
    """Base for expected domain rejection."""


class InvalidDomainValue(DomainError, ValueError):
    """A shared value object's construction input is invalid."""


class InvalidTransition(DomainError):
    """The requested lifecycle transition is not legal."""


class UnauthorizedTransition(DomainError):
    """The initiating authority cannot perform the requested transition."""


class InvariantViolation(DomainError):
    """A domain invariant would be violated."""


class ConcurrencyConflict(DomainError):
    """A mutation is based on a stale entity version."""


class EntityNotFound(DomainError):
    """The requested entity does not exist."""


class InvalidRelationship(DomainError):
    """A domain relationship is invalid."""


class CompletionPolicyNotSatisfied(DomainError):
    """The applicable completion policy has not been satisfied."""


class ImmutableRecordViolation(DomainError):
    """An operation would alter an immutable record."""
