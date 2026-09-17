# Governance-Layer Validation Experiment

This bounded Issue #85 experiment, corrected under Issue #86, places a fake
Worker and fake external system outside the accepted Stage 1 kernel. It changes
no production source or accepted semantics.

The architecture is:

```text
fake Worker / evaluator / Human / gateway
        -> opaque-port experimental facade (5 operations)
        -> Stage 1 domain + LifecycleService + SQLiteStore
        -> durable Stage 1 events/supporting records

fake external system (independent state)
        <- trusted experimental gateway only
```

Primary facade operations are `submit_creation`, `apply_transition`,
`bind_authorization_evidence`, `commit_effect`, and `export_audit`. The bounded
binding verifies an exact persisted accepted Outcome disposition, the exact
effective Evaluation version/judgment/evidence, and any supporting arbitration
before an exact Human authorization can commit an Effect. A nonblank string is
not sufficient.

The caller directly handles six broad existing API types: `CreationRequest`,
`CreationContext`, `LifecycleEntityId`, `TransitionRequest`,
`TransitionContext`, and `TransitionResult`. Concrete request/context
construction exposes many additional Stage 1 semantic record types, which is
an ergonomics cost rather than hidden from the measurement.

Measured facade glue is 445 nonblank, non-comment lines in `facade.py` (480
physical lines). The baseline is 216 nonblank, non-comment lines (249 physical
lines). Audit execution/export is reported separately and is not counted as
facade glue.

Artifacts:

- `artifacts/result-summary.json` — machine-readable G1-G8/H1-H5 results;
- `artifacts/blind-audit-packet.md` — packet for the independent reviewer;
- `artifacts/audit-answer-key.md` — deliberately separate answer key;
- `artifacts/audit-records.json` — normalized records exported from the executed
  durable scenario.

The audit runner executes candidate supersession, Evaluation arbitration,
Outcome disposition, exact authorization binding, external receipt/occurrence,
and compensation. The exporter then reopens SQLite and reads Stage 1
`entity_versions`, `events`, `operations`, and `supporting_records`, plus
append-only `strategic_authorization_bindings` and
`strategic_integration_records`. No hand-authored `RECORDS` narrative is used.
The answer key is never embedded in the packet. Criterion D remains pending a
genuinely independent blind review.

Run:

```text
uv run pytest tests/experiments
```

This namespace is experimental, not a public v1 SDK or a Stage 2 runtime.
