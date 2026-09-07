"""Explicit Evaluation target scope without target objects or lookups."""

from dataclasses import dataclass
from typing import overload

from .candidate_refs import EvidenceRef
from .errors import InvalidDomainValue
from .ids import EffectId, OutcomeId, RunId
from .version import EntityVersion


@dataclass(frozen=True, slots=True, init=False)
class EvaluationTargetRef:
    """One typed target: a versioned entity ID or an anchored EvidenceRef.

    The reference type discriminates the target; no independent kind label can
    disagree with it. Entity versions are observed scope, not current-state proof.
    """

    reference: RunId | OutcomeId | EffectId | EvidenceRef
    version: EntityVersion | None

    @overload
    def __init__(
        self, reference: RunId | OutcomeId | EffectId, version: EntityVersion
    ) -> None: ...

    @overload
    def __init__(self, reference: EvidenceRef, version: None = None) -> None: ...

    def __init__(
        self,
        reference: RunId | OutcomeId | EffectId | EvidenceRef,
        version: EntityVersion | None = None,
    ) -> None:
        if isinstance(reference, (RunId, OutcomeId, EffectId)):
            if not isinstance(version, EntityVersion):
                raise InvalidDomainValue("Entity targets require an EntityVersion")
        elif isinstance(reference, EvidenceRef):
            if version is not None:
                raise InvalidDomainValue(
                    "Evidence targets do not have an entity version"
                )
        else:
            raise InvalidDomainValue(
                "Target must be a RunId, OutcomeId, EffectId or EvidenceRef"
            )
        object.__setattr__(self, "reference", reference)
        object.__setattr__(self, "version", version)
