"""Deterministic blind-audit fixture and renderers for Issue #85."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass

QUESTIONS = (
    "Did the consequential external action occur?",
    "Who/what authorized it?",
    "Which exact evidence/judgment supported authorization?",
    "Which earlier evidence became stale/superseded and why could it no longer "
    "authorize the later state?",
    "Was there any point where the authoritative record was uncertain about "
    "occurrence? If the experiment does not model such uncertainty, say so.",
    "Did compensation/remediation erase the original occurrence?",
    "Why is the final authoritative disposition/history what it is?",
)


@dataclass(frozen=True, slots=True)
class AuditRecord:
    sequence: int
    kind: str
    identity: str
    exact_binding: str
    fact: str


RECORDS = (
    AuditRecord(1, "candidate", "outcome-A/v1", "run-17", "Candidate A proposed."),
    AuditRecord(
        2,
        "evaluation",
        "evaluation-E1/v3",
        "outcome-A/v1",
        "E1 supported candidate A.",
    ),
    AuditRecord(
        3,
        "supersession",
        "outcome-B/v1",
        "prior=outcome-A/v1",
        "Candidate B superseded A; E1 remains historical but targets A only.",
    ),
    AuditRecord(
        4,
        "evaluation",
        "evaluation-E2/v3",
        "outcome-B/v1",
        "E2 supported candidate B with evidence evidence:B-support.",
    ),
    AuditRecord(
        5,
        "evaluation",
        "evaluation-E3/v3",
        "outcome-B/v1",
        "E3 conflicted with E2 using evidence evidence:B-conflict.",
    ),
    AuditRecord(
        6,
        "arbitration",
        "arbitration-AB/v1",
        "E2/v3+E3/v3",
        "An independent Human arbitration upheld E2 and reversed E3 for effective use.",
    ),
    AuditRecord(
        7,
        "disposition",
        "outcome-B/v2",
        "arbitration-AB/v1",
        "Outcome B accepted from the current arbitrated effective judgment.",
    ),
    AuditRecord(
        8,
        "effect_request",
        "effect-42/v1",
        "outcome-B/v2",
        "A consequential publish Effect was requested.",
    ),
    AuditRecord(
        9,
        "human_authorization",
        "human-auth-42",
        "effect-42/v1+target+payload+correlation",
        "Human operator human-7 authorized the exact prepared operation.",
    ),
    AuditRecord(
        10,
        "external_receipt",
        "receipt-42",
        "effect-42/v1+operation-key-42",
        "The independent external system returned a commit receipt.",
    ),
    AuditRecord(
        11,
        "occurrence",
        "effect-42/v2",
        "receipt-42",
        "Independent observation confirmed the external action occurred.",
    ),
    AuditRecord(
        12,
        "compensation",
        "effect-42/v4",
        "original-occurrence=effect-42/v2",
        "Compensation completed; original occurrence remains historical.",
    ),
)


class AuditLedger:
    """Durable append-only experimental export ledger, separate from the answer key."""

    def __init__(self, database: str) -> None:
        self._connection = sqlite3.connect(database)
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS audit_records (
                sequence INTEGER PRIMARY KEY,
                kind TEXT NOT NULL,
                identity TEXT NOT NULL,
                exact_binding TEXT NOT NULL,
                fact TEXT NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS audit_records_no_update
            BEFORE UPDATE ON audit_records
            BEGIN SELECT RAISE(ABORT, 'append-only audit history'); END;
            CREATE TRIGGER IF NOT EXISTS audit_records_no_delete
            BEFORE DELETE ON audit_records
            BEGIN SELECT RAISE(ABORT, 'append-only audit history'); END;
            """
        )

    def append(self, record: AuditRecord) -> None:
        self._connection.execute(
            "INSERT INTO audit_records VALUES (?,?,?,?,?)",
            (
                record.sequence,
                record.kind,
                record.identity,
                record.exact_binding,
                record.fact,
            ),
        )
        self._connection.commit()

    def records(self) -> tuple[AuditRecord, ...]:
        return tuple(
            AuditRecord(*row)
            for row in self._connection.execute(
                "SELECT sequence,kind,identity,exact_binding,fact "
                "FROM audit_records ORDER BY sequence"
            )
        )

    def close(self) -> None:
        self._connection.close()


def packet_text() -> str:
    lines = [
        "# Blind Audit Packet — Strategic Governance-Layer Validation",
        "",
        "This packet contains exported deterministic records only. It does not "
        "contain the answer key.",
        "",
        "## Records",
        "",
    ]
    for record in RECORDS:
        lines.append(
            f"{record.sequence}. **{record.kind}** `{record.identity}` — "
            f"binding: `{record.exact_binding}`. {record.fact}"
        )
    lines.extend(
        (
            "",
            "## Scope and limitations",
            "",
            "- Occurrence uncertainty was not exercised in this narrative; no "
            "QUARANTINED/UNCERTAIN interval is claimed.",
            "- Stage 1 represents supersession, immutable Evaluations, conflict "
            "membership, arbitration, disposition, Effect occurrence and "
            "compensation. It does not execute an external service itself.",
            "- The experimental trusted gateway performed the fake external commit. "
            "Its exact Human authorization and receipt are durable experimental "
            "integration records; confirmed occurrence and compensation are Stage 1 "
            "records.",
            "",
            "## Blind-review questions",
            "",
        )
    )
    lines.extend(f"{index}. {question}" for index, question in enumerate(QUESTIONS, 1))
    return "\n".join(lines) + "\n"


def answer_key_text() -> str:
    answers = (
        "Yes. Receipt-42 and the confirmed occurrence effect-42/v2 establish it.",
        "Human operator human-7 authorized the exact effect-42/v1 operation; the "
        "trusted experimental gateway committed it.",
        "The exact-current arbitrated judgment arbitration-AB/v1, ultimately "
        "supported by E2/evidence:B-support, supported disposition and the bound "
        "Human authorization supported the Effect.",
        "E1 targets outcome-A/v1. Candidate B is a distinct successor exact-bound "
        "to A, so E1 cannot authorize B.",
        "No. This deterministic narrative never represents occurrence as uncertain.",
        "No. Compensation effect-42/v4 explicitly retains effect-42/v2 as the "
        "original occurrence.",
        "B is accepted using the current arbitrated E2/E3 effective judgment; the "
        "Effect then occurred under exact Human authorization and was compensated "
        "without deleting any earlier record.",
    )
    lines = ["# Audit Answer Key", ""]
    lines.extend(f"{index}. {answer}" for index, answer in enumerate(answers, 1))
    return "\n".join(lines) + "\n"


def records_json() -> str:
    return (
        json.dumps(
            [
                {
                    "sequence": record.sequence,
                    "kind": record.kind,
                    "identity": record.identity,
                    "exact_binding": record.exact_binding,
                    "fact": record.fact,
                }
                for record in RECORDS
            ],
            indent=2,
        )
        + "\n"
    )
