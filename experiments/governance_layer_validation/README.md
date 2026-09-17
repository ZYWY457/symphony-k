# Governance-Layer Validation Experiment

This bounded Issue #85 experiment places a fake Worker and fake external system
outside the accepted Stage 1 kernel. It changes no production source or accepted
semantics.

The architecture is:

```text
fake Worker / evaluator / Human / gateway
        -> opaque-port experimental facade (4 operations)
        -> Stage 1 domain + LifecycleService + SQLiteStore
        -> durable Stage 1 events/supporting records

fake external system (independent state)
        <- trusted experimental gateway only
```

Primary facade operations are `submit_creation`, `apply_transition`,
`commit_effect`, and `export_audit`. The caller directly handles six broad
existing API types: `CreationRequest`, `CreationContext`, `LifecycleEntityId`,
`TransitionRequest`, `TransitionContext`, and `TransitionResult`. Concrete
request/context construction exposes many additional Stage 1 semantic record
types, which is an ergonomics cost rather than hidden from the measurement.

Measured facade glue is 234 nonblank, non-comment lines in `facade.py` (264
physical lines). The baseline is 183 nonblank, non-comment lines (211 physical
lines). Audit rendering is reported separately and is not counted as facade
glue.

Artifacts:

- `artifacts/result-summary.json` — machine-readable G1-G8/H1-H5 results;
- `artifacts/blind-audit-packet.md` — packet for the independent reviewer;
- `artifacts/audit-answer-key.md` — deliberately separate answer key;
- `artifacts/audit-records.json` — deterministic exported narrative records.

The audit packet is regenerated deterministically and its source records pass a
SQLite close/reopen durability test. The answer key is never embedded in the
packet. Criterion D remains pending a genuinely independent blind review.

Run:

```text
uv run pytest tests/experiments
```

This namespace is experimental, not a public v1 SDK or a Stage 2 runtime.
