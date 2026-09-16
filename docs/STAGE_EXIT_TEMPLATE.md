# Human Stage Exit Template

Use this checklist only after every required milestone has completed its own
independent review. A parent plan or passing Worker report is not enough.

## Stage identity and evidence boundary

- Stage and parent plan:
- Candidate exit commit:
- Accepted milestone commits and review records:
- Constitutional baseline:
- Reviewer and decision date:

## Preconditions

- [ ] Entry implementation and prerequisite stage were Human Accepted.
- [ ] All milestone plans are reconciled and historical corrections are linked.
- [ ] The candidate exactly matches the required baseline and stage scope.
- [ ] Required ADRs/designs are accepted and documentation reflects behavior.

## Constitutional and security review

- [ ] Constitutional invariants remain preserved.
- [ ] Worker, controller, evaluator, Human and Effect authorities remain separate.
- [ ] Security/trust questions in the parent plan have evidence-backed answers.
- [ ] Credentials, permissions, isolation and external Effects fail closed.
- [ ] Facts, provenance and audit history remain append-only in meaning.

## Reliability and recovery review

- [ ] Rollback/recovery behavior was tested where applicable.
- [ ] Persistence and historical records survive relevant loss/restart cases.
- [ ] Concurrency, idempotency and replay behavior have objective evidence.
- [ ] Known failures and rejected candidates remain visible and attributable.

## Quality and continuity review

- [ ] Required quality gates passed at the exact candidate commit.
- [ ] Documentation, links, commands and status are current.
- [ ] Deferred work is explicit, non-blocking and owned by a later stage/backlog.
- [ ] The next stage boundary, prerequisites and non-goals are clear.
- [ ] A fresh maintainer can reproduce the review from repository artifacts.

## Human decision

Answer every Human Exit Review question from the parent plan and record one:

```text
ACCEPTED
REQUEST CHANGES
```

`REQUEST CHANGES` preserves the candidate and opens bounded correction work.
`ACCEPTED` does not by itself move files or rewrite status.

## Governance reconciliation

A stage becomes `COMPLETE` only after independent Human Exit acceptance and a
subsequent durable governance reconciliation that:

- records the exact acceptance evidence;
- updates `STATUS.md` and the roadmap/development path as needed;
- moves the parent plan from `active/` to `completed/` without erasing history;
- identifies what, if anything, is authorized next;
- leaves implementation of the next stage blocked until its own TaskSpec.
