# Blind Audit Packet — Strategic Governance-Layer Validation

This packet contains exported deterministic records only. It does not contain the answer key.

## Records

1. **candidate** `outcome-A/v1` — binding: `run-17`. Candidate A proposed.
2. **evaluation** `evaluation-E1/v3` — binding: `outcome-A/v1`. E1 supported candidate A.
3. **supersession** `outcome-B/v1` — binding: `prior=outcome-A/v1`. Candidate B superseded A; E1 remains historical but targets A only.
4. **evaluation** `evaluation-E2/v3` — binding: `outcome-B/v1`. E2 supported candidate B with evidence evidence:B-support.
5. **evaluation** `evaluation-E3/v3` — binding: `outcome-B/v1`. E3 conflicted with E2 using evidence evidence:B-conflict.
6. **arbitration** `arbitration-AB/v1` — binding: `E2/v3+E3/v3`. An independent Human arbitration upheld E2 and reversed E3 for effective use.
7. **disposition** `outcome-B/v2` — binding: `arbitration-AB/v1`. Outcome B accepted from the current arbitrated effective judgment.
8. **effect_request** `effect-42/v1` — binding: `outcome-B/v2`. A consequential publish Effect was requested.
9. **human_authorization** `human-auth-42` — binding: `effect-42/v1+target+payload+correlation`. Human operator human-7 authorized the exact prepared operation.
10. **external_receipt** `receipt-42` — binding: `effect-42/v1+operation-key-42`. The independent external system returned a commit receipt.
11. **occurrence** `effect-42/v2` — binding: `receipt-42`. Independent observation confirmed the external action occurred.
12. **compensation** `effect-42/v4` — binding: `original-occurrence=effect-42/v2`. Compensation completed; original occurrence remains historical.

## Scope and limitations

- Occurrence uncertainty was not exercised in this narrative; no QUARANTINED/UNCERTAIN interval is claimed.
- Stage 1 represents supersession, immutable Evaluations, conflict membership, arbitration, disposition, Effect occurrence and compensation. It does not execute an external service itself.
- The experimental trusted gateway performed the fake external commit. Its exact Human authorization and receipt are durable experimental integration records; confirmed occurrence and compensation are Stage 1 records.

## Blind-review questions

1. Did the consequential external action occur?
2. Who/what authorized it?
3. Which exact evidence/judgment supported authorization?
4. Which earlier evidence became stale/superseded and why could it no longer authorize the later state?
5. Was there any point where the authoritative record was uncertain about occurrence? If the experiment does not model such uncertainty, say so.
6. Did compensation/remediation erase the original occurrence?
7. Why is the final authoritative disposition/history what it is?
