"""The fair comparison is secure for the same bounded cases, not crippled."""

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from experiments.governance_layer_validation.baseline import (  # noqa: E402
    Approval,
    BaselineRejection,
    BaselineService,
    Candidate,
    Effect,
    Evaluation,
)


def candidate() -> Candidate:
    return Candidate("candidate-a", 1, "worker:one", "payload-a")


def evaluation(version: int = 1, candidate_id: str = "candidate-a") -> Evaluation:
    return Evaluation(
        "evaluation-e1",
        candidate_id,
        version,
        "evaluator:one",
        "PASS",
        "evidence:e1",
    )


def approval(version: int = 1, effect_id: str = "effect-a") -> Approval:
    return Approval(effect_id, version, "remote:a", "payload:a", "human:one", "corr:a")


def test_baseline_g1_g2_self_success_and_self_accept_are_rejected() -> None:
    service = BaselineService()
    service.record_candidate(candidate())
    service.record_evaluation(evaluation())
    with pytest.raises(BaselineRejection, match="producer"):
        service.dispose("candidate-a", 1, "evaluation-e1", "worker:one", "ACCEPTED")


def test_baseline_g3_stale_evidence_is_rejected() -> None:
    service = BaselineService()
    service.record_candidate(candidate())
    service.record_evaluation(evaluation())
    service.revise_candidate("candidate-a", 1, "payload-b")
    with pytest.raises(BaselineRejection, match="exact-current"):
        service.dispose("candidate-a", 2, "evaluation-e1", "reviewer:one", "ACCEPTED")


def test_baseline_g4_cross_entity_substitution_is_rejected() -> None:
    service = BaselineService()
    service.record_candidate(candidate())
    service.record_candidate(Candidate("candidate-b", 1, "worker:two", "payload-b"))
    service.record_evaluation(evaluation())
    with pytest.raises(BaselineRejection, match="exact-current"):
        service.dispose("candidate-b", 1, "evaluation-e1", "reviewer:one", "ACCEPTED")


def test_baseline_g5_old_context_replay_is_rejected() -> None:
    service = BaselineService()
    service.record_candidate(candidate())
    service.record_evaluation(evaluation())
    service.dispose("candidate-a", 1, "evaluation-e1", "reviewer:one", "ACCEPTED")
    with pytest.raises(BaselineRejection, match="stale"):
        service.dispose("candidate-a", 1, "evaluation-e1", "reviewer:one", "ACCEPTED")


def test_baseline_g6_sensitive_commit_needs_human_authorization() -> None:
    service = BaselineService()
    service.request_effect(Effect("effect-a", 1, "remote:a", "payload:a"))
    with pytest.raises(BaselineRejection, match="Human"):
        service.commit_effect("effect-a", 1, None, "key:a")


def test_baseline_g7_occurrence_cannot_be_erased_through_api() -> None:
    service = BaselineService()
    service.request_effect(Effect("effect-a", 1, "remote:a", "payload:a"))
    service.commit_effect("effect-a", 1, approval(), "key:a")
    compensated = service.compensate("effect-a", 2)
    assert compensated.occurred is True
    assert [event["kind"] for event in service.audit()] == [
        "effect_requested",
        "effect_committed",
        "effect_compensated",
    ]


def test_baseline_g8_stale_concurrent_writer_has_one_winner() -> None:
    service = BaselineService()
    service.record_candidate(candidate())

    def revise(payload: str) -> str:
        try:
            service.revise_candidate("candidate-a", 1, payload)
            return "updated"
        except BaselineRejection:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = sorted(pool.map(revise, ("payload-b", "payload-c")))
    assert results == ["conflict", "updated"]


def test_baseline_h1_h5_legal_flow() -> None:
    service = BaselineService()
    assert service.record_candidate(candidate()).state == "PROPOSED"  # H1
    assert service.record_evaluation(evaluation()).verdict == "PASS"  # H2
    assert (
        service.dispose(
            "candidate-a", 1, "evaluation-e1", "reviewer:one", "ACCEPTED"
        ).state
        == "ACCEPTED"
    )  # H3
    service.request_effect(Effect("effect-a", 1, "remote:a", "payload:a"))
    assert service.commit_effect("effect-a", 1, approval(), "key:a").occurred  # H4
    remediated = service.compensate("effect-a", 2)
    assert remediated.compensated and remediated.occurred  # H5
