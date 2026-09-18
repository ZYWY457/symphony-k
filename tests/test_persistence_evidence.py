"""G2/M1 SQLite evidence durability, codec, and atomicity contracts."""

import sqlite3
from dataclasses import replace
from pathlib import Path

import pytest

from symphony_k.domain import ConcurrencyConflict, EventId, EvidenceRef
from symphony_k.governance import (
    ConflictError,
    EvidenceProvenanceService,
    EvidenceRecordRef,
    EvidenceTrustStatus,
    GovernanceInvariantError,
    NotFoundError,
    decode_evidence_record,
    encode_evidence_record,
    record_fingerprint,
)
from symphony_k.persistence._records import record_key
from symphony_k.persistence.sqlite import SQLiteStore
from tests.test_governance_evidence import Collector, claim, draft, finding_claim


def test_evidence_closed_codec_is_canonical_and_fingerprint_excludes_itself() -> None:
    store = SQLiteStore()
    service = EvidenceProvenanceService(store, Collector(draft()))
    record = service.register(claim()).record

    assert decode_evidence_record(encode_evidence_record(record)) == record
    assert encode_evidence_record(record) == encode_evidence_record(record)
    assert record_fingerprint(record) == record.record_fingerprint
    altered_derived = replace(record, record_fingerprint="b" * 64)
    assert record_fingerprint(altered_derived) == record.record_fingerprint
    store.close()


def test_file_backed_evidence_survives_reopen_with_exact_history(
    tmp_path: Path,
) -> None:
    database = str(tmp_path / "evidence.sqlite")
    first_store = SQLiteStore(database)
    first_service = EvidenceProvenanceService(first_store, Collector(draft()))
    original = first_service.register(claim()).record
    first_service.append_trust_finding(
        finding_claim(
            original.exact_ref,
            EvidenceTrustStatus.UNRESOLVED,
            finding_id="finding:durable",
        )
    )
    first_store.close()

    reopened = SQLiteStore(database)
    reopened_service = EvidenceProvenanceService(reopened, Collector(draft()))
    view = reopened_service.read(original.exact_ref)
    assert view.record == original
    assert tuple(item.finding_id for item in view.findings) == ("finding:durable",)
    assert reopened_service.register(claim()).record == original
    assert reopened._connection.execute(
        "SELECT COUNT(*) FROM evidence_operations"
    ).fetchone() == (1,)
    reopened.close()


def test_exact_read_rejects_fingerprint_substitution() -> None:
    store = SQLiteStore()
    service = EvidenceProvenanceService(store, Collector(draft()))
    reference = service.register(claim()).record.exact_ref

    with pytest.raises(ConflictError, match="does not match"):
        service.read(replace(reference, record_fingerprint="b" * 64))
    store.close()


def test_record_and_operation_receipt_are_atomic_on_partial_failure() -> None:
    store = SQLiteStore()
    store._connection.execute(
        "CREATE TRIGGER fail_evidence_operation BEFORE INSERT ON evidence_operations "
        "BEGIN SELECT RAISE(ABORT, 'injected partial failure'); END"
    )
    service = EvidenceProvenanceService(store, Collector(draft()))

    with pytest.raises(GovernanceInvariantError):
        service.register(claim())

    assert store._connection.execute(
        "SELECT COUNT(*) FROM evidence_records"
    ).fetchone() == (0,)
    assert store._connection.execute(
        "SELECT COUNT(*) FROM evidence_operations"
    ).fetchone() == (0,)
    store.close()


@pytest.mark.parametrize(
    "table",
    ["evidence_records", "evidence_operations", "evidence_trust_findings"],
)
def test_evidence_tables_are_append_only(table: str) -> None:
    store = SQLiteStore()
    service = EvidenceProvenanceService(store, Collector(draft()))
    reference = service.register(claim()).record.exact_ref
    service.append_trust_finding(
        finding_claim(
            reference,
            EvidenceTrustStatus.VERIFIED,
            finding_id="finding:append-only",
        )
    )

    with pytest.raises(sqlite3.IntegrityError, match="append-only history"):
        store._connection.execute(f"DELETE FROM {table}")
    store.close()


def test_identity_collision_never_overwrites_original_row() -> None:
    store = SQLiteStore()
    collector = Collector(draft())
    service = EvidenceProvenanceService(store, collector)
    original = service.register(claim()).record
    collector.result = replace(draft(), collection_request_ref="request:altered")

    with pytest.raises(ConflictError):
        service.register(claim(key="operation:2"))

    assert service.read(original.exact_ref).record == original
    assert store._connection.execute(
        "SELECT COUNT(*) FROM evidence_records"
    ).fetchone() == (1,)
    assert store._connection.execute(
        "SELECT COUNT(*) FROM evidence_operations"
    ).fetchone() == (1,)
    store.close()


def test_supporting_record_and_lifecycle_routes_cannot_mint_evidence_trust() -> None:
    store = SQLiteStore()
    service = EvidenceProvenanceService(store, Collector(draft()))
    record = service.register(claim()).record

    assert record_key(record) is None
    assert not hasattr(store, "register_evidence")
    store._record_provenance(record, EventId.new())
    assert store._connection.execute(
        "SELECT COUNT(*) FROM supporting_records"
    ).fetchone() == (0,)
    assert service.read(record.exact_ref).record == record
    store.close()


def test_operation_receipt_detects_direct_altered_replay_without_new_record() -> None:
    store = SQLiteStore()
    service = EvidenceProvenanceService(store, Collector(draft()))
    original = service.register(claim()).record
    stored = store._connection.execute(
        "SELECT record FROM evidence_records WHERE evidence_ref=?",
        (original.exact_ref.evidence_ref.value,),
    ).fetchone()
    operation = store._connection.execute(
        "SELECT claim FROM evidence_operations WHERE operation_key=?",
        (claim().idempotency_key,),
    ).fetchone()
    assert stored is not None and operation is not None

    with pytest.raises(ConcurrencyConflict):
        store._evidence_register(
            original.exact_ref.evidence_ref.value,
            original.exact_ref.record_fingerprint,
            stored[0],
            claim().idempotency_key,
            "b" * 64,
            operation[0],
            (),
        )
    assert service.read(original.exact_ref).record == original
    store.close()


def test_missing_exact_evidence_reference_is_not_fabricated_by_query_port() -> None:
    store = SQLiteStore()
    service = EvidenceProvenanceService(store, Collector(draft()))
    missing = EvidenceRecordRef(EvidenceRef("evidence:missing"), "0" * 64)

    with pytest.raises(NotFoundError):
        service.read(missing)
    assert store._connection.execute(
        "SELECT COUNT(*) FROM evidence_records"
    ).fetchone() == (0,)
    store.close()
