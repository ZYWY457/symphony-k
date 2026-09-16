# Exec Plans

Use Exec Plans for substantial multi-step work.

Each plan should contain:

- objective,
- context,
- architecture constraints,
- in scope,
- out of scope,
- milestones,
- dependencies,
- risks,
- acceptance criteria,
- evidence required for completion,
- decisions or ADR references.

Exec Plans have three repository states:

```text
planned/   future parent plans; not execution authorization
active/    the current authorized planning or implementation stage
completed/ exited and accepted historical plans
```

The normal lifecycle is `planned -> active -> completed`. Merely placing a file
under `planned/` MUST NOT authorize code mutation. Activation requires a durable
Human-approved TaskSpec and every applicable prior-stage exit gate. Stage-level
parent plans may remain active until their whole stage exits. Completed task
plans move to `completed/` without rewriting their historical content.

## Activation and exit

Activation is a Human governance decision. Its durable TaskSpec must identify
the exact plan, prerequisite acceptance boundary, allowed scope and first
bounded work. A planned parent contract is not an all-at-once implementation
Issue, and an open Issue does not by itself authorize unspecified work.

A parent plan moves to `completed/` only after:

1. all required milestone candidates have independent acceptance or explicit
   later-stage ownership;
2. its Human Exit Review is `ACCEPTED` with evidence; and
3. a subsequent durable governance reconciliation records the decision,
   archives the plan and updates current status.

`REQUEST CHANGES` preserves the candidate and creates bounded correction work;
it does not rewrite the failed history. `STATUS.md` is the compact current-stage
summary, but it remains subordinate to the Constitution, core beliefs, accepted
ADRs, Architecture and accepted designs.
