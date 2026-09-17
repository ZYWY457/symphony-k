"""Blind packet is deterministic, separate and covers all registered questions."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from experiments.governance_layer_validation.audit import (  # noqa: E402
    QUESTIONS,
    RECORDS,
    AuditLedger,
    answer_key_text,
    packet_text,
    records_json,
)

ROOT = Path(__file__).parents[2]
ARTIFACTS = ROOT / "experiments" / "governance_layer_validation" / "artifacts"


def test_audit_packet_and_answer_key_are_separate_and_reproducible() -> None:
    packet = (ARTIFACTS / "blind-audit-packet.md").read_text(encoding="utf-8")
    key = (ARTIFACTS / "audit-answer-key.md").read_text(encoding="utf-8")
    assert packet == packet_text()
    assert key == answer_key_text()
    assert "Audit Answer Key" not in packet
    assert len(QUESTIONS) == 7


def test_machine_readable_audit_fixture_is_reproducible() -> None:
    assert (ARTIFACTS / "audit-records.json").read_text(
        encoding="utf-8"
    ) == records_json()
    assert [record.sequence for record in RECORDS] == list(range(1, 13))


def test_audit_records_survive_process_boundary_and_are_append_only(
    tmp_path: Path,
) -> None:
    database = str(tmp_path / "audit.sqlite")
    ledger = AuditLedger(database)
    for record in RECORDS:
        ledger.append(record)
    ledger.close()
    reopened = AuditLedger(database)
    assert reopened.records() == RECORDS
    reopened.close()


def test_registered_result_matrix_is_complete() -> None:
    summary = json.loads(
        (ARTIFACTS / "result-summary.json").read_text(encoding="utf-8")
    )
    assert [item["id"] for item in summary["adversarial"]] == [
        f"G{index}" for index in range(1, 9)
    ]
    assert [item["id"] for item in summary["legal"]] == [
        f"H{index}" for index in range(1, 6)
    ]
    assert summary["scores"]["D_audit_reconstruction"].startswith("PENDING")
