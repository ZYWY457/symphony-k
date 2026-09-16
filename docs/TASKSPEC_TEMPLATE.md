# Durable TaskSpec Template

Use this template to draft a bounded development Issue. It becomes executable
only after a Human materializes it as a durable Issue with a concrete identity
and launches a Worker with that identity and exact approved content or direct
read access.

At execution time the Issue number and URL MUST be concrete. A placeholder,
title-only reference, future Issue or conversation-only draft is prohibited.

## Title

State the bounded outcome, not an implementation slogan.

## Stage and milestone

- Stage:
- Parent plan:
- Milestone:
- Candidate or reconciliation work:

## Purpose

Describe the desired repository outcome and why it is needed.

## Required baseline

- Repository:
- Required starting commit:
- Required parent, when relevant:
- Required clean-worktree/toolchain preflight:
- TaskSpec access mode: `direct-read` or `materialized-handoff`

The Worker must stop before mutation on any mismatch.

## Accepted starting truth

List only durable Human Accepted facts and exact evidence/commit boundaries.
Distinguish historical candidate facts from currently accepted truth.

## Governing documents

List the Constitution, core beliefs, accepted ADRs/designs, Architecture,
roadmap/development path and active parent plan that apply, in authority order.

## In scope

List bounded deliverables and behavior.

## Out of scope

List prohibited adjacent work, future-stage capabilities and protected files.

## Architecture constraints

State authority, trust, persistence, isolation, compatibility, history and ADR
requirements. Any new top-level concept or cross-cutting dependency requires an
accepted ADR before implementation.

## Expected files

List files/directories that may be added, modified, moved or deleted. State the
files that must remain unchanged.

## Ordered commit plan

For multi-commit work, define each exact title, purpose, allowed paths and order.
State whether amend, squash or rebase is prohibited.

## Validation matrix

| Requirement | Validation command or inspection | Expected evidence |
| --- | --- | --- |
| Example boundary | exact command | objective pass condition |

Include diff checks, changed-file inspection, tests proportional to the change,
link/status audits for documentation and protected-path checks.

## STOP conditions

At minimum: baseline mismatch, TaskSpec identity/content mismatch, higher-
authority conflict, unavailable execution substrate, dirty overlapping work,
missing required ADR, failed required validation or need for scope expansion.

## Staging rules

Require explicit paths. Prohibit broad staging such as `git add .` and
`git add -A`. Require cached name/status, whitespace and full-diff inspection
before each commit.

## Remote mutation boundary

State separately whether push, PR/Issue mutation, remote branch/tag changes or
release publication is authorized. Local commit authority never implies remote
authority.

## Candidate versus Human Accepted status

State what the Worker may produce and the independent review needed before it
becomes accepted truth or changes stage status.

## Final report contract

Require TaskSpec reference/access/precondition, starting baseline, exact commit
SHAs/parents/titles/files, validation evidence, protected-file confirmation,
worktree state, unresolved risks and `remote mutation = none` when applicable.
