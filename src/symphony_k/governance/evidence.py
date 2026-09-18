"""Durable trusted-evidence provenance intake outside lifecycle authority."""

from __future__ import annotations

import json
from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
from typing import Protocol
from uuid import UUID

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    ConcurrencyConflict,
    DomainError,
    EffectId,
    EntityNotFound,
    EntityVersion,
    EvidenceRef,
    InvariantViolation,
    OutcomeId,
    RunId,
    Timestamp,
)

from .errors import (
    AuthorityDeniedError,
    ConflictError,
    GovernanceFacadeError,
    GovernanceInvariantError,
    InvalidRequestError,
    NotFoundError,
    translate_domain_error,
)
from .types import EffectRef, OutcomeRef, RunRef

CANONICAL_EVIDENCE_RECORD_VERSION = "symphony-k.evidence-record/v1"
CANONICAL_EVIDENCE_FINGERPRINT_ALGORITHM = "sha256/v1"


def _text(value: object, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InvalidRequestError(f"{label} must contain non-whitespace text")


def _canonical_value(value: object) -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if isinstance(value, Enum):
        return {
            "type": type(value).__name__,
            "value": _canonical_value(value.value),
        }
    if type(value) is UUID:
        return {"type": "uuid", "value": str(value)}
    if type(value) is datetime:
        return {
            "type": "datetime",
            "value": value.isoformat(timespec="microseconds"),
        }
    if isinstance(value, (tuple, frozenset)):
        items = [_canonical_value(item) for item in value]
        if isinstance(value, frozenset):
            items.sort(key=lambda item: json.dumps(item, sort_keys=True))
        return {"type": type(value).__name__, "items": items}
    if is_dataclass(value) and not isinstance(value, type):
        if _EVIDENCE_CODEC_TYPES.get(type(value).__name__) is not type(value):
            raise InvalidRequestError(
                f"{type(value).__name__} is outside the closed evidence schema"
            )
        return {
            "type": type(value).__name__,
            "fields": {
                field.name: _canonical_value(getattr(value, field.name))
                for field in fields(value)
            },
        }
    raise InvalidRequestError(
        f"{type(value).__name__} is not supported by evidence canonicalization"
    )


def _fingerprint(value: object) -> str:
    envelope = {
        "canonical_version": CANONICAL_EVIDENCE_RECORD_VERSION,
        "semantic_record": _canonical_value(value),
    }
    encoded = json.dumps(
        envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class VersionedDescriptor:
    identity: str
    version: str

    def __post_init__(self) -> None:
        _text(self.identity, "descriptor identity")
        _text(self.version, "descriptor version")


@dataclass(frozen=True, slots=True)
class PrincipalRef:
    principal_id: str
    issuer: str
    assertion_ref: str

    def __post_init__(self) -> None:
        _text(self.principal_id, "principal_id")
        _text(self.issuer, "principal issuer")
        _text(self.assertion_ref, "principal assertion_ref")


@dataclass(frozen=True, slots=True)
class ContentDigestClaim:
    algorithm_claim: str
    algorithm_version_claim: str
    digest_claim: str

    def __post_init__(self) -> None:
        _text(self.algorithm_claim, "algorithm claim")
        _text(self.algorithm_version_claim, "algorithm version claim")
        _text(self.digest_claim, "digest claim")


@dataclass(frozen=True, slots=True)
class ExternalAnchorClaim:
    provider_claim: str
    locator_claim: str
    receipt_claim: str
    revision_claim: str | None = None

    def __post_init__(self) -> None:
        _text(self.provider_claim, "provider claim")
        _text(self.locator_claim, "locator claim")
        _text(self.receipt_claim, "receipt claim")
        if self.revision_claim is not None:
            _text(self.revision_claim, "revision claim")


type IntegrityAnchorClaim = ContentDigestClaim | ExternalAnchorClaim
type EvidenceTargetClaim = RunRef | OutcomeRef | EffectRef | EvidenceRef


@dataclass(frozen=True, slots=True)
class MaterialProvenanceClaim:
    method_identity_claim: str
    method_version_claim: str
    tool_identity_claim: str
    tool_version_claim: str
    provider_identity_claim: str
    provider_version_claim: str

    def __post_init__(self) -> None:
        for label, value in (
            ("method identity claim", self.method_identity_claim),
            ("method version claim", self.method_version_claim),
            ("tool identity claim", self.tool_identity_claim),
            ("tool version claim", self.tool_version_claim),
            ("provider identity claim", self.provider_identity_claim),
            ("provider version claim", self.provider_version_claim),
        ):
            _text(value, label)


@dataclass(frozen=True, slots=True)
class EvidenceSubmissionClaim:
    """Caller-controlled values. No field establishes trust or authority."""

    target: EvidenceTargetClaim
    source_locator_claim: str
    caller_identity_claim: ActorIdentity
    idempotency_key: str
    requested_evidence_ref: EvidenceRef | None = None
    integrity_anchor_claim: IntegrityAnchorClaim | None = None
    observed_at_claim: Timestamp | None = None
    material_provenance_claim: MaterialProvenanceClaim | None = None
    producing_principal_claims: tuple[str, ...] = ()
    source_provider_claim: str | None = None
    source_namespace_claim: str | None = None
    collector_identity_claim: str | None = None
    trusted_claim: bool | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.target, (RunRef, OutcomeRef, EffectRef, EvidenceRef)):
            raise InvalidRequestError("Evidence target claim has an unsupported type")
        _text(self.source_locator_claim, "source locator claim")
        if not isinstance(self.caller_identity_claim, ActorIdentity):
            raise InvalidRequestError("caller_identity_claim must be ActorIdentity")
        _text(self.idempotency_key, "idempotency_key")
        if self.requested_evidence_ref is not None and not isinstance(
            self.requested_evidence_ref, EvidenceRef
        ):
            raise InvalidRequestError("requested_evidence_ref must be EvidenceRef")
        if self.observed_at_claim is not None and not isinstance(
            self.observed_at_claim, Timestamp
        ):
            raise InvalidRequestError("observed_at_claim must be Timestamp")
        for principal in self.producing_principal_claims:
            _text(principal, "producing principal claim")
        for label, value in (
            ("source provider claim", self.source_provider_claim),
            ("source namespace claim", self.source_namespace_claim),
            ("collector identity claim", self.collector_identity_claim),
        ):
            if value is not None:
                _text(value, label)
        if self.trusted_claim is not None and type(self.trusted_claim) is not bool:
            raise InvalidRequestError("trusted_claim must be boolean when supplied")


@dataclass(frozen=True, slots=True)
class EvidenceRecordRef:
    evidence_ref: EvidenceRef
    record_fingerprint: str

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_ref, EvidenceRef):
            raise InvalidRequestError("evidence_ref must be EvidenceRef")
        if (
            not isinstance(self.record_fingerprint, str)
            or len(self.record_fingerprint) != 64
            or any(
                character not in "0123456789abcdef"
                for character in self.record_fingerprint
            )
        ):
            raise InvalidRequestError(
                "record_fingerprint must be a lowercase SHA-256 digest"
            )


type ExactEvidenceTarget = RunRef | OutcomeRef | EffectRef | EvidenceRecordRef


@dataclass(frozen=True, slots=True)
class ContentDigestAnchor:
    algorithm: str
    algorithm_version: str
    digest: str
    representation: str

    def __post_init__(self) -> None:
        for label, value in (
            ("digest algorithm", self.algorithm),
            ("digest algorithm version", self.algorithm_version),
            ("digest", self.digest),
            ("digest representation", self.representation),
        ):
            _text(value, label)


@dataclass(frozen=True, slots=True)
class ExternalImmutableAnchor:
    provider_identity: str
    namespace: str
    immutable_observation_id: str
    verification_mechanism: VersionedDescriptor
    locator: str
    provider_revision: str
    assertion_ref: str
    collected_at: Timestamp
    observed_at: Timestamp

    def __post_init__(self) -> None:
        for label, value in (
            ("anchor provider identity", self.provider_identity),
            ("anchor namespace", self.namespace),
            ("immutable observation identity", self.immutable_observation_id),
            ("anchor locator", self.locator),
            ("provider revision", self.provider_revision),
            ("anchor assertion_ref", self.assertion_ref),
        ):
            _text(value, label)
        if not isinstance(self.verification_mechanism, VersionedDescriptor):
            raise InvalidRequestError("verification_mechanism is invalid")
        if not isinstance(self.collected_at, Timestamp) or not isinstance(
            self.observed_at, Timestamp
        ):
            raise InvalidRequestError("anchor times must be Timestamp values")


type IntegrityAnchor = ContentDigestAnchor | ExternalImmutableAnchor


@dataclass(frozen=True, slots=True)
class EvidenceSource:
    kind: str
    provider_identity: str
    namespace: str

    def __post_init__(self) -> None:
        _text(self.kind, "source kind")
        _text(self.provider_identity, "source provider identity")
        _text(self.namespace, "source namespace")


@dataclass(frozen=True, slots=True)
class ObservedTimeProvenance:
    observed_at: Timestamp
    provenance_ref: str

    def __post_init__(self) -> None:
        if not isinstance(self.observed_at, Timestamp):
            raise InvalidRequestError("observed_at must be Timestamp")
        _text(self.provenance_ref, "observation-time provenance_ref")


@dataclass(frozen=True, slots=True)
class MaterialProvenance:
    method: VersionedDescriptor
    tool: VersionedDescriptor
    provider: VersionedDescriptor

    def __post_init__(self) -> None:
        if any(
            not isinstance(value, VersionedDescriptor)
            for value in (self.method, self.tool, self.provider)
        ):
            raise InvalidRequestError(
                "Material method, tool, and provider must be versioned"
            )


@dataclass(frozen=True, slots=True)
class VerificationProvenance:
    verifier: PrincipalRef
    mechanism: VersionedDescriptor
    verified_at: Timestamp

    def __post_init__(self) -> None:
        if not isinstance(self.verifier, PrincipalRef):
            raise InvalidRequestError("verifier must be PrincipalRef")
        if not isinstance(self.mechanism, VersionedDescriptor):
            raise InvalidRequestError("verification mechanism is invalid")
        if not isinstance(self.verified_at, Timestamp):
            raise InvalidRequestError("verified_at must be Timestamp")


@dataclass(frozen=True, slots=True)
class TrustedEvidenceDraft:
    """Boundary-produced facts; the service alone turns this into a record."""

    evidence_ref: EvidenceRef
    target: ExactEvidenceTarget
    integrity_anchor: IntegrityAnchor
    source: EvidenceSource
    collector: PrincipalRef
    collector_adapter: VersionedDescriptor
    collected_at: Timestamp
    observed_at: ObservedTimeProvenance
    material_provenance: MaterialProvenance
    producing_principals: tuple[PrincipalRef, ...]
    collection_request_ref: str
    evidence_policy: VersionedDescriptor
    verification: VerificationProvenance
    supersedes: EvidenceRecordRef | None = None


@dataclass(frozen=True, slots=True)
class EvidenceRecordSemantics:
    """Complete immutable projection covered by the record fingerprint."""

    canonical_version: str
    fingerprint_algorithm: str
    evidence_ref: EvidenceRef
    target: ExactEvidenceTarget
    integrity_anchor: IntegrityAnchor
    source: EvidenceSource
    collector: PrincipalRef
    collector_adapter: VersionedDescriptor
    collected_at: Timestamp
    observed_at: ObservedTimeProvenance
    material_provenance: MaterialProvenance
    producing_principals: tuple[PrincipalRef, ...]
    collection_request_ref: str
    evidence_policy: VersionedDescriptor
    verification: VerificationProvenance
    supersedes: EvidenceRecordRef | None


@dataclass(frozen=True, slots=True)
class TrustedEvidenceRecord:
    semantics: EvidenceRecordSemantics
    record_fingerprint: str

    @property
    def exact_ref(self) -> EvidenceRecordRef:
        return EvidenceRecordRef(self.semantics.evidence_ref, self.record_fingerprint)


class EvidenceTrustStatus(Enum):
    VERIFIED = "VERIFIED"
    ADVERSE = "ADVERSE"
    UNRESOLVED = "UNRESOLVED"
    INCOMPLETE = "INCOMPLETE"


@dataclass(frozen=True, slots=True)
class EvidenceTrustFindingRecord:
    finding_id: str
    evidence_record: EvidenceRecordRef
    status: EvidenceTrustStatus
    finding_authority: PrincipalRef
    finding_policy: VersionedDescriptor
    recorded_at: Timestamp
    reason: str
    supersedes_finding_id: str | None = None

    def __post_init__(self) -> None:
        _text(self.finding_id, "finding_id")
        if not isinstance(self.evidence_record, EvidenceRecordRef):
            raise InvalidRequestError("finding must exact-bind an evidence record")
        if not isinstance(self.status, EvidenceTrustStatus):
            raise InvalidRequestError("finding status is invalid")
        if not isinstance(self.finding_authority, PrincipalRef):
            raise InvalidRequestError("finding authority is invalid")
        if not isinstance(self.finding_policy, VersionedDescriptor):
            raise InvalidRequestError("finding policy is invalid")
        if not isinstance(self.recorded_at, Timestamp):
            raise InvalidRequestError("finding recorded_at must be Timestamp")
        _text(self.reason, "finding reason")
        if self.supersedes_finding_id is not None:
            _text(self.supersedes_finding_id, "supersedes_finding_id")
            if self.supersedes_finding_id == self.finding_id:
                raise InvalidRequestError("A finding cannot supersede itself")


@dataclass(frozen=True, slots=True)
class EvidenceTrustFindingClaim:
    """Caller request for a finding; every value remains non-authoritative."""

    evidence_record_claim: EvidenceRecordRef
    status_claim: EvidenceTrustStatus
    reason_claim: str
    caller_identity_claim: ActorIdentity
    requested_finding_id: str | None = None
    supersedes_finding_id_claim: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_record_claim, EvidenceRecordRef):
            raise InvalidRequestError("finding target claim must be exact")
        if not isinstance(self.status_claim, EvidenceTrustStatus):
            raise InvalidRequestError("finding status claim is invalid")
        _text(self.reason_claim, "finding reason claim")
        if not isinstance(self.caller_identity_claim, ActorIdentity):
            raise InvalidRequestError("finding caller claim must be ActorIdentity")
        if self.requested_finding_id is not None:
            _text(self.requested_finding_id, "requested_finding_id")
        if self.supersedes_finding_id_claim is not None:
            _text(
                self.supersedes_finding_id_claim,
                "supersedes_finding_id claim",
            )


_EVIDENCE_CODEC_CLASSES: tuple[type, ...] = (
    ActorId,
    ActorType,
    ActorIdentity,
    EvidenceRef,
    RunId,
    OutcomeId,
    EffectId,
    EntityVersion,
    Timestamp,
    RunRef,
    OutcomeRef,
    EffectRef,
    VersionedDescriptor,
    PrincipalRef,
    ContentDigestClaim,
    ExternalAnchorClaim,
    MaterialProvenanceClaim,
    EvidenceSubmissionClaim,
    EvidenceRecordRef,
    ContentDigestAnchor,
    ExternalImmutableAnchor,
    EvidenceSource,
    ObservedTimeProvenance,
    MaterialProvenance,
    VerificationProvenance,
    EvidenceRecordSemantics,
    TrustedEvidenceRecord,
    EvidenceTrustStatus,
    EvidenceTrustFindingRecord,
    EvidenceTrustFindingClaim,
)
_EVIDENCE_CODEC_TYPES = {value.__name__: value for value in _EVIDENCE_CODEC_CLASSES}
if len(_EVIDENCE_CODEC_TYPES) != len(_EVIDENCE_CODEC_CLASSES):
    raise RuntimeError("Evidence codec type tags must be unique")


def _decode_canonical(value: object) -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if not isinstance(value, dict) or not isinstance(value.get("type"), str):
        raise ValueError("Evidence record must contain closed type tags")
    tag = value["type"]
    if tag in {"tuple", "frozenset"}:
        if set(value) != {"type", "items"} or not isinstance(value["items"], list):
            raise ValueError("Invalid evidence collection encoding")
        items = [_decode_canonical(item) for item in value["items"]]
        return tuple(items) if tag == "tuple" else frozenset(items)
    if tag in {"uuid", "datetime"}:
        if set(value) != {"type", "value"} or not isinstance(value["value"], str):
            raise ValueError("Invalid evidence scalar encoding")
        return (
            UUID(value["value"])
            if tag == "uuid"
            else datetime.fromisoformat(value["value"])
        )
    cls = _EVIDENCE_CODEC_TYPES.get(tag)
    if cls is None:
        raise ValueError("Unknown evidence type tag")
    if issubclass(cls, Enum):
        if set(value) != {"type", "value"}:
            raise ValueError("Invalid evidence enum encoding")
        return cls(_decode_canonical(value["value"]))
    data = value.get("fields")
    if set(value) != {"type", "fields"} or not isinstance(data, dict):
        raise ValueError("Invalid evidence record encoding")
    if not is_dataclass(cls) or set(data) != {field.name for field in fields(cls)}:
        raise ValueError("Evidence record fields differ from the closed schema")
    return cls(**{key: _decode_canonical(item) for key, item in data.items()})


def _encode_evidence(value: object) -> str:
    return json.dumps(
        {
            "format": CANONICAL_EVIDENCE_RECORD_VERSION,
            "record": _canonical_value(value),
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _decode_evidence(text: str) -> object:
    value = json.loads(text)
    if (
        not isinstance(value, dict)
        or set(value) != {"format", "record"}
        or value["format"] != CANONICAL_EVIDENCE_RECORD_VERSION
    ):
        raise ValueError("Invalid evidence persistence envelope")
    result = _decode_canonical(value["record"])
    if _encode_evidence(result) != text:
        raise ValueError("Evidence persistence input is not canonical")
    return result


@dataclass(frozen=True, slots=True)
class EvidenceProvenanceView:
    record: TrustedEvidenceRecord
    findings: tuple[EvidenceTrustFindingRecord, ...]


class TrustedEvidenceCollector(Protocol):
    """Injected trusted boundary; callers cannot pass a trusted draft directly."""

    def collect(self, claim: EvidenceSubmissionClaim) -> TrustedEvidenceDraft: ...

    def establish_finding(
        self, claim: EvidenceTrustFindingClaim
    ) -> EvidenceTrustFindingRecord: ...


class EvidenceStore(Protocol):
    def _evidence_load_exact(
        self, evidence_ref: str, record_fingerprint: str
    ) -> str: ...

    def _evidence_load_identity(self, evidence_ref: str) -> tuple[str, str]: ...

    def _evidence_findings(
        self, evidence_ref: str, record_fingerprint: str
    ) -> tuple[str, ...]: ...

    def _evidence_register(
        self,
        evidence_ref: str,
        record_fingerprint: str,
        record: str,
        operation_key: str,
        operation_fingerprint: str,
        claim: str,
        linked_records: tuple[tuple[str, str], ...],
    ) -> str: ...

    def _evidence_append_finding(
        self,
        finding_id: str,
        evidence_ref: str,
        record_fingerprint: str,
        status: str,
        supersedes_finding_id: str | None,
        record: str,
    ) -> None: ...


def _record_from_draft(draft: TrustedEvidenceDraft) -> TrustedEvidenceRecord:
    if not isinstance(draft, TrustedEvidenceDraft):
        raise AuthorityDeniedError("Trusted collector returned an invalid result")
    semantics = EvidenceRecordSemantics(
        CANONICAL_EVIDENCE_RECORD_VERSION,
        CANONICAL_EVIDENCE_FINGERPRINT_ALGORITHM,
        draft.evidence_ref,
        draft.target,
        draft.integrity_anchor,
        draft.source,
        draft.collector,
        draft.collector_adapter,
        draft.collected_at,
        draft.observed_at,
        draft.material_provenance,
        draft.producing_principals,
        draft.collection_request_ref,
        draft.evidence_policy,
        draft.verification,
        draft.supersedes,
    )
    return TrustedEvidenceRecord(semantics, _fingerprint(semantics))


class EvidenceProvenanceService:
    """Register and resolve evidence without acquiring lifecycle authority."""

    def __init__(
        self,
        store: EvidenceStore,
        collector: TrustedEvidenceCollector,
        *,
        allowed_content_digests: frozenset[tuple[str, str]] = frozenset(
            {("sha256", "1")}
        ),
    ) -> None:
        self._store = store
        self._collector = collector
        self._allowed_content_digests = allowed_content_digests

    def register(self, claim: EvidenceSubmissionClaim) -> EvidenceProvenanceView:
        if not isinstance(claim, EvidenceSubmissionClaim):
            raise InvalidRequestError("Expected EvidenceSubmissionClaim")
        try:
            draft = self._collector.collect(claim)
            self._validate_draft(draft)
            record = _record_from_draft(draft)
            self._validate_links(record)
            operation_fingerprint = _fingerprint((claim, record.semantics))
            links = tuple(
                (reference.evidence_ref.value, reference.record_fingerprint)
                for reference in (
                    record.semantics.target,
                    record.semantics.supersedes,
                )
                if isinstance(reference, EvidenceRecordRef)
            )
            stored = self._store._evidence_register(
                record.semantics.evidence_ref.value,
                record.record_fingerprint,
                _encode_evidence(record),
                claim.idempotency_key,
                operation_fingerprint,
                _encode_evidence(claim),
                links,
            )
            self._decode_record(stored, record.exact_ref)
            return self.read(record.exact_ref)
        except GovernanceFacadeError:
            raise
        except DomainError as exc:
            raise translate_domain_error(exc) from exc
        except Exception as exc:
            raise GovernanceInvariantError(
                "Evidence registration failed inside the trusted boundary"
            ) from exc

    def read(self, reference: EvidenceRecordRef) -> EvidenceProvenanceView:
        if not isinstance(reference, EvidenceRecordRef):
            raise InvalidRequestError("Expected EvidenceRecordRef")
        try:
            record = self._decode_record(
                self._store._evidence_load_exact(
                    reference.evidence_ref.value, reference.record_fingerprint
                ),
                reference,
            )
            findings = tuple(
                self._decode_finding(value, reference)
                for value in self._store._evidence_findings(
                    reference.evidence_ref.value, reference.record_fingerprint
                )
            )
            return EvidenceProvenanceView(record, findings)
        except GovernanceFacadeError:
            raise
        except EntityNotFound as exc:
            raise NotFoundError("Evidence record is not found") from exc
        except ConcurrencyConflict as exc:
            raise ConflictError("Evidence exact reference does not match") from exc
        except DomainError as exc:
            raise translate_domain_error(exc) from exc
        except Exception as exc:
            raise GovernanceInvariantError("Evidence read failed") from exc

    def lookup(self, evidence_ref: EvidenceRef) -> EvidenceProvenanceView:
        if not isinstance(evidence_ref, EvidenceRef):
            raise InvalidRequestError("Expected EvidenceRef")
        try:
            fingerprint, encoded = self._store._evidence_load_identity(
                evidence_ref.value
            )
            reference = EvidenceRecordRef(evidence_ref, fingerprint)
            record = self._decode_record(encoded, reference)
        except EntityNotFound as exc:
            raise NotFoundError("Evidence identity is not found") from exc
        except DomainError as exc:
            raise translate_domain_error(exc) from exc
        except Exception as exc:
            raise GovernanceInvariantError("Evidence lookup failed") from exc
        return self.read(record.exact_ref)

    def append_trust_finding(self, claim: EvidenceTrustFindingClaim) -> None:
        if not isinstance(claim, EvidenceTrustFindingClaim):
            raise InvalidRequestError("Expected EvidenceTrustFindingClaim")
        try:
            finding = self._collector.establish_finding(claim)
            if not isinstance(finding, EvidenceTrustFindingRecord):
                raise AuthorityDeniedError(
                    "Trusted provider returned an invalid finding"
                )
            self._store._evidence_load_exact(
                finding.evidence_record.evidence_ref.value,
                finding.evidence_record.record_fingerprint,
            )
            self._store._evidence_append_finding(
                finding.finding_id,
                finding.evidence_record.evidence_ref.value,
                finding.evidence_record.record_fingerprint,
                finding.status.value,
                finding.supersedes_finding_id,
                _encode_evidence(finding),
            )
        except GovernanceFacadeError:
            raise
        except EntityNotFound as exc:
            raise NotFoundError("Finding target evidence is not found") from exc
        except DomainError as exc:
            raise translate_domain_error(exc) from exc
        except Exception as exc:
            raise GovernanceInvariantError("Evidence finding write failed") from exc

    @staticmethod
    def _decode_record(
        encoded: str, reference: EvidenceRecordRef
    ) -> TrustedEvidenceRecord:
        value = _decode_evidence(encoded)
        if not isinstance(value, TrustedEvidenceRecord):
            raise InvariantViolation("Stored evidence record type differs")
        if value.exact_ref != reference or record_fingerprint(value) != (
            reference.record_fingerprint
        ):
            raise InvariantViolation("Stored evidence record integrity differs")
        return value

    @staticmethod
    def _decode_finding(
        encoded: str, reference: EvidenceRecordRef
    ) -> EvidenceTrustFindingRecord:
        value = _decode_evidence(encoded)
        if (
            not isinstance(value, EvidenceTrustFindingRecord)
            or value.evidence_record != reference
        ):
            raise InvariantViolation("Stored evidence finding binding differs")
        return value

    def resolve_trusted(
        self,
        reference: EvidenceRecordRef | EvidenceRef,
        *,
        expected_target: ExactEvidenceTarget | None = None,
    ) -> EvidenceProvenanceView:
        view = (
            self.read(reference)
            if isinstance(reference, EvidenceRecordRef)
            else self.lookup(reference)
        )
        if (
            expected_target is not None
            and view.record.semantics.target != expected_target
        ):
            raise AuthorityDeniedError(
                "Evidence is not scoped to the required exact target"
            )
        self._resolve_chain(view.record, set())
        self._require_current_trust(view)
        return view

    def _resolve_chain(
        self, record: TrustedEvidenceRecord, visited: set[EvidenceRecordRef]
    ) -> None:
        reference = record.exact_ref
        if reference in visited:
            raise AuthorityDeniedError("Cyclic evidence target is not trusted")
        visited.add(reference)
        target = record.semantics.target
        if isinstance(target, EvidenceRecordRef):
            try:
                target_view = self.read(target)
            except (NotFoundError, ConflictError) as exc:
                raise AuthorityDeniedError(
                    "Evidence target cannot be resolved exactly"
                ) from exc
            self._require_current_trust(target_view)
            self._resolve_chain(target_view.record, visited)
        visited.remove(reference)

    @staticmethod
    def _require_current_trust(view: EvidenceProvenanceView) -> None:
        superseded = {
            finding.supersedes_finding_id
            for finding in view.findings
            if finding.supersedes_finding_id is not None
        }
        current = tuple(
            finding for finding in view.findings if finding.finding_id not in superseded
        )
        if any(
            finding.status
            in {
                EvidenceTrustStatus.ADVERSE,
                EvidenceTrustStatus.UNRESOLVED,
                EvidenceTrustStatus.INCOMPLETE,
            }
            for finding in current
        ):
            raise AuthorityDeniedError(
                "Current evidence trust finding blocks authoritative resolution"
            )

    def _validate_links(self, record: TrustedEvidenceRecord) -> None:
        target = record.semantics.target
        if isinstance(target, EvidenceRecordRef):
            if target.evidence_ref == record.semantics.evidence_ref:
                raise AuthorityDeniedError("Evidence cannot target itself")
            self._resolve_chain(self.read(target).record, {record.exact_ref})
        supersedes = record.semantics.supersedes
        if supersedes is not None:
            if supersedes.evidence_ref == record.semantics.evidence_ref:
                raise ConflictError("A correction requires a new EvidenceRef")
            self.read(supersedes)

    def _validate_draft(self, draft: TrustedEvidenceDraft) -> None:
        if not isinstance(draft, TrustedEvidenceDraft):
            raise AuthorityDeniedError("Trusted collector returned an invalid result")
        if not isinstance(draft.evidence_ref, EvidenceRef):
            raise AuthorityDeniedError("Trusted collector did not establish identity")
        if not isinstance(
            draft.target, (RunRef, OutcomeRef, EffectRef, EvidenceRecordRef)
        ):
            raise AuthorityDeniedError("Trusted collector did not exact-bind target")
        if not isinstance(draft.source, EvidenceSource):
            raise AuthorityDeniedError("Trusted collector did not establish source")
        if not isinstance(draft.collector, PrincipalRef) or not isinstance(
            draft.collector_adapter, VersionedDescriptor
        ):
            raise AuthorityDeniedError("Trusted collector provenance is incomplete")
        if not isinstance(draft.collected_at, Timestamp) or not isinstance(
            draft.observed_at, ObservedTimeProvenance
        ):
            raise AuthorityDeniedError("Trusted evidence times are incomplete")
        if not isinstance(draft.material_provenance, MaterialProvenance):
            raise AuthorityDeniedError("Material provenance is incomplete")
        if not draft.producing_principals or any(
            not isinstance(principal, PrincipalRef)
            for principal in draft.producing_principals
        ):
            raise AuthorityDeniedError("Producing principal provenance is incomplete")
        _text(draft.collection_request_ref, "collection request reference")
        if not isinstance(draft.evidence_policy, VersionedDescriptor) or not isinstance(
            draft.verification, VerificationProvenance
        ):
            raise AuthorityDeniedError(
                "Policy or verification provenance is incomplete"
            )
        if draft.supersedes is not None and not isinstance(
            draft.supersedes, EvidenceRecordRef
        ):
            raise AuthorityDeniedError("Supersession provenance is invalid")
        anchor = draft.integrity_anchor
        if isinstance(anchor, ContentDigestAnchor):
            if (
                anchor.algorithm,
                anchor.algorithm_version,
            ) not in self._allowed_content_digests:
                raise AuthorityDeniedError(
                    "Content digest algorithm/version is not allowed"
                )
            if anchor.algorithm == "sha256" and (
                len(anchor.digest) != 64
                or any(
                    character not in "0123456789abcdef" for character in anchor.digest
                )
            ):
                raise AuthorityDeniedError(
                    "Content digest is not a canonical SHA-256 digest"
                )
        elif isinstance(anchor, ExternalImmutableAnchor):
            if (
                anchor.provider_identity != draft.source.provider_identity
                or anchor.namespace != draft.source.namespace
                or anchor.collected_at != draft.collected_at
                or anchor.observed_at != draft.observed_at.observed_at
                or anchor.verification_mechanism != draft.verification.mechanism
            ):
                raise AuthorityDeniedError("External anchor provenance is substituted")
        else:
            raise AuthorityDeniedError(
                "Trusted collector did not establish an integrity anchor"
            )


def record_fingerprint(record: TrustedEvidenceRecord) -> str:
    """Recompute the versioned semantic fingerprint, excluding itself."""
    if not isinstance(record, TrustedEvidenceRecord):
        raise InvalidRequestError("Expected TrustedEvidenceRecord")
    return _fingerprint(record.semantics)


def encode_evidence_record(record: TrustedEvidenceRecord) -> str:
    """Return the deterministic closed-schema persistence representation."""
    if not isinstance(record, TrustedEvidenceRecord):
        raise InvalidRequestError("Expected TrustedEvidenceRecord")
    return _encode_evidence(record)


def decode_evidence_record(encoded: str) -> TrustedEvidenceRecord:
    """Decode only the closed evidence schema and verify its exact fingerprint."""
    if not isinstance(encoded, str):
        raise InvalidRequestError("Evidence encoding must be text")
    value = _decode_evidence(encoded)
    if not isinstance(value, TrustedEvidenceRecord):
        raise InvalidRequestError("Encoding does not contain an evidence record")
    if record_fingerprint(value) != value.record_fingerprint:
        raise InvalidRequestError("Encoded evidence fingerprint differs")
    return value


def operation_fingerprint(
    claim: EvidenceSubmissionClaim, record: TrustedEvidenceRecord
) -> str:
    """Expose deterministic replay identity for conformance tests/adapters."""
    return _fingerprint((claim, record.semantics))
