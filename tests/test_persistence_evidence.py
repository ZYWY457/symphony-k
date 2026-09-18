"""G2/M1 SQLite evidence durability, codec, and atomicity contracts."""

import sqlite3
from dataclasses import replace
from pathlib import Path

import pytest

from symphony_k.domain import ConcurrencyConflict, EventId, EvidenceRef
from symphony_k.governance import (
    AuthorityDeniedError,
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
from tests.test_governance_evidence import (
    Collector,
    claim,
    draft,
    external_anchor,
    finding_claim,
)


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


@pytest.mark.parametrize("depth", [0, 1, 2])
@pytest.mark.parametrize(
    "allowed", [frozenset(), frozenset({("sha256", "2")}), frozenset({("sha512", "1")})]
)
def test_reopened_digest_policy_blocks_trusted_use_but_preserves_history(
    tmp_path: Path, depth: int, allowed: frozenset[tuple[str, str]]
) -> None:
    database = str(tmp_path / "digest-policy.sqlite")
    store = SQLiteStore(database)
    collector = Collector(draft())
    service = EvidenceProvenanceService(store, collector)
    original = service.register(claim())
    views = [original]
    for index in range(depth):
        target = views[-1].record.exact_ref
        # External anchors remain eligible: only the leaf's content policy denies.
        collector.result = draft(
            EvidenceRef(f"parent:{index}"), target=target, anchor=external_anchor()
        )
        views.append(
            service.register(claim(key=f"parent:{index}", target=target.evidence_ref))
        )
    root = views[-1].record.exact_ref
    assert service.resolve_trusted(root) == views[-1]
    store.close()

    reopened = SQLiteStore(database)
    restricted = EvidenceProvenanceService(
        reopened, collector, allowed_content_digests=allowed
    )
    before = reopened._connection.total_changes
    for view in views:
        reference = view.record.exact_ref
        assert restricted.read(reference) == view
        assert restricted.lookup(reference.evidence_ref) == view
        for query in (reference, reference.evidence_ref):
            with pytest.raises(AuthorityDeniedError, match="algorithm/version"):
                restricted.resolve_trusted(query)
            assert not reopened._connection.in_transaction
    assert reopened._connection.total_changes == before
    # The stored bytes and fingerprints survive; restoring policy restores eligibility.
    restored = EvidenceProvenanceService(reopened, collector)
    assert restored.resolve_trusted(root) == views[-1]
    reopened.close()


@pytest.mark.parametrize("initially_adverse", [True, False])
@pytest.mark.parametrize("by_identity", [True, False])
def test_chain_resolution_uses_one_snapshot_during_independent_writer_findings(
    tmp_path: Path, initially_adverse: bool, by_identity: bool
) -> None:
    database = str(tmp_path / "snapshot.sqlite")
    writer = SQLiteStore(database)
    # WAL permits both public writer operations to commit while the reader stays open.
    assert writer._connection.execute("PRAGMA journal_mode=WAL").fetchone() == ("wal",)
    collector = Collector(draft(EvidenceRef("B")))
    writing = EvidenceProvenanceService(writer, collector)
    b = writing.register(claim(key="B")).record.exact_ref
    collector.result = draft(EvidenceRef("A"), target=b)
    a = writing.register(claim(key="A", target=b.evidence_ref)).record.exact_ref
    if initially_adverse:
        writing.append_trust_finding(
            finding_claim(b, EvidenceTrustStatus.ADVERSE, finding_id="B-bad")
        )

    class InterleavedStore(SQLiteStore):
        switched = False

        def _evidence_findings(
            self, evidence_ref: str, record_fingerprint: str
        ) -> tuple[str, ...]:
            rows = super()._evidence_findings(evidence_ref, record_fingerprint)
            if evidence_ref == a.evidence_ref.value and not self.switched:
                self.switched = True
                writing.append_trust_finding(
                    finding_claim(a, EvidenceTrustStatus.ADVERSE, finding_id="A-bad")
                )
                writing.append_trust_finding(
                    finding_claim(
                        b,
                        EvidenceTrustStatus.VERIFIED,
                        finding_id="B-good",
                        supersedes="B-bad" if initially_adverse else None,
                    )
                )
            return rows

    reader = InterleavedStore(database)
    reading = EvidenceProvenanceService(reader, collector)
    query = a.evidence_ref if by_identity else a
    statements: list[str] = []
    reader._connection.set_trace_callback(statements.append)
    before = reader._connection.total_changes
    if initially_adverse:
        # Before/during/after the writes A and B were NEVER jointly trusted.
        with pytest.raises(AuthorityDeniedError, match="finding blocks"):
            reading.resolve_trusted(query)
    else:
        # The old snapshot really was trusted, so it remains a valid observation.
        view = reading.resolve_trusted(query)
        assert view.record.exact_ref == a
        assert view.findings == ()
    reader._connection.set_trace_callback(None)
    assert reader.switched
    assert reader._connection.total_changes == before
    assert statements[0] == "BEGIN" and statements[-1] == "ROLLBACK"
    assert all(sql.startswith(("BEGIN", "SELECT", "ROLLBACK")) for sql in statements)
    assert not reader._connection.in_transaction
    # A new observation sees A's adverse finding, while B is now eligible.
    with pytest.raises(AuthorityDeniedError, match="finding blocks"):
        reading.resolve_trusted(query)
    assert reading.resolve_trusted(b).record.exact_ref == b
    assert len(reading.read(a).findings) == 1
    # Success and failure both release the snapshot and permit later writes.
    reading.append_trust_finding(
        finding_claim(
            a, EvidenceTrustStatus.VERIFIED, finding_id="A-good", supersedes="A-bad"
        )
    )
    assert reading.resolve_trusted(a).record.exact_ref == a
    assert not reader._connection.in_transaction
    reader.close()
    writer.close()


@pytest.mark.parametrize("journal_mode", ["delete", "wal"])
def test_trusted_resolution_needs_no_writer_lock(
    tmp_path: Path, journal_mode: str
) -> None:
    database = str(tmp_path / "read-only.sqlite")
    writer = SQLiteStore(database)
    assert writer._connection.execute(
        f"PRAGMA journal_mode={journal_mode}"
    ).fetchone() == (journal_mode,)
    service = EvidenceProvenanceService(writer, Collector(draft()))
    original = service.register(claim())
    reader = SQLiteStore(database)
    reader._connection.execute("PRAGMA busy_timeout=0")
    reading = EvidenceProvenanceService(reader, Collector(draft()))
    before = reader._connection.total_changes
    # A reserved writer lock must not prevent an ordinary consistent read.
    with writer._transaction():
        assert reading.resolve_trusted(original.record.exact_ref) == original
    assert reader._connection.total_changes == before
    assert not reader._connection.in_transaction
    reader.close()
    writer.close()


def test_resolution_does_not_borrow_or_rollback_an_existing_transaction() -> None:
    store = SQLiteStore()
    service = EvidenceProvenanceService(store, Collector(draft()))
    original = service.register(claim())
    with store._transaction():
        with pytest.raises(ConflictError, match="idle connection"):
            service.resolve_trusted(original.record.exact_ref)
        assert store._connection.in_transaction
    assert service.resolve_trusted(original.record.exact_ref) == original
    store.close()
