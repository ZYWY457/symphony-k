# ADR-0004: Evidence Before Acceptance

## Status

Accepted.

## Context

Worker self-report is not a reliable basis for authoritative completion. A separate judge model is also insufficient as a universal source of truth.

## Decision

Completion and acceptance rely on an evidence-based dynamic verification pipeline. Deterministic evidence is preferred when available. Semantic model evaluation is used where necessary and remains one validator among many.

## Consequences

- Outcome acceptance is independent from worker self-assessment,
- Evaluations preserve evidence and provenance,
- validator disagreements can be escalated,
- human arbitration remains available for low-confidence or high-risk cases.
