# Stage 1 M7C4B — Canonical Outcome Disposition Semantic Guards

**Version:** 1
**Status:** Active
**Scope:** GitHub Issue #39 only

## Boundary

M7C4B extends the accepted M7C4A/M7C4A1 Outcome semantic boundary for exactly
`VALIDATING -> ACCEPTED` and `VALIDATING -> REJECTED`. It consumes immutable,
exact-bound validation lineage, Evaluation effective-use observations, Outcome
disposition-policy decisions, and conditional human acceptance. It does not
derive Evaluation conflict, arbitration, or invalidation history; load or persist
records; execute policy; or mutate another lifecycle entity.

## Bounded steps

1. Add minimum typed provenance for the validation-start lineage, exact observed
   Evaluation effective-use result, intended Outcome disposition, dedicated
   Outcome disposition policy, and conditional human acceptance.
2. Extend the canonical Outcome guard to validate the two disposition edges while
   preserving the accepted validation-start edge and denying all eight future
   supersession/expiry edges by default.
3. Enforce exact Outcome/candidate/Evaluation/request/judgement/policy/correlation
   binding, effective-use eligibility, positive policy authority, producer
   independence, explicit rejection, and required human acceptance.
4. Add deterministic tests covering both successful dispositions, provenance
   substitution, effective-use failure modes, policy/human authority, lifecycle
   isolation, retained M7B1/M7B2 gates, topology, and M7C4A regression behavior.
5. Run all Issue #39 validation gates, explicitly stage only Issue #39 files,
   inspect the staged diff, and create exactly one local commit without remote
   mutation.

## Acceptance evidence

- Evaluation judgement remains distinct from Outcome ACCEPTED/REJECTED; no
  `EvaluationVerdict.value` taxonomy is introduced or parsed.
- The current VALIDATING snapshot is tied to the prior candidate snapshot and the
  exact Evaluation request accepted at validation start without equating Outcome
  and Evaluation version domains.
- Only an eligible existing Evaluation effective-use view can support an explicit,
  exact-bound Outcome disposition-policy decision; rejection is never inferred
  from failed acceptance.
- Human acceptance is separate, affirmative, evidence-backed, and required exactly
  when the acceptance policy says so.
- Successful transition changes only Outcome state/version. Existing topology and
  all other entity snapshots remain unchanged.
