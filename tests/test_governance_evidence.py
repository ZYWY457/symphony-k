"""G2/M1 trusted evidence boundary and adversarial service contracts."""

from contextlib import nullcontext
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    DomainError,
    EffectId,
    EntityVersion,
    EvidenceRef,
    InvalidDomainValue,
    OutcomeId,
    RunId,
    Timestamp,
)
from symphony_k.governance import (
    AuthorityDeniedError,
    ConflictError,
    ContentDigestAnchor,
    ContentDigestClaim,
    EffectRef,
    EvidenceProvenanceService,
    EvidenceRecordRef,
    EvidenceSource,
    EvidenceSubmissionClaim,
    EvidenceTrustFindingClaim,
    EvidenceTrustFindingRecord,
    EvidenceTrustStatus,
    ExternalAnchorClaim,
    ExternalImmutableAnchor,
    GovernanceFacadeError,
    GovernanceInvariantError,
    InvalidRequestError,
    MaterialProvenance,
    MaterialProvenanceClaim,
    NotFoundError,
    ObservedTimeProvenance,
    OutcomeRef,
    PrincipalRef,
    RunRef,
    TrustedEvidenceDraft,
    TrustedEvidenceRecord,
    VerificationProvenance,
    VersionedDescriptor,
    encode_evidence_record,
    record_fingerprint,
)
from symphony_k.persistence.sqlite import SQLiteStore

NOW = Timestamp(datetime(2026, 9, 18, 4, 0, tzinfo=UTC))
LATER = Timestamp(NOW.value + timedelta(minutes=1))
RUN = RunRef(RunId.new(), EntityVersion(7))
CALLER = ActorIdentity(ActorId.new(), ActorType.WORKER)
COLLECTOR = PrincipalRef("collector:approved", "issuer:trusted", "assertion:c1")
PRODUCER = PrincipalRef("producer:actual", "issuer:trusted", "assertion:p1")
VERIFIER = PrincipalRef("verifier:approved", "issuer:trusted", "assertion:v1")
ADAPTER = VersionedDescriptor("collector-adapter", "3")
METHOD = MaterialProvenance(
    VersionedDescriptor("method:test", "2"),
    VersionedDescriptor("tool:pytest", "9"),
    VersionedDescriptor("provider:local", "1"),
)
POLICY = VersionedDescriptor("evidence-policy", "4")
VERIFY_MECHANISM = VersionedDescriptor("digest-verifier", "1")
DIGEST = "a" * 64
CALLER_REQUESTED = EvidenceRef("caller:requested")
EVIDENCE_ONE = EvidenceRef("evidence:one")


class Collector:
    def __init__(self, result: TrustedEvidenceDraft) -> None:
        self.result = result

    def collect(self, claim: EvidenceSubmissionClaim) -> TrustedEvidenceDraft:
        return self.result

    def establish_finding(
        self, claim: EvidenceTrustFindingClaim
    ) -> EvidenceTrustFindingRecord:
        return EvidenceTrustFindingRecord(
            claim.requested_finding_id or "finding:provider-issued",
            claim.evidence_record_claim,
            claim.status_claim,
            VERIFIER,
            POLICY,
            LATER,
            "trusted post-collection review",
            claim.supersedes_finding_id_claim,
        )


def claim(
    *,
    key: str = "operation:1",
    target: RunRef | OutcomeRef | EffectRef | EvidenceRef = RUN,
    requested: EvidenceRef | None = CALLER_REQUESTED,
) -> EvidenceSubmissionClaim:
    return EvidenceSubmissionClaim(
        target=target,
        source_locator_claim="https://mutable.invalid/latest",
        caller_identity_claim=CALLER,
        idempotency_key=key,
        requested_evidence_ref=requested,
        integrity_anchor_claim=ContentDigestClaim("sha256", "fake", "0" * 64),
        observed_at_claim=Timestamp(NOW.value - timedelta(days=1)),
        material_provenance_claim=MaterialProvenanceClaim(
            "fabricated-method",
            "999",
            "fabricated-tool",
            "999",
            "fabricated-provider",
            "999",
        ),
        producing_principal_claims=("principal:fabricated",),
        source_provider_claim="provider:fabricated",
        source_namespace_claim="namespace:fabricated",
        collector_identity_claim="collector:fabricated",
        trusted_claim=True,
    )


def draft(
    evidence_ref: EvidenceRef = EVIDENCE_ONE,
    *,
    target: RunRef | OutcomeRef | EffectRef | EvidenceRecordRef = RUN,
    anchor: ContentDigestAnchor | ExternalImmutableAnchor | None = None,
    supersedes: EvidenceRecordRef | None = None,
) -> TrustedEvidenceDraft:
    return TrustedEvidenceDraft(
        evidence_ref=evidence_ref,
        target=target,
        integrity_anchor=anchor
        or ContentDigestAnchor("sha256", "1", DIGEST, "exact-bytes"),
        source=EvidenceSource("test-output", "provider:trusted", "build:42"),
        collector=COLLECTOR,
        collector_adapter=ADAPTER,
        collected_at=NOW,
        observed_at=ObservedTimeProvenance(NOW, "observation:42"),
        material_provenance=METHOD,
        producing_principals=(PRODUCER,),
        collection_request_ref="collection-request:42",
        evidence_policy=POLICY,
        verification=VerificationProvenance(VERIFIER, VERIFY_MECHANISM, NOW),
        supersedes=supersedes,
    )


def service_for(
    store: SQLiteStore, value: TrustedEvidenceDraft
) -> tuple[EvidenceProvenanceService, Collector]:
    collector = Collector(value)
    return EvidenceProvenanceService(store, collector), collector


def test_caller_trust_source_collector_and_principal_claims_grant_no_trust() -> None:
    store = SQLiteStore()
    service, _ = service_for(store, draft())

    view = service.register(claim())

    assert view.record.semantics.evidence_ref == EvidenceRef("evidence:one")
    assert view.record.semantics.source.provider_identity == "provider:trusted"
    assert view.record.semantics.collector == COLLECTOR
    assert view.record.semantics.producing_principals == (PRODUCER,)
    assert view.record.semantics.material_provenance == METHOD
    assert view.record.semantics.observed_at.observed_at == NOW
    store.close()


def test_exact_replay_returns_original_after_unrelated_write() -> None:
    store = SQLiteStore()
    service, collector = service_for(store, draft())
    request = claim()
    first = service.register(request)
    collector.result = draft(EvidenceRef("evidence:other"))
    service.register(claim(key="operation:other"))
    collector.result = draft()

    assert service.register(request) == first
    assert service.lookup(EvidenceRef("evidence:one")) == first
    store.close()


def test_same_exact_record_under_new_operation_reuses_immutable_identity() -> None:
    store = SQLiteStore()
    service, _ = service_for(store, draft())
    first = service.register(claim()).record

    second = service.register(claim(key="operation:2")).record

    assert second == first
    assert store._connection.execute(
        "SELECT COUNT(*) FROM evidence_records"
    ).fetchone() == (1,)
    assert store._connection.execute(
        "SELECT COUNT(*) FROM evidence_operations"
    ).fetchone() == (2,)
    store.close()


def test_same_idempotency_key_with_altered_request_is_rejected() -> None:
    store = SQLiteStore()
    service, _ = service_for(store, draft())
    service.register(claim())

    with pytest.raises(ConflictError, match="operation key"):
        service.register(
            replace(claim(), source_locator_claim="https://different.invalid")
        )
    store.close()


def test_same_idempotency_key_with_altered_trusted_result_is_rejected() -> None:
    store = SQLiteStore()
    service, collector = service_for(store, draft())
    service.register(claim())
    collector.result = replace(draft(), collected_at=LATER)

    with pytest.raises(ConflictError, match="operation key"):
        service.register(claim())
    store.close()


@pytest.mark.parametrize(
    "changed",
    [
        replace(draft().integrity_anchor, digest="b" * 64),
        ContentDigestAnchor("sha256", "1", DIGEST, "canonical-json"),
    ],
)
def test_same_evidence_id_with_altered_integrity_is_collision(
    changed: ContentDigestAnchor,
) -> None:
    store = SQLiteStore()
    service, collector = service_for(store, draft())
    service.register(claim())
    collector.result = draft(anchor=changed)

    with pytest.raises(ConflictError, match="another immutable record"):
        service.register(claim(key="operation:2"))
    store.close()


def test_same_evidence_id_with_altered_target_or_version_is_collision() -> None:
    store = SQLiteStore()
    service, collector = service_for(store, draft())
    service.register(claim())
    collector.result = draft(target=replace(RUN, version=EntityVersion(8)))

    with pytest.raises(ConflictError, match="another immutable record"):
        service.register(
            claim(key="operation:2", target=replace(RUN, version=EntityVersion(8)))
        )
    store.close()


@pytest.mark.parametrize(
    "field,value",
    [
        ("source", EvidenceSource("test-output", "provider:other", "build:42")),
        ("collector", PrincipalRef("collector:other", "issuer:trusted", "a:2")),
        ("collected_at", LATER),
        (
            "material_provenance",
            replace(METHOD, method=VersionedDescriptor("method:test", "3")),
        ),
        ("evidence_policy", VersionedDescriptor("evidence-policy", "5")),
        (
            "producing_principals",
            (PrincipalRef("producer:other", "issuer:trusted", "p:2"),),
        ),
        (
            "verification",
            replace(
                draft().verification,
                verifier=PrincipalRef("verifier:other", "issuer:trusted", "v:2"),
            ),
        ),
    ],
)
def test_same_evidence_id_with_altered_provenance_is_collision(
    field: str, value: object
) -> None:
    store = SQLiteStore()
    service, collector = service_for(store, draft())
    service.register(claim())
    collector.result = replace(draft(), **{field: value})

    with pytest.raises(ConflictError, match="another immutable record"):
        service.register(claim(key=f"operation:{field}"))
    store.close()


def test_exact_target_scope_rejects_version_and_entity_substitution() -> None:
    store = SQLiteStore()
    service, _ = service_for(store, draft())
    reference = service.register(claim()).record.exact_ref

    with pytest.raises(AuthorityDeniedError, match="exact target"):
        service.resolve_trusted(
            reference, expected_target=replace(RUN, version=EntityVersion(8))
        )
    with pytest.raises(AuthorityDeniedError, match="exact target"):
        service.resolve_trusted(
            reference, expected_target=RunRef(RunId.new(), RUN.version)
        )
    store.close()


def external_anchor(
    *, provider: str = "provider:trusted", revision: str = "revision:immutable"
) -> ExternalImmutableAnchor:
    return ExternalImmutableAnchor(
        provider,
        "build:42",
        "receipt:signed:42",
        VERIFY_MECHANISM,
        "provider://objects/42",
        revision,
        "assertion:provider:42",
        NOW,
        NOW,
    )


def test_mutable_external_locator_or_provider_revision_substitution_fails_closed() -> (
    None
):
    store = SQLiteStore()
    value = draft(anchor=external_anchor(provider="provider:caller"))
    service, collector = service_for(store, value)
    request = replace(
        claim(),
        integrity_anchor_claim=ExternalAnchorClaim(
            "provider:trusted", "https://mutable.invalid", "free-form"
        ),
    )

    with pytest.raises(AuthorityDeniedError, match="substituted"):
        service.register(request)

    collector.result = draft(anchor=external_anchor())
    service.register(request)
    collector.result = draft(anchor=external_anchor(revision="revision:other"))
    with pytest.raises(ConflictError, match="another immutable record"):
        service.register(replace(request, idempotency_key="operation:2"))
    store.close()


def test_mutable_locator_without_trusted_integrity_anchor_fails_closed() -> None:
    store = SQLiteStore()
    without_anchor = replace(draft(), integrity_anchor=None)  # type: ignore[arg-type]
    service, _ = service_for(store, without_anchor)
    request = replace(
        claim(),
        integrity_anchor_claim=ExternalAnchorClaim(
            "provider:fabricated", "https://mutable.invalid", "free-form"
        ),
    )

    with pytest.raises(AuthorityDeniedError, match="integrity anchor"):
        service.register(request)
    assert store._connection.execute(
        "SELECT COUNT(*) FROM evidence_records"
    ).fetchone() == (0,)
    store.close()


def test_digest_algorithm_version_must_be_allowed_and_is_identity_bound() -> None:
    store = SQLiteStore()
    unapproved = ContentDigestAnchor("sha256", "2", DIGEST, "exact-bytes")
    service, collector = service_for(store, draft(anchor=unapproved))

    with pytest.raises(AuthorityDeniedError, match="not allowed"):
        service.register(claim())

    collector.result = draft()
    service.register(claim())
    collector.result = draft(
        anchor=ContentDigestAnchor("sha256", "1", "b" * 64, "exact-bytes")
    )
    with pytest.raises(ConflictError):
        service.register(claim(key="operation:2"))
    store.close()


def test_unresolved_and_self_referential_evidence_targets_fail_closed() -> None:
    store = SQLiteStore()
    missing = EvidenceRecordRef(EvidenceRef("evidence:missing"), "0" * 64)
    service, collector = service_for(store, draft(target=missing))

    with pytest.raises(NotFoundError):
        service.register(claim(target=missing.evidence_ref))

    collector.result = draft(
        target=EvidenceRecordRef(EvidenceRef("evidence:one"), "0" * 64)
    )
    with pytest.raises(AuthorityDeniedError, match="itself"):
        service.register(claim(target=EvidenceRef("evidence:one")))
    store.close()


def test_evidence_on_evidence_resolves_exact_record_without_substitution() -> None:
    store = SQLiteStore()
    service, collector = service_for(store, draft())
    first = service.register(claim()).record.exact_ref
    collector.result = draft(EvidenceRef("evidence:two"), target=first)
    second = service.register(
        claim(key="operation:2", target=first.evidence_ref)
    ).record.exact_ref

    assert service.resolve_trusted(second).record.semantics.target == first
    wrong = replace(first, record_fingerprint="b" * 64)
    collector.result = draft(EvidenceRef("evidence:three"), target=wrong)
    with pytest.raises(AuthorityDeniedError, match="requested exact target"):
        service.register(claim(key="operation:3", target=first.evidence_ref))
    store.close()


def test_cyclic_evidence_target_from_corrupt_store_fails_closed() -> None:
    store = SQLiteStore()
    service, collector = service_for(store, draft())
    first = service.register(claim()).record
    collector.result = draft(EvidenceRef("evidence:two"), target=first.exact_ref)
    second = service.register(
        claim(key="operation:2", target=first.exact_ref.evidence_ref)
    ).record
    store.close()

    first_semantics = replace(first.semantics, target=second.exact_ref)
    first_cycle = TrustedEvidenceRecord(first_semantics, first.record_fingerprint)
    first_cycle = replace(
        first_cycle, record_fingerprint=record_fingerprint(first_cycle)
    )
    second_semantics = replace(second.semantics, target=first_cycle.exact_ref)
    second_cycle = TrustedEvidenceRecord(second_semantics, second.record_fingerprint)
    second_cycle = replace(
        second_cycle, record_fingerprint=record_fingerprint(second_cycle)
    )

    class CyclicStore:
        def _evidence_read_snapshot(self):
            return nullcontext()

        def _evidence_load_exact(self, evidence_ref: str, fingerprint: str) -> str:
            reference = EvidenceRecordRef(EvidenceRef(evidence_ref), fingerprint)
            if reference == first_cycle.exact_ref:
                return encode_evidence_record(first_cycle)
            if reference == second.exact_ref:
                return encode_evidence_record(second_cycle)
            raise AssertionError("unexpected exact reference")

        def _evidence_load_identity(self, evidence_ref: str) -> tuple[str, str]:
            return (
                first_cycle.record_fingerprint,
                encode_evidence_record(first_cycle),
            )

        def _evidence_findings(
            self, evidence_ref: str, fingerprint: str
        ) -> tuple[str, ...]:
            return ()

        def _evidence_register(self, *args: object) -> str:
            raise AssertionError("not used")

        def _evidence_append_finding(self, *args: object) -> None:
            raise AssertionError("not used")

    corrupt_service = EvidenceProvenanceService(CyclicStore(), Collector(draft()))
    with pytest.raises(GovernanceInvariantError, match="integrity differs"):
        corrupt_service.resolve_trusted(first_cycle.exact_ref)


def finding(
    reference: EvidenceRecordRef,
    status: EvidenceTrustStatus,
    *,
    finding_id: str,
    supersedes: str | None = None,
) -> EvidenceTrustFindingRecord:
    return EvidenceTrustFindingRecord(
        finding_id,
        reference,
        status,
        VERIFIER,
        POLICY,
        LATER,
        "post-collection trust review",
        supersedes,
    )


def finding_claim(
    reference: EvidenceRecordRef,
    status: EvidenceTrustStatus,
    *,
    finding_id: str,
    supersedes: str | None = None,
) -> EvidenceTrustFindingClaim:
    return EvidenceTrustFindingClaim(
        reference,
        status,
        "untrusted requested reason",
        CALLER,
        finding_id,
        supersedes,
    )


@pytest.mark.parametrize(
    "status",
    [
        EvidenceTrustStatus.ADVERSE,
        EvidenceTrustStatus.UNRESOLVED,
        EvidenceTrustStatus.INCOMPLETE,
    ],
)
def test_adverse_unresolved_or_incomplete_finding_blocks_resolution_without_rewrite(
    status: EvidenceTrustStatus,
) -> None:
    store = SQLiteStore()
    service, _ = service_for(store, draft())
    original = service.register(claim()).record
    service.append_trust_finding(
        finding_claim(original.exact_ref, status, finding_id=f"finding:{status.value}")
    )

    assert service.read(original.exact_ref).record == original
    with pytest.raises(AuthorityDeniedError, match="finding blocks"):
        service.resolve_trusted(original.exact_ref)
    store.close()


def test_verified_finding_can_append_only_supersede_adverse_finding() -> None:
    store = SQLiteStore()
    service, _ = service_for(store, draft())
    reference = service.register(claim()).record.exact_ref
    service.append_trust_finding(
        finding_claim(reference, EvidenceTrustStatus.ADVERSE, finding_id="finding:1")
    )
    service.append_trust_finding(
        finding_claim(
            reference,
            EvidenceTrustStatus.VERIFIED,
            finding_id="finding:2",
            supersedes="finding:1",
        )
    )

    assert len(service.resolve_trusted(reference).findings) == 2
    store.close()


def test_caller_cannot_submit_complete_trusted_finding_record() -> None:
    store = SQLiteStore()
    service, _ = service_for(store, draft())
    reference = service.register(claim()).record.exact_ref
    trusted_body = finding(
        reference, EvidenceTrustStatus.VERIFIED, finding_id="finding:fabricated"
    )

    with pytest.raises(InvalidRequestError, match="EvidenceTrustFindingClaim"):
        service.append_trust_finding(trusted_body)  # type: ignore[arg-type]
    assert service.read(reference).findings == ()
    store.close()


def test_correction_uses_new_identity_and_preserves_both_records() -> None:
    store = SQLiteStore()
    service, collector = service_for(store, draft())
    original = service.register(claim()).record
    collector.result = draft(
        EvidenceRef("evidence:corrected"),
        anchor=ContentDigestAnchor("sha256", "1", "b" * 64, "exact-bytes"),
        supersedes=original.exact_ref,
    )
    corrected = service.register(claim(key="operation:2")).record

    assert service.read(original.exact_ref).record == original
    assert service.read(corrected.exact_ref).record == corrected
    assert corrected.semantics.supersedes == original.exact_ref
    store.close()


def test_registration_does_not_create_evaluation_or_mutate_outcome() -> None:
    store = SQLiteStore()
    service, _ = service_for(store, draft())
    before = store._connection.total_changes

    service.register(claim())

    assert store._connection.execute("SELECT COUNT(*) FROM heads").fetchone() == (0,)
    assert store._connection.execute("SELECT COUNT(*) FROM events").fetchone() == (0,)
    assert store._connection.total_changes > before
    store.close()


def test_provider_failure_is_caller_safe() -> None:
    class BrokenCollector:
        def collect(self, claim: EvidenceSubmissionClaim) -> TrustedEvidenceDraft:
            raise RuntimeError("secret provider credential")

    store = SQLiteStore()
    service = EvidenceProvenanceService(store, BrokenCollector())
    with pytest.raises(GovernanceInvariantError) as captured:
        service.register(claim())
    assert "secret provider credential" not in str(captured.value)
    store.close()


@pytest.mark.parametrize(
    "requested",
    [
        RUN,
        OutcomeRef(OutcomeId.new(), RUN.version),
        EffectRef(EffectId.new(), RUN.version),
    ],
)
@pytest.mark.parametrize("change", ["version", "identity", "family"])
def test_registration_rejects_provider_target_substitution_without_writes(
    requested: RunRef | OutcomeRef | EffectRef, change: str
) -> None:
    if change == "version":
        substituted = replace(requested, version=EntityVersion(8))
    elif change == "identity":
        if isinstance(requested, RunRef):
            substituted = replace(requested, run_id=RunId.new())
        elif isinstance(requested, OutcomeRef):
            substituted = replace(requested, outcome_id=OutcomeId.new())
        else:
            substituted = replace(requested, effect_id=EffectId.new())
    else:
        substituted = (
            OutcomeRef(OutcomeId.new(), RUN.version)
            if isinstance(requested, RunRef)
            else RUN
        )
    store = SQLiteStore()
    service, collector = service_for(store, draft(target=substituted))
    request = claim(target=requested)
    with pytest.raises(AuthorityDeniedError, match="requested exact target"):
        service.register(request)
    for table in ("evidence_records", "evidence_operations", "events", "heads"):
        assert store._connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone() == (0,)
    # Rejection did not consume the operation key; exact target succeeds and replays.
    collector.result = draft(target=requested)
    original = service.register(request)
    assert service.register(request) == original
    assert service.resolve_trusted(original.record.exact_ref) == original
    store.close()


@pytest.mark.parametrize("requested_exists", [False, True])
def test_evidence_target_identity_cannot_be_replaced_by_existing_record(
    requested_exists: bool,
) -> None:
    store = SQLiteStore()
    service, collector = service_for(store, draft(EvidenceRef("target:Y")))
    other = service.register(claim()).record.exact_ref
    requested = EvidenceRef("target:X")
    if requested_exists:
        collector.result = draft(requested)
        service.register(claim(key="target:X"))
    before = store._connection.total_changes
    collector.result = draft(EvidenceRef("child"), target=other)
    with pytest.raises(AuthorityDeniedError if requested_exists else NotFoundError):
        service.register(claim(key="child", target=requested))
    assert store._connection.total_changes == before
    assert store._connection.execute(
        "SELECT COUNT(*) FROM evidence_operations WHERE operation_key='child'"
    ).fetchone() == (0,)
    with pytest.raises(NotFoundError):
        service.lookup(EvidenceRef("child"))
    assert store._connection.execute("SELECT COUNT(*) FROM events").fetchone() == (0,)
    store.close()


@pytest.mark.parametrize("operation", ["collect", "establish_finding"])
@pytest.mark.parametrize(
    "provider_error,public_error",
    [
        (InvalidDomainValue, InvalidRequestError),
        (AuthorityDeniedError, AuthorityDeniedError),
        (DomainError, GovernanceInvariantError),
        (GovernanceFacadeError, GovernanceInvariantError),
        (RuntimeError, GovernanceInvariantError),
    ],
)
def test_provider_boundary_sanitizes_all_exception_families(
    operation: str,
    provider_error: type[Exception],
    public_error: type[GovernanceFacadeError],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = SQLiteStore()
    service, collector = service_for(store, draft())
    original = service.register(claim())
    failure = provider_error("SENTINEL-private-provider-assertion")

    def fail(request: object) -> None:
        raise failure

    monkeypatch.setattr(collector, operation, fail)
    before = store._connection.total_changes
    with pytest.raises(public_error) as caught:
        if operation == "collect":
            service.register(claim(key="failure"))
        else:
            service.append_trust_finding(
                finding_claim(
                    original.record.exact_ref,
                    EvidenceTrustStatus.ADVERSE,
                    finding_id="failure",
                )
            )
    assert type(caught.value) is public_error
    assert "SENTINEL" not in str(caught.value)
    assert caught.value.__cause__ is failure
    assert store._connection.total_changes == before
    assert service.resolve_trusted(original.record.exact_ref) == original
    store.close()
