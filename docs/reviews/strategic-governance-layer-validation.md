# Strategic Governance-Layer Validation Correction — Issue #86

## Authority and precondition

```text
TaskSpec reference: https://github.com/ZYWY457/symphony-k/issues/86
TaskSpec revision: r1 - strategic-validation-evidence-correction
TaskSpec access mode: direct-read
TaskSpec updatedAt: 2026-09-17T02:02:14Z
TaskSpec precondition: PASS
Starting SHA: 52879a6ddcbfa4005c666c0cf23776899dd7825d
Starting parent: b7d105fa44d3252ada401e0aeab48e3ef773ef1d
Starting title: docs(strategy): record governance-layer validation evidence
```

Issue #85 and independent review comment `5707299068` were freshly read before
mutation. Issue #79 was freshly read as
`r3 - stage-02-m2-blocked-after-unknown-collection-stop`, **BLOCKED / NOT
RELEASED**. Remote `main` matched the required starting SHA; origin, clean
worktree, parent/title, merge/rebase absence, Git, Python and uv all matched the
TaskSpec. No durable overlap or later Issue #86 revision was present.

This correction changes only the Issue #85 experiment, tests, generated
evidence and this review. Production `src/symphony_k`, accepted Stage 1
semantics, Constitution, Product Contract, Roadmap, Development Path, ADRs and
Stage 2 plans/design are unchanged.

## Corrected G1 — execution success is distinct from Outcome acceptance

G1 now starts with an accepted Stage 1 `Run` in `RUNNING`. The external Worker
uses its Worker port and a Worker-labelled transition request to attempt
`Run.RUNNING -> COMPLETED`. The facade rejects the Worker lane before the Run
head changes. This is a real execution/work-success boundary: `COMPLETED` means
normal execution closure and is controlled by the Run controller; it does not
mean Outcome acceptance.

G2 remains the separate attack in which a Worker forges/relabels a disposition
port to accept its own Outcome. The fair baseline now has a distinct execution
attempt record and rejects Worker self-completion separately from candidate
self-acceptance.

Result: both registered threats are distinct and produce the expected safe
behavior.

## Corrected G3 — stale Evaluation, current Outcome request

The corrected Symphony-K attack keeps the authoritative Outcome and
`TransitionRequest.expected_version` exactly current. It first persists the
Evaluation snapshot referenced by the accepted disposition semantics, then a
trusted independent writer advances that Evaluation to a newer durable version.
The disposition still supplies the earlier exact Evaluation/effective-use
observation while requesting the current Outcome version.

The domain transition is structurally valid and the Outcome version check
passes. Stage 1 persistence rejects it with
`Outcome disposition requires an unchanged current Evaluation`; the Outcome
head remains unchanged. The rejection is therefore caused by exact durable
Evaluation/effective-use binding, not by an ordinary stale Outcome request.

The fair baseline performs the analogous case: it revises the candidate, keeps
the disposition request current, and supplies the earlier exact-version
Evaluation. Its exact-current Evaluation check rejects the request.

Result: expected safe behavior in both systems; Symphony-K additionally
re-derives the effective-use view from durable Evaluation/arbitration history.

## Corrected G7 — threat-equivalent direct history attack

Both sides now receive an attack beneath their normal service API.

- Symphony-K: direct SQL deletion from the Stage 1 `events` table is rejected by
  the SQLite append-only trigger; the `COMMITTED` occurrence remains factual.
- Baseline: the bounded baseline intentionally remains the same competent
  in-process service with exact checks, lock/CAS, idempotency and an
  append-only-by-API event list. It has no durable database or private
  persistence boundary. A direct in-memory attack can clear the event history
  and replace the Effect with `occurred=false`.

The baseline result is **UNPROTECTED**, not a comparable SAFE pass. No baseline
check was removed or weakened; the corrected test exposes the structural limit
of its original persistence design.

## Executed audit scenario and exporter

The former hand-authored `RECORDS` tuple and standalone narrative ledger were
removed. `audit.py` now executes one deterministic scenario through the Issue
#85 facade and accepted Stage 1 service/persistence:

```text
candidate A in validation
-> persisted Evaluation E1 exact-bound to A
-> accepted Outcome supersession A -> B
-> persisted supporting E2 and conflicting E3 exact-bound to B
-> persisted direct Stage 1 arbitration upholding E2 for effective use
-> accepted Outcome B disposition using exact-current arbitrated E2
-> persisted planned Effect
-> verified experimental authorization/evidence binding
-> exact Human authorization
-> trusted gateway commit and external receipt
-> confirmed Stage 1 occurrence
-> Stage 1 compensation preserving the committed occurrence
```

E3 is honestly represented as a separate persisted conflicting judgment. It is
not claimed as a member of a Stage 1 conflict set. The implemented effective
resolution used for B is direct Stage 1 arbitration of E2. This is narrower
than full multi-member conflict-set arbitration and is stated in the blind
packet.

After execution, the exporter closes and reopens SQLite and derives all packet
records from these durable sources:

- Stage 1 `entity_versions` and `events` for candidates, Evaluations and Effect;
- Stage 1 `operations` provenance for supersession and disposition;
- Stage 1 `supporting_records` for Evaluation arbitration, Effect occurrence and
  compensation semantics;
- append-only experimental `strategic_authorization_bindings`;
- append-only experimental `strategic_integration_records` for Human
  authorization and external receipt.

The renderer normalizes those records into stable human-readable labels. It
does not begin with desired answers or pre-authored narrative records.

Fresh artifacts:

- blind packet:
  `experiments/governance_layer_validation/artifacts/blind-audit-packet.md`;
- separate answer key:
  `experiments/governance_layer_validation/artifacts/audit-answer-key.md`;
- machine export:
  `experiments/governance_layer_validation/artifacts/audit-records.json`.

The seven Issue #86 questions are unchanged. The packet contains no answer key.

## Authorization-to-evidence binding

Issue #86 Option A is implemented outside production `src/`.

`bind_authorization_evidence` accepts the exact `HumanAuthorization`, Effect,
accepted Outcome and effective Evaluation identities. Before inserting an
append-only binding it verifies:

1. exact current Effect identity/version/target/payload;
2. current accepted Outcome and its current persisted disposition event;
3. disposition operation provenance contains the exact Evaluation
   id/version/state/target/verifier and an eligible effective-use view;
4. the Evaluation has persisted nonempty evidence;
5. every referenced arbitration identity resolves to a persisted Stage 1
   supporting record.

`commit_effect` reloads the durable binding, re-derives it from current persisted
sources and requires exact equality before touching the external system. A
nonblank but unbound `evidence_ref` is explicitly tested and rejected before
external mutation.

This is bounded experimental adapter storage. It does not change or claim a new
accepted Stage 1 production semantic.

## Corrected raw results

| ID | Symphony-K result | Fair baseline result | Corrected interpretation |
|---|---|---|---|
| G1 | SAFE: Worker cannot complete its Run | SAFE: Worker cannot complete its execution attempt | Distinct execution-success threat; equal bounded protection |
| G2 | SAFE: forged disposition port rejected | SAFE: producer cannot dispose own candidate | Distinct Outcome self-acceptance threat; equal protection |
| G3 | SAFE: current Outcome request rejected because Evaluation observation is no longer durable-current | SAFE: current candidate request rejects earlier-version Evaluation | Registered stale-evidence threat now exercised |
| G4 | SAFE: nominal/exact binding rejects substitution | SAFE: string identity equality rejects substitution | Same outcome; reusable structural binding advantage |
| G5 | SAFE: exact durable replay returns original immutable receipt | SAFE: stale replay rejected | Material durable replay/provenance difference |
| G6 | SAFE: missing or unbound Human authorization rejected before external mutation | SAFE: missing approval rejected | Experimental exact evidence binding now demonstrated |
| G7 | SAFE: direct SQL deletion rejected | UNPROTECTED: direct in-memory mutation erases occurrence/history | Material durable structural difference; not counted as baseline SAFE |
| G8 | SAFE: one SQLite writer wins, one conflicts | SAFE: lock/CAS gives one winner | Equal outcome; Symphony-K history is durable |

All H1-H5 legal controls pass. H4 now includes successful durable
authorization-to-disposition/evaluation/evidence binding before exact Human
authorization and external commit.

## Recomputed provisional criteria

- **A — PASS (provisional):** meaningful candidate, Evaluation, disposition,
  Effect and audit governance still execute without owning Planner, Router,
  AgentDriver or Sandbox.
- **B — PASS (provisional):** corrected distinct G1, true stale-evidence G3,
  G2/G4-G8 all produce their registered safe behavior; H1-H5 all succeed.
- **C — PASS (provisional):** G4 exact nominal/provenance binding, G5 durable
  idempotent replay and G7 database-enforced append-only history remain three
  material structural differentiators after the fair direct-attack correction.
- **D — PENDING INDEPENDENT BLIND REVIEW:** the Worker does not self-score it.
- **E — PASS (provisional):** five primary operations, 445 measured
  nonblank/non-comment facade lines (480 physical), zero production changes and
  zero accepted semantic changes. The large Stage 1 type surface remains a
  material ergonomics warning.

The baseline is 216 measured nonblank/non-comment lines (249 physical). Audit
scenario/export code is 575 measured nonblank/non-comment lines (608 physical)
and is reported separately from facade glue.

**NON-BINDING Worker recommendation: DEFER STRATEGIC CLASSIFICATION.** A/B/C/E
are provisionally PASS, but no GO/CONDITIONAL/NO-GO conclusion should be made
before the independent blind review determines D. Product Contract and Roadmap
remain unchanged.

## Negative and falsifying evidence

1. The competent fair baseline still matches most bounded safety/legal outcomes
   with less code and fewer concepts.
2. The baseline lacks durable/private persistence, making it structurally
   vulnerable to direct history mutation; this is a genuine negative for the
   baseline, not proof that every ordinary application shares the weakness.
3. E3 is not part of a persisted Stage 1 conflict set. The scenario demonstrates
   direct arbitration of E2, not full conflict-set resolution across E2/E3.
4. Authorization-to-evidence binding is experimental integration storage, not a
   production Stage 1 contract.
5. A crash after the external commit but before local occurrence recording is
   still not transactionally solved.
6. Five facade operations meet the numeric target, but constructing accepted
   request/context objects exposes a broad semantic type surface.
7. Independent blind comprehensibility is not yet established; criterion D
   remains pending.

## Validation evidence

All required executable gates passed on the corrected worktree:

```text
uv run pytest tests/experiments -q
28 passed

uv run pytest
3297 passed

uv run ruff check .
All checks passed!

uv run ruff format --check .
252 files already formatted

uv run mypy src tests
Success: no issues found in 128 source files

uv run mypy experiments tests/experiments
Success: no issues found in 10 source files
```

The full suite includes the constitutional lifecycle assertions: 43 states,
91 transition edges plus 8 creation variants, for the unchanged total of 99.
Experiment tests execute the scenario, close/reopen SQLite, export the records
twice and compare them with freshly executed output. Regeneration of the three
audit artifacts is byte-reproducible.

Final path and diff checks confirmed no change under `src/symphony_k`,
Constitution, Product Contract, Roadmap, Development Path, ADRs, accepted Stage
1 semantic/domain files, Stage 2 technical design or plans. No Docker, E2B,
Daytona, Temporal, Planner, Router, AgentDriver, Sandbox, recovery engine, UI or
production network service was added.

Issue #79 remains **BLOCKED / NOT RELEASED**. Stage 2 runtime implementation is
**NOT STARTED**. Product Contract/Roadmap are unchanged. `remote mutation = none`.
