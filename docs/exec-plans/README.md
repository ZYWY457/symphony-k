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
