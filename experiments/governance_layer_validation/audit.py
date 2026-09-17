"""Executed deterministic audit scenario and renderers for Issue #86."""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from uuid import UUID

from symphony_k.domain import (
    ActorId,
    ActorIdentity,
    ActorType,
    Effect,
    EffectAuthorizationStatus,
    EffectCompensationStartSemantics,
    EffectState,
    EntityVersion,
    Evaluation,
    EvaluationArbitrationRecord,
    EvaluationConfidence,
    EvaluationId,
    EvaluationMethodRef,
    EvaluationResult,
    EvaluationState,
    EvaluationTargetRef,
    EvaluationVerdict,
    EventId,
    EvidenceRef,
    ExecutionProfileRef,
    Outcome,
    OutcomeEvaluationEffectiveUseSnapshot,
    OutcomeId,
    OutcomeState,
    Run,
    RunId,
    RunState,
    TaskId,
)
from symphony_k.domain.evaluation_effective_use import derive_evaluation_effective_use
from symphony_k.persistence.sqlite import SQLiteStore
from tests import (
    test_effect_observation_quarantine_semantic_transitions as occurrence_fx,
)
from tests import test_effect_remediation_semantic_transitions as remediation_fx
from tests import (
    test_evaluation_conflict_arbitration_semantic_transitions as arbitration_fx,
)
from tests import test_outcome_disposition_semantic_transitions as disposition_fx
from tests import test_outcome_supersession_semantic_transitions as supersession_fx
from tests.persistence_fixtures import seed_snapshot

from .facade import (
    FakeExternalSystem,
    GovernanceFacade,
    HumanAuthorization,
    issue_test_ports,
)

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

A_ID = OutcomeId(UUID(int=101))
B_ID = disposition_fx.outcome().outcome_id
E1_ID = EvaluationId(UUID(int=201))
E2_ID = EvaluationId(disposition_fx.OTHER)
E3_ID = EvaluationId(UUID(int=203))
AUTHORIZER = ActorIdentity(ActorId(UUID(int=301)), ActorType.HUMAN_OPERATOR)
BINDING_ID = "authorization-binding:audit-v1"


@dataclass(frozen=True, slots=True)
class AuditRecord:
    sequence: int
    kind: str
    identity: str
    exact_binding: str
    fact: str
    durable_source: str


def _evaluation(
    identity: EvaluationId,
    target: EvaluationTargetRef,
    verdict: EvaluationVerdict,
    evidence: str,
    verifier: ActorIdentity,
    version: int,
) -> Evaluation:
    return Evaluation(
        identity,
        EvaluationState.COMPLETED,
        EntityVersion(version),
        target,
        EvaluationMethodRef("strategic-audit", "1"),
        verifier,
        EvaluationResult(
            verdict,
            EvaluationConfidence("deterministic"),
            f"Executed audit observation backed by {evidence}.",
            frozenset({EvidenceRef(evidence)}),
        ),
    )


def execute_audit_scenario(database: str) -> None:
    store = SQLiteStore(database)
    ports = issue_test_ports()
    facade = GovernanceFacade(store, ports)

    task_id = TaskId(UUID(int=401))
    profile = ExecutionProfileRef("audit-profile", "1")
    run_a = Run(
        RunId(UUID(int=402)), task_id, RunState.RUNNING, EntityVersion(20), profile
    )
    run_b = Run(
        RunId(disposition_fx.VALUE),
        task_id,
        RunState.RUNNING,
        EntityVersion(21),
        profile,
    )
    seed_snapshot(store, run_a)
    seed_snapshot(store, run_b)

    candidate_a = replace(
        supersession_fx.source(OutcomeState.VALIDATING),
        outcome_id=A_ID,
        run_id=run_a.run_id,
    )
    candidate_b = replace(
        disposition_fx.outcome(),
        run_id=run_b.run_id,
        prior_outcome_id=candidate_a.outcome_id,
    )
    seed_snapshot(store, candidate_a)
    seed_snapshot(store, candidate_b)

    evaluator = disposition_fx.identity(ActorType.EVALUATOR, disposition_fx.THIRD)
    e1 = _evaluation(
        E1_ID,
        EvaluationTargetRef(candidate_a.outcome_id, candidate_a.version),
        EvaluationVerdict("candidate A supported"),
        "evidence:A-support",
        evaluator,
        11,
    )
    e2 = _evaluation(
        E2_ID,
        EvaluationTargetRef(candidate_b.outcome_id, disposition_fx.CANDIDATE_VERSION),
        disposition_fx.JUDGEMENT,
        "evidence:B-support",
        evaluator,
        disposition_fx.OBSERVED_EVALUATION_VERSION.value,
    )
    e3 = _evaluation(
        E3_ID,
        EvaluationTargetRef(candidate_b.outcome_id, disposition_fx.CANDIDATE_VERSION),
        EvaluationVerdict("candidate B should be rejected"),
        "evidence:B-conflict",
        ActorIdentity(ActorId(UUID(int=302)), ActorType.EVALUATOR),
        31,
    )
    for evaluation in (e1, e2, e3):
        seed_snapshot(store, evaluation)

    supersede_request = replace(
        supersession_fx.request(candidate_a), event_id=EventId(UUID(int=1001))
    )
    facade.apply_transition(
        ports[2],
        candidate_a.outcome_id,
        supersede_request,
        supersession_fx.context(
            candidate_a,
            supersede_request,
            supersession_fx.semantics(candidate_a, candidate_b, task_id=task_id),
        ),
    )

    arbitration = arbitration_fx.arbitration(e2)
    arbitration_request = replace(
        arbitration_fx.request(
            e2, EvaluationState.ARBITRATED, arbitration_fx.ARBITRATOR
        ),
        event_id=EventId(UUID(int=1002)),
    )
    arbitrated = facade.apply_transition(
        ports[1],
        e2.evaluation_id,
        arbitration_request,
        arbitration_fx.context(
            e2,
            arbitration_request,
            arbitration_fx.arbitration_semantics(e2, record=arbitration),
        ),
    ).entity
    assert isinstance(arbitrated, Evaluation)
    effective = derive_evaluation_effective_use(
        arbitrated,
        applicable_conflict_sets=frozenset(),
        arbitration_records=frozenset({arbitration}),
        invalidation_records=frozenset(),
    )
    assert effective.effective_judgement is not None

    disposition = disposition_fx.semantics(
        candidate_b, OutcomeState.ACCEPTED, evaluation_state=EvaluationState.ARBITRATED
    )
    observation = replace(
        disposition.evaluation,
        evaluation_id=arbitrated.evaluation_id,
        observed_evaluation_version=arbitrated.version,
        observed_state=arbitrated.state,
        target=arbitrated.target,
        verifier=arbitrated.verifier,
        effective_use=effective,
        effective_use_snapshot=OutcomeEvaluationEffectiveUseSnapshot(
            arbitrated.evaluation_id,
            arbitrated.version,
            arbitrated.state,
            arbitrated.target,
            effective,
        ),
    )
    disposition = replace(
        disposition,
        evaluation=observation,
        policy_decision=replace(
            disposition.policy_decision,
            evaluation_id=arbitrated.evaluation_id,
            observed_evaluation_version=arbitrated.version,
            effective_judgement=effective.effective_judgement,
        ),
    )
    accept_request = replace(
        disposition_fx.request(candidate_b, OutcomeState.ACCEPTED),
        event_id=EventId(UUID(int=1003)),
    )
    accepted = facade.apply_transition(
        ports[2],
        candidate_b.outcome_id,
        accept_request,
        disposition_fx.context(
            candidate_b,
            accept_request,
            disposition_fx.guard(candidate_b, OutcomeState.ACCEPTED, disposition),
        ),
    ).entity
    assert isinstance(accepted, Outcome)

    planned = remediation_fx.effect(EffectState.PLANNED)
    seed_snapshot(store, planned)
    authorization = HumanAuthorization(
        planned.effect_id,
        planned.version,
        planned.target_ref,
        planned.payload_ref,
        occurrence_fx.CORRELATION,
        AUTHORIZER,
        BINDING_ID,
    )
    facade.bind_authorization_evidence(
        ports[3], authorization, accepted.outcome_id, arbitrated.evaluation_id
    )
    commit_semantics = occurrence_fx.confirmed_semantics(
        planned, EffectAuthorizationStatus.AUTHORIZED
    )
    commit_request = replace(
        occurrence_fx.request(planned, EffectState.COMMITTED),
        event_id=EventId(UUID(int=1004)),
    )
    committed = facade.commit_effect(
        ports[3],
        FakeExternalSystem(),
        authorization,
        "operation:audit-publish-v1",
        commit_request,
        occurrence_fx.context(planned, commit_request, commit_semantics),
    ).entity
    assert isinstance(committed, Effect)

    plan = remediation_fx.compensation_plan(committed)
    start_semantics = EffectCompensationStartSemantics(
        commit_semantics.observation,
        plan,
        remediation_fx.authorization(
            remediation_fx.authorization_scope(committed, plan=plan)
        ),
    )
    start_request = replace(
        remediation_fx.request(committed, EffectState.COMPENSATING),
        event_id=EventId(UUID(int=1005)),
    )
    started_result = facade.apply_transition(
        ports[3],
        committed.effect_id,
        start_request,
        remediation_fx.context(committed, start_request, start_semantics),
    )
    started = started_result.entity
    assert isinstance(started, Effect)
    finish_request = remediation_fx.request(
        started,
        EffectState.COMPENSATED,
        controller=remediation_fx.COMPLETION_CONTROLLER,
        event_id=UUID(int=1006),
    )
    completion = replace(
        remediation_fx.completion_semantics(started, plan),
        original_commit_observation=commit_semantics.observation,
    )
    facade.apply_transition(
        ports[3],
        started.effect_id,
        finish_request,
        remediation_fx.context(
            started,
            finish_request,
            completion,
            start_event=started_result.event,
        ),
    )
    store.close()


def export_executed_records(database: str) -> tuple[AuditRecord, ...]:
    """Normalize only records re-read from durable Stage 1/integration storage."""
    store = SQLiteStore(database)
    candidate_a = store.outcomes.load(A_ID)
    candidate_b = store.outcomes.load(B_ID)
    e1 = store.evaluations.load(E1_ID)
    e2 = store.evaluations.load(E2_ID)
    e3 = store.evaluations.load(E3_ID)
    effect = store.effects.load(remediation_fx.effect(EffectState.PLANNED).effect_id)
    a_events = store.events.for_entity(A_ID)
    b_events = store.events.for_entity(B_ID)
    effect_events = store.events.for_entity(effect.effect_id)
    arbitrations = store.supporting_records(EvaluationArbitrationRecord)
    integrations = tuple(
        {"kind": kind, **json.loads(payload)}
        for kind, payload in store._connection.execute(
            "SELECT kind,payload FROM strategic_integration_records ORDER BY sequence"
        )
    )
    row = store._connection.execute(
        "SELECT payload FROM strategic_authorization_bindings WHERE binding_id=?",
        (BINDING_ID,),
    ).fetchone()
    assert row is not None
    binding_payload = json.loads(row[0])
    store.close()

    e1_result = e1.result
    e2_result = e2.result
    e3_result = e3.result
    assert e1_result is not None and e2_result is not None and e3_result is not None
    assert e1.target.version is not None
    assert e2.target.version is not None
    assert e3.target.version is not None
    arbitration = arbitrations[-1]
    supersession = a_events[-1]
    disposition = b_events[-1]
    authorization = next(
        item for item in integrations if item["kind"] == "human_authorization"
    )
    receipt = next(item for item in integrations if item["kind"] == "external_receipt")
    committed = next(
        item
        for item in effect_events
        if item.metadata.new_state is EffectState.COMMITTED
    )
    compensated = effect_events[-1]
    return (
        AuditRecord(
            1,
            "candidate",
            f"{A_ID}/v{candidate_a.version.value - 1}",
            f"run={candidate_a.run_id}",
            "Candidate A entered the persisted validation history.",
            "Stage1 entity_versions/events",
        ),
        AuditRecord(
            2,
            "evaluation",
            f"{e1.evaluation_id}/v{e1.version.value}",
            f"target={e1.target.reference}/v{e1.target.version.value}",
            f"E1 recorded {e1_result.verdict.value} with "
            f"{next(iter(e1_result.evidence_refs)).value}.",
            "Stage1 entity_versions/events",
        ),
        AuditRecord(
            3,
            "supersession",
            f"{candidate_a.outcome_id}/v{supersession.entity_version.value}",
            f"replacement={candidate_a.superseded_by_outcome_id}/v"
            f"{candidate_b.version.value - 1}",
            "Candidate B superseded A. E1 remains historical and exact-bound to A, "
            "so it is non-effective for B.",
            "Stage1 event operation provenance",
        ),
        AuditRecord(
            4,
            "evaluation",
            f"{e2.evaluation_id}/v{e2.version.value - 1}",
            f"target={e2.target.reference}/v{e2.target.version.value}",
            f"E2 supported B with {next(iter(e2_result.evidence_refs)).value}.",
            "Stage1 entity_versions/events",
        ),
        AuditRecord(
            5,
            "evaluation",
            f"{e3.evaluation_id}/v{e3.version.value}",
            f"target={e3.target.reference}/v{e3.target.version.value}",
            f"E3 recorded a conflicting judgment with "
            f"{next(iter(e3_result.evidence_refs)).value}.",
            "Stage1 entity_versions/events",
        ),
        AuditRecord(
            6,
            "arbitration",
            str(arbitration.arbitration_id),
            f"evaluation={e2.evaluation_id}/v{e2.version.value - 1}",
            "An independent Stage 1 arbitration upheld E2 for effective use; E3 "
            "remains a separate conflicting historical judgment and was not erased.",
            "Stage1 supporting_records and Evaluation event",
        ),
        AuditRecord(
            7,
            "disposition",
            f"{candidate_b.outcome_id}/v{candidate_b.version.value}",
            f"event={disposition.event_id};evaluation={e2.evaluation_id}/v"
            f"{e2.version.value}",
            "Outcome B became ACCEPTED from the persisted exact-current effective E2 "
            "judgment.",
            "Stage1 operations/events/supporting_records",
        ),
        AuditRecord(
            8,
            "effect_request",
            f"{effect.effect_id}/v{effect_events[0].entity_version.value}",
            f"target={effect.target_ref.value}",
            "A consequential Effect was durably PLANNED.",
            "Stage1 entity_versions/events",
        ),
        AuditRecord(
            9,
            "authorization_evidence_binding",
            binding_payload["binding_id"],
            f"disposition={binding_payload['disposition_event_id']};"
            f"evaluation={binding_payload['evaluation_id']}/v"
            f"{binding_payload['evaluation_version']}",
            "The trusted experimental binding verified and persisted the exact "
            "authorization, accepted disposition, effective judgment and evidence "
            f"{','.join(binding_payload['evidence_refs'])}.",
            "strategic_authorization_bindings",
        ),
        AuditRecord(
            10,
            "human_authorization",
            authorization["evidence_ref"],
            f"effect={authorization['effect_id']}/v{authorization['effect_version']}",
            f"Human operator {authorization['authorized_by']} authorized the exact "
            "prepared operation through the verified binding.",
            "strategic_integration_records",
        ),
        AuditRecord(
            11,
            "external_receipt",
            receipt["operation_key"],
            f"effect={receipt['effect_id']}",
            "The independent fake external system returned a durable receipt.",
            "strategic_integration_records",
        ),
        AuditRecord(
            12,
            "occurrence",
            f"{effect.effect_id}/v{committed.entity_version.value}",
            f"receipt={receipt['operation_key']}",
            "Independent observation confirmed that the external action occurred.",
            "Stage1 Effect event and occurrence supporting records",
        ),
        AuditRecord(
            13,
            "compensation",
            f"{effect.effect_id}/v{compensated.entity_version.value}",
            f"original-occurrence={effect.effect_id}/v{committed.entity_version.value}",
            "Compensation completed while the original committed occurrence remained "
            "in immutable history.",
            "Stage1 Effect events/supporting_records",
        ),
    )


def executed_records() -> tuple[AuditRecord, ...]:
    with tempfile.TemporaryDirectory() as directory:
        database = str(Path(directory) / "audit.sqlite")
        execute_audit_scenario(database)
        return export_executed_records(database)


def packet_text(records: tuple[AuditRecord, ...] | None = None) -> str:
    records = executed_records() if records is None else records
    lines = [
        "# Blind Audit Packet — Strategic Governance-Layer Validation",
        "",
        "This packet was normalized from an executed deterministic scenario. Its "
        "sources are persisted Stage 1 events, versions, operation provenance and "
        "supporting records plus append-only trusted experimental integration records. "
        "It does not contain the answer key.",
        "",
        "## Records",
        "",
    ]
    for record in records:
        lines.append(
            f"{record.sequence}. **{record.kind}** `{record.identity}` — binding: "
            f"`{record.exact_binding}`. {record.fact} Source: "
            f"`{record.durable_source}`."
        )
    lines.extend(
        (
            "",
            "## Scope and limitations",
            "",
            "- Occurrence uncertainty was not exercised; no QUARANTINED/UNCERTAIN "
            "interval is claimed.",
            "- Stage 1 does not dispatch external services. The bounded trusted "
            "experimental gateway performed the fake commit.",
            "- E3 is a persisted conflicting judgment, but it was not made a member of "
            "a Stage 1 conflict set. The implemented effective resolution used for B "
            "is the exact persisted direct arbitration of E2; the packet does not "
            "claim broader conflict-set resolution.",
            "- The authorization-to-evidence association is experimental adapter "
            "storage, not accepted production Stage 1 semantics.",
            "",
            "## Blind-review questions",
            "",
        )
    )
    lines.extend(f"{index}. {question}" for index, question in enumerate(QUESTIONS, 1))
    return "\n".join(lines) + "\n"


def answer_key_text(records: tuple[AuditRecord, ...] | None = None) -> str:
    records = executed_records() if records is None else records
    by_kind = {record.kind: record for record in records}
    answers = (
        f"Yes. {by_kind['external_receipt'].identity} and "
        f"{by_kind['occurrence'].identity} establish occurrence.",
        by_kind["human_authorization"].fact,
        f"{by_kind['authorization_evidence_binding'].exact_binding}; "
        f"{by_kind['authorization_evidence_binding'].fact}",
        by_kind["supersession"].fact,
        "No. The executed scenario did not model an uncertain occurrence interval.",
        f"No. {by_kind['compensation'].fact}",
        "B is ACCEPTED from exact-current arbitrated E2; the bound Human "
        "authorization permitted the Effect gateway commit, occurrence was confirmed, "
        "and compensation appended later records without erasing prior facts.",
    )
    lines = ["# Audit Answer Key", ""]
    lines.extend(f"{index}. {answer}" for index, answer in enumerate(answers, 1))
    return "\n".join(lines) + "\n"


def records_json(records: tuple[AuditRecord, ...] | None = None) -> str:
    records = executed_records() if records is None else records
    return (
        json.dumps(
            [
                {
                    "sequence": record.sequence,
                    "kind": record.kind,
                    "identity": record.identity,
                    "exact_binding": record.exact_binding,
                    "fact": record.fact,
                    "durable_source": record.durable_source,
                }
                for record in records
            ],
            indent=2,
        )
        + "\n"
    )


def write_artifacts(directory: Path) -> None:
    records = executed_records()
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "blind-audit-packet.md").write_text(
        packet_text(records), encoding="utf-8"
    )
    (directory / "audit-answer-key.md").write_text(
        answer_key_text(records), encoding="utf-8"
    )
    (directory / "audit-records.json").write_text(
        records_json(records), encoding="utf-8"
    )
